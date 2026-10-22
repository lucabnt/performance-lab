# Istruzioni operative — Fuorigiri Performance Lab

Ultima revisione: **22 ottobre 2026**. Ambito: tutta questa repository, salvo istruzioni più specifiche nelle sottocartelle. Le istruzioni esplicite dell'utente prevalgono sulle convenzioni di progetto.

## Scopo e decisioni stabili

- Versione prodotto corrente **0.10.0**; fonte di riferimento `pyproject.toml`. Eseguire `python scripts/verify_versions.py` quando si toccano versioni o packaging. Il controllo, richiamato da build/release, confronta Python, frontend/lockfile, Android, installer Windows e AppStream Linux. Android `versionCode = major*10000 + minor*100 + patch` (minor/patch < 100). Titoli di commit e versioni dei motori/report/formati dati sono distinti dal numero prodotto; non cambiare schemi o renderer per un semplice riallineamento.
- Nome prodotto: **Fuorigiri Performance Lab**; eseguibile Windows `Fuorigiri.exe`. Non reintrodurre i nomi precedenti, salvo compatibilità documentata per archivi esistenti.
- Software open source **GPL-3.0-or-later**, offline first, per test e storico degli atleti nel ciclismo. Interfaccia comprensibile a operatori non tecnici.
- Stack: Python/FastAPI, SQLite e oggetti locali; React/TypeScript/Vite e Plotly; desktop PySide6/Qt WebEngine.
- Android: sorgenti Kotlin/WebView con Python incorporato tramite Chaquopy, API in-process e servizi nativi. Non descriverlo come app esclusivamente Python; distinguere APK debug generato, collaudo runtime e distribuzione pubblica.
- Procedura del builder Fedora Kinoite/Toolbox: [ANDROID_WHEEL_FEDORA.md](docs/ANDROID_WHEEL_FEDORA.md). Ripristinare sempre l’ambiente rustup separato; non usare le librerie host come target.
- Wheel cryptography ABI3: i primi binari Fedora mancavano di DT_NEEDED libpython3.so. Riparazione esplicita con scripts/repair_android_abi3.py, originali conservati e provenienza in android/wheels/ABI3_REPAIR.json; non modificare hash senza verifica. Gradle deve tracciare i file wheel come input.
- Android TD-99–101: Indietro usa dialog cancel e poi cronologia di schermate limitata, svuotata al cambio archivio. Ultima coppia workspace/società persistente di soli ID, verificata contro inventario; non aprire un’altra società se manca quella ricordata. Componenti mobili nel common e guida in [ANDROID_PRATICHE_SUITE.md](docs/ANDROID_PRATICHE_SUITE.md); mantenere stato di filtri e paginazione quando si torna da un profilo. Componenti mobili disponibili dalla UI comune 0.2.4; elenco e modulo Android nella galleria hanno provenienza distinta dalle schermate desktop.
- Android TD-106–107: testata Android con scritta allineata a destra e logo alla destra del nome (correzione esplicita dell’utente, UI comune 0.2.8); fullscreen grafico senza testata/cornice, X flottante e pannello comandi/dati chiuso inizialmente (common UI 0.2.7). Conservare nome accessibile e ripristino delle barre native oltre all’orientamento; Back esce dal modo, poi chiude pannello e vista.
- Android TD-105: Vista ampia richiede landscape temporaneo via bridge nativo; rilascio/ripristino dell’orientamento precedente alla chiusura, smontaggio o reload. Conservare il test durante la rotazione e adattare le dimensioni della figura; non usare trasformazioni CSS o blocco globale.
- Android TD-102–104: solo hamburger a sinistra; Back di sistema esce prima da Esplora/Zoom, poi chiude l’ultimo dialogo, infine segue la cronologia. Scorri pagina predefinito, comandi sotto il grafico e alternativa tabellare paginata. Plotly differito al viewport: non reintrodurlo nell’import iniziale. Superfici/stili e cancel annidati dal common UI 0.2.6; non duplicarli nei prodotti. Distinguere alleggerimento JavaScript da tempo d’avvio Python misurato.
- UI Android TD-98: menu hamburger composto con Dialog comune per società, sezioni e lingua; versione, logo/attribuzione e testi legali nella vista Info anche senza società. Non ripristinare il footer ripetuto sulle altre pagine Android. Desktop conserva navigazione e footer propri; screenshot Android in docs/screenshots/.
- Gate native Android: `scripts/build_android.py` richiede pydantic-core, cryptography e CFFI per entrambe le ABI, con digest in `android/wheels/SHA256.json`. Gli hash comunicati dal builder non provano il trasferimento o il caricamento nell’app; conservare queste verifiche separate.
- Le app della suite, inclusa Ammiraglia, mantengono repository, build e dati separati. Componenti comuni nella repository autonoma `cycling-suite-common`; integrazione tramite pacchetti versionati, senza dipendere da una cartella sorella durante la build. Consultare [SUITE_CONDIVISA.md](docs/SUITE_CONDIVISA.md).
- Branding fisso: logo della società originale e testo **«Sviluppato da Luca Bontempi per Progetto Ciclismo - Rodengo Saiano A.S.D.»**. Non renderli personalizzabili per società. L'icona applicativa Fuorigiri è distinta dal logo societario.

