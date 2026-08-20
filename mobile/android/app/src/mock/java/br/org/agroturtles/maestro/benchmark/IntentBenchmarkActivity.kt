package br.org.agroturtles.maestro.benchmark

import android.app.Activity
import android.os.Build
import android.os.Bundle
import android.os.SystemClock
import android.util.Log
import br.org.agroturtles.maestro.domain.LocalIntentClassifier
import java.security.MessageDigest
import kotlin.math.ceil
import kotlin.math.max
import org.json.JSONObject


class IntentBenchmarkActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        runCatching(::benchmark)
            .onSuccess { Log.i(TAG, it.toString()) }
            .onFailure { error ->
                Log.e(
                    TAG,
                    JSONObject()
                        .put("status", "FAIL")
                        .put("error", error.message ?: error.javaClass.simpleName)
                        .toString(),
                )
            }
        finish()
    }

    private fun benchmark(): JSONObject {
        val modelBytes = assets.open("intent_model.json").use { it.readBytes() }
        val fixture = assets.open("parity_cases.json").bufferedReader().use { reader ->
            JSONObject(reader.readText())
        }
        val classifier = LocalIntentClassifier.fromJson(
            modelBytes.toString(Charsets.UTF_8),
            fixture.getDouble("confidence_threshold"),
        )
        val tolerance = fixture.getDouble("confidence_tolerance")
        val cases = fixture.getJSONArray("cases")

        repeat(WARMUP_ITERATIONS) {
            repeat(cases.length()) { index ->
                classifier.classify(cases.getJSONObject(index).getString("text"))
            }
        }

        val runtime = Runtime.getRuntime()
        val heapBefore = usedHeap(runtime)
        var observedHeapPeak = heapBefore
        val timings = LongArray(cases.length() * ITERATIONS_PER_CASE)
        var timingIndex = 0

        repeat(ITERATIONS_PER_CASE) {
            repeat(cases.length()) { index ->
                val case = cases.getJSONObject(index)
                val startedAt = SystemClock.elapsedRealtimeNanos()
                val prediction = classifier.classify(case.getString("text"))
                timings[timingIndex++] = SystemClock.elapsedRealtimeNanos() - startedAt

                check(prediction.label == case.getString("expected_label")) {
                    "${case.getString("id")}: esperado ${case.getString("expected_label")}, " +
                        "obtido ${prediction.label}"
                }
                check(
                    kotlin.math.abs(
                        prediction.confidence - case.getDouble("expected_confidence")
                    ) <= tolerance
                ) { "${case.getString("id")}: confiança divergente" }
                observedHeapPeak = max(observedHeapPeak, usedHeap(runtime))
            }
        }

        val sorted = timings.sortedArray()
        val heapAfter = usedHeap(runtime)
        return JSONObject()
            .put("status", "PASS")
            .put("device", "${Build.MANUFACTURER} ${Build.MODEL}")
            .put("android_release", Build.VERSION.RELEASE)
            .put("android_api", Build.VERSION.SDK_INT)
            .put("abi", Build.SUPPORTED_ABIS.firstOrNull() ?: "unknown")
            .put("model_sha256", sha256(modelBytes))
            .put("cases", cases.length())
            .put("iterations_per_case", ITERATIONS_PER_CASE)
            .put("total_inferences", timings.size)
            .put("median_us", percentile(sorted, 0.50) / NANOS_PER_MICROSECOND)
            .put("p95_us", percentile(sorted, 0.95) / NANOS_PER_MICROSECOND)
            .put("max_us", sorted.last() / NANOS_PER_MICROSECOND)
            .put("heap_before_bytes", heapBefore)
            .put("heap_after_bytes", heapAfter)
            .put("heap_peak_observed_bytes", observedHeapPeak)
    }

    private fun usedHeap(runtime: Runtime): Long = runtime.totalMemory() - runtime.freeMemory()

    private fun percentile(sorted: LongArray, percentile: Double): Long {
        val index = (ceil(percentile * sorted.size).toInt() - 1).coerceIn(sorted.indices)
        return sorted[index]
    }

    private fun sha256(bytes: ByteArray): String = MessageDigest
        .getInstance("SHA-256")
        .digest(bytes)
        .joinToString("") { "%02x".format(it) }

    companion object {
        private const val TAG = "MaestroAIBenchmark"
        private const val WARMUP_ITERATIONS = 5
        private const val ITERATIONS_PER_CASE = 30
        private const val NANOS_PER_MICROSECOND = 1_000L
    }
}
