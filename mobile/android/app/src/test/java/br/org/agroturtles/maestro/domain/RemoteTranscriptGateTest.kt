package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertSame
import org.junit.Test

class RemoteTranscriptGateTest {
    @Test
    fun allowsShortOperationalUtterances() {
        assertSame(RemoteTranscriptDecision.Allowed, RemoteTranscriptGate.evaluate("volte para a doca"))
        assertSame(RemoteTranscriptDecision.Allowed, RemoteTranscriptGate.evaluate("não faça isso agora"))
        assertSame(RemoteTranscriptDecision.Allowed, RemoteTranscriptGate.evaluate("pulverize o plot 02"))
    }

    @Test
    fun blocksObviousPersonalDataAndUrlsBeforeRemoteClassification() {
        listOf(
            "meu e-mail é pessoa@exemplo.test",
            "ligue para 11987654321 antes de voltar",
            "meu cpf é 000.000.000-00",
            "o cnpj é 00.000.000/0000-00",
        ).forEach { transcript ->
            assertEquals(
                transcript,
                RemoteTranscriptBlockReason.PERSONAL_DATA,
                blockedReason(transcript),
            )
        }
        assertEquals(
            RemoteTranscriptBlockReason.URL,
            blockedReason("veja https://exemplo.test e volte"),
        )
    }

    @Test
    fun blocksLongAndOutsideScopeTurns() {
        assertEquals(
            RemoteTranscriptBlockReason.TOO_LONG,
            blockedReason("x".repeat(RemoteTranscriptGate.MAX_CHARS + 1)),
        )
        assertEquals(
            RemoteTranscriptBlockReason.OUTSIDE_REMOTE_SCOPE,
            blockedReason("qual é a previsão do tempo para amanhã"),
        )
    }

    private fun blockedReason(transcript: String): RemoteTranscriptBlockReason {
        val decision = RemoteTranscriptGate.evaluate(transcript)
        return (decision as RemoteTranscriptDecision.Blocked).reason
    }
}
