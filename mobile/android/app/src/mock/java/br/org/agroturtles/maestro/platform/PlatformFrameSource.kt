package br.org.agroturtles.maestro.platform

import androidx.activity.ComponentActivity


class PlatformFrameSource(
    @Suppress("UNUSED_PARAMETER") activity: ComponentActivity,
    @Suppress("UNUSED_PARAMETER") targetMapJson: String,
) : FrameSource {
    override fun captureTarget(completion: (Result<TargetObservation>) -> Unit) {
        completion(Result.success(TargetObservation.now("plot-03")))
    }
}
