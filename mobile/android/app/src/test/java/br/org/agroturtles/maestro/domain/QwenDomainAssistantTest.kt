package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class QwenDomainAssistantTest {

    @Test
    fun validDomainReplyBecomesChat() {
        val assistant = QwenDomainAssistant(
            QwenEngine { _, _, completion ->
                completion(
                    Result.success(
                        """{"type":"CHAT","response":"O Maestro é um sistema da AgroTurtles."}"""
                    )
                )
            }
        )

        assistant.respond("o que é o Maestro?") { result ->
            val reply = result.getOrThrow()

            assertEquals(AssistantReplyType.CHAT, reply.type)
            assertEquals(
                "O Maestro é um sistema da AgroTurtles.",
                reply.response,
            )
        }
    }

    @Test
    fun systemAndUserPromptsArePassedSeparately() {
        var capturedSystemPrompt: String? = null
        var capturedUserPrompt: String? = null

        val assistant = QwenDomainAssistant(
            QwenEngine { systemPrompt, userPrompt, completion ->
                capturedSystemPrompt = systemPrompt
                capturedUserPrompt = userPrompt

                completion(
                    Result.success(
                        """{"type":"CHAT","response":"Resposta."}"""
                    )
                )
            }
        )

        assistant.respond("Como funciona o Maestro?") { result ->
            result.getOrThrow()
        }

        assertEquals(
            MaestroKnowledge.systemPrompt,
            capturedSystemPrompt,
        )
        assertEquals(
            "Como funciona o Maestro?",
            capturedUserPrompt,
        )
    }

    @Test
    fun canonicalKnowledgeIdentifiesAgroTurtles() {
        assertTrue(
            MaestroKnowledge.systemPrompt.contains(
                "desenvolvido pela equipe AgroTurtles"
            )
        )
    }

    @Test
    fun canonicalKnowledgeContainsSafetyRules() {
        val prompt = MaestroKnowledge.systemPrompt

        assertTrue(prompt.contains("ROS 2"))
        assertTrue(prompt.contains("Nav2"))
        assertTrue(prompt.contains("SPRAY, DOCK e UNDOCK"))
        assertTrue(prompt.contains("confirmação explícita"))
        assertTrue(prompt.contains("Nunca envie comandos ROS"))
        assertTrue(prompt.contains("Nunca envie mensagens WebSocket"))
        assertTrue(prompt.contains("Nunca altere o estado do robô"))
    }

    @Test
    fun canonicalKnowledgeDefinesOutOfScopeExamples() {
        val prompt = MaestroKnowledge.systemPrompt

        assertTrue(prompt.contains("Como fazer bolo de chocolate?"))
        assertTrue(prompt.contains("Faça dock agora."))
        assertTrue(prompt.contains("OUT_OF_SCOPE"))
        assertFalse(prompt.contains("\"type\":\"COMMAND\""))
    }

    @Test
    fun outOfScopeResponseIsNormalized() {
        val assistant = QwenDomainAssistant(
            QwenEngine { _, _, completion ->
                completion(
                    Result.success(
                        """{"type":"OUT_OF_SCOPE","response":"Qualquer texto inventado pelo modelo."}"""
                    )
                )
            }
        )

        assistant.respond("como fazer bolo?") { result ->
            val reply = result.getOrThrow()

            assertEquals(
                AssistantReplyType.OUT_OF_SCOPE,
                reply.type,
            )
            assertEquals(
                QwenDomainAssistant.OUT_OF_SCOPE_MESSAGE,
                reply.response,
            )
        }
    }

    @Test
    fun inventedCommandTypeFailsClosed() {
        val assistant = QwenDomainAssistant(
            QwenEngine { _, _, completion ->
                completion(
                    Result.success(
                        """{"type":"COMMAND","response":"Dock iniciado."}"""
                    )
                )
            }
        )

        assistant.respond("qualquer coisa") { result ->
            val reply = result.getOrThrow()

            assertEquals(
                AssistantReplyType.OUT_OF_SCOPE,
                reply.type,
            )
            assertEquals(
                QwenDomainAssistant.OUT_OF_SCOPE_MESSAGE,
                reply.response,
            )
        }
    }

    @Test
    fun malformedOutputFailsClosed() {
        val assistant = QwenDomainAssistant(
            QwenEngine { _, _, completion ->
                completion(Result.success("DOCK"))
            }
        )

        assistant.respond("qualquer coisa") { result ->
            val reply = result.getOrThrow()

            assertEquals(
                AssistantReplyType.OUT_OF_SCOPE,
                reply.type,
            )
            assertEquals(
                QwenDomainAssistant.OUT_OF_SCOPE_MESSAGE,
                reply.response,
            )
        }
    }
}
