# Configurare la sincronizzazione

Guida corrente ai trasporti. Per il formato e i limiti di spazio vedere [scalabilità](SYNC_DIMENSIONI_E_SCALABILITA.md); per account e ruoli vedere [società e accessi](SOCIETA_BACKUP_E_ACCESSI.md). Configurazione locale, account collegato e accesso alla destinazione verificato all’ultimo scambio sono stati distinti. Registrazioni OAuth e collaudi reali rimangono necessari.

Implementati adapter WebDAV, Google Drive API v3, Dropbox API v2, Microsoft Graph OneDrive e client di predisposizione a un relay dedicato. Lo stesso database SQLite resta locale; sul cloud transitano pacchetti cifrati e controlli firmati, non il database aperto. Una destinazione per società su ciascun dispositivo: scegliere lo stesso provider/cartella fra collaboratori. Non è implementato il mirroring automatico fra cloud differenti.

**Stato verificato:** test automatici con risposte API simulate e server WebDAV locale, UI desktop compilata. Nessun accesso ad account reali o registrazione OAuth creato in questa attività; disponibilità dei permessi e collaborazione con due account vanno collaudate sul provider. Android ha gli adapter condivisi e i flussi nativi nei sorgenti; compilazione APK e verifica su dispositivo restano rimandate, come Linux.

## Uso e registrazioni

Archivio e scambio → società selezionata → sincronizzazione. Il ruolo Fuorigiri deriva dall’invito personale e non dal provider. Ogni operatore accede al cloud con il proprio account, che deve poter leggere/scrivere la cartella. Un visualizzatore Fuorigiri può configurare il collegamento e ricevere dati, ma non pubblica modifiche ai dati.

La distribuzione open source non contiene registrazioni OAuth di altri né segreti universali. Il distributore registra l’app e configura client ID/app key; per ora l’interfaccia espone questi parametri avanzati. Non sono necessari Python o SDK cloud sul PC utente. Dalla configurazione usare **Collega account**, autorizzare nel browser di sistema, poi **Salva connessione e sincronizza**. Non usare un WebView per il login. Lo stato e lo scollegamento sono disponibili nello stesso pannello; lo scollegamento locale non sostituisce la revoca sul sito del provider.

### WebDAV

Cartella server già condivisa, URL finale HTTPS, utente e password applicazione. Portachiavi di sistema, nessun fallback in chiaro; niente redirect con credenziali. Supporto condiviso desktop/mobile già presente dalla 0.6.

### Google Drive

Abilitare Drive API nel progetto Google Cloud, configurare schermata consenso e utenti di test o pubblicazione secondo le regole Google. Desktop: client OAuth **Desktop app**, client ID e, quando richiesto dalla registrazione, client secret salvato nel portachiavi. Callback loopback `http://127.0.0.1:53682/oauth/callback`, PKCE S256, access_type offline; il listener esiste solo durante il consenso e scade dopo 5 minuti. Il segreto di una desktop app non è una credenziale di server confidenziale.

Inserire l’ID reale della cartella condivisa (parte della URL Drive). `drive.file` limita l’accesso ai file autorizzati all’app: **incollare l’ID di una cartella non concede automaticamente accesso ai file dei collaboratori**. Per la collaborazione su cartella esistente è disponibile la scelta esplicita dello scope Drive completo, con consenso più ampio e possibili requisiti di verifica Google. La UI lo espone; non viene ampliato silenziosamente. Picker e creazione automatica/cartelle condivise non sono implementati: creare e condividere sul sito del provider.

Android: registrare il package org.fuorigiri.performancelab e SHA del certificato; il client desktop non sostituisce la registrazione Android. Sorgenti con AuthorizationClient di Google Play services, consenso nativo e access token in Keystore. Il rinnovo silenzioso usa la stessa API; quando serve una nuova risoluzione l’app chiede di ricollegare in primo piano, senza un client secret desktop nel telefono. Sono richiesti Google Play services; build/dispositivi senza questi servizi potranno usare gli altri provider. Verificare la selezione dell’account previsto quando si usano più account Google sullo stesso telefono.

API: inventario paginato, parent ID, supporto shared drives, download media, creazione multipart con ID Google pregenerato e persistito per retry. Nomi con prefisso del canale. Drive ammette nomi duplicati: duplicati con contenuti autenticati diversi bloccano lo scambio; cifrature diverse dello stesso evento possono coesistere senza duplicare il record locale.

