package br.org.agroturtles.maestro.domain

data class ReadOnlyQuery(
    val requestId: String,
    val requestedAt: String,
    val kind: String,
    val plotId: String? = null,
    val commandId: String? = null,
)

data class ReadOnlyOperationRecord(
    val plotId: String,
    val completedAt: String,
    val origin: String,
)

enum class RobotOperationState {
    QUEUED,
    EXECUTING,
    COMPLETED,
    FAILED,
}

data class ReadOnlyRobotOperation(
    val commandId: String,
    val intent: String,
    val targetId: String?,
    val state: RobotOperationState,
)

enum class ReadOnlyQueryStatus {
    FOUND,
    NOT_FOUND,
    INVALID_QUERY,
    UNAVAILABLE,
}

data class ReadOnlyQueryResponse(
    val requestId: String,
    val kind: String,
    val status: ReadOnlyQueryStatus,
    val record: ReadOnlyOperationRecord? = null,
    val operation: ReadOnlyRobotOperation? = null,
)

fun interface ReadOnlyQueryTransport {
    fun send(query: ReadOnlyQuery, completion: (ReadOnlyQueryResponse) -> Unit)
}

const val LAST_SIMULATED_SPRAY_FOR_PLOT = "LAST_SIMULATED_SPRAY_FOR_PLOT"
const val ROBOT_STATUS = "ROBOT_STATUS"
