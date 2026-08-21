#include <jni.h>

#include "llama.h"

extern "C"
JNIEXPORT jstring JNICALL
Java_br_org_agroturtles_maestro_ai_MaestroQwenNative_nativeSystemInfo(
        JNIEnv * env,
        jobject /* thiz */) {
    const char * info = llama_print_system_info();

    if (info == nullptr) {
        return env->NewStringUTF("");
    }

    return env->NewStringUTF(info);
}
