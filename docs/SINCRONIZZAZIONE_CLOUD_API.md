# Sincronizzazione con API cloud — verifica e disegno

## Stato 0.7 - aggiornamento che supera le note implementative precedenti

Adapter diretti Drive/Dropbox/OneDrive ora implementati insieme a WebDAV, UI OAuth e predisposizione per relay dedicato. Android: flussi nativi nei sorgenti, build ancora rimandata. Test automatici dei contratti disponibili; nessun account reale collegato. [Istruzioni operative, permessi e verifiche ancora necessarie](CLOUD_CONFIGURAZIONE_07.md). La ricerca e gli stati 0.4-0.6 sotto sono mantenuti come cronologia: non descrivono il perimetro del codice 0.7.

## Chiarimento CLOUD-03 — quattro trasporti richiesti anche su Android

18 ottobre 2026: WebDAV, Google Drive, Dropbox e OneDrive sono requisiti della versione Android; OneDrive passa da candidato a requisito. È necessario l’accesso diretto dal programma, distinto dall’uso dei client cartella su PC. Il codice 0.6 offre cartella/WebDAV; le tre API proprietarie non sono implementate. Le qualifiche storiche “OneDrive candidato” sotto sono superate come priorità di prodotto, non come stato di sviluppo. Build Linux/Android rimangono rimandate.

## Aggiornamento implementativo 0.6 — WebDAV presente, verifica reale aperta

Il trasporto cartella è stato estratto e WebDAV HTTPS è ora nel codice desktop e riusato dal backend Android. Configurazione nella società, portachiavi, oggetti immutabili, retry/rilettura, accessi firmati versionati e rotazione del canale: [contratto e limiti effettivi](CONSOLIDAMENTO_DISTRIBUZIONE_06.md). Test con server fixture passati; Nextcloud/account reali/Fedora/Android non ancora collaudati. Android ha sorgenti della shell/bridge, non APK disponibile. Le API Drive/Dropbox e i relativi spike con due account rimangono aperti; non compaiono come connessioni funzionanti. La ricerca sottostante conserva le decisioni e non equivale a implementazione di quei provider.

Verifica documentale del **17 ottobre 2026**, architettura 1.2; software invariato 0.4.1. Esaminate le API ufficiali, senza collegare account, creare progetti OAuth o effettuare prove autenticate. Le capacità documentate sono distinte dalle verifiche di interoperabilità ancora necessarie.

## Risultato

**È possibile scambiare direttamente i pacchetti di Fuorigiri tramite API cloud**, su desktop e Android, mantenendo database e allegati operativi offline. Non serve necessariamente un server Fuorigiri né il client di sincronizzazione del provider. L’accesso a una cartella scelta, però, non ha lo stesso modello di autorizzazione su tutti i servizi.

**CLOUD-02, conferma successiva dell’utente:** WebDAV è un requisito per Windows, Fedora e Android, non più un candidato. Mantenere il trasporto cartella locale; proporre WebDAV come primo adapter remoto dopo l’astrazione del trasporto, con spike Drive indipendente e successiva integrazione Drive/Dropbox. OneDrive rimane candidato. Nessun adapter remoto è ancora implementato. Android avrà come obiettivo lo scambio diretto via API, con import/export manuale e SAF come alternative, non come unico percorso ordinario. Il supporto WebDAV multipiattaforma è confermato; l’ordine dei lavori sui provider è una raccomandazione, non un’integrazione già implementata.

## Google Drive

