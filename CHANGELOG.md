# Changelog

## 0.5.0 — 17 ottobre 2026 / architettura 1.3

- Schema 3 con copia del database pre-migrazione, preset immutabili e identità dell’analisi salvata, risultati legacy invariati e separati nei confronti.
- Motore incrementale versionato: coperture senza arrotondamento, aderenza separata, finestre FC/recupero, marker/esclusioni, rampe/discontinui descrittivi, condizioni e RPE per scala.
- Import FIT con scelta sessione, correzioni esplicite e timer; import gas CSV; lattato a 2/4 mmol, Dmax cubico/modificato, VO2peak, grafici e suggerimenti ventilatori da revisione, ripetibilità con incertezza descrittiva ed export.
- Report società/gruppo/stagione/atleta da modello comune, PDF e Markdown con grafici, copertura, aggregati, schede e provenienza; qualità e analisi specialistiche anche nel singolo test.
- Fixture sintetiche e verifiche aggiunte; fonti scientifiche e limiti documentati. Nessuna importazione dei dati personali del PDF, validazione clinica o certificazione generale degli esportatori dichiarata.


## Architettura 1.2 — 17 ottobre 2026 / software invariato 0.4.1

- WebDAV confermato per Windows/Fedora e Android: TD-59/CLOUD-02, non più candidato.
- Aggiornati ordine degli adapter, criteri desktop/mobile e piano dei prossimi passi; nessuna integrazione o credenziale attivata.


## Architettura 1.1 — 17 ottobre 2026 / software invariato 0.4.1

- Verificate API ufficiali Drive, Dropbox, OneDrive e Nextcloud/WebDAV; documentati consenso OAuth, limiti dell’accesso per cartella, collaborazione con account distinti e sincronizzazione offline.
- Aggiunti CLOUD-01/UI-19 e TD-58: adapter comuni, spike Drive con permessi minimi e due account, migrazione/scambio, test di accettazione; Dropbox condiviso distinto da App Folder.
- Aggiornato il disegno Android: API cloud come obiettivo ordinario, SAF/import-export come alternative. Nessuna integrazione attivata, account collegato o prova autenticata eseguita.

## 0.4.1 — 17 ottobre 2026 / architettura 1.0

- Formalizzati metodi incrementali, convenzioni confermate, formule, finestre, provenienza/versioni, casi di accettazione e scostamenti dal motore corrente. Nessun cambio di algoritmo o ricalcolo dei test in questo step.
- Nome Fuorigiri esteso a pacchetto, comandi, header, variabili, nomi scaricati e bundle/eseguibile; riconoscimento di archivi e canali precedenti senza modificare identità o chiavi. Superata la precedente scelta UI-16.
- Aggiunto sviluppo Android TD-57/AND-01–05, dopo consolidamento incrementale desktop e prima di Sprint breve/Wingate; proposta architetturale, limiti del cloud su Android, UI-18 e criteri di collaudo.
- Aggiornati requisiti, decisioni, architettura e guida di prova. I nuovi metodi specialistici e l’app Android non sono ancora implementati.


## Software 0.4.0 / architettura 0.9 — 17 ottobre 2026

- TD-45/UI-17: tre percorsi distinti Crea nuova società, Collega tramite invito, Ripristina da backup; selezione automatica e crediti societari fissi conservati.
- TD-46/47/REC-01: backup dati schema 2 con checksum, lettura schema 1, anteprima e ripristino validato/atomico in destinazione nuova. Consultazione senza privilegi, copia indipendente con nuove credenziali e provenienza, oppure recupero originale con file del fondatore cifrato separatamente. Verifica delle firme, password e società; nessun segreto nel normale ZIP dati.
- TD-48: corretta la prima sincronizzazione della società associata ancora vuota; cartella, errori e ultimo scambio visibili.
- TD-49: ruolo/dispositivo correnti visibili, controlli di scrittura in UI/API, elenco pubblico firmato, rinnovo/cambio ruolo con nuovo invito applicabile alla stessa copia; un visualizzatore può gestire l’aggiunta di archivi indipendenti senza ottenere diritti sulla società selezionata.
- TD-50 parziale: revoca conservativa con hash esatti degli eventi già acquisiti; restano da sviluppare audit completo, portachiavi e rotazione del canale in INC-11.
- Ripristini e creazioni pubblicati solo a operazione completa; percorsi occupati/sovrapposti rifiutati. Ridotto il nome temporaneo degli allegati per evitare MAX_PATH su Windows.
- Aggiunte 13 prove automatiche (45 totali) e guida SOCIETA_BACKUP_E_ACCESSI.md; collaudo GUI su fixture sintetiche. Nessun nuovo motore di analisi dell’incrementale o dei test successivi.


## Architettura 0.8 / requisiti — 17 ottobre 2026

**Tipo: aggiornamento documentale; software invariato alla 0.3.0.** Recepita la richiesta di registrare le osservazioni sugli accessi e confermare il perimetro dei prossimi sviluppi.

