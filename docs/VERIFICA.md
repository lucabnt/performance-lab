# Verifiche locali — Fuorigiri Performance Lab

## 25 ottobre 2026 — REPORT-SAVED-01

- 5 test backend mirati report/workspace passati: data e contesto con atleta archiviato, ordine, esclusione maturazione, originali invariati e download. 31 test frontend passati; build TypeScript/Vite riuscita dopo limite finale a 5. Warning dimensione chunk preesistente.
- Browser sull'app compilata con backend reale e 25 report sintetici in archivio QA nuovo: 1–5 e 6–10, filtro MD con 9 risultati e ritorno a 1–5, ricerca senza risultati, download dalla scheda; date e ambiti leggibili anche nel viewport stretto. Paginazione locale; nessun benchmark su inventari remoti grandi. Nessun archivio operativo modificato, installer 03 non ricompilato.

## 25 ottobre 2026 — report archivio e rose storiche

- Python completo: 238 passati, 1 saltato; frontend: 31 test passati e build TypeScript/Vite riuscita. Versione prodotto 0.10.0 e UI comune 0.2.8 verificate. Warning Plotly sulla dimensione del chunk invariato.
- Browser su build compilata e backend reale con dati sintetici: ricerca senza risultati e filtro Attivi precedenti, apertura Esordienti 2023 con 3 atleti archiviati; risultato Tutti, ricerca vuota e 3 righe. Esportazione PDF reale con spinner, messaggio accessibile, controlli disabilitati e ripristinati al termine; verificata anche anteprima.
- PDF sintetico con 19 atleti, 89 test e 51 misure: 93 pagine renderizzate e ispezionate tramite cinque fogli di contatto; indice, aggregati, scheda atleta, dettagli e protocolli esaminati anche a risoluzione maggiore. Indice completo a pagina 2 con collegamenti e segnalibri; font incorporati, tabelle nei margini. Test automatici su indice/destinazioni, ambito individuale, dati invariati e tabelle lunghe. Il numero di pagine non è confrontabile con il PDF privato dell'utente, che contiene un altro dataset. Originale preservato.
- Windows candidato 03: PyInstaller e Inno Setup completati, EXE congelato avviato in smoke con esito 0 (import, logo e backend HTTP). Android assembleRelease offline riuscito; nessuna firma generata o installazione operativa effettuata.
- Guida Drive confrontata con documentazione ufficiale Google; nessun consenso reale o scambio fra account eseguito. Questi gate restano aperti.

## 22 ottobre 2026 — GRUPPI-01 assegnazioni

- 9 test mirati appartenenze/workspace passati: aggiunta atomica, ripetizione senza duplicati, sovrapposizioni inclusive, periodi consecutivi, anno di categoria, gruppo/stagione, dati di altra società, atleti archiviati, date incoerenti, compatibilità con appartenenze singole precedenti e blocco viewer.
- Suite completa in esecuzione separata dalla build: 219 passati, 1 saltato; 25 test frontend passati. La prima esecuzione concorrente alla build frontend aveva incontrato un file del logo temporaneamente non accessibile; ripetizione a build conclusa riuscita. Nessuna modifica allo smoke o ai controlli per aggirarlo.
- Browser sull’app compilata completa, backend reale e archivio sintetico nuovo: aggiunti Beta/Gamma alla stagione 2026 dopo ricerca con selezione conservata; Alfa già assegnato disabilitato. Conferma con due aggiunte e conteggi 1→3. Dal profilo Beta aggiunta singola al gruppo padre, senza riscrivere l’appartenenza alla stagione. Nessun dato personale o archivio operativo usato.
- Ultima build frontend ricontrollata nel browser: comandi su gruppo/stagione e lista filtrata, dialogo con due scelte e conferma, stagione distinta nel profilo. Screenshot reale in `docs/screenshots/gruppi-aggiungi-atleti.png`.
- Build 05: bundle Windows completato e smoke EXE congelato con PATH Windows riuscito. Installer Inno Setup compilato in 112,781 s. APK release/debug completati offline in 1 min 2 s; ZIP, frontend corrente e runtime di entrambe le ABI verificati, firma debug v2 valida, release non firmato e allineamento controllati.
- Consegna 05 completata: 14 checksum finali verificati, ZIP integri e sorgenti funzionali confrontati con lo snapshot; frontend bundle/APK corrente. Portabile estratto in directory nuova e smoke con PATH Windows riuscito. Nessuna installazione operativa o collaudo su telefono/PC pulito eseguito in questa sessione.
- Preparazione pacchetti successivi `pilot-20261022-05`, con versione prodotto 0.10.0 invariata e consegne precedenti conservate; telefono e PC pulito rimangono verifiche distinte.

## 22 ottobre 2026 — IMPORT-03 test e modelli CSV

- Lettura in sola pianificazione dei CSV forniti: 51 test aerobici e 2 protocolli, 38 test anaerobici e 1 protocollo; nessun errore. File originali e archivi operativi non modificati; dati personali non inclusi nelle fixture o nelle consegne.
- Suite completa: 214 passati, 1 saltato; 25 test frontend e build riusciti. Tre test aggiuntivi coprono modelli canonici con sole intestazioni, preview vuota valida per tutti i profili, download, conteggio separato protocolli/righe, preview limitata a 20 test effettivi e commit, Sprint/15/30 e legacy nello stesso lotto, duplicati e conflitti dei metadati legacy. 29 test mirati import/anaerobici passati; warning preesistenti.
- Browser con backend reale e archivio QA nuovo: caricati quattro CSV sintetici, controllate le preview; download effettivo dei quattro modelli confrontato byte per byte con le intestazioni canoniche. Screenshot reale della pagina QA in `docs/screenshots/import-csv-anaerobici.png`. Nessuna alterazione delle regole di origine o sicurezza per eseguire il collaudo.
- Bundle Windows 04 compilato e smoke EXE congelato con PATH limitato a Windows riuscito. Android release/debug completati offline in 33 s.
- Installer Windows 04 compilato da bundle isolato in 127,672 s (196097209 byte). Verificati firma debug v2, assenza firma release, allineamento APK, ZIP e hash del frontend corrente nelle due build Android, entrambe con runtime ARM64/x86_64. 53 test mirati import/anaerobico/crescita passati sullo stato finale.
- Consegna 04 completata in `dist/candidates/Fuorigiri-0.10.0-pilot-20261022-04`: installer, portabile, APK debug e release non firmato, sorgenti, wheel e ZIP dei quattro modelli vuoti. Verificati 14 checksum e corrispondenza byte dei sorgenti funzionali nello ZIP; portabile estratto e smoke indipendente riuscito con PATH Windows. Nessun pacchetto precedente o archivio operativo sostituito. Firma release, telefono e PC pulito restano da collaudare.
- Preparazione finale Windows/Android `pilot-20261022-04` dai sorgenti con IMPORT-02/03; build precedenti conservate. Le nuove anteprime non certificano la comparabilità scientifica dei protocolli o ricreano campioni assenti.

## 22 ottobre 2026 — IMPORT-02 antropometria

- CSV personale letto soltanto per pianificazione, senza commit: 51 righe pronte, nessun errore; 44 pesi misurati, 2 arrotondati, 5 derivati, nessuna statura presente. Nessun dato personale copiato nelle fixture, negli archivi QA o nei pacchetti.
- 35 test mirati import/crescita passati; suite completa 211 passati, 1 saltato; 25 test frontend e build riusciti. Test sintetico API su anteprima, fonti incluso stimato e default dichiarato, commit, duplicati, correzione, origine ed export; fonte sconosciuta segnalata e derivato non ammesso al modello Moore.
- Browser: componente ImportPanel reale in pagina QA temporanea con API sintetica; atleta, data, peso, statura mancante, fonte derivata e origine verificati visivamente. Cattura in `output/qa-import-antropometria/anteprima.png`; non prova il bridge Android.
- Preparazione `pilot-20261022-03` interrotta prima del confezionamento per includere IMPORT-03 nel successivo candidato 04, separato dalle consegne precedenti. Android assembleRelease e assembleDebug completati offline in 40 s con JDK 21. Nessuna installazione operativa o modifica dei dati già importati.

## 22 ottobre 2026 — build pilot-20261022-02

- Suite Python completa: 210 passati, 1 saltato, warning preesistenti Starlette/httpx e ZIP con nome duplicato nel caso di corruzione intenzionale. Frontend corrente già compilato e 25 test modelli passati; versioni prodotto 0.10.0, UI 0.2.8 e core 0.1.2 coerenti.
- Bundle Windows isolato in `output/build-pilot-20261022-02/bundle/Fuorigiri`: PyInstaller completato; smoke EXE congelato con PATH limitato ai percorsi Windows riuscito, backend HTTP/logo/dipendenze verificati su dati QA nuovi.
- Installer Inno Setup compilato dal bundle corrente (129,969 s), destinazione isolata; 196062762 byte. Pacchetto finale in `dist/candidates/Fuorigiri-0.10.0-pilot-20261022-02/`, con sorgenti e materiali di ricostruzione.
- Android: Gradle 8.13 offline con JDK Temurin 21 ha completato assembleRelease e assembleDebug. ZIP, frontend corrente confrontato per SHA-256 e runtime Python di entrambe le ABI verificati; firma debug v2 valida, release non firmato confermato, zipalign con controllo 16 KB riuscito per entrambi. Allineamento non equivale a qualifica runtime su dispositivo 16 KB. Nessuna nuova chiave di firma generata.
- Confezionamento finale completato: 13 checksum verificati, ZIP controllati dal packager, portabile estratto in directory nuova e smoke indipendente riuscito con PATH Windows. APK debug aggiuntivo e relative informazioni inclusi nel manifest finale; nessun artefatto precedente sovrascritto.
- Nessuna installazione sopra dati operativi o prova su telefono/PC pulito in questa sessione; cloud reale e qualifica biologica restano gate separati. Consegne precedenti conservate.

## 22 ottobre 2026 — anteprima anagrafica CSV

- CSV fornito letto senza commit: 19 righe pronte, nessun errore; cognomi e anni presenti. Nessun dato personale aggiunto alla repository o agli archivi QA.
- 10 test Python di tests/test_features.py passati, inclusa regressione anteprima/commit su identità, nascita, fonte, sesso, stato e note con dati sintetici; 25 test frontend passati e build riuscita. Warning preesistenti Starlette/httpx e dimensioni bundle.
- Browser: componente ImportPanel reale in pagina QA temporanea con risposta API sintetica, due atleti attivo/archiviato e nascita confermata/non confermata; tabella e messaggio senza errori verificati visivamente. Non eseguito import del CSV personale nell’archivio operativo.

## 22 ottobre 2026 — PROTOCOLLI-01, codice modificabile

