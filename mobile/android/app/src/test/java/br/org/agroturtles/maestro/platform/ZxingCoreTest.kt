package br.org.agroturtles.maestro.platform

import com.google.zxing.BarcodeFormat
import com.google.zxing.BinaryBitmap
import com.google.zxing.RGBLuminanceSource
import com.google.zxing.common.HybridBinarizer
import com.google.zxing.multi.qrcode.QRCodeMultiReader
import com.google.zxing.qrcode.QRCodeWriter
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test


class ZxingCoreTest {
    @Test
    fun plotMarkerRoundTripsEntirelyInMemory() {
        val matrix = QRCodeWriter().encode("plot-03", BarcodeFormat.QR_CODE, SIZE, SIZE)
        val pixels = IntArray(SIZE * SIZE) { index ->
            val x = index % SIZE
            val y = index / SIZE
            if (matrix[x, y]) BLACK else WHITE
        }
        val bitmap = BinaryBitmap(
            HybridBinarizer(RGBLuminanceSource(SIZE, SIZE, pixels))
        )

        val result = QRCodeMultiReader().decodeMultiple(bitmap).single()
        val centerX = result.resultPoints.map { it.x }.average().toFloat() / SIZE
        val centerY = result.resultPoints.map { it.y }.average().toFloat() / SIZE

        assertEquals("plot-03", result.text)
        assertTrue(DecodedQr(result.text, centerX, centerY).isCentral())
    }

    companion object {
        private const val SIZE = 320
        private const val BLACK = -0x1000000
        private const val WHITE = -0x1
    }
}
