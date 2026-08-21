package br.org.agroturtles.maestro.platform

import java.time.Instant


data class TargetObservation(
    val targetId: String,
    val observedAt: String,
) {
    companion object {
        fun now(targetId: String): TargetObservation = TargetObservation(
            targetId = targetId,
            observedAt = Instant.now().toString(),
        )
    }
}


interface FrameSource : AutoCloseable {
    fun captureTarget(completion: (Result<TargetObservation>) -> Unit)

    fun cancelCapture() = Unit

    override fun close() = Unit
}
