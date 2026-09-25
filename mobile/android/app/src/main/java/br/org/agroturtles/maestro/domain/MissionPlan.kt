package br.org.agroturtles.maestro.domain

import java.text.Normalizer
import java.time.Clock
import java.time.Instant
import java.util.Locale
import java.util.UUID

const val MISSION_PREVIEW_INTENT = "MISSION_PREVIEW"

enum class MissionStepIntent {
    UNDOCK,
    SPRAY,
    PLOT_STATUS_QUERY,
    DOCK,
}

data class MissionStep(
    val stepId: String,
    val intent: MissionStepIntent,
    val targetId: String? = null,
)

data class MissionPlan(
    val schemaVersion: String = "1.0",
    val planId: String,
    val createdAt: String,
    val steps: List<MissionStep>,
)

sealed interface MissionPreviewParseResult {
    data object NotApplicable : MissionPreviewParseResult
    data class Preview(val plan: MissionPlan) : MissionPreviewParseResult
    data class Rejected(val reason: String) : MissionPreviewParseResult
}

/**
 * Parses only the small, documented mission grammar. It never creates a
 * Command: execution is intentionally owned by the later mission executor.
 */
class MissionPreviewParser(
    private val targetResolver: TargetResolver,
    private val clock: Clock = Clock.systemUTC(),
    private val planIdFactory: () -> String = { UUID.randomUUID().toString() },
) {
    fun parse(text: String): MissionPreviewParseResult {
        val clauses = splitClauses(text)
        if (clauses.size < 2) return MissionPreviewParseResult.NotApplicable

        val steps = clauses.mapIndexed { index, clause ->
            parseStep(index, clause) ?: return MissionPreviewParseResult.Rejected(
                "Não entendi a etapa ${index + 1} da missão."
            )
        }
        val validationError = validate(steps)
        if (validationError != null) return MissionPreviewParseResult.Rejected(validationError)

        return MissionPreviewParseResult.Preview(
            MissionPlan(
                planId = planIdFactory(),
                createdAt = Instant.now(clock).toString(),
                steps = steps,
            )
        )
    }

    private fun splitClauses(text: String): List<String> {
        val normalized = text.trim()
        if (normalized.isBlank()) return emptyList()
        return normalized
            .replace(Regex("(?i)\\s*,\\s*"), "|")
            .replace(Regex("(?i)\\s+e\\s+depois\\s+"), "|")
            .replace(Regex("(?i)\\s+depois\\s+"), "|")
            .replace(Regex("(?i)\\s+então\\s+|\\s+entao\\s+"), "|")
            .replace(
                Regex("(?i)\\s+e\\s+(?=(saia|sair|pulverize|pulverizar|verifique|informe|volte|voltar|retorne|retornar)\\b)"),
                "|",
            )
            .split('|')
            .map(String::trim)
            .filter(String::isNotBlank)
    }

    private fun parseStep(index: Int, clause: String): MissionStep? {
        val normalized = normalize(clause)
        val intent = when {
            containsAny(normalized, "desacopl", "saia da doca", "sair da doca", "saia da base", "sair da base") ->
                MissionStepIntent.UNDOCK

            containsAny(normalized, "volte para a doca", "voltar para a doca", "retorne para a doca", "retornar para a doca", "volte para a base", "retorne para a base", "acopl") ->
                MissionStepIntent.DOCK

            containsAny(normalized, "ultima pulverizacao", "ultima aplicacao", "historico", "histórico", "quando foi", "informe a ultima", "informe a última") ->
                MissionStepIntent.PLOT_STATUS_QUERY

            containsAny(normalized, "pulveriz", "aplique", "aplicacao", "aplicação", "trate") ->
                MissionStepIntent.SPRAY

            else -> return null
        }

        val targetRequired = intent == MissionStepIntent.SPRAY ||
            intent == MissionStepIntent.PLOT_STATUS_QUERY
        val targetId = if (targetRequired) {
            val resolution = targetResolver.resolve(null, clause)
            if (resolution.status != TargetResolutionStatus.RESOLVED) return null
            resolution.targetId
        } else {
            null
        }

        return MissionStep(
            stepId = "step-${index + 1}",
            intent = intent,
            targetId = targetId,
        )
    }

    private fun validate(steps: List<MissionStep>): String? {
        if (steps.size !in 2..4) return "A missão precisa ter entre duas e quatro etapas."
        if (steps.map(MissionStep::stepId).distinct().size != steps.size) {
            return "A missão tem etapas repetidas."
        }
        if (steps.count { it.intent == MissionStepIntent.UNDOCK } > 1 ||
            steps.count { it.intent == MissionStepIntent.DOCK } > 1
        ) {
            return "A missão não pode repetir saída ou retorno à doca."
        }
        val undockIndex = steps.indexOfFirst { it.intent == MissionStepIntent.UNDOCK }
        if (undockIndex > 0) return "Sair da doca precisa ser a primeira etapa."
        val dockIndex = steps.indexOfFirst { it.intent == MissionStepIntent.DOCK }
        if (dockIndex >= 0 && dockIndex != steps.lastIndex) {
            return "Voltar para a doca precisa ser a última etapa."
        }
        return null
    }

    private fun containsAny(text: String, vararg fragments: String): Boolean =
        fragments.any { text.contains(normalize(it)) }

    private fun normalize(text: String): String =
        Normalizer.normalize(text.lowercase(Locale.ROOT), Normalizer.Form.NFKD)
            .replace(Regex("\\p{M}+"), "")
}
