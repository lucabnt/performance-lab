# Distribuzione desktop e prerequisiti mobile

## Prima pre-release 0.10.0-alpha.1

**Decisione del 21 novembre 2026, sera (2):** il CI con Python 3.12 ha rilevato che REPORT-ZIP-01 rompeva report ed export su quella versione; i binari (3.13 e 3.14) non erano colpiti, ma l’utente sceglie di rifare il candidato. Nuovo candidato `rc-20261121-04` (commit `fc63893`); la cartella `dist/release/Fuorigiri-0.10.0-alpha.1-rc-20261121-03/` e il suo APK firmato restano come preparazione superata. Servono un nuovo APK release firmato con la stessa chiave, una nuova cartella di release con `SHA256SUMS.txt` e il tag spostato su `fc63893`.

**Decisione del 21 novembre 2026, sera:** l’utente sceglie di includere nella release anche REPORT-ZIP-01. Nuovo candidato `rc-20261121-03` (commit `0a6c4be`); la cartella `dist/release/Fuorigiri-0.10.0-alpha.1-rc-20261121-02/` e il suo APK firmato restano come preparazione superata. APK release firmato con la stessa chiave, cartella `dist/release/Fuorigiri-0.10.0-alpha.1-rc-20261121-03/` con `SHA256SUMS.txt` e tag spostato su `0a6c4be`; resta la creazione della release su GitHub.

**Decisione del 21 novembre 2026, pomeriggio:** dopo la riscrittura della storia l’utente ha eliminato la release `v0.10.0-alpha.1` costruita su `rc-20261121-01`, perché i suoi allegati Windows e lo ZIP dei sorgenti contenevano ancora i documenti con le segnalazioni a Microsoft. Nuovo candidato `rc-20261121-02` (commit `0e3f900`, stesso codice). APK release firmato dal titolare con la stessa chiave, cartella `dist/release/Fuorigiri-0.10.0-alpha.1-rc-20261121-02/` con `SHA256SUMS.txt` sui cinque allegati e tag spostato su `0e3f900`; resta la creazione della release su GitHub. La cartella `dist/release/Fuorigiri-0.10.0-alpha.1-rc-20261121-01/` resta come preparazione superata.

**Decisione del 21 novembre 2026:** la release `v0.10.0-alpha.1`, creata dall’utente con la repository ancora privata, viene spostata sul candidato `rc-20261121-01` (commit `ccc50ce`), che aggiunge REPORT-LOCALE-01 e FIT-SESSIONE-01. Servono un nuovo APK release firmato con la stessa chiave del titolare, nuovi allegati e `SHA256SUMS.txt`, il tag spostato su `ccc50ce` e la sostituzione degli allegati nella release; la cartella `dist/release/Fuorigiri-0.10.0-alpha.1/` del 20 novembre va conservata come preparazione superata, non sovrascritta. Nuova cartella `dist/release/Fuorigiri-0.10.0-alpha.1-rc-20261121-01/`; l’APK firmato differisce dal candidato solo per `certifi` 2026.11.20 (dipendenza secondaria non fissata), differenza accettata dall’utente.

**Decisione del 20 novembre 2026, pomeriggio:** la preparazione di release del mattino da `rc-20261120-01` (commit `46959ed`, cartella `dist/release/Fuorigiri-0.10.0-rc-20261120-01-non-pubblicata/`) non viene pubblicata; la prima pre-release pubblica è `v0.10.0-alpha.1`, compilata dal candidato `rc-20261120-02` (commit `8e9de2d`), che aggiunge SYNC-SPAZIO-01 fasi 0–1. Allegati in `dist/release/Fuorigiri-0.10.0-alpha.1/`, tag sul commit `8e9de2d`; APK release firmato dal titolare con la stessa chiave il 20 novembre e identico nel contenuto al release del candidato; `SHA256SUMS.txt` calcolato sui cinque allegati. Le indicazioni sotto restano come storico della preparazione.

