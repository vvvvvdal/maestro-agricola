package br.org.agroturtles.maestro.platform

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Test

class JevTestDiagnosticsTest {

    @Test
    fun mockFixtureHasTheCompleteChoiceVector() {
        val answer = requireNotNull(JevTestDiagnostics.current())

        assertEquals("SPRAY", answer.choice)
        assertEquals(
            setOf("SPRAY", "DOCK", "UNDOCK", "CONFIRM", "CANCEL", "UNKNOWN"),
            answer.probabilities.keys,
        )
        assertNotNull(answer.probabilities[answer.choice])
        assertEquals(1.0, answer.probabilities.values.sum(), 0.0001)
        assertEquals(0.74, answer.confidence, 0.0)
    }
}
