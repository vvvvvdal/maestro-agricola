package br.org.agroturtles.maestro.ui

import br.org.agroturtles.maestro.domain.InteractionState
import br.org.agroturtles.maestro.domain.JevChoiceAnswer
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test


class JourneyPresentationTest {

    @Test
    fun sprayJourneyWalksEveryStep() {
        assertEquals(
            listOf(StepStatus.ACTIVE, StepStatus.PENDING, StepStatus.PENDING, StepStatus.PENDING),
            journeySteps(InteractionState.IDLE, null).map { it.status },
        )
        assertEquals(
            listOf(StepStatus.DONE, StepStatus.ACTIVE, StepStatus.PENDING, StepStatus.PENDING),
            journeySteps(InteractionState.TARGET_READY, null).map { it.status },
        )
        assertEquals(
            listOf(StepStatus.DONE, StepStatus.DONE, StepStatus.ACTIVE, StepStatus.PENDING),
            journeySteps(InteractionState.AWAITING_CONFIRMATION, "SPRAY").map { it.status },
        )
        assertEquals(
            listOf(StepStatus.DONE, StepStatus.DONE, StepStatus.DONE, StepStatus.DONE),
            journeySteps(InteractionState.ACCEPTED, "SPRAY").map { it.status },
        )
    }

    @Test
    fun dockAndUndockSkipTheTargetStep() {
        listOf("DOCK", "UNDOCK").forEach { intent ->
            assertEquals(
                StepStatus.SKIPPED,
                journeySteps(InteractionState.AWAITING_CONFIRMATION, intent).first().status,
            )
            assertEquals("não requer alvo", targetValue(intent, null))
        }
    }

    @Test
    fun unsafeOutcomesNeverLookLikeExecution() {
        val cancelled = journeySteps(InteractionState.CANCELLED, null).map { it.status }
        assertEquals(StepStatus.BLOCKED, cancelled[2])
        assertEquals(StepStatus.PENDING, cancelled[3])

        val ambiguous = journeySteps(InteractionState.AMBIGUOUS, "SPRAY").map { it.status }
        assertEquals(StepStatus.BLOCKED, ambiguous[0])
        assertEquals(StepStatus.PENDING, ambiguous[3])

        val rejected = journeySteps(InteractionState.ERROR, "SPRAY").map { it.status }
        assertEquals(StepStatus.BLOCKED, rejected[3])
    }

    @Test
    fun pendingConfirmationUsesTheAttentionTone() {
        assertEquals(
            Tone.ATTENTION,
            statusHeadline(InteractionState.AWAITING_CONFIRMATION).tone,
        )
        assertEquals(Tone.SUCCESS, statusHeadline(InteractionState.ACCEPTED).tone)
        assertEquals(Tone.DANGER, statusHeadline(InteractionState.ERROR).tone)
    }

    @Test
    fun targetDetailExposesResolutionSource() {
        assertEquals("talhão 3 · câmera", targetDetail("SPRAY", "plot-03", "VISUAL"))
        assertEquals("talhão 2 · voz", targetDetail("SPRAY", "plot-02", "VOICE"))
        assertEquals("talhão 1 · câmera e voz", targetDetail("SPRAY", "plot-01", "AGREED"))
        assertEquals("olhe para a placa ou diga o ID", targetDetail("SPRAY", null, null))
    }

    @Test
    fun robotCardDescribesTheLastAcceptedCommand() {
        assertEquals(UnknownRobotPresentation, robotPresentation(null, null))
        assertEquals("Saindo da doca", robotPresentation("UNDOCK", null).title)
        assertEquals("Retornando à doca", robotPresentation("DOCK", null).title)

        val spraying = robotPresentation("SPRAY", "plot-02")
        assertEquals("Navegando", spraying.title)
        assertEquals("destino talhão 2 · permanece no destino", spraying.detail)
    }

    @Test
    fun predictionDetailKeepsConfidenceAndSourceVisible() {
        assertEquals("SPRAY · 87% · Jev", predictionDetail("SPRAY", 0.87, "JEV"))
        assertEquals("DOCK · 91% · Jev", predictionDetail("DOCK", 0.91, "JEV"))
        assertEquals("SPRAY · 97% · modelo local", predictionDetail("SPRAY", 0.9712, "MODEL"))
        assertEquals("CONFIRM · 100% · regra determinística", predictionDetail("CONFIRM", 1.0, "RULE"))
        assertEquals("classificador local", predictionSourceLabel(null))
        assertEquals("aguardando fala", predictionDetail(null, null, null))
    }

    @Test
    fun jevIntentStatesKeepUnknownAndUnavailableSafe() {
        assertEquals(
            IntentPresentation("Pulverizar", "SPRAY · 87% · Jev", Tone.INFO),
            intentPresentation("SPRAY", "SPRAY", 0.87, "JEV"),
        )
        assertEquals(
            IntentPresentation("Retornar à doca", "DOCK · 91% · Jev", Tone.INFO),
            intentPresentation("DOCK", "DOCK", 0.91, "JEV"),
        )
        assertEquals(
            IntentPresentation(
                "Não reconhecida",
                "UNKNOWN · 42% · Jev · nenhum comando enviado",
                Tone.ATTENTION,
            ),
            intentPresentation(null, "UNKNOWN", 0.42, "JEV"),
        )
        assertEquals(
            IntentPresentation(
                "Classificação indisponível",
                "sem decisão remota · nenhum comando enviado",
                Tone.ATTENTION,
            ),
            intentPresentation(null, "UNKNOWN", 0.0, "JEV"),
        )
    }

    @Test
    fun jevDiagnosticsAreStructuredAndRestrictedToMock() {
        val answer = JevChoiceAnswer(
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

        val diagnostic = requireNotNull(jevDiagnosticPresentation(answer))
        assertEquals("SPRAY", diagnostic.choice)
        assertEquals("87%", diagnostic.selectedProbability)
        assertEquals("74%", diagnostic.confidence)
        assertEquals(
            listOf("SPRAY", "DOCK", "UNDOCK", "CONFIRM", "CANCEL", "UNKNOWN"),
            diagnostic.rows.map { it.label },
        )
        assertFalse(shouldShowJevDiagnostics("dat", diagnostic))
        assertFalse(shouldShowJevDiagnostics("mock", null))
        assertTrue(shouldShowJevDiagnostics("mock", diagnostic))
    }

    @Test
    fun factCardDescriptionKeepsJevDecisionContextTogether() {
        assertEquals(
            "INTENÇÃO: Pulverizar. SPRAY · 87% · Jev.",
            factCardContentDescription("INTENÇÃO", "Pulverizar", "SPRAY · 87% · Jev"),
        )
    }
}
