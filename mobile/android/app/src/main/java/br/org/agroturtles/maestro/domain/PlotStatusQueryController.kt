package br.org.agroturtles.maestro.domain

import java.time.Instant
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale
import java.util.UUID

class PlotStatusQueryController(
    private val targetResolver: TargetResolver,
    private val transportFactory: () -> ReadOnlyQueryTransport,
    private val languageRouter: ReadOnlyLanguageRouter = ReadOnlyLanguageRouter(),
    private val requestId: () -> String = { UUID.randomUUID().toString() },
    private val requestedAt: () -> String = { Instant.now().toString() },
) {
    fun handle(
        text: String,
        completion: (InteractionResult) -> Unit,
    ): InteractionResult? {
        if (languageRouter.route(text) != ReadOnlyLanguageRoute.PLOT_STATUS_QUERY) return null

        val prediction = IntentPrediction(
            label = "PLOT_STATUS_QUERY",
            confidence = 1.0,
            source = "RULE",
        )
        val resolution = targetResolver.resolve(visualTargetId = null, transcript = text)
        if (resolution.status != TargetResolutionStatus.RESOLVED) {
            return queryResult(
                status = ReadOnlyQueryStatus.INVALID_QUERY,
                prediction = prediction,
            )
        }

        val plotId = checkNotNull(resolution.targetId)
        val query = ReadOnlyQuery(
            requestId = requestId(),
            requestedAt = requestedAt(),
            kind = LAST_SIMULATED_SPRAY_FOR_PLOT,
            plotId = plotId,
        )
        transportFactory().send(query) { response ->
            completion(queryResult(response, query, prediction))
        }

        return InteractionResult(
            state = InteractionState.QUERYING,
            message = "Consultando o histórico de ${plotLabel(plotId)}",
            speech = "Consultando o histórico de ${plotLabel(plotId)}.",
            prediction = prediction,
            intent = prediction.label,
            targetId = plotId,
            targetSource = "VOICE",
        )
    }

    private fun queryResult(
        response: ReadOnlyQueryResponse,
        query: ReadOnlyQuery,
        prediction: IntentPrediction,
    ): InteractionResult {
        val verified = response.requestId == query.requestId && response.kind == query.kind
        if (!verified) {
            return queryResult(ReadOnlyQueryStatus.UNAVAILABLE, prediction, query.plotId)
        }
        if (
            response.status == ReadOnlyQueryStatus.FOUND &&
            response.record?.plotId != query.plotId
        ) {
            return queryResult(ReadOnlyQueryStatus.UNAVAILABLE, prediction, query.plotId)
        }
        return queryResult(response.status, prediction, query.plotId, response.record)
    }

    private fun queryResult(
        status: ReadOnlyQueryStatus,
        prediction: IntentPrediction,
        plotId: String? = null,
        record: ReadOnlyOperationRecord? = null,
    ): InteractionResult {
        val message = when (status) {
            ReadOnlyQueryStatus.FOUND -> {
                val completedAt = record?.completedAt?.let(::formatCompletedAt)
                    ?: return queryResult(ReadOnlyQueryStatus.UNAVAILABLE, prediction, plotId)
                "A última missão simulada de pulverização no ${plotLabel(plotId)} " +
                    "foi concluída em $completedAt no Gazebo."
            }

            ReadOnlyQueryStatus.NOT_FOUND ->
                "Não há missão simulada de pulverização concluída para " +
                    "${plotLabel(plotId)} nesta sessão."

            ReadOnlyQueryStatus.INVALID_QUERY ->
                "Não consegui identificar um talhão cadastrado para consulta."

            ReadOnlyQueryStatus.UNAVAILABLE ->
                "A consulta está indisponível. Nenhum comando foi enviado."
        }

        return InteractionResult(
            state = InteractionState.QUERY_COMPLETED,
            message = message,
            speech = message,
            prediction = prediction,
            intent = prediction.label,
            targetId = plotId,
            targetSource = if (plotId == null) null else "VOICE",
        )
    }

    private fun formatCompletedAt(value: String): String? = runCatching {
        Instant.parse(value)
            .atZone(ZoneId.systemDefault())
            .format(
                DateTimeFormatter.ofPattern(
                    "dd/MM 'às' HH:mm",
                    Locale.forLanguageTag("pt-BR"),
                )
            )
    }.getOrNull()
}
