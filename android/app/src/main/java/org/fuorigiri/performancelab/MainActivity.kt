package org.fuorigiri.performancelab

import android.annotation.SuppressLint
import android.content.Intent
import android.content.pm.ActivityInfo
import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import android.util.Base64
import android.util.Log
import android.view.ViewGroup
import android.webkit.*
import android.widget.TextView
import android.widget.Toast
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.ProgressBar
import android.widget.ImageView
import android.widget.Button
import android.view.Gravity
import android.view.View
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.webkit.WebViewAssetLoader
import androidx.webkit.WebViewCompat
import androidx.webkit.WebViewFeature
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import org.json.JSONObject

class MainActivity : ComponentActivity() {
    private var chartPreviousOrientation: Int? = null
    private var chartPreviousBars: Int? = null
    private var chartPreviousBarsBehavior: Int? = null
    private fun chartLandscape(enabled: Boolean) {
        val controller = WindowInsetsControllerCompat(window, window.decorView)
        if (enabled) {
            if (chartPreviousOrientation == null) chartPreviousOrientation = requestedOrientation
            if (chartPreviousBars == null) {
                val insets = ViewCompat.getRootWindowInsets(window.decorView)
                chartPreviousBars = listOf(WindowInsetsCompat.Type.statusBars(),WindowInsetsCompat.Type.navigationBars()).filter { insets?.isVisible(it) != false }.fold(0) { mask, type -> mask or type }
                chartPreviousBarsBehavior = controller.systemBarsBehavior
            }
            controller.systemBarsBehavior = WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            controller.hide(WindowInsetsCompat.Type.systemBars())
            requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE
        } else {
            chartPreviousOrientation?.let { requestedOrientation = it }
            chartPreviousOrientation = null
            chartPreviousBars?.let { visible ->
                if (visible != 0) controller.show(visible)
                val hidden = WindowInsetsCompat.Type.systemBars() and visible.inv()
                if (hidden != 0) controller.hide(hidden)
            }
            chartPreviousBarsBehavior?.let { controller.systemBarsBehavior = it }
            chartPreviousBars = null;chartPreviousBarsBehavior = null
        }
    }
    private var googleSession: String? = null
    private val googleResolution = registerForActivityResult(ActivityResultContracts.StartIntentSenderForResult()) { result ->
        try {
            val data = result.data ?: error("Consenso annullato")
            completeGoogle(com.google.android.gms.auth.api.identity.Identity.getAuthorizationClient(this).getAuthorizationResultFromIntent(data).accessToken)
        } catch (_: Exception) { Toast.makeText(this,"Autorizzazione Google non completata",Toast.LENGTH_LONG).show() }
    }
    private fun completeGoogle(token: String?) {
        val state=googleSession ?: return
        if(token==null)return
        Runtime.executor.execute {
            try { synchronized(Runtime.lock) { Runtime.get(applicationContext).callAttr("google_authorized",state,token) } }
            catch (_: Exception) { runOnUiThread { Toast.makeText(this,"Collegamento Google non completato",Toast.LENGTH_LONG).show() } }
        }
    }
    override fun onNewIntent(intent: Intent) { super.onNewIntent(intent);setIntent(intent);handleOAuth(intent) }
    private fun handleOAuth(intent: Intent) {
        val uri=intent.data ?: return
        if(uri.scheme!="fuorigiri" || uri.host!="oauth" || uri.path!="/callback")return
        Runtime.executor.execute {
            try { synchronized(Runtime.lock) { Runtime.get(applicationContext).callAttr("finish_cloud_oauth",uri.toString()) } }
            catch (_: Exception) { runOnUiThread { Toast.makeText(this,"Sessione OAuth scaduta o non valida: riprovare",Toast.LENGTH_LONG).show() } }
        }
    }
    private lateinit var web: WebView
    private var pickerCallback: ValueCallback<Array<Uri>>? = null
    private var exportBytes: ByteArray? = null
    private val origin = "https://appassets.androidplatform.net"
    private val preferences by lazy { getSharedPreferences("preferences", MODE_PRIVATE) }
    private val picker = registerForActivityResult(ActivityResultContracts.OpenMultipleDocuments()) { uris ->
        pickerCallback?.onReceiveValue(if (uris.isEmpty()) null else uris.toTypedArray()); pickerCallback = null
    }
    private val exporter = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        val data = exportBytes; exportBytes = null
        if (result.resultCode == RESULT_OK && data != null) {
            val uri = result.data?.data
            Runtime.executor.execute {
                try {
                    check(uri != null)
                    contentResolver.openOutputStream(uri, "w")!!.use { it.write(data) }
                    runOnUiThread { Toast.makeText(this, "File esportato", Toast.LENGTH_SHORT).show() }
                } catch (_: Exception) { runOnUiThread { Toast.makeText(this, "Esportazione non riuscita: riprovare", Toast.LENGTH_LONG).show() } }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        requestedOrientation = ActivityInfo.SCREEN_ORIENTATION_UNSPECIFIED
        WindowInsetsControllerCompat(window, window.decorView).apply {
            isAppearanceLightStatusBars = true
            isAppearanceLightNavigationBars = true
        }
        showStatus("Fuorigiri Performance Lab\nPreparazione del motore locale…")
        Runtime.executor.execute {
            try {
                Runtime.get(applicationContext)
                runOnUiThread { showStatus("Fuorigiri Performance Lab\nApertura dell’interfaccia…");setupWebView();handleOAuth(intent) }
            } catch (error: Exception) {
                if (BuildConfig.DEBUG) Log.e("FuorigiriStartup", "Offline runtime initialization failed", error)
                runOnUiThread { showStatus("Avvio non riuscito. I dati locali sono conservati. Riavvia l’app; se il problema persiste, segnala il codice AVVIO-01.", failed = true) }
            }
        }
    }

    private fun showStatus(message: String, failed: Boolean = false) {
        val margin = (24 * resources.displayMetrics.density).toInt()
        val status = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL; gravity = Gravity.CENTER
            setPadding(margin, margin, margin, margin)
            setBackgroundColor(android.graphics.Color.rgb(246,248,251))
            addView(LinearLayout(this@MainActivity).apply {
                orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL
                addView(ImageView(this@MainActivity).apply {
                    setImageResource(R.drawable.fuorigiri)
                    importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
                }, LinearLayout.LayoutParams((40*resources.displayMetrics.density).toInt(),(40*resources.displayMetrics.density).toInt()).apply { marginEnd=(10*resources.displayMetrics.density).toInt() })
                addView(TextView(this@MainActivity).apply {
                    text="Fuorigiri\nPERFORMANCE LAB";textSize=20f
                    setTextColor(android.graphics.Color.rgb(27,48,72))
                })
            })
            if (!failed) addView(ProgressBar(this@MainActivity).apply {
                contentDescription = "Apertura in corso"
                importantForAccessibility = View.IMPORTANT_FOR_ACCESSIBILITY_NO
            })
            addView(TextView(this@MainActivity).apply {
                text = message.removePrefix("Fuorigiri Performance Lab\n"); textSize = 18f; gravity = Gravity.CENTER
                setTextColor(android.graphics.Color.rgb(27,48,72))
                setPadding(0, margin, 0, margin)
                accessibilityLiveRegion = View.ACCESSIBILITY_LIVE_REGION_POLITE
            })
            if (failed) addView(Button(this@MainActivity).apply {
                text = "Riprova"; minHeight = (48 * resources.displayMetrics.density).toInt()
                setOnClickListener { recreate() }
            })
        }
        setContentView(status)
        ViewCompat.setOnApplyWindowInsetsListener(status) { view, insets ->
            val bars = insets.getInsets(WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.displayCutout())
            view.setPadding(margin + bars.left, margin + bars.top, margin + bars.right, margin + bars.bottom)
            insets
        }
        ViewCompat.requestApplyInsets(status)
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        web = WebView(this)
        WebView.setWebContentsDebuggingEnabled(BuildConfig.DEBUG)
        web.settings.apply {
            javaScriptEnabled = true; domStorageEnabled = true
            allowFileAccess = false; allowContentAccess = true
            mixedContentMode = WebSettings.MIXED_CONTENT_NEVER_ALLOW
            setSupportMultipleWindows(false)
        }
        val loader = WebViewAssetLoader.Builder().addPathHandler("/", WebViewAssetLoader.AssetsPathHandler(this)).build()
        web.webViewClient = object : WebViewClient() {
            override fun onPageStarted(view: WebView, url: String, favicon: Bitmap?) {
                chartLandscape(false)
                super.onPageStarted(view, url, favicon)
            }
            override fun shouldInterceptRequest(view: WebView, request: WebResourceRequest): WebResourceResponse {
                if (request.url.scheme != "https" || request.url.host != "appassets.androidplatform.net") return blocked()
                return loader.shouldInterceptRequest(request.url) ?: blocked()
            }
            override fun shouldOverrideUrlLoading(view: WebView, request: WebResourceRequest): Boolean {
                if (request.url.toString().startsWith("$origin/")) return false
                if (request.isForMainFrame && request.url.scheme in listOf("https", "http")) {
                    startActivity(Intent(Intent.ACTION_VIEW, request.url))
                }
                return true
            }
        }
        web.webChromeClient = object : WebChromeClient() {
            override fun onShowFileChooser(view: WebView, callback: ValueCallback<Array<Uri>>, params: FileChooserParams): Boolean {
                pickerCallback?.onReceiveValue(null); pickerCallback = callback
                picker.launch(arrayOf("*/*")); return true
            }
            override fun onJsAlert(view: WebView, url: String, message: String, result: JsResult): Boolean {
                android.app.AlertDialog.Builder(this@MainActivity).setMessage(message).setPositiveButton("OK") { _, _ -> result.confirm() }.setOnCancelListener { result.cancel() }.show(); return true
            }
            override fun onJsConfirm(view: WebView, url: String, message: String, result: JsResult): Boolean {
                android.app.AlertDialog.Builder(this@MainActivity).setMessage(message).setPositiveButton("Conferma") { _, _ -> result.confirm() }.setNegativeButton("Annulla") { _, _ -> result.cancel() }.setOnCancelListener { result.cancel() }.show(); return true
            }
        }
        if (!WebViewFeature.isFeatureSupported(WebViewFeature.WEB_MESSAGE_LISTENER)) {
            setContentView(TextView(this).apply { text="Aggiorna Android System WebView per utilizzare Fuorigiri." }); return
        }
        WebViewCompat.addWebMessageListener(web, "FuorigiriNative", setOf(origin)) { _, message, sourceOrigin, isMainFrame, _ ->
            if (!isMainFrame || sourceOrigin.toString() != origin) return@addWebMessageListener
            val raw = message.data ?: return@addWebMessageListener
            if (raw.length > 110_000_000) return@addWebMessageListener
            val command = try { JSONObject(raw) } catch (_: Exception) { return@addWebMessageListener }
            val id = command.optString("id")
            when (command.optString("type")) {
                "chartOrientation" -> runOnUiThread { chartLandscape(command.optBoolean("landscape")) }
                "request" -> Runtime.executor.execute {
                    val response = try {
                        val result = synchronized(Runtime.lock) { Runtime.get(applicationContext).callAttr("request", command.getJSONObject("payload").toString()).toString() }
                        JSONObject().put("id", id).put("response", JSONObject(result))
                    } catch (_: Exception) { JSONObject().put("id", id).put("error", "Operazione non completata. I dati locali sono conservati.") }
                    runOnUiThread { if (!isFinishing) web.evaluateJavascript("window.fuorigiriNativeResponse(${response});", null) }
                }
                "export" -> {
                    if (exportBytes != null) { Toast.makeText(this,"Completa prima l’esportazione aperta",Toast.LENGTH_SHORT).show(); return@addWebMessageListener }
                    try {
                        val data=Base64.decode(command.getString("body"),Base64.DEFAULT)
                        require(data.size <= 80_000_000);exportBytes=data
                        val name=command.optString("name","fuorigiri-export").replace(Regex("[/\\\\\u0000-\u001f]"),"_").take(180)
                        exporter.launch(Intent(Intent.ACTION_CREATE_DOCUMENT).apply { addCategory(Intent.CATEGORY_OPENABLE); type=command.optString("mime","application/octet-stream").ifBlank {"application/octet-stream"}; putExtra(Intent.EXTRA_TITLE,name) })
                    } catch (_: Exception) { exportBytes=null;Toast.makeText(this,"Esportazione non riuscita",Toast.LENGTH_LONG).show() }
                }
                "oauth" -> {
                    val uri=Uri.parse(command.optString("url"))
                    if(uri.scheme=="https" && uri.host in listOf("www.dropbox.com","login.microsoftonline.com"))
                        startActivity(Intent(Intent.ACTION_VIEW,uri))
                }
                "googleAuth" -> {
                    googleSession=command.optString("session")
                    val scope=command.optString("scope")
                    if(scope in listOf("https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive")) {
                        val request=com.google.android.gms.auth.api.identity.AuthorizationRequest.builder()
                            .setRequestedScopes(listOf(com.google.android.gms.common.api.Scope(scope))).build()
                        com.google.android.gms.auth.api.identity.Identity.getAuthorizationClient(this).authorize(request)
                            .addOnSuccessListener { result ->
                                if(result.hasResolution())googleResolution.launch(androidx.activity.result.IntentSenderRequest.Builder(result.pendingIntent!!.intentSender).build())
                                else completeGoogle(result.accessToken)
                            }.addOnFailureListener { Toast.makeText(this,"Autorizzazione Google non completata",Toast.LENGTH_LONG).show() }
                    }
                }
                "background" -> {
                    val enabled=command.optBoolean("enabled")
                    preferences.edit().putBoolean("background",enabled).apply()
                    if(enabled)SyncWorker.schedule(this) else SyncWorker.cancel(this)
                }
            }
        }
        val container = FrameLayout(this).apply {
            addView(web, FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        }
        setContentView(container)
        ViewCompat.setOnApplyWindowInsetsListener(container) { view, insets ->
            val bars=insets.getInsets(WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.ime() or WindowInsetsCompat.Type.displayCutout())
            view.setPadding(bars.left,bars.top,bars.right,bars.bottom);insets
        }
        ViewCompat.requestApplyInsets(container)
        web.loadUrl("$origin/index.html")
        if(preferences.getBoolean("background",false))SyncWorker.schedule(this)
        onBackPressedDispatcher.addCallback(this, object: OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                web.evaluateJavascript("(()=>{if(typeof window.fuorigiriChartBack==='function'&&window.fuorigiriChartBack())return true;const dialogs=document.querySelectorAll('dialog[open]');const dialog=dialogs[dialogs.length-1];if(dialog){dialog.dispatchEvent(new Event('cancel',{bubbles:false,cancelable:true}));return true}const close=document.querySelector('.overlay .close, .overlay button[aria-label=\"Chiudi\"]');if(close){close.click();return true}return typeof window.fuorigiriBack==='function'?window.fuorigiriBack():false})()") { value -> if(value!="true")finish() }
            }
        })
    }
    private fun blocked() = WebResourceResponse("text/plain", "UTF-8", 403, "Blocked", emptyMap(), "Contenuto non disponibile".byteInputStream())
    override fun onDestroy() { chartLandscape(false);pickerCallback?.onReceiveValue(null);pickerCallback=null;if(::web.isInitialized) web.destroy();super.onDestroy() }
}