- TD-45–50: distinti creazione società, collegamento con invito e ripristino ZIP; registrati ripristino dati mancante, recupero identità del fondatore separato, difetto della prima sincronizzazione con archivio vuoto, gestione comprensibile di operatori/dispositivi/ruoli e limiti della revoca offline. Scelte UI-17 e REC-01.
- TD-51 / INC-01–11: tutte le lacune per la copertura completa dell'incrementale diventano requisiti confermati da implementare, comprese priorità P2, scambi gassosi nell'incrementale e tutti i punti di consolidamento operativo/distributivo. Aggiunti ID stabili e checklist di accettazione; nessuna voce dichiarata completata.
- TD-52–54: fase successiva riservata a Sprint breve / potenza neuromuscolare, Wingate 30 s e Wingate 15 s. Registrato l'uso storico del 15 s nella società, con necessità di ricostruire il protocollo e mantenere separate durate, versioni e confronti; nessuna equivalenza fisiologica o conversione presunta.
- Allineati registro principale, roadmap, decisioni e architettura. Gli altri test rimangono candidati, senza implementazione autorizzata da questa pianificazione documentale.

## Software 0.3.0 / architettura 0.7 — 17 ottobre 2026

- Nome Fuorigiri Performance Lab in UI, finestra e report; dati e identificatori tecnici compatibili.
- Selettore Società unico, gestione società globale e pagine archivio/storici riordinate; dialoghi opachi con blocco dello scorrimento sottostante.
- Nomi delle metriche leggibili, unità e aggregati con media/mediana; report storico sulla metrica/statistica selezionata.
- Protocollo d'archivio senza step, test manuale senza FIT, nome figlio ereditato dalla categoria.
- Contratto CSV con campi richiesti/facoltativi e controlli su intestazioni, righe e valori mancanti; import a lotti con anteprima e commit atomico.
- PDF uniformati con blu societario, tabelle compatte, logo e attribuzione fissa nel footer di tutte le pagine; nuova versione della cache report.
- Quattro FIT simulati riproducibili dagli ERG originali, CSV sintetici e demo costruita dai medesimi file; sei nuovi casi automatici.
- Registro TD-30–44, scelte UI-11–16, lacune del motore incrementale e roadmap di sprint/CP/FTP/lattato/VO2 con fonti primarie.


Le versioni dell'architettura sono distinte da quelle del programma. Ogni voce deve indicare data, natura della modifica, motivo e identificatori di requisiti/decisioni. Una modifica documentale non certifica l'implementazione della funzione.

## Software 0.2.0 / Architettura 0.6 — 2026-10-17

**Tipo: implementazione e collaudo locale**, dopo approvazione delle scelte e ripresa del lavoro interrotto.

- Logo originale aggiunto in `frontend/public/branding/`, incluso nel bundle Vite/PyInstaller e nei report. Branding reso fisso su richiesta successiva: «Sviluppato da Luca Bontempi per Progetto CIclismo - Rodengo Saiano A.S.D.» (TD-02/03/26; UI-02/03). Le società non possono personalizzarlo.
- Implementati modifica profilo, nascita completa facoltativa, categorie/stagioni e anno di categoria, ciclo di vita reversibile di atleti/protocolli e filtri storici (TD-09/10/13/14/24).
- Aggiunti editor protocolli con fasi e versioni, export ERG/JSON e tabelle ordinabili (TD-08/11/12). Confronto grafico delle differenze ancora futuro.
- Import FIT/CSV temporale, lattato/RPE/recupero manuale, coefficienti e riferimenti, proposta ultima antropometria e preset stimati con fonte; revisioni successive di test con campioni e risultati storici (TD-15/21/22/23/29).
- Zone a numero variabile per FC/potenza, confini concordati senza arrotondamento preventivo, tempi validi in zona, report dinamici ed export lungo separato (TD-28; ZONE-01).
- Import CSV dei tre profili con anteprima, riconciliazione ID, errori per riga, commit atomico e riconoscimento duplicati (TD-07). Adapter di colonne arbitrarie ancora futuro.
- Storici per atleta/categoria/anno/stagione/coorte, statistiche per metrica, modalità ultimo test per atleta o tutti i test, variazioni antropometriche e confronto appaiato (TD-04/05/17/18).
- Report MD/PDF di storico con manifest, branding e revisioni; conservazione degli artefatti e download delle versioni precedenti; CSV compatibili più formato esteso (TD-16).
- Workspace separati, inviti cifrati per operatore/dispositivo, ruoli admin/visualizzatore, firma delle operazioni e risoluzione conflitti. Revoca delle scritture propagata allo scambio; limiti di lettura e credenziali locali documentati (TD-19/20).
- Aggiunta infrastruttura IT/EN, selettore GUI e titoli dei report; localizzazione completa delle diagnostiche ancora parziale (TD-06).
- Aggiunta [guida per testare anche la GUI](docs/TESTARE_IL_PROGETTO.md), script server locale, fixture sintetiche FIT/ERG/CSV e istruzioni Vite. Aggiornati README, registro requisiti, decisioni e verifiche.
- Nessuna formula scientifica non concordata introdotta. Nome suite, modelli avanzati di maturazione, modulo anaerobico, portachiavi/recupero, rilascio Fedora e verifiche cloud reali restano esplicitamente aperti.
- Nel collaudo del bundle Windows individuata una DLL ICU di Poppler raccolta dal PATH, incompatibile con Qt. Isolato il PATH del sottoprocesso di build; il PATH del sistema non viene modificato. La verifica del bundle comprende caricamento Qt WebEngine, presenza del logo e avvio/health del backend HTTP. Logging desktop reso indipendente dalla console, con errore di avvio esplicito e test senza stdout/stderr.