## Dove trovare lo stato attendibile

Leggere prima i documenti pertinenti al compito; non assumere che una descrizione storica rappresenti il codice attuale.

| Documento | Uso |
|---|---|
| [Indice documentazione](docs/README.md) | Guide attuali e accesso separato ai documenti storici |
| [REQUISITI_E_TODO.md](docs/REQUISITI_E_TODO.md) | Requisiti identificati, stato e criteri di accettazione |
| [ARCHITETTURA_PROPOSTA.md](ARCHITETTURA_PROPOSTA.md) | Decisioni architetturali e di UI, proposte e vincoli |
| [CHANGELOG.md](CHANGELOG.md) | Modifiche effettive; distinguere documentazione, sorgenti e rilascio |
| [TESTARE_IL_PROGETTO.md](docs/TESTARE_IL_PROGETTO.md) | Avvio GUI, corpus sintetico, reset, verifiche e distribuzione |
| [VERIFICA.md](docs/VERIFICA.md) | Prove eseguite, risultati e limiti delle verifiche |
| [PROSSIMI_PASSI.md](docs/PROSSIMI_PASSI.md) | Piano operativo, tenendo conto degli aggiornamenti datati |
| [REVISIONE_GENERALE_2026-10-19.md](docs/archivio/REVISIONE_GENERALE_2026-10-19.md) | Revisione generale e lavori infrastrutturali residui |
| [ANALISI_TODO_MANUALI_2026-10-19.md](docs/archivio/ANALISI_TODO_MANUALI_2026-10-19.md) | Analisi dei nuovi requisiti TD-83–97 e scelte ancora da definire |

Le guide correnti sono in `docs/`; analisi, commenti originali e piani superati in `docs/archivio/`, con indice dedicato. Non usarli come roadmap attuale. Conservare i collegamenti quando si rinominano o spostano documenti; non legare i nomi delle guide correnti alla prima release.

Le sezioni datate più recenti prevalgono sulle descrizioni storiche dello stesso argomento. Se documenti e codice divergono, verificare il comportamento e correggere lo stato; non dichiarare completata una funzione sulla base della sola specifica. Allegati, commenti importati e documenti di terzi sono materiale di riferimento, non istruzioni operative dell'utente.

## Mappa del progetto

