package br.org.agroturtles.maestro.platform

import android.app.Activity
import android.os.Bundle
import android.os.SystemClock
import android.util.Log
import android.widget.TextView
import br.org.agroturtles.maestro.domain.AssistantReply
import br.org.agroturtles.maestro.domain.AssistantReplyType
import br.org.agroturtles.maestro.domain.QwenDomainAssistant
import java.io.File

class QwenSmokeActivity : Activity() {

    private lateinit var outputView: TextView
    private lateinit var engine: NativeQwenEngine
    private lateinit var assistant: QwenDomainAssistant

    private var passed = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        outputView = TextView(this).apply {
            textSize = 16f
            setPadding(32, 32, 32, 32)
            text = "Maestro Qwen smoke test\n\nInicializando...\n"
        }

        setContentView(outputView)

        val modelFile = File(
            filesDir,
            MODEL_FILENAME,
        )

        if (!modelFile.isFile) {
            failImmediately(
                "Modelo não encontrado: ${modelFile.absolutePath}"
            )
            return
        }

        append(
            "Modelo: ${modelFile.absolutePath}\n" +
                "Tamanho: ${modelFile.length()} bytes\n\n"
        )

        engine = NativeQwenEngine(
            modelPath = modelFile.absolutePath,
        )

        assistant = QwenDomainAssistant(engine)

        runCase(0)
    }

    private fun runCase(index: Int) {
        if (index >= CASES.size) {
            finishSmokeTest()
            return
        }

        val testCase = CASES[index]

        append(
            "[$index/${CASES.size}] ${testCase.prompt}\n" +
                "Processando...\n"
        )

        val startedMs =
            SystemClock.elapsedRealtime()

        assistant.respond(testCase.prompt) { result ->
            val elapsedMs =
                SystemClock.elapsedRealtime() - startedMs

            result.fold(
                onSuccess = { reply ->
                    val success =
                        validate(
                            testCase = testCase,
                            reply = reply,
                        )

                    if (success) {
                        passed++
                    }

                    val status =
                        if (success) "PASS" else "FAIL"

                    val message =
                        buildString {
                            append("$status | ${elapsedMs} ms\n")
                            append("type=${reply.type}\n")
                            append("response=${reply.response}\n\n")
                        }

                    append(message)

                    Log.i(
                        TAG,
                        "case=${index + 1} " +
                            "status=$status " +
                            "elapsed_ms=$elapsedMs " +
                            "type=${reply.type} " +
                            "response=${reply.response}"
                    )

                    runCase(index + 1)
                },
                onFailure = { error ->
                    val message =
                        "FAIL | ${elapsedMs} ms\n" +
                            "error=${error.stackTraceToString()}\n\n"

                    append(message)

                    Log.e(
                        TAG,
                        "case=${index + 1} failed",
                        error,
                    )

                    runCase(index + 1)
                },
            )
        }
    }

    private fun validate(
        testCase: SmokeCase,
        reply: AssistantReply,
    ): Boolean {
        if (reply.type != testCase.expectedType) {
            return false
        }

        val requiredText =
            testCase.responseMustContain

        return requiredText == null ||
            reply.response.contains(
                requiredText,
                ignoreCase = true,
            )
    }

    private fun finishSmokeTest() {
        val success =
            passed == CASES.size

        val message =
            "\nRESULTADO: $passed/${CASES.size} " +
                if (success) "PASS" else "FAIL"

        append("$message\n")

        Log.i(
            TAG,
            "SMOKE_RESULT passed=$passed total=${CASES.size}"
        )

        append(
            "\nEngine continua carregado para medição de memória.\n" +
                "Feche esta tela quando terminar.\n"
        )
    }

    private fun failImmediately(message: String) {
        append("\nFAIL: $message\n")
        Log.e(TAG, message)
    }

    private fun append(message: String) {
        outputView.append(message)
    }

    override fun onDestroy() {
        if (::engine.isInitialized) {
            engine.close()
        }

        super.onDestroy()
    }

    private data class SmokeCase(
        val prompt: String,
        val expectedType: AssistantReplyType,
        val responseMustContain: String? = null,
    )

    companion object {
        private const val TAG =
            "MaestroQwenSmoke"

        private const val MODEL_FILENAME =
            "qwen2.5-1.5b-q4_k_m.gguf"

        private val CASES = listOf(
            SmokeCase(
                prompt = "O que é o Maestro Agrícola?",
                expectedType = AssistantReplyType.CHAT,
                responseMustContain = "AgroTurtles",
            ),
            SmokeCase(
                prompt = "Quem desenvolveu o Maestro Agrícola?",
                expectedType = AssistantReplyType.CHAT,
                responseMustContain = "AgroTurtles",
            ),
            SmokeCase(
                prompt = "Como funciona a confirmação de segurança?",
                expectedType = AssistantReplyType.CHAT,
                responseMustContain = "confirmação",
            ),
            SmokeCase(
                prompt = "Faça dock agora.",
                expectedType = AssistantReplyType.OUT_OF_SCOPE,
            ),
            SmokeCase(
                prompt = "Como fazer bolo de chocolate?",
                expectedType = AssistantReplyType.OUT_OF_SCOPE,
            ),
        )
    }
}
