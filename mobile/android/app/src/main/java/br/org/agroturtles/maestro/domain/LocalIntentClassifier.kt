package br.org.agroturtles.maestro.domain

import java.text.Normalizer
import java.util.Locale
import kotlin.math.exp
import org.json.JSONObject


class LocalIntentClassifier private constructor(
    private val labels: List<String>,
    private val bias: Map<String, Double>,
    private val weights: Map<String, Map<String, Double>>,
    private val threshold: Double,
) : IntentClassifier {

    private val vocabulary = weights.values.flatMapTo(mutableSetOf()) { it.keys }

    override fun classify(text: String): IntentPrediction {
        val current = features(text).filterTo(mutableSetOf()) { it in vocabulary }
        if (current.isEmpty()) return IntentPrediction("UNKNOWN", 1.0)

        val scores = labels.associateWith { label ->
            bias.getValue(label) + current.sumOf { weights.getValue(label)[it] ?: 0.0 }
        }
        val peak = scores.values.max()
        val denominator = scores.values.sumOf { exp(it - peak) }
        val best = scores.maxBy { it.value }
        val confidence = exp(best.value - peak) / denominator
        return if (best.key != "UNKNOWN" && confidence < threshold) {
            IntentPrediction("UNKNOWN", confidence)
        } else {
            IntentPrediction(best.key, confidence)
        }
    }

    companion object {
        fun fromJson(json: String, threshold: Double = 0.40): LocalIntentClassifier {
            val payload = JSONObject(json)
            require(payload.getString("model_type") == "linear_softmax")
            val labelsJson = payload.getJSONArray("labels")
            val labels = List(labelsJson.length()) { labelsJson.getString(it) }
            val biasJson = payload.getJSONObject("bias")
            val bias = labels.associateWith(biasJson::getDouble)
            val weightsJson = payload.getJSONObject("weights")
            val weights = labels.associateWith { label ->
                val values = weightsJson.getJSONObject(label)
                values.keys().asSequence().associateWith(values::getDouble)
            }
            return LocalIntentClassifier(labels, bias, weights, threshold)
        }

        private fun features(text: String): Set<String> {
            val normalized = Normalizer.normalize(text.lowercase(Locale.ROOT), Normalizer.Form.NFKD)
                .replace(Regex("\\p{M}+"), "")
            val tokens = Regex("[a-z0-9]+").findAll(normalized).map { it.value }.toList()
            return buildSet {
                tokens.forEach { token ->
                    add("u:$token")
                    if (token.length >= 6) {
                        add("p6:${token.take(6)}")
                        add("s6:${token.takeLast(6)}")
                    }
                }
                tokens.zipWithNext().forEach { (left, right) -> add("b:${left}_$right") }
            }
        }
    }
}
