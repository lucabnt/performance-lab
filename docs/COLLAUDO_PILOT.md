# Collaudo del candidato pilot — Windows e Android

## Candidato corrente — rc-20261121-02, Windows + Android, 21 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-rc-20261121-02/` dal commit `0e3f900` con working tree pulito. Stesso codice di `rc-20261121-01`, ricostruito dopo la riscrittura della storia che toglie dai documenti le segnalazioni inviate a Microsoft (documenti inclusi nel pacchetto Windows e nei sorgenti). Base della nuova release `v0.10.0-alpha.1`: la precedente è stata eliminata.

- **Windows:** come sotto; launcher nuovo (SHA-256 `febf062f…3758`), quindi la prova con Defender attivo va ripetuta su questa build.
- **Android:** debug verificato su emulatore x86_64 (2 test strumentali, avvio). Release rigenerato e firmato dal titolare con la stessa chiave (SHA-256 `9663b12e…a678`, [FIRMA_ANDROID.md](FIRMA_ANDROID.md)), identico al candidato salvo le intestazioni `.pyc`; installazione del firmato non riprovata.
- Smoke, scansioni Defender, contenuti e 25 checksum verificati; [prove e digest](VERIFICA.md).

## Candidato precedente — rc-20261121-01, Windows + Android, 21 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-rc-20261121-01/` dal commit `ccc50ce` con working tree pulito: `rc-20261120-02` più REPORT-LOCALE-01 (i file dei report esportati restano sul dispositivo che li crea, solo i metadati sono sincronizzati) e FIT-SESSIONE-01 (import dei FIT con fine sessione uguale all’inizio), oltre a politica di sicurezza e guida ai contributi. Destinato a sostituire `rc-20261120-02` come base della release `v0.10.0-alpha.1`, non ancora resa pubblica.

- **Windows:** installer sopra l’installazione esistente dopo un backup e con l’app chiusa, oppure portabile completo; prova di installazione, avvio e riapertura con Defender attivo, poi W-01…W-07.
- **Android:** `android-debug-test.apk` (firma di test) si installa come aggiornamento; verificato su emulatore x86_64 (2 test strumentali, avvio). Release rigenerato e firmato dal titolare il 21 novembre con la stessa chiave (SHA-256 `91095c6f…eceb`, [FIRMA_ANDROID.md](FIRMA_ANDROID.md)), con `certifi` 2026.11.20 invece della versione del candidato; aggiornamento sopra il release precedente provato su emulatore. ARM64 non provato su dispositivo reale; 4 librerie non conformi a 16 KB.
- Smoke, scansioni Defender, contenuti e 25 checksum verificati; [prove e digest](VERIFICA.md).

## Candidato precedente — rc-20261120-02, Windows + Android, 20 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-rc-20261120-02/` dal commit `8e9de2d` con working tree pulito: `rc-20261120-01` più SYNC-SPAZIO-01 (pagine delta della sync v2 e pannello «Spazio occupato dallo scambio»). È la base della release `v0.10.0-alpha.1`; la preparazione di release da `rc-20261120-01` non è stata pubblicata.

- **Windows:** come per `rc-20261120-01`: installer sopra l’installazione esistente dopo un backup e con l’app chiusa, oppure portabile completo; prima prova installazione, avvio e riapertura con Defender attivo ([WINDOWS_DEFENDER.md](WINDOWS_DEFENDER.md)), poi W-01…W-07.
- **Android:** `android-debug-test.apk` si installa come aggiornamento; verificato su emulatore x86_64 (2 test strumentali, avvio con dati conservati). `android-release-unsigned.apk` è l’input di confronto per la firma del titolare ([FIRMA_ANDROID.md](FIRMA_ANDROID.md)). ARM64 non provato su dispositivo reale; 4 librerie non conformi a 16 KB.
- **Sync:** con la v2 attiva, dopo l’aggiornamento di tutti gli admin lo spazio remoto deve crescere solo con le modifiche; verificare con «Analizza lo spazio» prima e dopo alcuni scambi WebDAV reali.
- Smoke, scansioni Defender, contenuti e 25 checksum verificati; [prove e digest](VERIFICA.md).

