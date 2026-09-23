package br.org.agroturtles.maestro.domain

import java.util.concurrent.atomic.AtomicLong

sealed interface LanguageDispatch {
    data class Operational(
        val result: InteractionResult,
    ) : LanguageDispatch

    data class AssistantPending(
        val prediction: IntentPrediction,
    ) : LanguageDispatch
}

class LanguageInteractionController(
    classifier: IntentClassifier,
    private val interactionEngine: InteractionEngine,
    private val assistant: DomainAssistant?,
) {
    private val router = LanguageRouter(classifier)
    private val assistantRequest = AtomicLong(0)

    fun handle(
        text: String,
        assistantCompletion: (IntentPrediction, Result<AssistantReply>) -> Unit,
    ): LanguageDispatch {
        return handlePrediction(text, router.route(text).prediction, assistantCompletion)
    }

    /** Applies a prediction already obtained off the main thread, for example by Jev. */
    fun handlePrediction(
        text: String,
        prediction: IntentPrediction,
        assistantCompletion: (IntentPrediction, Result<AssistantReply>) -> Unit,
    ): LanguageDispatch {
        if (interactionEngine.state !in ASSISTANT_ELIGIBLE_STATES) {
            cancelAssistant()
            return LanguageDispatch.Operational(
                interactionEngine.handlePrediction(text, prediction)
            )
        }

        if (
            prediction.label != "UNKNOWN" ||
            assistant == null ||
            text.isBlank()
        ) {
            cancelAssistant()
            return LanguageDispatch.Operational(
                interactionEngine.handlePrediction(text, prediction)
            )
        }

        val requestId = assistantRequest.incrementAndGet()
        assistant.respond(text) { result ->
            if (assistantRequest.get() == requestId) {
                assistantCompletion(prediction, result)
            }
        }

        return LanguageDispatch.AssistantPending(prediction)
    }

    fun cancelAssistant() {
        assistantRequest.incrementAndGet()
    }

    private companion object {
        val ASSISTANT_ELIGIBLE_STATES = setOf(
            InteractionState.IDLE,
            InteractionState.TARGET_READY,
        )
    }
}
