package br.org.agroturtles.maestro.domain


data class IntentPrediction(
    val label: String,
    val confidence: Double,
    val source: String = "MODEL",
)

fun interface IntentClassifier {
    fun classify(text: String): IntentPrediction
}
