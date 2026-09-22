package br.org.agroturtles.maestro.platform

import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class JevTestDiagnosticsTest {

    @Test
    fun datFlavorDoesNotExposeJevDiagnostics() {
        assertNull(JevTestDiagnostics.current())
        assertTrue(JevTestDiagnostics.scenarios().isEmpty())
    }
}
