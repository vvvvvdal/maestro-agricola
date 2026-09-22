package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test


class JevEvaluationTest {

    @Test
    fun preservesSuccessfulChoiceTelemetryOutsideIntentPrediction() {
        val answer = JevChoiceAnswer(
            choice = "SPRAY",
            probabilities = mapOf(
                "SPRAY" to 0.82,
                "UNKNOWN" to 0.18,
            ),
            confidence = 0.64,
        )
        val evaluation = JevEvaluation(
            requestedModel = "jev-1.13.0",
            responseModel = "jev-1.13.0",
            answer = answer,
            usage = JevUsage(inputTokens = 42, outputTokens = 7),
            latencyMs = 91,
            costUsd = 0.000001764,
        )

        assertEquals("SPRAY", evaluation.answer?.choice)
        assertEquals(0.82, evaluation.answer?.probabilities?.get("SPRAY") ?: 0.0, 0.0)
        assertEquals(0.64, evaluation.answer?.confidence ?: 0.0, 0.0)
        assertEquals("jev-1.13.0", evaluation.responseModel)
        assertEquals(42, evaluation.usage?.inputTokens)
        assertEquals(91, evaluation.latencyMs)
        assertEquals(0.000001764, evaluation.costUsd ?: 0.0, 0.0)
        assertNull(evaluation.error)
    }

    @Test
    fun mapsSelectedProbabilityInsteadOfJevConfidence() {
        val answer = JevChoiceAnswer(
            choice = "SPRAY",
            probabilities = mapOf(
                "SPRAY" to 0.82,
                "UNKNOWN" to 0.18,
            ),
            confidence = 0.64,
        )

        val prediction = answer.toIntentPrediction()

        assertEquals("SPRAY", prediction.label)
        assertEquals(0.82, prediction.confidence, 0.0)
        assertEquals("JEV", prediction.source)
        assertEquals(0.64, answer.confidence, 0.0)
    }

    @Test
    fun preservesFailureTelemetryWithoutChoiceAnswer() {
        val evaluation = JevEvaluation(
            requestedModel = "jev-1.13.0",
            latencyMs = 2_000,
            error = JevEvaluationError(
                code = JevErrorCode.TIMEOUT,
                detail = "request deadline elapsed",
            ),
        )

        assertNull(evaluation.answer)
        assertNull(evaluation.responseModel)
        assertNull(evaluation.usage)
        assertNull(evaluation.costUsd)
        assertEquals(JevErrorCode.TIMEOUT, evaluation.error?.code)
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsChoiceAnswerWithError() {
        JevEvaluation(
            requestedModel = "jev-1.13.0",
            responseModel = "jev-1.13.0",
            answer = JevChoiceAnswer(
                choice = "UNKNOWN",
                probabilities = mapOf("UNKNOWN" to 1.0),
                confidence = 1.0,
            ),
            usage = JevUsage(inputTokens = 1, outputTokens = 1),
            latencyMs = 1,
            error = JevEvaluationError(code = JevErrorCode.INVALID_RESPONSE),
        )
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsChoiceWithoutSelectedProbability() {
        JevChoiceAnswer(
            choice = "SPRAY",
            probabilities = mapOf("UNKNOWN" to 1.0),
            confidence = 0.2,
        ).toIntentPrediction()
    }

    @Test
    fun retriesOnlyFirstRateLimitOrOverloadWithinDelayBudget() {
        val policy = JevRequestPolicy()

        assertEquals(
            750L,
            policy.retryDelayMs(
                JevEvaluationError(
                    code = JevErrorCode.RATE_LIMITED,
                    retryAfterMs = 750,
                ),
                completedAttempts = 1,
            ),
        )
        assertEquals(
            250L,
            policy.retryDelayMs(
                JevEvaluationError(code = JevErrorCode.OVERLOADED),
                completedAttempts = 1,
            ),
        )
        assertNull(
            policy.retryDelayMs(
                JevEvaluationError(code = JevErrorCode.RATE_LIMITED),
                completedAttempts = 2,
            ),
        )
        assertNull(
            policy.retryDelayMs(
                JevEvaluationError(
                    code = JevErrorCode.RATE_LIMITED,
                    retryAfterMs = 1_001,
                ),
                completedAttempts = 1,
            ),
        )
    }

    @Test
    fun failsClosedForNonRetryableFailures() {
        val policy = JevRequestPolicy()
        val nonRetryableCodes = listOf(
            JevErrorCode.TIMEOUT,
            JevErrorCode.UNAUTHORIZED,
            JevErrorCode.INVALID_REQUEST,
            JevErrorCode.INVALID_RESPONSE,
            JevErrorCode.TRANSPORT,
            JevErrorCode.HTTP_ERROR,
        )

        nonRetryableCodes.forEach { code ->
            assertNull(policy.retryDelayMs(JevEvaluationError(code = code), completedAttempts = 1))
        }
    }

    @Test
    fun classifiesOfficialHttpStatuses() {
        assertEquals(JevErrorCode.UNAUTHORIZED, JevErrorCode.fromHttpStatus(401))
        assertEquals(JevErrorCode.INVALID_REQUEST, JevErrorCode.fromHttpStatus(422))
        assertEquals(JevErrorCode.RATE_LIMITED, JevErrorCode.fromHttpStatus(429))
        assertEquals(JevErrorCode.OVERLOADED, JevErrorCode.fromHttpStatus(529))
        assertEquals(JevErrorCode.HTTP_ERROR, JevErrorCode.fromHttpStatus(500))
    }
}
