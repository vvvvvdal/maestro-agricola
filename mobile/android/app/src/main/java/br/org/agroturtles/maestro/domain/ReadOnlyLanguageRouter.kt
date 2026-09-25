package br.org.agroturtles.maestro.domain

import java.text.Normalizer
import java.util.Locale

enum class ReadOnlyLanguageRoute {
    PLOT_STATUS_QUERY,
    STATUS_QUERY,
    INSPECT_TARGET,
    NONE,
}

/** Local, closed routing for read-only capabilities outside the six Jev labels. */
class ReadOnlyLanguageRouter {
    fun route(text: String): ReadOnlyLanguageRoute {
        val normalized = normalize(text)

        return when {
            looksLikeRobotStatusQuestion(normalized) -> ReadOnlyLanguageRoute.STATUS_QUERY
            looksLikePlotHistoryQuestion(normalized) -> ReadOnlyLanguageRoute.PLOT_STATUS_QUERY
            looksLikeInspectionRequest(normalized) -> ReadOnlyLanguageRoute.INSPECT_TARGET
            else -> ReadOnlyLanguageRoute.NONE
        }
    }

    private fun looksLikePlotHistoryQuestion(text: String): Boolean {
        val asksForHistory = listOf("ultima", "historico", "quando", "me diga", "informe")
            .any(text::contains)
        val refersToOperation = listOf("pulveriz", "aplic", "trat", "operacao", "mexeram")
            .any(text::contains)
        return asksForHistory && refersToOperation
    }

    private fun looksLikeRobotStatusQuestion(text: String): Boolean {
        val asksForStatus = listOf("status", "como esta", "situacao", "estado").any(text::contains)
        return asksForStatus && (text.contains("robo") || text.contains("operacao"))
    }

    private fun looksLikeInspectionRequest(text: String): Boolean {
        val requestsInspection = listOf("inspec", "leia", "identifique", "capture", "escaneie")
            .any(text::contains)
        val refersToMarker = listOf("marcador", "qr", "placa", "etiqueta").any(text::contains)
        return requestsInspection && refersToMarker
    }

    private fun normalize(text: String): String =
        Normalizer.normalize(text.lowercase(Locale.ROOT), Normalizer.Form.NFKD)
            .replace(Regex("\\p{M}+"), "")
}
