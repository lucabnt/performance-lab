# Android — requisito e architettura proposta

## Valutazione dell'implementazione ibrida — 18 ottobre 2026

L'implementazione attuale contiene già Kotlin: `MainActivity.kt` gestisce WebView, import/export e autorizzazioni; `NativeSecrets.kt` protegge le credenziali; `SyncWorker.kt` usa WorkManager; `FuorigiriApplication.kt` inizializza il runtime Python tramite Chaquopy. React/TypeScript fornisce l'interfaccia condivisa, Python il motore e i servizi locali. Il bridge chiama FastAPI in-process mediante ASGITransport: nessun server HTTP in ascolto sul telefono. Le vecchie sezioni che proponevano Capacitor descrivono l'alternativa iniziale, non il contenitore effettivamente scritto.

Incorporare Python non è di per sé una pratica scorretta: è esattamente lo scopo di [Chaquopy](https://chaquo.com/chaquopy/). È una scelta di riuso che evita una seconda implementazione delle formule e dei formati di scambio. La parte nativa resta necessaria per integrare correttamente servizi, credenziali, file e autorizzazioni; Kotlin è la scelta adottata, senza sostenere che sia l'unico linguaggio tecnicamente possibile.

Il costo reale è un'app con runtime Python, WebView e bridge, dipendenze scientifiche/crypto native e compatibilità ABI da verificare. Non equivale a un'app tutta Kotlin/Compose: avvio, memoria, dimensione APK, accessibilità/touch, ciclo di vita, prestazioni del bridge e sincronizzazione in background richiedono misure. WorkManager segue i [vincoli del sistema Android](https://developer.android.com/topic/architecture/data-layer/offline-first), non assicura intervalli esatti. La versione condivisa del motore include ora l'interpolazione lattato v2, ma non è stata collaudata su Android.

Il controllo locale `scripts/build_android.py --check` segnala wheel verificate per pydantic_core e cryptography mancanti su arm64/x86_64, SDK 35/build-tools, JDK e Gradle assenti/non configurati. Il controllo è necessario ma non sufficiente: in build andranno verificate anche le versioni bloccate di NumPy, Matplotlib e ReportLab rispetto a Python 3.13 e alle ABI. Nessun APK è stato compilato o provato. Il rinvio concordato delle build resta valido.

Prima di confermare definitivamente questa architettura: produrre una build debug, verificare in modalità aereo FIT → analisi → PDF, misurare avvio/memoria/dimensioni e collaudare sincronizzazione, riavvio, sospensione e recupero del processo su dispositivo fisico. Se i costi risultano eccessivi, valutare adapter più sottili o UI nativa con lo stesso motore, mediante decisione documentata; nessuna riscrittura automatica è avviata da questa osservazione.


## Sorgenti 0.8 — protocolli e schede condivise

Catalogo, flussi manuale/file e campi opzionali tipizzati sono condivisi con la UI React e l’API Python. Nessun modulo di calcolo custom viene eseguito sul telefono: le osservazioni conservano schema, unità e snapshot come sul desktop. I contratti sono verificati su PC; la nuova UI non è stata collaudata su dispositivo Android. Build APK ancora rimandata secondo la consegna concordata.

## Sorgenti 0.7 - quattro provider diretti

WebDAV e adapter API Drive/Dropbox/OneDrive riusati dal backend in-process. Dropbox/OneDrive: consenso nel browser di sistema, deep link fuorigiri://oauth/callback e stato PKCE monouso. Drive: AuthorizationClient Google Play services (dipendenza play-services-auth), consenso nativo e rinnovo silenzioso quando già autorizzato; eventuale consenso aggiuntivo richiede primo piano. Token nel Keystore, WorkManager esteso ai trasporti remoti. Manifest con deep link, listener limitato all’origine interna e apertura esterna limitata ai provider previsti. [Registrazioni e limiti](CLOUD_CONFIGURAZIONE_07.md).

Questi sono sorgenti: nessuna build APK né verifica del nuovo codice Kotlin/Google Play services su dispositivo è stata eseguita. Il rinvio della toolchain Linux/Android rimane valido. Non sono inclusi client ID registrati o certificati di firma. Per la sincronizzazione Google occorrono package/SHA registrati e Play services; gli altri provider restano alternative su dispositivi senza questi servizi.

**Chiarimento CLOUD-03, 18 ottobre 2026:** la versione Android deve poter sincronizzare direttamente tramite WebDAV, Google Drive, Dropbox e OneDrive. Tutti e quattro sono ora requisiti; OneDrive non è più soltanto candidato. La 0.6 contiene il trasporto WebDAV condiviso, non gli adapter delle tre API proprietarie né un APK collaudato. Questo chiarimento non riattiva le build rimandate. Prevale sulle indicazioni storiche sottostanti; vedere [TD-67](REQUISITI_E_TODO.md).

**Consegna concordata il 18 ottobre 2026:** Windows e sorgenti; l’utente ha rimandato le build Linux/Android. I gate e i collaudi sotto restano documentati, senza avviare CI o pubblicazioni.

## Stato 0.6 — sorgente della shell e contratto, APK ancora da costruire

18 ottobre 2026. **AND-01/02 avviati, TD-57 aperto.** Implementati `android/` (Kotlin/WebView) e `backend/cycling_test/mobile_runtime.py`: stessa API FastAPI eseguita tramite ASGI in-process, senza server HTTP né socket sul telefono. Il frontend React usa un adapter fetch per i messaggi nativi; grafici e viste condivisi, layout compatto, import tramite picker SAF, export PDF/MD/CSV/backup tramite creazione documento, ruoli e revisioni condivisi. Password WebDAV cifrate con chiave AES-GCM in Android Keystore; lavoro periodico WorkManager facoltativo, con rete/batteria e retry, più Sincronizza ora. Backup automatico Android disabilitato per non duplicare silenziosamente identità/chiavi.

**MOB-02, revisione della shell:** uso diretto di WebViewAssetLoader + WebMessageListener ristretto all’origine locale e al frame principale, anziché introdurre Capacitor per questo primo porting. Mantiene React/Python, riduce le dipendenze del bridge e non riscrive le formule. Qt e uvicorn non sono dipendenze Android. La UI non carica codice remoto nel contesto con accesso nativo; i link esterni aprono il browser, le richieste WebView fuori dagli asset vengono bloccate. L’API locale sul bridge assegna internamente il token e filtra path/header, mantenendo le autorizzazioni applicative.

**Prerequisito verificato, non aggirato:** nel repository ufficiale Chaquopy manca Pydantic Core e la wheel Cryptography cp313 disponibile è 42.0.8. Il progetto richiede wheel aggiornate `pydantic_core 2.41.4` e `cryptography 50.0.2`, entrambe le ABI, prima della build. NumPy 1.26.2 / Matplotlib 3.8.4 hanno wheel cp313 disponibili; equivalenza numerica e compatibilità di tutte le librerie native, incluse pagine 16 KB, sono da verificare su Android. Nessuna wheel Linux può essere rinominata come Android. Chaquopy raccomanda [cibuildwheel su Linux/macOS per Python 3.13+](https://github.com/chaquo/chaquopy/blob/master/server/pypi/README.md); questo ambiente Windows non ha SDK Android, JDK completo, Gradle o Linux/WSL disponibili. Il controllo riproducibile restituisce esattamente questi prerequisiti mancanti.

```sh
python scripts/build_android.py --check
# Su builder con le wheel revisionate + SHA256.json, SDK 35, JDK e Gradle 8.13:
python scripts/build_android.py
# Release non firmata, firma del titolare separata:
python scripts/build_android.py --release
```

La pipeline `.github/workflows/android-build.yml` riceve un artefatto `android-native-wheels` da un run revisionato e produce un APK debug candidato. Non è stata eseguita; non equivale a una pipeline già verde o a un APK disponibile. Le wheel aggiornate richiedono prima un builder POSIX e toolchain native; vedere [gate delle wheel](../android/wheels/README.md). MinSdk scelto 26 (Android 8), target/compile SDK 35, Python 3.13, Chaquopy 17.1, ARM64 + x86_64. È un target iniziale da collaudare; distribuzione su Play Store e requisiti correnti dello store sono un’attività distinta.

**Prove eseguite qui:** quattro test del bridge su Windows, inclusi creazione/riapertura dell’archivio, test manuale, report PDF/Markdown/CSV/backup, upload multipart FIT e rifiuto delle scritture di un visualizzatore. Chiamano il backend reale; non usano risposte fittizie. Aggiunto un test strumentale Android per import delle librerie native, archivio privato e Keystore, ancora da eseguire. Import/report/GUI/modalità aereo/WorkManager e scambio con desktop su dispositivo fisico rimangono criteri necessari. **Non esiste ancora un APK installabile collaudato di questa revisione.**

Limite iniziale bridge: 80 MB per richiesta/risposta, messaggi base64 e memoria da misurare su telefono. File grandi/spazio esaurito, gestione completa dei gesti/tastiera/lettore schermo, grafici su telefono/tablet e cambio processo durante un export richiedono prove. Non introdurre localStorage come archivio: viene usato soltanto per la preferenza del lavoro in background, mentre dati/oggetti restano in SQLite/area privata.

La proposta sotto conserva la cronologia di disegno; il suo testo “non implementato” descrive il punto di partenza e non annulla il codice della 0.6. Il completamento richiede ancora tutti i criteri AND-01–05.

17 ottobre 2026. **TD-57: sviluppo richiesto, non implementato.** Stesso prodotto Fuorigiri Performance Lab e GPL-3.0-or-later, logo e attribuzione fissi. Telefono e tablet, offline first, accessi personali per società e dati interoperabili con Windows/Fedora. Nessun APK viene dichiarato disponibile in questa revisione.

## Posizione nel piano

Preparare contratti e isolamento delle dipendenze durante il completamento dell’incrementale desktop. Eseguire poi una verifica tecnica Android; sviluppare e collaudare l’app **dopo la copertura incrementale e il consolidamento di migrazioni/sync/accessi desktop, prima di Sprint breve, Wingate 30 s e Wingate 15 s**. I nuovi motori saranno così progettati per entrambi gli ambienti. La ricerca di fattibilità non blocca il lavoro sui metodi dell’incrementale. iOS resta fuori dalla richiesta attuale.

## Scelta raccomandata e alternative

Proposta **React/TypeScript + Capacitor per la shell Android**, bridge Kotlin per servizi della piattaforma e **riuso del nucleo Python tramite Chaquopy**, senza server HTTP sul telefono. Il codice React può essere riutilizzato, ma richiede viste responsive e un adapter applicativo: desktop usa FastAPI, mobile chiama metodi del bridge con lo stesso contratto di comandi/risultati. Separare motore scientifico puro, repository e rendering dal framework prima del porting. Non incorporare Qt, uvicorn o un PC sempre acceso nella soluzione mobile.

[Capacitor](https://capacitorjs.com/docs) offre il contenitore web e l’accesso nativo; [Chaquopy](https://chaquo.com/chaquopy/doc/current/index.html) incorpora Python in Android. **La loro integrazione in questo progetto è una proposta da provare**, non una compatibilità già verificata: dipendenze native, PDF, FIT e crittografia vanno costruiti e testati sulle ABI supportate. Non fissare ora versioni Android/SDK sulla base delle dipendenze desktop; scegliere minSdk/targetSdk e versioni bloccate al momento dello spike. Verificare licenze di runtime, plugin e wheel e aggiornare THIRD_PARTY.

| Alternativa | Vantaggio | Costo / limite |
|---|---|---|
| Capacitor + Python incorporato, raccomandata | UI e un solo motore di calcolo condivisi | Bridge e distribuzione dei pacchetti Android da verificare |
| Capacitor + motore TypeScript riscritto | Nessun runtime Python sul telefono | Due implementazioni scientifiche da mantenere; equivalenza obbligatoria su vettori di test |
| Kotlin/Compose + Python | Integrazione nativa completa | Seconda UI e minore riuso dell’investimento React |
| PWA o frontend collegato al PC | Prototipo di consultazione rapido | Non soddisfa da solo import, calcoli e archivio autonomi offline |

Se lo spike Python fallisce, registrare un ADR con misure e scegliere l’alternativa; non convertire silenziosamente Android in visualizzatore dipendente dal desktop.

## Archivio, sicurezza e sincronizzazione

SQLite e allegati nell’area privata dell’app, migrazioni transazionali e cache separata dai dati persistenti. Il database locale è la fonte operativa anche senza rete: è il modello della [guida Android offline first](https://developer.android.com/topic/architecture/data-layer/offline-first). Non sincronizzare il file SQLite aperto, non collocarlo in Drive e non usare localStorage come archivio atleti. Conservare gli stessi ID, revisioni, firme, hash, conflitti e regole di ruolo della suite; ogni installazione ha la propria identità dispositivo. Valutare cifratura a riposo e backup del sistema coerenti con il recupero delle chiavi.

Credenziali protette tramite Android Keystore e bridge dedicato; il formato crittografico portabile resta lo stesso, con test di interoperabilità. Chiavi legate al dispositivo non sono esportabili come tali: il recupero cifrato della società deve restare distinto dal backup dei dati. Viewer e admin mantengono le stesse autorizzazioni; nessun account Google diventa automaticamente admin della società.

**Drive/Dropbox su Android non garantiscono una cartella locale equivalente a quella desktop.** Il [Storage Access Framework](https://developer.android.com/training/data-storage/shared/documents-files) restituisce URI e accessi tramite provider; supporto a directory, disponibilità offline e permessi persistenti vanno verificati per provider. Non convertire una `content://` URI in un percorso filesystem e non richiedere accesso indiscriminato a tutti i file.

Introdurre un’interfaccia di trasporto dei pacchetti cifrati: elenco, lettura, pubblicazione con integrità, ripresa e deduplicazione. **Aggiornamento CLOUD-01:** lo scambio diretto tramite API Drive/Dropbox e WebDAV è l’obiettivo ordinario anche su Android; selettore documenti, SAF e import/export sono alternative. Desktop mantiene anche l’adapter cartella. La [verifica delle API cloud](SINCRONIZZAZIONE_CLOUD_API.md) precisa OAuth, limiti dei permessi per cartella, collaborazione con account distinti e prove necessarie: CLOUD-02/TD-59 conferma WebDAV anche su Android e ne propone l’implementazione come primo adapter remoto; Drive richiede uno spike con il solo `drive.file`. Nessun server Fuorigiri obbligatorio. I limiti dei provider sull’atomicità richiedono staging, verifica hash e gestione di file parziali; nessuna integrazione API è già implementata.

L’aggiornamento in background sarà affidato a WorkManager con vincoli di rete/batteria, retry e comandi idempotenti; non promettere sincronizzazione immediata o periodi esatti. Esporre sempre «Sincronizza ora», ultima sincronizzazione riuscita, coda locale, errori e conflitti. [Documentazione WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager).

## UI, import e report

UI-18: navigazione adattata a telefono/tablet, priorità atleta → test → storico; sidebar desktop trasformata in navigazione compatta; tabelle con riepilogo e dettaglio, grafici touch con zoom/reset e selezione temporale accessibile, unità e nomi leggibili condivisi. Formulari usabili con tastiera aperta, anteprima degli allegati prima dell’import, stato offline e ruolo sempre comprensibili. Branding della società fondatrice fisso anche nel footer dei report, senza personalizzazione.

Import FIT/ERG/CSV da picker o «Apri con»; copiare l’originale nell’archivio con hash prima di analizzarlo. Calcoli, anteprima e produzione MD/PDF devono funzionare in modalità aereo. Il renderer PDF Python attuale va verificato: se non portabile, adapter Android con medesimo modello di report, senza duplicare le formule. Esportazioni tramite selettore/condivisione del sistema e file temporanei eliminabili; niente dipendenza dalla directory Download desktop.

## Criteri di accettazione e sottoattività

1. **AND-01, fattibilità:** prova installabile con UI React, chiamata al motore Python, decodifica FIT sintetico, firma/cifratura interoperabile e PDF offline; misurare avvio, dimensioni e memoria. CI e dispositivo fisico, non solo emulatore. Verifica delle librerie native e dei requisiti correnti del sistema prima di scegliere la distribuzione.
2. **AND-02, contratti:** separare adapter desktop/mobile, schemi di scambio e preset versionati; equivalenza dei risultati numerici su tutti i vettori della specifica incrementale, con tolleranze dichiarate.
3. **AND-03, nucleo offline:** società/invito, atleti/gruppi, misure, protocolli, import e revisione dei test, grafici, storico, MD/PDF/CSV, consultazione e modifica secondo ruolo anche dopo riavvio in modalità aereo.
4. **AND-04, scambio:** due dispositivi più desktop con account personali distinti, API del provider esplicitamente supportato, import/export alternativo, retry/duplicati, modifiche concorrenti, revoche e recupero. CLOUD-01/TD-58 definiscono adapter e spike Drive; CLOUD-02/TD-59 richiede anche WebDAV con collaudo desktop/mobile; la sola esportazione manuale non chiude il requisito cloud.
5. **AND-05, qualità e distribuzione:** migrazioni, interruzione del processo, spazio esaurito, grandi tracce, accessibilità/touch, finestre adattive, firma APK e gestione sicura della chiave di rilascio. APK firmato e sorgenti/procedura riproducibile; pubblicazione su store eventuale, distinta dallo sviluppo richiesto.

Il completamento Android richiede tutti questi flussi. Un prototipo, una PWA o la sola visualizzazione dello storico non chiudono TD-57. Raccolta live Bluetooth/ANT+ e controllo del rullo sono possibili estensioni, non comprese automaticamente nell’analisi di file richiesta.
