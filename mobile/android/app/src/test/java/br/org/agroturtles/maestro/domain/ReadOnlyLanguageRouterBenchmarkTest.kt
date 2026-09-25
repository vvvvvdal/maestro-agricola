package br.org.agroturtles.maestro.domain

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ReadOnlyLanguageRouterBenchmarkTest {
    private val router = ReadOnlyLanguageRouter()

    @Test
    fun matchesTheDevelopmentCorpus() {
        val cases = checkNotNull(javaClass.getResourceAsStream("/read-only-development.tsv"))
            .bufferedReader()
            .use { reader ->
                reader.readLines().drop(1).map { line ->
                    val fields = line.split('\t')
                    check(fields.size == 4) { "invalid corpus row: $line" }
                    BenchmarkCase(
                        id = fields[0],
                        text = fields[1],
                        expected = ReadOnlyLanguageRoute.valueOf(fields[2]),
                    )
                }
            }

        assertEquals(32, cases.size)
        assertEquals(
            mapOf(
                ReadOnlyLanguageRoute.PLOT_STATUS_QUERY to 8,
                ReadOnlyLanguageRoute.STATUS_QUERY to 8,
                ReadOnlyLanguageRoute.INSPECT_TARGET to 8,
                ReadOnlyLanguageRoute.NONE to 8,
            ),
            cases.groupingBy { it.expected }.eachCount(),
        )

        val mismatches = cases.filter { router.route(it.text) != it.expected }

        assertTrue(
            "unexpected local routes: ${mismatches.joinToString { it.id }}",
            mismatches.isEmpty(),
        )
    }

    private data class BenchmarkCase(
        val id: String,
        val text: String,
        val expected: ReadOnlyLanguageRoute,
    )
}