Il nome prodotto resta 0.10.0. Il tag è `v0.10.0-alpha.1`. Per il primo tag pubblico utilizzare una repository inizializzata dallo snapshot controllato, senza genitori della storia privata. Il vecchio identificativo di profilo resta nelle revisioni precedenti. Conservare la repository originale privata. Verificare anche eventuali fork, allegati, Actions, wiki, issue e pull request prima di cambiare la visibilità di un progetto esistente.

**Decisione del 20 novembre 2026:** l’utente pubblica la release `v0.10.0-alpha.1` su **questa** repository e la rende pubblica lui stesso dopo la release, invece di inizializzarne una nuova dallo snapshot. Controllo della storia (71 commit) prima della scelta: nessun percorso personale, account, email, chiave o token; autori con indirizzo noreply GitHub. L’identificativo Intervals.icu usato come esempio nelle prime revisioni (anche nella vecchia `docs/screenshots/intervals-id.png`) è stato rimosso dalla storia il 20 novembre con riscrittura e push forzato, su richiesta dell’utente. Il 21 novembre, su richiesta dell’utente, i riferimenti alle segnalazioni inviate a Microsoft sono stati tolti dai documenti e dall’intera storia, con riscrittura e push forzato di `main` e del tag. I commit hanno cambiato identificativo: i documenti riportano i nuovi, mentre manifest, `candidate.json` e allegati già prodotti conservano i precedenti (per esempio `rc-20261121-01` registra `8cb232b`, ora `ccc50ce`). Corrispondenza completa in `.local/commit-map-riscrittura-20261121.txt`, copia della storia precedente in `.local/backup-storia-prima-riscrittura-20261121.bundle`, entrambi fuori dalla repository. Gli allegati Windows e lo ZIP dei sorgenti di `rc-20261121-01` contengono ancora i documenti con le segnalazioni; l’APK no. Prima di cambiare la visibilità rivedere anche issue, pull request, Actions (log e artefatti), wiki e impostazioni dei secret. Allegati preparati quel mattino: cartella locale `dist/release/Fuorigiri-0.10.0-rc-20261120-01-non-pubblicata/`, compilati dal commit `46959ed`; superati nel pomeriggio da `rc-20261120-02` (decisione sopra).

| Allegato | Quando inserirlo |
|---|---|
| Fuorigiri-0.10.0-sources.zip | Snapshot dei file tracciati del candidato, con esempi sintetici, licenza, componenti comuni e istruzioni. |
| SHA256SUMS.txt | Generato esclusivamente sugli allegati effettivamente pubblicati. |
| Fuorigiri-0.10.0-windows-x64-setup.exe | Installer dopo completamento avvisi e sorgenti delle dipendenze ridistribuite. |
| Fuorigiri-0.10.0-windows-x64-portable.zip | Stesso perimetro dell’installer. Estrarre l’intera cartella. |
| Fuorigiri-0.10.0-android-native-wheels.zip | Supporto alla ricostruzione Android, dopo ricostruzione sanitizzata delle sei wheel che contengono percorsi con account del builder e verifica delle condizioni dei binari nativi. Estrarre nella radice dei sorgenti. |
| Fuorigiri-0.10.0-android-release-signed.apk | Solo dopo verifica condizioni dei componenti Android, firma stabile e prova sul telefono. |

**13 novembre 2026:** gli avvisi Qt/Chromium sono ora generati nel bundle (`licenses/qt`), resta la decisione su come garantire l’accesso ai sorgenti Qt. `direct_url.json` viene rimosso durante la build Gradle. `build_android.py --release` blocca wheel e APK con percorsi del builder, finché le sei wheel non sono ricostruite ([procedura](ANDROID_WHEEL_FEDORA.md)).

La verifica degli asset Android ha anche individuato il percorso locale della wheel comune in direct_url.json nel pacchetto Chaquopy. Preparare il successore da un checkout neutro e riesaminare i metadati incorporati, oltre a ELF e SBOM.

