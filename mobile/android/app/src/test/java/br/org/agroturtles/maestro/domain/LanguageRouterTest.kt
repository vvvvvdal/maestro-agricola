package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class LanguageRouterTest {

    @Test
    fun operationalIntentNeverGoesToAssistant() {
        val router = LanguageRouter(
            IntentClassifier {
                IntentPrediction(
                    label = "DOCK",
                    confidence = 0.99,
                    source = "MODEL",
                )
            }
        )

        val result = router.route("voltar para a base")

        assertEquals(LanguageRouteType.OPERATIONAL, result.type)
        assertEquals("DOCK", result.prediction.label)
        assertNull(result.assistantText)
    }

    @Test
    fun unknownIntentGoesToAssistant() {
        val router = LanguageRouter(
            IntentClassifier {
                IntentPrediction(
                    label = "UNKNOWN",
                    confidence = 1.0,
                    source = "MODEL",
                )
            }
        )

        val result = router.route(
            "como funciona o Maestro Agrícola?"
        )

        assertEquals(LanguageRouteType.ASSISTANT, result.type)
        assertEquals(
            "como funciona o Maestro Agrícola?",
            result.assistantText,
        )
    }

    @Test
    fun cancelNeverGoesToAssistant() {
        val router = LanguageRouter(
            IntentClassifier {
                IntentPrediction(
                    label = "CANCEL",
                    confidence = 1.0,
                    source = "RULE",
                )
            }
        )

        val result = router.route("cancela isso")

        assertEquals(LanguageRouteType.OPERATIONAL, result.type)
        assertNull(result.assistantText)
    }
}
