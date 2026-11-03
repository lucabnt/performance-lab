package org.fuorigiri.performancelab

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import com.chaquo.python.Python

@RunWith(AndroidJUnit4::class)
class OfflineRuntimeTest {
    @Test fun pillowImagesFontsAndPdf() {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        Runtime.get(instrumentation.targetContext)
        val source = instrumentation.context.assets.open("check_android_pillow_runtime.py")
            .bufferedReader().use { it.readText() }
        synchronized(Runtime.lock) {
            val builtins = Python.getInstance().getModule("builtins")
            val scope = builtins.callAttr("dict")
            builtins.callAttr("exec", source, scope)
            val result = scope.callAttr("__getitem__", "check").call(
                instrumentation.targetContext.cacheDir.absolutePath,
                File(instrumentation.targetContext.filesDir, "bundled/branding/progetto-ciclismo.png").absolutePath
            )
            android.util.Log.i("PillowRuntimeCheck", "device_api=${android.os.Build.VERSION.SDK_INT} result=$result")
            assertTrue(result.toString().contains("passed"))
            val pdf = File(result.callAttr("__getitem__", "pdf_path").toString())
            android.os.ParcelFileDescriptor.open(pdf, android.os.ParcelFileDescriptor.MODE_READ_ONLY).use { descriptor ->
                android.graphics.pdf.PdfRenderer(descriptor).use { renderer ->
                    assertEquals(1, renderer.pageCount)
                    renderer.openPage(0).use { page ->
                        val bitmap = android.graphics.Bitmap.createBitmap(595, 842, android.graphics.Bitmap.Config.ARGB_8888)
                        page.render(bitmap, null, null, android.graphics.pdf.PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY)
                        bitmap.recycle()
                    }
                }
            }
        }
    }

    @Test fun nativeImportsPrivateArchiveAndKeystore() {
        val context=InstrumentationRegistry.getInstrumentation().targetContext
        Runtime.get(context)
        synchronized(Runtime.lock) {
            val python=Python.getInstance()
            // Exercise actual native imports, not just the existence of files.
            python.getModule("numpy")
            python.getModule("matplotlib.figure")
            python.getModule("reportlab.platypus")
            python.getModule("pydantic_core")
            python.getModule("_cffi_backend")
            python.getModule("cryptography.hazmat.primitives.asymmetric.ed25519")
            val builtins = python.getModule("builtins")
            builtins.callAttr("exec", """
                from cryptography.fernet import Fernet
                from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
                payload = b'fuorigiri-android-native-check'
                cipher = Fernet(Fernet.generate_key())
                assert cipher.decrypt(cipher.encrypt(payload)) == payload
                signing = Ed25519PrivateKey.generate()
                signing.public_key().verify(signing.sign(payload), payload)
            """.trimIndent(), builtins.callAttr("dict"))
            val path=File(context.cacheDir,"instrumented-${System.nanoTime()}").absolutePath
            val runtime=python.getModule("cycling_test.mobile_runtime").callAttr("MobileRuntime",path)
            val response=JSONObject(runtime.callAttr("request",JSONObject().put("path","/api/v1/state").put("method","GET").toString()).toString())
            assertEquals(200,response.getInt("status"))
            val secrets=NativeSecrets(context)
            secrets.put("instrumentation","synthetic-test-credential")
            assertEquals("synthetic-test-credential",secrets.get("instrumentation"))
        }
    }
}