- Python: `pytest -q tests/test_features.py tests/test_custom_protocols.py tests/test_anaerobic.py`: **40 passati**. Regressioni Sprint/Wingate con codice personalizzato, metodo conservato, versione collegata, duplicati e codice vuoto rifiutati, inserimento manuale e compatibilità con payload senza codice. Avviso deprecazione Starlette/httpx preesistente.
- Frontend: `npm --prefix frontend run test:signals`: **25 passati**; `npm --prefix frontend run build`: riuscita (avviso dimensione chunk Plotly). `scripts/verify_suite_ui.py`: UI comune 0.2.8 coerente. `git diff --check`: pulito.
- Browser locale sul frontend compilato, archivio QA nuovo con soli dati sintetici: Codice iniziale visibile per incrementale, Sprint, Wingate 15/30 e personalizzato; modifica e salvataggio Wingate con `ANA-DEMO-15`, visualizzazione nel catalogo e codice ereditato in Nuova versione. Acquisizione reale verificata visivamente in `screenshots/protocollo-codice.png`. Import ERG aggiornato nei sorgenti e compilato, senza prova di caricamento file in questa sessione.
- Nessuna modifica agli archivi reali, migrazione, metodo scientifico o pacchetto UI comune. Nessun EXE/APK/installer ricostruito; nessun collaudo Android implicito. Per incrementali e personalizzati restano i vincoli precedenti di codice invariato durante la revisione.


## 22 ottobre 2026 — DESKTOP-01, riapertura ultima società

- Suite Python completa: **206 passati, 1 saltato**; nuovi casi di persistenza dopo ricreazione backend/cambio porta/token, preferenza malformata, ID incoerenti, autenticazione e visualizzatore. Restano i warning noti Starlette/httpx e ZIP duplicato intenzionale.
- Frontend: **25 test passati**, TypeScript/Vite compilati; warning noto sul chunk Plotly.
- GUI desktop web compilata su archivio QA nuovo `.local/qa-last-society-20261022`: creata società sintetica, arrestato backend sulla porta 8774, riavviato sulla 8775 con nuova sessione/token e nuova scheda. La società ricordata si apre direttamente sulla pagina Atleti, senza selezione manuale. Verificato stato accessibile della GUI.
- Nessun layout cambiato; schermate della galleria ancora rappresentative. Nessun archivio preesistente modificato. Il candidato del 21 ottobre e l’installazione precedente non contengono questa correzione. Nuova build Windows isolata in `.local/candidate-windows-20261022-01`: PyInstaller riuscito e smoke dell’EXE congelato superato con PATH limitato a Windows, senza Python/Node. Installer Inno Setup compilato con successo (111,625 s), consegna `dist/candidates/Fuorigiri-0.10.0-windows-20261022-01`, SHA-256 `b4d1538adb7d1f0f5659ec41b07662fb3e38d774884799f8859aaa507c9f7915`, 196051115 byte, quattro checksum verificati. Non firmato Authenticode; aggiornamento sopra l’installazione dell’utente non eseguito dall’agente, resta W-04/W-07.


## Aggiornamento candidato pilot-20261021-02 — 21 ottobre 2026

Anche lo ZIP portabile finale è stato estratto in una nuova cartella QA: smoke dell'EXE estratto riuscito, PATH limitato a Windows e archivio di prova separato.

Consegna completata in `dist/candidates/Fuorigiri-0.10.0-pilot-20261021-02`: installer 196044889 byte, ZIP portabile 279666090 byte, APK unsigned 99396505 byte (SHA-256 `c512ac572ae5d67d6dc3008806425ac5f325c45cc8a4730887e6d500e00a27ff`). Verificati i 12 checksum finali e CRC degli ZIP; smoke dell'EXE compilato riuscito con PATH senza Python/Node. Installer creato da Inno Setup 6.7.3 senza installazione o firma Authenticode. Sorgenti e wheel incluse in archivi separati; vecchia consegna conservata.

Ricompilati bundle Windows e APK release dai sorgenti corretti nella revisione odierna; versione prodotto 0.10.0/code 1000 invariata, candidato distinto. PyInstaller in `.local/candidate-windows-20261021-02`; Gradle 8.13 offline con JDK Temurin 21, `assembleRelease` e lintVital riusciti. Primo tentativo con JDK 25 di Android Studio fallito per incompatibilità del runtime, senza modifica al progetto. APK con arm64-v8a/x86_64, minSdk 26/target 35, non debuggable; zipalign 16 KB riuscito, apksigner conferma assenza di firma. Nessuna chiave generata, nessuna installazione Android o prova ARM64/pagine 16 KB runtime. Candidato precedente conservato; checklist corrente aggiornata al nuovo ID.

## Revisione sorgenti e correzioni conservative — 21 ottobre 2026

- Header token non ASCII rifiutati con 401; misure eliminate escluse anche dal CSV antropometrico principale; CSV malformati o con campi oltre limite rifiutati con 422, senza importazione parziale. Preservati CSV multilinea validi, virgolette raddoppiate, formati e metodi scientifici.
- I tre nuovi test di regressione fallivano prima delle correzioni. Suite finale: **204 test Python superati, 1 saltato**, in 74,57 s. Dopo l'aggiunta dell'ulteriore asserzione sui CSV validi, i 6 test di `test_review_regressions.py` sono stati rieseguiti con successo. Baseline: 201 passati e 1 saltato.
- **25 test frontend superati**, build TypeScript/Vite riuscita; `pip check`, verificatori versioni/UI/core e `git diff --check` riusciti. `npm audit --json` non segnala vulnerabilità note nei pacchetti npm. Non equivale a scansione CVE Python: `pip-audit` non disponibile nell'ambiente controllato.
- Restano warning Starlette/httpx, ZIP duplicato intenzionale nel test di corruzione e dimensione del chunk Plotly già separato. Non modificata la UI, non ripetuto il collaudo grafico. Nessun installer/EXE/APK rigenerato o provider reale contattato.
- Export CSV grezzo con rischio di interpretazione formule conservato per compatibilità: occorre una scelta distinta per l'export destinato ai fogli di calcolo. Analisi trasversale in `cycling-suite-common/docs/REVISIONE_APPLICAZIONI_2026-10-21.md`. I candidati compilati esistenti non includono queste correzioni.

## Preparazione candidato pilot — 21 ottobre 2026

Candidato locale prodotto 0.10.0, ID pilot-20261021-01; nessuna pubblicazione. Regressione completa: **201 Python passati, 1 saltato**, due warning noti (Starlette/httpx e ZIP corrotto intenzionalmente duplicato). **25 test frontend passati**, build TypeScript/Vite e verificatori versioni/UI 0.2.8/core 0.1.2 riusciti. Sintassi dei due script Python di packaging e dei due blocchi PowerShell della guida firma verificata senza eseguire generazione chiavi.

Windows: PyInstaller 6.22.3 in directory nuova .local/candidate-windows-20261021-01, bundle dipendenze incluso (circa 691 MB prima degli archivi). Smoke del binario congelato con PATH limitato alle directory Windows: exit 0, import/logo/backend HTTP riusciti, dati QA nuovi; non è un PC pulito né collaudo GUI completo. Warning PyInstaller su plugin QML opzionale non presente; nessun errore bloccante nello smoke, verifica grafica sul PC di destinazione ancora aperta. ISCC locale con Authenticode Valid del compilatore; installer Fuorigiri **non firmato** prodotto con Inno Setup (196030915 byte), nessuna installazione/disinstallazione sul profilo operativo per non toccare registrazioni esistenti.

Android: digest delle sei wheel verificati; assembleRelease --offline inizialmente fermato da Lint non in cache. Ripreso con download delle dipendenze ufficiali, senza disabilitare lintVitalRelease, build riuscita. APK release unsigned con package org.fuorigiri.performancelab, versione 0.10.0/code 1000, minSdk 26, target/compile 35, ABI arm64-v8a e x86_64, flag application-debuggable assente. zipalign -c -P 16 -v 4 riuscito; apksigner verify fallisce come atteso per assenza di firma. Questi controlli non qualificano runtime ARM64 o pagine 16 KB. Nessuna chiave generata, APK non installato perché non firmato, come richiesto dal titolare.

Consegna congelata in dist/candidates/Fuorigiri-0.10.0-pilot-20261021-01: installer Windows 196030915 byte, ZIP portabile 279664863 byte, APK release non firmato 99396505 byte, sorgenti 4510737 byte e wheel native 13773852 byte. CRC di tutti gli ZIP e SHA-256 dei 12 file della consegna verificati. APK SHA-256 `358b660953639cc7d6c3ad45cfee245ff14ae851f67e27735e6a59123dcd334b`, installer `31a85b0da2a3a01d9cb2c7e696a13fa8f2cd4172ff941b2c89d88190f4765dc0`; Authenticode installer NotSigned. ZIP portabile estratto in una nuova directory QA e secondo smoke del suo EXE con PATH senza Python/Node e percorso dati con spazi/accenti: exit 0. La checklist allegata al candidato è la fotografia al packaging, quella nei sorgenti registra anche le verifiche successive.

Checklist in COLLAUDO_PILOT.md: marcate solo prove effettive; PC pulito, firma del titolare, telefono, aggiornamento operativo, provider/account reali e validazione scientifica esterna rimangono aperti. Manifest/checksum della consegna identificano i byte; sorgenti dal working tree con modifiche locali, non dal solo commit base.


## Correzione TD-106 — logo a destra, 21 ottobre 2026

Testata Android corretta su indicazione esplicita: scritta prima dell’icona e allineamento a destra. Common UI 0.2.8 consegnata a Fuorigiri (10 test Node/3 core passati); primo tentativo di installazione npm fermato da apertura transitoria del lockfile, secondo riuscito senza modifiche manuali al vendor. Build frontend/APK e verify_suite_ui riusciti; APK installato senza reset, SHA-256 `34e6f569585d60f3c6e1167a290387671457be5b7dfee983fa1c58d8bf9a4635`.

Prova reale emulatore API 35 x86_64: bounding rect dell’icona interamente a destra del testo, text-align right, bordo destro del gruppo uguale a quello della testata. Screenshot Atleti/Menu/Info rinnovati e ispezionati con sola società sintetica. Nessuna modifica a dati/metodi o altre schermate; test dei modelli/backend non ripetuti per il solo riordino visivo.

## Android TD-106–107 — 21 ottobre 2026

25 test frontend passati, build TypeScript/Vite e APK debug riusciti; verificatori UI 0.2.7/versione prodotto 0.10.0 coerenti. Common: 10 test Node/3 test core passati durante la consegna, build e sync:ui --check riusciti. APK installato senza reset, SHA-256 `4eecdbe9e0d9c7331186aae2aa948eab705762b99bffc0266f512d0dde760b25`. Nessuna pubblicazione o ricalcolo scientifico.

