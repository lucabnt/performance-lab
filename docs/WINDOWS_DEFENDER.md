# Windows: eseguibile rimosso da Microsoft Defender

## 15 novembre 2026 — quarto candidato bloccato e cambio di strategia (WIN-AV-02)

Alle 18:42:09 e 18:42:33 Defender (definizioni 1.463.310.0, motore 1.1.26100.4, protezione in tempo reale attiva) ha registrato due eventi 1116 `Trojan:Win32/Bearfoos.A!ml` sul launcher installato di `revisione-tecnica-20261115-01`: il primo con processo il launcher stesso, il secondo con processo Explorer. Alla diagnosi mancava l’evento 1117 e lo stato era «Attivo» (azione richiesta). Il file era presente ma illeggibile, quindi non è stato confrontato con il digest del manifest (`5cd856e8310a195af8a60da0bac88a7d1beae6c3f2d6d6b6472859d584bb4bc3`, 17.420.543 byte). Le scansioni di confezionamento con le stesse definizioni non avevano rilevato nulla: il rilevamento compare in esecuzione.

È il quarto candidato consecutivo segnalato. Ogni build produce un launcher nuovo e il modello automatico (`!ml`) lo segnala di nuovo: contestare il rilevamento file per file non è una soluzione sostenibile. Interventi sul launcher, in vigore dalle build successive a questa data:

