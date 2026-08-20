package br.org.agroturtles.maestro.platform

import br.org.agroturtles.maestro.domain.Command
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import org.json.JSONObject
import java.util.concurrent.atomic.AtomicBoolean


class WebSocketCommandTransport(
    private val endpoint: String,
    private val client: OkHttpClient = sharedClient,
) : CommandTransport {
    override fun send(command: Command, completion: (Boolean, String) -> Unit) {
        val completed = AtomicBoolean(false)
        fun completeOnce(accepted: Boolean, reason: String) {
            if (completed.compareAndSet(false, true)) completion(accepted, reason)
        }
        val request = Request.Builder().url(endpoint).build()
        client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                webSocket.send(command.toJson())
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                runCatching { JSONObject(text) }
                    .onSuccess { payload ->
                        if (payload.optString("command_id") != command.commandId) {
                            completeOnce(false, "Resposta pertence a outro comando")
                        } else {
                            completeOnce(
                                payload.optString("status") == "ACCEPTED",
                                payload.optString("reason", payload.optString("status", "Resposta inválida")),
                            )
                        }
                    }
                    .onFailure { completeOnce(false, "Resposta inválida") }
                webSocket.close(1000, null)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                completeOnce(false, t.message ?: "Falha de conexão")
                webSocket.close(1001, null)
            }
        })
    }

    private fun Command.toJson(): String {
        val payload = JSONObject()
            .put("schema_version", "1.0")
            .put("command_id", commandId)
            .put("created_at", createdAt)
            .put("expires_in_ms", 5000)
            .put("intent", intent)
            .put("confirmed", true)

        if (targetId != null) {
            payload.put(
                "target",
                JSONObject()
                    .put("type", "MAPPED_PLOT")
                    .put("id", targetId)
            )
        } else {
            payload.put("target", JSONObject.NULL)
        }

        return payload.toString()
    }

    companion object {
        private val sharedClient = OkHttpClient()
    }
}
