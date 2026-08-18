package br.org.agroturtles.maestro.domain

import java.time.Instant
import java.util.UUID


enum class InteractionState {
    IDLE,
    TARGET_READY,
    AWAITING_CONFIRMATION,
    SENDING,
    ACCEPTED,
    CANCELLED,
    AMBIGUOUS,
    ERROR,
}

data class Command(
    val commandId: String,
    val createdAt: String,
    val targetId: String,
)

data class InteractionResult(
    val state: InteractionState,
    val message: String,
    val speech: String? = null,
    val command: Command? = null,
    val prediction: IntentPrediction? = null,
)

class InteractionEngine(
    private val classifier: IntentClassifier,
    private val targetResolver: TargetResolver,
) {
    constructor(classifier: IntentClassifier) : this(classifier, TargetResolver(setOf("plot-03")))

    private var visualTargetId: String? = null
    private var targetId: String? = null
    var state: InteractionState = InteractionState.IDLE
        private set

    fun observeTarget(id: String): InteractionResult {
        visualTargetId = id
        targetId = null
        state = InteractionState.TARGET_READY
        return InteractionResult(state, "Alvo $id identificado", "Alvo $id identificado")
    }

    fun handleTranscript(text: String): InteractionResult {
        val prediction = classifier.classify(text)
        return when (state) {
            InteractionState.IDLE, InteractionState.TARGET_READY -> handleIntent(text, prediction)
            InteractionState.AWAITING_CONFIRMATION -> handleConfirmation(prediction)
            else -> ambiguous("Inicie uma nova interação", prediction)
        }
    }

    fun transportCompleted(accepted: Boolean, reason: String): InteractionResult {
        state = if (accepted) InteractionState.ACCEPTED else InteractionState.ERROR
        val speech = if (accepted) "Comando enviado" else "Comando recusado"
        return InteractionResult(state, reason, speech)
    }

    fun confirmationTimedOut(): InteractionResult {
        if (state != InteractionState.AWAITING_CONFIRMATION) {
            return InteractionResult(state, "Nenhuma confirmação pendente")
        }
        targetId = null
        visualTargetId = null
        state = InteractionState.CANCELLED
        return InteractionResult(state, "Confirmação expirada", "Tempo esgotado. Operação cancelada")
    }

    fun reset(): InteractionResult {
        targetId = null
        visualTargetId = null
        state = InteractionState.IDLE
        return InteractionResult(state, "Pronto para iniciar")
    }

    private fun handleIntent(text: String, prediction: IntentPrediction): InteractionResult {
        if (prediction.label != "SPRAY") return ambiguous("Intenção não reconhecida", prediction)
        val resolution = targetResolver.resolve(visualTargetId, text)
        if (resolution.status != TargetResolutionStatus.RESOLVED) {
            targetId = null
            state = InteractionState.AMBIGUOUS
            val message = when (resolution.status) {
                TargetResolutionStatus.CONFLICT -> "Alvo falado e visual não conferem"
                TargetResolutionStatus.UNKNOWN -> "Alvo não cadastrado"
                TargetResolutionStatus.NEEDS_VISUAL -> "Olhe para a placa ou diga o ID do plot"
                TargetResolutionStatus.RESOLVED -> error("estado impossível")
            }
            return InteractionResult(state, message, "$message. Operação cancelada", prediction = prediction)
        }
        val target = requireNotNull(resolution.targetId)
        targetId = target
        state = InteractionState.AWAITING_CONFIRMATION
        return InteractionResult(
            state,
            "Pulverizar $target?",
            "Pulverizar ${target.replace("plot-", "talhão ")}, confirmar?",
            prediction = prediction,
        )
    }

    private fun handleConfirmation(prediction: IntentPrediction): InteractionResult = when (prediction.label) {
        "CONFIRM" -> {
            val target = requireNotNull(targetId)
            state = InteractionState.SENDING
            InteractionResult(
                state,
                "Enviando comando",
                command = Command(UUID.randomUUID().toString(), Instant.now().toString(), target),
                prediction = prediction,
            )
        }
        "CANCEL" -> {
            state = InteractionState.CANCELLED
            InteractionResult(state, "Operação cancelada", "Operação cancelada", prediction = prediction)
        }
        else -> ambiguous("Confirmação ambígua", prediction)
    }

    private fun ambiguous(message: String, prediction: IntentPrediction): InteractionResult {
        return InteractionResult(state, message, "Não entendi. Tente novamente", prediction = prediction)
    }
}