Drive API v3 permette creazione, elenco, lettura e aggiornamento di file/cartelle. Per il consenso minimo Google raccomanda **`drive.file`**, che dà accesso ai file creati dall’app o esplicitamente aperti/concessi all’app, anche tramite Picker. È un permesso **per file**, non uno scope genericamente equivalente a «tutto il contenuto di questa cartella». La condivisione Drive fra utenti e l’autorizzazione OAuth dell’app sono livelli distinti. [Scope ufficiali](https://developers.google.com/workspace/drive/api/guides/api-specific-auth).

Flusso proposto: il fondatore collega Google, crea/seleziona una cartella dedicata, Fuorigiri conserva il suo ID e pubblica pacchetti cifrati; i collaboratori, con il proprio account, devono avere accesso alla cartella e autorizzare l’app. La condivisione può inizialmente essere gestita nell’interfaccia Drive, senza chiedere a Fuorigiri di amministrarla. Il [Picker per app desktop/mobile](https://developers.google.com/workspace/drive/picker/guides/desktop-mobile-picker) permette la selezione tramite browser di sistema e callback; il suo flusso documentato ammette solo `drive.file`. Non presumere che selezionare una cartella autorizzi automaticamente tutti i file presenti e futuri.

**Verifica bloccante per dichiarare supportata la collaborazione:** due account distinti, client desktop e Android dello stesso progetto OAuth, file creati dall’app di entrambi gli utenti, pacchetti già presenti creati dal client di sincronizzazione e nuovi file aggiunti esternamente. Per ciascuno provare elenco e download con il solo `drive.file`, anche dopo nuova installazione/revoca/riautorizzazione. Non basta riuscire a caricare un file o a leggere la cartella. Questa ricerca non dimostra il comportamento ricorsivo o inter-account del caso completo.

Se il perimetro minimo non copre il caso richiesto: valutare una migrazione esplicita dei pacchetti autorizzati, un flusso diverso di selezione, oppure scope più ampio con consenso e requisiti di verifica pertinenti. Non ampliare silenziosamente i permessi e non presentare un filtro applicativo sulla cartella come isolamento imposto da Google. Lo scope completo `drive` è classificato restricted nella documentazione; la distribuzione pubblica deve seguire il percorso di verifica applicabile.

Non usare **`appDataFolder`** per il canale della società: è un’area specifica dell’app e non consente condivisione dei contenuti. Può eventualmente ospitare impostazioni personali, non l’archivio collaborativo. [Vincoli ufficiali](https://developers.google.com/workspace/drive/api/guides/appdata).

Implementazione dell’adapter: `files.list` con parent ID e `trashed=false`, paginazione completa, download binario e upload; memorizzare ID remoti, non affidarsi all’unicità dei nomi. `changes.getStartPageToken`/`changes.list` consentono aggiornamenti incrementali, da filtrare sul canale autorizzato. Upload idempotenti con ID pre-generati persistiti nell’outbox quando applicabile, verifica dell’esito dopo timeout, hash del payload e deduplicazione per ID evento. [Ricerca file](https://developers.google.com/workspace/drive/api/guides/search-files), [cambiamenti](https://developers.google.com/workspace/drive/api/guides/manage-changes), [ID pre-generati](https://developers.google.com/workspace/drive/api/guides/create-file).

OAuth desktop: browser esterno e client di tipo Desktop con callback loopback, PKCE secondo il flusso supportato. Android: client Android e API native di autorizzazione, non riuso della callback loopback desktop. `AuthorizationClient.authorize()` gestisce l’ottenimento di un access token anche nelle sessioni successive, richiedendo interazione se necessaria. Il mancato rinnovo sospende solo lo scambio, non l’accesso offline. Non introdurre un backend soltanto per custodire un secret incorporato nell’APK. [OAuth desktop/mobile](https://developers.google.com/identity/protocols/oauth2/resources/loopback-migration), [autorizzazione Android](https://developer.android.com/identity/authorization).

## Dropbox

Il modello distingue **App Folder**, limitata alla directory privata dell’app, e **Full Dropbox**, che consente operazioni sull’account secondo gli scope concessi. Non esiste, in questo modello standard, un consenso Full Dropbox che diventi una restrizione OAuth alla sola cartella scelta dalla nostra UI. [Guida sviluppatori](https://www.dropbox.com/developers/reference/developer-guide).

App Folder è utile per i dispositivi dello **stesso account**, ma è incompatibile con cartelle condivise: non è la soluzione per collaboratori con account personali diversi. Per una cartella condivisa serve il modello Full Dropbox; Fuorigiri limiterà le proprie operazioni al relativo ID/namespace, dichiarando però il perimetro reale del consenso. [Vincoli delle cartelle condivise](https://help.dropbox.com/share/shared-folder-faq), [endpoint di condivisione](https://docs.dropboxapi.com/dropbox-api/api-reference/user-endpoints/sharing/share-folder).

Scope indicativi: `files.metadata.read`, `files.content.read` e, per chi pubblica, `files.content.write`. Richiedere scope di sharing soltanto se si decide di amministrare la condivisione dall’app; in prima iterazione la cartella può essere condivisa tramite Dropbox. Controllare scope effettivi sugli endpoint usati e namespace dei team; non confondere ruoli Dropbox con ruoli Fuorigiri. OAuth Authorization Code + PKCE e refresh token per lo scambio senza interazione continuativa sono documentati per client desktop/mobile pubblici. [Guida OAuth](https://developers.dropbox.com/oauth-guide).

Trasporto: `files/list_folder`, paginazione e cursor con `list_folder/continue`, download/upload di pacchetti, controllo `rev` per aggiornamenti del controllo firmato, gestione conflitti senza sovrascrittura automatica. Se il cursor non è più valido, ripetere l’inventario e deduplicare gli eventi. Long polling è possibile quando l’app è attiva; per il background Android restano i vincoli del sistema. [Rilevamento modifiche](https://docs.dropboxapi.com/dropbox-api/docs/detecting-changes).

## OneDrive e Nextcloud/WebDAV

**OneDrive / Microsoft Graph:** esiste `Files.ReadWrite.AppFolder`, con accesso a `special/approot`, utile come spazio specifico dell’app. Per accesso selettivo a file/cartelle esistono anche i permessi Selected: richiedono consenso e assegnazione esplicita sulla risorsa. La reference indica consenso amministratore per `Files.SelectedOperations.Selected`; non è un semplice selettore universale per qualunque account personale. Prima dell’adapter distinguere OneDrive personale e Microsoft 365/SharePoint e validare gli account effettivamente usati dalla società. [App folder](https://learn.microsoft.com/en-us/graph/onedrive-sharepoint-appfolder), [Selected permissions](https://learn.microsoft.com/en-us/graph/permissions-selected-overview), [reference dei permessi](https://learn.microsoft.com/en-us/graph/permissions-reference).

**Nextcloud/WebDAV:** API di elenco/lettura/scrittura tramite `PROPFIND`, `GET`, `PUT` e operazioni WebDAV. Preferire login per app/app password revocabile, con connessione TLS. Una password per app non va automaticamente presentata come autorizzazione a una singola cartella: verificare permessi server, account e condivisione. È un’alternativa interoperabile se si dispone già di un servizio Nextcloud, gestito o proprio; non impone di installare un server Fuorigiri. [API ufficiali](https://docs.nextcloud.com/server/stable/developer_manual/client_apis/WebDAV/basic.html), [autenticazione per client](https://docs.nextcloud.com/server/latest/user_manual/en/files/access_webdav.html).

## Contratto di trasporto comune

Separare `SyncEngine` (firme, revisioni, conflitti e applicazione locale) da `Transport` (inventario, lettura, pubblicazione, controllo e credenziali). Interfaccia obiettivo:

| Operazione | Semantica |
|---|---|
| `connect` / `check_access` | Autorizzazione interattiva iniziale e verifica dell’accesso al canale |
| `list_packets(cursor)` | Paginazione, ID remoti opachi, cursor e riconciliazione dopo reset |
| `download(remote_id)` | Copia in staging, verifica integrità, decifratura/firma prima dell’applicazione |
| `publish_once(event_id, payload)` | Outbox durevole, gestione esito incerto e duplicati; niente overwrite di eventi |
| `get_control` / `publish_control(expected_version)` | Directory accessi/revoche firmate, prevenzione rollback e conflitti |
| `disconnect` | Rimuove credenziali di trasporto locali; non elimina l’archivio o revoca automaticamente un ruolo |

Configurazione per società: provider, account collegato, root ID/namespace, identificatore canale, schema trasporto e stato locale. Token e sessioni non vanno in SQLite esportato, inviti, backup dati, file condivisi, log o repository: usare portachiavi desktop/Android Keystore tramite adapter. Client ID e configurazione pubblica sono distinti dai token privati; prevedere configurazioni proprie per build indipendenti open source. Su Drive verificare anche gli effetti di progetti OAuth diversi sulla visibilità per-app.

Ogni dispositivo legge/scrive prima localmente; una coda pubblica modifiche firmate e cifrate quando può. Conservare la cifratura attuale sopra TLS e le verifiche applicative indipendenti dal provider. Nomi remoti opachi e pochi metadati; il cloud vede comunque dimensioni, frequenza e account autorizzati. Nessun caricamento diretto del database aperto.

Non assumere transazioni distribuite, nomi univoci, ordine delle notifiche o exactly-once. I controlli firmati mutabili richiedono confronto della versione e del contenuto: ETag/rev se disponibile, altrimenti pubblicazioni di controllo versionate e riconciliazione deterministica da specificare prima del codice. Un semplice ultimo upload vince non è accettabile per revoche/accessi. Preservare payload e formato esistenti ove possibile; un’eventuale nuova disposizione remota richiede versione e migrazione esplicita.

Lo stesso canale non va gestito contemporaneamente via API e client cartella fino a un collaudo dedicato: pacchetti caricati esternamente, file temporanei e permessi per-app possono differire. Passaggio di trasporto guidato con inventario, conteggi e hash verificati, mantenendo lo stesso archivio/identità; niente nuova società creata per errore.

## Esperienza utente e responsabilità

UI-19: in «Condivisione e collaboratori» scegliere **Cartella locale**, **Google Drive** o **Dropbox** solo quando l’adapter è realmente disponibile. Poi «Collega account», «Crea/seleziona cartella», controllo accessi e «Sincronizza ora». Mostrare account, società, destinazione remota, permessi effettivi, ultimo successo, coda, problemi di autorizzazione e conflitti. Le opzioni pianificate non devono comparire come funzionanti.

Il login cloud abilita il trasporto, **non attribuisce il ruolo admin** e non sostituisce l’invito cifrato della società. Per accedere servono entrambe le autorizzazioni: quella cloud alla cartella e quella Fuorigiri ai dati/azioni. All’uscita di un collaboratore considerare separatamente revoca del certificato, rimozione della condivisione cloud e, quando disponibile, rotazione chiavi; nessuna rimozione può cancellare copie già scaricate.

## Ordine di lavoro e accettazione — TD-58

1. Refactoring del trasporto cartella esistente dietro contratto comune, con test di regressione e senza modificare i risultati dei test sportivi.
2. **WebDAV desktop e Android, supporto richiesto:** contratto comune, configurazione URL/cartella e autenticazione protetta, inventario paginato dove applicabile, pubblicazione/ripresa, gestione dei controlli firmati e collaudo su un server di riferimento (Nextcloud proposto). Un adapter HTTP condiviso non sostituisce i test sulle tre piattaforme. Provider WebDAV non collaudati vanno indicati come tali.
3. Progetto/app OAuth di sviluppo e spike **Drive con due account**, tutte le combinazioni descritte sopra e ripresa offline. Nessun obbligo di account di servizio, secret centrale o server intermediario. Registrazione pubblica, consenso/verifica, quote e politiche del provider da valutare per il rilascio effettivo, senza promettere assenza di costi futuri.
4. Adapter Drive desktop, gestione credenziali/riconnessione, migrazione dal canale locale, poi riuso del protocollo su Android con autorizzazione nativa. Se l’esperimento non soddisfa i permessi minimi, registrare la scelta alternativa e il consenso necessario prima del rilascio.
5. Adapter Dropbox con test Full Dropbox/cartella condivisa e comunicazione corretta dei permessi; OneDrive rimane candidato. WebDAV è incluso nel perimetro confermato per desktop/mobile (TD-59), anche se nessun cloud proprietario venisse collegato.
6. Collaudo: Windows/Fedora/Android, account distinti, nuovi dispositivi, viewer/admin, doppio upload, timeout dopo commit remoto, paginazione, cursor resettato, quota/rate limit con backoff, perdita di rete/processo, token revocato, perdita di condivisione, pacchetto alterato, conflitto dati e controllo accessi concorrente. Salvataggio offline sempre disponibile; un errore OAuth non deve bloccare l’archivio.

Questo lavoro rientra nel consolidamento della sincronizzazione **INC-11 / TD-50** e in **AND-04**; la verifica Drive può iniziare sul desktop prima della fase Android. Il requisito non sposta lo sviluppo Android dopo Sprint/Wingate e non dichiara nessun provider API già implementato. Per prove reali serviranno account di collaudo e registrazioni OAuth dedicati; questa revisione contiene soltanto ricerca e disegno.
