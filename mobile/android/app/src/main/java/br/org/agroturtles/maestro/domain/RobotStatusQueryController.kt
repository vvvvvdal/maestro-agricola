package br.org.agroturtles.maestro.domain

import java.text.Normalizer
import java.time.Instant
import java.util.Locale
import java.util.UUID

data class OperationStatusUpdate(
    val result: InteractionResult,
    val terminal: Boolean,
)

class RobotStatusQueryController(
    private val transportFactory: () -> ReadOnlyQueryTransport,
    private val requestId: () -> String = { UUID.randomUUID().toString() },
    private val requestedAt: () -> String = { Instant.now().toString() },
) {
    fun handle(
        text: String,
        completion: (InteractionResult) -> Unit,
    ): InteractionResult? {
        if (!looksLikeRobotStatusQuestion(text)) return null
        val prediction = IntentPrediction("STATUS_QUERY", 1.0, "RULE")
        send(command = null) { response -> completion(manualResult(response, prediction)) }
        return InteractionResult(
            state = InteractionState.QUERYING,
            message = "Consultando o estado do robô",
            speech = "Consultando o estado do robô.",
            prediction = prediction,
            intent = prediction.label,
        )
    }

    fun track(command: Command, completion: (OperationStatusUpdate) -> Unit) {
        send(command) { response -> completion(trackingResult(command, response)) }
    }

    fun trackingStarted(command: Command): InteractionResult = InteractionResult(
        state = InteractionState.EXECUTING,
        message = "Comando aceito. Acompanhando ${actionDescription(command)} no simulador.",
        intent = command.intent,
        targetId = command.targetId,
    )

    fun trackingTimedOut(command: Command): OperationStatusUpdate = terminalResult(
        command,
        "O acompanhamento da operação expirou. Verifique o robô no simulador antes de reiniciar.",
    )

    private fun send(command: Command?, completion: (ReadOnlyQueryResponse) -> Unit) {
        val query = ReadOnlyQuery(
            requestId = requestId(),
            requestedAt = requestedAt(),
            kind = ROBOT_STATUS,
            commandId = command?.commandId,
        )
        transportFactory().send(query, completion)
    }

    private fun manualResult(
        response: ReadOnlyQueryResponse,
        prediction: IntentPrediction,
    ): InteractionResult {
        val message = when {
            response.kind != ROBOT_STATUS || response.status == ReadOnlyQueryStatus.UNAVAILABLE ->
                "A consulta de estado está indisponível. Nenhum comando foi enviado."

            response.status == ReadOnlyQueryStatus.NOT_FOUND ->
                "O robô está aguardando um comando nesta sessão."

            response.status == ReadOnlyQueryStatus.FOUND && response.operation != null ->
                manualMessage(response.operation)

            else -> "Não foi possível consultar o estado do robô. Nenhum comando foi enviado."
        }
        return InteractionResult(
            state = InteractionState.QUERY_COMPLETED,
            message = message,
            speech = message,
            prediction = prediction,
            intent = prediction.label,
        )
    }

    private fun trackingResult(command: Command, response: ReadOnlyQueryResponse): OperationStatusUpdate {
        val operation = response.operation
        if (
            response.kind != ROBOT_STATUS ||
            response.status != ReadOnlyQueryStatus.FOUND ||
            operation?.commandId != command.commandId ||
            operation.intent != command.intent
        ) {
            return terminalResult(
                command,
                "Não foi possível acompanhar a operação. Não envie outro comando sem verificar o robô.",
            )
        }

        return when (operation.state) {
            RobotOperationState.QUEUED -> OperationStatusUpdate(
                result = trackingResult(
                    command,
                    "Operação aceita. Aguardando início seguro.",
                    speech = null,
                ),
                terminal = false,
            )

            RobotOperationState.EXECUTING -> OperationStatusUpdate(
                result = trackingResult(
                    command,
                    "Executando ${actionDescription(command)} no simulador.",
                    speech = null,
                ),
                terminal = false,
            )

            RobotOperationState.COMPLETED -> OperationStatusUpdate(
                result = InteractionResult(
                    state = InteractionState.COMPLETED,
                    message = "${actionDescription(command).replaceFirstChar(Char::uppercase)} concluída no Gazebo.",
                    speech = "${actionDescription(command).replaceFirstChar(Char::uppercase)} concluída no Gazebo.",
                    intent = command.intent,
                    targetId = command.targetId,
                ),
                terminal = true,
            )

            RobotOperationState.FAILED -> terminalResult(
                command,
                "${actionDescription(command).replaceFirstChar(Char::uppercase)} falhou no simulador. Nenhum novo comando foi enviado.",
            )
        }
    }

    private fun terminalResult(command: Command, message: String) = OperationStatusUpdate(
        result = InteractionResult(
            state = InteractionState.OPERATION_FAILED,
            message = message,
            speech = message,
            intent = command.intent,
            targetId = command.targetId,
        ),
        terminal = true,
    )

    private fun trackingResult(command: Command, message: String, speech: String?) = InteractionResult(
        state = InteractionState.EXECUTING,
        message = message,
        speech = speech,
        intent = command.intent,
        targetId = command.targetId,
    )

    private fun manualMessage(operation: ReadOnlyRobotOperation): String = when (operation.state) {
        RobotOperationState.QUEUED -> "O robô aguarda o início seguro de ${actionDescription(operation)}."
        RobotOperationState.EXECUTING -> "O robô está executando ${actionDescription(operation)}."
        RobotOperationState.COMPLETED -> "A última operação, ${actionDescription(operation)}, foi concluída no Gazebo."
        RobotOperationState.FAILED -> "A última operação, ${actionDescription(operation)}, falhou no simulador."
    }

    private fun actionDescription(command: Command): String = actionDescription(
        ReadOnlyRobotOperation(command.commandId, command.intent, command.targetId, RobotOperationState.QUEUED)
    )

    private fun actionDescription(operation: ReadOnlyRobotOperation): String = when (operation.intent) {
        "SPRAY" -> "a pulverização${operation.targetId?.let { " no ${plotLabel(it)}" }.orEmpty()}"
        "DOCK" -> "o retorno à doca"
        "UNDOCK" -> "a saída da doca"
        else -> "a operação solicitada"
    }

    private fun looksLikeRobotStatusQuestion(text: String): Boolean {
        val normalized = Normalizer.normalize(text.lowercase(Locale.ROOT), Normalizer.Form.NFKD)
            .replace(Regex("\\p{M}+"), "")
        val asksForStatus = listOf("status", "como esta", "situacao", "estado").any(normalized::contains)
        return asksForStatus && (normalized.contains("robo") || normalized.contains("operacao"))
    }
}