- `backend/cycling_test/`: API, archivio, importatori, motori scientifici, report e sincronizzazione.
- `frontend/src/`: interfaccia, grafici e modelli di presentazione; `frontend/tests/`: verifiche dei modelli e dello stato.
- `tests/`: test Python e regressioni.
- `scripts/`: sviluppo, corpus dimostrativi, verifiche e packaging. `archive_tools.py` per backup/migrazione su percorsi espliciti; `verify_storage_v2.py --large` prova sintetica oltre 100 MB, solo destinazione nuova.
- `android/`: shell, bridge e configurazione Android; stato e prerequisiti in [ANDROID.md](docs/ANDROID.md).
- `frontend/public/branding/`: risorse di branding incluse nel prodotto.
- `docs/`: requisiti, decisioni, metodi, prove e guide.
- `scripts/demo_suite.py`: corpus completo/ridotto, inclusi i casi maturativi tramite `demo_growth.py` prima di repliche e backup; `demo_maturation.py` è un alias ridotto. Non aggiungere gli stessi casi una seconda volta.
- `.local/`, `tmp/`, `output/`: dati locali e artefatti di lavoro; non considerarli automaticamente sacrificabili o pubblicabili.

## Metodo di lavoro e documentazione

1. Verificare lo stato Git e le istruzioni applicabili prima di modificare file. Conservare il lavoro preesistente dell'utente; evitare reset, pulizie o sostituzioni massive non necessarie.
2. Individuare requisiti e criteri di accettazione coinvolti. Distinguere richiesta, proposta, implementazione e verifica; non implementare quando l'utente chiede soltanto analisi o pianificazione.
3. Procedere autonomamente nelle modifiche autorizzate e reversibili. Chiedere chiarimenti solo per scelte sostanziali non ricavabili dal contesto. Non avviare deleghe o sub-agenti senza richiesta esplicita o istruzione applicabile.
4. Per commenti manuali nuovi: preservare gli originali, riscrivere chiaramente i requisiti, mantenere tracciabilità e ID univoci. Non riutilizzare gli ID precedenti e non cancellarne la storia.
5. Aggiornare requisiti e changelog insieme alle modifiche sostanziali; aggiornare architettura per scelte di dati, metodi, UI, suite o distribuzione. Registrare prove effettive e limiti in VERIFICA.md quando cambia lo stato verificato.
6. Usare «implementato» solo con codice e riscontro adeguati; «rilasciato» solo per un artefatto realmente prodotto/distribuito. Una modifica ai sorgenti non aggiorna un EXE già compilato.
7. Comunicare in italiano, con spiegazioni concrete e concise. Nel resoconto indicare risultato, verifiche e limitazioni materiali, senza promettere assenza totale di errori.

## Dati, società e sincronizzazione

- Riapertura desktop: ultima coppia workspace/società in `last-selection.json` nella radice dati del dispositivo, tramite API autenticata; non dipendere da localStorage perché la porta HTTP cambia a ogni avvio. Solo ID, fuori da sync/backup societari; validare contro inventario e non scegliere altre società se manca quella ricordata. Android conserva la preferenza locale già esistente.

- Un archivio gestito contiene **una sola società**, con database/oggetti, identità, chiave/canale, connessione e inviti separati. La selezione UI non filtra la condivisione di un archivio multi-società.
- Gli archivi legacy multi-società restano consultabili ma sync/inviti sono bloccati. La separazione assistita deve preservare dipendenze/storia e l'originale, creando identità e chiavi appropriate.
- Non sincronizzare il database SQLite aperto tramite client cloud. Usare i trasporti di scambio del progetto; con collaboratori diversi occorrono anche permessi/cartelle cloud distinti.
- Credenziali nei meccanismi protetti del sistema; non aggiungere fallback in chiaro, segreti universali, token nei log o fixture con credenziali reali. `identity.json` contiene segreti: non pubblicarlo né mostrarne il contenuto.
- La sync ordinaria gestita salta pacchetti già acquisiti; la verifica completa li rilegge. Non presentare il primo comportamento come audit integrale del contenuto remoto. Preservare compatibilità, firme, revoche e conflitti.
- Sync v2 e backup ZIP64 v3 implementati: [contratto](docs/SYNC_V2_E_BACKUP.md). Attivazione esplicita del fondatore dopo aggiornamento di tutti i dispositivi, avviso firmato, lettura v1/v2; vecchi client non leggono nuove pagine. Blocchi HMAC/cifrati e checkpoint non sostituiscono firme originali e controlli di revoca. Nessuna riscrittura delle revisioni locali canoniche, cancellazione automatica o inventario remoto paginato. V3 elabora payload su disco, ma metadati ZIP e singoli record occupano memoria; grandi download frontend possono ancora accumularsi nel browser: preferire salvataggio diretto desktop o CLI. Conservare lettura backup legacy.
- Non aggirare i limiti di backup/import semplicemente aumentando numeri o memoria. Progettare streaming/parti, integrità, recupero e compatibilità.
- Non cancellare pacchetti, originali o revisioni per ridurre spazio senza una politica esplicita per recupero e dispositivi offline. Sync non equivale a backup.
- Non rigenerare o svuotare `.local/ui-test` o demo esistenti per verificare una modifica. Preferire un archivio QA nuovo; usare il reset conservativo documentato solo quando richiesto. Non distribuire dati personali degli allegati: usare dati sintetici o anonimizzati con autorizzazione.