Emulatore API 35 x86_64: fullscreen reale della WebView 870×412 CSS px (cutout rispettato), dialogo a x=0/y=0 e figura alta 412 px; intestazione visuale assente, nome accessibile Esplora grafico conservato, X raggiungibile e pannello richiamabile. Rimossa la prima istruzione di sistema “Viewing full screen” con Got it prima della cattura reale, senza ritocchi alla foto. Comandi Esplora richiudono il pannello; Back torna a Scorri pagina mantenendo fullscreen, poi chiude pannello se aperto e infine vista. Dopo chiusura, viewport verticale 412×846 con barre nuovamente visibili e test ancora aperto. Screenshot fullscreen sostituito e ispezionato; nuovo elenco acquisito. Header: logo interamente a sinistra del testo, stessa riga verificata con bounding rect e screenshot.

L’avvio nativo include il marchio orizzontale nei sorgenti compilati; il tentativo di catturarlo immediatamente mostrava ancora il launcher e non viene usato come prova visiva del bootstrap. Header e fullscreen verificati effettivamente. Restano telefono/gesture reali/TalkBack, altre configurazioni di barre e tablet/multiwindow. Nessun nuovo collaudo desktop o modifica ai dati reali.

## Android TD-105 — 21 ottobre 2026

Build TypeScript/Vite, 25 test frontend, verificatori UI 0.2.6/versioni 0.10.0 e assembleDebug --offline riusciti. APK aggiornato installato con -r senza reset, SHA-256 `7ba3671a08145a3bf1c7b3aa09c7b7e6b4eca781ef588d96cb08ab0ab2d27aad`. Nessuna modifica ai metodi o dipendenze native, test backend/runtime scientifico non ripetuti.

Su emulatore API 35 x86_64, società esclusivamente sintetica: Vista ampia ruota da viewport 412×846 a 870×336 CSS px; dopo assestamento figura alta 220 px, tracciato/assi/legenda realmente disegnati e screenshot orizzontale 2424×1080 ispezionato. Primo Back da Esplora mantiene due dialoghi e landscape con Scorri pagina; chiusura tramite Back o X torna al viewport verticale e mantiene il test aperto. Nessuna navigazione o reimportazione dati durante la rotazione. Non provati telefono, autorotazione nelle due posizioni orizzontali, reload durante la vista ampia o tablet/multiwindow. Documento Android consultato per il contratto di orientamento; non dichiarata compatibilità completa di tali configurazioni.

## Android TD-102–104 — 21 ottobre 2026

- **Build e modelli:** 25 test frontend superati, inclusi mancanti/zero/coordinate indipendenti e paginazione su 100.000 valori della tabella accessibile. TypeScript/Vite riusciti. Bundle iniziale circa 479,95 kB (gzip 148,19 kB), Plotly locale separato circa 4.843,38 kB; rimane avviso Vite sul chunk grafico grande. Common UI 0.2.6: 10 test Node e 3 test core passati, build catalogo/UI e sync:ui --check Fuorigiri riusciti. Verificatori versione 0.10.0 e integrità UI passati. Nessuna modifica ai motori o backend; suite backend completa non ripetuta.
- **APK reale:** assembleDebug --offline riuscito; installazione -r senza cancellare dati e force-stop/riavvio sulla stessa società sintetica. APK 102239106 byte, SHA-256 `1dcb46a8a0f72c78302280bf9301d63a63848caf681385991a9a9e63306f172a`. Nessuna pubblicazione. Un collegamento ADB inizialmente offline è tornato operativo prima dell’installazione riuscita.
- **Emulatore API 35 x86_64:** prima schermata atleti con hamburger come primo pulsante, società/sezione/ruolo visibili e nessun overflow orizzontale; nessuna risorsa Plotly caricata nell’elenco. La prima figura visibile carica un solo chunk locale. Modalità iniziale Scorri pagina con grafico statico; swipe nativo scorre il dialogo. Comandi sotto la figura (ordine DOM e verifica visiva). Zoom con swipe ADB cambia l’asse X da circa −0,05–22 a 5,67–17,34 min senza scorrere il dialogo; Back torna a Scorri pagina mantenendo l’intervallo e il test aperto; Ripristina restituisce l’intervallo completo. Vista ampia parte anch’essa in Scorri pagina; Back chiude solo quella vista. Corretto durante il collaudo il cancel sintetico React che prima raggiungeva il dialogo genitore e la cattura touch esplicita durante zoom/pan.
- **Alternativa tabellare:** sul tracciato sintetico Riva Giulia 01/10/2026, 4 serie, conteggi/min/max con unità corretti, 30 righe visibili su 3969 e controlli di paginazione. Le coordinate non sono allineate artificialmente fra serie. Modulo vuoto aperto e chiuso senza salvataggio. Lingua EN: documento lang=en, Open menu, Athletes/Founder; ripristinata IT e medesima società. Catture reali finali di menu, Info, elenco, modulo e grafico ispezionate visivamente e collegate al README.
- **Limiti:** nessun benchmark comparativo del tempo d’avvio totale/Python; misurata la separazione del bundle e osservato il caricamento delle risorse. Non forzati errori di inizializzazione per collaudare Riprova. Nessun nuovo collaudo visivo desktop (immagini desktop conservano provenienza precedente), TalkBack, telefono ARM64, testo di sistema ingrandito o provider reali. Le migliorie di semantica/focus/contrasto/movimento ridotto non costituiscono una certificazione completa di accessibilità. Nessun dato reale modificato né reset di demo esistenti.

## Android TD-99–101 — completamento 21 ottobre 2026

- **Implementazione:** Indietro chiude prima il dialogo (con protezione delle modifiche), poi torna nella cronologia limitata; schede per atleti/test con 20 elementi per pagina, filtri richiudibili e stato conservato tornando dal profilo. Azioni dei moduli persistenti, controlli touch e campi facoltativi raccolti. Ultima società persistita come coppia di ID, verificata contro inventario prima del caricamento.
- **Prove automatiche:** 23 test frontend passati; build TypeScript/Vite riuscita con avviso noto sul bundle >500 KB. Common UI 0.2.4: 10 test Node e 3 test Python core passati durante la consegna; build UI/catalogo e sync:ui --check su Fuorigiri riusciti. Verificatori prodotto 0.10.0 e integrità UI superati. Backend scientifico e formati invariati; suite backend completa non ripetuta per questo intervento UI.
- **Prove sull’emulatore API 35 x86_64:** ripristinata come copia indipendente una società esclusivamente sintetica (20 atleti attivi, 149 test visibili). Filtro Wingate e pagina 21–40/50 mantenuti dopo apertura/chiusura dettaglio e passaggio al profilo atleta; nessuno scorrimento orizzontale negli elenchi provati. Indietro nativo chiude il dettaglio; modulo modificato mostra conferma, consente di continuare e di scartare senza creare record. Salva rimane visibile nel modulo scorrevole. Force-stop/riavvio riapre la medesima società. Non modificati archivi sorgenti o dati reali, nessuna sync avviata.
- **Artefatto:** APK debug ricompilato e installato senza reset dati; SHA-256 `696b347fcdfb53f291574b07a50d94805a876ad827f306ea5302d15ef72deb34`. Catture finali reali di menu, Info, elenco e modulo in docs/screenshots/, ispezionate visivamente il 21 ottobre. Nessuna pubblicazione; il precedente test strumentale runtime rimane distinto da queste prove UI.
- **Limiti:** l’emulatore usa la tastiera Gboard flottante/minimale: apertura IME osservata, ma non qualificata la tastiera completa su telefono. Restano telefono ARM64, TalkBack, tutte le schermate analitiche mobili e provider reali. Nessun nuovo collaudo grafico desktop. Guida riutilizzabile nel common e registro d’adozione in ANDROID_PRATICHE_SUITE.md; consegnata UI 0.2.4 soltanto a Fuorigiri.

## Preparazione Android Studio — 20 ottobre 2026

- **TD-98 navigazione Android:** frontend compilato (TypeScript/Vite; solo avviso bundle >500 KB), 19 test frontend passati, verify_suite_ui conferma common 0.2.2. APK debug ricompilato e installato con successo sull’emulatore API 35 x86_64 senza reset dell’archivio. Verifica visiva delle schermate menu/Info, catture integrali in docs/screenshots/android-menu.png e android-info.png. Verifica su WebView: nessuna sidebar/footer sulla pagina Android ordinaria; menu con società/sei sezioni/Info/lingua; tasto nativo Indietro chiude il menu senza terminare l’app; Gestisci società apre un solo dialogo; Info accessibile senza società e licenza apribile. Provate etichette EN (Open menu/About/Version), poi ripristinata lingua IT. Nessun dato reale creato o cambiato. Il ramo desktop conserva JSX/layout precedenti e common invariato; non eseguito nuovo collaudo visivo desktop o su telefono per questa modifica. Screenshot e documentazione aggiornati.

- **Avvio Android x86_64 corretto e verificato:** emulatore API 35, installazione APK con adb install -r riuscita, nessun reset/dato cancellato. Riprodotto l’errore runtime `cannot locate symbol PyType_GetFlags` e verificato ELF: cryptography originale senza dipendenza libpython, simbolo presente nel runtime. Riparazione DT_NEEDED libpython3.so su entrambe le wheel con LIEF 1.0.0 tramite scripts/repair_android_abi3.py; originali conservati in tmp/android-original-wheels-before-abi3, provenienza e hash prima/dopo in android/wheels/ABI3_REPAIR.json. RECORD/CRC delle due wheel e sezioni .text/architettura/allineamento LOAD 16 KB verificati, hash correnti in SHA256.json. Primo tentativo di rigenerazione RECORD includeva directory: rifiutato da Chaquopy, corretto escludendole prima della build riuscita.
- **Packaging e test effettivi:** aggiunti wheel/manifest agli input Gradle perché prima il cambio binario non invalidava installDebugPythonRequirements. assembleDebug/assembleDebugAndroidTest riusciti. connectedDebugAndroidTest --offline bloccato da una dipendenza UTP non in cache; APK test compilato ed eseguito direttamente con ADB am instrument: **OK (1 test)**. Test nativo prova import numpy, matplotlib, reportlab, pydantic-core, CFFI e cryptography, Fernet encrypt/decrypt, Ed25519 sign/verify, API state e Keystore. Primo test exec senza globals falliva nel contesto Java: corretto con dizionario esplicito. Quattro test Python mobile su Windows passati; verify_versions 0.10.0 e diff --check passati. Test ARM64/telefono, report completi, provider reali e dispositivo 16 KB non eseguiti.
- **Rendering sull’emulatore:** schermata reale Gestisci società visibile; capture verificata in tmp/android-runtime-ready-insets.png. Corretto contenitore WebView con insets di sistema/cutout/tastiera e icone barre leggibili; testi di avvio/errore rispettano le barre. Eccezioni di avvio registrate solo nelle build debug con tag FuorigiriStartup; release mantiene messaggio generico AVVIO-01 senza attribuire sempre la causa alle dipendenze. APK debug aggiornato SHA-256 `4e4f69dd4ad2648e638d2e58a018a6cedc6e9fc6b1a19b5612cc37f7e201a5bf`, presente e installato. Questo è un primo collaudo di avvio, non accettazione dell’intera app. Nessuna pubblicazione.

