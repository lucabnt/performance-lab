# Fuorigiri Performance Lab

**Sviluppo suite:** primo pacchetto UI comune estratto in una repository autonoma e già consumato da Fuorigiri. [Integrazione con Ammiraglia e perimetro](docs/SUITE_CONDIVISA.md).

**Versione 0.8.0:** protocolli manuali/ERG e custom nel catalogo Protocolli; Nuovo test manuale o da file; campi facoltativi tipizzati con report e storici. [Guida aggiornata](docs/TESTARE_IL_PROGETTO.md) · [Corpus realistico completo](docs/CORPUS_SINTETICO_08.md) · [Campi custom](docs/PROTOCOLLI_E_CAMPI_CUSTOM.md).

**Funzioni introdotte in 0.7.0:** test Sprint/Wingate, importazione CSV storico, confronti separati e report; sincronizzazione diretta WebDAV/Google Drive/Dropbox/OneDrive e predisposizione servizio dedicato. [Uso e metodi anaerobici](docs/TEST_ANAEROBICI.md) · [Configurazione cloud e verifiche necessarie](docs/CLOUD_CONFIGURAZIONE_07.md). Le API cloud richiedono registrazione OAuth e collaudo con account reali. Windows e sorgenti; build Linux/Android ancora rimandate.

**Funzioni introdotte in 0.6.0:** sincronizzazione cifrata via WebDAV o cartella, credenziali nel portachiavi, accessi firmati versionati e rotazione recuperabile del canale. Icona Fuorigiri e installer Windows con dipendenze incluse; build Flatpak predisposta per Fedora. [Distribuzione, uso e limiti](docs/CONSOLIDAMENTO_DISTRIBUZIONE_06.md).

**Consegna attuale: Windows e sorgenti; build Linux/Android rimandate su richiesta dell’utente.**

**Android avviato nel sorgente, APK non ancora disponibile:** shell Kotlin/React, backend Python in-process, SAF/Keystore/WorkManager e test del contratto. Mancano wheel native aggiornate, toolchain POSIX/Android e collaudo del dispositivo. [Stato Android](docs/ANDROID.md).

**Versione 0.5.0:** preset e migrazione schema 3, motore incrementale aggiornato, allineamento/qualità, lattato/gas/ripetibilità e report completi di società, gruppo, stagione e atleta. [Funzioni, fonti scientifiche e limiti](docs/IMPLEMENTAZIONE_INCREMENTALE_05.md), [prova con dati sintetici e GUI](docs/TESTARE_IL_PROGETTO.md). Nessun ricalcolo automatico degli storici e nessuna importazione dei dati personali allegati.


[API cloud: verifica e disegno](docs/SINCRONIZZAZIONE_CLOUD_API.md), architettura 1.3: proposta di scambio diretto Drive/Dropbox su desktop e Android; ancora da implementare e collaudare con account reali.

Aggiornamento **0.4.1**: eseguibile `Fuorigiri.exe`, bundle `dist/Fuorigiri/`; rinomina tecnica con riconoscimento degli archivi precedenti. [Metodi incrementali, specifica 1.0](docs/METODI_INCREMENTALE.md) distingue convenzioni confermate e lavori ancora necessari. [Android](docs/ANDROID.md) è richiesto e pianificato dopo il consolidamento dell’incrementale desktop, prima dei test Sprint/Wingate; non ancora disponibile.


Applicazione desktop open source per analisi e archivio di test incrementali nel ciclismo. **Python + React/TypeScript**, SQLite locale, shell PySide6/Qt WebEngine. Licenza del codice **GPL-3.0-or-later**. Nome prodotto: **Fuorigiri Performance Lab**.

**Sviluppato da Luca Bontempi per Progetto CIclismo - Rodengo Saiano A.S.D.** Logo originale incluso in `frontend/public/branding/` e nel bundle finale. Logo, collegamenti e attribuzione sono fissi; le anagrafiche delle società non modificano il branding del prodotto.

## Stato: anteprima di sviluppo 0.6

Piano successivo confermato: completare tutte le lacune della copertura incrementale, inclusi ripristino/accessi e consolidamento operativo; poi Sprint breve / potenza neuromuscolare, Wingate 30 s e Wingate 15 s (già usato dalla società). [Requisiti TD-45–54](docs/REQUISITI_E_TODO.md) e [roadmap INC-01–11](docs/COPERTURA_TEST_E_ROADMAP.md). La 0.5 sviluppa l’analisi incrementale avanzata e i report gerarchici; collaudo esterno, consolidamento operativo, Android e nuovi test rimangono nelle fasi indicate.

Implementazione locale con dati sintetici e prove automatiche; richiede collaudo su PC puliti, Fedora, FIT reali e client cloud reali prima del rilascio operativo. Nessun dato personale degli allegati è incluso.


Novità 0.4: Gestisci società con creazione/invito/ripristino separati, bootstrap anche senza dati, tre modalità di ripristino, recupero cifrato del fondatore, ruoli visibili e cambio ruolo tramite nuovo invito. [Guida società, backup e accessi](docs/SOCIETA_BACKUP_E_ACCESSI.md).

Novità precedenti 0.3: selettore unico Società e Gestisci società, metriche leggibili, aggregati con media/mediana, archivio riordinato, protocolli senza step e nuovi test solo manuali, CSV con campi richiesti espliciti, PDF con footer societario e quattro FIT sintetici basati sugli ERG originali. [Requisiti e scelte UI](docs/REVISIONE_FUORIGIRI_03.md) · [Copertura e roadmap dei test](docs/COPERTURA_TEST_E_ROADMAP.md).

