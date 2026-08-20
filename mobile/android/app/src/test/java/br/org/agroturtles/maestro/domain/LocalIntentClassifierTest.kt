package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Test
import org.json.JSONObject


class LocalIntentClassifierTest {
    private val classifier by lazy {
        val json = checkNotNull(javaClass.classLoader?.getResource("intent_model.json"))
            .readText()
        LocalIntentClassifier.fromJson(json)
    }

    @Test
    fun classifiesCoreIntents() {
        assertEquals("SPRAY", classifier.classify("pulverize esse talhão").label)
        assertEquals("CONFIRM", classifier.classify("sim pode continuar").label)
        assertEquals("CANCEL", classifier.classify("não envie esse comando").label)
        assertEquals("UNKNOWN", classifier.classify("qual a cotação do dólar").label)
        assertEquals("UNKNOWN", classifier.classify("sim mas espere").label)
        assertEquals("UNKNOWN", classifier.classify("o produto foi pulverizado ontem").label)
        assertEquals("CANCEL", classifier.classify("deixa quieto").label)
        assertEquals("CONFIRM", classifier.classify("isso mesmo").label)
        assertEquals("RULE", classifier.classify("não pulverize o talhão").source)
    }

    @Test
    fun matchesSharedParityFixture() {
        val json = checkNotNull(javaClass.classLoader?.getResource("parity_cases.json"))
            .readText()
        val payload = JSONObject(json)
        val tolerance = payload.getDouble("confidence_tolerance")
        val cases = payload.getJSONArray("cases")

        repeat(cases.length()) { index ->
            val case = cases.getJSONObject(index)
            val prediction = classifier.classify(case.getString("text"))
            val id = case.getString("id")
            assertEquals(id, case.getString("expected_label"), prediction.label)
            assertEquals(id, case.getString("expected_source"), prediction.source)
            assertEquals(
                id,
                case.getDouble("expected_confidence"),
                prediction.confidence,
                tolerance,
            )
        }
    }
}