Il bundle Windows include 113 testi di licenza e avvisi disponibili nel builder (Python e frontend). Le librerie terze Qt conservano riferimenti a profili di compilazione a monte. Per la qualifica della distribuzione completare la corrispondenza con i sorgenti e verificare gli avvisi WebEngine/Chromium. [Dettagli licenze](../THIRD_PARTY.md).

La cartella privata del candidato conserva l’APK non firmato per il titolare. La [guida di firma](FIRMA_ANDROID.md) descrive allineamento, firma, controllo dell’impronta e aggiornamento da una versione precedente. Le note di accettazione sono in [COLLAUDO_PILOT.md](COLLAUDO_PILOT.md). Le vecchie consegne includono log tecnici e possono conservare esempi rimossi. Per i download pubblici usare esclusivamente i nomi espliciti della tabella, con digest ricalcolati sulla selezione finale.

## Candidato del 9 novembre — ordine e maturazione, 9 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-ordine-maturazione-20261109-01/`: nuove build Windows/Android **0.10.0** con **UI-ORDINE-02** (cognome/nome, test e misure dal più recente in pagine indipendenti da 15) e **MAT-AVVISI-01** (stime datate decrescenti e indici antropometrici con avvisi, motore growth-maturity/2), oltre alle funzioni precedenti; UI comune **0.2.9** invariata. Installer/portabile completi, APK debug firmato per i test, release non firmato, supporto strumentale, sorgenti/wheel e **25 checksum finali verificati**. Avvio Windows, scansioni Defender attivo e controlli di contenuti/firme/allineamento riusciti. [Prove e digest](VERIFICA.md).

Nessuna pubblicazione, chiave nuova o installazione sopra dati operativi. Restano Windows pulito/aggiornamento, firma release e runtime Android/telefono, sei problemi LOAD 16 KB, provider reali e validazione esterna. WIN-AV-01 attende reinstallazione/riapertura con protezione attiva: le scansioni di questa nuova build sono una verifica distinta. La documentazione congelata nei pacchetti precede questa annotazione conclusiva.

## Candidato precedente — import-avvisi, 8 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-import-avvisi-20261108-01/`: nuove build Windows/Android **0.10.0** con avvisi CSV non bloccanti, riconoscimento duplicati e correzione dello scorrimento dei dialoghi tramite UI comune **0.2.9**, oltre alle funzioni precedenti. Installer e portabile completi, APK debug firmato per i test, release non firmato, supporto strumentale, sorgenti/wheel e **25 checksum verificati**. Smoke Windows e scansioni correnti riusciti, firme/allineamento/contenuti APK verificati. [Prove e digest](VERIFICA.md).

Nessuna pubblicazione, nuova chiave o installazione sopra dati operativi. Restano WIN-AV-01 storico, Windows pulito/aggiornamento, firma release, runtime della nuova build Android e telefono, provider reali e sei problemi LOAD 16 KB. Zipalign e smoke non sostituiscono tali gate. La documentazione congelata nei pacchetti precede questa annotazione finale.

## Candidato precedente — antro-incrementale, 8 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-antro-incrementale-20261108-01/`: nuove build Windows/Android 0.10.0 con import CSV incrementale, altezza perineale e rapporto sulla statura nel profilo; include eliminazione/ripristino di misure e test e le funzioni precedenti. Installer/portabile completi, APK debug firmato per i test, release non firmato per il titolare, APK strumentale, sorgenti e wheel. Smoke Windows e scansioni correnti riusciti, contenuti e **25 checksum finali verificati**. [Registro e digest](VERIFICA.md). Nessuna pubblicazione o nuova chiave.

