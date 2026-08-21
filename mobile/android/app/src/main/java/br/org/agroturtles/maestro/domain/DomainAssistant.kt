package br.org.agroturtles.maestro.domain

enum class AssistantReplyType {
    CHAT,
    OUT_OF_SCOPE,
}

data class AssistantReply(
    val type: AssistantReplyType,
    val response: String,
    val source: String = "QWEN",
)

fun interface DomainAssistant {
    fun respond(
        text: String,
        completion: (Result<AssistantReply>) -> Unit,
    )
}
