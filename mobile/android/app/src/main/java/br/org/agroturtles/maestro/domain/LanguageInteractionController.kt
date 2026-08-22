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
        if (interactionEngine.state !in ASSISTANT_ELIGIBLE_STATES) {
            cancelAssistant()
            return LanguageDispatch.Operational(
                interactionEngine.handleTranscript(text)
            )
        }

        val route = router.route(text)
        val assistantText = route.assistantText

        if (
            route.type == LanguageRouteType.OPERATIONAL ||
            assistant == null ||
            assistantText == null
        ) {
            cancelAssistant()
            return LanguageDispatch.Operational(
                interactionEngine.handlePrediction(text, route.prediction)
            )
        }

        val requestId = assistantRequest.incrementAndGet()
        assistant.respond(assistantText) { result ->
            if (assistantRequest.get() == requestId) {
                assistantCompletion(route.prediction, result)
            }
        }

        return LanguageDispatch.AssistantPending(route.prediction)
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
