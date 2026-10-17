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
            python.getModule("cryptography.hazmat.primitives.asymmetric.ed25519")
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
