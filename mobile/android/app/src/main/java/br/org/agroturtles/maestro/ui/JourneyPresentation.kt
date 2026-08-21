package br.org.agroturtles.maestro.ui

import br.org.agroturtles.maestro.domain.InteractionState
import br.org.agroturtles.maestro.domain.actionLabel
import br.org.agroturtles.maestro.domain.plotLabel
import kotlin.math.roundToInt

/**
 * Mapeamento puro entre o estado da jornada e o que a tela mostra.
 *
 * Fica fora do Compose para ser coberto por teste unitário e para manter o
 * layout sem regra de apresentação espalhada.
 */

enum class Tone { NEUTRAL, INFO, ATTENTION, SUCCESS, DANGER }

data class StatusHeadline(
    val label: String,
    val title: String,
    val tone: Tone,
)

fun statusHeadline(state: InteractionState): StatusHeadline = when (state) {
    InteractionState.IDLE ->
        StatusHeadline("PASSO 1", "Olhe para o alvo ou fale o talhão", Tone.NEUTRAL)

    InteractionState.TARGET_READY ->
        StatusHeadline("PASSO 2", "Alvo identificado. Diga a ação", Tone.INFO)

    InteractionState.AWAITING_CONFIRMATION ->
        StatusHeadline("CONFIRMAÇÃO PENDENTE", "Confirme por voz para executar", Tone.ATTENTION)

    InteractionState.SENDING ->
        StatusHeadline("ENVIANDO", "Comando confirmado, indo ao robô", Tone.INFO)

    InteractionState.ACCEPTED ->
        StatusHeadline("COMANDO ENVIADO", "Aceito pelo robô", Tone.SUCCESS)

    InteractionState.CANCELLED ->
        StatusHeadline("CANCELADO", "Nada foi enviado ao robô", Tone.NEUTRAL)

    InteractionState.AMBIGUOUS ->
        StatusHeadline("AMBÍGUO", "Alvo não resolvido com segurança", Tone.ATTENTION)

    InteractionState.ERROR ->
        StatusHeadline("RECUSADO", "O robô não aceitou o comando", Tone.DANGER)
}

enum class StepStatus { PENDING, ACTIVE, DONE, SKIPPED, BLOCKED }

data class JourneyStep(
    val label: String,
    val status: StepStatus,
)

private val STEP_LABELS = listOf("Alvo", "Intenção", "Confirmar", "Executar")

private val TARGETLESS_INTENTS = setOf("DOCK", "UNDOCK")

fun journeySteps(state: InteractionState, intent: String?): List<JourneyStep> {
    val target = if (intent in TARGETLESS_INTENTS) StepStatus.SKIPPED else StepStatus.DONE

    val statuses = when (state) {
        InteractionState.IDLE -> listOf(
            StepStatus.ACTIVE, StepStatus.PENDING, StepStatus.PENDING, StepStatus.PENDING,
        )

        InteractionState.TARGET_READY -> listOf(
            StepStatus.DONE, StepStatus.ACTIVE, StepStatus.PENDING, StepStatus.PENDING,
        )

        InteractionState.AWAITING_CONFIRMATION -> listOf(
            target, StepStatus.DONE, StepStatus.ACTIVE, StepStatus.PENDING,
        )

        InteractionState.SENDING -> listOf(
            target, StepStatus.DONE, StepStatus.DONE, StepStatus.ACTIVE,
        )

        InteractionState.ACCEPTED -> listOf(
            target, StepStatus.DONE, StepStatus.DONE, StepStatus.DONE,
        )

        InteractionState.CANCELLED -> listOf(
            StepStatus.PENDING, StepStatus.PENDING, StepStatus.BLOCKED, StepStatus.PENDING,
        )

        InteractionState.AMBIGUOUS -> listOf(
            StepStatus.BLOCKED, StepStatus.DONE, StepStatus.PENDING, StepStatus.PENDING,
        )

        InteractionState.ERROR -> listOf(
            target, StepStatus.DONE, StepStatus.DONE, StepStatus.BLOCKED,
        )
    }

    return STEP_LABELS.mapIndexed { index, label -> JourneyStep(label, statuses[index]) }
}

fun targetValue(intent: String?, targetId: String?): String = when {
    intent in TARGETLESS_INTENTS -> "não requer alvo"
    targetId.isNullOrBlank() -> "—"
    else -> targetId
}

fun targetDetail(intent: String?, targetId: String?, targetSource: String?): String = when {
    intent in TARGETLESS_INTENTS -> "comando de doca"
    targetId.isNullOrBlank() -> "olhe para a placa ou diga o ID"
    else -> "${plotLabel(targetId)} · ${targetSourceLabel(targetSource)}"
}

fun targetSourceLabel(source: String?): String = when (source) {
    "VISUAL" -> "câmera"
    "VOICE" -> "voz"
    "AGREED" -> "câmera e voz"
    else -> "origem indefinida"
}

fun intentValue(intent: String?): String =
    if (intent == null) "—" else actionLabel(intent)

fun predictionDetail(label: String?, confidence: Double?, source: String?): String {
    if (label == null || confidence == null) return "aguardando fala"
    return "$label · ${(confidence * 100).roundToInt()}% · ${predictionSourceLabel(source)}"
}

fun predictionSourceLabel(source: String?): String = when (source) {
    "RULE" -> "regra determinística"
    "MODEL" -> "modelo local"
    else -> "classificador local"
}

data class RobotPresentation(
    val title: String,
    val detail: String,
    val tone: Tone,
)

val UnknownRobotPresentation = RobotPresentation(
    "Aguardando comando",
    "nenhum comando aceito nesta sessão",
    Tone.NEUTRAL,
)

/**
 * O bridge responde `ACCEPTED` quando aceita e enfileira o comando, não quando
 * o robô conclui a manobra. O rótulo descreve o comando aceito, não uma
 * telemetria confirmada.
 */
fun robotPresentation(intent: String?, targetId: String?): RobotPresentation = when (intent) {
    "UNDOCK" -> RobotPresentation(
        "Saindo da doca",
        "undock explícito aceito pelo bridge",
        Tone.INFO,
    )

    "SPRAY" -> RobotPresentation(
        "Navegando",
        "destino ${plotLabel(targetId)} · permanece no destino",
        Tone.INFO,
    )

    "DOCK" -> RobotPresentation(
        "Retornando à doca",
        "aproximação e docking aceitos pelo bridge",
        Tone.INFO,
    )

    else -> UnknownRobotPresentation
}
