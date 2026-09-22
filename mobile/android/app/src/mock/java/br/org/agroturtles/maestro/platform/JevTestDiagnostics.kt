package br.org.agroturtles.maestro.platform

import br.org.agroturtles.maestro.domain.JevChoiceAnswer

/** Static local fixture for the mock-only JEV diagnostics panel. */
object JevTestDiagnostics {
    fun current(): JevChoiceAnswer? = JevChoiceAnswer(
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
    )
}
