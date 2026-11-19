# Analisi delle alternative e decisione «build vs adopt» — 18 novembre 2026

Ambito: Fuorigiri Performance Lab 0.10.0 (questa repository). La suite (Ammiraglia, `cycling-suite-common`, futura app Allenamenti) è citata solo dove incide sulla decisione. Nessun file di codice è stato modificato. Le verifiche web sono del **18 novembre 2026**; dove un dato non è stato verificato è scritto «n.v.».

## 1. Sintesi

**Verdetto: opzione E — continuare lo sviluppo, riducendo il perimetro generico e appoggiandosi a strumenti esistenti dove non c'è valore distintivo.** Confidenza: media.

- Nessuna alternativa verificata copre insieme ciò che Fuorigiri fa già: protocolli incrementali con lattato, VO₂, Sprint/Wingate separati, crescita/maturazione con provenienza e snapshot, report per società/gruppo/stagione, uso offline senza server e dati di minori sotto il controllo della società.
- Le alternative mature (GoldenCheetah, Intervals.icu, TrainingPeaks/WKO5, INSCYD) sono centrate sull'**allenamento quotidiano del singolo atleta** o sulla **modellazione metabolica a pagamento**, non sull'archivio dei test di un vivaio. Le piattaforme di monitoraggio per club (Teamworks AMS, ex Smartabase) sono enterprise e con prezzo su preventivo.
- Il rischio principale non è la duplicazione ma la **sostenibilità**: circa 38 mila righe tra sorgenti, test e script, un solo autore, e costi elevati in parti non distintive (provider cloud nativi, filiera di wheel native Android, firma e Defender su Windows).
- Azioni chiave: congelare i provider Drive/Dropbox/OneDrive nativi (restano WebDAV e cartella), usare `lactater`, `lactate-thresholds`, `matuR` e `sitar` come **oracoli di validazione** e non riscrivere ciò che fanno, togliere dalla roadmap l'app Allenamenti (coperta da Intervals.icu, TrainingPeaks e OpenAthlete) e il server opzionale.

### Decisioni dell'autore sul report (18 novembre 2026, PERIMETRO-01)

- **Accolto:** Google Drive, Dropbox e OneDrive diretti diventano sperimentali; WebDAV e cartella restano i trasporti supportati.
- **Accolto con variante:** l'app allenamenti A Ruota Training Lab è **sospesa**, non eliminata. Fuorigiri si limita al pulsante verso Intervals.icu, senza esportazioni verso piattaforme di allenamento.
- **Accolto con variante:** il server opzionale resta fra gli sviluppi futuri da considerare, ma non è in sviluppo.
- **Deciso diversamente dal suggerimento di §7:** Android resta un'**app completa**; l'autore giudica buono il livello raggiunto. Il costo della filiera nativa resta un rischio da monitorare.

Registrazione in [REQUISITI_E_TODO.md](REQUISITI_E_TODO.md), [ARCHITETTURA_PROPOSTA.md](../ARCHITETTURA_PROPOSTA.md) e [PROSSIMI_PASSI.md](PROSSIMI_PASSI.md).

## 2. Il progetto ricostruito dal repository (Fase 0)

### 2.1 Problema e utenti
Tecnici, preparatori e operatori non tecnici di società ciclistiche giovanili (nato per Progetto Ciclismo Rodengo Saiano, generalizzabile) devono archiviare, analizzare e confrontare nel tempo test di laboratorio e di campo, antropometria e maturazione, per atleta, gruppo e stagione. Devono produrre report e conoscere la provenienza di ogni dato, condividendo l'archivio fra pochi collaboratori senza un server.

### 2.2 Requisiti funzionali

