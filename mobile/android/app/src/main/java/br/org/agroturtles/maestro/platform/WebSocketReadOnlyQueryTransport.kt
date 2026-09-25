package br.org.agroturtles.maestro.platform

import br.org.agroturtles.maestro.domain.ReadOnlyOperationRecord
import br.org.agroturtles.maestro.domain.ReadOnlyRobotOperation
import br.org.agroturtles.maestro.domain.ReadOnlyQuery
import br.org.agroturtles.maestro.domain.ReadOnlyQueryResponse
import br.org.agroturtles.maestro.domain.ReadOnlyQueryStatus
import br.org.agroturtles.maestro.domain.ReadOnlyQueryTransport
import br.org.agroturtles.maestro.domain.RobotOperationState
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import org.json.JSONObject
import java.util.concurrent.atomic.AtomicBoolean

class WebSocketReadOnlyQueryTransport(
    endpoint: String,
    private val client: OkHttpClient = sharedClient,
) : ReadOnlyQueryTransport {
    private val endpoint = endpoint.trimEnd('/') + "/read-only"

    override fun send(query: ReadOnlyQuery, completion: (ReadOnlyQueryResponse) -> Unit) {
        val completed = AtomicBoolean(false)
        fun completeOnce(response: ReadOnlyQueryResponse) {
            if (completed.compareAndSet(false, true)) completion(response)
        }
        val request = Request.Builder().url(endpoint).build()
        client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                webSocket.send(query.toJson())
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                completeOnce(parseResponse(text, query))
                webSocket.close(1000, null)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                completeOnce(unavailable(query))
                webSocket.close(1001, null)
            }
        })
    }

    private fun parseResponse(text: String, query: ReadOnlyQuery): ReadOnlyQueryResponse =
        runCatching {
            val payload = JSONObject(text)
            val status = ReadOnlyQueryStatus.valueOf(payload.getString("status"))
            val record = payload.optJSONObject("record")?.let {
                ReadOnlyOperationRecord(
                    plotId = it.getString("plot_id"),
                    completedAt = it.getString("completed_at"),
                    origin = it.getString("origin"),
                )
            }
            val operation = payload.optJSONObject("operation")?.let {
                ReadOnlyRobotOperation(
                    commandId = it.getString("command_id"),
                    intent = it.getString("intent"),
                    targetId = it.optString("target_id").takeIf(String::isNotBlank),
                    state = RobotOperationState.valueOf(it.getString("state")),
                )
            }
            ReadOnlyQueryResponse(
                requestId = payload.getString("request_id"),
                kind = payload.getString("kind"),
                status = status,
                record = record,
                operation = operation,
            )
        }.getOrElse { unavailable(query) }

    private fun unavailable(query: ReadOnlyQuery) = ReadOnlyQueryResponse(
        requestId = query.requestId,
        kind = query.kind,
        status = ReadOnlyQueryStatus.UNAVAILABLE,
    )

    private fun ReadOnlyQuery.toJson(): String = JSONObject()
        .put("schema_version", "1.0")
        .put("request_id", requestId)
        .put("requested_at", requestedAt)
        .put("kind", kind)
        .also { payload ->
            plotId?.let { payload.put("plot_id", it) }
            commandId?.let { payload.put("command_id", it) }
        }
        .toString()

    private companion object {
        val sharedClient = OkHttpClient()
    }
}