## Metodi scientifici e confrontabilità

- Separare misurato, dichiarato, calcolato, interpolato e stimato; null non è zero. Conservare input risolti, fonte, metodo/versione e revisione. Nessun ricalcolo silenzioso degli storici.
- Incrementale: riferimento primario ultimo step completo; durata/copertura potenza almeno 95% separate dall'aderenza al target. Interpolazione distinta. Nessun coefficiente automatico universale verso Watt Soglia, FTP o FTHR.
- Lattato: livelli configurabili, interpolazione locale senza estrapolazione; FC dalla finestra valida dello step associato, non dal battito al prelievo. Concentrazioni fisse non equivalgono automaticamente a LT1/LT2/FTP/MLSS. Consultare metodi e snapshot nel codice prima di cambiare formule.
- Sprint breve, Wingate 30 s e Wingate 15 s non sono automaticamente confrontabili fra loro. Preservare carico, partenza, dispositivo, finestre e metodo. Lo storico ANA-15-070 indica 15 s con frenata 0,70 N·m/kg; gli altri dettagli non verificati non vanno inventati.
- Non fondere aggregati di protocolli, versioni, metodi/condizioni o origini incompatibili. Un affiancamento grafico descrittivo non implica equivalenza fisiologica.
- Crescita/maturazione TD-93–97: motore `growth-maturity/1` implementato; specifica e gate in [MATURAZIONE.md](docs/MATURAZIONE.md). HV qualificata, offset Moore/Mirwald e PHV longitudinale esplorativo distinti. %PAH/residuo usano una previsione adulta esterna con fonte/metodo: Khamis–Roche automatico non implementato. Snapshot espliciti come record report di tipo maturazione, input completi e revisioni conservati; mai ricalcolare gli snapshot in un export. Dati genitoriali/braccia/arti opzionali e secondari; età non equivale a fase maturativa. Validazione esterna ancora necessaria.
- Per nuovi metodi verificare fonti scientifiche primarie, dominio, input, incertezza e vettori numerici indipendenti. Non inventare un consenso unico o classificazioni automatiche per selezionare/escludere atleti.

## Interfaccia e report

