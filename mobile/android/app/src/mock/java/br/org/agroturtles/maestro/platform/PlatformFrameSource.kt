package br.org.agroturtles.maestro.platform


class PlatformFrameSource : FrameSource {
    override fun captureTarget(completion: (Result<String>) -> Unit) {
        completion(Result.success("plot-03"))
    }
}
