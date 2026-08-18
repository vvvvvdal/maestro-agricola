package br.org.agroturtles.maestro.domain

import java.text.Normalizer
import java.util.Locale
import org.json.JSONObject


enum class TargetResolutionStatus { RESOLVED, NEEDS_VISUAL, CONFLICT, UNKNOWN }

data class TargetResolution(
    val status: TargetResolutionStatus,
    val targetId: String? = null,
    val source: String? = null,
)

class TargetResolver(private val allowedTargetIds: Set<String>) {
    fun resolve(visualTargetId: String?, transcript: String): TargetResolution {
        val visual = canonicalTargetId(visualTargetId)
        val spoken = extractSpokenTargetId(transcript)
        if (visual != null && spoken != null && visual != spoken) {
            return TargetResolution(TargetResolutionStatus.CONFLICT)
        }
        val candidate = visual ?: spoken
        if (candidate != null && candidate !in allowedTargetIds) {
            return TargetResolution(TargetResolutionStatus.UNKNOWN)
        }
        return when {
            visual != null && spoken != null -> TargetResolution(TargetResolutionStatus.RESOLVED, candidate, "AGREED")
            visual != null -> TargetResolution(TargetResolutionStatus.RESOLVED, visual, "VISUAL")
            spoken != null -> TargetResolution(TargetResolutionStatus.RESOLVED, spoken, "VOICE")
            else -> TargetResolution(TargetResolutionStatus.NEEDS_VISUAL)
        }
    }

    companion object {
        private val numberWords = mapOf(
            "zero" to 0, "um" to 1, "uma" to 1, "dois" to 2, "duas" to 2,
            "tres" to 3, "quatro" to 4, "cinco" to 5, "seis" to 6,
            "sete" to 7, "oito" to 8, "nove" to 9,
        )

        fun fromJson(json: String): TargetResolver {
            val targets = JSONObject(json).getJSONObject("targets")
            return TargetResolver(targets.keys().asSequence().toSet())
        }

        private fun normalizedTokens(text: String): List<String> {
            val normalized = Normalizer.normalize(text.lowercase(Locale.ROOT), Normalizer.Form.NFKD)
                .replace(Regex("\\p{M}+"), "")
            return Regex("[a-z0-9]+").findAll(normalized).map { it.value }.toList()
        }

        private fun canonicalTargetId(value: String?): String? {
            if (value.isNullOrBlank()) return null
            val normalized = value.trim().lowercase(Locale.ROOT)
            val match = Regex("^plot[-_ ]?(\\d{1,3})$").matchEntire(normalized) ?: return normalized
            return "plot-${match.groupValues[1].toInt().toString().padStart(2, '0')}"
        }

        private fun extractSpokenTargetId(transcript: String): String? {
            val tokens = normalizedTokens(transcript)
            tokens.forEachIndexed { index, token ->
                if (token !in setOf("plot", "talhao") || index + 1 >= tokens.size) return@forEachIndexed
                val first = tokens[index + 1]
                val number = first.toIntOrNull() ?: numberWords[first]?.let { firstDigit ->
                    val secondDigit = tokens.getOrNull(index + 2)?.let(numberWords::get)
                    if (secondDigit == null) firstDigit else firstDigit * 10 + secondDigit
                }
                if (number != null) return "plot-${number.toString().padStart(2, '0')}"
            }
            return null
        }
    }
}