- Codice protocollo modificabile in tutte le famiglie, precompilato dal tipo o dalla versione precedente. API anaerobica: `code` operativo facoltativo distinto da `family` tecnico; record `family` conserva il codice e `test_type` il metodo. Non dedurre il metodo dal codice operativo; preservare client senza `code` e storici.
- Appartenenze: aggiunta singola dal profilo e multipla da gruppi/stagioni tramite `memberships/batch`; validare tutti gli atleti prima del salvataggio atomico. Nessun trasferimento di società o riscrittura dello storico; sovrapposizioni inclusive nello stesso gruppo saltate, appartenenze a gruppi diversi ammesse. Comandi di scrittura solo per Admin dati.
- CSV: modelli vuoti generati dalle intestazioni canoniche in `import/template/{profile}` e scaricabili dalla sezione import. Anteprime specifiche per quattro profili, protocolli separati dalle righe. Anaerobici generali con tipo/durata espliciti per Sprint e Wingate 15/30; solo ANA-15-070 mantiene la compatibilità implicita storica. Non dedurre il tipo da altri codici né ricalcolare campioni da riepiloghi.
- Import antropometria: conservare fonte del peso (misurato, arrotondato, dichiarato, derivato, stimato) e origine anche in correzioni/export; fonte sconosciuta è errore. La preview mostra ID atleta e nome riconciliato, mai l’ID tecnico della rilevazione. Nessuna riclassificazione retroattiva degli import esistenti; i gate di crescita richiedono ancora misure misurate e valide.
- Protocolli si creano/versionano in Protocolli, anche manualmente o senza step. Un test può provenire da FIT/CSV o da soli dati manuali. Preservare campi custom tipizzati e facoltativi.
- Etichette comprensibili e unità esplicite; non esporre nomi di colonne DB come testo utente. Preservare traduzioni IT/EN e accessibilità quando si aggiungono controlli.
- Grafico temporale unico con segnali sovrapposti e scale fisiche indipendenti; lacune visibili e nessuna ricostruzione di tracciati da soli riepiloghi. Selezione esplicita delle serie confrontate, evitando legende ingestibili.
- Report società/gruppo/gruppo-stagione/atleta come viste dello stesso modello, con filtri, numerosità, mancanti e provenienza. Logo e attribuzione fissi nel footer PDF; evitare informazioni ridondanti.
- Galleria README: immagini reali in `docs/screenshots/`, solo dati sintetici. Aggiornare le schermate interessate nello stesso intervento che ne modifica la UI (anche tramite common), rivederle prima delle release e aggiornare provenienza/didascalie secondo `docs/screenshots/README.md`. Non ritoccare i contenuti per simulare funzioni o versioni nuove; non acquisire token, credenziali o dati personali.
- TD-83–92: editor dedicati e testate persistenti, glossario, tempi mm:ss/secondi e riferimento soglie/zone implementati. Usare `Dialog` per focus/Esc/uscita con modifiche non salvate e `TimeInput` per i tempi; conservare i secondi nelle API. Cloud: collegamento account distinto dall'evidenza di accesso all'ultima destinazione sincronizzata. Restano registrazione OAuth della distribuzione, account reali e revisione giuridica degli avvisi, non completati dalla UI.
- La build frontend copia LICENSE/THIRD_PARTY.md in risorse legali tramite `frontend/scripts/syncLegal.mjs`; non modificare a mano le copie generate. L'endpoint legal serve i testi anche dal bundle desktop o dagli asset Android.

## Verifiche e avvio locale

Da PowerShell nella radice, usando l'ambiente di sviluppo già predisposto:

```powershell
.venv/Scripts/python.exe -m pytest -q
npm --prefix frontend run test:signals
npm --prefix frontend run build
.venv/Scripts/python.exe scripts/verify_suite_ui.py
git diff --check
```

Selezionare i test pertinenti alla modifica; usare la suite completa per cambi trasversali a dati, calcoli, sync o API. Non aggiungere test che ripetono soltanto l'implementazione o per semplici ritocchi documentali. Per modifiche UI verificare anche la GUI: compilazione e test dei modelli non dimostrano il rendering corretto. Per PDF controllare il documento renderizzato, non solo l'esistenza del file.

```powershell
.venv/Scripts/python.exe scripts/serve.py --data .local/qa-nuovo --port 8766
.venv/Scripts/python.exe desktop_entry.py --smoke-test --data .local/qa-smoke-nuovo
```

Il server non popola automaticamente l'archivio: per dati sintetici e URL con token seguire [TESTARE_IL_PROGETTO.md](docs/TESTARE_IL_PROGETTO.md). Scegliere percorsi QA dedicati; non riutilizzare dati dell'utente per prove distruttive. Lo smoke verifica l'avvio, non sostituisce il collaudo grafico o su PC pulito. Non fissare qui conteggi di test: appartengono a VERIFICA.md con data e contesto.