## Candidato precedente — rc-20261120-01, Windows + Android, 20 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-rc-20261120-01/` dal commit `46959ed` con working tree pulito: traduzioni inglesi complete (I18N-01), core comune 0.2.0, etichette «sperimentale» dei provider, bootloader Windows locale e wheel Android neutre. Sostituisce per il collaudo `core020-20261119-01` e `android-neutre-20261120-01`.

- **Windows:** installer da eseguire sopra l’installazione esistente dopo un backup e con l’app chiusa, oppure portabile completo. Prima prova: installazione, avvio e riapertura dal collegamento con Defender attivo, controllando gli eventi 1116/1117 ([WINDOWS_DEFENDER.md](WINDOWS_DEFENDER.md)); poi W-01…W-07.
- **Android:** `android-debug-test.apk` (firma di test) si installa come aggiornamento senza disinstallare; verificato su emulatore x86_64 (2 test strumentali, avvio, passaggio all’inglese). `android-release-unsigned.apk` è il file da firmare con la chiave del titolare ([FIRMA_ANDROID.md](FIRMA_ANDROID.md)); scansione dei percorsi pulita. ARM64 non provato su dispositivo reale; 4 librerie non conformi a 16 KB.
- Smoke, scansioni Defender, contenuti e 25 checksum verificati; [prove e digest](VERIFICA.md).

## Candidato precedente Android — android-neutre, 20 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-android-neutre-20261120-01/`, **solo Android**, con le wheel native ricostruite da radice neutra. `android-debug-test.apk` (firma di test abituale) si installa come aggiornamento sopra l’APK di test già presente, senza disinstallare; verificato su emulatore API 35 x86_64, non su telefono. `android-release-unsigned.apk` è da firmare con la chiave del titolare ([FIRMA_ANDROID.md](FIRMA_ANDROID.md)): la scansione dei percorsi è pulita. Restano A-01…A-12, in particolare telefono ARM64 e 4 librerie non conformi a 16 KB. [Prove e digest](VERIFICA.md).

## Candidato precedente Windows — core020, solo Windows, 19 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-core020-20261119-01/`, **solo Windows**, dal commit `9239cb8` con working tree pulito. Rispetto a `win-av02-20261115-02` aggiunge l’etichetta «sperimentale» di Drive/Dropbox/OneDrive (PERIMETRO-01), il core comune 0.2.0 e la correzione della pulizia del backup protetto; mantiene bootloader locale e risorsa di versione (WIN-AV-02) e MAT-PHV-01. Installer da eseguire sopra l’installazione esistente dopo un backup e con l’app chiusa (W-04), oppure portabile completo. **Prima prova da fare:** installazione, avvio, chiusura e riapertura dal collegamento con Defender attivo, controllando gli eventi 1116/1117 ([WINDOWS_DEFENDER.md](WINDOWS_DEFENDER.md)). Per Android vedere il candidato `android-neutre-20261120-01` sopra. Smoke, scansioni Defender e 15 checksum verificati; [prove e digest](VERIFICA.md). Restano WIN-AV-01/02, Windows pulito, firma Authenticode e i gate Android.

## Candidato precedente — win-av02, 15 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-win-av02-20261115-02/` dal commit `d66d337`: Windows con bootloader PyInstaller locale e risorsa di versione (WIN-AV-02), MAT-PHV-01; Android debug di test, release non firmato e supporto strumentale. Installazione con Defender attivo mai eseguita; superato da core020 per Windows. [Prove e digest](VERIFICA.md).

## Candidato precedente — revisione tecnica, 15 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-revisione-tecnica-20261115-01/`: build Windows/Android **0.10.0** con la revisione tecnica del 14–15 novembre (backup protetto da password, prestazioni, inviti, CSP, permessi, CSV) e le funzioni di alpha.1. Windows: installer da eseguire sopra l’installazione esistente dopo un backup e con l’app chiusa (W-04), oppure portabile completo. Android: `debug-test.apk` con la firma di test abituale, da installare come aggiornamento senza disinstallare; release non firmato e non distribuibile (percorsi del builder nelle wheel). Smoke, scansioni Defender, firme e 26 checksum verificati; [prove e digest](VERIFICA.md). Restano Windows pulito/WIN-AV-01, runtime Android della build, 16 KB, firma release e provider reali. Gli inviti nuovi richiedono che tutti i dispositivi siano aggiornati.

