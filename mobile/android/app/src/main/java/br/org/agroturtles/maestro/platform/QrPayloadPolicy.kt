package br.org.agroturtles.maestro.platform

import java.util.Locale
import org.json.JSONObject


class QrPayloadPolicy(
    private val allowedTargetIds: Set<String>,
) {
    fun resolve(decodedValues: List<String>): Result<String> {
        val candidates = decodedValues
            .mapNotNull(::canonicalTargetId)
            .distinct()

        return when {
            candidates.isEmpty() -> Result.failure(
                TargetDetectionException("Nenhum marcador reconhecido")
            )

            candidates.size > 1 -> Result.failure(
                TargetDetectionException("Mais de um alvo visível; operação cancelada")
            )

            candidates.single() !in allowedTargetIds -> Result.failure(
                TargetDetectionException("Marcador não cadastrado")
            )

            else -> Result.success(candidates.single())
        }
    }

    private fun canonicalTargetId(value: String): String? {
        val normalized = value.trim().lowercase(Locale.ROOT)
        if (normalized.isEmpty()) return null
        val match = Regex("^plot[-_ ]?(\\d{1,3})$").matchEntire(normalized)
            ?: return normalized
        return "plot-${match.groupValues[1].toInt().toString().padStart(2, '0')}"
    }

    companion object {
        fun fromTargetMapJson(targetMapJson: String): QrPayloadPolicy {
            val targets = JSONObject(targetMapJson).getJSONObject("targets")
            return QrPayloadPolicy(targets.keys().asSequence().toSet())
        }
    }
}


fun interface QrValueDecoder<Input> {
    fun decode(input: Input): List<DecodedQr>
}


data class DecodedQr(
    val value: String,
    val centerX: Float,
    val centerY: Float,
) {
    fun isCentral(fraction: Float = CENTRAL_FRACTION): Boolean {
        require(fraction > 0f && fraction <= 1f)
        val margin = (1f - fraction) / 2f
        return centerX in margin..(1f - margin) && centerY in margin..(1f - margin)
    }

    companion object {
        const val CENTRAL_FRACTION = 0.70f
    }
}


class QrTargetDetector<Input>(
    private val decoder: QrValueDecoder<Input>,
    private val payloadPolicy: QrPayloadPolicy,
) {
    fun detect(input: Input): Result<TargetObservation> = runCatching {
        decoder.decode(input)
    }.fold(
        onSuccess = { decodedValues ->
            payloadPolicy.resolve(
                decodedValues.filter { it.isCentral() }.map(DecodedQr::value)
            ).map(TargetObservation::now)
        },
        onFailure = { error ->
            Result.failure(
                if (error is TargetDetectionException) error
                else TargetDetectionException("Não foi possível ler o marcador")
            )
        },
    )
}


class TargetDetectionException(message: String) : IllegalStateException(message)
