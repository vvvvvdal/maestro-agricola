package br.org.agroturtles.maestro.platform


fun interface FrameSource {
    fun captureTarget(completion: (Result<String>) -> Unit)
}