## Prima pre-release del 10 novembre 2026

Per alpha.1 consultare [allegati e limiti](DISTRIBUZIONE.md) e [verifiche](VERIFICA.md). L’APK candidato richiede bonifica delle dipendenze e firma. I risultati storici sotto riguardano le rispettive build.

## Candidato precedente — ordine e maturazione, 9 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-ordine-maturazione-20261109-01/`: nuove build Windows/Android **0.10.0** con **UI-ORDINE-02** (cognome/nome, test e misure dal più recente in pagine indipendenti da 15) e **MAT-AVVISI-01** (stime datate decrescenti e indici antropometrici con avvisi, motore growth-maturity/2), oltre alle funzioni precedenti; UI comune **0.2.9** invariata. Installer/portabile completi, APK debug firmato per i test, release non firmato, supporto strumentale, sorgenti/wheel e **25 checksum finali verificati**. Avvio Windows, scansioni Defender attivo e controlli di contenuti/firme/allineamento riusciti. [Prove e digest](VERIFICA.md).

Nessuna pubblicazione, chiave nuova o installazione sopra dati operativi. Restano Windows pulito/aggiornamento, firma release e runtime Android/telefono, sei problemi LOAD 16 KB, provider reali e validazione esterna. WIN-AV-01 attende reinstallazione/riapertura con protezione attiva: le scansioni di questa nuova build sono una verifica distinta. La documentazione congelata nei pacchetti precede questa annotazione conclusiva.

## Candidato precedente — import-avvisi, 8 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-import-avvisi-20261108-01/`: nuove build Windows/Android **0.10.0** con avvisi CSV non bloccanti, riconoscimento duplicati e correzione dello scorrimento dei dialoghi tramite UI comune **0.2.9**, oltre alle funzioni precedenti. Installer e portabile completi, APK debug firmato per i test, release non firmato, supporto strumentale, sorgenti/wheel e **25 checksum verificati**. Smoke Windows e scansioni correnti riusciti, firme/allineamento/contenuti APK verificati. [Prove e digest](VERIFICA.md).

Nessuna pubblicazione, nuova chiave o installazione sopra dati operativi. Restano WIN-AV-01 storico, Windows pulito/aggiornamento, firma release, runtime della nuova build Android e telefono, provider reali e sei problemi LOAD 16 KB. Zipalign e smoke non sostituiscono tali gate. La documentazione congelata nei pacchetti precede questa annotazione finale.

## Candidato precedente — antro-incrementale, 8 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-antro-incrementale-20261108-01/`: nuove build Windows/Android 0.10.0 con import CSV incrementale, altezza perineale e rapporto sulla statura nel profilo; include eliminazione/ripristino di misure e test e le funzioni precedenti. Installer/portabile completi, APK debug firmato per i test, release non firmato per il titolare, APK strumentale, sorgenti e wheel. Smoke Windows e scansioni correnti riusciti, contenuti e **25 checksum finali verificati**. [Registro e digest](VERIFICA.md). Nessuna pubblicazione o nuova chiave.

Restano Windows pulito/aggiornamento, WIN-AV-01 del candidato storico, firma release, runtime della nuova build Android e telefono, provider reali e sei problemi LOAD nativi a 16 KB. Non confondere zipalign con qualifica 16 KB; le scansioni correnti non dimostrano un falso positivo sul vecchio candidato. La documentazione congelata nei pacchetti precede questa annotazione finale.

## Candidato record-lifecycle — 8 novembre 2026

Consegna precedente `dist/candidates/Fuorigiri-0.10.0-record-lifecycle-20261108-01/`: nuove build Windows/Android con RECORD-LIFECYCLE-01 e funzioni precedenti. Installer e ZIP portabile completi, APK debug firmato con la chiave di test abituale, release non firmato e APK strumentale separato, sorgenti/wheel, manifest e 25 checksum verificati. Smoke Windows e scansioni correnti del nuovo bundle/installer riusciti. [Prove e digest](VERIFICA.md).

