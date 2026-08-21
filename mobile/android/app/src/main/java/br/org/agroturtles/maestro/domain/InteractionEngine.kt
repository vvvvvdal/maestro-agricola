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
    val intent: String,
    val targetId: String? = null,
)

data class InteractionResult(
    val state: InteractionState,
    val message: String,
    val speech: String? = null,
    val command: Command? = null,
    val prediction: IntentPrediction? = null,
    val intent: String? = null,
    val targetId: String? = null,
    val targetSource: String? = null,
)

class InteractionEngine(
    private val classifier: IntentClassifier,
    private val targetResolver: TargetResolver,
) {

    constructor(classifier: IntentClassifier) : this(
        classifier,
        TargetResolver(setOf("plot-01", "plot-02", "plot-03")),
    )

    private var visualTargetId: String? = null
    private var targetId: String? = null
    private var targetSource: String? = null
    private var pendingIntent: String? = null

    var state: InteractionState = InteractionState.IDLE
        private set


    fun observeTarget(id: String): InteractionResult {
        visualTargetId = id
        targetId = null
        targetSource = VISUAL_SOURCE

        state = InteractionState.TARGET_READY

        return result(
            "Alvo $id identificado",
            "Alvo ${plotLabel(id)}. Diga a ação desejada."
        )
    }


    fun handleTranscript(text: String): InteractionResult {
        val prediction = classifier.classify(text)

        return when (state) {
            InteractionState.IDLE,
            InteractionState.TARGET_READY -> handleIntent(text, prediction)

            InteractionState.AWAITING_CONFIRMATION -> handleConfirmation(prediction)

            else -> ambiguous(
                "Inicie uma nova interação",
                "Reinicie para começar outra jornada.",
                prediction
            )
        }
    }


    fun transportCompleted(
        accepted: Boolean,
        reason: String
    ): InteractionResult {

        state = if (accepted) {
            InteractionState.ACCEPTED
        } else {
            InteractionState.ERROR
        }

        return result(
            reason,
            if (accepted) {
                acceptedSpeech()
            } else {
                "Comando recusado pelo robô. Nada foi executado."
            }
        )
    }


    fun confirmationTimedOut(): InteractionResult {

        if (state != InteractionState.AWAITING_CONFIRMATION) {
            return result("Nenhuma confirmação pendente")
        }

        clearTargetContext()
        state = InteractionState.CANCELLED

        return result(
            "Confirmação expirada",
            "Tempo esgotado. Operação cancelada e nada foi enviado."
        )
    }


    fun reset(): InteractionResult {

        clearTargetContext()
        state = InteractionState.IDLE

        return result("Pronto para iniciar")
    }


    private fun handleIntent(
        text: String,
        prediction: IntentPrediction
    ): InteractionResult {

        val intent = prediction.label

        if (intent !in SUPPORTED_INTENTS) {
            return ambiguous(
                "Intenção não reconhecida",
                "Não entendi. Diga pulverizar, sair da doca ou retornar à doca.",
                prediction
            )
        }

        pendingIntent = intent


        if (!requiresTarget(intent)) {

            state = InteractionState.AWAITING_CONFIRMATION

            return result(
                "${actionLabel(intent)}?",
                "${actionLabel(intent)}. Confirmar?",
                prediction = prediction
            )
        }


        val resolution = targetResolver.resolve(
            visualTargetId,
            text
        )


        if (resolution.status != TargetResolutionStatus.RESOLVED) {

            clearTargetContext()

            state = InteractionState.AMBIGUOUS

            val message = when (resolution.status) {

                TargetResolutionStatus.CONFLICT ->
                    "Alvo falado e visual não conferem"

                TargetResolutionStatus.UNKNOWN ->
                    "Alvo não cadastrado"

                TargetResolutionStatus.NEEDS_VISUAL ->
                    "Olhe para a placa ou diga o ID do talhão"

                TargetResolutionStatus.RESOLVED ->
                    error("estado impossível")
            }

            return result(
                message,
                "$message. Operação cancelada.",
                prediction = prediction
            )
        }


        targetId = resolution.targetId
        targetSource = resolution.source

        state = InteractionState.AWAITING_CONFIRMATION


        return result(
            "Pulverizar $targetId?",
            "Pulverizar ${plotLabel(targetId)}. Confirmar?",
            prediction = prediction
        )
    }


    private fun handleConfirmation(
        prediction: IntentPrediction
    ): InteractionResult {

        return when (prediction.label) {


            "CONFIRM" -> {

                val intent = requireNotNull(pendingIntent)

                state = InteractionState.SENDING


                result(
                    "Enviando comando",

                    command = Command(
                        commandId = UUID.randomUUID().toString(),
                        createdAt = Instant.now().toString(),
                        intent = intent,
                        targetId = if (requiresTarget(intent)) {
                            targetId
                        } else {
                            null
                        }
                    ),

                    prediction = prediction
                )
            }


            "CANCEL" -> {

                clearTargetContext()

                state = InteractionState.CANCELLED


                result(
                    "Operação cancelada",
                    "Operação cancelada. Nada foi enviado ao robô.",
                    prediction = prediction
                )
            }


            else -> ambiguous(
                "Confirmação ambígua",
                "Não entendi. Diga sim para confirmar ou cancelar para abortar.",
                prediction
            )
        }
    }


    private fun ambiguous(
        message: String,
        speech: String,
        prediction: IntentPrediction
    ): InteractionResult {

        return result(
            message,
            speech,
            prediction = prediction
        )
    }


    private fun acceptedSpeech(): String = when (pendingIntent) {
        "SPRAY" -> "Comando aceito. Indo pulverizar o ${plotLabel(targetId)}."
        "DOCK" -> "Comando aceito. Retornando à doca."
        "UNDOCK" -> "Comando aceito. Saindo da doca."
        else -> "Comando aceito pelo robô."
    }


    /**
     * Cada resultado carrega o retrato completo da jornada, para a interface
     * destacar alvo, intenção e confirmação pendente sem consultar o motor.
     */
    private fun result(
        message: String,
        speech: String? = null,
        command: Command? = null,
        prediction: IntentPrediction? = null,
    ): InteractionResult {

        return InteractionResult(
            state = state,
            message = message,
            speech = speech,
            command = command,
            prediction = prediction,
            intent = pendingIntent,
            targetId = targetId ?: visualTargetId,
            targetSource = targetSource,
        )
    }


    private fun clearTargetContext() {
        visualTargetId = null
        targetId = null
        targetSource = null
        pendingIntent = null
    }


    private fun requiresTarget(
        intent: String
    ): Boolean {
        return intent == "SPRAY"
    }


    companion object {
        const val CONFIRMATION_TIMEOUT_SECONDS = 10

        private const val VISUAL_SOURCE = "VISUAL"
        private val SUPPORTED_INTENTS = setOf("SPRAY", "DOCK", "UNDOCK")
    }
}
