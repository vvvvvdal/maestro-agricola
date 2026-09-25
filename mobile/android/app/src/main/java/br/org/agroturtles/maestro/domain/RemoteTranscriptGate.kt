package br.org.agroturtles.maestro.domain

import java.text.Normalizer

sealed interface RemoteTranscriptDecision {
    data object Allowed : RemoteTranscriptDecision

    data class Blocked(val reason: RemoteTranscriptBlockReason) : RemoteTranscriptDecision
}

enum class RemoteTranscriptBlockReason {
    PERSONAL_DATA,
    URL,
    TOO_LONG,
    OUTSIDE_REMOTE_SCOPE,
}

/**
 * Conservative, local-only filter for the optional mockDebug Jev path.
 *
 * It is intentionally a prevention aid, not a detector that can prove a
 * transcript has no personal data.
 */
object RemoteTranscriptGate {
    const val MAX_CHARS = 180

    private val emailPattern = Regex("""\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b""")
    private val phonePattern = Regex("""(?<!\d)(?:\+?\d[ .()\-]*){8,}\d(?!\d)""")
    private val cpfPattern = Regex("""(?<!\d)\d{3}[.\s]?\d{3}[.\s]?\d{3}[-\s]?\d{2}(?!\d)""")
    private val cnpjPattern = Regex("""(?<!\d)\d{2}[.\s]?\d{3}[.\s]?\d{3}[-/\s]?\d{4}[-\s]?\d{2}(?!\d)""")
    private val urlPattern = Regex("""\b(?:https?://|www\.)""", RegexOption.IGNORE_CASE)
    private val remoteScopeTerms = setOf(
        "pulveriz", "apli", "defensiv", "trat", "produto", "talhao", "plot",
        "doca", "base", "carreg", "retorn", "volt", "sai", "desacopl",
        "confirm", "cance", "cancel", "nao", "deixa", "pare", "segur",
        "sim", "isso", "liberad", "certo", "pode",
    )

    fun evaluate(transcript: String): RemoteTranscriptDecision = when {
        transcript.length > MAX_CHARS -> RemoteTranscriptDecision.Blocked(
            RemoteTranscriptBlockReason.TOO_LONG
        )
        urlPattern.containsMatchIn(transcript) -> RemoteTranscriptDecision.Blocked(
            RemoteTranscriptBlockReason.URL
        )
        listOf(emailPattern, phonePattern, cpfPattern, cnpjPattern).any {
            it.containsMatchIn(transcript)
        } -> RemoteTranscriptDecision.Blocked(RemoteTranscriptBlockReason.PERSONAL_DATA)
        remoteScopeTerms.none { normalize(transcript).contains(it) } -> RemoteTranscriptDecision.Blocked(
            RemoteTranscriptBlockReason.OUTSIDE_REMOTE_SCOPE
        )
        else -> RemoteTranscriptDecision.Allowed
    }

    private fun normalize(value: String): String = Normalizer.normalize(value, Normalizer.Form.NFD)
        .replace(Regex("\\p{Mn}+"), "")
        .lowercase()
}
