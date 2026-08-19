package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
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
    fun explicitCancelAndLateConfirmationNeverCreateCommand() {
        val labels = ArrayDeque(listOf("SPRAY", "CANCEL", "CONFIRM"))
        val engine = InteractionEngine { IntentPrediction(labels.removeFirst(), 0.99) }
        engine.observeTarget("plot-03")
        engine.handleTranscript("pulverizar")
        val cancelled = engine.handleTranscript("cancelar")
        assertEquals(InteractionState.CANCELLED, cancelled.state)
        assertNull(cancelled.command)

        val lateConfirmation = engine.handleTranscript("confirmar")
        assertEquals(InteractionState.CANCELLED, lateConfirmation.state)
        assertNull(lateConfirmation.command)
    }

    @Test
    fun timeoutAndLateConfirmationNeverCreateCommand() {
        val labels = ArrayDeque(listOf("SPRAY", "CONFIRM"))
        val engine = InteractionEngine { IntentPrediction(labels.removeFirst(), 0.99) }
        engine.observeTarget("plot-03")
        engine.handleTranscript("pulverizar")
        val timedOut = engine.confirmationTimedOut()
        assertEquals(InteractionState.CANCELLED, timedOut.state)
        assertNull(timedOut.command)

        val lateConfirmation = engine.handleTranscript("confirmar")
        assertEquals(InteractionState.CANCELLED, lateConfirmation.state)
        assertNull(lateConfirmation.command)
    }

    @Test
    fun ambiguousConfirmationCanBeRetriedWithoutEarlyCommand() {
        val labels = ArrayDeque(listOf("SPRAY", "UNKNOWN", "CONFIRM"))
        val engine = InteractionEngine { IntentPrediction(labels.removeFirst(), 0.99) }
        engine.observeTarget("plot-03")
        engine.handleTranscript("pulverizar")

        val ambiguous = engine.handleTranscript("talvez")
        assertEquals(InteractionState.AWAITING_CONFIRMATION, ambiguous.state)
        assertNull(ambiguous.command)

        val retried = engine.handleTranscript("confirmar")
        assertEquals(InteractionState.SENDING, retried.state)
        assertNotNull(retried.command)
    }

    @Test
    fun unknownIntentNeverCreatesCommand() {
        val engine = InteractionEngine { IntentPrediction("UNKNOWN", 0.20) }
        engine.observeTarget("plot-03")

        val unknown = engine.handleTranscript("qual a previsão do tempo")
        assertEquals(InteractionState.TARGET_READY, unknown.state)
        assertNull(unknown.command)
    }

    @Test
    fun missingTargetNeverCreatesCommand() {
        val engine = InteractionEngine { IntentPrediction("SPRAY", 0.99) }

        val missing = engine.handleTranscript("pulverizar esta área")
        assertEquals(InteractionState.AMBIGUOUS, missing.state)
        assertNull(missing.command)
    }

    @Test
    fun unknownTargetNeverCreatesCommand() {
        val engine = InteractionEngine { IntentPrediction("SPRAY", 0.99) }

        val unknown = engine.handleTranscript("pulverize no plot quatro")
        assertEquals(InteractionState.AMBIGUOUS, unknown.state)
        assertNull(unknown.command)
    }

    @Test
    fun explicitSpokenTargetWorksWithoutVisualMarker() {
        val labels = ArrayDeque(listOf("SPRAY", "CONFIRM"))
        val engine = InteractionEngine { IntentPrediction(labels.removeFirst(), 0.99) }
        val requested = engine.handleTranscript("pulverize no plot-03")
        assertEquals(InteractionState.AWAITING_CONFIRMATION, requested.state)
        val confirmed = engine.handleTranscript("confirmar")
        assertEquals("plot-03", confirmed.command?.targetId)
    }

    @Test
    fun visualAndSpokenConflictRejectsLateConfirmation() {
        val labels = ArrayDeque(listOf("SPRAY", "CONFIRM"))
        val engine = InteractionEngine { IntentPrediction(labels.removeFirst(), 0.99) }
        engine.observeTarget("plot-03")
        val conflict = engine.handleTranscript("pulverize no plot quatro")
        assertEquals(InteractionState.AMBIGUOUS, conflict.state)
        assertNull(conflict.command)

        val lateConfirmation = engine.handleTranscript("confirmar")
        assertEquals(InteractionState.AMBIGUOUS, lateConfirmation.state)
        assertNull(lateConfirmation.command)
    }
}
