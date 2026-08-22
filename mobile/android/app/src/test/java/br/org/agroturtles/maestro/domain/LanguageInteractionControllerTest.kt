package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class LanguageInteractionControllerTest {

    @Test
    fun operationalIntentBypassesAssistant() {
        var assistantCalls = 0
        val classifier = IntentClassifier {
            IntentPrediction("DOCK", 0.99, "MODEL")
        }
        val engine = InteractionEngine(classifier)
        val controller = LanguageInteractionController(
            classifier = classifier,
            interactionEngine = engine,
            assistant = DomainAssistant { _, _ -> assistantCalls++ },
        )

        val dispatch = controller.handle("voltar para a base") { _, _ -> }

        assertTrue(dispatch is LanguageDispatch.Operational)
        val result = (dispatch as LanguageDispatch.Operational).result
        assertEquals(InteractionState.AWAITING_CONFIRMATION, result.state)
        assertEquals("DOCK", result.intent)
        assertNull(result.command)
        assertEquals(0, assistantCalls)
    }

    @Test
    fun everyOperationalLabelBypassesAssistant() {
        val cases = listOf(
            "SPRAY" to "pulverizar no plot-03",
            "DOCK" to "voltar para a base",
            "UNDOCK" to "sair da doca",
            "CONFIRM" to "sim",
            "CANCEL" to "cancelar",
        )

        cases.forEach { (label, text) ->
            var assistantCalls = 0
            val classifier = IntentClassifier {
                IntentPrediction(label, 0.99, "MODEL")
            }
            val engine = InteractionEngine(classifier)
            val controller = LanguageInteractionController(
                classifier,
                engine,
                DomainAssistant { _, _ -> assistantCalls++ },
            )

            val dispatch = controller.handle(text) { _, _ -> }

            assertTrue(
                "$label deve permanecer operacional",
                dispatch is LanguageDispatch.Operational,
            )
            assertNull((dispatch as LanguageDispatch.Operational).result.command)
            assertEquals("$label não pode chamar Qwen", 0, assistantCalls)
        }
    }

    @Test
    fun unknownIntentUsesAssistantWithoutCreatingCommand() {
        val classifier = IntentClassifier {
            IntentPrediction("UNKNOWN", 0.82, "MODEL")
        }
        val engine = InteractionEngine(classifier)
        val assistant = DomainAssistant { _, completion ->
            completion(
                Result.success(
                    AssistantReply(
                        type = AssistantReplyType.CHAT,
                        response = "O Maestro foi desenvolvido pela AgroTurtles.",
                    )
                )
            )
        }
        val controller = LanguageInteractionController(
            classifier,
            engine,
            assistant,
        )
        var reply: AssistantReply? = null

        val dispatch = controller.handle("o que é o Maestro?") { _, result ->
            reply = result.getOrThrow()
        }

        assertTrue(dispatch is LanguageDispatch.AssistantPending)
        assertEquals(AssistantReplyType.CHAT, reply?.type)
        assertEquals(InteractionState.IDLE, engine.state)
        assertEquals(
            "UNKNOWN",
            (dispatch as LanguageDispatch.AssistantPending).prediction.label,
        )
    }

    @Test
    fun missingAssistantPreservesSafeUnknownFallback() {
        val classifier = IntentClassifier {
            IntentPrediction("UNKNOWN", 0.25, "MODEL")
        }
        val engine = InteractionEngine(classifier)
        val controller = LanguageInteractionController(
            classifier,
            engine,
            assistant = null,
        )

        val dispatch = controller.handle("pergunta aberta") { _, _ -> }

        assertTrue(dispatch is LanguageDispatch.Operational)
        val result = (dispatch as LanguageDispatch.Operational).result
        assertEquals(InteractionState.IDLE, result.state)
        assertEquals("Intenção não reconhecida", result.message)
        assertNull(result.command)
    }

    @Test
    fun confirmationStateNeverUsesAssistant() {
        val labels = ArrayDeque(listOf("DOCK", "UNKNOWN"))
        val classifier = IntentClassifier {
            IntentPrediction(labels.removeFirst(), 0.99, "MODEL")
        }
        val engine = InteractionEngine(classifier)
        var assistantCalls = 0
        val controller = LanguageInteractionController(
            classifier,
            engine,
            DomainAssistant { _, _ -> assistantCalls++ },
        )

        controller.handle("voltar para a base") { _, _ -> }
        val dispatch = controller.handle("talvez") { _, _ -> }

        assertTrue(dispatch is LanguageDispatch.Operational)
        val result = (dispatch as LanguageDispatch.Operational).result
        assertEquals(InteractionState.AWAITING_CONFIRMATION, result.state)
        assertEquals("Confirmação ambígua", result.message)
        assertNull(result.command)
        assertEquals(0, assistantCalls)
    }

    @Test
    fun staleAssistantReplyIsIgnoredAfterOperationalIntent() {
        var label = "UNKNOWN"
        val classifier = IntentClassifier {
            IntentPrediction(label, 0.99, "MODEL")
        }
        val engine = InteractionEngine(classifier)
        var pendingCompletion: ((Result<AssistantReply>) -> Unit)? = null
        val controller = LanguageInteractionController(
            classifier,
            engine,
            DomainAssistant { _, completion -> pendingCompletion = completion },
        )
        var deliveredReplies = 0

        controller.handle("o que é o Maestro?") { _, _ -> deliveredReplies++ }
        label = "UNDOCK"
        val operational = controller.handle("sair da doca") { _, _ -> }
        pendingCompletion?.invoke(
            Result.success(
                AssistantReply(AssistantReplyType.CHAT, "Resposta atrasada")
            )
        )

        assertTrue(operational is LanguageDispatch.Operational)
        assertEquals(InteractionState.AWAITING_CONFIRMATION, engine.state)
        assertEquals(0, deliveredReplies)
        assertNotNull(pendingCompletion)
    }

    @Test
    fun cancelledAssistantReplyIsIgnoredDuringLifecycleChange() {
        val classifier = IntentClassifier {
            IntentPrediction("UNKNOWN", 0.99, "MODEL")
        }
        val engine = InteractionEngine(classifier)
        var pendingCompletion: ((Result<AssistantReply>) -> Unit)? = null
        val controller = LanguageInteractionController(
            classifier,
            engine,
            DomainAssistant { _, completion -> pendingCompletion = completion },
        )
        var deliveredReplies = 0

        controller.handle("o que é o Maestro?") { _, _ -> deliveredReplies++ }
        controller.cancelAssistant()
        pendingCompletion?.invoke(
            Result.success(
                AssistantReply(AssistantReplyType.CHAT, "Resposta após rotação")
            )
        )

        assertEquals(0, deliveredReplies)
        assertEquals(InteractionState.IDLE, engine.state)
        assertNotNull(pendingCompletion)
    }
}
