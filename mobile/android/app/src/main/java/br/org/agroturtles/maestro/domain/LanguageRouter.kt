package br.org.agroturtles.maestro.domain

enum class LanguageRouteType {
    OPERATIONAL,
    ASSISTANT,
}

data class LanguageRoute(
    val type: LanguageRouteType,
    val prediction: IntentPrediction,
    val assistantText: String? = null,
)

class LanguageRouter(
    private val classifier: IntentClassifier,
) {
    fun route(text: String): LanguageRoute {
        val prediction = classifier.classify(text)

        return if (prediction.label == "UNKNOWN") {
            LanguageRoute(
                type = LanguageRouteType.ASSISTANT,
                prediction = prediction,
                assistantText = text,
            )
        } else {
            LanguageRoute(
                type = LanguageRouteType.OPERATIONAL,
                prediction = prediction,
            )
        }
    }
}