Prima di accettare: installazione/riapertura e aggiornamento su Windows pulito con protezioni attive, firma release del titolare, runtime della nuova build su Android e conservazione dei dati, provider reali se inclusi nel pilot. Audit APK 222 ELF con gli stessi sei problemi LOAD 16 KB; zipalign superato non chiude il gate. WIN-AV-01 del candidato precedente resta aperto e non viene aggirato con esclusioni. Nessuna nuova chiave, installazione sui dati operativi o pubblicazione.

## Candidato sync-intervals — consegna 8 novembre 2026

`dist/candidates/Fuorigiri-0.10.0-sync-intervals-20261107-01/`: nuove build del 7 con SYNC-AUTO-01 / INT-ICU-01 e modifiche correnti. Installer e portabile completi, APK debug già firmato per i test, release non firmato per il titolare, sorgenti/wheel, manifest e 24 checksum verificati. [Prove](VERIFICA.md). Nessuna pubblicazione o modifica ai vecchi pacchetti.

Nuovo bundle e installer senza rilevamenti nelle scansioni Defender correnti, smoke su QA nuovo riuscito. Non chiude WIN-AV-01 del candidato precedente e non sostituisce installazione/riapertura con protezioni attive su Windows pulito. APK: firma debug invariata e zipalign riuscito, ma audit 222 ELF con sei problemi LOAD 16 KB invariati. Nessuna prova runtime di questa build su emulatore/telefono o provider reale; gli altri gate e la firma release rimangono aperti.

## Blocco Windows — 7 novembre 2026

**WIN-AV-01 aperto:** Defender rimuove l'EXE del candidato `windows-alpha-review-20261102-01` con `Trojan:Win32/Bearfoos.A!ml`. Sospendere la qualificazione di questo candidato; gli smoke precedenti non risolvono il blocco. [Riscontri e criteri per ripetere installazione e riapertura](WINDOWS_DEFENDER.md). Falso positivo non confermato, nessuna esclusione o nuova build in questa diagnosi.

## Candidato Windows alpha review — 2 novembre 2026

`dist/candidates/Fuorigiri-0.10.0-windows-alpha-review-20261102-01/`: bundle/installer ricompilati con correzione backup e dipendenze aggiornate dopo alpha-prep. Regressione 271 Python passati/1 skip e 37 frontend; smoke dell'EXE con sole directory Windows nel PATH e archivio QA nuovo riuscito. Installer/portabile/sorgenti separati dagli APK; 13 checksum verificati, non firmato Authenticode. [Esiti e limiti](VERIFICA.md).

Restano Windows pulito, aggiornamento/dati e operazioni backup/ripristino sui PC destinatari, provider reali se inclusi e accettazione. Il kit Fedora nativo 16 KB è pronto ma attende compilazione/revisione: nessun nuovo APK qualificato da questa fase. Il report con grafico sul telefono rimane rimandato per scelta dell'utente. Nessuna pubblicazione o firma implicita.

## Candidato Android Pillow — 2 novembre 2026

Decisione dell'utente: **report con grafico sul telefono rimandato per il momento**; per questa fase è accettato il test positivo sull'emulatore. Non richiedere ora un nuovo corpus QA o debug USB per questa prova e non marcarla come eseguita sul telefono. Rimangono distinti il riscontro manuale dell'export PDF ricevuto e gli altri gate pilot.

Riscontro manuale successivo: utente riferisce aggiornamento/avvio apparentemente riusciti e export PDF riuscito sul telefono; PDF ricevuto di due pagine verificato strutturalmente e visivamente sul PC, con logo/tabelle/testi leggibili. Report storico privo di campioni, quindi senza grafici. Restano conferma del lettore PDF sul telefono, report sintetico con tracciato/grafico, controllo completo dei dati e test ARM64 strumentali; non marcare questi ultimi completati dal solo allegato. Dati personali del documento non inclusi nel registro o nella galleria.

`dist/candidates/Fuorigiri-0.10.0-android-pillow-20261102-01/`: debug installabile con firma abituale, release non firmato e APK dei test separati; sorgenti, wheel e checksum inclusi. Pillow 13.0.0 e multipart 0.0.32 verificati in entrambi gli APK. Emulatore API35 x86_64/pagine 4 KB: due test passati, logo/immagini/font/Matplotlib/PDF e apertura Android PdfRenderer; aggiornamento senza disinstallazione, dati dei workspace invariati. Dettagli e limiti in [VERIFICA.md](VERIFICA.md).

