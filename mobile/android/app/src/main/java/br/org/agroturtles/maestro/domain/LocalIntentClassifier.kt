package br.org.agroturtles.maestro.domain

import java.text.Normalizer
import java.util.Locale
import kotlin.math.exp
import org.json.JSONObject


class LocalIntentClassifier private constructor(
    private val labels: List<String>,
    private val bias: Map<String, Double>,
    private val weights: Map<String, Map<String, Double>>,
    private val rules: List<Pair<String, List<Regex>>>,
    private val threshold: Double,
) : IntentClassifier {

    private val vocabulary = weights.values.flatMapTo(mutableSetOf()) { it.keys }

    override fun classify(text: String): IntentPrediction {
        val normalized = normalizeText(text)
        rules.firstOrNull { (_, patterns) -> patterns.any { it.containsMatchIn(normalized) } }
            ?.let { (label, _) -> return IntentPrediction(label, 1.0, "RULE") }

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
            require(payload.getString("model_type") in setOf("linear_softmax", "hybrid_regex_linear_softmax"))
            val labelsJson = payload.getJSONArray("labels")
            val labels = List(labelsJson.length()) { labelsJson.getString(it) }
            val biasJson = payload.getJSONObject("bias")
            val bias = labels.associateWith(biasJson::getDouble)
            val weightsJson = payload.getJSONObject("weights")
            val weights = labels.associateWith { label ->
                val values = weightsJson.getJSONObject(label)
                values.keys().asSequence().associateWith(values::getDouble)
            }
            val rules = if (payload.has("deterministic_rules")) {
                val rulesJson = payload.getJSONArray("deterministic_rules")
                List(rulesJson.length()) { index ->
                    val rule = rulesJson.getJSONObject(index)
                    val patterns = rule.getJSONArray("patterns")
                    rule.getString("label") to List(patterns.length()) { patterns.getString(it).toRegex() }
                }
            } else {
                emptyList()
            }
            return LocalIntentClassifier(labels, bias, weights, rules, threshold)
        }

        private fun normalizeText(text: String): String {
            val normalized = Normalizer.normalize(text.lowercase(Locale.ROOT), Normalizer.Form.NFKD)
                .replace(Regex("\\p{M}+"), "")
            return Regex("[a-z0-9]+").findAll(normalized).joinToString(" ") { it.value }
        }

        private fun features(text: String): Set<String> {
            val tokens = normalizeText(text).split(" ").filter(String::isNotEmpty)
            return buildSet {
                tokens.forEach { token ->
                    add("u:$token")
                    val padded = "^$token$"
                    for (size in 3..5) {
                        for (index in 0..padded.length - size) {
                            add("c$size:${padded.substring(index, index + size)}")
                        }
                    }
                }
                tokens.zipWithNext().forEach { (left, right) -> add("b:${left}_$right") }
            }
        }
    }
}
