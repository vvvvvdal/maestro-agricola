package br.org.agroturtles.maestro.domain

class JevIntentClassifier(
    private val evaluator: JevChoiceEvaluator,
    private val threshold: Double = DEFAULT_THRESHOLD,
    private val cancelGuard: ExplicitCancelGuard = ExplicitCancelGuard.disabled(),
) : IntentClassifier {
    init {
        require(threshold in 0.0..1.0)
    }

    override fun classify(text: String): IntentPrediction {
        val explicitCancel = try {
            cancelGuard.matches(text)
        } catch (_: Exception) {
            return guardedCancel()
        }
        if (explicitCancel) return guardedCancel()

        val evaluation = try {
            evaluator.evaluate(text)
        } catch (_: Exception) {
            return unknown()
        }
        val answer = evaluation.answer ?: return unknown()

        if (!answer.isValidOperationalChoice()) return unknown()

        val prediction = answer.toIntentPrediction()
        return if (prediction.label != UNKNOWN && prediction.confidence < threshold) {
            unknown(prediction.confidence)
        } else {
            prediction
        }
    }

    private fun JevChoiceAnswer.isValidOperationalChoice(): Boolean {
        if (choice !in SUPPORTED_LABELS || probabilities.keys != SUPPORTED_LABELS) return false
        if (!confidence.isFinite() || confidence !in 0.0..1.0) return false
        if (probabilities.values.any { !it.isFinite() || it !in 0.0..1.0 }) return false
        if (kotlin.math.abs(probabilities.values.sum() - 1.0) > PROBABILITY_TOLERANCE) return false

        val selectedProbability = probabilities.getValue(choice)
        return probabilities.values.none { it > selectedProbability + PROBABILITY_TOLERANCE }
    }

    private fun unknown(confidence: Double = 0.0): IntentPrediction = IntentPrediction(
        label = UNKNOWN,
        confidence = confidence,
        source = SOURCE,
    )

    private fun guardedCancel(): IntentPrediction = IntentPrediction(
        label = CANCEL,
        confidence = 1.0,
        source = GUARD_SOURCE,
    )

    private companion object {
        const val CANCEL = "CANCEL"
        const val UNKNOWN = "UNKNOWN"
        const val SOURCE = "JEV"
        const val GUARD_SOURCE = "JEV_GUARD"
        const val DEFAULT_THRESHOLD = 0.40
        const val PROBABILITY_TOLERANCE = 0.001

        val SUPPORTED_LABELS = setOf(
            "SPRAY",
            "DOCK",
            "UNDOCK",
            "CONFIRM",
            "CANCEL",
            UNKNOWN,
        )
    }
}
