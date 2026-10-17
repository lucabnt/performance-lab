# Ciclo Test

Applicazione desktop **Python + React/TypeScript**, archivio locale SQLite e shell PySide6/Qt WebEngine. Licenza **GPL-3.0-or-later**.

## Stato: anteprima di sviluppo 0.1

Prima implementazione eseguibile del percorso locale, non rilascio validato per uso operativo. Nessun dato personale degli allegati è incluso. Il nome Ciclo Test è provvisorio.

Disponibile:

- società, atleti, gruppi e appartenenze datate;
- rilevazioni di peso/statura;
- import ERG in catalogo, versioni immutabili e relazione con il protocollo precedente;
- import FIT tramite `fitdecode` (MIT), controllo CRC, potenza/FC/cadenza e pause;
- offset e termine sforzo manuali, anteprima e archiviazione;
- MAP operativa da ultimo step completo, interpolazione separata, W/kg, FC osservata e recupero;
- grafici interattivi del test e progressione separata per versione di protocollo;
- PDF, pacchetto Markdown con grafico, tre CSV con intestazioni concordate;
- backup consistente tramite SQLite backup API;
- trasporto sperimentale cifrato tramite cartella, con riconoscimento duplicati e conservazione dei conflitti.

Limitazioni esplicite:

- Nessun FIT reale degli esportatori è stato fornito: verificato con FIT sintetico e CRC, non certificato su GoldenCheetah/MyWhoosh/Zwift.
- La validità dello step usa durata e copertura potenza del 95%; non verifica aderenza al target. La convenzione va validata prima di usare i risultati operativamente.
- Protocollo a rampa leggibile/graficabile, ma MAP per step non calcolata. Più sessioni FIT e timestamp duplicati vengono rifiutati con messaggio.
- Ancora da implementare: editor manuale protocolli, confronto differenze, revisione di un test, formule configurabili e campi avanzati storici, recupero manuale, gruppi annidati, filtri storici completi, modifiche UI delle anagrafiche, cancellazioni reversibili.
- Sync sperimentale: scambio manuale dell'intero archivio locale con chiave condivisa, non selezione per società; conflitti conservati ma senza risolutore. Non usarlo per dati reali. Nessun portachiavi, rotazione chiavi, tombstone, snapshot/compattazione o revoca ancora implementati.
- Backup esportabile; ripristino guidato non ancora implementato. Backup e database locali non cifrati.
- Report generati su richiesta, non ancora conservati come artefatti immutabili. Analisi e protocollo associati al test restano salvati.
- Pacchetto Windows di prova senza firma/installazione; packaging Fedora/Flatpak e verifica su macchina Linux ancora da completare.

## Avvio da sorgente

Python 3.12+ e Node.js 22+ durante lo sviluppo. Utenti del pacchetto non necessitano di Python/Node installati.

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[desktop,dev]"
cd frontend
npm ci
npm run build
cd ..
.venv/Scripts/python.exe -m cycling_test.desktop
```

Linux: usare `.venv/bin/python` al posto del percorso Windows. L'archivio predefinito è `%LOCALAPPDATA%/CicloTest` su Windows e `~/.local/share/CicloTest` su Linux. `--data PERCORSO` sceglie un archivio diverso. `--browser` usa il browser di sistema al posto della finestra Qt.

```powershell
.venv/Scripts/python.exe scripts/demo.py
.venv/Scripts/python.exe -m cycling_test.desktop --data .local/demo
```

La demo usa **solo dati sintetici**, genera un archivio separato e non sovrascrive archivi esistenti. I file di prova vengono scritti in `tmp/qa/`.

I due ERG forniti sono disponibili in `examples/protocols/`, per l'importazione dal catalogo Protocolli. Non contengono dati personali. Indicare 600 secondi come fine del riscaldamento e confermare le convenzioni prima dell'uso.

## Verifiche e build

```powershell
.venv/Scripts/python.exe -m pytest -q
cd frontend
npm run build
cd ..
.venv/Scripts/python.exe scripts/build.py
```

Il bundle è in `dist/CicloTest/`: distribuire tutta la cartella, non solo l'eseguibile. PyInstaller va eseguito separatamente su ciascun sistema operativo. L'opzione `--smoke-test --data PERCORSO_TEMP` verifica import e risorse e scrive `smoke-ok.txt`, senza aprire finestre.

Il backend è limitato a loopback e richiede una credenziale effimera generata dalla shell. Nessuna esposizione in LAN. Nessuna risorsa UI caricata da CDN.

## Dati ed esportazioni

Il database è il modello operativo; i CSV non ne replicano tutte le relazioni. Le intestazioni compatibili sono in `backend/cycling_test/reports.py`. `manifest.json` collega test e versioni esatte; i soli CSV non costituiscono un backup. Il CSV è un export dati grezzi: trattare come testo le note importate in fogli di calcolo. Campi non disponibili restano vuoti. La colonna `map_alt_w` contiene l'interpolazione dichiarata dal nuovo metodo, senza equivalenza automatica ai metodi storici.

I dispositivi scambiano pacchetti cifrati, non il database SQLite aperto. Nella versione sperimentale il canale include tutto l'archivio selezionato all'avvio. Il programma può confermare la scrittura nella cartella, non l'upload del client cloud. Google Drive non ha client desktop ufficiale per Linux: serve una soluzione esterna verificata.

## Documenti

- `ARCHITETTURA_PROPOSTA.md`: architettura obiettivo; non tutto è implementato.
- `docs/DECISIONI.md`: decisioni confermate e scostamenti della prima implementazione.
- `THIRD_PARTY.md`: dipendenze e avvisi per la distribuzione.

Non pubblicare `.local/`, FIT reali, backup, token o chiavi. I file esclusi in `.gitignore` contengono dati runtime o build.
