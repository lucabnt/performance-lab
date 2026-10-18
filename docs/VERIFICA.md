# Verifiche locali — Fuorigiri Performance Lab

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
