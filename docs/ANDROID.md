# Android — requisito e architettura proposta

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
