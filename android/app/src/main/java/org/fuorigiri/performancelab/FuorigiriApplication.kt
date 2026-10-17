package org.fuorigiri.performancelab

import android.app.Application
import android.content.Context
import com.chaquo.python.Python
import com.chaquo.python.PyObject
import com.chaquo.python.android.AndroidPlatform
import java.io.File
import java.util.concurrent.Executors

class FuorigiriApplication : Application()

/** One Python application shared by the UI and the worker; no HTTP server. */
object Runtime {
    val lock = Any()
    val executor = Executors.newSingleThreadExecutor()
    private var instance: PyObject? = null
    fun get(context: Context): PyObject = synchronized(lock) {
        instance ?: run {
            if (!Python.isStarted()) Python.start(AndroidPlatform(context.applicationContext))
            val assets = File(context.filesDir, "bundled/branding").apply { mkdirs() }
            context.assets.open("branding/progetto-ciclismo.png").use { input ->
                File(assets, "progetto-ciclismo.png").outputStream().use { input.copyTo(it) }
            }
            Python.getInstance().getModule("cycling_test.mobile_runtime").callAttr(
                "MobileRuntime", File(context.filesDir, "archive").absolutePath,
                assets.parentFile!!.absolutePath, NativeSecrets(context.applicationContext)
            ).also { instance = it }
        }
    }
}
