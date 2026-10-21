# Collaudo del candidato pilot — Windows e Android

Candidato **Fuorigiri 0.10.0 · pilot-20261021-02**. Preparato il **21 ottobre 2026**. Versione prodotto invariata; identificativo candidato e digest distinguono questa consegna dalle build precedenti. Non è una release pubblicata né un’accettazione per la produzione.

La cartella di consegna è `dist/candidates/Fuorigiri-0.10.0-pilot-20261021-02/`; `candidate.json` identifica sorgenti, artefatti e limitazioni, `SHA256SUMS.txt` contiene i digest. Il sorgente congelato proviene dal working tree con modifiche locali: il commit base da solo non identifica tutti i byte. Non sostituire file dopo aver iniziato il collaudo; una correzione produce un nuovo candidato.

**Come usare i check:** `[x]` soltanto con prova effettiva e riscontro annotato; `[ ]` significa ancora da eseguire. Non trasformare un test sintetico/emulatore in una prova di account reale o dispositivo fisico. Annotare data, operatore, dispositivo/OS, digest e risultato. Per un errore usare l’ID della prova e descrivere atteso/ottenuto; allegare solo log e immagini senza dati personali, credenziali o token.

Questa checklist nei sorgenti è un registro vivo. La copia inclusa nella consegna fotografa il momento del packaging: annotare i risultati successivi qui o in una propria copia, senza modificare gli artefatti originali o riscrivere i loro checksum. Verifica finale locale dei 12 file e ZIP portabile estratto/smoke riuscita; PC pulito e telefono restano da provare.

## 0. Identificazione e preparazione

- [ ] **P-01** Confrontare i digest dei file ricevuti con SHA256SUMS.txt: devono coincidere. Registrare il candidato esatto nel verbale in fondo.
- [ ] **P-02** Predisporre PC Windows senza Python/Node/Qt e telefono Android ARM64; annotare versione OS, modello, spazio libero e versione Android System WebView.
- [ ] **P-03** Prima delle prove su archivi esistenti, conservare backup dati e materiali di recupero degli accessi/identità in luogo distinto. Non sincronizzare il database aperto tramite cloud.
- [ ] **P-04** Usare una copia QA della società sintetica, cartella cloud separata e account di prova. Non cancellare o rigenerare l’archivio abituale.
- [ ] **P-05** Concordare un solo provider iniziale del pilot e due operatori, uno Admin e uno Visualizzatore. Gli altri provider rimangono non qualificati finché non provati.

## 1. Controlli tecnici del candidato

- [x] **T-01** Build frontend TypeScript/Vite e 25 test dei modelli superati nella preparazione. Plotly resta un chunk locale differito; avviso sulla sua dimensione noto.
- [x] **T-02** Metadati prodotto 0.10.0, UI comune 0.2.8 e core 0.1.2 verificati; digest delle sei wheel Android controllati prima della compilazione.
- [x] **T-03** Regressione Python completa superata; registrare conteggio, eventuali skip e motivi in VERIFICA.md.
- [x] **T-04** Bundle Windows compilato e smoke del binario congelato superato: dipendenze, logo e backend HTTP disponibili. Lo smoke non prova tutto il rendering.
- [x] **T-05** Installer Windows prodotto dal bundle corrente; non richiede installare dipendenze a mano.
- [x] **T-06** APK release non firmato prodotto e ZIP verificato; presenza delle due ABI e frontend/asset legali controllata. Non equivale a runtime ARM64 o pagine 16 KB collaudati.
- [x] **T-07** Artefatti finali, sorgenti e wheel native raccolti; integrità ZIP e checksum verificati.

## 2. Windows — installazione e aggiornamento

- [ ] **W-01** Installare su Windows pulito con utente normale. Atteso: avvio senza Python/Node/Qt installati, logo, frontend e Info/versione corretti.
- [ ] **W-02** Disabilitare Internet e riaprire. Atteso: società locale, elenchi, protocolli, test e grafici disponibili; nessuna rete richiesta per Plotly.
- [ ] **W-03** Percorso dati con spazi/accenti; apertura e riapertura senza errori. Non usare la cartella dei binari per archiviare dati.
- [ ] **W-04** Installare sopra una versione precedente su copia QA dopo backup. Atteso: archivi, identità, credenziali e storico conservati; nessuna migrazione o ricalcolo silenzioso dei risultati.
- [ ] **W-05** Disinstallare e reinstallare sul PC QA. Atteso: dati separati conservati e società recuperabile. Non provare su archivi operativi come primo tentativo.
- [ ] **W-06** Controllare portachiavi e connessioni dopo riavvio; nessuna credenziale in file in chiaro o log.

