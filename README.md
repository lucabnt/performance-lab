# Fuorigiri Performance Lab

Applicazione open source per analizzare, confrontare e archiviare test di ciclismo. Funziona prima di tutto offline, con un archivio locale separato per ogni società e condivisione facoltativa tra collaboratori.

**Sviluppato da Luca Bontempi per Progetto Ciclismo - Rodengo Saiano A.S.D.** Logo e attribuzione della società sono parte fissa del prodotto. Il progetto è generalizzabile a società e gruppi diversi.

## About the project

Fuorigiri Performance Lab is an open-source, offline-first application for cycling performance testing and athlete monitoring. It combines a Python analysis backend with a React/TypeScript interface to manage athletes, organisations, groups and versioned test protocols; analyse incremental, sprint and Wingate tests from FIT/CSV files or manual results; explore interactive histories; and export Markdown, PDF and CSV reports. Growth and maturation estimates retain their inputs, methods and limitations. Each organisation has a separate local archive, with optional encrypted synchronisation through WebDAV, Google Drive, Dropbox or OneDrive. Windows packaging includes application dependencies; Linux build configurations and sources are present; Linux packaging remains pending. An Android debug APK now runs on an x86_64 emulator with a native runtime smoke test; physical-device and complete workflow validation remain pending.

## Stato attuale

Candidato locale **0.10.0 · pilot-20261021-01** preparato (Windows installer/portabile e Android release non firmato): [checklist di collaudo](docs/COLLAUDO_PILOT.md) e [firma APK Android](docs/FIRMA_ANDROID.md). Versione prodotto 0.10.0; pacchetti locali e gate nel [registro verifiche](docs/VERIFICA.md), nessuna release pubblica.

Anteprima di sviluppo: versione dichiarata nei sorgenti **0.10.0**, con modifiche descritte nel [changelog](CHANGELOG.md). Una modifica ai sorgenti non aggiorna gli installer già prodotti.

- **Desktop:** Python/FastAPI, SQLite e oggetti locali; React/TypeScript e Plotly; finestra PySide6/Qt WebEngine. Packaging Windows con dipendenze incluse, ancora da qualificare su PC pulito per i sorgenti attuali.
- **Linux/Fedora:** configurazioni e sorgenti presenti; packaging e collaudo rimandati.
- **Android:** APK debug compilato e avviato su emulatore x86_64, con test del runtime nativo passato. Shell Kotlin, interfaccia React e backend Python incorporato; telefono e collaudo completo ancora aperti, nessuna release Android pubblicata.
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

## L’interfaccia in immagini

Schermate reali della versione **0.10.0**, aggiornate il **20 ottobre 2026**, con persone e risultati interamente sintetici. Mostrano l’interfaccia web condivisa con la finestra desktop; non rappresentano un collaudo Android. Cliccare un’immagine per aprirla a dimensione originale.

**Atleti e squadra** — profili, ricerca, gruppi e riepilogo dell’archivio della società.

[![Panoramica atleti di Fuorigiri con ricerca, filtri e risultati recenti](docs/screenshots/ui-coherence-010/atleti.png)](docs/screenshots/ui-coherence-010/atleti.png)

| Protocolli ripetibili | Analisi incrementale |
|---|---|
| [![Protocolli versionati, definizioni manuali e importazione ERG](docs/screenshots/protocolli.jpg)](docs/screenshots/protocolli.jpg) | [![Test incrementale con potenza, frequenza cardiaca, cadenza, VO₂ e prelievi di lattato sovrapposti](docs/screenshots/test-incrementale.jpg)](docs/screenshots/test-incrementale.jpg) |
| Creazione manuale o da ERG, famiglie e versioni conservate. | Tracciato unico con scale indipendenti e misure di lattato. |
| **Sprint e Wingate** | **Storici e confronti** |
| [![Wingate 30 secondi con tracciato e risultati della prova](docs/screenshots/test-wingate.jpg)](docs/screenshots/test-wingate.jpg) | [![Evoluzione stagionale della MAP con mediana, media e numerosità](docs/screenshots/storici-confronti.jpg)](docs/screenshots/storici-confronti.jpg) |
| Esempio Wingate 30 s; metodi e durate rimangono distinti. | Serie selezionate esplicitamente, aggregati e dati mancanti. |
| **Crescita e maturazione** | **Report ed esportazioni** |
| [![Profilo atleta con velocità di crescita, PHV esplorativo e stime datate](docs/screenshots/crescita-maturazione.jpg)](docs/screenshots/crescita-maturazione.jpg) | [![Report filtrabili per società, gruppo, stagione o atleta e importazione CSV](docs/screenshots/ui-coherence-010/archivio.png)](docs/screenshots/ui-coherence-010/archivio.png) |
| HV, analisi conservate e stime con metodo e limiti espliciti. | PDF e Markdown della società o delle sue sottosezioni; scambio CSV. |

### Android: navigazione compatta

Catture reali dell’APK debug su emulatore API 35 x86_64, 21 ottobre 2026, con società sintetica. Menu, Info, elenchi, moduli e grafici adattati al touch; il collaudo sul telefono resta aperto.

| Menu Android | Info |
|---|---|
| <a href="docs/screenshots/android-menu.png"><img src="docs/screenshots/android-menu.png" width="230" alt="Menu Android con società, sezioni, Info e lingua"/></a> | <a href="docs/screenshots/android-info.png"><img src="docs/screenshots/android-info.png" width="230" alt="Info Android con versione, logo societario, attribuzione e licenza"/></a> |

| Elenco atleti | Modulo con azione persistente |
|---|---|
| <a href="docs/screenshots/android-atleti.png"><img src="docs/screenshots/android-atleti.png" width="230" alt="Schede atleti e filtri richiudibili su Android"/></a> | <a href="docs/screenshots/android-modulo.png"><img src="docs/screenshots/android-modulo.png" width="230" alt="Modulo Android con Salva visibile durante lo scorrimento"/></a> |

<a href="docs/screenshots/android-grafico.png"><img src="docs/screenshots/android-grafico.png" width="270" alt="Grafico Android con Scorri pagina predefinito e comandi di esplorazione sotto la figura"/></a>

<a href="docs/screenshots/android-grafico-orizzontale.png"><img src="docs/screenshots/android-grafico-orizzontale.png" width="650" alt="Vista ampia Android immersiva: grafico orizzontale a tutto schermo con comandi richiamabili"/></a>

La [guida della galleria](docs/screenshots/README.md) descrive come riprodurre le viste e aggiornare immagini e didascalie insieme alle modifiche dell’interfaccia.

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

## Candidato Windows del 1 novembre 2026

Nuova consegna verificata `dist/candidates/Fuorigiri-0.10.0-pilot-20261101-01/`, con accessi CSV contestuali per Atleti/Gruppi/Test/Antropometria e punto completo espandibile in Archivio. Versione prodotto 0.10.0 invariata; ID candidato e checksum identificano i binari. Build e smoke del binario con PATH Windows superati; installer, 328 sorgenti congelati e 12 checksum verificati. Installer non firmato Authenticode; installazione su PC pulito e accettazione restano da eseguire. Nessun APK nuovo o aggiornamento operativo automatico.
