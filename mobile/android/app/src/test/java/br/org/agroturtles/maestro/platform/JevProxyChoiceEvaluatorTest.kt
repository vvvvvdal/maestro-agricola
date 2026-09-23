package br.org.agroturtles.maestro.platform

import br.org.agroturtles.maestro.domain.JevErrorCode
import org.junit.Assert.assertEquals
import org.junit.Test

class JevProxyChoiceEvaluatorTest {

    @Test
    fun disabledEvaluatorFailsClosedWithoutARequest() {
        val evaluation = JevProxyChoiceEvaluator().evaluate("volte para a doca")

        assertEquals(JevErrorCode.TRANSPORT, evaluation.error?.code)
    }
}
