package br.org.agroturtles.maestro.domain

import java.time.Clock
import java.time.Instant
import java.time.ZoneOffset
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class MissionExecutionControllerTest {
    private val controller = MissionExecutionController(
        targetResolver = TargetResolver(setOf("plot-01", "plot-02", "plot-03")),
        clock = Clock.fixed(Instant.parse("2026-09-25T12:00:00Z"), ZoneOffset.UTC),
        commandIdFactory = { "123e4567-e89b-12d3-a456-426614174000" },
    )

    @Test
    fun emitsOneConfirmedCommandThenStopsForTheReadOnlyStep() {
        val first = controller.begin(plan())
        assertEquals(MissionStepIntent.UNDOCK, (first as MissionExecutionAction.AwaitingConfirmation).step.intent)

        val send = controller.confirm(IntentPrediction("CONFIRM", 1.0, "RULE"))
        val command = (send as MissionExecutionAction.SendCommand).command
        assertEquals("UNDOCK", command.intent)
        assertEquals("123e4567-e89b-12d3-a456-426614174000", command.commandId)

        val spray = controller.operationFinished(succeeded = true, reason = "completed")
        assertEquals(MissionStepIntent.SPRAY, (spray as MissionExecutionAction.AwaitingConfirmation).step.intent)
        controller.confirm(IntentPrediction("CONFIRM", 1.0, "RULE"))

        val query = controller.operationFinished(succeeded = true, reason = "completed")
        assertEquals(MissionStepIntent.PLOT_STATUS_QUERY, (query as MissionExecutionAction.ExecuteQuery).step.intent)
    }

    @Test
    fun queryDoesNotAuthorizeTheFollowingPhysicalStep() {
        controller.begin(planStartingWithQuery())
        assertEquals(MissionExecutionState.AWAITING_QUERY, controller.current()?.state)

        val next = controller.queryFinished(succeeded = true, reason = "found")

        assertEquals(MissionStepIntent.DOCK, (next as MissionExecutionAction.AwaitingConfirmation).step.intent)
        assertEquals(MissionExecutionState.AWAITING_CONFIRMATION, controller.current()?.state)
    }

    @Test
    fun rejectionFailureAndTimeoutPauseWithoutAdvancing() {
        controller.begin(plan())
        controller.confirm(IntentPrediction("CONFIRM", 1.0, "RULE"))
        val rejected = controller.commandRejected("bridge unavailable")
        assertTrue(rejected is MissionExecutionAction.Paused)
        assertEquals(0, controller.current()?.currentStepIndex)

        controller.begin(plan())
        val timedOut = controller.confirmationTimedOut()
        assertTrue(timedOut is MissionExecutionAction.Paused)
        assertEquals(MissionExecutionState.PAUSED, controller.current()?.state)
    }

    @Test
    fun invalidTargetAndCancellationNeverCreateACommand() {
        val invalid = plan().copy(steps = plan().steps.mapIndexed { index, step ->
            if (index == 1) step.copy(targetId = "plot-99") else step
        })
        assertTrue(controller.begin(invalid) is MissionExecutionAction.Paused)

        controller.begin(plan())
        assertTrue(controller.confirm(IntentPrediction("CANCEL", 1.0, "RULE")) is MissionExecutionAction.Cancelled)
        assertEquals(MissionExecutionState.CANCELLED, controller.current()?.state)
    }

    private fun plan() = MissionPlan(
        planId = "00000000-0000-4000-8000-000000000001",
        createdAt = "2026-09-25T12:00:00Z",
        steps = listOf(
            MissionStep("step-1", MissionStepIntent.UNDOCK),
            MissionStep("step-2", MissionStepIntent.SPRAY, "plot-02"),
            MissionStep("step-3", MissionStepIntent.PLOT_STATUS_QUERY, "plot-03"),
            MissionStep("step-4", MissionStepIntent.DOCK),
        ),
    )

    private fun planStartingWithQuery() = MissionPlan(
        planId = "00000000-0000-4000-8000-000000000002",
        createdAt = "2026-09-25T12:00:00Z",
        steps = listOf(
            MissionStep("step-1", MissionStepIntent.PLOT_STATUS_QUERY, "plot-03"),
            MissionStep("step-2", MissionStepIntent.DOCK),
        ),
    )
}
