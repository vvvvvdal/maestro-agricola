package br.org.agroturtles.maestro.platform


class PlatformFrameSource : FrameSource {
    override fun captureTarget(completion: (Result<String>) -> Unit) {
        completion(Result.failure(
            IllegalStateException("Conecte aqui Wearables -> DeviceSession -> Camera -> Stream.capturePhoto()")
        ))
    }
}
