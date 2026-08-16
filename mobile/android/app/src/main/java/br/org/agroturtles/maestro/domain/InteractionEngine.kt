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

class InteractionEngine(private val classifier: IntentClassifier) {
    private var targetId: String? = null
    var state: InteractionState = InteractionState.IDLE
        private set

    fun observeTarget(id: String): InteractionResult {
        targetId = id
        state = InteractionState.TARGET_READY
        return InteractionResult(state, "Alvo $id identificado", "Alvo identificado")
    }

    fun handleTranscript(text: String): InteractionResult {
        val prediction = classifier.classify(text)
        return when (state) {
            InteractionState.TARGET_READY -> handleIntent(prediction)
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
        state = InteractionState.CANCELLED
        return InteractionResult(state, "Confirmação expirada", "Tempo esgotado. Operação cancelada")
    }

    fun reset(): InteractionResult {
        targetId = null
        state = InteractionState.IDLE
        return InteractionResult(state, "Pronto para iniciar")
    }

    private fun handleIntent(prediction: IntentPrediction): InteractionResult {
        if (prediction.label != "SPRAY") return ambiguous("Intenção não reconhecida", prediction)
        val target = targetId ?: return ambiguous("Alvo ausente", prediction)
        state = InteractionState.AWAITING_CONFIRMATION
        return InteractionResult(
            state,
            "Pulverizar $target?",
            "Pulverizar talhão três, confirmar?",
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