Prima di distribuire: telefono ARM64 e conservazione dei suoi dati, export PDF tramite UI/app esterna, firma release del titolare, audit nativo e altri gate pilot. Sei moduli ulteriori non soddisfano il controllo LOAD 16 KB: non qualificare l'intero APK dal solo zipalign o dai moduli Pillow corretti. Il candidato Windows precedente rimane storico e non viene aggiornato da questa consegna Android.

## Revisione pre-alpha — 2 novembre 2026

ALPHA-REVIEW-01 è successivo alla preparazione sotto: correzione backup e dipendenze aggiornate richiedono un nuovo candidato e nuove verifiche T-02–T-07. Non promuovere `alpha-prep-20261102-01` come comprensivo delle correzioni. Prima della distribuzione Android risolvere Pillow nativo e qualificare il parser multipart aggiornato: [riscontri e gate](REVISIONE_ALPHA.md). I check storici restano riferiti ai rispettivi artefatti.

## Preparazione prima alpha — 2 novembre 2026

Cartella `dist/candidates/Fuorigiri-0.10.0-alpha-prep-20261102-01/`: installer Windows originale `pilot-20261101-01`, verificato contro il codice attuale e riusato senza ricompilazione; nuovi APK debug di test e release non firmato. Versione prodotto 0.10.0 invariata. Il debug conserva la firma dei test precedenti; il release richiede la [firma del titolare](FIRMA_ANDROID.md). Manifest e checksum distinguono questi file e la provenienza Windows. Questa preparazione non pubblica Alpha 1 e non completa i check operativi sotto.

Prima della distribuzione alpha, completare firma release e prove Windows pulito/telefono, installazione e aggiornamento, backup/ripristino e flussi inclusi nel perimetro dei tester. Per la UI corrente ripetere F-08 dagli import contestuali (Atleti, Gruppi, Test, Antropometria e punto completo in Archivio). Se si distribuisce la sincronizzazione, qualificare provider e due account reali. Esiti tecnici e limiti in VERIFICA.md; nessuna installazione automatica.

## Aggiornamento VO₂ — 31 ottobre 2026

Nuovo installer Windows `dist/candidates/Fuorigiri-0.10.0-pilot-20261031-01/` e APK di test `dist/android-tests/Fuorigiri-0.10.0-pixel9-test-20261031-01/`, versione prodotto 0.10.0. Includono VO2-01 e le correzioni precedenti. Windows: bundle completo e smoke verificati, installer non firmato Authenticode. Android: APK debug con firma invariata per l’aggiornamento dei test precedenti; nessuna nuova chiave release. La sezione storica sotto sull’APK release non firmato riguarda il candidato del 21 ottobre, non questo APK di test.

Ripetere F-03/F-09/F-10 usando VO₂ temporizzato in L/min, CSV temporale o gas separato (una sola fonte), asse indipendente e VO₂peak assoluto/relativo, esportazioni risultati/osservazioni e conservazione delle revisioni. Un punto isolato non deve produrre VO₂peak; VO₂max richiede evidenze esplicite del laboratorio. I nuovi binari non ricalcolano gli storici automaticamente. Prima di aggiornare conservare backup e chiudere l’app; non disinstallare Android per applicare il nuovo APK di test. Windows pulito, telefono e provider reali restano da collaudare, come riportato in VERIFICA.md. Non marcare completati i check per analogia con compilazione o smoke.

Candidato **Fuorigiri 0.10.0 · pilot-20261021-02**. Preparato il **21 ottobre 2026**. Versione prodotto invariata; identificativo candidato e digest distinguono questa consegna dalle build precedenti. Non è una release pubblicata né un’accettazione per la produzione.

La cartella di consegna è `dist/candidates/Fuorigiri-0.10.0-pilot-20261021-02/`; `candidate.json` identifica sorgenti, artefatti e limitazioni, `SHA256SUMS.txt` contiene i digest. Il sorgente congelato proviene dal working tree con modifiche locali: il commit base da solo non identifica tutti i byte. Non sostituire file dopo aver iniziato il collaudo; una correzione produce un nuovo candidato.

