package br.org.agroturtles.maestro.domain

/** Experimental boundary for obtaining one Jev Choice evaluation. */
fun interface JevChoiceEvaluator {
    fun evaluate(text: String): JevEvaluation
}