1. **Bootloader compilato localmente.** `scripts/build_pyinstaller_bootloader.py` scarica lo sdist della versione PyInstaller installata, lo verifica con lo SHA-256 pubblicato da PyPI, elimina i bootloader Windows precompilati e li ricompila con MSVC (waf). Poi costruisce la wheel in una cartella nuova, la installa con `--install` e registra i digest con `--record` in `packaging/windows/bootloader/PROVENIENZA.json`. `scripts/build.py` rifiuta la build se il PyInstaller installato non usa quei bootloader o usa quelli della wheel pubblica (`runw.exe` pubblico `2291f269…5d41`). Il lockfile fissa ancora `pyinstaller==6.22.3` con gli hash della wheel pubblica: dopo un'installazione da lockfile si deve reinstallare la wheel locale, e il gate lo segnala. Il workflow manuale `desktop-build` compila il bootloader sul runner e passa a `build.py` la provenienza appena prodotta (`--bootloader-record`); non è ancora stato eseguito con questa modifica.
2. **Risorsa di versione.** Il launcher dichiara prodotto, versione, autore (come `AppPublisher` dell'installer), descrizione e nome file originale (`scripts/windows_launcher.py`, `--version-file`). Prima non aveva risorse `VERSIONINFO`.
3. **Firma Authenticode: aperta.** È l'unico intervento che consente a Microsoft di riconoscere anche le build future, tramite la reputazione del certificato. Richiede una decisione del titolare su servizio, costo e intestatario (per esempio un servizio di firma cloud o un certificato OV). Nessuna chiave o certificato creato.

Nessuno dei tre punti dimostra da solo l'assenza di rilevamenti. Il criterio resta quello sotto: installazione, avvio, chiusura e riapertura di un nuovo candidato con protezione attiva, senza nuovi eventi 1116. Non usare esclusioni né «Consenti». Il candidato `revisione-tecnica-20261115-01` resta bloccato.

Primo candidato con queste modifiche: `win-av02-20261115-02` (launcher SHA-256 `22f4f69f…f190`). Da collaudare sul PC con Defender attivo; esito da registrare qui e in VERIFICA.md.

*19 novembre 2026:* `win-av02-20261115-02` non è stato installato. Il successore `core020-20261119-01` (solo Windows, commit `9239cb8`, launcher SHA-256 `d04c0bd0…b0b0`, stesso bootloader locale) è il candidato su cui eseguire la prova; scansioni di confezionamento senza rilevamenti con definizioni 1.463.367.0, che come per i candidati precedenti non dimostrano l’esito in esecuzione.

*20 novembre 2026:* la prova va fatta su `rc-20261120-01` (commit `46959ed`, launcher SHA-256 `0e0b6bb8…4c78`, stesso bootloader locale), che succede a `core020-20261119-01` e aggiunge le traduzioni inglesi. Scansioni di confezionamento senza rilevamenti con definizioni 1.463.382.0.

*21 novembre 2026, pomeriggio:* la prova va fatta su `rc-20261121-02` (commit `0e3f900`, launcher SHA-256 `febf062f…3758`), che sostituisce `rc-20261121-01` con gli stessi sorgenti e documenti senza le segnalazioni; scansioni di confezionamento senza rilevamenti con definizioni 1.463.398.0.

*21 novembre 2026:* la prova andava fatta su `rc-20261121-01` (commit `ccc50ce`, launcher SHA-256 `a3649187…1eac`), destinato alla release; scansioni di confezionamento senza rilevamenti con definizioni 1.463.390.0.

*20 novembre 2026, pomeriggio:* la prova andava fatta su `rc-20261120-02` (commit `8e9de2d`, launcher SHA-256 `f7ed4824…ce4a`, stesso bootloader locale), che aggiunge SYNC-SPAZIO-01 ed è la base di `v0.10.0-alpha.1`. Scansioni di confezionamento senza rilevamenti con definizioni 1.463.384.0.

## 10 novembre 2026 — nuovo blocco sul PC destinatario

Il 10 novembre, dalle 09:52:46 alle 09:53:37, Defender ha rilevato Bearfoos sull’eseguibile installato (1116) e ha registrato la quarantena riuscita (1117), con definizioni 1.463.222.0 e motore 1.1.26100.4. L’EXE è assente. Il file del disinstallatore è datato 9 novembre alle 21:03:21. Le impronte dei file dell’interfaccia rimasti coincidono per 19/19 con ordine-maturazione-20261109-01 e per 18/19 con import-avvisi. Il launcher atteso del 9 novembre ha SHA-256 `6e7257afe7a3aae7dfc1772809d592e552f64181c52e8b98979fa714450b97d0`; manca un digest della copia rimossa. WIN-AV-01 resta aperto sul candidato corrente.

Alle 10:00:26 Defender ha registrato anche la quarantena della copia in `bundle/Fuorigiri/Fuorigiri.exe` della build del 9 novembre. Il file è assente da quella cartella. La copia intermedia in `work/Fuorigiri` risultava elencata, ma Defender ha impedito la lettura per il confronto SHA-256.

## 8 novembre, ore 23:12 — blocco riprodotto dopo aggiornamento Defender

Dopo la reinstallazione riferita dall’utente, il registro locale mostra le definizioni 1.463.191.0 alle 23:10:13 (evento 2000), rilevamenti Bearfoos sull’eseguibile installato dalle 23:12:17 e quarantena riuscita alle 23:12:50 (1116/1117). Entrambe le schermate riguardano lo stesso episodio. Il collegamento Start riportato punta al menu Programmi; l’elenco comprende anche il processo e la registrazione del disinstallatore. Il registro non identifica il componente responsabile. Il manifesto della consegna assegna al launcher 17.409.111 byte e SHA-256 `287c57daaac894a086e874241d8ace51bab19daf9e5fde22c6cadcdbd3f1259d`. Il digest della copia installata rimossa resta indisponibile. Il collaudo Windows è fallito anche con le nuove definizioni.

## 8 novembre 2026 — blocco dopo installazione del candidato import-avvisi

Sul PC destinatario il file di disinstallazione risulta aggiornato alle 18:41:09. Tutti i 19 asset dell'interfaccia installata coincidono per SHA-256 con il manifest di `import-avvisi-20261108-01`. Alle 18:42:04–18:42:42 gli eventi 1116 della protezione in tempo reale identificano il processo e il file installato `Fuorigiri.exe` come `Trojan:Win32/Bearfoos.A!ml` (ID 2147731250). Gli eventi 1117 registrano quarantena riuscita. Il launcher manca dalla cartella installata. Il suo SHA-256 atteso è `287c57daaac894a086e874241d8ace51bab19daf9e5fde22c6cadcdbd3f1259d`; manca un digest della copia rimossa.

Le definizioni 1.463.187.0 coincidono con quelle delle scansioni di confezionamento senza rilevamenti. Il registro documenta il blocco in uso, senza identificare il componente che lo provoca o mostrare comandi remoti eseguiti. WIN-AV-01 blocca anche questo candidato Windows. Nessun campione inviato in questa verifica.

## Riscontro del 7 novembre 2026 — WIN-AV-01 aperto

Il candidato `windows-alpha-review-20261102-01` è bloccato sul PC destinatario: Defender segnala `Trojan:Win32/Bearfoos.A!ml` (ID 2147731250) e rimuove `Fuorigiri.exe` dalla cartella di installazione. Eventi del 5 novembre alle 21:58–21:59 e del 7 novembre alle 20:09–20:10, ora locale. Il collegamento non trova più il file dopo l'intervento dell'antivirus.

L'installer indirizza collegamenti e avvio finale a `{app}\Fuorigiri.exe`; non contiene cancellazioni post-installazione. Nella cartella installata restano dipendenze, documentazione e disinstallatore, mentre manca l'EXE. Nessun difetto di destinazione del collegamento individuato.

La lettura dell'EXE originale della build per confrontarne il digest è stata bloccata con lo stesso rilevamento, alle 20:46 del 7 novembre. Il confronto con il portabile **non è stato completato**. La scansione mirata con `-DisableRemediation` ha stampato «found no threats», ma non costituisce assoluzione: le letture erano bloccate e la protezione in tempo reale conferma il rilevamento. Nessuna esecuzione del file sospetto durante questa diagnosi.

Definizioni osservate: **1.463.178.0**, motore **1.1.26100.4**, prodotto **4.18.26100.4**. Il tentativo di aggiornamento non ha cambiato le definizioni. Un possibile falso positivo resta un'ipotesi da sottoporre a Microsoft; non è stato dimostrato che il binario sia sicuro né che sia compromesso.

## Materiale per la revisione

Alle 21:03:33 del 7 novembre il registro operativo Defender ha rilevato anche la copia di lavoro `work/Fuorigiri/Fuorigiri.exe` (evento 1116). Alle 21:04:05 ha registrato «Metti in quarantena» sullo stesso percorso (evento 1117). La copia finale in `bundle/Fuorigiri` era già stata messa in quarantena alle 20:47:28. Al controllo successivo entrambi i percorsi risultano privi dell'EXE. Al controllo successivo nessuna copia del launcher era più direttamente disponibile.

- Candidato: `dist/candidates/Fuorigiri-0.10.0-windows-alpha-review-20261102-01/`.
- Installer: `Fuorigiri-0.10.0-windows-x64-setup.exe`, 196.889.335 byte; SHA-256 registrato alla preparazione: `402e9f45e4e6c97bed2a02444bad866b3edb8bb9aba81ec5887b0ded494b27c5`.
- Portabile: `Fuorigiri-0.10.0-windows-x64-portable.zip`; SHA-256 registrato: `8297ce92bfb08d103f8f0832791bd190791f185c42c1c1d4dee62a7c576dcc83`.
- Launcher PyInstaller onedir, Python/Qt inclusi, prodotto 0.10.0; binari non firmati Authenticode. Queste caratteristiche non dimostrano la causa del rilevamento.

I digest provengono dal manifest della consegna e **non sono stati ricalcolati in questa diagnosi**. Conservare la consegna originale senza modificarne manifest o checksum.

## Risoluzione e criteri di chiusura

1. Mantenere protezione e quarantena. Reinstallare lo stesso candidato non risolve il blocco; non aggiungere esclusioni o consentire il file per far superare la prova.
2. Sottoporre il campione alla [revisione ufficiale Microsoft](https://www.microsoft.com/en-us/wdsi/filesubmission), indicando Software developer, Microsoft Defender Antivirus, rilevamento ed eventi sopra. L'invio richiede accesso al portale e autorizzazione al caricamento; **nessun campione inviato durante questa attività**. Non includere archivi societari, credenziali o dati degli atleti. Se la protezione impedisce l'accesso al campione, usare il percorso di assistenza senza disattivarla per estrarlo.
3. Conservare l'esito della revisione fuori dalla repository. Se Microsoft conferma un falso positivo, aggiornare le definizioni e ripetere il controllo sul campione originale. Se emergono componenti compromessi, ricostruire da sorgenti e dipendenze verificati in ambiente pulito, con un nuovo identificativo candidato.
4. Ripetere installazione, primo avvio, chiusura e riapertura dal collegamento con protezioni attive; controllare che EXE e collegamenti restino presenti senza nuovi rilevamenti. Ripetere l'aggiornamento su archivio QA, senza dati operativi. Conservare separati gli altri gate pilot.

La [FAQ Microsoft per sviluppatori](https://learn.microsoft.com/en-us/defender-xdr/developer-faq) indica l'invio del campione per contestare un rilevamento. Firma, ricompilazione o smoke riuscito non dimostrano da soli che il problema sia risolto.

## Verifica di provenienza del 7 novembre 2026

Analisi statica della consegna e degli intermedi conservati nella directory di build. Nessuna esecuzione, estrazione o ripristino del launcher Fuorigiri. Nessun invio di campioni. Le verifiche di uguaglianza indicano esattamente quale copia è stata confrontata.

- **Consegna e sorgenti.** Ricalcolati tutti i 13 SHA-256 di `SHA256SUMS.txt`, inclusi setup e ZIP portabile. Dimensioni e digest corrispondono anche alle 12 voci di `candidate.json`. I 344 file dello ZIP sorgenti sono stati confrontati con gli oggetti Git, ammettendo per i testi la normalizzazione CRLF/LF. Rispetto alla base dichiarata `dbacff38` ci sono 29 file aggiunti o diversi. Rispetto al successore `52b6ef2` coincidono 339 file su 344, senza percorsi mancanti. Le cinque differenze riguardano AGENTS.md e le guide COLLAUDO_PILOT, PROSSIMI_PASSI, REVISIONE_ALPHA e VERIFICA. I 49 digest backend corrispondono ai sorgenti congelati. Tutti i 19 asset frontend nel portabile corrispondono a CONTENTS.json.
- **Codice confezionato.** Nel file intermedio `Fuorigiri.pkg`, il codice compilato di `desktop_entry.py` coincide con quello ottenuto dal sorgente congelato. L'archivio Python incorporato nel medesimo intermedio coincide con `PYZ-00.pyz`. Confrontati gli oggetti di codice senza eseguirli: corrispondono tutti i 48 moduli applicativi, i 5 moduli della wheel comune tracciata in Git e i 1.546 moduli provenienti dalle dipendenze installate (1.541 dai sorgenti delle wheel pubbliche e 5 dalla wheel comune, già contati). Le due distribuzioni locali `ciclo-test` e `fuorigiri` puntano alla stessa repository nell'ambiente di build. L'inventario registra anche pacchetti presenti nell'ambiente, indipendentemente dall'inclusione nel prodotto.
- **Dipendenze native del portabile.** Tutte le 294 voci BINARY e le 67 EXTENSION di `COLLECT-00.toc` coincidono con i file indicati come origine. Per 333 file si è verificata anche l'identità con il contenuto di wheel aventi SHA-256 pubblicato da PyPI. Gli altri 28 provengono da CPython. Per 27 c'è identità con lo ZIP ufficiale Windows 3.14.7 a 64 bit. Per `sqlite3.dll` lo ZIP embeddable contiene una variante diversa, ma il file della consegna coincide byte per byte con quello nel pacchetto ufficiale dell'installer `lib.msi`. SHA-256 della DLL `9a8fb79d6b7e581d127314028dcecf754b8d7fe4aca1247f82c1f33ee8fccc7e`, firma locale verificata valida della Python Software Foundation. [Distribuzione CPython 3.14.7](https://www.python.org/ftp/python/3.14.7/) e [pacchetto verificato](https://www.python.org/ftp/python/3.14.7/amd64/lib.msi).
- **Avvio PyInstaller.** Il registro EXE indica `runw.exe` della versione 6.22.3. La copia locale di quel componente coincide con la wheel Windows x64 ufficiale: SHA-256 della wheel `500bd58c7bf7e584a8435adccbd763a0b918d5c12b08d74ff50fd79b2915458b`, del componente `2291f269c3a3804fde1079462239e09a8b32fffbeeaa8f628a531faf5be77d41`. Entrambi identificano input di build. Nel portabile, i soli file con estensione .exe sono Fuorigiri.exe e QtWebEngineProcess.exe, quest'ultimo incluso nel controllo delle wheel. [Metadati della release PyInstaller su PyPI](https://pypi.org/pypi/pyinstaller/6.22.3/json).

**Esito WIN-AV-01.** Nessun componente inatteso emerso nei confronti descritti. Resta aperto il collegamento tra gli intermedi verificati e l'eseguibile effettivamente segnalato sul PC. I checksum complessivi consentono di riconoscere la consegna, ma manca un digest originario del singolo launcher e il confronto diretto tra copia di build e copia installata. Il candidato resta bloccato in attesa del collaudo con protezioni attive.

## Confronto con il predecessore Windows

Il riferimento è `pilot-20261101-01`. La successiva consegna `alpha-prep-20261102-01` riutilizza lo stesso bundle Windows. Il suo manifest originale registra per il vecchio launcher SHA-256 `0ef90127ff0975b1f4f25c59710c51e60eb837f9e7765a7ab57a6ead9c2ea671`. Le directory dei due ZIP portabili riportano rispettivamente 17.398.091 e 17.403.020 byte per il launcher precedente e quello segnalato.

- Nei sorgenti congelati sono identici l'ingresso desktop, lo script di build e lo script installer Windows. Entrambi usano PyInstaller 6.22.3, hook 2026.8, PySide6 6.12.0 e lo stesso percorso per il bootloader. Dei 19 file frontend nel portabile varia solo l'avviso legale di terze parti.
- Nel backend cambiano due moduli, `backup_stream` e `recovery`, per validare i membri delle copie di sicurezza prima del ripristino. Nell'ambiente di build cambiano Pillow 12.3.0 → 13.0.0, certifi 2026.7.22 → 2026.10.19, setuptools 84.0.0 → 84.1.0 e pypdf 6.21.2 → 6.21.4.
- Nei due intermedi `Fuorigiri.pkg` l'unica voce con contenuto differente è l'archivio di moduli Python `PYZ.pyz`. Confrontando le voci decompresse del PYZ cambiano 81 moduli comuni (76 Pillow, 2 Fuorigiri, 2 setuptools, 1 certifi). Scompare `PIL.ImageMath`, senza moduli aggiunti. Il PYZ non contiene pypdf. Questo confronto riguarda gli intermedi conservati, senza eseguire o ripristinare i launcher.
- Sul PC il marker del primo avvio riuscito del nuovo candidato reca data e ora locali **3 novembre 10:27**. Il registro Defender riporta l'aggiornamento a **1.463.102.0** alle 09:36 di quel giorno, quindi rilevamenti di Fuorigiri con **1.463.135.0** il 5 novembre e **1.463.178.0** il 7. Negli eventi 1116 disponibili dal 21 ottobre non compare un rilevamento di Fuorigiri precedente al 5 novembre. Il percorso installato è comune ai candidati. Non c'è una prova comparativa dei due launcher nelle stesse condizioni antivirus, né un'indicazione del componente responsabile.
