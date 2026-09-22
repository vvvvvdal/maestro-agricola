package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class FakeJevChoiceEvaluatorTest {

    private val fake = FakeJevChoiceEvaluator(
        mapOf(
            "pulverize o talhao dois" to successfulEvaluation("SPRAY", 0.91),
            "talvez pulverize o talhao dois" to successfulEvaluation("SPRAY", 0.23),
            "timeout" to failedEvaluation(JevErrorCode.TIMEOUT),
            "rate limited" to failedEvaluation(
                code = JevErrorCode.RATE_LIMITED,
                retryAfterMs = 750,
            ),
            "invalid choice" to failedEvaluation(JevErrorCode.INVALID_RESPONSE),
        ),
    )

    @Test
    fun returnsValidAndLowProbabilityChoicesDeterministically() {
        val valid = fake.evaluate("pulverize o talhao dois")
        val lowProbability = fake.evaluate("talvez pulverize o talhao dois")

        assertEquals("SPRAY", valid.answer?.choice)
        assertEquals(0.91, valid.answer?.probabilities?.get("SPRAY") ?: 0.0, 0.0)
        assertEquals("SPRAY", lowProbability.answer?.choice)
        assertEquals(0.23, lowProbability.answer?.probabilities?.get("SPRAY") ?: 0.0, 0.0)
        assertNull(valid.error)
        assertNull(lowProbability.error)
    }

    @Test
    fun returnsConfiguredFailuresWithoutChoiceAnswers() {
        val timeout = fake.evaluate("timeout")
        val rateLimited = fake.evaluate("rate limited")
        val invalidChoice = fake.evaluate("invalid choice")

        assertFailure(timeout, JevErrorCode.TIMEOUT)
        assertFailure(rateLimited, JevErrorCode.RATE_LIMITED)
        assertEquals(750L, rateLimited.error?.retryAfterMs)
        assertFailure(invalidChoice, JevErrorCode.INVALID_RESPONSE)
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsAnUnconfiguredText() {
        fake.evaluate("not configured")
    }

    private fun assertFailure(evaluation: JevEvaluation, code: JevErrorCode) {
        assertNull(evaluation.answer)
        assertEquals(code, evaluation.error?.code)
    }

    private companion object {
        fun successfulEvaluation(choice: String, probability: Double): JevEvaluation = JevEvaluation(
            requestedModel = "jev-1.13.0",
            responseModel = "jev-1.13.0",
            answer = JevChoiceAnswer(
                choice = choice,
                probabilities = mapOf(choice to probability),
                confidence = probability,
            ),
            usage = JevUsage(inputTokens = 1, outputTokens = 1),
            latencyMs = 1,
        )

        fun failedEvaluation(
            code: JevErrorCode,
            retryAfterMs: Long? = null,
        ): JevEvaluation = JevEvaluation(
            requestedModel = "jev-1.13.0",
            latencyMs = 1,
            error = JevEvaluationError(
                code = code,
                retryAfterMs = retryAfterMs,
            ),
        )
    }
}
