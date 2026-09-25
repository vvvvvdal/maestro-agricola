package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test


class RobotStatusQueryControllerTest {
    @Test
    fun recognizesStatusQuestionWithoutCreatingCommand() {
        val transport = FakeReadOnlyQueryTransport()
        val controller = RobotStatusQueryController(
            transportFactory = { transport },
            requestId = { REQUEST_ID },
            requestedAt = { "2026-09-25T15:34:00Z" },
        )
        var completed: InteractionResult? = null

        val pending = controller.handle("qual o status do robô?") { completed = it }

        assertEquals(InteractionState.QUERYING, pending?.state)
        assertEquals("STATUS_QUERY", pending?.intent)
        assertEquals(ROBOT_STATUS, transport.lastQuery?.kind)
        assertNull(transport.lastQuery?.commandId)
        assertNull(pending?.command)

        transport.respond(
            ReadOnlyQueryResponse(
                requestId = REQUEST_ID,
                kind = ROBOT_STATUS,
                status = ReadOnlyQueryStatus.NOT_FOUND,
            )
        )

        assertEquals(InteractionState.QUERY_COMPLETED, completed?.state)
        assertTrue(checkNotNull(completed).message.contains("aguardando"))
        assertNull(completed?.command)
    }

    @Test
    fun tracksTheSameAcceptedCommandUntilItCompletes() {
        val transport = FakeReadOnlyQueryTransport()
        val controller = RobotStatusQueryController(
            transportFactory = { transport },
            requestId = { REQUEST_ID },
            requestedAt = { "2026-09-25T15:34:00Z" },
        )
        val command = Command(
            commandId = COMMAND_ID,
            createdAt = "2026-09-25T15:34:00Z",
            intent = "SPRAY",
            targetId = "plot-02",
        )
        var update: OperationStatusUpdate? = null

        controller.track(command) { update = it }
        assertEquals(COMMAND_ID, transport.lastQuery?.commandId)

        transport.respond(operationResponse(RobotOperationState.EXECUTING))

        assertEquals(InteractionState.EXECUTING, update?.result?.state)
        assertFalse(checkNotNull(update).terminal)
        assertNull(update?.result?.command)

        controller.track(command) { update = it }
        transport.respond(operationResponse(RobotOperationState.COMPLETED))

        assertEquals(InteractionState.COMPLETED, update?.result?.state)
        assertTrue(checkNotNull(update).terminal)
        assertTrue(checkNotNull(update).result.message.contains("concluída"))
    }

    @Test
    fun failsClosedForMismatchedOrUnavailableStatus() {
        val transport = FakeReadOnlyQueryTransport()
        val controller = RobotStatusQueryController(
            transportFactory = { transport },
            requestId = { REQUEST_ID },
            requestedAt = { "2026-09-25T15:34:00Z" },
        )
        val command = Command(COMMAND_ID, "2026-09-25T15:34:00Z", "UNDOCK")
        var update: OperationStatusUpdate? = null

        controller.track(command) { update = it }
        transport.respond(
            ReadOnlyQueryResponse(
                requestId = REQUEST_ID,
                kind = ROBOT_STATUS,
                status = ReadOnlyQueryStatus.UNAVAILABLE,
            )
        )

        assertEquals(InteractionState.OPERATION_FAILED, update?.result?.state)
        assertTrue(checkNotNull(update).terminal)
        assertTrue(checkNotNull(update).result.message.contains("Não envie outro comando"))
    }

    @Test
    fun trackingTimeoutFailsClosedWithoutAnotherReadOnlyRequest() {
        val transport = FakeReadOnlyQueryTransport()
        val controller = RobotStatusQueryController(transportFactory = { transport })
        val command = Command(COMMAND_ID, "2026-09-25T15:34:00Z", "UNDOCK")

        val update = controller.trackingTimedOut(command)

        assertTrue(update.terminal)
        assertEquals(InteractionState.OPERATION_FAILED, update.result.state)
        assertEquals(0, transport.sentCount)
    }

    private fun operationResponse(state: RobotOperationState) = ReadOnlyQueryResponse(
        requestId = REQUEST_ID,
        kind = ROBOT_STATUS,
        status = ReadOnlyQueryStatus.FOUND,
        operation = ReadOnlyRobotOperation(
            commandId = COMMAND_ID,
            intent = "SPRAY",
            targetId = "plot-02",
            state = state,
        ),
    )

    private class FakeReadOnlyQueryTransport : ReadOnlyQueryTransport {
        var lastQuery: ReadOnlyQuery? = null
        var sentCount = 0
        private var completion: ((ReadOnlyQueryResponse) -> Unit)? = null

        override fun send(query: ReadOnlyQuery, completion: (ReadOnlyQueryResponse) -> Unit) {
            sentCount++
            lastQuery = query
            this.completion = completion
        }

        fun respond(response: ReadOnlyQueryResponse) {
            checkNotNull(completion).invoke(response)
        }
    }

    private companion object {
        const val REQUEST_ID = "123e4567-e89b-12d3-a456-426614174000"
        const val COMMAND_ID = "123e4567-e89b-12d3-a456-426614174001"
    }
}