- **Primo APK debug Windows prodotto:** log utente `:app:assembleDebug` riuscito in 4m28s (47 task), installazione requisiti Python completata per ARM64 e x86_64. Verifica locale successiva: sei wheel presenti e digest coerenti con SHA256.json; `android/app/build/outputs/apk/debug/app-debug.apk` presente, 100544590 byte (~95,9 MiB), SHA-256 `6787f7ba8bb2f78d3cfaca94b65f6ddc1c77c0bf365bc60cb132cdc08de7a4ce`. ZIP/CRC verificati, entrambe le directory native lib/arm64-v8a e lib/x86_64 e assets/index.html presenti. Il warning stripDebugDebugSymbols non ha impedito il packaging; né quel warning né BUILD SUCCESSFUL certificano runtime o pagine 16 KB. ADB locale restituisce lista dispositivi vuota al controllo successivo: installazione e avvio non eseguiti, nessuna cancellazione dati. APK debug locale, nessuna release pubblicata.

- **Guida Fedora consolidata:** controllata la sintassi di 21 blocchi Bash con bash -n, cinque blocchi/script Python con ast.parse e tre configurazioni TOML con tomllib. Verificati 50 link locali nelle guide/indice/istruzioni coinvolti; git diff --check passa. Questi controlli non eseguono download, estrazioni o ricompilazioni Fedora: le sei wheel restano provate dai log/output utente, non da una nuova esecuzione della guida end-to-end.

- Verifica locale successiva: manifest con sei digest valido; check_wheels segnala correttamente tutti e sei i binari assenti, comprese le due CFFI. verify_versions.py conferma 0.10.0 e git diff --check passa. Non eseguita build Android; gate positivo da verificare dopo trasferimento.

- **Sei wheel prodotte sul builder utente:** elenco e SHA-256 ricevuti per pydantic-core 2.41.4, cffi 2.0.0 e cryptography 50.0.2, entrambe le ABI Android API 26. Cryptography x86_64 supera abi3audit strict (baseline 3.13); ARM64 confermata da elenco/checksum, non dal log di audit completo. Hash attesi registrati in android/wheels/SHA256.json; file ancora da trasferire e verificare localmente, nessun import Android/APK. Risolti sul builder selezione errata Rust Fedora e header Python.h mediante staging degli header target nel solo prefisso temporaneo. Gate locale esteso anche a CFFI, versione runtime fissata a 2.0.0.

- **CFFI entrambe le ABI presenti:** elenco/checksum forniti dall’utente confermano ARM64 `cffi-2.0.0-cp313-cp313-android_26_arm64_v8a.whl` (~204 KB), SHA-256 `fbfcfa61d649dc8f894cf71aa1045a63673aeeb74c01b62709e2b54f48730baa`, e x86_64 con checksum invariato `c950835e10bd2dd0bb3ab970503e0c75cfe4364f682bdb7c0a8cfe0be24c8e6e`. Nessun trasferimento/import nell’app ancora verificato; prossima build cryptography 50.0.2 con OpenSSL Android statico e vincolo cffi 2.0.0.
- **CFFI x86_64 riuscito:** log utente conferma `cffi-2.0.0-cp313-cp313-android_26_x86_64.whl`, circa 212,4 kB, auditwheel repair riuscito, SHA-256 dichiarato `c950835e10bd2dd0bb3ab970503e0c75cfe4364f682bdb7c0a8cfe0be24c8e6e`. Risolto mediante hook before-build che copia ffi.h/ffitarget.h/libffi.a nel prefisso target temporaneo. In seguito a un errore di copia `__file__`→`file`, lo script sul builder usa Path.cwd() ed è eseguito dalla radice del builder. Restano ARM64 CFFI, cryptography e test runtime. Le righe sotto descrivono i tentativi precedenti, non lo stato finale di x86_64.
- Terzo tentativo CFFI ancora senza prefisso libffi Android. Analisi dei sorgenti ufficiali cibuildwheel `platforms/android.py`: setup_android_env acquisisce ambiente da android.py e sovrascrive CFLAGS/LDFLAGS/PKG_CONFIG dopo l’ambiente utente; confermato perché flag e wrapper precedenti non arrivavano al build finale. Correzioni precedenti insufficienti, non verificate come riuscite. Proposta hook before-build che installa ffi.h/ffitarget.h/libffi.a nel prefisso target temporaneo già presente nei flag NDK. Nessun nuovo esito di compilazione ancora disponibile.
- Secondo tentativo CFFI fornito dall’utente: header ora risolto tramite CPPFLAGS, compilazione C completata con warning non fatali; linking fallisce `unable to find library -lffi`. Nel comando effettivo manca il prefisso `-L` passato tramite LDFLAGS. Nessuna wheel prodotta. Prossima correzione: wrapper pkg-config per ABI che imposta internamente LIBDIR/PATH senza SYSROOT host, così setup.py riceve include_dirs/library_dirs direttamente; non ancora verificata.
- Prima build CFFI 2.0.0 x86_64 fallita sul builder: `ffi.h` assente dai percorsi di ricerca; comando clang mostrava solo include predefiniti `/usr/include/ffi` e `/usr/include/libffi`, senza prefisso libffi Android. Nessuna wheel CFFI prodotta da quel tentativo. Correzione proposta: CPPFLAGS/CFLAGS/LDFLAGS espliciti sul prefisso della rispettiva ABI e disabilitazione della ricerca pkg-config per evitare fallback host; esito ancora da verificare.
- Builder dell’utente: archivi statici `libffi.a` x86_64 (93 KB) e ARM64 (118 KB) presenti nei due prefissi della ricetta libffi 3.8.0/NDK Android. Confermata la presenza dei file dall’output, non ancora ricevuti checksum, ispezione ELF o test CFFI/runtime. Prossima prova: wheel CFFI 2.0.0 cp313 con pkg-config ristretto al prefisso Android della rispettiva ABI.
- L’utente mostra `libcrypto.a` Android x86_64 e ARM64, circa 12 MB ciascuna, ai percorsi di installazione OpenSSL della ricetta 3.5.9/API 26. Non ancora ricevuti log completi, hash o verifica degli archivi/header. Ispezione sorgenti ufficiali cryptography 50.0.2: richiede anche **cffi >=2.0.0** in build e runtime; catalogo Chaquopy cp313 consultato precedente a 2.0, nessuna wheel Android nel JSON PyPI cffi consultato. Aggiunto gate transitivo CFFI/libffi: non installare la libffi Fedora come binario target e non dichiarare sufficienti le sole quattro wheel iniziali.
- L’utente conferma anche la wheel ARM64 `pydantic_core-2.41.4-cp313-cp313-android_26_arm64_v8a.whl` (circa 1,9 MB), SHA-256 dichiarato `34dbd1267ddd193122c9361333f1e1446990cd09b558899a27dc3c3a8cf579ae`; x86_64 confermato con checksum già registrato. Entrambe presenti nella wheelhouse Fedora. File non ancora trasferiti né importati in Android; gate di packaging/runtime ancora aperto, cryptography non costruita.
- Log fornito dall’utente da Fedora Kinoite 44/Toolbox x86_64: prima wheel **pydantic_core 2.41.4**, CPython 3.13, Android API 26 x86_64 compilata e riparata con auditwheel. File `pydantic_core-2.41.4-cp313-cp313-android_26_x86_64.whl`, circa 2,1 MB; SHA-256 dichiarato dal builder `9d5b792e1d46177e247514adb3cf8fbf803b83656cb6618105e837b4211e1518`. Rust 1.99.1/rustup 1.29.1, Temurin 21.0.12.1 e NDK 27.3.13750724. Durata riportata circa tre minuti; warning di visibilità Rust non fatali. Wheel non ancora trasferita/ispezionata in questa sessione, nessun test di import su Android: checksum da riverificare sul file dopo trasferimento. ARM64 e cryptography restano aperti; nessun APK.
- Tentativo successivo fornito dall’utente: Python host ora trovato; `installDebugPythonRequirements` avvia l’installazione ARM64 e legge il core comune 0.1.2, poi fallisce con **No matching distribution found for pydantic-core==2.41.4**. Confermato il gate reale della wheel Android mancante; il log non prova ancora la risoluzione di cryptography o delle altre librerie native. Emulatore x86_64 non ancora destinatario di un APK; entrambe le ABI richieste dalla build restano da predisporre.
- Primo `:app:assembleDebug --stacktrace` eseguito dall’utente con Gradle 8.13: fallimento in `:app:installDebugPythonRequirements`, **Couldn't find Python 3.13**. Launcher locale rileva 3.14 e 3.11, ambiente di sviluppo 3.14.7; serve installazione host 3.13 affiancata, senza sostituire la venv desktop. Il tentativo non ha ancora raggiunto la risoluzione delle wheel native Android né la compilazione Kotlin/APK.
- Output IDE fornito dall’utente: `:wrapper` e modello Kotlin riusciti con Gradle 9.6; warning deprecazione kotlinOptions non fatale. Verificati wrapper generato e SDK configurato in local.properties; distribuzione wrapper riallineata a 8.13, senza eseguirla con il JBR 25 configurato. JDK 21 ancora da selezionare nell’IDE. Nessuna task assembleDebug eseguita e nessuna prova APK implicata dal BUILD SUCCESSFUL di `:wrapper`.
- Aggiornamento: ADB rileva `emulator-5554` online; `sys.boot_completed=1`, API **35**, ABI **x86_64**. Questo conferma l’avvio di Android, non l’esecuzione di Fuorigiri. Processo emulator rilevato, ma directory SDK non accessibile dalla sessione di verifica; accelerazione non misurata. `build_android.py --check` continua a segnalare quattro wheel native e configurazione SDK/JDK/Gradle mancanti nella sessione; nessun APK prodotto/installato.
- Dopo l’installazione comunicata dall’utente, rilevati processo Studio e JDK incluso 25.0.3; SDK e AVD non presenti nei percorsi predefiniti al controllo. Preferenza aggiornata: emulatore prima del telefono. Per Gradle 8.13 serve JDK 17/21 separato; accelerazione non ancora verificabile perché manca emulator.exe nel percorso SDK standard.
- Richiesta di riprendere il collaudo Android locale; ispezione non distruttiva di configurazione e toolchain. Nessuna installazione Studio rilevata nei percorsi standard o nei programmi registrati, nessun processo studio64 rilevato; SDK standard assente. Presente adb separato. Il controllo build segnala SDK/JDK/Gradle non configurati e quattro wheel native Android verificate mancanti.
- `pytest tests/test_mobile_runtime.py -q`: **4 passati**; `scripts/verify_core.py`: core 0.1.2 integro e installato. Sono prove del bridge su Windows, non Android. Nessun download/installazione toolchain, build Gradle, APK o test su telefono/emulatore eseguito. Le wheel crypto richieste non risultano nel catalogo Chaquopy consultato; il loro gate rimane aperto.

## 20 ottobre: estrazione del runtime Python common

