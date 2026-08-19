package br.org.agroturtles.maestro.domain

import java.security.MessageDigest
import org.junit.Assert.assertEquals
import org.junit.Test
import org.json.JSONObject


class LocalIntentClassifierTest {
    private val modelBytes by lazy {
        checkNotNull(javaClass.classLoader?.getResource("intent_model.json"))
            .openStream()
            .use { it.readBytes() }
    }

    private val classifier by lazy {
        LocalIntentClassifier.fromJson(modelBytes.toString(Charsets.UTF_8))
    }

    @Test
    fun classifiesCoreIntents() {
        assertEquals("SPRAY", classifier.classify("pulverize esse talhão").label)
        assertEquals("CONFIRM", classifier.classify("sim pode continuar").label)
        assertEquals("CANCEL", classifier.classify("não envie esse comando").label)
        assertEquals("UNKNOWN", classifier.classify("qual a cotação do dólar").label)
    }

    @Test
    fun matchesSharedParityFixture() {
        val json = checkNotNull(javaClass.classLoader?.getResource("parity_cases.json"))
            .readText()
        val payload = JSONObject(json)
        assertEquals("1.0", payload.getString("schema_version"))
        assertEquals(payload.getString("model_sha256"), sha256(modelBytes))

        val threshold = payload.getDouble("confidence_threshold")
        val tolerance = payload.getDouble("confidence_tolerance")
        val cases = payload.getJSONArray("cases")
        val parityClassifier = LocalIntentClassifier.fromJson(
            modelBytes.toString(Charsets.UTF_8),
            threshold,
        )

        repeat(cases.length()) { index ->
            val case = cases.getJSONObject(index)
            val prediction = parityClassifier.classify(case.getString("text"))
            val id = case.getString("id")
            assertEquals(id, case.getString("expected_label"), prediction.label)
            assertEquals(
                id,
                case.getDouble("expected_confidence"),
                prediction.confidence,
                tolerance,
            )
        }
    }

    private fun sha256(bytes: ByteArray): String = MessageDigest
        .getInstance("SHA-256")
        .digest(bytes)
        .joinToString("") { "%02x".format(it) }
}
