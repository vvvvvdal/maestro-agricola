package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ExplicitCancelGuardTest {

    private val guard = ExplicitCancelGuard.developmentPolicy()

    @Test
    fun matchesOnlyExplicitCancellationPhrases() {
        listOf(
            "cancele",
            "não pulverize",
            "deixa quieto",
            "segure essa operação",
        ).forEach { text ->
            assertTrue(text, guard.matches(text))
        }
    }

    @Test
    fun leavesConversationHistoryAndHesitationOutsideTheGuard() {
        listOf(
            "não sei se devo pulverizar",
            "o produto foi pulverizado ontem",
            "talvez pulverize depois",
            "explique como cancelar",
        ).forEach { text ->
            assertFalse(text, guard.matches(text))
        }
    }
}
