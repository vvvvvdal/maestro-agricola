package br.org.agroturtles.maestro.domain


data class IntentPrediction(
    val label: String,
    val confidence: Double,
)

fun interface IntentClassifier {
    fun classify(text: String): IntentPrediction
}
