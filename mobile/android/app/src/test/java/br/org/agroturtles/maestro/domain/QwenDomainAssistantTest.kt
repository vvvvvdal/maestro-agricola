package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class QwenDomainAssistantTest {

    @Test
    fun validDomainReplyBecomesChat() {
        val assistant = QwenDomainAssistant(
            QwenEngine { _, completion ->
                completion(
                    Result.success(
                        """{"type":"CHAT","response":"O Maestro permite comandar o robô por voz."}"""
                    )
                )
            }
        )

        assistant.respond("o que é o Maestro?") { result ->
            val reply = result.getOrThrow()

            assertEquals(AssistantReplyType.CHAT, reply.type)
            assertEquals(
                "O Maestro permite comandar o robô por voz.",
                reply.response,
            )
        }
    }

    @Test
    fun outOfScopeReplyRemainsOutOfScope() {
        val assistant = QwenDomainAssistant(
            QwenEngine { _, completion ->
                completion(
                    Result.success(
                        """{"type":"OUT_OF_SCOPE","response":"Posso ajudar apenas com assuntos relacionados ao Maestro Agrícola."}"""
                    )
                )
            }
        )

        assistant.respond("me ensina uma receita") { result ->
            assertEquals(
                AssistantReplyType.OUT_OF_SCOPE,
                result.getOrThrow().type,
            )
        }
    }

    @Test
    fun inventedCommandTypeFailsClosed() {
        val assistant = QwenDomainAssistant(
            QwenEngine { _, completion ->
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
            QwenEngine { _, completion ->
                completion(Result.success("DOCK"))
            }
        )

        assistant.respond("qualquer coisa") { result ->
            assertEquals(
                AssistantReplyType.OUT_OF_SCOPE,
                result.getOrThrow().type,
            )
        }
    }

    @Test
    fun promptExplicitlyForbidsRobotExecution() {
        val assistant = QwenDomainAssistant(
            QwenEngine { _, _ -> }
        )

        val prompt = assistant.buildPrompt(
            "como funciona a pulverização?"
        )

        assertTrue(prompt.contains("Não gere comandos ROS"))
        assertTrue(prompt.contains("Não altere o estado do robô"))
        assertTrue(prompt.contains("OUT_OF_SCOPE"))
        assertFalse(prompt.contains("\"type\":\"COMMAND\""))
    }
}