## 3. Android — prima della distribuzione ai tester

**L’APK release di questo candidato è intenzionalmente NON firmato e non è installabile.** L’utente ha richiesto di preparare la procedura senza generare ora una chiave. Seguire [FIRMA_ANDROID.md](FIRMA_ANDROID.md). La firma Windows Authenticode non è applicata: annotare eventuali avvisi del sistema senza attribuire al prodotto la firma del compilatore Inno Setup.

- [ ] **A-01** Creare/custodire la chiave release del titolare con copia di recupero e password separata; mai committare keystore/password o inviarli in chat.
- [ ] **A-02** Firmare una copia dell’APK con la chiave stabile, verificare certificato e allineamento e calcolare un nuovo SHA-256. Conservare l’APK non firmato originale.
- [ ] **A-03** Non tentare aggiornamento diretto debug→release con firme diverse. Predisporre backup dati e recupero accessi; provare il passaggio su copia QA prima di rimuovere qualsiasi installazione.
- [ ] **A-04** Installare il firmato su telefono ARM64 e aprire offline. Atteso: backend nativo avviato, società disponibile e nessun AVVIO-01.
- [ ] **A-05** Importare FIT/CSV e ripristinare backup attraverso il picker Android; esportare PDF/MD/CSV/ZIP con SAF e riaprire i file fuori dall’app.
- [ ] **A-06** Chiudere il processo e riaprire. Atteso: ultima società corretta; nessun passaggio automatico a un’altra società se quella ricordata manca.
- [ ] **A-07** Navigare elenco→test→profilo→Indietro. Atteso: filtri/pagina conservati, nessuna perdita della bozza; modifiche non salvate protette.
- [ ] **A-08** Aprire grafico: Scorri pagina predefinito; Esplora/Zoom e ripristino funzionanti. Vista ampia in landscape immersivo senza fascia del titolo; comandi richiamabili; Back e X ripristinano orientamento/barre e mantengono il test.
- [ ] **A-09** Tastiera completa, rotazione, testo ingrandito e TalkBack: campi/azioni raggiungibili, nomi comprensibili, nessun contenuto indispensabile tagliato.
- [ ] **A-10** Chiusura forzata/riavvio durante normali operazioni su copia QA. Atteso: nessuna corruzione; operazioni non completate riconoscibili e ripetibili.
- [ ] **A-11** Aggiornare fra due APK release firmati con la stessa chiave e versionCode crescente. Atteso: dati e identità conservati. Ripetere prima della seconda consegna pilot.
- [ ] **A-12** Qualificare compatibilità su dispositivo/emulatore con pagine 16 KB prima di dichiararla o scegliere un canale che la richieda. La sola presenza delle wheel non basta.

Le precedenti prove emulatore x86_64 sono in VERIFICA.md. Questi check sul telefono non sono marcati completati per analogia.

## 4. Flusso dati e report — su entrambe le piattaforme

- [ ] **F-01** Creare società QA, gruppo e sottogruppo/stagione, atleta e appartenenza. Atteso: contesti e storico corretti; nessuna esposizione ad altre società.
- [ ] **F-02** Creare/versionare protocollo manuale con step, senza step e da ERG; conservare tutte le versioni e verificare l’associazione ai test.
- [ ] **F-03** Inserire test incrementale da FIT/CSV e solo manuale; un tracciato genera potenza/FC/cadenza con unità e lacune, un riepilogo manuale non inventa una curva.
- [ ] **F-04** Confrontare un incrementale con un riferimento calcolato indipendentemente. Completezza/copertura distinte dall’aderenza; ultimo step completo primario, interpolazione e soglia separati.
- [ ] **F-05** Lattato: prelievi/finestre associati correttamente, interpolazione locale e livelli configurabili, nessuna estrapolazione o assimilazione automatica a LT/FTP.
- [ ] **F-06** Sprint breve, Wingate 15 s e 30 s: finestre, carico/partenza e risultati coerenti con casi controllati; protocolli incompatibili non aggregati automaticamente.
- [ ] **F-07** Campi custom, valori zero, false e mancanti conservati; correzioni motivate generano revisione e non cancellano lo storico.
- [ ] **F-08** Import CSV anagrafiche/antropometria/storici: anteprima, errori, opzionali e duplicati gestiti. Esportazione leggibile e coerente con i dati importati.
- [ ] **F-09** Storici: filtri per protocollo/metodo, media/mediana/numerosità e mancanti corretti. Valori di metodi incompatibili separati.
- [ ] **F-10** Report società→gruppo→stagione→atleta coerenti come sottoinsiemi; PDF e Markdown effettivamente aperti, grafici/tabelle leggibili, footer societario fisso e assenza di duplicazioni inutili.
- [ ] **F-11** Crescita/maturazione: domini e input mancanti rispettati, misurato/stimato distinti; snapshot conservato invariato negli export. Validazione esterna rimane distinta dal funzionamento software.