| ID | Requisito | Stato | Dove |
|---|---|---|---|
| R1 | Società, atleti, categorie, gruppi, stagioni, appartenenze datate | Implementato | `registry_api.py`, `workspaces.py`, `membership_import.py`, GRUPPI-02/03 |
| R2 | Antropometria con fonte del peso, IMC descrittivo, altezza perineale | Implementato | `observations.py`, ANTRO-PERINEALE-01, ANTRO-INCREMENTALE-01 |
| R3 | Protocolli versionati da ERG o manuali, campi personalizzati | Implementato | `custom_fields.py`, `custom_tests.py`, `frontend/src/protocols.tsx` |
| R4 | Import FIT e CSV (cinque profili, anteprima, `plan_hash`) | Implementato | `fit.py` (fitdecode), `csv_import.py`, `docs/IMPORT_CSV.md` |
| R5 | Analisi incrementale: ultimo step completo, copertura ≥95%, aderenza | Implementato | `analysis.py`, `docs/METODI_INCREMENTALE.md` |
| R6 | Lattato con livelli configurabili, interpolazione locale | Implementato | `specialist.py::lactate` |
| R7 | VO₂ da un'unica fonte gas, VO₂peak con finestre | Implementato | `specialist.py::gas_analysis`, VO2Input.tsx |
| R8 | Sprint, Wingate 30 s e 15 s come metodi distinti | Implementato | `anaerobic.py`, `docs/TEST_ANAEROBICI.md` |
| R9 | Zone di allenamento da test, con profilo latest/test/custom | Implementato | `training_zones.py`, `zones.py` |
| R10 | Crescita e maturazione: HV, Moore/Mirwald, PHV longitudinale, snapshot | Implementato (validazione esterna aperta, Khamis–Roche assente) | `maturation.py`, MAT-PHV-01, `docs/MATURAZIONE.md` |
| R11 | Storici e aggregati con numerosità, mediana, mancanti | Implementato | `history.py`, `history_report.py` |
| R12 | Report PDF/Markdown per società, gruppo, stagione e atleta; export CSV | Implementato | `reports.py`, `archive_report.py`, `archive_pdf.py`, `csv_safety` |
| R13 | Revisioni, eliminazione recuperabile, nessun ricalcolo silenzioso | Implementato | `store.py`, RECORD-LIFECYCLE-01 |
| R14 | Condivisione cifrata e firmata senza server, ruoli admin/visualizzatore, inviti | Implementato su cartella/WebDAV; parziale per Drive/Dropbox/OneDrive (codice presente, non qualificato) | `sync_v2.py`, `cloud.py`, `access.py`, `docs/SYNC_V2_E_BACKUP.md` |
| R15 | Backup ZIP64 v3 e backup protetto da password `.fgbak` | Implementato | `backup_stream.py`, `backup_crypto.py` |
| R16 | Desktop Windows | Parziale: build prodotte; Windows pulito, Defender (WIN-AV-01) e firma aperti | `packaging/`, `docs/WINDOWS_DEFENDER.md` |
| R17 | Android | Parziale: APK su emulatore; telefono, firma release e pagine da 16 KB aperti | `android/`, `docs/ANDROID.md`, `docs/REVISIONE_ALPHA.md` |
| R18 | IT/EN, accessibilità | Parziale (QA-RELEASE-01) | `i18n.ts` |
| R19 | Link a Intervals.icu (solo URL) | Implementato | INT-ICU-01 |
| R20 | Linux/Fedora, server opzionale, app Allenamenti | Solo pianificati o rinviati | `ARCHITETTURA_PROPOSTA.md` §10.4, §15 |