Portachiavi OS, trasporti cartella/WebDAV, lock d'istanza e finestra Qt derivati da `cycling-suite-core` 0.1.2, con adattatori prodotto e nomi di vault/canali/lock conservati. **201 test backend superati, 1 saltato; 19 test frontend superati**, build TypeScript/Vite e verificatori autonomi UI/core riusciti. Il common verifica anche la derivazione nei due consumatori. Smoke del launcher desktop dai sorgenti su nuovo archivio sintetico `.local/qa-common-desktop-20261020`: import, logo e backend HTTP verificati. L'estrazione non modifica il motore scientifico o archivi reali.

Predisposta l'inclusione della wheel in Chaquopy e nella wheelhouse Flatpak; build e qualificazione Android/Linux restano rinviate. Nessun nuovo installer Fuorigiri prodotto da questo intervento. Restano i warning noti Starlette/httpx e chunk Plotly grande; il test di corruzione ZIP genera deliberatamente un nome duplicato. Un warning della cache pytest su Windows non ha impedito la regressione. [Consegna e compatibilità](CORE_CONDIVISO.md).

## Galleria README — 20 ottobre 2026

- Sette JPEG acquisite dalla GUI compilata corrente (0.10.0, UI comune 0.2.2), con sole persone e misure sintetiche: squadra, protocolli, incrementale, Wingate 30 s, aggregati stagionali, crescita/maturazione, report/esportazioni. Catture reali del browser locale e ispezione visiva delle immagini; tracciati e curva HV effettivamente disegnati, nessun token o credenziale nelle inquadrature.
- Nessuna rigenerazione di demo esistenti, nessun ricalcolo dei risultati o scambio cloud avviato. Provenienza e istruzioni di rinnovo in `screenshots/README.md`, regola di manutenzione in AGENTS.md. Aggiornamento solo documentale: nessuna build applicativa nuova o suite funzionale ripetuta.
- Verificati i sette JPEG (504.296 byte complessivi), 308 collegamenti Markdown locali senza destinazioni mancanti e `git diff --check`. Server QA arrestati e scheda browser chiusa al termine.

## Riallineamento 0.10.0 — 20 ottobre 2026

- `verify_versions.py` riuscito per Python, frontend e lockfile, Android (versionName 0.10.0 / versionCode 1000), installer Windows e prima voce AppStream. Verificato il rifiuto di una versione frontend discordante su una copia temporanea dei soli metadati.
- API FastAPI e pannello legale verificati a 0.10.0 tramite TestClient; GUI compilata aperta su archivio QA nuovo: barra laterale mostra 0.10.0. Smoke desktop dai sorgenti riuscito.
- 13 test cloud e 19 test frontend passati; build TypeScript/Vite riuscita, compilazione Python e `git diff --check` riusciti. Rimangono warning Starlette/httpx e chunk Plotly già noti. Nessuna modifica a metodi scientifici o formati dei dati; non ripetuta l’intera suite per questo riallineamento.
- Changelog raggruppato sotto 0.10.0, con precedenti versioni e prove storiche conservate. Controllo metadati richiamato prima di build desktop/Android e preparazione release; nomi APK letti da pyproject. Nessun EXE/installer/Flatpak/APK prodotto o pubblicato e nessun tag Git creato da questa operazione.

## Sync v2, backup v3 e separazione società — 19 ottobre 2026

- Suite completa: **200 passati, 1 saltato** (permessi symlink Windows). Dopo l’ultimo affinamento della cache per ricezione interrotta: **8 test v2 mirati passati**, compreso il nuovo caso di ripresa dall’ultimo blocco mancante. Warning Starlette/httpx preesistente; warning ZIP duplicato prodotto intenzionalmente dal test di rifiuto.
- Verificati firme originali e firma dell’involucro v2, rifiuto di pagine contraffatte da un visualizzatore, deduplicazione tra revisioni, ricezione mancante/ritentata e corruzione con verifica completa, convivenza v1/v2, conflitti e revoca. Interruzione durante la pubblicazione e durante la ricezione: riuso dei blocchi già validati, senza cancellare storico.
- Backup v3: export/verifica/ripristino senza letture integrali degli allegati, rifiuto di corruzione/duplicati/percorsi estranei/oggetti storici mancanti, lettura legacy e recupero originale. Separazione legacy con dipendenze, tutte le revisioni, file propri, nuovi accessi, impronta obsoleta rifiutata, ambiguità bloccate e rollback in caso di errore del registro.
- Prova effettiva `verify_storage_v2.py --large` su `.local/qa-streaming-101mb-20261019`: payload sintetico non comprimibile **101.000.000 byte**, ZIP **101.033.574 byte**, ripristino indipendente e SHA-256 verificati. Picco allocazioni Python durante l’export **4.280.330 byte**, circa **8,92 s** per export/verifica/ripristino su questo PC; non comprende tutta la memoria nativa/OS e non è un benchmark dei limiti massimi. Riepilogo locale `verification.json` nel corpus QA.
- **19 test frontend passati**, build TypeScript/Vite riuscita e UI comune verificata; rimane il noto chunk Plotly. Smoke desktop dai sorgenti riuscito; compilazione sintattica e controllo diff riusciti.
- GUI su archivio QA dedicato: analisi di due società legacy → estrazione indipendente → apertura della società corretta; attivazione v2 subordinata al controllo dei dispositivi aggiornati; scambio locale v2 completato; salvataggio diretto del backup v3 e ispezione via CLI. Screenshot `output/sync-v2-verifica.png` e `output/backup-v3-verifica.png`. Archivi operativi e demo dell’utente non migrati né rigenerati.
- Limiti: inventario remoto ancora completo, nessuna compattazione/garbage collection, record canonici ancora nel DB locale; legacy ambigui richiedono correzione prima dell’estrazione. Non collaudati volumi 64/256 GB, un milione di file, account cloud reali, Windows pulito o backup nativi Android grandi. Nessun installer ricompilato e nessuna build Fedora/Android avviata. [Contratto e uso](SYNC_V2_E_BACKUP.md).

## Riordino documentazione — 19 ottobre 2026

- Verificati 280 collegamenti locali in 33 documenti (README, AGENTS, architettura, changelog e documentazione): nessuna destinazione mancante prima delle sole aggiunte a questo registro e ai requisiti. Nessun riferimento Markdown ai nomi delle tre guide rinominate rimasto. `git diff --check` riuscito.
- Modifica documentale: non ripetute build o prove applicative; valgono le verifiche dei sorgenti riportate sotto.

## Profilo da test e corpus maturazione — 19 ottobre 2026

- 25 test mirati passati (`test_maturation.py`, `test_demo_suite.py`): riferimenti numerici maschili/femminili, indici opzionali, inclusione degli snapshot nel visualizzatore e nei backup, manifest e ripristino.
- 19 test frontend passati; build TypeScript/Vite riuscita. Rimane il noto avviso sulle dimensioni Plotly.
- GUI verificata su archivio QA nuovo: dettaglio Wingate → «Apri profilo atleta» → Elena Moretti, anche se archiviata. Corpus ridotto generato fino al riepilogo finale in `.local/qa-profile-maturity-20261019`: 14 atleti, 102 rilevazioni, 36 test e 8 snapshot maturativi. Nessun archivio demo dell’utente rigenerato; nessun installer aggiornato.

## Attuazione TD-83–97 — 19 ottobre 2026

- **180 test backend passati, 1 saltato** (permessi symlink Windows), warning Starlette/httpx preesistente. Nuovi 24 casi maturazione: oracoli Moore/Mirwald, null/zero/domini/qualità, HV e picco cubico noto, stabilità adulta, API e revisione concorrente, snapshot conservati, CSV/MD/PDF, sync firmata verso visualizzatore e ripristino indipendente effettivo. Verifica dell'accesso cartella vincolata alla destinazione.
- **19 test Node passati**, inclusa conversione mm:ss e arrotondamento al minuto; TypeScript/Vite e artefatto UI comune verificati. Rimane l'avviso del chunk Plotly (circa 5,3 MB minificati).
- GUI compilata verificata sul nuovo corpus QA, senza modificare la demo dell'utente: profilo crescita con PHV atteso 8,96 cm/anno, scelta snapshot, dettaglio incrementale con soglie/zone, X persistente fino al glossario, editor dedicato, 23:45 → 1425 s e annullamento esplicito senza salvataggio. Verificati anche editor custom e Wingate 15 s (60 s = 1:00), pannello licenza e Drive non configurato con spiegazione e comando disabilitato. Nessun consenso o account reale usato.
- Report sintetico atleta con maturazione: PDF di tre pagine generato, renderizzato con Poppler e ispezionato; tabelle, grafico HV, provenienza e footer societario. Corretto salto della sezione e precisione APHV. Artifact `output/pdf/crescita-maturazione-esempio.pdf`, Markdown corrispondente e screenshot `output/crescita-maturazione-gui.png`, `output/dettaglio-soglie-zone.png`, `output/dettaglio-chiusura-persistente.png`.
- Smoke desktop dai sorgenti riuscito su archivio QA nuovo. Nessun installer ricompilato o account cloud reale collegato. Validazione scientifica esterna, revisione giuridica e build/collaudo Fedora/Android rimangono distinti. [Metodi e limiti](MATURAZIONE.md).

## Revisione generale e sincronizzazione per società — 19 ottobre 2026

- **156 test backend passati, 1 saltato** per permessi symlink Windows; warning Starlette/httpx preesistente. Il gruppo mirato sync/backup/provider passa 43 test.
- **18 test Node passati**, TypeScript/Vite e verifica dell'artefatto UI comune riusciti. Rimane il chunk Plotly di circa 5,3 MB minificati. `pip check`, compilazione sintattica e smoke desktop dai sorgenti riusciti.
- Verificati isolamento di due società, rifiuto di archivi multi-società prima dell'accesso al trasporto, firme/record estranei, download incrementale e verifica completa, simmetria dei limiti ZIP. Non provati account cloud reali o installer aggiornati su PC pulito.
- Misure sintetiche: archivio Aurora 150 test, circa 6,9 MB locali e 7,9 MB di pacchetti v1; registrazione di 63 minuti a 1 Hz circa 0,81 MB per revisione nel canale. Modelli a 5 Hz e revisioni ripetute inclusi nella [valutazione dimensionale](SYNC_DIMENSIONI_E_SCALABILITA.md).
- Correzioni, prove UI, limiti residui e sequenza del lavoro nella [revisione completa](archivio/REVISIONE_GENERALE_2026-10-19.md).

## Interpolazione lattato v2 — 18 ottobre 2026

