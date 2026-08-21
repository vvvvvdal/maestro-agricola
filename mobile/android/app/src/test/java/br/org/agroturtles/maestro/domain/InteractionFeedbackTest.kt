package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test


/**
 * Cobre o retrato da jornada e as mensagens faladas consumidas pela tela de
 * demonstração. As garantias de segurança continuam em `InteractionEngineTest`.
 */
class InteractionFeedbackTest {

    @Test
    fun everyResultCarriesTheJourneySnapshot() {
        val labels = ArrayDeque(listOf("SPRAY", "CONFIRM"))
        val engine = InteractionEngine { IntentPrediction(labels.removeFirst(), 0.99) }

        val observed = engine.observeTarget("plot-03")
        assertEquals("plot-03", observed.targetId)
        assertEquals("VISUAL", observed.targetSource)
        assertNull(observed.intent)

        val requested = engine.handleTranscript("pulverizar")
        assertEquals("SPRAY", requested.intent)
        assertEquals("plot-03", requested.targetId)
        assertEquals("VISUAL", requested.targetSource)

        val confirmed = engine.handleTranscript("confirmar")
        assertEquals("SPRAY", confirmed.intent)
        assertEquals("plot-03", confirmed.targetId)

        val accepted = engine.transportCompleted(true, "navigation goal queued")
        assertEquals("SPRAY", accepted.intent)
        assertEquals("plot-03", accepted.targetId)
    }

    @Test
    fun spokenTargetIsReportedAsVoiceResolution() {
        val engine = InteractionEngine { IntentPrediction("SPRAY", 0.99) }

        val requested = engine.handleTranscript("pulverize no plot dois")

        assertEquals("plot-02", requested.targetId)
        assertEquals("VOICE", requested.targetSource)
    }

    @Test
    fun resetClearsTheSnapshot() {
        val engine = InteractionEngine { IntentPrediction("SPRAY", 0.99) }
        engine.observeTarget("plot-03")

        val reset = engine.reset()

        assertNull(reset.intent)
        assertNull(reset.targetId)
        assertNull(reset.targetSource)
    }

    @Test
    fun confirmationPromptIsSpokenInNaturalPortuguese() {
        val engine = InteractionEngine { IntentPrediction("SPRAY", 0.99) }
        engine.observeTarget("plot-03")

        val requested = engine.handleTranscript("pulverizar")

        assertEquals("Pulverizar plot-03?", requested.message)
        assertEquals("Pulverizar talhão 3. Confirmar?", requested.speech)
    }

    @Test
    fun dockAndUndockPromptsUseTheOperatorVocabulary() {
        val dock = InteractionEngine { IntentPrediction("DOCK", 0.99) }
        val dockRequest = dock.handleTranscript("volte para a base")
        assertEquals("Retornar à doca?", dockRequest.message)
        assertEquals("Retornar à doca. Confirmar?", dockRequest.speech)

        val undock = InteractionEngine { IntentPrediction("UNDOCK", 0.99) }
        val undockRequest = undock.handleTranscript("saia da doca")
        assertEquals("Sair da doca?", undockRequest.message)
        assertEquals("Sair da doca. Confirmar?", undockRequest.speech)
    }

    @Test
    fun acceptedCommandIsAnnouncedPerIntent() {
        val spray = ArrayDeque(listOf("SPRAY", "CONFIRM"))
        val sprayEngine = InteractionEngine { IntentPrediction(spray.removeFirst(), 0.99) }
        sprayEngine.observeTarget("plot-02")
        sprayEngine.handleTranscript("pulverizar")
        sprayEngine.handleTranscript("confirmar")
        assertEquals(
            "Comando aceito. Indo pulverizar o talhão 2.",
            sprayEngine.transportCompleted(true, "navigation goal queued").speech,
        )

        val undock = ArrayDeque(listOf("UNDOCK", "CONFIRM"))
        val undockEngine = InteractionEngine { IntentPrediction(undock.removeFirst(), 0.99) }
        undockEngine.handleTranscript("saia da doca")
        undockEngine.handleTranscript("confirmar")
        assertEquals(
            "Comando aceito. Saindo da doca.",
            undockEngine.transportCompleted(true, "undock queued").speech,
        )
    }

    @Test
    fun rejectionIsSpokenWithoutReadingTheTechnicalReason() {
        val labels = ArrayDeque(listOf("SPRAY", "CONFIRM"))
        val engine = InteractionEngine { IntentPrediction(labels.removeFirst(), 0.99) }
        engine.observeTarget("plot-03")
        engine.handleTranscript("pulverizar")
        engine.handleTranscript("confirmar")

        val rejected = engine.transportCompleted(false, "robot unavailable: robot is docked")

        assertEquals(InteractionState.ERROR, rejected.state)
        assertEquals("robot unavailable: robot is docked", rejected.message)
        assertEquals("Comando recusado pelo robô. Nada foi executado.", rejected.speech)
    }

    @Test
    fun unrecognizedIntentSuggestsTheSupportedCommands() {
        val engine = InteractionEngine { IntentPrediction("UNKNOWN", 0.20) }

        val unknown = engine.handleTranscript("qual a previsão do tempo")

        assertNull(unknown.command)
        assertEquals(
            "Não entendi. Diga pulverizar, sair da doca ou retornar à doca.",
            unknown.speech,
        )
    }

    @Test
    fun ambiguousConfirmationRepeatsTheSafeVocabulary() {
        val labels = ArrayDeque(listOf("SPRAY", "UNKNOWN"))
        val engine = InteractionEngine { IntentPrediction(labels.removeFirst(), 0.99) }
        engine.observeTarget("plot-03")
        engine.handleTranscript("pulverizar")

        val ambiguous = engine.handleTranscript("talvez")

        assertEquals(InteractionState.AWAITING_CONFIRMATION, ambiguous.state)
        assertNull(ambiguous.command)
        assertEquals(
            "Não entendi. Diga sim para confirmar ou cancelar para abortar.",
            ambiguous.speech,
        )
    }

    @Test
    fun timeoutIsAnnouncedAsCancellation() {
        val engine = InteractionEngine { IntentPrediction("SPRAY", 0.99) }
        engine.observeTarget("plot-03")
        engine.handleTranscript("pulverizar")

        val timedOut = engine.confirmationTimedOut()

        assertNotNull(timedOut.speech)
        assertTrue(timedOut.speech!!.contains("cancelada", ignoreCase = true))
        assertNull(timedOut.intent)
        assertNull(timedOut.targetId)
    }

    @Test
    fun targetCaptureFailureIsFailClosedAndCanBeReset() {
        val engine = InteractionEngine { IntentPrediction("SPRAY", 0.99) }

        val failed = engine.targetCaptureFailed("Câmera indisponível")

        assertEquals(InteractionState.ERROR, failed.state)
        assertEquals("Câmera indisponível", failed.message)
        assertNull(failed.command)
        assertNull(failed.targetId)
        assertTrue(failed.speech!!.contains("Nada foi enviado"))

        val reset = engine.reset()
        assertEquals(InteractionState.IDLE, reset.state)
    }

    @Test
    fun plotLabelReadsAsSpokenPortuguese() {
        assertEquals("talhão 3", plotLabel("plot-03"))
        assertEquals("talhão 12", plotLabel("plot-12"))
        assertEquals("alvo desconhecido", plotLabel(null))
    }
}
