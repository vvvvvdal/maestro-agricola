package br.org.agroturtles.maestro.domain


data class JevChoiceAnswer(
    val choice: String,
    val probabilities: Map<String, Double>,
    val confidence: Double,
)

fun JevChoiceAnswer.toIntentPrediction(): IntentPrediction {
    val selectedProbability = requireNotNull(probabilities[choice]) {
        "Choice probability is missing for $choice"
    }
    return IntentPrediction(
        label = choice,
        confidence = selectedProbability,
        source = "JEV",
    )
}

data class JevUsage(
    val inputTokens: Int,
    val outputTokens: Int,
)

enum class JevErrorCode {
    TIMEOUT,
    RATE_LIMITED,
    OVERLOADED,
    UNAUTHORIZED,
    INVALID_REQUEST,
    INVALID_RESPONSE,
    TRANSPORT,
    HTTP_ERROR,
    ;

    companion object {
        fun fromHttpStatus(statusCode: Int): JevErrorCode = when (statusCode) {
            401 -> UNAUTHORIZED
            422 -> INVALID_REQUEST
            429 -> RATE_LIMITED
            529 -> OVERLOADED
            else -> HTTP_ERROR
        }
    }
}

data class JevEvaluationError(
    val code: JevErrorCode,
    val detail: String? = null,
    val retryAfterMs: Long? = null,
) {
    init {
        require(retryAfterMs == null || retryAfterMs >= 0)
    }
}

data class JevRequestPolicy(
    val timeoutMs: Long = 2_000,
    val maxAttempts: Int = 2,
    val fallbackRetryDelayMs: Long = 250,
    val maxRetryAfterMs: Long = 1_000,
) {
    init {
        require(timeoutMs > 0)
        require(maxAttempts == 2)
        require(fallbackRetryDelayMs >= 0)
        require(maxRetryAfterMs >= fallbackRetryDelayMs)
    }

    fun retryDelayMs(error: JevEvaluationError, completedAttempts: Int): Long? {
        if (completedAttempts != 1 || error.code !in RETRYABLE_CODES) return null
        val retryAfterMs = error.retryAfterMs ?: return fallbackRetryDelayMs
        return retryAfterMs.takeIf { it in 0..maxRetryAfterMs }
    }

    private companion object {
        val RETRYABLE_CODES = setOf(
            JevErrorCode.RATE_LIMITED,
            JevErrorCode.OVERLOADED,
        )
    }
}

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
