package br.org.agroturtles.maestro.platform

import android.content.ContentProvider
import android.content.ContentValues
import android.database.Cursor
import android.net.Uri
import android.os.ParcelFileDescriptor
import java.io.FileNotFoundException
import kotlin.concurrent.thread


/**
 * Entrega ao MockDeviceKit a fixture versionada sem criar uma cópia em disco.
 * O provider não é exportado e aceita somente leitura do marcador conhecido.
 */
class DatMockAssetProvider : ContentProvider() {
    override fun onCreate(): Boolean = true

    override fun getType(uri: Uri): String? = when (uri.lastPathSegment) {
        TARGET_ASSET -> "image/png"
        else -> null
    }

    override fun openFile(uri: Uri, mode: String): ParcelFileDescriptor {
        if (mode != "r" || uri.lastPathSegment != TARGET_ASSET) {
            throw FileNotFoundException("Fixture DAT indisponível")
        }
        val appContext = checkNotNull(context).applicationContext
        val pipe = ParcelFileDescriptor.createPipe()
        thread(name = "dat-mock-asset", isDaemon = true) {
            ParcelFileDescriptor.AutoCloseOutputStream(pipe[1]).use { output ->
                appContext.assets.open(TARGET_ASSET).use { input -> input.copyTo(output) }
            }
        }
        return pipe[0]
    }

    override fun query(
        uri: Uri,
        projection: Array<out String>?,
        selection: String?,
        selectionArgs: Array<out String>?,
        sortOrder: String?,
    ): Cursor? = null

    override fun insert(uri: Uri, values: ContentValues?): Uri? = null

    override fun delete(uri: Uri, selection: String?, selectionArgs: Array<out String>?): Int = 0

    override fun update(
        uri: Uri,
        values: ContentValues?,
        selection: String?,
        selectionArgs: Array<out String>?,
    ): Int = 0

    companion object {
        const val TARGET_ASSET = "plot-03.png"
    }
}
