package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Test


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
    }
}
