package br.org.agroturtles.maestro.domain

class FakeJevChoiceEvaluator(
    private val evaluations: Map<String, JevEvaluation>,
) : JevChoiceEvaluator {
    override fun evaluate(text: String): JevEvaluation = requireNotNull(evaluations[text]) {
        "No fake Jev evaluation configured for text"
    }
}
