package br.org.agroturtles.maestro.platform

import br.org.agroturtles.maestro.domain.JevChoiceAnswer
import br.org.agroturtles.maestro.domain.JevChoiceEvaluator
import br.org.agroturtles.maestro.domain.JevErrorCode
import br.org.agroturtles.maestro.domain.JevEvaluation
import br.org.agroturtles.maestro.domain.JevEvaluationError
import br.org.agroturtles.maestro.domain.JevUsage
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.io.IOException
import java.util.concurrent.TimeUnit

/**
 * Talks only to the local demonstration proxy. The TypeSafe credential and
 * Choice rubric intentionally stay outside Android.
 */
class JevProxyChoiceEvaluator(
    private val client: OkHttpClient = OkHttpClient.Builder()
        .callTimeout(5, TimeUnit.SECONDS)
        .build(),
) : JevChoiceEvaluator {
    @Volatile
    var enabled = false

    override fun evaluate(text: String): JevEvaluation {
        if (!enabled) return failure(JevErrorCode.TRANSPORT)
        val body = JSONObject().put("transcript", text).toString()
            .toRequestBody("application/json; charset=utf-8".toMediaType())
        val request = Request.Builder().url(LOOPBACK_URL).post(body).build()

        return try {
            client.newCall(request).execute().use { response ->
                val responseBody = response.body.string()
                if (!response.isSuccessful) return failure(errorCode(responseBody, response.code))
                parse(responseBody)
            }
        } catch (_: IOException) {
            failure(JevErrorCode.TIMEOUT)
        } catch (_: Exception) {
            failure(JevErrorCode.INVALID_RESPONSE)
        }
    }

    private fun parse(raw: String): JevEvaluation {
        val payload = JSONObject(raw)
        val answer = payload.getJSONObject("answer")
        val probabilitiesJson = answer.getJSONObject("probabilities")
        val probabilities = SUPPORTED_LABELS.associateWith { probabilitiesJson.getDouble(it) }
        return JevEvaluation(
            requestedModel = payload.getString("requested_model"),
            responseModel = payload.getString("response_model"),
            answer = JevChoiceAnswer(
                choice = answer.getString("choice"),
                probabilities = probabilities,
                confidence = answer.getDouble("confidence"),
            ),
            usage = payload.getJSONObject("usage").let {
                JevUsage(it.getInt("input_tokens"), it.getInt("output_tokens"))
            },
            latencyMs = payload.getLong("latency_ms"),
        )
    }

    private fun errorCode(raw: String, status: Int): JevErrorCode = try {
        JevErrorCode.valueOf(JSONObject(raw).getJSONObject("error").getString("code"))
    } catch (_: Exception) {
        JevErrorCode.fromHttpStatus(status)
    }

    private fun failure(code: JevErrorCode): JevEvaluation = JevEvaluation(
        requestedModel = MODEL,
        latencyMs = 0,
        error = JevEvaluationError(code),
    )

    private companion object {
        const val MODEL = "jev-1.13.0"
        const val LOOPBACK_URL = "http://127.0.0.1:8787/v1/intent"
        val SUPPORTED_LABELS = listOf("SPRAY", "DOCK", "UNDOCK", "CONFIRM", "CANCEL", "UNKNOWN")
    }
}