- Suite backend: **147 passati, 1 saltato** (symlink Windows); warning Starlette/httpx preesistente. Nuovi 19 casi: oracolo 220 W/155 bpm a 4 mmol/L, livelli decimali, mancanze FC/peso, copertura/step parziali/rampa, ambiguità, validazione livelli, associazione CSV/manuale, API, storici, CSV/MD, revisioni e cache del vecchio renderer.
- **12 test Node passati**, TypeScript/Vite compilato con avviso dimensione chunk Plotly. GUI verificata sul solo archivio QA separato: livelli 2/3/3.5/4/6 nel modulo di correzione, curve e tabella con W/W/kg/FC; 6 mmol/L indisponibile fuori intervallo. Nessuna modifica dei dati nell'archivio demo principale.
- PDF sintetico generato, 4 pagine renderizzate con Poppler e ispezionate; verificati titolo atleta, valori, descrizione metodo, grafico e footer. Artifact: `output/pdf/lattato-livelli-esempio.pdf`, screenshot `output/lattato-livelli-gui.png`.
- Android `build_android.py --check`: prerequisiti mancanti (wheel pydantic_core/cryptography verificate per arm64/x86_64, SDK 35, JDK, Gradle). Sorgenti Kotlin presenti; nessun APK compilato o testato, nessuna build Linux/Android avviata.

## Grafico unico e confronto di serie — 18 ottobre 2026

- **12 test Node passati**: sovrapposizione con assi indipendenti, selezione dei canali, lattato puntuale nello stesso grafico, lacune e zero; raggruppamento di più anni nella stessa serie, esclusione delle serie senza valori, metodi/protocolli/origini separati, selezione iniziale e limite quattro, categorie globali ordinate e colori stabili.
- Build TypeScript/Vite riuscita, con il consueto avviso dimensione del chunk Plotly. Nessuna modifica a formule, aggregazioni backend o schema dati in questo intervento; la precedente suite backend resta documentata sotto.
- GUI verificata sul corpus completo: MAP mostra inizialmente 1 delle 6 serie utili, anziché legende per tutti i protocolli; quattro serie ALL/ESO selezionabili, ulteriori scelte disabilitate e avviso di confronto descrittivo visibile. Incrementale Riva Giulia 15/03/2026 mostra potenza/FC/cadenza e lattato nello stesso grafico, su assi colorati indipendenti.
- Screenshot: `output/test-linee-sovrapposte.png`, `output/storico-serie-selezionate.png`. Archivi demo non rigenerati, installer non ricompilati.

## Grafici nel dettaglio test — 18 ottobre 2026

- **128 test backend passati, 1 saltato** (permessi symlink Windows), warning Starlette/httpx preesistente. Nuove regressioni su CSV con canali opzionali/null/zero, valori non validi, unità reali dei campi FIT e recupero campioni senza alterare la revisione del record.
- **5 test Node** del modello grafico: scale indipendenti, canali visibili, nessuna curva da riepiloghi, tempi dei prelievi, lacune e target allineato. Build TypeScript/Vite riuscita; rimane l'avviso dimensione chunk Plotly.
- GUI compilata verificata su corpus completo esistente: filtro 22 tracciati nella società Aurora, incrementale Riva Giulia del 15/03/2026 con tre canali e lattato, Wingate 15 s Moretti Elena con tre canali; custom manuale con spiegazione esplicita. Nessun test demo modificato o rigenerato. Screenshot locale `output/test-tracciato-canali.png`.
- Nessun installer ricompilato; canali aggiuntivi non conservati dal vecchio decoder richiedono nuova importazione del file originale.

## Reset e rigenerazione delle demo — 18 ottobre 2026

- Suite completa: **122 test passati, 1 saltato**, warning Starlette/httpx preesistente. Il test saltato riguarda i link simbolici, non creabili con i permessi Windows di questa sessione.
- Verificati conservazione integrale della vecchia cartella, più reset sullo stesso nome, percorsi rifiutati, archivi principali/repliche aperti, nessun accesso ai riferimenti esterni e retry limitato per handle transitori Windows. Il corpus ridotto viene rigenerato sullo stesso percorso con nuove identità e gli stessi conteggi.
- Collaudo CLI reale su una cartella QA nuova: creazione demo minima di 4 test, `demo.py --reset`, rifiuto di `demo_suite.py --reset` e serve.py con archivio bloccato, quindi sostituzione con corpus ridotto (6 atleti / 36 test) ed export ZIP riuscito. Sentinella e directory precedenti conservate nei backup; `.local/ui-test` dell’utente non svuotata durante il collaudo.
- Guida principale riordinata con comandi completi, distinzione demo minima/completa, recupero dei backup raw al percorso originale, nuove schede browser, repliche e ZIP portabili. Nessun installer ricompilato.

## Estrazione UI comune — sorgenti successivi alla 0.8

Repository autonoma UI 0.1.0 installata e compilata da sola, 4 test Node passati; catalogo browser verificato con nome Ammiraglia e logo societario fisso. Fuorigiri usa l’artefatto in vendor: TypeScript/Vite riusciti e 117 test backend passati. GUI Fuorigiri verificata per ordinamento MAP e apertura modulo atleta su corpus fittizio, senza salvataggi. Checksum, sorgenti/licenza e immagine originale verificati da scripts/verify_suite_ui.py. Non ricompilati gli installer; nessuna CI remota o build Linux/Android. [Dettagli](SUITE_CONDIVISA.md).

## Verifica 0.8 — 18 ottobre 2026

- **117 test passati** su Windows, inclusi protocollo custom, tipi/limiti, null/zero/false, revisioni e conflitto 409, confronti, PDF/MD/CSV, corpus ridotto con due società/repliche, casi FIT invalidi, oracoli numerici indipendenti e ripristino di backup con campi custom. Rimane il warning preesistente Starlette/httpx.
- TypeScript e build Vite riusciti; rimane l’avviso sulle dimensioni del chunk Plotly.
- Corpus completo generato in `.local/demo-fuorigiri-completo`: 24 atleti, 216 misure, 192 test (190 non eliminati), 12 versioni di protocollo per ciascuna delle due società. Distribuzione portabile separata con due backup e fixture, senza identità private né configurazione di percorsi assoluti. [Matrice e istruzioni](DATI_SINTETICI.md).
- GUI browser verificata sul corpus sintetico: catalogo e creazione custom con campi tipizzati; nuova prova manuale custom con anteprima 900 W, zero e No distinti dai mancanti; FIT Wingate con scelta sessione, offset 60 s, zoom e calcolo; storico custom con etichette, medie e mediane. Anteprime non archiviate per mantenere i conteggi del corpus.
- Due PDF sintetici (custom: 1 pagina; Wingate: 2 pagine) generati, renderizzati e ispezionati, incluse tabelle, grafico e footer con logo/attribuzione; ZIP Markdown corrispondenti generati. Nessuna analisi di persone reali.
- Corretto un difetto scoperto dal corpus: i backup prodotti dopo sincronizzazione contengono `sync_audit`; il validatore ora ne ammette soltanto la struttura nota. Il ripristino ricostruisce l’archivio e avvia un nuovo registro locale del dispositivo. Verificati sia ripristino valido sia rifiuto di una struttura audit estranea.
- Bundle Windows 0.8 ricompilato; smoke test finale con exit code 0 (import, logo, backend HTTP). Verificata la presenza del codice finale per le anteprime di revisione e l’identità SHA256 delle risorse frontend incluse rispetto alla build GUI verificata. Non è una prova su PC pulito.
- Restano distinti: qualificazione scientifica esterna, device reali e provider/account cloud reali, Windows pulito, Fedora e APK Android. Le nuove funzioni non costituiscono quei collaudi.

## Verifica 0.7

Suite completa: **102 test passati**; TypeScript e build Vite completati. Eseguibile Windows ricompilato e smoke test locale completato con exit code 0 (import, branding e backend HTTP); non è una prova su PC pulito.

Aggiunti test per Sprint/Wingate, integrali, finestre, lacune/offset/esclusioni, provenienza, storico ed export/reimport esteso, revisioni e report. Adapter cloud verificati con risposte API simulate: PKCE, stato monouso, rinnovo, ruoli, duplicati, download senza Bearer e contratto relay. Il CSV privato fornito supera la validazione (38 prove, 0 errori) in archivio temporaneo rimosso; non è incluso nella distribuzione. GUI verificata con dati sintetici; report sintetici renderizzati e ispezionati. Registrazioni e account reali, Kotlin/APK, Fedora e PC Windows pulito restano da collaudare.

## Software 0.6 / architettura 1.4 — 18 ottobre 2026

- Bundle finale `dist/Fuorigiri/Fuorigiri.exe` compilato; smoke test con PATH limitato a Windows/System32 riuscito (codice 0, versione 0.6.0). Import, logo, icona, backend HTTP e portachiavi importabile verificati. Risorse PE: sette immagini icona e un gruppo icone.
- Installer `dist/release/Fuorigiri-0.6.0-windows-x64-setup.exe` compilato con Inno Setup 6.7.3. Installazione per utente in `.local/installed-06-qa`, senza installazione precedente registrata: codice 0. Eseguibile installato identico al bundle per SHA256; smoke test con PATH senza Python/Node riuscito. Disinstallazione tramite il suo uninstaller: codice 0, binari e chiave di disinstallazione rimossi, archivio SQLite e sentinella sintetica separati conservati. Non è una prova su un Windows pulito o un collaudo di aggiornamento da ogni versione precedente.
- Su richiesta esplicita dell’utente, consegna Windows + sorgenti; build Linux/Android rimandate. Nessun commit/push, run CI remoto o pubblicazione eseguiti. Installer Fuorigiri non firmato Authenticode; la firma del compilatore Inno Setup scaricato è stata verificata separatamente e non attribuita al prodotto.
- **74 test passati** su Windows. Rispetto alla 0.5: WebDAV con server loopback, timeout dopo commit, idempotenza, conflitti, viewer con server in sola lettura, integrità dei PUT, inventario esterno respinto, URL/autenticazione, collisioni immutabili, nessun rollback dei controlli firmati, versioni divergenti, rotazione e ripresa dopo interruzione, password escluse dal JSON, accessi viewer e conservazione della cartella precedente. Regressioni anche contro riuso di un elenco accessi firmato come revoche e pacchetti con forma JSON errata.
- Contratto mobile: creazione e riapertura di società/atleta/protocollo/test, PDF/MD/CSV/backup, upload multipart FIT e viewer senza scrittura attraverso il backend ASGI reale. **Eseguito su PC**, non su Android. Lock OS della doppia apertura e smoke desktop coperti.
- TypeScript e build Vite riusciti. Resta l’avviso sul chunk Plotly grande; non è un errore di compilazione. JSON/XML di packaging e manifest Android e collegamenti locali nuovi verificati.
- GUI browser su archivio sintetico `.local/qa-06-gui`: prima pubblicazione 2 eventi, ripetizione 0, configurazione conservata, modulo WebDAV, rifiuto URL HTTP e blocco di Sincronizza ora con impostazioni non salvate. Nessun account cloud reale o dato operativo utilizzato.
- Windows Credential Manager realmente verificato, con scrittura/lettura/rimozione della sola credenziale fittizia `Fuorigiri.QA/synthetic-06` nella sessione utente. La prima prova nella sandbox non aveva una sessione di logon utilizzabile; la prova nella sessione utente è riuscita. Nessun altro segreto letto.
- Icona SVG renderizzata in PNG/ICO e ispezionata; logo originale della società preservato. DLL VC runtime presenti nel bundle insieme a Python/Qt; verifica su Windows pulito ancora necessaria.
- Android: `scripts/build_android.py --check` **fallisce correttamente**, elencando wheel native Pydantic Core/Cryptography per le due ABI, SDK 35, JDK completo e Gradle mancanti. Verificati gli indici ufficiali Chaquopy: nessuna wheel Pydantic Core e Cryptography cp313 solo 42.0.8, non usata come sostituto della versione richiesta. Sorgente shell/bridge presente, APK e test strumentali non eseguiti. Nessun Linux/WSL/toolchain Android disponibile qui.
- Collaudi ancora aperti: Nextcloud con due account e tre dispositivi, Fedora/Wayland/X11/Secret Service, Windows pulito, firma prodotto, inventario completo licenze di distribuzione, compatibilità Android delle dipendenze native e pagine 16 KB. Il lavoro non certifica questi ambienti.

