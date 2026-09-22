package br.org.agroturtles.maestro.platform

import br.org.agroturtles.maestro.domain.JevChoiceAnswer

/** Static local fixtures for mock-only JEV presentation scenarios. */
object JevTestDiagnostics {
    private val fixtures = listOf(
        JevChoiceAnswer(
            choice = "SPRAY",
            probabilities = linkedMapOf(
                "SPRAY" to 0.87,
                "DOCK" to 0.03,
                "UNDOCK" to 0.02,
                "CONFIRM" to 0.01,
                "CANCEL" to 0.01,
                "UNKNOWN" to 0.06,
            ),
            confidence = 0.74,
        ),
        JevChoiceAnswer(
            choice = "UNKNOWN",
            probabilities = linkedMapOf(
                "SPRAY" to 0.05,
                "DOCK" to 0.04,
                "UNDOCK" to 0.03,
                "CONFIRM" to 0.02,
                "CANCEL" to 0.01,
                "UNKNOWN" to 0.85,
            ),
            confidence = 0.81,
        ),
    )

    fun scenarios(): List<JevChoiceAnswer> = fixtures

    fun current(): JevChoiceAnswer? = fixtures.firstOrNull()
}