## Architettura 0.5 — 2026-10-17

**Tipo: conferme, valutazione allegati e specifica; nessuna modifica funzionale al software.**

- Registrata accettazione delle convenzioni per categorie/stagioni, ciclo di vita, revisioni, aggregazioni per atleta, ruoli e confini della suite.
- Esaminato archivio_test.pdf e aggiunta [specifica storico, zone e branding](docs/STORICO_ZONE_E_BRANDING.md): nove viste HIST-01–09, fattibilità e prerequisiti, modalità tutti i test distinta dal default per atleta, anno di categoria distinto da stagione/coorte, copertura per metrica e confrontabilità.
- Documentati limiti: soglie storiche stimate da distinguere da misure; nessuna statura disponibile per crescita in altezza; risultati anaerobici importabili come estensione candidata ANA-01, senza assumere approvato un nuovo motore di calcolo. Non copiati dati personali nei documenti di progetto.
- Acquisito il logo fornito dall'utente come riferimento UI-02/03, con colori rilevati nel file e regole d'uso; nessuna modifica all'asset o alla UI.
- Registrate le tabelle originali delle zone e la normalizzazione dei confini confermata dall'utente, incluso il 55% di potenza in Z1 (TD-28/D26). Esempi numerici sintetici e controlli attesi.
- Aggiunto ZONE-01: numero di zone configurabile oltre cinque, indipendente per FC/potenza; schema a lista, editor, rendering ed export esteso dinamici. Cinque zone restano il preset iniziale, non il limite del programma.
- Aggiornati architettura, decisioni e backlog. Verificati collegamenti locali e calcoli degli esempi ai confini; nessun test applicativo necessario per questa modifica documentale.

## Architettura 0.4 — 2026-10-17

**Tipo: documentazione e disegno; nessuna modifica funzionale al software.** Revisione richiesta dopo i commenti dell'utente nella sezione To-Do.

- Trasferiti tutti i 29 commenti in [Requisiti e to-do](docs/REQUISITI_E_TODO.md), riscritti con ID TD-01–29, stato e criteri verificabili; conservata la [trascrizione originale](docs/COMMENTI_ORIGINALI_2026-10-17.md). Aggiunto SUITE-01 per l'app gemella.
- Registrate le parti già presenti: flusso ERG con codice/step/riscaldamento iniziale e inserimento manuale antropometrico; distinte dalle richieste composte ancora incomplete (TD-01/08/14).
- Esteso il modello con categorie/stagioni, nascita completa facoltativa, ciclo di vita di atleti/protocolli e revisioni manuali dei test (TD-09/10/13/24/29; D20–22).
- Promosso l'import CSV da estensione futura a requisito, distinguendo risultati storici e serie temporali; dettagliato editor/export ERG (TD-07/11/15; D19).
- Integrati lattato, coefficienti, FC pre-test/recupero, RPE e proposte da storico/preset, con provenienza e separazione fra stime e misure; introdotto il contratto delle zone (TD-15/21/22/23/28; D26). Preset numerici e metodi avanzati restano da validare.
- Definiti aggregati, confronti, crescita descrittiva e report di atleta/categoria/stagione con popolazione e revisioni congelate (TD-04/05/16/17/18; D23).
- Aggiornata la collaborazione: archivi e cartelle per società, ruoli admin/visualizzatore e verifica delle scritture ricevute. Esplicitati limiti della revoca offline e differenza fra cifratura e autorizzazione (TD-19/20; D07).
- Aggiunto nell'architettura il registro UI-01–10: branding blu/giallo proposto, logo e crediti, nuovo motto, IT/EN, grafici, tabelle ordinabili, accessibilità e componenti comuni (TD-02/03/05/06/12/25/26; D24).
- Disegnati confini della suite, librerie e contratti condivisi con DB separati; proposti nomi coordinati senza rinominare la preview (SUITE-01; D25).
- Aggiunta [ricognizione dei prodotti](docs/CONFRONTO_PRODOTTI.md) con fonti ufficiali e candidati separati dai requisiti approvati (TD-27).
- Aggiornati piano e verifiche attese. Verificata la copertura dei 29 commenti, i collegamenti locali dei documenti e la coerenza del registro. Non rieseguiti test applicativi: intervento solo documentale.

## Stato precedente

Il documento di partenza era Architettura 0.3 del 16 ottobre 2026, con preview locale 0.1. Questo changelog viene istituito il 17 ottobre: non ricostruisce retroattivamente un elenco completo di modifiche o rilasci precedenti. Lo stato tecnico precedente resta descritto in [README](README.md), [decisioni](docs/DECISIONI.md) e [verifiche](docs/VERIFICA.md).