## Software 0.5 / architettura 1.3 — 17 ottobre 2026

- **59 test passati** su Windows: dodici nuovi casi per copertura 95% senza arrotondamento, aderenza distinta, interpolazione, esclusioni sovrapposte, marker/FC al termine, canali mancanti, rampa, copia schema 2 e migrazione 3 senza riscrittura, versioni immutabili, lattato/Dmax, unità/finestre gas, ripetibilità e incertezza, sessioni FIT/duplicati, ambiti dei report e API con allegati/revisioni gas conservati.
- TypeScript e Vite compilati; persiste l’avviso sul bundle Plotly grande. Audit nomi e collegamenti locali riuscito; nessun nome di prodotto precedente reintrodotto.
- Verifica conclusiva del bundle Windows il 18 ottobre 2026: build finale riuscita; `dist/Fuorigiri/Fuorigiri.exe --smoke-test --data .local/smoke-fuorigiri-05-final` concluso con codice 0. Import, logo e backend HTTP verificati; marker con versione 0.5.0 presente nell’archivio isolato. La GUI 0.5 è stata verificata nel browser come descritto sotto; non è stato ripetuto il collaudo completo della finestra Qt.
- GUI browser su archivi sintetici isolati: anteprima società 4 atleti/8 test/8 misure; filtro Allievi/2026 2 atleti/2 test/2 misure; dettaglio con aderenza, curve lattato, gas ed etichette. Pubblicazione di preset FC 20 s, calcolo anteprima e archiviazione di una revisione motivata confermati nel dettaglio. Nessun dato reale importato.
- Cinque PDF sintetici prodotti e renderizzati: società 15 pagine, gruppo 8, gruppo/2026 5, atleta 3, test specialistico 5. Controllati tavole di tutte le pagine, pagine rappresentative a maggiore risoluzione, footer/attribuzione, grafici e testi. Quattro ZIP Markdown con immagini e manifest. Compattati i dettagli e accorpate le avvertenze comuni.
- Collaudi non eseguiti: Fedora/PC pulito, corpus FIT reali autorizzati per tutte le versioni degli esportatori, formati gas proprietari e validazione fisiologica/laboratoristica dei risultati. I breakpoint ventilatori sono suggerimenti da revisione, VO2max è una verifica dichiarata con evidenze; nessuna certificazione clinica implicita.

## Software 0.4.1 / specifica 1.0 — 17 ottobre 2026

- **47 test passati** su Windows: inclusi riconoscimento della directory dati precedente senza spostamenti e scambio nel canale cifrato preesistente con gli stessi eventi/chiavi; due canali per la stessa chiave producono errore esplicito.
- Bundle `dist/Fuorigiri/Fuorigiri.exe` compilato; smoke test con codice di uscita 0 e marker 0.4.1 in `.local/smoke-fuorigiri-041`: dipendenze, logo e backend HTTP verificati. Nuove specifiche ed esempio JSON inclusi nella distribuzione. La GUI Qt completa della 0.4.1 e Fedora non sono stati nuovamente collaudati in questa revisione.
- TypeScript e Vite compilati; persiste l’avviso sul bundle Plotly grande. Audit dei file mantenuti: nessuna occorrenza del nome storico, collegamenti locali delle nuove specifiche e JSON di esempio validi. Le scritture separate del marchio ritirato sono limitate al riconoscimento dei percorsi su disco.
- La specifica dei metodi documenta convenzioni confermate, risultati attesi e scostamenti del motore attuale: **non equivale al superamento dei casi futuri** né a validazione fisiologica. Nessun algoritmo incrementale o risultato storico modificato. Android documentato, non implementato o collaudato.
- I nomi negli esempi storici di eseguibile/percorso sottostanti sono stati normalizzati in Fuorigiri per richiesta dell’utente: non descrivono una seconda esecuzione retroattiva delle vecchie verifiche.

## Software 0.4 — 17 ottobre 2026

- 45 test automatici passati su Windows: 13 nuovi casi di recupero/ruoli, inclusi tre modi di ripristino, schema precedente, più società, integrità, file di recupero precedente con directory accessi più recente, password/società errate, percorsi non consentiti, destinazione occupata, rollback, bootstrap, cambio ruolo e revoche con preservazione degli eventi esatti.
- TypeScript e Vite compilati. GUI browser con dati sintetici: creazione società/apertura automatica, collegamento invito visualizzatore, onboarding senza record e prima sincronizzazione locale con acquisizione di un atleta; anteprima ZIP e ripristino di consultazione, ruolo esplicito nel contesto.
- I flussi completi di recupero fondatore, copia indipendente, promozione/demozione e revoca sono verificati dalle API/prove automatiche; la GUI è stata provata sui percorsi sopra, non su ogni combinazione di piattaforma e client cloud.
- Nessun dato operativo o identità reale importati. Archivi e credenziali delle fixture isolati sotto .local/ e tmp/, esclusi dalla repository. Nessuna validazione fisiologica nuova.
- Pacchetto Windows 0.4 ricompilato: smoke test con import, logo e backend HTTP riuscito in .local/smoke-04; modulo cycling_test.recovery incluso nel bundle. Finestra Qt realmente aperta, versione 0.4 e tre percorsi verificati; apertura della scheda Ripristina da backup controllata. Nessun archivio creato nel profilo predefinito durante questa verifica; finestra poi chiusa. Flussi completi sui dati verificati nelle istanze browser/API isolate.


## Software 0.3 — 17 ottobre 2026

- **32 test passati** su Windows, inclusi sei nuovi casi: protocollo senza step, creazione/revisione di test manuali, gruppo figlio senza nome, CSV obbligatori/facoltativi, media diversa dalla mediana e decodifica/analisi di quattro FIT basati sugli ERG originali.
- TypeScript e build Vite completati. Rimane l'avviso di bundle Plotly grande; non è un errore di compilazione.
- GUI nel browser, su archivio isolato sintetico: aggregazione per categoria e media, etichette leggibili, creazione scheda senza step, inserimento di MAP 230 W/peso 50 kg senza FIT e risultato dichiarato 4,6 W/kg.
- PDF di test e aggregato renderizzati e controllati visivamente: stile blu, tabelle leggibili, logo/credito fisso nel footer di ogni pagina. Report di esempio con tracciato su tre pagine e aggregato su una; il numero di pagine varia con contenuti e zone.
- Nessuna importazione dei dati personali originali. I quattro FIT sono simulazioni e non certificano gli esportatori reali.
- Bundle Windows ricompilato: `dist/Fuorigiri/Fuorigiri.exe --smoke-test --data .local/smoke-03` riuscito, con marker Fuorigiri 0.3.0. Apertura effettiva della finestra Qt verificata: titolo Fuorigiri Performance Lab, nuovo selettore e asset del prodotto presenti. Le operazioni complete sui dati e lo scroll sono stati provati nella GUI browser; la finestra Qt è stata aperta e chiusa sull'archivio predefinito vuoto, senza aggiungere dati.
- GUI finale: creazione di Allievi/2027 senza nome; anteprima del contratto CSV antropometria; dettaglio FIT scorso fino al fondo senza trasparenze nel pannello, sfondo bianco e `body` con overflow bloccato. Archivi runtime isolati, nessun dato operativo alterato.
- La distribuzione comprende anche `examples/protocols` ed `examples/synthetic` con i quattro FIT/CSV e manifest, così possono essere provati senza la repository sorgente.

Le prove della 0.2 riportate sotto sono cronologia; eventuali riferimenti a dodici test riguardano la vecchia demo. Il nuovo generatore crea quattro esecuzioni corrispondenti ai file in `examples/synthetic`.

## Software 0.2 — verifiche precedenti

17 ottobre 2026. Ambiente Windows, Python 3.14 e Node.js 24. I risultati descrivono prove locali su dati sintetici; non costituiscono validazione fisiologica del metodo. Per ripeterle: [guida completa, inclusa GUI](TESTARE_IL_PROGETTO.md).

## Automatiche

`python -m pytest -q`: **26 test passati**. Copertura dei comportamenti principali:

- avvio completo del backend HTTP senza stdout/stderr, come nel bundle Windows senza console;
- ERG forniti, salti e rampe, validazione dei punti e confini degli step;
- ultimo step completo, interpolazione distinta, dati mancanti, campionamento irregolare e recupero;
- FIT sintetico con CRC e rifiuto dei file alterati;
- aggiornamenti concorrenti, revisioni di test con campioni e risultati storici;
- preset zone ai confini esatti, schemi a 3/5/7 zone e tempi non classificati;
- CSV con anteprima, commit atomico, blocco del lotto errato, ID e reimportazioni;
- storico per atleta rispetto a tutti i test, crescita descrittiva e confronto appaiato;
- report MD/PDF, lingua dei titoli, logo incluso e attribuzione fissa; rifiuto di un campo logo nell'anagrafica società;
- workspace separati, visualizzatore bloccato, inviti cifrati, verifica delle firme anche con pacchetto alterato usando la chiave di lettura;
- conflitto fra due admin e convergenza dopo risoluzione.

È presente un avviso di deprecazione dell'integrazione Starlette/httpx; i test passano. Non è un errore del metodo o dei dati.

Controllo TypeScript `tsc -b`: riuscito. Build Vite di produzione: riuscita. Asset PNG copiato in `frontend/dist/branding/progetto-ciclismo.png`; bundle JavaScript circa 5,17 MB prima della compressione. Avviso Vite sul chunk grande dovuto soprattutto a Plotly, da ottimizzare nel consolidamento.

## Interfaccia

Verificata nel browser locale su archivio sintetico separato `.local/qa-02`:

- elenco atleti, pulsanti di ordinamento, profilo e grafici della MAP/peso/statura;
- logo leggibile nel footer e dicitura fissa richiesta;
- categoria Allievi con sottogruppo Stagione 2026;
- pagina storici: 4 atleti e 4 test selezionati nel default, 12 test nella modalità Tutti i test;
- pannello copertura, variazioni antropometriche e disponibilità del confronto appaiato;
- cambio IT → EN → IT, con branding invariato;
- apertura Nuovo test e aggiunta di due zone FC: 7 zone FC e 5 potenza, con 12 campi nome zona complessivi.

