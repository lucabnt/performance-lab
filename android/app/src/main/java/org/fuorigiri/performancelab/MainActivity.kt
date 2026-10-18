package org.fuorigiri.performancelab

import android.annotation.SuppressLint
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.util.Base64
import android.view.ViewGroup
import android.webkit.*
import android.widget.TextView
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.activity.result.contract.ActivityResultContracts
import androidx.webkit.WebViewAssetLoader
import androidx.webkit.WebViewCompat
import androidx.webkit.WebViewFeature
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import org.json.JSONObject

class MainActivity : ComponentActivity() {
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
        setContentView(TextView(this).apply { text = "Fuorigiri Performance Lab\nAvvio dell’archivio offline…"; setPadding(32, 64, 32, 32) })
        Runtime.executor.execute {
            try {
                Runtime.get(applicationContext)
                runOnUiThread { setupWebView();handleOAuth(intent) }
            } catch (_: Exception) {
                runOnUiThread { setContentView(TextView(this).apply { text = "Avvio non riuscito. L’archivio è conservato. Questa build richiede la verifica delle dipendenze native Android."; setPadding(32,64,32,32) }) }
            }
        }
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
        setContentView(web, ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT))
        ViewCompat.setOnApplyWindowInsetsListener(web) { view, insets ->
            val bars=insets.getInsets(WindowInsetsCompat.Type.systemBars() or WindowInsetsCompat.Type.ime())
            view.setPadding(bars.left,bars.top,bars.right,bars.bottom);insets
        }
        web.loadUrl("$origin/index.html")
        if(preferences.getBoolean("background",false))SyncWorker.schedule(this)
        onBackPressedDispatcher.addCallback(this, object: OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                web.evaluateJavascript("(()=>{const close=document.querySelector('.overlay .close, .overlay button[aria-label=\"Chiudi\"]');if(close){close.click();return true}return false})()") { value -> if(value!="true")finish() }
            }
        })
    }
    private fun blocked() = WebResourceResponse("text/plain", "UTF-8", 403, "Blocked", emptyMap(), "Contenuto non disponibile".byteInputStream())
    override fun onDestroy() { pickerCallback?.onReceiveValue(null);pickerCallback=null;if(::web.isInitialized) web.destroy();super.onDestroy() }
}
