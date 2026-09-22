package br.org.agroturtles.maestro.platform

import org.junit.Assert.assertEquals
import org.junit.Test

class JevTestDiagnosticsTest {

    @Test
    fun mockFixturesContainOnlyThePresentationScenarios() {
        val scenarios = JevTestDiagnostics.scenarios()

        assertEquals(listOf("SPRAY", "UNKNOWN"), scenarios.map { it.choice })
        assertEquals(scenarios.first(), JevTestDiagnostics.current())
        scenarios.forEach { answer ->
            assertEquals(
                setOf("SPRAY", "DOCK", "UNDOCK", "CONFIRM", "CANCEL", "UNKNOWN"),
                answer.probabilities.keys,
            )
            assertEquals(1.0, answer.probabilities.values.sum(), 0.0001)
            assertEquals(
                answer.probabilities.getValue(answer.choice),
                answer.probabilities.values.max(),
                0.0,
            )
        }
    }
}