**Come usare i check:** `[x]` soltanto con prova effettiva e riscontro annotato; `[ ]` significa ancora da eseguire. Non trasformare un test sintetico/emulatore in una prova di account reale o dispositivo fisico. Annotare data, operatore, dispositivo/OS, digest e risultato. Per un errore usare l’ID della prova e descrivere atteso/ottenuto; allegare solo log e immagini senza dati personali, credenziali o token.

Questa checklist nei sorgenti è un registro vivo. La copia inclusa nella consegna fotografa il momento del packaging: annotare i risultati successivi qui o in una propria copia, senza modificare gli artefatti originali o riscrivere i loro checksum. Verifica finale locale dei 12 file e ZIP portabile estratto/smoke riuscita; PC pulito e telefono restano da provare.

## Aggiornamento Windows del 22 ottobre 2026

Consegna Windows separata: `dist/candidates/Fuorigiri-0.10.0-windows-20261022-01/`. Include DESKTOP-01; il candidato Windows/Android del 21 ottobre rimane conservato. Numero prodotto 0.10.0 invariato: identificativo della consegna e SHA-256 distinguono i binari. Questo prova la sostituzione della stessa versione; un futuro passaggio di versione richiederà una prova distinta.

1. Prima dell’aggiornamento, esportare un backup dei dati e il recupero degli accessi; annotare società e numerosità di atleti/test. Conservare le copie fuori dalla cartella dell’app.
2. Chiudere Fuorigiri e avviare il nuovo `Fuorigiri-0.10.0-windows-x64-setup.exe`, con lo stesso utente Windows e mantenendo la cartella di installazione proposta. Non occorre disinstallare prima.
3. Aprire l’app e verificare società, dati e accessi conservati (W-04). L’installer mantiene AppId e destinazione; non include archivi dimostrativi nella cartella dati dell’utente.
4. Al primo avvio aggiornato selezionare una volta la società: la vecchia versione non aveva salvato la preferenza desktop. Chiudere completamente e riaprire: deve aprirsi direttamente quella società (W-07).
5. Ripetere con un’altra società e senza rete. Annotare esito, digest dell’installer e problemi. Il nuovo installer non è firmato Authenticode; l’eventuale avviso Windows sulla provenienza è distinto da un errore dell’app.

## Aggiornamento Windows e Android del 22 ottobre 2026

Nuova consegna `dist/candidates/Fuorigiri-0.10.0-pilot-20261022-02/`, con DESKTOP-01, codice protocolli e anteprima anagrafica IMPORT-01. Versione prodotto 0.10.0 invariata, candidato e checksum distinti; pacchetti precedenti conservati. Windows: installer sopra la versione esistente o ZIP portabile completo. Android: release non firmato per firma del titolare, debug separato per collaudo con la stessa firma debug precedente; non sostituisce il percorso release e non richiede disinstallare o cancellare dati.

Ripetere F-02 sul codice modificabile per tutte le famiglie e F-08 sull’anteprima anagrafica completa, più W-04/W-07 e A-05/A-06 sui dispositivi del collaudo. Non importare dati personali nei corpus distribuiti. Esiti tecnici effettivi e limiti in VERIFICA.md; la preparazione dei pacchetti non aggiorna automaticamente l’installazione del PC o del telefono.

## Aggiornamento importazioni del 22 ottobre 2026

Consegna `dist/candidates/Fuorigiri-0.10.0-pilot-20261022-04/`, successiva al candidato 02 e con IMPORT-02/03. La preparazione 03 è stata interrotta prima del confezionamento per includere la richiesta estesa sui test e sui modelli CSV. Ripetere F-08 su tutti i profili: scaricare e compilare i quattro modelli vuoti; verificare nomi/risultati nelle anteprime, conteggi separati dei protocolli e import anaerobico Sprint/15/30 con tipo e durata espliciti. Per antropometria verificare origine e fonti derivate/stimate in salvataggio, correzione ed export.

Nessuna riscrittura automatica delle rilevazioni già importate con la vecchia versione; conservare gli originali e usare correzioni motivate se necessario. Windows e Android restano 0.10.0; checksum e candidato distinguono la consegna. I pacchetti precedenti restano conservati.

## Assegnazione gruppi del 22 ottobre 2026

