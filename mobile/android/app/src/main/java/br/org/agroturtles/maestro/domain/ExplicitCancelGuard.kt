package br.org.agroturtles.maestro.domain

import java.text.Normalizer
import java.util.Locale

fun interface ExplicitCancelGuard {
    fun matches(text: String): Boolean

    companion object {
        fun disabled(): ExplicitCancelGuard = ExplicitCancelGuard { false }

        fun developmentPolicy(): ExplicitCancelGuard = PatternCancelGuard(
            listOf(
                "^(cancelar|cancele|cancela|abortar|aborte|aborta|interromper|interrompa|recusar|recuse|desista)$",
                "^nao (execute|executar|envie|enviar|faca|pulverize|pulverizar|aplique|aplicar|confirme|confirmar|prossiga|prosseguir)$",
                "^(deixa quieto|deixe quieto|melhor nao|esquece isso|esqueca isso|volte atras)$",
                "^segure essa operacao$",
            ).map(::Regex),
        )
    }
}

private class PatternCancelGuard(
    private val patterns: List<Regex>,
) : ExplicitCancelGuard {
    override fun matches(text: String): Boolean {
        val normalized = Normalizer.normalize(text.lowercase(Locale.ROOT), Normalizer.Form.NFKD)
            .replace(Regex("\\p{M}+"), "")
        val tokens = Regex("[a-z0-9]+").findAll(normalized).joinToString(" ") { it.value }
        return patterns.any { it.matches(tokens) }
    }
}
