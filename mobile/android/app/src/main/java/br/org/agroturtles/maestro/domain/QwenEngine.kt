package br.org.agroturtles.maestro.domain

fun interface QwenEngine {
    fun generate(
        systemPrompt: String,
        userPrompt: String,
        completion: (Result<String>) -> Unit,
    )
}