Restano Windows pulito/aggiornamento, WIN-AV-01 del candidato storico, firma release, runtime della nuova build Android e telefono, provider reali e sei problemi LOAD nativi a 16 KB. Non confondere zipalign con qualifica 16 KB; le scansioni correnti non dimostrano un falso positivo sul vecchio candidato. La documentazione congelata nei pacchetti precede questa annotazione finale.

## Candidato precedente record-lifecycle — 8 novembre 2026

`dist/candidates/Fuorigiri-0.10.0-record-lifecycle-20261108-01/` include le build precedenti con eliminazione/ripristino di rilevazioni e test. Windows: installer o ZIP completo; Android: debug firmato per i test e release non firmato per la firma del titolare. Sorgenti, wheel e checksum inclusi. [Riscontri](VERIFICA.md), [gate di accettazione](COLLAUDO_PILOT.md). Nessuna pubblicazione; scansioni correnti e smoke non sostituiscono Windows pulito o risoluzione del rilevamento storico WIN-AV-01. Nessuna qualifica runtime Android/16 KB implicita.

## Blocco Windows — 7 novembre 2026

Il candidato `windows-alpha-review-20261102-01` è bloccato da Microsoft Defender, che rimuove `Fuorigiri.exe` con rilevamento `Trojan:Win32/Bearfoos.A!ml`. Non è attualmente qualificato per l'uso. [Diagnosi](WINDOWS_DEFENDER.md); falso positivo non confermato. Le prove di build/smoke del 2 novembre restano storiche.

## Preparazione alpha — 2 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-alpha-prep-20261102-01/`, prodotto 0.10.0: installer Windows del 1 novembre verificato e riusato senza ricompilazione, nuovi APK debug e release non firmato, sorgenti, wheel native e checksum. Il debug è solo per le prove; per distribuire il release seguire [FIRMA_ANDROID.md](FIRMA_ANDROID.md). Nessuna pubblicazione, firma release o accettazione operativa implicita: [checklist](COLLAUDO_PILOT.md), [prove effettive](VERIFICA.md). Le sezioni datate precedenti restano come riferimento storico.

Guida di packaging; conserva anche il dettaglio della prima implementazione 0.6. Il prodotto nei sorgenti dichiara 0.10.0: ricompilare prima di collaudare le novità. Windows e sorgenti erano il perimetro iniziale; Fedora resta rimandato, il collaudo Android è stato riaperto e il candidato Windows/Android è stato preparato il 21 ottobre. Gli adapter cloud oggi sono implementati: per il loro stato usare la [guida sincronizzazione](CONFIGURARE_LA_SINCRONIZZAZIONE.md), che supera le indicazioni storiche sotto.

**Consegna concordata il 18 ottobre 2026:** Windows e sorgenti; l’utente ha rimandato le build Linux/Android. I gate e i collaudi sotto restano documentati, senza avviare CI o pubblicazioni.

18 ottobre 2026. L’utente autorizza il consolidamento della sincronizzazione/distribuzione, quindi Android, e richiede dipendenze incluse per l’utente finale e un’icona minimale. Il motore scientifico rimane **0.5.0**, lo schema dei dati rimane **3**: nessun risultato storico viene ricalcolato per questo aggiornamento.

## Candidato pilot — 21 ottobre 2026

Prodotto 0.10.0, identificativo separato pilot-20261021-01. Artefatti in `dist/candidates/Fuorigiri-0.10.0-pilot-20261021-01/`, senza sovrascrivere vecchie release. Windows con bundle dipendenze, installer e ZIP portabile; Android release intenzionalmente non firmato, come richiesto dal titolare. Prima di installarlo seguire [firma Android](FIRMA_ANDROID.md). [Checklist e verbale del pilot](COLLAUDO_PILOT.md), stato effettivo in VERIFICA.md. Nessun rilascio pubblico, chiave generata o prova su PC pulito/telefono implicita.

