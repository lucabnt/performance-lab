# Distribuzione desktop e prerequisiti mobile

## Blocco Windows — 7 novembre 2026

Il candidato `windows-alpha-review-20261102-01` è bloccato da Microsoft Defender, che rimuove `Fuorigiri.exe` con rilevamento `Trojan:Win32/Bearfoos.A!ml`. Non è attualmente qualificato per l'uso. Le prove di build/smoke del 2 novembre restano storiche.

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
.venv/Scripts/python.exe -m pip install -r requirements-lock-windows.txt
# nella cartella frontend: npm ci; npm run build
.venv/Scripts/python.exe scripts/build.py
& 'C:/Program Files (x86)/Inno Setup 6/ISCC.exe' packaging/windows/Fuorigiri.iss
.venv/Scripts/python.exe scripts/release.py
```

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
