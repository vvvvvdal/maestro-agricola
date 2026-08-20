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
    private var pendingIntent: String? = null

    var state: InteractionState = InteractionState.IDLE
        private set


    fun observeTarget(id: String): InteractionResult {
        visualTargetId = id
        targetId = null

        state = InteractionState.TARGET_READY

        return InteractionResult(
            state,
            "Alvo $id identificado",
            "Alvo $id identificado"
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

        return InteractionResult(
            state,
            reason,
            if (accepted) {
                "Comando enviado"
            } else {
                "Comando recusado"
            }
        )
    }


    fun confirmationTimedOut(): InteractionResult {

        if (state != InteractionState.AWAITING_CONFIRMATION) {
            return InteractionResult(
                state,
                "Nenhuma confirmação pendente"
            )
        }

        clearTargetContext()
        state = InteractionState.CANCELLED

        return InteractionResult(
            state,
            "Confirmação expirada",
            "Tempo esgotado. Operação cancelada"
        )
    }


    fun reset(): InteractionResult {

        clearTargetContext()
        state = InteractionState.IDLE

        return InteractionResult(
            state,
            "Pronto para iniciar"
        )
    }


    private fun handleIntent(
        text: String,
        prediction: IntentPrediction
    ): InteractionResult {

        val intent = prediction.label

        if (intent !in setOf("SPRAY", "DOCK", "UNDOCK")) {
            return ambiguous(
                "Intenção não reconhecida",
                prediction
            )
        }

        pendingIntent = intent


        if (!requiresTarget(intent)) {

            state = InteractionState.AWAITING_CONFIRMATION

            return InteractionResult(
                state,
                "$intent?",
                "${intent.lowercase().replaceFirstChar { it.uppercase() }}, confirmar?",
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
                    "Olhe para a placa ou diga o ID do plot"

                TargetResolutionStatus.RESOLVED ->
                    error("estado impossível")
            }

            return InteractionResult(
                state,
                message,
                "$message. Operação cancelada",
                prediction = prediction
            )
        }


        targetId = resolution.targetId

        state = InteractionState.AWAITING_CONFIRMATION


        return InteractionResult(
            state,
            "Pulverizar $targetId?",
            "Pulverizar ${targetId?.replace("plot-", "talhão ")}, confirmar?",
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


                InteractionResult(
                    state,
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


                InteractionResult(
                    state,
                    "Operação cancelada",
                    "Operação cancelada",
                    prediction = prediction
                )
            }


            else -> ambiguous(
                "Confirmação ambígua",
                prediction
            )
        }
    }


    private fun ambiguous(
        message: String,
        prediction: IntentPrediction
    ): InteractionResult {

        return InteractionResult(
            state,
            message,
            "Não entendi. Tente novamente",
            prediction = prediction
        )
    }


    private fun clearTargetContext() {
        visualTargetId = null
        targetId = null
        pendingIntent = null
    }


    private fun requiresTarget(
        intent: String
    ): Boolean {
        return intent == "SPRAY"
    }
}