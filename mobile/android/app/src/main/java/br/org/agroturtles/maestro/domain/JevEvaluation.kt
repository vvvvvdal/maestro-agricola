package br.org.agroturtles.maestro.domain


data class JevChoiceAnswer(
    val choice: String,
    val probabilities: Map<String, Double>,
    val confidence: Double,
)

data class JevUsage(
    val inputTokens: Int,
    val outputTokens: Int,
)

data class JevEvaluationError(
    val code: String,
    val detail: String? = null,
)

/**
 * Experimental record for a single Jev Choice evaluation.
 *
 * It deliberately stays separate from IntentPrediction. JEV-22 owns the
 * mapping from a valid Choice answer to the operational classifier contract.
 */
data class JevEvaluation(
    val requestedModel: String,
    val responseModel: String? = null,
    val answer: JevChoiceAnswer? = null,
    val usage: JevUsage? = null,
    val latencyMs: Long,
    val costUsd: Double? = null,
    val error: JevEvaluationError? = null,
) {
    init {
        require(requestedModel.isNotBlank())
        require(latencyMs >= 0)
        require(costUsd == null || costUsd >= 0.0)
        require((answer == null) == (error != null))
        require((answer == null) == (responseModel == null))
        require(answer == null || usage != null)
    }
}
