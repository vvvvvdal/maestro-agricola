#include <android/log.h>
#include <jni.h>

#include <algorithm>
#include <cstdint>
#include <mutex>
#include <stdexcept>
#include <string>
#include <vector>

#include "llama.h"

namespace {

constexpr const char * LOG_TAG = "MaestroQwen";

constexpr int CONTEXT_SIZE = 2048;
constexpr int BATCH_SIZE = 512;
constexpr int N_THREADS = 4;
constexpr int MAX_GENERATED_TOKENS = 64;

constexpr const char * RESPONSE_GRAMMAR = R"GBNF(
root ::= "{" ws "\"type\"" ws ":" ws type ws "," ws "\"response\"" ws ":" ws string ws "}"
type ::= "\"CHAT\"" | "\"OUT_OF_SCOPE\""
string ::= "\"" char* "\""
char ::= [^"\\\n\r] | escape
escape ::= "\\" (["\\/bfnrt] | "u" hex hex hex hex)
hex ::= [0-9a-fA-F]
ws ::= [ \t\n]*
)GBNF";

std::mutex g_mutex;

llama_model * g_model = nullptr;
llama_context * g_context = nullptr;
const llama_vocab * g_vocab = nullptr;
llama_sampler * g_grammar_template = nullptr;

bool g_backend_initialized = false;

std::string g_model_path;
std::string g_chat_template;
std::string g_system_prompt;
std::string g_formatted_system_prompt;

int32_t g_system_token_count = 0;

void log_info(const std::string & message) {
    __android_log_print(
        ANDROID_LOG_INFO,
        LOG_TAG,
        "%s",
        message.c_str()
    );
}

void log_error(const std::string & message) {
    __android_log_print(
        ANDROID_LOG_ERROR,
        LOG_TAG,
        "%s",
        message.c_str()
    );
}

std::string jstring_to_string(
    JNIEnv * env,
    jstring value
) {
    if (value == nullptr) {
        throw std::runtime_error("null Java string");
    }

    const char * chars = env->GetStringUTFChars(value, nullptr);

    if (chars == nullptr) {
        throw std::runtime_error("failed to read Java string");
    }

    std::string result(chars);
    env->ReleaseStringUTFChars(value, chars);

    return result;
}

void throw_java_exception(
    JNIEnv * env,
    const char * class_name,
    const std::string & message
) {
    jclass exception_class = env->FindClass(class_name);

    if (exception_class != nullptr) {
        env->ThrowNew(exception_class, message.c_str());
    }
}

std::vector<llama_token> tokenize(
    const std::string & text,
    bool add_special
) {
    if (g_vocab == nullptr) {
        throw std::runtime_error("Qwen vocabulary is not loaded");
    }

    std::vector<llama_token> tokens(
        std::max<size_t>(text.size() + 32, 128)
    );

    int32_t count = llama_tokenize(
        g_vocab,
        text.c_str(),
        static_cast<int32_t>(text.size()),
        tokens.data(),
        static_cast<int32_t>(tokens.size()),
        add_special,
        true
    );

    if (count == INT32_MIN) {
        throw std::runtime_error("tokenization overflow");
    }

    if (count < 0) {
        tokens.resize(static_cast<size_t>(-count));

        count = llama_tokenize(
            g_vocab,
            text.c_str(),
            static_cast<int32_t>(text.size()),
            tokens.data(),
            static_cast<int32_t>(tokens.size()),
            add_special,
            true
        );
    }

    if (count < 0) {
        throw std::runtime_error("failed to tokenize prompt");
    }

    tokens.resize(static_cast<size_t>(count));
    return tokens;
}

void decode_tokens(
    const std::vector<llama_token> & tokens
) {
    if (g_context == nullptr) {
        throw std::runtime_error("Qwen context is not initialized");
    }

    for (size_t offset = 0; offset < tokens.size();) {
        const int32_t count = static_cast<int32_t>(
            std::min<size_t>(
                BATCH_SIZE,
                tokens.size() - offset
            )
        );

        llama_batch batch = llama_batch_get_one(
            const_cast<llama_token *>(tokens.data() + offset),
            count
        );

        const int32_t result = llama_decode(
            g_context,
            batch
        );

        if (result != 0) {
            throw std::runtime_error(
                "llama_decode failed with code " +
                std::to_string(result)
            );
        }

        offset += static_cast<size_t>(count);
    }
}

void decode_token(
    llama_token token
) {
    llama_batch batch = llama_batch_get_one(
        &token,
        1
    );

    const int32_t result = llama_decode(
        g_context,
        batch
    );

    if (result != 0) {
        throw std::runtime_error(
            "llama_decode generated token failed with code " +
            std::to_string(result)
        );
    }
}

std::string token_to_piece(
    llama_token token
) {
    char local_buffer[256];

    int32_t length = llama_token_to_piece(
        g_vocab,
        token,
        local_buffer,
        sizeof(local_buffer),
        0,
        false
    );

    if (length >= 0) {
        return std::string(
            local_buffer,
            static_cast<size_t>(length)
        );
    }

    std::vector<char> buffer(
        static_cast<size_t>(-length)
    );

    length = llama_token_to_piece(
        g_vocab,
        token,
        buffer.data(),
        static_cast<int32_t>(buffer.size()),
        0,
        false
    );

    if (length < 0) {
        throw std::runtime_error(
            "failed to convert generated token to text"
        );
    }

    return std::string(
        buffer.data(),
        static_cast<size_t>(length)
    );
}

std::string apply_chat_template(
    const std::vector<llama_chat_message> & messages,
    bool add_assistant
) {
    if (g_chat_template.empty()) {
        throw std::runtime_error(
            "model does not provide a supported chat template"
        );
    }

    size_t content_size = 0;

    for (const auto & message : messages) {
        if (message.content != nullptr) {
            content_size += std::string(message.content).size();
        }
    }

    std::vector<char> buffer(
        std::max<size_t>(
            content_size * 2 + 1024,
            4096
        )
    );

    int32_t length = llama_chat_apply_template(
        g_chat_template.c_str(),
        messages.data(),
        messages.size(),
        add_assistant,
        buffer.data(),
        static_cast<int32_t>(buffer.size())
    );

    if (length < 0) {
        throw std::runtime_error(
            "failed to apply model chat template"
        );
    }

    if (static_cast<size_t>(length) > buffer.size()) {
        buffer.resize(static_cast<size_t>(length) + 1);

        length = llama_chat_apply_template(
            g_chat_template.c_str(),
            messages.data(),
            messages.size(),
            add_assistant,
            buffer.data(),
            static_cast<int32_t>(buffer.size())
        );

        if (length < 0) {
            throw std::runtime_error(
                "failed to reapply model chat template"
            );
        }
    }

    return std::string(
        buffer.data(),
        static_cast<size_t>(length)
    );
}

void clear_turn_keep_system() {
    if (g_context == nullptr) {
        return;
    }

    llama_memory_seq_rm(
        llama_get_memory(g_context),
        0,
        g_system_token_count,
        -1
    );
}

void cache_system_prompt(
    const std::string & system_prompt
) {
    if (
        g_model == nullptr ||
        g_context == nullptr ||
        g_vocab == nullptr ||
        g_grammar_template == nullptr
    ) {
        throw std::runtime_error(
            "Qwen model is not initialized"
        );
    }

    llama_memory_clear(
        llama_get_memory(g_context),
        false
    );

    g_system_prompt = system_prompt;

    const std::vector<llama_chat_message> messages = {
        {
            "system",
            g_system_prompt.c_str()
        }
    };

    g_formatted_system_prompt = apply_chat_template(
        messages,
        false
    );

    const auto tokens = tokenize(
        g_formatted_system_prompt,
        true
    );

    if (
        tokens.empty() ||
        tokens.size() + MAX_GENERATED_TOKENS + 4 >=
            static_cast<size_t>(CONTEXT_SIZE)
    ) {
        throw std::runtime_error(
            "Maestro system prompt does not fit Qwen context"
        );
    }

    decode_tokens(tokens);

    g_system_token_count =
        static_cast<int32_t>(tokens.size());

    log_info(
        "system prompt cached with " +
        std::to_string(g_system_token_count) +
        " tokens"
    );
}

void unload_locked() {
    if (g_grammar_template != nullptr) {
        llama_sampler_free(g_grammar_template);
        g_grammar_template = nullptr;
    }

    if (g_context != nullptr) {
        llama_free(g_context);
        g_context = nullptr;
    }

    if (g_model != nullptr) {
        llama_model_free(g_model);
        g_model = nullptr;
    }

    g_vocab = nullptr;

    g_model_path.clear();
    g_chat_template.clear();
    g_system_prompt.clear();
    g_formatted_system_prompt.clear();
    g_system_token_count = 0;

    if (g_backend_initialized) {
        llama_backend_free();
        g_backend_initialized = false;
    }
}

void load_locked(
    const std::string & model_path,
    const std::string & system_prompt
) {
    unload_locked();

    const int64_t started_us = llama_time_us();

    llama_backend_init();
    g_backend_initialized = true;

    llama_model_params model_params =
        llama_model_default_params();

    g_model = llama_model_load_from_file(
        model_path.c_str(),
        model_params
    );

    if (g_model == nullptr) {
        unload_locked();

        throw std::runtime_error(
            "failed to load Qwen GGUF: " + model_path
        );
    }

    g_vocab = llama_model_get_vocab(g_model);

    if (g_vocab == nullptr) {
        unload_locked();

        throw std::runtime_error(
            "failed to obtain Qwen vocabulary"
        );
    }

    g_grammar_template =
        llama_sampler_init_grammar(
            g_vocab,
            RESPONSE_GRAMMAR,
            "root"
        );

    if (g_grammar_template == nullptr) {
        unload_locked();

        throw std::runtime_error(
            "failed to initialize Maestro grammar at model load"
        );
    }

    log_info(
        "response grammar initialized at model load"
    );

    const char * chat_template =
        llama_model_chat_template(
            g_model,
            nullptr
        );

    if (chat_template == nullptr) {
        unload_locked();

        throw std::runtime_error(
            "Qwen GGUF has no chat template"
        );
    }

    g_chat_template = chat_template;

    llama_context_params context_params =
        llama_context_default_params();

    context_params.n_ctx = CONTEXT_SIZE;
    context_params.n_batch = BATCH_SIZE;
    context_params.n_ubatch = BATCH_SIZE;
    context_params.n_seq_max = 1;
    context_params.n_threads = N_THREADS;
    context_params.n_threads_batch = N_THREADS;

    g_context = llama_init_from_model(
        g_model,
        context_params
    );

    if (g_context == nullptr) {
        unload_locked();

        throw std::runtime_error(
            "failed to create Qwen context"
        );
    }

    g_model_path = model_path;

    try {
        cache_system_prompt(system_prompt);
    } catch (...) {
        unload_locked();
        throw;
    }

    const double elapsed_ms =
        static_cast<double>(
            llama_time_us() - started_us
        ) / 1000.0;

    log_info(
        "model loaded in " +
        std::to_string(elapsed_ms) +
        " ms; threads=" +
        std::to_string(N_THREADS) +
        "; ctx=" +
        std::to_string(CONTEXT_SIZE)
    );
}

std::string generate_locked(
    const std::string & user_prompt
) {
    if (
        g_model == nullptr ||
        g_context == nullptr ||
        g_vocab == nullptr ||
        g_grammar_template == nullptr
    ) {
        throw std::runtime_error(
            "Qwen model has not been loaded"
        );
    }

    if (user_prompt.empty()) {
        throw std::runtime_error(
            "Qwen user prompt cannot be empty"
        );
    }

    clear_turn_keep_system();

    const std::vector<llama_chat_message> messages = {
        {
            "system",
            g_system_prompt.c_str()
        },
        {
            "user",
            user_prompt.c_str()
        }
    };

    const std::string formatted_turn =
        apply_chat_template(
            messages,
            true
        );

    if (
        formatted_turn.size() <
            g_formatted_system_prompt.size() ||
        formatted_turn.compare(
            0,
            g_formatted_system_prompt.size(),
            g_formatted_system_prompt
        ) != 0
    ) {
        throw std::runtime_error(
            "Qwen chat template system prefix changed unexpectedly"
        );
    }

    const std::string turn_suffix =
        formatted_turn.substr(
            g_formatted_system_prompt.size()
        );

    const auto turn_tokens = tokenize(
        turn_suffix,
        false
    );

    if (
        static_cast<size_t>(g_system_token_count) +
            turn_tokens.size() +
            MAX_GENERATED_TOKENS +
            4 >=
        static_cast<size_t>(CONTEXT_SIZE)
    ) {
        throw std::runtime_error(
            "Qwen request exceeds Maestro context limit"
        );
    }

    const int64_t prompt_started_us =
        llama_time_us();

    try {
        decode_tokens(turn_tokens);
    } catch (...) {
        clear_turn_keep_system();
        throw;
    }

    const int64_t prompt_finished_us =
        llama_time_us();

    llama_sampler * sampler =
        llama_sampler_chain_init(
            llama_sampler_chain_default_params()
        );

    if (sampler == nullptr) {
        clear_turn_keep_system();

        throw std::runtime_error(
            "failed to create Qwen sampler chain"
        );
    }

    llama_sampler * grammar =
        llama_sampler_clone(
            g_grammar_template
        );

    if (grammar == nullptr) {
        llama_sampler_free(sampler);
        clear_turn_keep_system();

        throw std::runtime_error(
            "failed to clone Maestro response grammar"
        );
    }

    llama_sampler_chain_add(
        sampler,
        grammar
    );

    llama_sampler_chain_add(
        sampler,
        llama_sampler_init_greedy()
    );

    std::string output;
    int generated_tokens = 0;

    const int64_t generation_started_us =
        llama_time_us();

    try {
        while (
            generated_tokens <
            MAX_GENERATED_TOKENS
        ) {
            const llama_token token =
                llama_sampler_sample(
                    sampler,
                    g_context,
                    -1
                );

            if (
                llama_vocab_is_eog(
                    g_vocab,
                    token
                )
            ) {
                break;
            }

            output += token_to_piece(token);

            decode_token(token);
            generated_tokens++;
        }
    } catch (...) {
        llama_sampler_free(sampler);
        clear_turn_keep_system();
        throw;
    }

    const int64_t generation_finished_us =
        llama_time_us();

    llama_sampler_free(sampler);
    clear_turn_keep_system();

    const double prompt_ms =
        static_cast<double>(
            prompt_finished_us -
            prompt_started_us
        ) / 1000.0;

    const double generation_ms =
        static_cast<double>(
            generation_finished_us -
            generation_started_us
        ) / 1000.0;

    log_info(
        "generation completed; prompt_ms=" +
        std::to_string(prompt_ms) +
        "; generation_ms=" +
        std::to_string(generation_ms) +
        "; generated_tokens=" +
        std::to_string(generated_tokens)
    );

    return output;
}

} // namespace

extern "C"
JNIEXPORT void JNICALL
Java_br_org_agroturtles_maestro_platform_MaestroQwenNative_load(
    JNIEnv * env,
    jobject,
    jstring jmodel_path,
    jstring jsystem_prompt
) {
    std::lock_guard<std::mutex> lock(g_mutex);

    try {
        load_locked(
            jstring_to_string(
                env,
                jmodel_path
            ),
            jstring_to_string(
                env,
                jsystem_prompt
            )
        );
    } catch (const std::exception & error) {
        log_error(error.what());

        throw_java_exception(
            env,
            "java/lang/IllegalStateException",
            error.what()
        );
    }
}

extern "C"
JNIEXPORT void JNICALL
Java_br_org_agroturtles_maestro_platform_MaestroQwenNative_setSystemPrompt(
    JNIEnv * env,
    jobject,
    jstring jsystem_prompt
) {
    std::lock_guard<std::mutex> lock(g_mutex);

    try {
        cache_system_prompt(
            jstring_to_string(
                env,
                jsystem_prompt
            )
        );
    } catch (const std::exception & error) {
        log_error(error.what());

        throw_java_exception(
            env,
            "java/lang/IllegalStateException",
            error.what()
        );
    }
}

extern "C"
JNIEXPORT jstring JNICALL
Java_br_org_agroturtles_maestro_platform_MaestroQwenNative_generate(
    JNIEnv * env,
    jobject,
    jstring juser_prompt
) {
    std::lock_guard<std::mutex> lock(g_mutex);

    try {
        const std::string result =
            generate_locked(
                jstring_to_string(
                    env,
                    juser_prompt
                )
            );

        return env->NewStringUTF(
            result.c_str()
        );
    } catch (const std::exception & error) {
        log_error(error.what());

        throw_java_exception(
            env,
            "java/lang/IllegalStateException",
            error.what()
        );

        return nullptr;
    }
}

extern "C"
JNIEXPORT jstring JNICALL
Java_br_org_agroturtles_maestro_platform_MaestroQwenNative_systemInfo(
    JNIEnv * env,
    jobject
) {
    std::lock_guard<std::mutex> lock(g_mutex);

    const char * info =
        llama_print_system_info();

    return env->NewStringUTF(
        info == nullptr ? "" : info
    );
}

extern "C"
JNIEXPORT void JNICALL
Java_br_org_agroturtles_maestro_platform_MaestroQwenNative_unload(
    JNIEnv *,
    jobject
) {
    std::lock_guard<std::mutex> lock(g_mutex);
    unload_locked();
}
