package br.org.agroturtles.maestro.platform

import android.os.Handler
import android.os.Looper
import br.org.agroturtles.maestro.domain.QwenEngine
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicBoolean

class NativeQwenEngine(
    private val modelPath: String,
) : QwenEngine, AutoCloseable {

    private val worker =
        Executors.newSingleThreadExecutor { runnable ->
            Thread(
                runnable,
                "maestro-qwen"
            ).apply {
                isDaemon = true
            }
        }

    private val mainHandler =
        Handler(Looper.getMainLooper())

    private val closed =
        AtomicBoolean(false)

    private var loaded = false
    private var loadedSystemPrompt: String? = null

    init {
        require(modelPath.isNotBlank()) {
            "Qwen model path cannot be blank"
        }
    }

    override fun generate(
        systemPrompt: String,
        userPrompt: String,
        completion: (Result<String>) -> Unit,
    ) {
        if (closed.get()) {
            completion(
                Result.failure(
                    IllegalStateException(
                        "NativeQwenEngine is closed"
                    )
                )
            )
            return
        }

        worker.execute {
            val result = runCatching {
                check(!closed.get()) {
                    "NativeQwenEngine is closed"
                }

                ensureLoaded(systemPrompt)

                MaestroQwenNative.generate(
                    userPrompt
                )
            }

            mainHandler.post {
                completion(result)
            }
        }
    }

    private fun ensureLoaded(
        systemPrompt: String,
    ) {
        if (!loaded) {
            MaestroQwenNative.load(
                modelPath = modelPath,
                systemPrompt = systemPrompt,
            )

            loaded = true
            loadedSystemPrompt = systemPrompt
            return
        }

        if (
            loadedSystemPrompt !=
            systemPrompt
        ) {
            MaestroQwenNative.setSystemPrompt(
                systemPrompt
            )

            loadedSystemPrompt =
                systemPrompt
        }
    }

    fun systemInfo(
        completion: (Result<String>) -> Unit,
    ) {
        if (closed.get()) {
            completion(
                Result.failure(
                    IllegalStateException(
                        "NativeQwenEngine is closed"
                    )
                )
            )
            return
        }

        worker.execute {
            val result = runCatching {
                MaestroQwenNative.systemInfo()
            }

            mainHandler.post {
                completion(result)
            }
        }
    }

    override fun close() {
        if (
            !closed.compareAndSet(
                false,
                true
            )
        ) {
            return
        }

        worker.execute {
            if (loaded) {
                runCatching {
                    MaestroQwenNative.unload()
                }

                loaded = false
                loadedSystemPrompt = null
            }

            worker.shutdown()
        }
    }
}