Consegna successiva `dist/candidates/Fuorigiri-0.10.0-pilot-20261022-05/`, con GRUPPI-01 e tutte le correzioni del candidato 04. Ripetere F-01: aggiungere dal profilo, selezionare più atleti da gruppo e stagione, cercare senza perdere selezioni e verificare conteggi, periodo e anno di categoria. Le appartenenze sovrapposte nello stesso gruppo sono saltate; le precedenti rimangono conservate. Verificare accesso in sola lettura e aggiornamento sopra la versione precedente su copia QA. Nessun aggiornamento operativo eseguito dall’agente.

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
- [ ] **W-07** Con installer contenente DESKTOP-01: creare/aprire una società, chiudere completamente e riaprire. Atteso: ultima società aperta direttamente, anche senza rete. Ripetere cambiando società; archivio ricordato indisponibile: selettore con avviso, nessun’altra società aperta automaticamente. Il candidato del 21 ottobre non contiene questa correzione.
- [ ] **W-02** Disabilitare Internet e riaprire. Atteso: società locale, elenchi, protocolli, test e grafici disponibili; nessuna rete richiesta per Plotly.
- [ ] **W-03** Percorso dati con spazi/accenti; apertura e riapertura senza errori. Non usare la cartella dei binari per archiviare dati.
- [ ] **W-04** Installare sopra una versione precedente su copia QA dopo backup. Atteso: archivi, identità, credenziali e storico conservati; nessuna migrazione o ricalcolo silenzioso dei risultati.
- [ ] **W-05** Disinstallare e reinstallare sul PC QA. Atteso: dati separati conservati e società recuperabile. Non provare su archivi operativi come primo tentativo.
- [ ] **W-06** Controllare portachiavi e connessioni dopo riavvio; nessuna credenziale in file in chiaro o log.

## 3. Android — prima della distribuzione ai tester

**L’APK release di questo candidato è intenzionalmente NON firmato e non è installabile.** L’utente ha richiesto di preparare la procedura senza generare ora una chiave. Seguire [FIRMA_ANDROID.md](FIRMA_ANDROID.md). La firma Windows Authenticode non è applicata: annotare eventuali avvisi del sistema senza attribuire al prodotto la firma del compilatore Inno Setup.

