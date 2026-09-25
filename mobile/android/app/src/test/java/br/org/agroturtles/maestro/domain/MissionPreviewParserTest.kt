package br.org.agroturtles.maestro.domain

import java.time.Clock
import java.time.Instant
import java.time.ZoneOffset
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class MissionPreviewParserTest {
    private val parser = MissionPreviewParser(
        targetResolver = TargetResolver(setOf("plot-01", "plot-02", "plot-03")),
        clock = Clock.fixed(Instant.parse("2026-09-25T12:00:00Z"), ZoneOffset.UTC),
        planIdFactory = { "00000000-0000-4000-8000-000000000001" },
    )

    @Test
    fun parsesTheDocumentedFourStepMission() {
        val parsed = parser.parse(
            "Saia da doca, pulverize o plot 02, depois verifique quando foi a última pulverização no plot 03 e depois volte para a doca."
        )

        val plan = (parsed as MissionPreviewParseResult.Preview).plan
        assertEquals("00000000-0000-4000-8000-000000000001", plan.planId)
        assertEquals("2026-09-25T12:00:00Z", plan.createdAt)
        assertEquals(
            listOf(
                MissionStep("step-1", MissionStepIntent.UNDOCK),
                MissionStep("step-2", MissionStepIntent.SPRAY, "plot-02"),
                MissionStep("step-3", MissionStepIntent.PLOT_STATUS_QUERY, "plot-03"),
                MissionStep("step-4", MissionStepIntent.DOCK),
            ),
            plan.steps,
        )
    }

    @Test
    fun doesNotTreatAnAtomicRequestAsAMission() {
        assertEquals(
            MissionPreviewParseResult.NotApplicable,
            parser.parse("pulverize o plot 02"),
        )
    }

    @Test
    fun rejectsMissingAndUnknownTargets() {
        val missing = parser.parse("saia da doca, pulverize e volte para a doca")
        val unknown = parser.parse("saia da doca, pulverize o plot 99 e volte para a doca")

        assertTrue(missing is MissionPreviewParseResult.Rejected)
        assertTrue(unknown is MissionPreviewParseResult.Rejected)
    }

    @Test
    fun rejectsInvalidDockOrderAndUnknownStep() {
        val badOrder = parser.parse("volte para a doca, pulverize o plot 02")
        val unknown = parser.parse("saia da doca, cante uma música")

        assertTrue(badOrder is MissionPreviewParseResult.Rejected)
        assertTrue(unknown is MissionPreviewParseResult.Rejected)
        assertFalse(badOrder is MissionPreviewParseResult.Preview)
    }
}
