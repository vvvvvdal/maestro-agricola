package br.org.agroturtles.maestro.platform

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test


class QrPayloadPolicyTest {
    private val policy = QrPayloadPolicy(setOf("plot-01", "plot-02", "plot-03"))

    @Test
    fun acceptsOneKnownTargetAndCanonicalizesItsId() {
        assertEquals("plot-03", policy.resolve(listOf(" PLOT 3 ")).getOrThrow())
    }

    @Test
    fun rejectsAnEmptyFrame() {
        val failure = policy.resolve(emptyList()).exceptionOrNull()

        assertTrue(failure is TargetDetectionException)
        assertEquals("Nenhum marcador reconhecido", failure?.message)
    }

    @Test
    fun rejectsAnUnknownTarget() {
        val failure = policy.resolve(listOf("plot-99")).exceptionOrNull()

        assertTrue(failure is TargetDetectionException)
        assertEquals("Marcador não cadastrado", failure?.message)
    }

    @Test
    fun rejectsDistinctTargetsButAllowsDuplicateReadsOfTheSameQr() {
        assertEquals(
            "plot-03",
            policy.resolve(listOf("plot-03", "PLOT_3")).getOrThrow(),
        )

        val failure = policy.resolve(listOf("plot-02", "plot-03")).exceptionOrNull()
        assertTrue(failure is TargetDetectionException)
        assertEquals("Mais de um alvo visível; operação cancelada", failure?.message)
    }

    @Test
    fun loadsAllowedTargetsFromTheCanonicalMap() {
        val policyFromJson = QrPayloadPolicy.fromTargetMapJson(
            """{"targets":{"plot-03":{"x":1.5,"y":1.0}}}"""
        )

        assertEquals("plot-03", policyFromJson.resolve(listOf("plot-03")).getOrThrow())
    }

    @Test
    fun detectorReturnsStructuredObservationForOneAllowedQr() {
        val detector = QrTargetDetector(
            decoder = QrValueDecoder<String> { listOf(DecodedQr(it, 0.5f, 0.5f)) },
            payloadPolicy = policy,
        )

        val observation = detector.detect("PLOT-03").getOrThrow()

        assertEquals("plot-03", observation.targetId)
        assertNotNull(observation.observedAt)
    }

    @Test
    fun detectorFailsClosedWhenImageDecoderThrows() {
        val detector = QrTargetDetector(
            decoder = QrValueDecoder<String> { error("imagem inválida") },
            payloadPolicy = policy,
        )

        val failure = detector.detect("bytes").exceptionOrNull()

        assertTrue(failure is TargetDetectionException)
        assertEquals("Não foi possível ler o marcador", failure?.message)
    }

    @Test
    fun detectorRejectsQrOutsideTheCentralRegion() {
        val detector = QrTargetDetector(
            decoder = QrValueDecoder<String> { listOf(DecodedQr(it, 0.02f, 0.5f)) },
            payloadPolicy = policy,
        )

        val failure = detector.detect("plot-03").exceptionOrNull()

        assertTrue(failure is TargetDetectionException)
        assertEquals("Nenhum marcador reconhecido", failure?.message)
    }
}
