package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test


class PlotStatusQueryControllerTest {
    @Test
    fun queriesCompletedSimulatedSprayWithoutCreatingCommand() {
        val transport = FakeReadOnlyQueryTransport()
        val controller = controller(transport)
        var completed: InteractionResult? = null

        val pending = controller.handle("qual foi a última pulverização no talhão dois?") {
            completed = it
        }

        assertEquals(InteractionState.QUERYING, pending?.state)
        assertEquals("PLOT_STATUS_QUERY", pending?.intent)
        assertEquals("plot-02", transport.lastQuery?.plotId)
        assertNull(pending?.command)

        transport.respond(
            ReadOnlyQueryResponse(
                requestId = checkNotNull(transport.lastQuery).requestId,
                kind = LAST_SIMULATED_SPRAY_FOR_PLOT,
                status = ReadOnlyQueryStatus.FOUND,
                record = ReadOnlyOperationRecord(
                    plotId = "plot-02",
                    completedAt = "2026-09-25T15:32:18Z",
                    origin = "GAZEBO_SIMULATOR",
                ),
            )
        )

        assertEquals(InteractionState.QUERY_COMPLETED, completed?.state)
        assertTrue(checkNotNull(completed).message.contains("no Gazebo"))
        assertNull(completed?.command)
    }

    @Test
    fun narratesMissingHistoryForKnownPlot() {
        val transport = FakeReadOnlyQueryTransport()
        val controller = controller(transport)
        var completed: InteractionResult? = null

        controller.handle("me diga o histórico de aplicação do plot 03") { completed = it }
        transport.respond(
            ReadOnlyQueryResponse(
                requestId = checkNotNull(transport.lastQuery).requestId,
                kind = LAST_SIMULATED_SPRAY_FOR_PLOT,
                status = ReadOnlyQueryStatus.NOT_FOUND,
            )
        )

        assertEquals(InteractionState.QUERY_COMPLETED, completed?.state)
        assertTrue(
            checkNotNull(completed).message.lowercase().contains("não há missão simulada")
        )
        assertNull(completed?.command)
    }

    @Test
    fun rejectsAmbiguousOrUnknownPlotLocallyWithoutCallingTransport() {
        val transport = FakeReadOnlyQueryTransport()
        val controller = controller(transport)

        val missingPlot = controller.handle("qual foi a última pulverização?") { error("unexpected") }
        val unknownPlot = controller.handle("qual foi a última aplicação no plot 99?") {
            error("unexpected")
        }

        assertEquals(InteractionState.QUERY_COMPLETED, missingPlot?.state)
        assertEquals(InteractionState.QUERY_COMPLETED, unknownPlot?.state)
        assertTrue(
            checkNotNull(missingPlot).message.lowercase().contains("não consegui identificar")
        )
        assertTrue(
            checkNotNull(unknownPlot).message.lowercase().contains("não consegui identificar")
        )
        assertNull(transport.lastQuery)
    }

    @Test
    fun leavesAStatementOfPastOperationForTheExistingUnknownPath() {
        val transport = FakeReadOnlyQueryTransport()
        val controller = controller(transport)

        val result = controller.handle("o produto foi pulverizado ontem") { error("unexpected") }

        assertNull(result)
        assertNull(transport.lastQuery)
    }

    @Test
    fun narratesUnavailableReadOnlyTransportWithoutCommand() {
        val transport = FakeReadOnlyQueryTransport()
        val controller = controller(transport)
        var completed: InteractionResult? = null

        controller.handle("quando foi a última aplicação no plot 01?") { completed = it }
        transport.respond(
            ReadOnlyQueryResponse(
                requestId = checkNotNull(transport.lastQuery).requestId,
                kind = LAST_SIMULATED_SPRAY_FOR_PLOT,
                status = ReadOnlyQueryStatus.UNAVAILABLE,
            )
        )

        assertEquals(InteractionState.QUERY_COMPLETED, completed?.state)
        assertEquals(
            "A consulta está indisponível. Nenhum comando foi enviado.",
            completed?.message,
        )
        assertFalse(checkNotNull(completed).state == InteractionState.SENDING)
        assertNull(completed?.command)
    }

    private fun controller(transport: FakeReadOnlyQueryTransport) = PlotStatusQueryController(
        targetResolver = TargetResolver(setOf("plot-01", "plot-02", "plot-03")),
        transportFactory = { transport },
        requestId = { "123e4567-e89b-12d3-a456-426614174000" },
        requestedAt = { "2026-09-25T15:34:00Z" },
    )

    private class FakeReadOnlyQueryTransport : ReadOnlyQueryTransport {
        var lastQuery: ReadOnlyQuery? = null
        private var completion: ((ReadOnlyQueryResponse) -> Unit)? = null

        override fun send(query: ReadOnlyQuery, completion: (ReadOnlyQueryResponse) -> Unit) {
            lastQuery = query
            this.completion = completion
        }

        fun respond(response: ReadOnlyQueryResponse) {
            checkNotNull(completion).invoke(response)
        }
    }
}
