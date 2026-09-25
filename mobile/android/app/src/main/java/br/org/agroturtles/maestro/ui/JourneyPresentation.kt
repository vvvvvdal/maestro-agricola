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

fun statusHeadline(state: InteractionState, intent: String? = null): StatusHeadline = when (state) {
    InteractionState.IDLE ->
        StatusHeadline("PASSO 1", "Olhe para o alvo ou fale o talhão", Tone.NEUTRAL)

    InteractionState.INSPECTING ->
        StatusHeadline("INSPECIONANDO", "Lendo o marcador", Tone.INFO)

    InteractionState.TARGET_READY ->
        StatusHeadline("PASSO 2", "Alvo identificado. Diga a ação", Tone.INFO)

    InteractionState.AWAITING_CONFIRMATION ->
        StatusHeadline("CONFIRMAÇÃO PENDENTE", "Confirme por voz para executar", Tone.ATTENTION)

    InteractionState.SENDING ->
        StatusHeadline("ENVIANDO", "Comando confirmado, indo ao robô", Tone.INFO)

    InteractionState.ACCEPTED ->
        StatusHeadline("COMANDO ENVIADO", "Aceito pelo robô", Tone.SUCCESS)

    InteractionState.EXECUTING ->
        StatusHeadline("EM EXECUÇÃO", "Acompanhando o robô", Tone.INFO)

    InteractionState.COMPLETED ->
        StatusHeadline("OPERAÇÃO CONCLUÍDA", "Concluída no simulador", Tone.SUCCESS)

    InteractionState.OPERATION_FAILED ->
        StatusHeadline("OPERAÇÃO INTERROMPIDA", "Verifique o robô antes de continuar", Tone.DANGER)

    InteractionState.QUERYING ->
        StatusHeadline(
            "CONSULTANDO",
            if (intent == "STATUS_QUERY") "Buscando estado do robô" else "Buscando histórico do talhão",
            Tone.INFO,
        )

    InteractionState.QUERY_COMPLETED ->
        StatusHeadline("CONSULTA CONCLUÍDA", "Nenhum comando enviado", Tone.SUCCESS)

    InteractionState.MISSION_PREVIEW ->
        StatusHeadline("PLANO PARA REVISÃO", "Nenhuma ação foi enviada", Tone.ATTENTION)

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
private val QUERY_STEP_LABELS = listOf("Talhão", "Consulta", "Buscar", "Resposta")
private val ROBOT_QUERY_STEP_LABELS = listOf("Robô", "Consulta", "Buscar", "Resposta")
private const val PLOT_STATUS_QUERY = "PLOT_STATUS_QUERY"
private const val STATUS_QUERY = "STATUS_QUERY"
private const val INSPECT_TARGET = "INSPECT_TARGET"
private const val MISSION_PREVIEW = "MISSION_PREVIEW"

private val TARGETLESS_INTENTS = setOf("DOCK", "UNDOCK")

fun journeySteps(state: InteractionState, intent: String?): List<JourneyStep> {
    if (intent == MISSION_PREVIEW) {
        val statuses = when (state) {
            InteractionState.MISSION_PREVIEW -> listOf(
                StepStatus.DONE, StepStatus.ACTIVE, StepStatus.PENDING, StepStatus.PENDING,
            )

            InteractionState.CANCELLED -> listOf(
                StepStatus.DONE, StepStatus.BLOCKED, StepStatus.PENDING, StepStatus.PENDING,
            )

            else -> listOf(
                StepStatus.PENDING, StepStatus.PENDING, StepStatus.PENDING, StepStatus.PENDING,
            )
        }
        return listOf("Plano", "Revisar", "Por etapa", "Executar").mapIndexed { index, label ->
            JourneyStep(label, statuses[index])
        }
    }
    if (intent == INSPECT_TARGET) {
        val statuses = when (state) {
            InteractionState.INSPECTING -> listOf(StepStatus.ACTIVE, StepStatus.PENDING, StepStatus.PENDING, StepStatus.PENDING)
            InteractionState.TARGET_READY -> listOf(StepStatus.DONE, StepStatus.DONE, StepStatus.DONE, StepStatus.DONE)
            InteractionState.ERROR -> listOf(StepStatus.BLOCKED, StepStatus.PENDING, StepStatus.PENDING, StepStatus.PENDING)
            else -> listOf(StepStatus.PENDING, StepStatus.PENDING, StepStatus.PENDING, StepStatus.PENDING)
        }
        return listOf("Captura", "Leitura", "Talhão", "Pronto").mapIndexed { index, label ->
            JourneyStep(label, statuses[index])
        }
    }
    if (intent == PLOT_STATUS_QUERY || intent == STATUS_QUERY) {
        val statuses = when (state) {
            InteractionState.QUERYING -> listOf(
                StepStatus.DONE, StepStatus.DONE, StepStatus.ACTIVE, StepStatus.PENDING,
            )

            InteractionState.QUERY_COMPLETED -> listOf(
                StepStatus.DONE, StepStatus.DONE, StepStatus.DONE, StepStatus.DONE,
            )

            else -> listOf(
                StepStatus.PENDING, StepStatus.PENDING, StepStatus.PENDING, StepStatus.PENDING,
            )
        }
        val labels = if (intent == STATUS_QUERY) ROBOT_QUERY_STEP_LABELS else QUERY_STEP_LABELS
        return labels.mapIndexed { index, label ->
            JourneyStep(label, statuses[index])
        }
    }

    val target = if (intent in TARGETLESS_INTENTS) StepStatus.SKIPPED else StepStatus.DONE

    val statuses = when (state) {
        InteractionState.IDLE -> listOf(
            StepStatus.ACTIVE, StepStatus.PENDING, StepStatus.PENDING, StepStatus.PENDING,
        )

        InteractionState.INSPECTING -> listOf(
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

        InteractionState.EXECUTING -> listOf(
            target, StepStatus.DONE, StepStatus.DONE, StepStatus.ACTIVE,
        )

        InteractionState.COMPLETED -> listOf(
            target, StepStatus.DONE, StepStatus.DONE, StepStatus.DONE,
        )

        InteractionState.OPERATION_FAILED -> listOf(
            target, StepStatus.DONE, StepStatus.DONE, StepStatus.BLOCKED,
        )

        InteractionState.QUERYING,
        InteractionState.QUERY_COMPLETED,
        InteractionState.MISSION_PREVIEW -> listOf(
            StepStatus.PENDING, StepStatus.PENDING, StepStatus.PENDING, StepStatus.PENDING,
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
    intent == MISSION_PREVIEW -> "ver etapas"
    intent in TARGETLESS_INTENTS -> "não requer alvo"
    targetId.isNullOrBlank() -> "—"
    else -> targetId
}

fun targetDetail(intent: String?, targetId: String?, targetSource: String?): String = when {
    intent == MISSION_PREVIEW -> "alvos definidos no plano"
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

fun intentValue(intent: String?): String = when (intent) {
    null -> "—"
    STATUS_QUERY -> "Consultar estado do robô"
    PLOT_STATUS_QUERY -> "Consultar histórico do talhão"
    INSPECT_TARGET -> "Inspecionar marcador"
    MISSION_PREVIEW -> "Revisar missão"
    else -> actionLabel(intent)
}

data class IntentPresentation(
    val value: String,
    val detail: String,
    val tone: Tone,
)

/**
 * Keeps a valid UNKNOWN choice distinct from Jev's closed failure fallback.
 * Jev reserves UNKNOWN with zero probability for unavailable evaluations.
 */
fun intentPresentation(
    intent: String?,
    label: String?,
    confidence: Double?,
    source: String?,
): IntentPresentation = when {
    intent == MISSION_PREVIEW -> IntentPresentation(
        value = "Revisar missão",
        detail = "plano local · nenhum comando enviado",
        tone = Tone.ATTENTION,
    )

    intent != null && label == null -> IntentPresentation(
        value = intentValue(intent),
        detail = "comando confirmado",
        tone = Tone.INFO,
    )

    isJevUnavailable(label, confidence, source) -> IntentPresentation(
        value = "Classificação indisponível",
        detail = "sem decisão remota · nenhum comando enviado",
        tone = Tone.ATTENTION,
    )

    label == "UNKNOWN" -> IntentPresentation(
        value = "Não reconhecida",
        detail = predictionDetail(label, confidence, source) + " · nenhum comando enviado",
        tone = Tone.ATTENTION,
    )

    else -> IntentPresentation(
        value = intentValue(intent),
        detail = predictionDetail(label, confidence, source),
        tone = if (intent == null) Tone.NEUTRAL else Tone.INFO,
    )
}

fun predictionDetail(label: String?, confidence: Double?, source: String?): String {
    if (label == null || confidence == null) return "aguardando fala"
    return "$label · ${(confidence * 100).roundToInt()}% · ${predictionSourceLabel(source)}"
}

fun predictionSourceLabel(source: String?): String = when (source) {
    "JEV" -> "Jev"
    "JEV_GUARD" -> "Jev + regra de cancelamento"
    "RULE" -> "regra determinística"
    "MODEL" -> "modelo local"
    else -> "classificador local"
}

private fun isJevUnavailable(label: String?, confidence: Double?, source: String?): Boolean =
    label == "UNKNOWN" && confidence == 0.0 && source == "JEV"

fun factCardContentDescription(title: String, value: String, detail: String): String =
    "$title: $value. $detail."

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
