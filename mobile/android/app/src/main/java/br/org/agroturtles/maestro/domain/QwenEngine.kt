package br.org.agroturtles.maestro.domain

fun interface QwenEngine {
    fun generate(
        prompt: String,
        completion: (Result<String>) -> Unit,
    )
}