## 5. Backup, recupero e sincronizzazione Windows–Android

- [ ] **S-01** Esportare backup e ripristinare realmente una copia; confrontare atleti, test, revisioni, tracciati e report. Una copia di backup deve restare fuori dal canale sync.
- [ ] **S-02** Collegare la stessa società sui due dispositivi tramite invito/accesso appropriato, non due cloni indipendenti. Atteso: medesima società/canale, accessi personali.
- [ ] **S-03** Creare/correggere offline sul PC, sincronizzare e ricevere sul telefono; ripetere in senso opposto. Nessun duplicato o perdita di allegati.
- [ ] **S-04** Modifiche concorrenti allo stesso record: conflitto esplicito e risoluzione tracciata, nessuna sovrascrittura silenziosa.
- [ ] **S-05** Visualizzatore può consultare/esportare ma non modificare; revoca e inviti verificati anche quando un dispositivo torna online dopo giorni.
- [ ] **S-06** Interrompere la rete a metà trasferimento sul canale QA. Atteso: retry senza pacchetti parziali utilizzati o duplicati; verifica completa distingue integrità da pacchetti già acquisiti.
- [ ] **S-07** Scadenza/rinnovo/revoca del token o credenziale del provider: errore comprensibile e ricollegamento senza perdita dell’archivio.
- [ ] **S-08** Se si usa sync in background Android, verificare su telefono con app chiusa e risparmio energetico; non dedurre l’esecuzione da WorkManager presente nei sorgenti.
- [ ] **S-09** Ripristino dopo perdita del dispositivo e recupero accessi realmente provati su archivio QA. Documentare cosa recupera backup dati e cosa richiede il materiale identità.
- [ ] **S-10** Annotare provider/server/account e condizioni effettivamente provati. Per ogni provider aggiuntivo ripetere S-02–S-08; nessuna qualifica implicita degli altri.

## 6. Pilot e promozione

- [ ] **R-01** Completati i check indispensabili P/T/W/A/F/S pertinenti all’uso concordato, con eccezioni esplicite e funzioni escluse dal pilot indicate ai tester.
- [ ] **R-02** Nessun blocco noto su perdita/corruzione dati, accessi o risultati errati; i problemi bloccanti impediscono la promozione.
- [ ] **R-03** Eseguite almeno due sessioni operative complete e un ciclo di aggiornamento/backup/ripristino con gli operatori del pilot; registrate anomalie e riscontri.
- [ ] **R-04** Riferimenti scientifici, avvisi/licenze e gestione dei dati riesaminati per il perimetro operativo; non dichiarare validazione biologica dall’esito della UI.
- [ ] **R-05** Chiave Android e modalità di distribuzione stabile definite; firma Windows/avvisi del sistema dichiarati. Nessuna pubblicazione automatica da questo candidato.
- [ ] **R-06** Approvata la promozione del candidato preciso (digest), oppure creato un successore per le correzioni. Conservare vecchio installer e backup: downgrade dei binari non garantisce downgrade dei dati.

## Verbale di prova

| Campo | Compilare |
|---|---|
| Candidato e SHA-256 dei pacchetti | |
| Operatore/data | |
| PC/Windows e telefono/Android/WebView | |
| APK firmato: impronta certificato e SHA-256 | |
| Società QA e provider testato (senza segreti) | |
| ID prove completate | |
| Problemi: ID, atteso, ottenuto, gravità | |
| Eccezioni/funzionalità escluse dal pilot | |
| Esito: da correggere / ammesso al pilot / promuovibile | |
| Responsabile della decisione | |