Build isolate: `python scripts/build.py --output-root .local/candidate-build-nuovo` rifiuta una destinazione già esistente. Inno Setup accetta `/DAppDistDir=<bundle-Fuorigiri-assoluto>` e `/DAppOutputDir=<output-assoluto>` mantenendo AppId e versione. `scripts/package_candidate.py --help` congela gli input in una destinazione nuova, include sorgenti/wheel native verificate e genera manifest/checksum; non firma né pubblica. Copiare l’intero bundle portabile, non il solo EXE. Fonti e wheel non costituiscono una cache offline completa di dipendenze PyPI/Gradle.

## Scelte e stato reale

| Area | Implementato | Ancora necessario per il rilascio operativo |
|---|---|---|
| Windows x64 | Bundle Python/Qt/librerie/UI, icona, installer Inno Setup per utente, sorgenti e checksum | Prova su Windows pulito; firma Authenticode di prodotto con certificato del titolare |
| Linux, Fedora iniziale | Manifest Flatpak, preparazione wheel nel medesimo SDK, launcher/icone e workflow di build | Eseguire build Linux, risolvere eventuali librerie native mancanti e collaudare Fedora pulita/Wayland/X11/portachiavi |
| Cartella condivisa | Trasporto comune, pacchetti invariati, pubblicazione locale atomica e senza sovrascritture | Collaudo con veri client cloud e due PC; upload del client non verificabile dall’app |
| WebDAV desktop | HTTPS, credenziali nel portachiavi, inventario, pubblicazione condizionale, rilettura, retry, accessi firmati e conflitti | Nextcloud/server reale, account distinti e interruzioni fra dispositivi reali |
| Android | Shell Kotlin/WebView, backend ASGI in-process, bridge React, SAF, Keystore, WorkManager e test del contratto condiviso | Wheel native aggiornate, SDK/JDK/Gradle, APK, emulatore e telefono fisico; TD-57 **aperto** |

Non chiamare questo stato “supporto certificato” di Nextcloud, Fedora o Android. Il test WebDAV usa un server HTTP locale di fixture; il prodotto accetta solo HTTPS. Gli adapter API Drive/Dropbox/OneDrive sono stati aggiunti dopo questa prima implementazione; OAuth e cartelle condivise richiedono ancora collaudo reale. I client desktop possono anche gestire una cartella locale.

Prima di preparare artefatti eseguire `python scripts/verify_versions.py`. La fonte prodotto è `pyproject.toml`; build/release rifiutano metadati discordanti. L’allineamento 0.10.0 del 20 ottobre non ricompila gli installer già esistenti.

## Distribuzione senza installare Python o Node

### Windows — DIST-01

Scelta: **PyInstaller onedir + installer Inno Setup per utente**, non un singolo EXE che riestrae tutto a ogni avvio. `Fuorigiri.exe` contiene il launcher e trova Python, Qt WebEngine, librerie scientifiche, frontend e risorse nella propria distribuzione. L’installer porta tutta la cartella sul PC: all’utente non servono Python, Node, Qt, compilatori o browser aggiuntivi.

Destinazione predefinita `%LOCALAPPDATA%/Programs/Fuorigiri`, senza privilegi admin; dati separati nella directory applicativa esistente. Collegamento Start, desktop facoltativo, icona in exe/installer/taskbar/finestra. Aggiornamento manuale con lo stesso AppId e dati conservati; disinstallazione dei binari senza rimozione dell’archivio. Prima di retrocedere una versione verificare la compatibilità dello schema e usare un backup, non abbassare artificialmente `user_version`.

Target iniziale Windows 10 22H2 x64 / Windows 11 x64 su sistema aggiornato. “Nessuna dipendenza da installare” non significa qualunque versione di Windows, driver assenti o OS non funzionante. La verifica su una macchina con strumenti di sviluppo presenti non sostituisce un PC/VM pulito.

Build dal sorgente (solo sviluppatore):

