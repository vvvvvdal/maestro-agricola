package br.org.agroturtles.maestro.domain

import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Test


class TargetResolverTest {
    @Test
    fun matchesSharedTargetResolutionCases() {
        val json = checkNotNull(javaClass.classLoader?.getResource("target_resolution_cases.json")).readText()
        val payload = JSONObject(json)
        val allowed = payload.getJSONArray("allowed_target_ids").let { values ->
            buildSet { repeat(values.length()) { add(values.getString(it)) } }
        }
        val resolver = TargetResolver(allowed)
        val cases = payload.getJSONArray("cases")
        repeat(cases.length()) { index ->
            val item = cases.getJSONObject(index)
            fun nullableString(key: String) = if (item.isNull(key)) null else item.getString(key)
            val visual = nullableString("visual_target_id")
            val result = resolver.resolve(visual, item.getString("transcript"))
            val id = item.getString("id")
            assertEquals(id, item.getString("expected_status"), result.status.name)
            assertEquals(id, nullableString("expected_target_id"), result.targetId)
            assertEquals(id, nullableString("expected_source"), result.source)
        }
    }
}