Fonti: [OAuth app native](https://developers.google.com/identity/protocols/oauth2/native-app), [scope Drive](https://developers.google.com/workspace/drive/api/guides/api-specific-auth), [upload e ID pregenerati](https://developers.google.com/workspace/drive/api/guides/manage-uploads), [autorizzazione Android](https://developer.android.com/identity/authorization).

### Dropbox

Registrare un’app **Scoped access / Full Dropbox** per usare una cartella condivisa fra persone. App Folder limita l’app alla propria cartella e non è la scelta prevista per lo scambio condiviso. Consentire almeno files.metadata.read, files.content.read e files.content.write. Inserire app key e percorso della cartella, es. /Fuorigiri, già esistente e accessibile all’account. Per spazi team, il percorso deve risultare risolvibile nel namespace dell’account: il selettore di namespace amministrativi non è incluso.

Redirect desktop `http://127.0.0.1:53682/oauth/callback`; Android `fuorigiri://oauth/callback`, da registrare nella console. Authorization code con PKCE S256 e token_access_type offline; nessun app secret obbligatorio nel client. Refresh token protetto, rinnovo e consenso revocato gestiti come errore recuperabile. Inventario paginato e caricamenti add/strict_conflict senza autorename, con rilettura.

[Guida OAuth Dropbox](https://www.dropbox.com/developers/reference/oauth-guide).

### Microsoft OneDrive

Registrare un’app pubblica Microsoft Entra con account personali/organizzativi necessari alla distribuzione. Registrare redirect desktop `http://127.0.0.1:53682/oauth/callback` e custom URI mobile `fuorigiri://oauth/callback` nella piattaforma appropriata. Scope delegated Files.ReadWrite.All e offline_access: sono permessi ampi, non accesso limitato magicamente a una cartella. Le policy del tenant possono richiedere amministratore o impedire il consenso.

Inserire ID reale della cartella e, se appartiene a un’altra raccolta o drive condiviso, ID drive effettivo del proprietario. Non usare come ID la URL di condivisione, un collegamento remoto o il testo `root`; il browser di scelta e la risoluzione automatica dei link condivisi non sono inclusi. Ogni account deve avere accesso alla destinazione sottostante. Inventario Graph paginato, creazione condizionale con conflictBehavior fail, rilettura; i download preautorizzati non ricevono il Bearer Graph. Redirect/paginazione verso host non previsti vengono rifiutati.

[OAuth code flow](https://learn.microsoft.com/en-us/entra/identity-platform/v2-oauth2-auth-code-flow), [upload Graph](https://learn.microsoft.com/en-us/graph/api/driveitem-put-content?view=graph-rest-1.0), [app folder e relativo perimetro](https://learn.microsoft.com/en-us/graph/onedrive-sharepoint-appfolder).

## Contratto del servizio dedicato

La UI include l’opzione avanzata **Servizio dedicato** e il backend ha un adapter utilizzabile da un futuro server compatibile. Non è stato creato o distribuito un server Fuorigiri. Configurare base URL HTTPS e token personale del servizio, protetto nel portachiavi; il token del relay non sostituisce inviti, firme o chiave del canale.

Base relativa `/v1/channels/{channel}/objects`:

| Operazione | Contratto |
|---|---|
| GET collezione | JSON `{ "schema": 1, "objects": ["nome.ctsync"] }`, inventario completo, massimo 100.000 nomi |
| GET /{nome} | Byte dell’oggetto cifrato, limite client 80 MB |
| PUT /{nome} | Bearer personale, If-None-Match: *, corpo opaco; 201/200/204 nuovo oggetto, 412 se già presente; mai sovrascrivere |

Il client rilegge e verifica il contenuto dopo PUT. Accetta cifrature diverse solo se il testo autenticato coincide con la chiave del canale; il motore verifica poi le firme degli eventi. Il server dovrà aggiungere account e ACL per canale, gestione/revoca credenziali, quote, limiti di richiesta, TLS, backup, monitoraggio e retention. Per grandi inventari progettare una versione paginata del contratto: non cambiare silenziosamente lo schema 1. Cursor/delta e push potranno ottimizzare il trasporto senza sostituire SQLite o il protocollo degli eventi.

## Sicurezza operativa e accettazione

Token e client secret: vault Windows / Secret Service Linux / Keystore Android, separati da archivio, inviti, esportazioni e backup dati. Dopo ripristino su altro dispositivo ricollegare gli account. Configurazione locale contiene solo destinazione e registrazione; le risposte API non espongono token. Stato OAuth monouso, PKCE, timeout, HTTPS, rinnovo dopo 401 e retry limitati. I callback scaduti o da un altro archivio non vengono accettati. Nessuna sostituzione distruttiva di oggetti remoti e nessuna cancellazione automatica della cartella.

Test riproducibili: `python -m pytest -q tests/test_cloud.py tests/test_sync_transports.py tests/test_mobile_runtime.py`. Comprendono paginazione, idempotenza dei contratti, PKCE/stato, rinnovo, separazione credenziali, ruolo viewer, download OneDrive senza Bearer e relay. Prima di qualificare un provider per l’uso quotidiano provare **due account distinti**, due dispositivi, creazione dati offline, allegati, stessa riga modificata contemporaneamente, revoca/401/403, quota/rete interrotta e ripresa. I test simulati non dimostrano i permessi inter-account di un tenant reale.