- [ ] **A-01** Creare/custodire la chiave release del titolare con copia di recupero e password separata; mai committare keystore/password o inviarli in chat. *20 novembre 2026:* chiave creata dal titolare in Android Studio (certificato SHA-256 `a04c6d2d…406d`); copia di recupero e custodia separata della password ancora da completare.
- [x] **A-02** Firmare una copia dell’APK con la chiave stabile, verificare certificato e allineamento e calcolare un nuovo SHA-256. Conservare l’APK non firmato originale. *20 novembre 2026:* release `46959ed` firmato con Android Studio (schema v2), certificato `CN=Luca Bontempi, C=IT`, zipalign `-P 16` e scansione percorsi superati, SHA-256 `72094a80…efca`; contenuto equivalente al release non firmato di `rc-20261120-01`.
- [ ] **A-03** Non tentare aggiornamento diretto debug→release con firme diverse. Predisporre backup dati e recupero accessi; provare il passaggio su copia QA prima di rimuovere qualsiasi installazione.
- [ ] **A-04** Installare il firmato su telefono ARM64 e aprire offline. Atteso: backend nativo avviato, società disponibile e nessun AVVIO-01.
- [ ] **A-05** Importare FIT/CSV e ripristinare backup attraverso il picker Android; esportare PDF/MD/CSV/ZIP con SAF e riaprire i file fuori dall’app.
- [ ] **A-06** Chiudere il processo e riaprire. Atteso: ultima società corretta; nessun passaggio automatico a un’altra società se quella ricordata manca.
- [ ] **A-07** Navigare elenco→test→profilo→Indietro. Atteso: filtri/pagina conservati, nessuna perdita della bozza; modifiche non salvate protette.
- [ ] **A-08** Aprire grafico: Scorri pagina predefinito; Esplora/Zoom e ripristino funzionanti. Vista ampia in landscape immersivo senza fascia del titolo; comandi richiamabili; Back e X ripristinano orientamento/barre e mantengono il test.
- [ ] **A-09** Tastiera completa, rotazione, testo ingrandito e TalkBack: campi/azioni raggiungibili, nomi comprensibili, nessun contenuto indispensabile tagliato.
- [ ] **A-10** Chiusura forzata/riavvio durante normali operazioni su copia QA. Atteso: nessuna corruzione; operazioni non completate riconoscibili e ripetibili.
- [ ] **A-11** Aggiornare fra due APK release firmati con la stessa chiave e versionCode crescente. Atteso: dati e identità conservati. Ripetere prima della seconda consegna pilot. *20 novembre 2026:* dall’APK firmato della preparazione `rc-20261120-01` a quello di alpha.1 (`rc-20261120-02`), stessa chiave, su emulatore x86_64: aggiornamento accettato, società e identità conservate; versionCode invariato e nessun telefono, quindi la voce resta aperta.
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
- [x] **S-02** Collegare la stessa società sui due dispositivi tramite invito/accesso appropriato, non due cloni indipendenti. Atteso: medesima società/canale, accessi personali. *13 novembre 2026, riferito dall’utente:* WebDAV fra Windows e Android con due operatori distinti, sincronizzazione funzionante. Build e server non annotati.
- [ ] **S-03** Creare/correggere offline sul PC, sincronizzare e ricevere sul telefono; ripetere in senso opposto. Nessun duplicato o perdita di allegati. *13 novembre:* scambio nei due sensi riferito come funzionante su WebDAV; correzioni offline e allegati non annotati, check aperto.
- [ ] **S-04** Modifiche concorrenti allo stesso record: conflitto esplicito e risoluzione tracciata, nessuna sovrascrittura silenziosa.
- [ ] **S-05** Visualizzatore può consultare/esportare ma non modificare; revoca e inviti verificati anche quando un dispositivo torna online dopo giorni.
- [ ] **S-06** Interrompere la rete a metà trasferimento sul canale QA. Atteso: retry senza pacchetti parziali utilizzati o duplicati; verifica completa distingue integrità da pacchetti già acquisiti.
- [ ] **S-07** Scadenza/rinnovo/revoca del token o credenziale del provider: errore comprensibile e ricollegamento senza perdita dell’archivio.
- [ ] **S-08** Se si usa sync in background Android, verificare su telefono con app chiusa e risparmio energetico; non dedurre l’esecuzione da WorkManager presente nei sorgenti.
- [ ] **S-09** Ripristino dopo perdita del dispositivo e recupero accessi realmente provati su archivio QA. Documentare cosa recupera backup dati e cosa richiede il materiale identità.
- [ ] **S-10** Annotare provider/server/account e condizioni effettivamente provati. Per ogni provider aggiuntivo ripetere S-02–S-08; nessuna qualifica implicita degli altri. *13 novembre:* provato soltanto WebDAV; Drive, Dropbox e OneDrive restano non qualificati. *18 novembre:* i tre provider sono sperimentali e fuori dai gate dell'alpha (PERIMETRO-01).

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

## Candidato Windows UI-SUITE-001 — 1 novembre 2026

Consegna prevista `dist/candidates/Fuorigiri-0.10.0-pilot-20261101-01/`, separata dai predecessori. Ripetere F-08 dai nuovi accessi contestuali: Atleti per anagrafiche, Gruppi per appartenenze, Test per aerobici/anaerobici, Antropometria per rilevazioni; Archivio conserva tutti i tracciati. Confermare annullamento/scarto e isolamento della società. Versione 0.10.0 invariata, ID e digest distinguono la consegna; nessun nuovo APK, installazione operativa o qualifica PC pulito impliciti. Gli esiti effettivi sono in VERIFICA e nei manifest della consegna.

Consegna Windows UI-SUITE-001 completata il 1 novembre: build isolata, 19 asset frontend identici nel bundle, smoke EXE con PATH Windows e installer Inno riusciti. Setup 196823276 byte, SHA-256 `0169b82c3d3431c97131d7c6ff70bb2acf6a3497712220ea404f970c162d9219`. Questo non completa W-01/W-04/W-05: nessuna installazione sul profilo operativo o PC pulito eseguita. Sorgenti e 12 checksum della consegna verificati; nessun nuovo APK.
