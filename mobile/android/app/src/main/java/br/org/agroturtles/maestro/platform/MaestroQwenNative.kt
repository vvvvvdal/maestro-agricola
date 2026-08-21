package br.org.agroturtles.maestro.platform

internal object MaestroQwenNative {

    init {
        System.loadLibrary("maestro-qwen")
    }

    external fun load(
        modelPath: String,
        systemPrompt: String,
    )

    external fun setSystemPrompt(
        systemPrompt: String,
    )

    external fun generate(
        userPrompt: String,
    ): String

    external fun systemInfo(): String

    external fun unload()
}
