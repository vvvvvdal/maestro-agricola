package br.org.agroturtles.maestro.platform

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import com.google.zxing.BarcodeFormat
import com.google.zxing.BinaryBitmap
import com.google.zxing.DecodeHintType
import com.google.zxing.NotFoundException
import com.google.zxing.RGBLuminanceSource
import com.google.zxing.common.HybridBinarizer
import com.google.zxing.multi.qrcode.QRCodeMultiReader
import com.meta.wearable.dat.camera.types.PhotoData
import kotlin.math.roundToInt


/** Decodifica somente QR em memória; não cria arquivo, cache ou log de mídia. */
class ZxingPhotoQrDecoder : QrValueDecoder<PhotoData> {
    override fun decode(input: PhotoData): List<DecodedQr> {
        val decoded = decodePhoto(input)
        var analysisBitmap = decoded.bitmap
        var ownsAnalysisBitmap = decoded.owned

        try {
            if (analysisBitmap.config == Bitmap.Config.HARDWARE) {
                analysisBitmap = analysisBitmap.copy(Bitmap.Config.ARGB_8888, false)
                    ?: throw TargetDetectionException("Não foi possível preparar a foto")
                ownsAnalysisBitmap = true
            }

            val largestDimension = maxOf(analysisBitmap.width, analysisBitmap.height)
            if (largestDimension > MAX_ANALYSIS_DIMENSION) {
                val scale = MAX_ANALYSIS_DIMENSION.toFloat() / largestDimension
                val scaled = Bitmap.createScaledBitmap(
                    analysisBitmap,
                    (analysisBitmap.width * scale).roundToInt().coerceAtLeast(1),
                    (analysisBitmap.height * scale).roundToInt().coerceAtLeast(1),
                    true,
                )
                if (ownsAnalysisBitmap && scaled !== analysisBitmap) analysisBitmap.recycle()
                analysisBitmap = scaled
                ownsAnalysisBitmap = true
            }

            return decodeWithRotations(analysisBitmap)
        } finally {
            if (ownsAnalysisBitmap && !analysisBitmap.isRecycled) analysisBitmap.recycle()
        }
    }

    private fun decodePhoto(photo: PhotoData): DecodedBitmap = when (photo) {
        is PhotoData.Bitmap -> DecodedBitmap(photo.bitmap, owned = false)
        is PhotoData.HEIC -> {
            val buffer = photo.data.duplicate().apply { rewind() }
            val bytes = ByteArray(buffer.remaining())
            buffer.get(bytes)
            val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
                ?: throw TargetDetectionException("Foto DAT inválida")
            DecodedBitmap(bitmap, owned = true)
        }
    }

    private fun decodeWithRotations(source: Bitmap): List<DecodedQr> {
        decodeBitmap(source)?.let { return it }

        for (degrees in ROTATIONS) {
            val matrix = android.graphics.Matrix().apply { postRotate(degrees.toFloat()) }
            val rotated = Bitmap.createBitmap(
                source,
                0,
                0,
                source.width,
                source.height,
                matrix,
                true,
            )
            try {
                decodeBitmap(rotated)?.let { return it }
            } finally {
                if (rotated !== source && !rotated.isRecycled) rotated.recycle()
            }
        }
        return emptyList()
    }

    private fun decodeBitmap(bitmap: Bitmap): List<DecodedQr>? {
        val pixels = IntArray(bitmap.width * bitmap.height)
        bitmap.getPixels(pixels, 0, bitmap.width, 0, 0, bitmap.width, bitmap.height)
        val binaryBitmap = BinaryBitmap(
            HybridBinarizer(RGBLuminanceSource(bitmap.width, bitmap.height, pixels))
        )

        val results = try {
            QRCodeMultiReader().decodeMultiple(binaryBitmap, HINTS)
        } catch (_: NotFoundException) {
            return null
        }

        return results.mapNotNull { result ->
            val points = result.resultPoints?.takeIf { it.isNotEmpty() } ?: return@mapNotNull null
            DecodedQr(
                value = result.text,
                centerX = points.map { it.x }.average().toFloat() / bitmap.width,
                centerY = points.map { it.y }.average().toFloat() / bitmap.height,
            )
        }.takeIf { it.isNotEmpty() }
    }

    private data class DecodedBitmap(
        val bitmap: Bitmap,
        val owned: Boolean,
    )

    companion object {
        private const val MAX_ANALYSIS_DIMENSION = 1_600
        private val ROTATIONS = intArrayOf(90, 180, 270)
        private val HINTS = mapOf(
            DecodeHintType.POSSIBLE_FORMATS to listOf(BarcodeFormat.QR_CODE),
            DecodeHintType.CHARACTER_SET to Charsets.UTF_8.name(),
            DecodeHintType.TRY_HARDER to true,
        )
    }
}
