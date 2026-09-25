package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Test

class OperationTrackingPolicyTest {
    @Test
    fun allowsDockMoreTimeThanOtherOperations() {
        assertEquals(120, operationStatusMaxPolls(command("DOCK")))
        assertEquals(60, operationStatusMaxPolls(command("SPRAY")))
        assertEquals(60, operationStatusMaxPolls(command("UNDOCK")))
    }

    private fun command(intent: String) = Command(
        commandId = "command-1",
        createdAt = "2026-09-25T15:34:00Z",
        intent = intent,
    )
}