```powershell
.venv/Scripts/python.exe -m pip install --require-hashes -r requirements-lock-windows.hashes
.venv/Scripts/python.exe -m pip install --no-deps --no-index -r requirements-common.txt
# nella cartella frontend: npm ci; npm run build
.venv/Scripts/python.exe scripts/build.py
$iscc = @("$env:LOCALAPPDATA/Programs/Inno Setup 6/ISCC.exe", 'C:/Program Files (x86)/Inno Setup 6/ISCC.exe') | Where-Object { Test-Path $_ } | Select-Object -First 1
& $iscc packaging/windows/Fuorigiri.iss
.venv/Scripts/python.exe scripts/release.py
```

`ISCC.exe` si trova in `%LOCALAPPDATA%/Programs/Inno Setup 6` se Inno Setup è installato per il solo utente (come sul PC di sviluppo), in `Program Files (x86)` se installato per tutti gli utenti (come sul runner del workflow `desktop-build`). Per le build dei candidati, passare a ISCC le cartelle con `/DAppDistDir=<bundle>` e `/DAppOutputDir=<cartella nuova>`.

L’ultimo comando crea un archivio dei sorgenti mantenuti, `SHA256SUMS.txt` e `release.json`. Non firma e non pubblica. La firma di Inno Setup scaricato identifica il compilatore, **non firma l’installer Fuorigiri risultante**. Il titolare dovrà fornire il proprio certificato di firma per un rilascio firmato; non generare un certificato fittizio presentandolo come attendibile.

### Fedora/Linux — DIST-02

Scelta: **Flatpak** con runtime Freedesktop 25.08, Python congelato e Qt inclusi nell’app. È più appropriato di un tarball PyInstaller nudo, che su Linux può ancora dipendere da librerie grafiche della distribuzione. Evita anche di chiedere all’utente una sequenza di `pip`/`dnf` per le dipendenze del programma.

