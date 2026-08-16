package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Test


class InteractionEngineTest {
    @Test
    fun requiresConfirmationBeforeCommand() {
        val labels = ArrayDeque(listOf("SPRAY", "CONFIRM"))
        val engine = InteractionEngine { IntentPrediction(labels.removeFirst(), 0.99) }
        engine.observeTarget("plot-03")
        val requested = engine.handleTranscript("pulverizar")
        assertEquals(InteractionState.AWAITING_CONFIRMATION, requested.state)
        val confirmed = engine.handleTranscript("confirmar")
        assertEquals(InteractionState.SENDING, confirmed.state)
        assertNotNull(confirmed.command)
    }

    @Test
    fun cancelNeverCreatesCommand() {
        val labels = ArrayDeque(listOf("SPRAY", "CANCEL"))
        val engine = InteractionEngine { IntentPrediction(labels.removeFirst(), 0.99) }
        engine.observeTarget("plot-03")
        engine.handleTranscript("pulverizar")
        val cancelled = engine.handleTranscript("cancelar")
        assertEquals(InteractionState.CANCELLED, cancelled.state)
        assertEquals(null, cancelled.command)
    }

    @Test
    fun timeoutNeverCreatesCommand() {
        val engine = InteractionEngine { IntentPrediction("SPRAY", 0.99) }
        engine.observeTarget("plot-03")
        engine.handleTranscript("pulverizar")
        val timedOut = engine.confirmationTimedOut()
        assertEquals(InteractionState.CANCELLED, timedOut.state)
        assertEquals(null, timedOut.command)
    }
}
