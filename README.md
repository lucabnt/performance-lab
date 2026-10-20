# Fuorigiri Performance Lab

Applicazione open source per analizzare, confrontare e archiviare test di ciclismo. Funziona prima di tutto offline, con un archivio locale separato per ogni società e condivisione facoltativa tra collaboratori.

**Sviluppato da Luca Bontempi per Progetto Ciclismo - Rodengo Saiano A.S.D.** Logo e attribuzione della società sono parte fissa del prodotto. Il progetto è generalizzabile a società e gruppi diversi.

## About the project

Fuorigiri Performance Lab is an open-source, offline-first application for cycling performance testing and athlete monitoring. It combines a Python analysis backend with a React/TypeScript interface to manage athletes, organisations, groups and versioned test protocols; analyse incremental, sprint and Wingate tests from FIT/CSV files or manual results; explore interactive histories; and export Markdown, PDF and CSV reports. Growth and maturation estimates retain their inputs, methods and limitations. Each organisation has a separate local archive, with optional encrypted synchronisation through WebDAV, Google Drive, Dropbox or OneDrive. Windows packaging includes application dependencies; Linux and Android build configurations and sources are present, but their builds and device validation remain pending.

## Stato attuale

Anteprima di sviluppo: versione dichiarata nei sorgenti **0.10.0**, con modifiche descritte nel [changelog](CHANGELOG.md). Una modifica ai sorgenti non aggiorna gli installer già prodotti.

- **Desktop:** Python/FastAPI, SQLite e oggetti locali; React/TypeScript e Plotly; finestra PySide6/Qt WebEngine. Packaging Windows con dipendenze incluse, ancora da qualificare su PC pulito per i sorgenti attuali.
- **Linux/Fedora e Android:** configurazioni e sorgenti presenti; build e collaudi rimandati. Android usa una shell Kotlin con interfaccia React e backend Python incorporato; nessun APK qualificato disponibile.
- **Cloud:** adapter implementati e verificati con fixture. Servono registrazioni OAuth per la distribuzione e collaudi con account reali distinti. Il servizio dedicato è predisposto come contratto/client, senza un servizio ospitato già disponibile.
- **Metodi:** risultati misurati, dichiarati, interpolati e stimati restano distinti e versionati. Le verifiche sintetiche non sostituiscono la validazione scientifica esterna.

## Funzionalità

- Profili atleta, società, categorie, gruppi stagionali e appartenenze datate; antropometria e storico individuale.
- Protocolli manuali o da ERG, anche senza step, versioni conservate e campi personalizzati facoltativi; test da FIT/CSV o solo manuali.
- Incrementali: ultimo step completo e aderenza distinti, riferimenti di soglia espliciti, zone configurabili, recupero, lattato e analisi specialistiche con limiti documentati.
- Sprint breve, Wingate 30 s e Wingate 15 s con metodi e confronti separati; importazione dello storico CSV.
- Grafici interattivi con segnali sovrapposti; storici e aggregati con media, mediana, numerosità e gestione dei mancanti.
- Crescita e maturazione: HV, stime Moore/Mirwald, PHV longitudinale esplorativo e analisi conservate. %PAH e residuo richiedono una previsione adulta esterna tracciata.
- Report gerarchici per società, gruppo, stagione e atleta in PDF/Markdown; esportazioni CSV standard ed estese.
- Archivi separati per società, inviti e ruoli, sincronizzazione cifrata v2 con blocchi riutilizzabili, conflitti, backup ZIP64 progressivi e separazione assistita degli archivi legacy. [Attivazione, compatibilità e limiti](docs/SYNC_V2_E_BACKUP.md).

## Provare l’interfaccia

La [guida di avvio e collaudo](docs/TESTARE_IL_PROGETTO.md) descrive installazione delle dipendenze di sviluppo, finestra desktop, browser e rigenerazione conservativa delle demo. Da un ambiente di sviluppo già predisposto, nella radice:

```powershell
npm --prefix frontend run build
.venv/Scripts/python.exe scripts/demo_suite.py --data .local/demo-nuova
.venv/Scripts/python.exe scripts/serve.py --data .local/demo-nuova --port 8766
```

Aprire l’URL completo stampato, incluso il token. Attendere il riepilogo finale del generatore prima di avviare il server; la preparazione delle repliche può richiedere alcuni minuti. Per una demo ridotta aggiungere `--small`. Su Linux usare `.venv/bin/python`.

Il generatore include test, crescita/maturazione, repliche admin/visualizzatore e backup con dati interamente fittizi. Rifiuta destinazioni esistenti: per rigenerarle conservando la copia precedente seguire la [procedura di reset](docs/TESTARE_IL_PROGETTO.md). Nessun dato personale degli allegati è incluso.

## Documentazione

L’[indice completo](docs/README.md) distingue guide attuali, specifiche e documenti storici.

| Per fare cosa | Documento |
|---|---|
| Avviare e collaudare app e interfaccia | [Guida di test](docs/TESTARE_IL_PROGETTO.md) · [Dati sintetici](docs/DATI_SINTETICI.md) |
| Gestire società, inviti, ruoli e ripristino | [Società, backup e accessi](docs/SOCIETA_BACKUP_E_ACCESSI.md) |
| Collegare cartella, WebDAV o cloud | [Configurazione sincronizzazione](docs/CONFIGURARE_LA_SINCRONIZZAZIONE.md) · [Limiti e scalabilità](docs/SYNC_DIMENSIONI_E_SCALABILITA.md) |
| Definire protocolli e campi facoltativi | [Protocolli e campi custom](docs/PROTOCOLLI_E_CAMPI_CUSTOM.md) |
| Conoscere metodi e limiti | [Incrementale](docs/METODI_INCREMENTALE.md) · [Sprint/Wingate](docs/TEST_ANAEROBICI.md) · [Maturazione](docs/MATURAZIONE.md) |
| Preparare distribuzione e mobile | [Distribuzione](docs/DISTRIBUZIONE.md) · [Android](docs/ANDROID.md) |
| Capire struttura e integrazione della suite | [Architettura](ARCHITETTURA_PROPOSTA.md) · [Componenti condivisi](docs/SUITE_CONDIVISA.md) |
| Contribuire e scegliere il prossimo lavoro | [Requisiti](docs/REQUISITI_E_TODO.md) · [Prossimi passi](docs/PROSSIMI_PASSI.md) · [Istruzioni repository](AGENTS.md) |
| Verificare ciò che è stato provato | [Registro verifiche](docs/VERIFICA.md) · [Changelog](CHANGELOG.md) |

## Licenza e dati

Codice distribuito sotto [GPL-3.0-or-later](LICENSE), con [avvisi delle dipendenze](THIRD_PARTY.md). Il marchio della società è distinto dalla licenza del codice.

Non pubblicare archivi locali, FIT personali, backup, inviti, token o chiavi. Sincronizzazione e backup hanno scopi distinti; conservare copie di recupero e verificarne il ripristino. Limiti attuali e qualifiche ancora necessarie sono descritti nella documentazione.
