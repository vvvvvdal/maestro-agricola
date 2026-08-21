package br.org.agroturtles.maestro.domain

class QwenDomainAssistant(
    private val engine: QwenEngine,
) : DomainAssistant {

    override fun respond(
        text: String,
        completion: (Result<AssistantReply>) -> Unit,
    ) {
        engine.generate(buildPrompt(text)) { result ->
            completion(
                result.map { raw ->
                    parseReply(raw)
                }
            )
        }
    }

    internal fun buildPrompt(text: String): String =
        """
        Você é o assistente local do Maestro Agrícola.

        Responda somente sobre:
        - o Maestro Agrícola;
        - funcionamento do sistema;
        - visão e identificação de alvos;
        - comandos suportados;
        - confirmação de segurança;
        - pulverização;
        - dock e undock;
        - operação do robô;
        - limitações e uso da solução.

        Não responda perguntas gerais fora desse domínio.
        Não ensine programação, matemática, receitas ou assuntos não relacionados.
        Não execute ações.
        Não gere comandos ROS.
        Não altere o estado do robô.

        Responda SOMENTE JSON válido em um destes formatos:

        {"type":"CHAT","response":"resposta curta em português"}

        ou

        {"type":"OUT_OF_SCOPE","response":"Posso ajudar apenas com assuntos relacionados ao Maestro Agrícola."}

        Em caso de dúvida, use OUT_OF_SCOPE.

        Pergunta do operador:
        $text
        """.trimIndent()

    internal fun parseReply(raw: String): AssistantReply {
        val type = TYPE_REGEX.find(raw)
            ?.groupValues
            ?.getOrNull(1)

        val response = RESPONSE_REGEX.find(raw)
            ?.groupValues
            ?.getOrNull(1)
            ?.let(::decodeJsonString)

        if (type == null || response.isNullOrBlank()) {
            return safeFallback()
        }

        return when (type) {
            "CHAT" -> AssistantReply(
                type = AssistantReplyType.CHAT,
                response = response,
            )

            "OUT_OF_SCOPE" -> AssistantReply(
                type = AssistantReplyType.OUT_OF_SCOPE,
                response = response,
            )

            else -> safeFallback()
        }
    }

    private fun safeFallback() = AssistantReply(
        type = AssistantReplyType.OUT_OF_SCOPE,
        response = OUT_OF_SCOPE_MESSAGE,
    )

    private fun decodeJsonString(value: String): String =
        value
            .replace("\\\"", "\"")
            .replace("\\n", "\n")
            .replace("\\\\", "\\")

    companion object {
        private val TYPE_REGEX =
            Regex("\"type\"\\s*:\\s*\"([A-Z_]+)\"")

        private val RESPONSE_REGEX =
            Regex("\"response\"\\s*:\\s*\"((?:\\\\.|[^\"\\\\])*)\"")

        const val OUT_OF_SCOPE_MESSAGE =
            "Posso ajudar apenas com assuntos relacionados ao Maestro Agrícola."
    }
}