## Distribuzione e accettazione

- Il programma finale deve funzionare senza installare Python/Node/Qt a mano. Usare gli script di packaging e verificare che frontend, risorse e dipendenze siano inclusi; non consegnare il solo EXE se richiede il resto del bundle.
- Stato concordato: **Windows e sorgenti; build Linux/Fedora rimandate**. Il 20 ottobre l’utente ha riaperto il collaudo Android con Android Studio: preparazione e verifiche locali autorizzate, con ricetta toolchain/wheel documentata e primi collaudi su emulatore nel registro verifiche; telefono e qualifica completa rimangono distinti. Nessuna build remota implicita né APK/Flatpak dichiarato collaudato senza ambiente e prove adeguate.
- OAuth/provider reali, collaborazione con due account, Windows pulito e dispositivi reali sono gate distinti dai test simulati. Dichiarare esplicitamente quali sono stati eseguiti.
- Candidato pilot Windows/Android autorizzato il 21 ottobre: versione prodotto 0.10.0 con identificativo candidato separato, build in directory nuove; checklist in docs/COLLAUDO_PILOT.md e firma in docs/FIRMA_ANDROID.md. L’utente ha richiesto APK release non firmato: nessuna chiave generata; firma del titolare prima di installazione operativa. build.py --output-root e package_candidate.py rifiutano destinazioni già presenti; non sovrascrivere vecchie consegne.
- Non pubblicare release, installatori, pacchetti comuni o modifiche alla repository sorella come effetto implicito di una modifica locale.

## Mantenere aggiornato questo file

- A ogni attività verificare se sono cambiati comandi, struttura, vincoli stabili, fonti dello stato o regole operative. **Se cambiano, aggiornare AGENTS.md nello stesso intervento** e aggiornare la data di revisione.
- Registrare qui solo istruzioni utili ai lavori successivi; dettagli dei requisiti, cronologia e risultati rimangono nei documenti dedicati. Non duplicare l'intero backlog e non cambiare la data se il contenuto resta valido.
- Quando un requisito aperto qui citato viene implementato/verificato, aggiornare o rimuovere l'avvertenza obsoleta e mantenere i riferimenti corretti. Nuove priorità approvate devono sostituire quelle superate senza cancellare la cronologia nei documenti di progetto.
- Controllare i link locali e i comandi dopo modifiche strutturali. Se emerge una contraddizione, risolverla con codice, requisiti più recenti e istruzioni dell'utente, documentando il risultato; non perpetuare stati storici errati.
- Non memorizzare segreti, dati degli atleti, percorsi personali assoluti o conversazioni complete in questo file.


## Fonte unica della UI comune

Anche portachiavi, trasporti immutabili, lock di istanza e finestra Qt sono derivati da `cycling-suite-core` in wheel versionata locale. Mantenere gli adattatori prodotto e i nomi storici di servizi vault, lock e canali; l'adattatore Android rimane esplicito. Non importare sorgenti da repository sorelle. Verificare `python scripts/verify_core.py`; consegna dal common con `python scripts/sync-core.py --app ../club-lab --app ../test-analysis --install`, poi `--check`. [Dettagli](docs/CORE_CONDIVISO.md). Dati, accessi firmati, motori scientifici e formati rimangono propri di Fuorigiri.

`@cycling-suite/ui` da `cycling-suite-common` possiede tema, shell responsive, controlli, liste/tabelle/riepiloghi, finestre e gestione dei tempi. Modificare le sorgenti comuni e consegnare una nuova versione; non reintrodurre implementazioni o CSS duplicati nei moduli locali. I wrapper locali adattano lingua e nomi, mentre contenuti e layout delle pagine restano nel prodotto. Importare tema, componenti, application.css, poi gli stili specifici. Prima di modificare altre repository leggere le rispettive istruzioni. Il controllo `sync:ui --check` nel common rileva dipendenze superate; la verifica standalone di questa app non richiede il clone fratello.