All’installazione online Flatpak acquisisce il runtime necessario. Una sola `.flatpak` **non contiene automaticamente tutti i runtime**: per installazione iniziale senza rete serve un supporto con app e runtime, secondo la [procedura ufficiale create-usb/sideload](https://docs.flatpak.org/en/latest/usb-drives.html). Flatpak è il meccanismo di installazione del sistema; su una distribuzione che ne è priva il gestore dell’OS deve prima installarlo. Il target iniziale è Fedora desktop con Flatpak disponibile, non un Linux minimale senza stack grafico.

Build su Linux con Flatpak/flatpak-builder e frontend già compilato:

```sh
flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --user flathub org.freedesktop.Platform//25.08 org.freedesktop.Sdk//25.08
python3 scripts/prepare_flatpak.py
flatpak-builder --user --force-clean --repo=flatpak-repo flatpak-build packaging/linux/org.fuorigiri.PerformanceLab.json
flatpak build-bundle flatpak-repo Fuorigiri-0.10.0-linux-x86_64.flatpak org.fuorigiri.PerformanceLab --runtime-repo=https://dl.flathub.org/repo/flathub.flatpakrepo
```

La preparazione risolve le dipendenze nel **Python 3.13 del medesimo SDK**, salva wheel, versioni risolte e checksum; la successiva build usa `--no-index`. Non riusare il lock Windows, che contiene pacchetti specifici Windows. `wheelhouse/requirements-resolved.txt` e `SHA256.json` devono accompagnare gli artefatti di build; prima di pubblicare una release congelare/revisionare quel risultato e verificare gli avvisi di licenza.

Permessi iniziali: rete per WebDAV e loopback desktop, grafica Wayland/X11/DRI, Secret Service per le password e home per cartelle di scambio e archivi scelti. L’accesso home è una concessione esplicita di questa versione: ridurlo a portali/percorso selezionato richiede ulteriore integrazione Qt. I dati di default usano `XDG_DATA_HOME`, quindi nel Flatpak l’area privata applicativa. Un archivio esterno resta selezionabile; usare sempre copie/backup per spostare un archivio già attivo.

La pipeline `.github/workflows/desktop-build.yml` prepara candidati Windows/Linux su richiesta. È stata aggiunta al sorgente, **non avviata o dichiarata passata** in questa sessione Windows senza builder Linux. I pacchetti ottenuti sono candidati da provare; nessuna pubblicazione automatica.

## Trasporti — SYNC-01 e UI-22

Il database SQLite e gli allegati operativi restano locali. Vengono scambiati soltanto eventi firmati e pacchetti cifrati Fernet, con lo stesso formato `.ctsync`; nessun database aperto viene sincronizzato. `FolderTransport` e `WebDAVTransport` espongono `list/get/put` immutabile. La cartella mantiene anche il riconoscimento dei canali precedenti sul disco.

In **Archivio e scambio → Condivisione e collaboratori**, dopo aver aperto una società:

1. Scegli cartella locale oppure WebDAV.
2. Per WebDAV crea prima una cartella remota e condividila con gli account interessati; inserisci URL WebDAV finale, nome utente e password applicazione.
3. Salva e sincronizza. La password non torna nell’API di configurazione e non viene scritta nel JSON locale. Windows usa Credential Manager, Linux Secret Service; su Android il bridge usa Keystore/AES-GCM. Nessun fallback in chiaro se il portachiavi manca o è bloccato.
4. Su ogni altro dispositivo applica un **invito Fuorigiri personale**, poi configura il proprio accesso al medesimo percorso remoto. Gli URL Nextcloud dei due account possono differire pur puntando alla stessa cartella condivisa.
5. Controlla ricevuti/pubblicati/in attesa/conflitti e l’esito dell’ultimo tentativo. I conflitti non vengono risolti sovrascrivendo automaticamente i dati.

Un account cloud non attribuisce il ruolo admin. L’invito stabilisce lettura/scrittura dei dati; i permessi della cartella cloud stabiliscono l’accesso al trasporto. Un visualizzatore può configurare la propria connessione e ricevere dati anche con permessi WebDAV in sola lettura, purché il fondatore abbia già creato/pubblicato il canale.

### Integrità e ripresa

- HTTPS con verifica standard del certificato; nessuna opzione “ignora TLS”. Password Basic soltanto sopra TLS; niente credenziali nell’URL, redirect autenticati, query/token nell’URL o destinazioni ricavate da href esterni.
- `PROPFIND Depth: 1`, creazione della sola sottocartella opaca del canale se assente; inventario limitato, XML senza DTD/entità e nomi validati. Niente download seguendo host/percorso indicato arbitrariamente dal server.
- `PUT If-None-Match: *` per gli oggetti immutabili e rilettura esatta. Non sono richiesti MOVE/DELETE o rename atomici al server. Un file incompleto o collisione viene segnalato, mai sostituito silenziosamente.
- Tre tentativi per richiesta, timeout 25 s e backoff breve limitato; un timeout dopo commit può essere risolto verificando l’oggetto già presente. La ripresa è **per oggetto intero**, non un upload parziale a byte; al prossimo scambio gli oggetti già presenti vengono deduplicati.
- Massimo 80 MB per pacchetto, inventario XML 16 MB / 100.000 file. Il canale viene ancora inventariato e i pacchetti riletti: compattazione e indici incrementali per archivi molto grandi restano da progettare, senza cancellare la cronologia delle firme.
- Controlli accessi/revoche firmati in versioni immutabili. Lettura prima della pubblicazione, nessun rollback locale a versioni più vecchie; due contenuti diversi con la stessa versione fermano lo scambio. Legge i vecchi `access.json`/`revocations.json`, ma per il nuovo schema operativo **aggiornare tutti i dispositivi alla 0.6 prima di usare revoche/rotazione**.
- Serializzazione delle operazioni sync/accessi nel processo; blocco OS della doppia apertura dello stesso archivio principale nella shell desktop. Non tenere copie del dispositivo fondatore contemporaneamente attive in due installazioni.
- Registro operativo locale SQLite con concatenazione hash e massimo 100 righe mostrate nell’API. Non contiene password, URL autenticati o dati clinici. È diagnostica verificabile localmente, **non un audit esterno a prova di amministratore del PC**.

Il messaggio “pubblicazione WebDAV verificata” conferma la rilettura sul server, non la ricezione da ogni collaboratore. In cartella l’upload del client rimane non osservabile. Se manca la rete, il salvataggio locale resta disponibile e la sincronizzazione può essere ripetuta.

### Rotazione e recupero — SYNC-02

Solo il fondatore può chiudere il vecchio canale e generare una nuova chiave. Prima aggiornare tutti i client, far sincronizzare ogni dispositivo, risolvere conflitti/errori e conservare un backup dati + recupero accessi aggiornato. La UI rende esplicita la conseguenza e richiede conferma prima della rotazione.

La procedura sincronizza lo stato noto, scrive un journal locale protetto dai permessi dell’account, pubblica sul vecchio canale un avviso firmato di chiusura e solo dopo cambia la chiave locale. Se il processo si interrompe, “Ruota chiave” riprende dal journal; il normale sync non procede finché la rotazione non viene completata. Il vecchio canale non riceve ulteriori pubblicazioni dai client 0.6 che vedono l’avviso.

Dopo: pubblicare il nuovo canale, usare **Rinnova / cambia ruolo** per emettere nuovi inviti ai dispositivi ammessi, applicarli agli archivi esistenti e scaricare un nuovo recupero accessi del fondatore. L’identità della società e i risultati restano gli stessi. Non serve creare una nuova società.

Una rotazione non può cancellare copie già scaricate, recuperare automaticamente le modifiche non inviate da un dispositivo assente, impedire la censura di file da parte del server o rendere sicuro un PC già compromesso. Gli eventi locali di un vecchio autore revocato restano conservati, ma non vengono automaticamente ri-firmati come se fossero nuovi: recuperarli tramite una revisione/importazione verificata. La rotazione del canale non sostituisce la revoca dei permessi cloud del collaboratore.

## Icona e marchio — UI-23

Nuova icona applicativa: quadrante aperto verde acqua, lancetta bianca e punto giallo su fondo blu scuro. Fonte mantenuta `frontend/public/branding/fuorigiri.svg`; script `scripts/generate_icons.py` genera PNG multi-taglia e ICO, vettore Android equivalente mantenuto nella shell.

Uso: exe, installer, finestra/taskbar Windows, favicon, testata app, launcher Linux e Android. Non sostituisce il logo originale della società: il footer e l’attribuzione **Sviluppato da Luca Bontempi per Progetto Ciclismo - Rodengo Saiano A.S.D.** rimangono fissi nei report/prodotto. L’icona Fuorigiri segue la licenza del progetto; il marchio della società mantiene lo stato già documentato in THIRD_PARTY.

## Accettazione prima del rilascio

Vedere [test e GUI](TESTARE_IL_PROGETTO.md) e [registro verifiche](VERIFICA.md). Restano: macchina pulita Windows, Fedora pulita, Nextcloud reale con due account/dispositivi, firma del prodotto e inventario completo delle licenze Qt/Chromium. Per Android vedere [stato e istruzioni](ANDROID.md): i test Windows del bridge non certificano un APK.

Fonti primarie: [WebDAV RFC 4918](https://www.rfc-editor.org/rfc/rfc4918), [keyring](https://keyring.readthedocs.io/en/stable/), [Inno Setup per utente](https://jrsoftware.org/ishelp/topic_setup_privilegesrequired.htm), [Flatpak Python](https://docs.flatpak.org/en/latest/python.html), [bundle Flatpak e dipendenze](https://docs.flatpak.org/en/latest/single-file-bundles.html), [distribuzione offline con runtime](https://docs.flatpak.org/en/latest/usb-drives.html).