Per provare tutto con dati fittizi: `python scripts/demo.py --data .local/demo-fuorigiri`, poi `python scripts/serve.py --data .local/demo-fuorigiri`; aprire l'URL stampato. Il generatore rifiuta archivi già popolati. Non importare il CSV storico degli esempi nello stesso archivio che contiene già le esecuzioni FIT corrispondenti.

Disponibile:

- società, categorie con stagioni figlie, appartenenze datate e anno di categoria;
- modifica profilo, nascita completa/solo anno/ignota, antropometria manuale e grafici peso/statura;
- archiviazione, eliminazione reversibile e ripristino di atleti/protocolli, conservando i riferimenti storici;
- import ERG, editor di fasi costanti/rampe, versioni immutabili ed export ERG/JSON;
- import FIT o CSV temporale, anteprima del tracciato, offset e fine sforzo correggibili dopo il salvataggio tramite revisione;
- RPE 1–10, FC a riposo con durata, recupero manuale a tempi personalizzati, lattato con istante e coefficienti/riferimenti espliciti;
- proposta dell'ultima antropometria precedente e preset facoltativi con fonte/popolazione di riferimento, conservati come stime;
- MAP dall'ultimo step completo, interpolazione distinta, soglia da coefficiente dichiarato; FTP solo se fornita esplicitamente;
- zone FC/potenza con riferimenti selezionabili e numero configurabile oltre cinque; tempo valido in zona e mancanti distinti;
- import CSV di anagrafiche, antropometria e risultati storici con anteprima, errori per riga, ID esterni e commit transazionale;
- storici per atleta, categoria, anno di categoria, stagione e coorte; statistiche con modalità per atleta o tutti i test;
- variazioni antropometriche descrittive e confronti fra stagioni sugli stessi atleti e protocollo;
- report PDF e ZIP Markdown con grafici, logo, riferimenti e revisioni; conservazione degli artefatti;
- export dei tre CSV concordati e formato esteso separato per zone/relazioni;
- workspace separati per società, inviti cifrati per operatore/dispositivo, admin e visualizzatore, pacchetti cifrati/firmati e risoluzione conflitti;
- interfaccia IT/EN, tabelle ordinabili e backup dati consistente.

Limiti ancora presenti:

- Step valido: durata prevista e copertura potenza ≥95%, senza verifica dell'aderenza al target. Convenzione da validare con il referente del metodo.
- Rampe leggibili/graficabili, ma MAP per step costanti non applicabile. FIT multisessione e timestamp duplicati rifiutati esplicitamente.
- Metodi lattato espliciti disponibili nella 0.5; maturazione/PHV e benchmark esterni non definiti. Sprint breve, Wingate 30 s e 15 s restano sviluppi confermati successivi ad Android.
- IT/EN copre navigazione, form e titoli principali dei report. Alcune diagnostiche, descrizioni dei metodi, controlli Plotly e testi secondari restano italiani/inglesi; localizzazione integrale da completare.
- Scambio manuale. Revoca delle scritture recepita al prossimo scambio, senza cancellazione delle copie o rotazione automatica delle chiavi di lettura. Segreti locali protetti dall'account/filesystem; portachiavi, trasferimento esclusivo dell’autorità e rotazione completa ancora da completare. Recupero guidato dati/accessi disponibile.
- Archivio precedente accessibile, senza migrazione automatica nei workspace. Per nuove condivisioni creare un workspace separato.
- Backup dati ZIP e ripristino guidato disponibili; recupero cifrato delle credenziali del fondatore esportabile separatamente. DB e backup dati standard non cifrati.
- Bundle Windows di sviluppo, senza installer/firma. Fedora/Flatpak e prove su macchine pulite ancora da eseguire.

## Avvio e test della GUI

La [guida completa al collaudo](docs/TESTARE_IL_PROGETTO.md) contiene installazione Windows/Fedora, test automatici, desktop/browser, Vite, fixture sintetiche e checklist per due dispositivi e ruoli.

Da un ambiente già preparato, dopo `npm run build` in `frontend/`:

```powershell
.venv/Scripts/python.exe scripts/demo.py --data .local/ui-test
.venv/Scripts/python.exe -m cycling_test.desktop --data .local/ui-test
```

Server browser senza finestra Qt:

```powershell
.venv/Scripts/python.exe scripts/serve.py --data .local/ui-test --port 8766
```

Aprire l'URL completo stampato, incluso il token. Su Linux usare `.venv/bin/python`. La demo rifiuta un archivio già popolato: riutilizzarlo per l'avvio o scegliere un nuovo percorso per rigenerarla.

```powershell
.venv/Scripts/python.exe -m pytest -q
```

Backend su loopback con token di sessione; asset UI locali. CSV temporali in secondi/W/bpm/rpm, colonne `t,power,hr,cadence`. Lo storico privo di campioni resta dichiarato.

## Distribuzione e documenti

Dopo la build frontend eseguire `.venv/Scripts/python.exe scripts/build.py`. Distribuire tutta `dist/Fuorigiri/`, non il solo EXE. PyInstaller va eseguito sul sistema destinatario. La guida descrive `--smoke-test` e verifica su PC pulito.

- [Architettura](ARCHITETTURA_PROPOSTA.md)
- [Requisiti e stato](docs/REQUISITI_E_TODO.md)
- [Guida di test, inclusa la GUI](docs/TESTARE_IL_PROGETTO.md)
- [Verifiche effettuate](docs/VERIFICA.md)
- [Decisioni](docs/DECISIONI.md)
- [Changelog](CHANGELOG.md)
- [Licenze delle dipendenze](THIRD_PARTY.md)

Non pubblicare `.local/`, FIT reali, backup, inviti, token o chiavi. Dati runtime e build sono esclusi da `.gitignore`. Il marchio della società è distinto dalla licenza GPL del codice.