### 2.3 Requisiti non funzionali
Offline first, nessun server applicativo (preferenza per **costi, privacy e facilità di configurazione**, confermata dall'autore). Windows e Android (Linux rinviato). Cifratura e firma dei pacchetti, segreti nel portachiavi di sistema. Dati antropometrici e fisiologici di minori. Interfaccia IT/EN per operatori non tecnici. Provenienza del dato e metodi versionati. Branding fisso. Licenza GPL-3.0-or-later.

### 2.4 Stack e dipendenze
Python ≥3.12, FastAPI e uvicorn, SQLite, numpy, matplotlib, reportlab, fitdecode, cryptography, pydantic. React 19, TypeScript, Vite, Plotly. PySide6 con Qt WebEngine. Android: Kotlin, WebView, Chaquopy. Librerie proprie `cycling-suite-core` (wheel) e `@cycling-suite/ui` (tgz). CI GitHub Actions su Windows (`verify.yml`); build desktop e Android manuali.

### 2.5 Maturità
- Git: 63 commit dal 17 ottobre al 15 novembre 2026, un solo autore. Il primo commit sembra uno snapshot: la storia reale può essere più lunga.
- Dimensioni (file tracciati): backend Python ≈12,8k righe, frontend ≈13,4k, test ≈6,9k (252 funzioni pytest più 13 file frontend), script ≈4,9k, Android ≈0,5k. Documentazione ≈6,5k righe Markdown. A queste si aggiungono le librerie comuni.
- Stima: ≈80% del perimetro funzionale dell'alpha; ≈50–60% verso una distribuzione usabile da altre società, per i gate esterni ancora aperti (firma, telefoni reali, PC pulito, provider reali, validazione scientifica).
- Issue, PR e stelle: n.v. (`gh` non disponibile).

### 2.6 Componenti

| Generici | Distintivi |
|---|---|
| Identità, ruoli, inviti (scrypt, firme) | Modello dei test di ciclismo con provenienza (misurato/dichiarato/stimato) |
| Sincronizzazione cifrata e trasporti cloud (WebDAV, Drive, Dropbox, OneDrive) | Motori incrementale, lattato e VO₂ con metodi versionati e snapshot |
| Backup e ripristino, anche cifrato | Sprint/Wingate 15–30 s non mescolati, import dello storico della società |
| Archivio SQLite con revisioni e audit | Crescita/maturazione con gate di qualità e PHV esplorativo |
| Import CSV con anteprima | Protocolli ERG versionati e campi custom tipizzati |
| Motore PDF, grafici, i18n, kit UI | Report gerarchici società/gruppo/stagione con mancanti e numerosità |
| Shell desktop e Android, packaging, portachiavi | Appartenenze stagionali di un vivaio |

### 2.7 Ipotesi confermate
Uso interno più distribuzione open source gratuita ad altre società (niente SaaS). Scala: decine di atleti e centinaia di test. «Nessun server» è una preferenza per costi, privacy e facilità di configurazione, non un vincolo assoluto. Un solo sviluppatore con assistenza AI, nessun budget per licenze.

## 3. Tabella comparativa delle alternative

| Soluzione | Descrizione | Licenza / costo | Salute del progetto | Stack ed estendibilità | Compatibilità con l'uso previsto |
|---|---|---|---|---|---|
| [GoldenCheetah](https://www.goldencheetah.org/) | Analisi di potenza desktop per ciclisti e coach | GPL-3.0, gratuito | ≈2,3k stelle, 480 fork, 11.462 commit, 50 issue aperte; 3.8 indicata come stabile sul sito, sviluppo attivo nel 2026 (build DEV2601) | C++/Qt; metadati e metriche personalizzate, grafici configurabili | Licenza compatibile (GPL-3.0). Orientato al singolo atleta; multi-atleta dalla 3.6; niente Android |
| [Intervals.icu](https://www.intervals.icu/pricing) | Piattaforma web di analisi e pianificazione, con funzioni coach | Proprietaria; gratuita, Supporter 4 $/mese per team e organizzazioni | Attiva (forum e funzioni nuove); finanziamento da abbonamenti; numero di sviluppatori n.v. | SaaS con API, campi wellness e campi intervallo personalizzati, JavaScript personalizzato | Dati sui server del fornitore; nessun uso offline. Già collegata da Fuorigiri (INT-ICU-01) |
| [TrainingPeaks Coach](https://www.trainingpeaks.com/pricing/for-coaches) + [WKO5](https://www.trainingpeaks.com/products/wko5/) | Piattaforma coach commerciale e software desktop di analisi | Proprietaria; Coach 21,99 $/mese, Unlimited 54,99 $/mese; WKO5 169 $ (PC, prezzo da confermare) | Commerciale consolidata | SaaS; WKO5 desktop | Costi ricorrenti; dati nel cloud; metodi non ispezionabili |
| [INSCYD](https://inscyd.com/pricing/) | Profilazione metabolica da lattato, potenza, gas | Proprietaria; da 49 €/mese per coach con atleti illimitati | Commerciale | Servizio online; integra misuratori di lattato e metabolimetri | Modello proprietario (VLamax, MLSS): non verificabile come richiesto dai principi del progetto |
| [OpenAthlete](https://github.com/openathleteorg/openathlete) | «Alternativa open source a TrainingPeaks», self-hosted | AGPL-3.0; 5 atleti gratis, illimitati con Supporter | 142 stelle, 1.765 commit, sviluppo attivo; giovane | React, Capacitor, NestJS, PostgreSQL, Redis | Richiede server; nessun lattato, antropometria o offline citati |
| [Teamworks AMS](https://explore.teamworks.com/transition-ams) (ex Smartabase) | Piattaforma di monitoraggio per club e federazioni | Proprietaria; prezzo su preventivo, con costo di attivazione | Commerciale enterprise | Moduli e calcoli configurabili, API | Fuori scala e budget per una società giovanile |
| [Grist](https://github.com/gristlabs/grist-core) (core + desktop) | Foglio di calcolo relazionale, desktop offline e server self-hosted | Apache-2.0 (open core) | Attivo; finanziato da Grist Labs | Formule, widget personalizzati | Soluzione low-code: archivio rapido, ma metodi, provenienza e report da costruire a mano |
| [wger](https://github.com/wger-project/wger) | Gestione allenamenti e misure, uso anche come piccola palestra | AGPL-3.0 | Release 2.6/2.7 nel 2026; app su F-Droid | Django, REST API, app Flutter | Fitness generico; nessuna analisi di test ciclistici |
| [Endurain](https://github.com/joaovitoriasilva/endurain) | Tracciamento attività self-hosted (alternativa a Strava) | AGPL-3.0 | ≈2,4k stelle; **feature freeze** temporaneo | Vue, FastAPI, PostgreSQL, fitdecode | Attività, non test di laboratorio |

Strumenti di nicchia: [Exphyslab](https://knowledgeiswatt.substack.com/p/first-lactate-threshold-lt1-web-app) (web gratuito per soglie di lattato, descrizione di terzi, n.v. sul sito), il [calcolatore di maturazione dell'Office of Sport NSW](https://www.sport.nsw.gov.au/pathways-and-development/maturity-status-calculator) (YPHV Mirwald e %PAH) e l'app iOS Lact8. Nessun prodotto italiano specifico per l'archivio dei test di un vivaio ciclistico è emerso dalla ricerca.

## 4. Matrice di copertura dei requisiti

Legenda: ✅ coperto · 🟡 parziale, tramite estensione o a mano · ❌ assente · ? non verificato.

| Requisito | Fuorigiri | GoldenCheetah | Intervals.icu | TP + WKO5 | INSCYD | OpenAthlete | Teamworks AMS | Grist |
|---|---|---|---|---|---|---|---|---|
| R1 Gruppi, stagioni, appartenenze datate | ✅ | 🟡 multi-atleta | 🟡 team e tag | 🟡 | ? | 🟡 dashboard coach | ✅ | 🟡 a mano |
| R2 Antropometria con fonte | ✅ | 🟡 misure corporee | 🟡 campi wellness | ? | ? | ❌ | ✅ configurabile | 🟡 a mano |
| R3 Protocolli versionati | ✅ | ❌ | 🟡 workout | 🟡 workout | ? | 🟡 workout | 🟡 | ❌ |
| R4 Import FIT/CSV storico | ✅ | ✅ FIT e molti formati | ✅ FIT, CSV per Supporter | ✅ | ✅ | ✅ FIT/GPX/TCX | ✅ via API | 🟡 CSV |
| R5 Incrementale (ultimo step, aderenza) | ✅ | 🟡 analisi generica degli intervalli | 🟡 rilevamento intervalli | ? | ✅ | ❌ | 🟡 | ❌ |
| R6 Lattato | ✅ | 🟡 metadati | 🟡 campi intervallo manuali | ? | ✅ | ❌ | 🟡 | 🟡 a mano |
| R7 VO₂ / gas | ✅ | ? | ❌ ? | ? | ✅ | ❌ | 🟡 | ❌ |
| R8 Sprint e Wingate separati | ✅ | 🟡 curva di potenza | 🟡 curva di potenza | 🟡 | ✅ sprint nel modello | 🟡 | 🟡 | ❌ |
| R9 Zone da test | ✅ | ✅ | ✅ zone custom (Supporter) | ✅ | ✅ | ✅ | 🟡 | ❌ |
| R10 Crescita e maturazione | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | 🟡 se configurata | 🟡 formule a mano |
| R11 Aggregati per gruppo/stagione | ✅ | 🟡 confronti fra atleti | 🟡 | 🟡 | ? | 🟡 | ✅ | 🟡 |
| R12 Report PDF gerarchici | ✅ | ❌ ? | ❌ ? | ? | ✅ report individuali | ❌ | ✅ | 🟡 |
| R13 Provenienza e revisioni | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ? | 🟡 cronologia |
| R14 Offline senza server | ✅ | ✅ | ❌ | 🟡 solo WKO5 | ❌ | ❌ server | ❌ | ✅ desktop, senza condivisione |
| R14 Condivisione con ruoli, senza server | ✅ (WebDAV/cartella) | ❌ | ✅ con server del fornitore | ✅ con server del fornitore | ✅ con server del fornitore | ✅ self-hosted | ✅ fornitore | 🟡 serve grist-core |
| R16–17 Windows e Android | 🟡 | 🟡 niente Android | ✅ web | ✅ web e app | ✅ web | ✅ web e app | ✅ | 🟡 |
| R18 Italiano | 🟡 IT/EN | ? | ? | ? | ? | 🟡 6 lingue, IT n.v. | ? | ? |
| Costo zero / open source | ✅ GPL | ✅ GPL | 🟡 freemium | ❌ | ❌ | 🟡 AGPL, server da gestire | ❌ | ✅ Apache |

**Lettura:** i requisiti R5–R8, R10 e R13 insieme a R14 sono coperti solo da Fuorigiri. INSCYD copre bene R5–R8 ma con un modello proprietario, a pagamento e online. Teamworks AMS copre la parte organizzativa, ma richiederebbe di configurare a mano i metodi scientifici.

## 5. Componenti generici sostituibili

| Componente in Fuorigiri | Dimensione indicativa | Alternativa matura | Beneficio / limite | Raccomandazione |
|---|---|---|---|---|
| Adattatori Drive, Dropbox, OneDrive (`cloud.py`) | ≈690 righe e app OAuth da registrare | [rclone](https://github.com/rclone/rclone) (MIT, 1.76.0, molti backend) oppure il client cloud del sistema più la cartella di scambio | Meno OAuth, revisioni giuridiche e collaudi con account reali. Uso di rclone su Android n.v. | **Congelare** i provider nativi come sperimentali; supportare ufficialmente WebDAV (Nextcloud) e cartella. Riaprire solo su richiesta concreta di una società |
| Protocollo di sincronizzazione firmato (`sync.py`, `sync_v2.py`, `sync_service.py`, `recovery.py`) | ≈1,5k righe | CRDT su SQLite: [cr-sqlite](https://github.com/vlcn-io/cr-sqlite) (stato 2026 incerto), [sqlite-sync](https://github.com/sqliteai/sqlite-sync) (licenza non standard, legata a SQLite Cloud); [Syncthing](https://syncthing.net/) (app Android ufficiale dismessa a dicembre 2024, resta un fork) | Nessuna alternativa conserva firme, ruoli e revoche senza server | **Mantenere** e non estendere: niente inventario paginato o compattazioni nuove senza un caso d'uso reale |
| Backup cifrato `.fgbak` | ≈560 righe | [restic](https://restic.net/) (BSD-2, 0.19.1, luglio 2026) | Robusto ma da riga di comando, poco adatto a operatori non tecnici | **Mantenere** il backup integrato; suggerire restic solo come seconda copia per chi gestisce un NAS |
| Soglie di lattato (`specialist.py`) | ≈170 righe | [lactater](https://cran.r-project.org/package=lactater) (R, MIT; Dmax, Log-log, OBLA, LTP), [lactate-thresholds](https://pypi.org/project/lactate-thresholds/) (Python, 0.3.8 marzo 2025, licenza non indicata nella pagina PyPI) | I metodi di Fuorigiri sono deliberatamente più conservativi (livelli fissi, niente estrapolazione) | **Non dipendere** da queste librerie: usarle come **vettori numerici indipendenti** nei test, come già chiede AGENTS.md per i nuovi metodi |
| Maturazione (`maturation.py`) | ≈790 righe | [matuR](https://cran.r-project.org/package=matuR) (R, MIT, Mirwald e Khamis–Roche, ultimo CRAN 2020), [sitar](https://cran.r-project.org/package=sitar) (1.5.0, luglio 2025, modelli di crescita longitudinali), calcolatore NSW | `sitar` è il riferimento per la PHV longitudinale; licenza n.v. | Usarli come **oracoli** per Mirwald e PHV; se servirà Khamis–Roche, confrontarlo con `matuR` prima di implementarlo |
| Lettura FIT, PDF, cifratura, portachiavi | — | Già librerie mature: fitdecode, reportlab, cryptography, keyring | — | Nessun cambiamento |
| Kit UI comune `@cycling-suite/ui` | Repo separata | Librerie React di componenti (n.v. in questa analisi) | Ridurrebbe codice proprio, ma la migrazione costa | Da valutare solo se la suite cresce; non prioritario |
| Python su Android (Chaquopy e wheel native ricostruite su Fedora) | Filiera documentata in 5 guide | n.v. in questa analisi | È il costo di manutenzione più alto fra le parti non distintive | Vedi §7: decidere il perimetro Android prima di investire ancora |

## 6. Analisi delle opzioni e utilità di proseguire

### 6.1 Confronto

| Opzione | Tempo per una versione usabile | Costo totale (sviluppo, manutenzione, hosting) | Migrazione dal codice attuale | Rischio | Controllo e lock-in | Valore distintivo |
|---|---|---|---|---|---|---|
| **A. Abbandonare e adottare** (es. Intervals.icu o GoldenCheetah più un foglio Grist) | 1–3 settimane | Basso in sviluppo; 0–4 $/mese o licenze TP/INSCYD; lavoro manuale ricorrente sui fogli | Export CSV già disponibili; storico e snapshot perdono la provenienza | Medio: metodi e maturazione tornano a fogli non verificati | Lock-in sul fornitore SaaS; dati di minori su server esterni | Perso quasi tutto |
| **B. Adottare ed estendere** (es. GoldenCheetah) | 3–6 mesi | Alto: riscrivere i motori Python in C++/Qt o negli script interni (supporto n.v.) | Bassa riusabilità diretta | Alto: architettura single-athlete, nessun Android | Buono (GPL) | Ricostruibile solo in parte |
| **C. Contribuire upstream** | Mesi per funzione, accettazione incerta | Medio-alto, con coordinamento | Parziale | Alto: gli obiettivi upstream non includono vivai e maturazione | Condiviso | Diluito |
| **D. Fork** (GoldenCheetah o OpenAthlete) | 2–4 mesi | Molto alto: mantenere una base C++ con 11k commit o un'architettura server | Riscrittura | Molto alto | Totale ma oneroso | Ricostruito |
| **E. Continuare, sostituendo il generico** | 4–8 settimane per l'alpha (gate già noti) | Il più basso fra le opzioni che conservano il valore: meno provider, meno superficie Android | Nessuna: si toglie, non si migra | Medio: un solo autore | Totale, nessun fornitore | Conservato |
| **F. Continuare così com'è** | Simile a E | Più alto di E: provider cloud, 16 KB, firme e collaudi per ogni piattaforma | Nessuna | Medio-alto: esaurimento del manutentore | Totale | Conservato |

Il costo già sostenuto non entra nel confronto: E prevale perché le parti distintive sono **già scritte e testate** e nessuna alternativa le offrirebbe senza riscriverle, mentre il lavoro residuo più costoso è proprio quello generico che E taglia.

### 6.2 Utilità di proseguire

- **Che cosa offre in più:** archivio dei test di un vivaio con metodi trasparenti e versionati, maturazione con gate di qualità, nessun ricalcolo silenzioso, report per gruppo e stagione, tutto offline e in italiano. È un vantaggio **reale ma di nicchia**: conta per chi fa valutazione funzionale strutturata su giovani, non per il ciclista amatore.
- **Gli utenti lo sceglierebbero?** La società d'origine sì, perché il prodotto rispecchia i suoi protocolli e il suo storico. Per altre società l'adozione dipende da installazione semplice e supporto: un tecnico abituato a Intervals.icu o TrainingPeaks lo userebbe **accanto**, per i test, non al posto di quelli per l'allenamento quotidiano.
- **Dove sta il valore:** soprattutto nel **contesto** (protocolli ERG della società, storico importato, scelte metodologiche documentate, dati di minori sotto controllo locale), poi nei motori di analisi. Trasporti e infrastruttura non sono distintivi.
- **Sostenibilità:** ≈38k righe con un solo autore e un ritmo di 63 commit in un mese sono sostenibili solo se il perimetro smette di crescere sulle piattaforme. Anche il processo documentale (≈6,5k righe, registri e gate) è un costo da contenere.
- **Ragioni per continuare comunque:** privacy dei minori e nessun costo ricorrente, controllo dei metodi scientifici, base comune per Ammiraglia, competenze acquisite.

## 7. Verdetto e prossimi passi

**Raccomandazione: E.** Le funzioni distintive sono implementate e nessuna alternativa verificata le copre insieme, offline e senza costi. Abbandonare (A) farebbe perdere metodi, maturazione e provenienza; adottare o forkare (B, D) significherebbe riscriverli su basi pensate per il singolo atleta. Il problema reale è il peso delle parti generiche e multipiattaforma: vanno ridotte, non ampliate.

**Confidenza: media.** Salirebbe con un riscontro di 2–3 società esterne interessate o con la scelta esplicita di un uso solo interno. Cambierebbe verso A se la società accettasse di tenere i dati su un SaaS (Intervals.icu con campi personalizzati) e rinunciasse a maturazione e provenienza, oppure se il manutentore non avesse più tempo per il collaudo delle piattaforme.

### Cosa costruire
1. Chiudere l'alpha sui gate già elencati in `PROSSIMI_PASSI.md`, con **WebDAV/Nextcloud e cartella** come soli trasporti supportati.
2. Validazione scientifica: vettori di confronto da `lactater` o `lactate-thresholds` per il lattato e da `matuR` o `sitar` per Mirwald e PHV, più il calcolatore NSW per controlli manuali.
3. Esperienza di installazione e primo avvio per un'altra società (è ciò che decide l'adozione esterna).

### Cosa sostituire o congelare
- Drive, Dropbox e OneDrive nativi: sperimentali e congelati; per chi li usa, client del sistema più cartella di scambio, oppure [rclone](https://github.com/rclone/rclone).
- Seconda copia di sicurezza opzionale con [restic](https://restic.net/) per chi ha un NAS.
- Allenamento quotidiano e carichi: lasciarli a [Intervals.icu](https://www.intervals.icu/) (già collegato) o a [GoldenCheetah](https://www.goldencheetah.org/).

### Cosa togliere dalla roadmap
- **App Allenamenti** della suite (`ARCHITETTURA_PROPOSTA.md` §15): già coperta da Intervals.icu, TrainingPeaks e [OpenAthlete](https://github.com/openathleteorg/openathlete); meglio un'esportazione di zone e risultati verso questi strumenti.
- **Server opzionale** (§10.4): rimandarlo finché non ci sono più società con molti operatori.
- **Pacchetto Linux/Flatpak**: lasciarlo rinviato.
- **Android completo:** decidere esplicitamente se serve modifica e import sul telefono o se bastano consultazione ed export. La filiera di wheel native (Pillow, pydantic-core, OpenBLAS, 16 KB) è il costo generico più alto del progetto. *Deciso il 18 novembre 2026: app completa (vedi §1).*

### Rischi e segnali da monitorare
- Tempo del manutentore e un solo autore: se i gate dell'alpha slittano oltre gennaio 2027, rivalutare il perimetro Android.
- Richieste reali di altre società (zero richieste in 6 mesi suggerirebbe un uso solo interno, con meno distribuzione e meno firme).
- Evoluzione di Intervals.icu (campi personalizzati, team) e di OpenAthlete (club multi-coach in roadmap): se aggiungessero test di laboratorio strutturati, il margine distintivo si ridurrebbe.
- Requisiti Google Play (16 KB) e falsi positivi Defender: costi esterni ricorrenti.
- Validazione esterna dei metodi: senza, il vantaggio «metodi trasparenti» resta dichiarato più che dimostrato.

## 8. Fonti consultate (verifica del 18 novembre 2026)

- GoldenCheetah: [sito](https://www.goldencheetah.org/), [GitHub](https://github.com/GoldenCheetah/GoldenCheetah), [v3.8-DEV2601](https://newreleases.io/project/github/GoldenCheetah/GoldenCheetah/release/v3.8-DEV2601), [novità 3.6](https://www.softpedia.com/progChangelog/GoldenCheetah-Changelog-155876.html)
- Intervals.icu: [prezzi](https://www.intervals.icu/pricing), [comunicazione e gestione atleti](https://www.intervals.icu/features/communicate/), [campi wellness personalizzati](https://forum.intervals.icu/t/custom-wellness-fields/23188), [campi intervallo personalizzati](https://forum.intervals.icu/t/custom-interval-fields/25942)
- TrainingPeaks: [prezzi coach](https://www.trainingpeaks.com/pricing/for-coaches), [aggiornamento prezzi coach](https://help.trainingpeaks.com/hc/en-us/articles/34619661884941-TrainingPeaks-Coach-Subscription-Pricing-Update), [WKO5](https://www.trainingpeaks.com/products/wko5/)
- INSCYD: [prezzi](https://inscyd.com/pricing/), [test del lattato](https://inscyd.com/functions/lactate-testing/)
- OpenAthlete: [GitHub](https://github.com/openathleteorg/openathlete)
- Teamworks AMS / Smartabase: [annuncio del cambio di nome](https://explore.teamworks.com/transition-ams), [scheda prezzi di terzi](https://enterprisedna.co/omni/instead-of/smartabase/pricing)
- Grist: [grist-core](https://github.com/gristlabs/grist-core), [Grist Desktop](https://sourceforge.net/mirror/grist-desktop/)
- wger: [GitHub](https://github.com/wger-project/wger), [release 2.7](https://newreleases.io/project/github/wger-project/wger/release/2.7), [F-Droid](https://f-droid.org/packages/de.wger.flutter/)
- Endurain: [GitHub](https://github.com/joaovitoriasilva/endurain), [documentazione](https://docs.endurain.com/)
- Lattato: [lactater (CRAN)](https://cran.r-project.org/package=lactater), [lactate-thresholds (PyPI)](https://pypi.org/project/lactate-thresholds/), [Exphyslab, descrizione di terzi](https://knowledgeiswatt.substack.com/p/first-lactate-threshold-lt1-web-app), [Lact8](https://apps.apple.com/us/app/lact8/id6757203590)
- Maturazione: [matuR (CRAN)](https://cran.r-project.org/package=matuR), [sitar (CRAN)](https://cran.r-project.org/package=sitar), [calcolatore NSW](https://www.sport.nsw.gov.au/pathways-and-development/maturity-status-calculator), [limiti di validazione Mirwald](https://pmc.ncbi.nlm.nih.gov/articles/PMC8312932)
- Componenti: [rclone 1.76.0](https://www.fosslinux.com/163653/rclone-1-76-0-security-fixes.htm), [restic 0.19.1](https://restic.net/blog/2026-07-05/restic-0.19.1-released/), [Syncthing Android dismesso](https://github.com/syncthing/syncthing-android), [cr-sqlite](https://github.com/vlcn-io/cr-sqlite), [sqlite-sync](https://awesome.ecosyste.ms/projects/github.com%2Fsqliteai%2Fsqlite-sync)
- Contesto italiano: [FIDAL, valutazione funzionale giovanile](https://www.fidal.it/upload/Friuli%20Venezia%20Giulia/Area%20Tecnica/01-formazione/02-corso-istruttori/Sacc%C3%A0-Valutazione_funzionale_giovanile_2022.pdf), [Federciclismo, consenso informato](https://www.federciclismo.it/wp-content/uploads/2026/02/Mod.-11.2-e-bis-Consenso-informato.pdf)

Limiti: issue, PR e stelle di questa repository non verificati (`gh` assente). Prezzi e versioni dei prodotti commerciali possono cambiare; diversi dati provengono da pagine di terzi, indicate come tali. Non sono stati provati direttamente i software citati.