Durante il collaudo è stato individuato un ridimensionamento Plotly su un elemento non più visualizzato: gestione aggiornata con stato del rendering, controllo di visibilità e pulizia dell'observer. La navigazione non deve generare errori di resize quando i grafici vengono rimossi.

I test API coprono salvataggio e revisione; la checklist GUI completa rimane necessaria per ogni rilascio e sistema operativo. Non tutte le righe della guida sono state eseguite manualmente in questa sessione.

## Report

Report sintetico con logo, attribuzione e zone renderizzato in tre pagine PNG e ispezionato visivamente: tabelle, grafico, crediti e cambi pagina leggibili. Verificati anche export Markdown con asset e manifest e generazione del report storico via API. I PDF di prova sono sotto `tmp/qa/`, esclusi dalla repository.

## Limiti del collaudo

Nessun FIT reale di GoldenCheetah/MyWhoosh/Zwift fornito. Nessuna prova su Fedora, PC Windows pulito o client cloud reale eseguita. Lo scambio testato fra directory locali non certifica affidabilità di Google Drive/Dropbox o consegna su due PC reali.

La regola provvisoria di step completo richiede durata prevista e almeno 95% di copertura potenza, senza controllo dell'aderenza al target. I riferimenti per le zone derivano dagli input/metodi dichiarati; nessun coefficiente fisiologico universale viene validato dai test software.

## Avvio senza finestra e risorse

Smoke test della shell da sorgente eseguito con `--smoke-test --data .local/smoke-02-source`: riuscito. Verificato che il logo originale, quello in repository e quello nel frontend compilato siano identici byte per byte. Collegamenti locali e blocchi Markdown della documentazione verificati.

## Correzioni del packaging Windows

Individuata e rimossa dalla ricerca delle dipendenze una DLL ICU di Poppler introdotta dal PATH degli strumenti. La build usa ora un PATH isolato per il solo sottoprocesso. Lo smoke test è stato esteso: importa Qt WebEngine, controlla il logo, avvia il backend e verifica `/health`. Logging desktop indipendente dalla console e diagnostica locale in `server.log`; avvio del backend fallito segnalato esplicitamente. Il test automatico senza stdout/stderr passa.

## Esito finale del bundle Windows

Build pulita riuscita con PATH isolato. Eseguito `Fuorigiri.exe --smoke-test` sul bundle finale: import, logo e backend HTTP verificati, marker in `.local/smoke-02-final/smoke-ok.txt`. Avviata anche la finestra sul desktop Windows: interfaccia caricata e footer con logo/attribuzione verificati visivamente e tramite accessibilità. Non equivale ancora al collaudo su un PC pulito.


## 20 ottobre 2026 — UI comune 0.2.2

Riallineamento alla UI corrente di Fuorigiri e dipendenza condivisa da common. Verificati 8 test della libreria, 5 test frontend Ammiraglia e 19 frontend Fuorigiri; build TypeScript/Vite dei due prodotti e del catalogo, controlli standalone dei tarball e allineamento versione/impronta sorgenti comune. Browser su archivi QA nuovi e sintetici: shell/onboarding di entrambe, società/dashboard/liste e scarto protetto Ammiraglia, finestra licenza Fuorigiri. Catalogo a larghezza ridotta: focus iniziale, Esc con modifiche, continua a modificare, blocco della chiusura durante salvataggio. Resta il warning sul grande bundle Plotly. Nessun nuovo installer, prova Qt su PC pulito, collaudo completo di tutte le pagine o suite backend completa; backend invariato. Artefatti da checkout locale modificato (`source_dirty=true`).

## 25 ottobre 2026 — GRUPPI-02

- `npm --prefix frontend run test:signals`: 30 test superati, inclusi 5 casi stagioni (compatibilita radice, intervalli futuri/scaduti/confini, esclusione figli e record eliminati, aggregazione odierna, default e gruppi senza stagione).
- `.venv/Scripts/python.exe -m pytest -q tests/test_memberships.py`: 5 superati; warning preesistente Starlette/httpx. API non modificata.
- `npm --prefix frontend run build`: TypeScript e build Vite riusciti; avviso dimensione chunk Plotly. `scripts/verify_suite_ui.py`: UI comune 0.2.8 integra. `git diff --check`: riuscito.
- Browser con app completa compilata, backend reale e archivio QA nuovo interamente sintetico: categorie Allievi/Esordienti con 2026 sul padre e 2027 figlio; schede sorelle. Assegnazione di un secondo atleta al 2027 salvata con date 2027-01-01 / 2027-12-31, conteggio aggiornato e due atleti visibili nel filtro 2027 prima dell'inizio della stagione. Esclusione della selezione gia assegnata preservata. Creata stagione 2028 sotto Allievi; modulo categoria principale privo di stagione incorporata. Screenshot in screenshots/README.md.
- L'utente riferisce collaudi personali su creazione societa/protocolli, quattro import bulk e gruppi: non equivale a nuova esecuzione automatica di quei flussi. Nessun dato reale modificato, nessuna nuova distribuzione EXE/APK e nessun collaudo del bridge Android o telefono.

## 25 ottobre 2026 — candidato installabile Windows con GRUPPI-02

Consegna locale `dist/candidates/Fuorigiri-0.10.0-pilot-20261025-01`, generata dal commit `326af8220c5f202b6d0de74a45bd0788989d76e1` con working tree pulito. Versione prodotto 0.10.0, nessuna modifica a schemi o motori per il packaging. Precedenti consegne preservate.

- Build frontend, verify_versions, verify_suite_ui e verify_core riusciti. Bundle Windows nuovo tramite build.py --output-root; installer Inno Setup compilato (AppId e directory precedente conservati). Installer 196237791 byte, SHA-256 `e1fb5b47842faff8d40b55e703fc109d334c58f27ecd8645953e2c3752130ee3`.
- EXE compilato: --smoke-test con archivio QA nuovo, exit 0 e marker smoke-ok.txt; import, logo e backend HTTP verificati. Frontend incluso nel bundle identico byte per byte a frontend/dist. Nessuna installazione automatica sopra i dati dell'utente o nuova prova su PC pulito.
- Android: Gradle 8.13 offline con JDK Temurin 21, assembleRelease riuscito. APK integro, tutti gli asset frontend identici, Python 3.13 ARM64/x86_64 presenti; zipalign -c -P 16 riuscito. APK non firmato confermato da apksigner (Missing META-INF/MANIFEST.MF); nessuna chiave creata o firma debug sostitutiva. Richiede firma del titolare prima dell'installazione; nessuna nuova prova sul telefono.
- package_candidate.py: installer, portabile, APK non firmato, sorgenti, wheel native, manifest e checksum prodotti; checksum di tutti i file consegnati ricontrollati. Sorgenti congelati prima di questo aggiornamento del registro. Nessuna pubblicazione.
- Warning di build: chunk Plotly grande; plugin QML opzionale assetdownloader assente segnalato da PyInstaller; SDK XML e deprecazioni Gradle. Smoke del bundle riuscito; nessuna qualifica aggiuntiva dei plugin QML opzionali.

## 25 ottobre 2026 — GRUPPI-03 / IMPORT-04

- Suite Python completa: **235 superati, 1 saltato**, 2 warning (Starlette/httpx e fixture ZIP duplicata); log locale test-groups-import-full-20261025.log. Include 6 test gestione gruppi, 10 import appartenenze e permessi visualizzatore sui nuovi endpoint. Coperti preservazione di ID/appartenenze, ripristino, conflitti di revisione, gerarchie, eliminazione stagione legacy, atomicita, riconciliazione ID/nome/date, reimport, sovrapposizioni e annullamento protetto da dipendenze.
- Frontend: **31 test superati**, TypeScript/build Vite e verify_suite_ui riusciti. Avviso Plotly oltre soglia chunk; UI comune invariata 0.2.8, nessun vendor modificato.
- Browser, app completa compilata e backend reale su archivio QA nuovo e sintetico: eliminata/ripristinata stagione legacy 2026 senza toccare 2027 e atleti; modifica nome stagione salvata; eliminazione categoria con figli attivi bloccata nella conferma. Modello/esempio accessibili dal quinto profilo import. Caricato CSV esempio: sovrapposizione con anno_categoria diverso rilevata e conferma disabilitata. Caricato lotto valido di 3 appartenenze, anteprima con 3 gruppi nuovi, salvataggio reale e conteggi 2024/2025/2027 verificati nella gerarchia.
- Download CSV verificati con TestClient (contenuto/BOM/intestazioni), copie canoniche in examples/import-appartenenze. Screenshot reali e provenienza in screenshots/README.md. Nessun dato reale, provider o telefono coinvolto; il nuovo stato binario e documentato nella consegna successiva, non attribuito al candidato 01 gia prodotto.

## 25 ottobre 2026 — consegna GRUPPI-03 / IMPORT-04, candidato 02

Nuovo candidato locale `dist/candidates/Fuorigiri-0.10.0-pilot-20261025-02`, versione prodotto 0.10.0, commit di base 326af8220c5f202b6d0de74a45bd0788989d76e1 con modifiche locali congelate nell'archivio sorgenti (`working_tree_dirty=true`). Il candidato 01 e le consegne precedenti sono preservati.

- Bundle EXE ricompilato in output nuovo; frontend finale ricompilato e riallineato nella sola directory di staging del bundle prima di Inno Setup, con confronto del set di file e dei byte. Modulo cycling_test.membership_import presente nel PYZ. Installer Inno riuscito; 196334194 byte, SHA-256 `0371fc81891430f067cc3efd939c761a41c1058847a371b685c2caea4e06406e`.
- EXE finale: --smoke-test con archivio QA nuovo, exit 0 e marker; import, logo, dipendenze e backend locale verificati. Nessuna installazione sopra i dati dell'utente e nessuna prova Windows pulito.
- Android assembleRelease offline con JDK 21 riuscito; APK ZIP integro, frontend finale identico e membership_import.pyc incluso. zipalign -c -P 16 riuscito e apksigner conferma assenza firma. Nessuna chiave generata, APK da firmare dal titolare; nessuna qualifica aggiuntiva su telefono.
- Consegna completa con installer, portabile, APK, sorgenti e wheel native; checksum di tutti i file ricontrollati. Sorgenti funzionali e CSV di esempio nel pacchetto confrontati con i file finali. Nessuna pubblicazione. Registro e screenshot finali aggiornati successivamente al congelamento della consegna; i binari comprendono tutte le modifiche funzionali.
- Ultimo controllo browser su archivio QA sintetico nuovo: download reale del CSV di esempio riuscito; caricamento del file completo da 4 righe, anteprima 4 appartenenze e 6 gruppi/stagioni nuovi senza errori. Screenshot import-csv-appartenenze.png aggiornato ai testi finali. Il salvataggio reale del lotto da 3 righe resta la prova precedente, distinta dalla cattura finale.
