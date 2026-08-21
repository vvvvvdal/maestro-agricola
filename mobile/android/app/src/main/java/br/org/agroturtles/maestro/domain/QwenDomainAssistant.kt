package br.org.agroturtles.maestro.domain

class QwenDomainAssistant(
    private val engine: QwenEngine,
) : DomainAssistant {

    override fun respond(
        text: String,
        completion: (Result<AssistantReply>) -> Unit,
    ) {
        engine.generate(
            systemPrompt = MaestroKnowledge.systemPrompt,
            userPrompt = text,
        ) { result ->
            completion(result.map(::parseReply))
        }
    }

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
                response = OUT_OF_SCOPE_MESSAGE,
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
