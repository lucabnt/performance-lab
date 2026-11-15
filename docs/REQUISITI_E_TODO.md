# Requisiti e to-do

## REV-TEC-01 — blocco 1 della revisione tecnica, 14 novembre 2026

Richiesta: implementare passo per passo il piano di [REVISIONE_TECNICA.md](REVISIONE_TECNICA.md), partendo dal blocco 1 (correttezza). **Implementato nei sorgenti e verificato con test automatici**; nessun nuovo EXE/APK.

- RT-03/RT-04: i download dei report (singolo test, storico e archivio) salvano un record `report` una sola volta per chiave (società, test e revisione, renderer, query, revisioni sorgente, formato, lingua). Il salvataggio richiede un admin non revocato: un admin revocato scarica il report senza scrivere. I duplicati già presenti restano invariati.
- RT-08: un `.ctindex` illeggibile viene elencato tra gli errori e la sync v2 prosegue con l’inventario completo.
- RT-07: salvataggi, lotti, annullamenti e applicazione degli eventi ricevuti prendono il lock di scrittura (`BEGIN IMMEDIATE`) prima del controllo di revisione.
- RT-14/RT-17: allegato assente → 422 «Allegato non presente nell’archivio locale.»; rimossi i rami irraggiungibili del percorso sync legacy.
- RT-13: le anteprime di ripristino in `restore-staging` più vecchie di 24 ore vengono rimosse all’avvio e a ogni nuova anteprima.

**Blocco 2 — implementato nei sorgenti, 14 novembre 2026:**

- RT-15: negli export CSV (archivio, estesi, maturazione, ripetibilità) i testi che iniziano con `=`, `+`, `-`, `@`, tabulazione o a capo ricevono un apice; numeri intatti. Tutti gli import CSV lo rimuovono in lettura; la trasformazione è reversibile anche per testi che iniziano già con un apice. Manifest dell’export aggiornato. Guida in IMPORT_CSV.md.
- RT-11: nota sulla cifratura del dispositivo (IT/EN) nella finestra «Licenza, limiti e backup», mostrata nella vista Info su Android e nel piè di pagina desktop; sezione «Proteggere i dati sul dispositivo» in SOCIETA_BACKUP_E_ACCESSI.md. Verificata nella GUI web desktop; vista Info Android non ricatturata.

**Blocco 3, voce 8 — implementata nei sorgenti, 14 novembre 2026:**

- RT-06: `scripts/verify.py` esegue tutte le verifiche locali con un solo comando e riepilogo; linter `ruff` 0.17.5 (dipendenza di sviluppo, solo errori pyflakes/sintassi) e workflow `verify.yml` su Windows, attivo dal 15 novembre 2026 a ogni push su `main`, sulle pull request e ad avvio manuale. Corretti i 70 rilievi iniziali (import e variabili inutilizzati), senza modifiche di comportamento; le riesportazioni di `transports.py` e gli import di prova di `desktop.py` sono esclusi per file.
- Criterio «workflow verde» non ancora verificato: richiede push e avvio su GitHub.

**Blocco 3, voce 9 — implementata nei sorgenti, 15 novembre 2026:**

- RT-05: formattazione automatica con `ruff format` e `prettier`, senza modifiche semantiche (AST Python identico, bundle frontend equivalente); controllo del formato in `scripts/verify.py`. Estrazione dei router API rinviata come previsto dal piano.

**Blocco 4, voce 10 — implementato nei sorgenti, 15 novembre 2026:**

- RT-11: opzione «Proteggi con password» per il backup v3 (download e salvataggio su disco) e ripristino dei file `.fgbak` con richiesta della password. Formato approvato dall'utente: involucro AES-256-GCM a blocchi da 1 MiB, chiave scrypt (n = 2^17) con parametri nell'intestazione, contenuto v3 invariato. Specifica in [BACKUP_CIFRATO.md](BACKUP_CIFRATO.md).
- Criteri: ripristino reale di un backup cifrato (API e GUI web), backup v3 in chiaro ancora producibili e leggibili, nessuna dipendenza nuova. Non provati l'emulatore o il telefono Android e l'EXE.

**Blocco 5, voce 11 — implementata nei sorgenti, 15 novembre 2026:**

- RT-01: `/state` usa `Store.list_without_samples`, che rimuove `samples` con `json_remove` in SQL; `has_trace` invariato. Misura preliminare richiesta dal piano: 513 ms su 300 test sintetici da 1.800 campioni, 93 ms dopo, risposta identica byte per byte; proiezione identica anche sui 7 archivi del corpus dimostrativo ridotto.
- RT-09: `ArchiveStore.verifier()` legge identità e revoche una volta e verifica ogni certificato una volta; usato da sync v1, sync v2 e controllo del recupero. Prima dell'invio si verificano solo gli eventi non ancora presenti nella cartella.
- RT-10: `Workspaces.get` riusa lo store finché lo stesso file `archive.sqlite` (dispositivo e inode) è presente; un file sostituito o assente viene riaperto con i controlli e le migrazioni consueti.
- RT-02: `Store.history` filtra con `json_extract` e l'indice `changes_record`, aggiunto senza cambiare `user_version`.

**Blocco 5, voce 12 — implementata nei sorgenti, 15 novembre 2026:**

- RT-12: `seal` scrive `kdf` (scrypt n = 2^17, r = 8, p = 1) nell'involucro di inviti e recupero; `unseal` legge gli involucri senza `kdf` con n = 2^14 e accetta solo n potenza di due tra 2^14 e 2^20 con r = 8 e p = 1. Le versioni precedenti dell'app non aprono i nuovi file.
- RT-18: intestazione `Content-Security-Policy` sulle risposte non `/api/` del backend (desktop e server di sviluppo). Android serve gli asset con il proprio loader e non riceve l'intestazione.
- RT-20: decoratore `viewer_allowed` (`backend/cycling_test/access.py`) sulle 24 rotte già consentite e su scollegamento e ricollegamento; il middleware individua la rotta e legge il marcatore. Le nuove rotte di scrittura restano vietate ai visualizzatori se non marcate.
- RT-19: azioni dei workflow fissate per SHA. Gli hash stanno in `requirements-lock-windows.hashes`, file distinto perché `sync-core.py` del common riscrive ogni `requirements*.txt` aggiungendo `requirements-common.txt` senza hash; nessuna modifica al common. La wheel comune si installa con `--no-deps --no-index` ed è verificata da `verify_core.py` sullo SHA-256 registrato. `verify.py` controlla offline che lock e hash coincidano. `scripts/lock_hashes.py` è consegnato dal common (fonte `cycling-suite-common/scripts/lock-hashes.py`), da non modificare qui.
- RT-16: `scripts/test_android_versions.py` crea un ambiente separato con `android/requirements.txt`, gli strumenti di test del lock desktop e la wheel comune, poi esegue `pytest`; job manuale `android-versions` su Python 3.12. Copre le differenze di libreria, non l'interprete Chaquopy 3.13 (numpy 1.26.2 e matplotlib 3.8.4 non hanno wheel PyPI per 3.13). Eseguito il 15 novembre: 358 test superati e 1 saltato (finestra Qt, PySide6 assente nel set Android).

## PUB-ALPHA-01 — prima distribuzione pubblica

Preparare uno snapshot con soli file tracciati e dati sintetici, verificare le revisioni raggiungibili, documentare licenze, allegati e gate per piattaforma. Il primo tag pubblico deve puntare ai sorgenti effettivamente distribuiti. [Distribuzione](DISTRIBUZIONE.md) e [prove](VERIFICA.md).

**13 novembre 2026 — binari nell’alpha:** l’utente vuole includere Windows e Android. Implementati gli avvisi Qt/Chromium nel bundle, la rimozione di `direct_url.json`, lo scanner dei percorsi e la procedura di ricostruzione neutra. Restano aperti: wheel ricostruite su Fedora, firma release, prove su telefono e su PC pulito, WIN-AV-01 e la decisione sull’accesso ai sorgenti Qt. WebDAV è l’unico provider con prova riferita (S-02).

## INT-ICU-01 — riservatezza degli esempi, 10 novembre 2026

Richiesta: verificare l’ID Intervals fornito come esempio e sostituirlo perché può identificare un profilo reale. Corretto nei sorgenti: segnaposto `i…` senza identificativo numerico, istruzioni IT/EN sul formato, URL parametrico nella guida e fixture locale sintetica di 39 cifre nei test (nessuna chiamata al provider). Anonimizzato anche l’ID nella citazione storica della richiesta; nessuna modifica ai dati degli atleti. Schermata editor rinnovata senza ID salvato. Il campo era già vuoto per i nuovi atleti; l’esempio non era un default. Pacchetti nativi preesistenti non aggiornati. Prove in VERIFICA.md.

## Consegna ordine/maturazione — 9 novembre 2026

UI-ORDINE-02 e MAT-AVVISI-01 inclusi nel candidato locale `ordine-maturazione-20261109-01`: installer/portabile Windows, APK debug con firma di test esistente, release non firmato, supporto strumentale, sorgenti e wheel prodotti e verificati, **25 checksum**. Supera le note «nessun nuovo EXE/APK» della fase di implementazione sottostante. Nessuna accettazione Windows pulito, runtime Android, firma release o qualifica 16 KB implicita. Prove in VERIFICA.md.

## UI-ORDINE-02 / MAT-AVVISI-01 — 9 novembre 2026

Richieste originali: «nella pagina atleti, dovrebbe essere possibile ordinarli per Atleta > mi aspetterei un ordine alfabetico per cognome»; «nella pagina del singolo atleta test e misure atropometriche dovrebbero presentarsi sempre ordinate per data dal più recente. Nel caso eccedessero entrambe le 15 rilevazioni, le manderei ad una pagina sucessiva»; «Ok il limite della data di nascita, ma per cose noon bloccanti vorrei che venissero calcolati gli indici, anche qua visualizzazione dal più recente» (allegata tabella delle stime Moore/Mirwald).

Implementato nei sorgenti: Atleti ordinati inizialmente per cognome e nome, controllo Atleta sul valore anagrafico senza avatar/didascalia. Test e antropometria dal più recente, pagine indipendenti da 15; grafici e calcoli mantengono tutti i dati. Tabelle maturative principali e facoltative dal più recente. Motore growth-maturity/2: fonte non misurata e qualità incerta diventano avvisi non bloccanti per Moore/Mirwald, %PAH/residuo e proporzioni. Restano necessari nascita completa per gli offset, parametro M/F, dominio di età e input specifici; misure escluse indisponibili. HV/PHV e stabilità conservano i gate precedenti. Formule e snapshot già conservati invariati. Riscontri in VERIFICA.md; nessuna nuova build nativa.

## Consegna import-avvisi — 8 novembre 2026

ANTRO-IMPORT-AVVISI-01 e UI-SCROLL-01 inclusi nel nuovo candidato locale `import-avvisi-20261108-01`, con le funzioni precedenti. Build Windows/Android prodotte e confezionate; contenuti, 25 checksum, smoke/scansioni Windows e firme/allineamento APK verificati. Supera le note «nessun nuovo candidato» delle precedenti fasi di implementazione, che restano come cronologia. Nessuna accettazione runtime Android, Windows pulito, firma release o qualifica 16 KB implicita. [Prove](VERIFICA.md).

## ANTRO-IMPORT-AVVISI-01 — metadati non bloccanti, 8 novembre 2026

Richiesta originale: «Correggi la logica, non dovrebbero esserci problemi per incongruenze nella colonna che non contenga una misura, nel caso segnalarlo mantenendo la versione precedente ma non limitare l’importazione».

Implementato nei sorgenti: date/peso identici su due rilevazioni con fonte dichiarato/derivato non generano più ambiguità al reimport di dati già presenti. Si riconoscono prima i sottoinsiemi numerici acquisiti, poi le corrispondenze di fonte/origine aiutano a distinguere le destinazioni delle integrazioni. Le differenze di fonte/origine producono avvisi con riga, atleta, data, campo, precedente e CSV; il dato precedente resta invariato e il lotto può essere confermato. Anche una fonte CSV sconosciuta su una rilevazione esistente viene ignorata con avviso; per nuove rilevazioni serve una fonte valida. Identità atleta e data restano necessarie per riconciliare i record; misure discordanti, record eliminati e aggiunte con più destinazioni realmente ambigue restano errori atomici. Nessuna fusione/cancellazione delle rilevazioni storiche. Supera la precedente regola bloccante sui metadati di ANTRO-INCREMENTALE-01. Prove in VERIFICA.md. Nessun nuovo candidato nativo.

## UI-SCROLL-01 — scorrimento dopo eliminazione, 8 novembre 2026

Richiesta originale: «Dopo eliminazione di un record di antropometria, la pagina successiva non scorre più su e giù, verifica e correggi».

Riprodotto nel browser: chiusura simultanea di editor e conferma ⇒ nessun dialogo aperto ma `body.style.overflow=hidden`. Corretto nel Dialog di `@cycling-suite/ui` 0.2.9: blocco condiviso per documento, stile iniziale ripristinato soltanto alla chiusura dell’ultima finestra, senza dipendere dall’ordine dei cleanup; rilascio idempotente e recupero anche se showModal fallisce. Nessun reset CSS locale nel prodotto. Dopo annullamento resta bloccato solo lo sfondo dell’editor; dopo eliminazione confermata scorrimento libero in entrambe le direzioni e nelle pagine successive. Prove automatiche e GUI in [VERIFICA.md](VERIFICA.md). Candidati EXE/APK esistenti invariati.

## Consegna antro-incrementale — 8 novembre 2026

ANTRO-INCREMENTALE-01, ANTRO-PERINEALE-01 e RECORD-LIFECYCLE-01 inclusi nel nuovo candidato locale `antro-incrementale-20261108-01`: Windows installer/portabile e APK debug/release non firmato prodotti, contenuti e checksum verificati. Smoke/scansioni Windows riusciti; runtime Android e accettazione esterna restano distinti. Questa consegna supera le note «nessuna nuova build» riferite alle precedenti fasi di implementazione, senza cancellarne la cronologia. [Prove](VERIFICA.md).

## ANTRO-INCREMENTALE-01 — integrazione CSV, 8 novembre 2026

Richiesta originale: «implementa l’integrazione incrementale». Successiva ad ANTRO-PERINEALE-01, ne sostituisce il precedente comportamento sulle righe arricchite.

Implementato e verificato nei sorgenti: per atleta/data l’import riempie solo peso, statura e altezza perineale mancanti di una rilevazione attiva compatibile e univoca. I valori comuni devono coincidere; tra più rilevazioni compatibili non viene scelta automaticamente una destinazione. Fonte e origine esplicite discordanti sono errore; se omesse si conservano quelle esistenti. Campi vuoti non cancellano dati; qualità, note, campi avanzati e identità rimangono invariati. Il record integrato conserva ID e una nuova revisione con motivo e hash del CSV. Righe complementari dello stesso lotto confluiscono nello stesso record; reimport di sottoinsiemi già acquisiti saltati.

Anteprima con Nuova rilevazione / Integra rilevazione e campi da aggiungere. `plan_hash` lega la conferma al piano e alle revisioni osservate: cambiamenti richiedono nuova anteprima. Un errore blocca tutte le scritture; la transazione include creazioni, revisioni, outbox e lotto. Nessun ripristino implicito di eliminati, sovrascrittura di valori discordanti o fusione delle rilevazioni storiche già distinte. La visualizzazione del rapporto resta limitata al singolo record risultante. Prove in VERIFICA.md; nessun nuovo EXE/APK.

## ANTRO-PERINEALE-01 — altezza perineale, 8 novembre 2026

Richiesta originale: «nuovo standard per import di dati antropometrici, con colonna dedicata all’altezza perineale. Se stessa occorrenza riporta entrambi i dati, calcola nel profilo atleta la colonna con il rapporto. Implementa».

Implementato nei sorgenti: colonna CSV facoltativa `altezza_perineale_cm`, conservata come `perineal_height_cm`, distinta dagli arti inferiori. Modello, anteprima, import, export ed editor aggiornati; ammessa anche rilevazione con sola altezza perineale. Nel profilo: valore in cm e rapporto perineale/statura × 100, solo con entrambi i valori nello stesso record. Nessuna fusione per data o ricalcolo degli snapshot maturativi. Valori positivi, finiti, fino a 180 cm e inferiori alla statura quando presente. CSV precedenti compatibili; duplicati distinguono anche la misura perineale. Comportamento iniziale sulle righe arricchite sostituito da ANTRO-INCREMENTALE-01 (sezione successiva della stessa giornata). Nessuna importazione dei dati personali allegati negli archivi QA. Prove in VERIFICA.md; nessuna nuova build nativa.

## RECORD-LIFECYCLE-01 — eliminazione dagli editor, 8 novembre 2026

Incluso nel nuovo candidato locale `record-lifecycle-20261108-01`: installer/portabile Windows e APK debug/release non firmato prodotti e confezionati. Smoke e controlli di integrità eseguiti; accettazione operativa ancora distinta, dettagli in [VERIFICA.md](VERIFICA.md).

Richiesta originale: «una rilevazione può essere corretta ma non cancellata. una volta selezionato correggi rilevazione dovrebbe essere possibile anche eliminarla. Vale per rilevazioni antropometriche che per i test.»

Implementato nei sorgenti: **Elimina rilevazione** nell’editor antropometrico esistente e **Elimina test** nelle correzioni di test incrementali con tracciato, manuali/storici, Sprint/Wingate e personalizzati. Conferma separata con Dialog comune, senza imporre il salvataggio o la validazione della bozza. Eliminazione recuperabile per revisione tramite `records/{id}/status`, esteso alle misure (solo active/deleted); API state mantiene `measurement` attivo e aggiunge `deleted_measurement` per il recupero. **Rilevazioni eliminate** nel profilo e **Test eliminati** nel profilo/in Test e analisi consentono Ripristina agli Admin dati. Mancanti/esclusioni nei calcoli correnti restano espliciti; revisioni, oggetti originali, input dei test e snapshot già conservati restano invariati. Propagazione con sync e backup esistenti, conflitto sulla revisione obsoleta e ruolo viewer preservati. Prove e limiti in [VERIFICA.md](VERIFICA.md); nessun nuovo EXE/APK implicito.

## SYNC-AUTO-01 e INT-ICU-01 — 7 novembre 2026

Richiesta: «quando avviene la sincronizzazione con webdav? […] fuorigiri windows non sincronizzava il contenuto locale se non triggerato. Scegliamo la strategia migliore per risolvere»; «feature […] attivabile e disattivabile […] id intervals.icu (eg. [ID omesso per riservatezza]) […] vedi su Intervals.icu». Approvata l’implementazione della proposta combinata. Correzione esplicita successiva: «gli id dovrebbero essere sincronizzati insieme a tutti i dati» e «lascia il campo, togli il pulsante alla disattivazione».

**SYNC-AUTO-01, implementato nei sorgenti:** una società gestita con destinazione configurata avvia lo stesso motore incrementale all’apertura, dopo circa 10 secondi di raggruppamento delle modifiche e ogni 5 minuti. Automatismo predefinito attivo, disattivabile per dispositivo/archivio, conservato in `sync-automatic.json` fuori dagli eventi e dai backup. Retry progressivo 30 s–30 min; una sola operazione per archivio; lavori manuali e verifica completa restano distinti. Ultimo scambio riuscito separato dall’ultimo tentativo. Nessun servizio Windows ad app chiusa; il background Android esistente resta una scelta separata.

**INT-ICU-01, implementato nei sorgenti:** campo `intervals_icu_id` facoltativo, vuoto oppure `i` seguito da cifre (massimo 40 caratteri), sempre presente nell’editor atleta per Admin dati. Interruttore `intervals_icu_enabled` nella società, inizialmente falso; revisione con conflitto ottimistico e stessi permessi. Con opzione attiva e ID valido il profilo mostra “Vedi su Intervals.icu”, URL HTTPS fisso `https://intervals.icu/athlete/{id}/activities`. Spegnimento conserva campo e valore, nascondendo soltanto il pulsante. ID e opzione condivisi con eventi/backup; aggiornamenti di vecchi client senza ID non lo cancellano. Nessun accesso alle API Intervals.icu.

Accettazione: debounce/ricezione periodica/retry con orologio controllato; isolamento preferenze; scambio e ripristino degli ID/opzione; validazione, conflitti e ruolo viewer; GUI con funzione disattiva/attiva e invio senza comando. Prove e limiti in [VERIFICA.md](VERIFICA.md). Non rilasciato in un nuovo pacchetto nativo.

**Aggiornamento 8 novembre, ore 18:42.** WIN-AV-01 blocca anche il candidato Windows corrente. [Diagnosi](WINDOWS_DEFENDER.md).

## WIN-AV-01 — EXE Windows rimosso dopo installazione, 7 novembre 2026

Richiesta: «installando l'ultimo candidato su windows […] dice che exe non esiste più. Verifica e in caso correggi». Diagnosi completata sul PC destinatario: Defender rimuove l'EXE e blocca anche l'originale di build con `Trojan:Win32/Bearfoos.A!ml`; nessun errore di destinazione individuato nell'installer. **Risoluzione aperta**. Il 10 novembre è stata osservata la quarantena anche sull’installazione di ordine-maturazione. Resta da ottenere installazione, avvio e riapertura del candidato corrente con definizioni aggiornate e protezioni attive. [Dettagli e criteri](WINDOWS_DEFENDER.md), [prove](VERIFICA.md). Nessuna correzione del binario o accettazione dichiarata.

## GRUPPI-05 e ANTRO-IMC-01 — elenco filtrato e IMC, 7 novembre 2026

Richieste originali: «Se qui apro mostra atleti mi porta all'elenco filtrato, senza possibilità di aggiungere»; «Procedi con le due feature suggerite», riferite al comando collettivo nell’elenco filtrato e all’IMC descrittivo.

- **GRUPPI-05:** Aggiungi atleti al gruppo disponibile nell’elenco filtrato per categoria o stagione, anche con rosa già popolata o senza risultati di ricerca. Una stagione è preimpostata; dalla categoria si sceglie esplicitamente la destinazione, limitata alla categoria e alle sue stagioni attive. Il dialogo usa tutti gli atleti attivi della società, non solo quelli visibili nel filtro. Date modificabili, doppioni e permessi Admin dati restano governati dal flusso atomico esistente.
- **ANTRO-IMC-01:** colonna IMC (BMI) in kg/m² nelle rilevazioni datate del profilo, formula kg/(cm/100)² solo con peso e statura numerici, finiti e positivi dello stesso record. Nessun abbinamento fra date o record diversi. Fonte originale conservata, — se incompleto; grafico storico facoltativo con almeno due valori. Nessuna classificazione, percentile, stima di composizione corporea o obiettivo prestativo. Calcolo descrittivo frontend senza modifica di record, snapshot o versioni del motore di maturazione. Fonti e uso in [MATURAZIONE.md](MATURAZIONE.md), prove in [VERIFICA.md](VERIFICA.md).

## ANTRO-CHART-01 — collegare le misure disponibili, 7 novembre 2026

Richiesta originale: «correggiamo per far si che si connettano», riferita alle interruzioni delle linee peso e statura nel profilo atleta. Implementato il collegamento visivo dei punti disponibili di ciascuna serie, anche in presenza di rilevazioni intermedie della sola altra misura. Criteri: peso e statura mantengono date, valori, unità e scale indipendenti; i mancanti restano tali nella tabella e nei dati; nessun punto sintetico, ricalcolo o modifica al motore di maturazione. Prove e limiti in [VERIFICA.md](VERIFICA.md).

## ALPHA-REVIEW-01 — revisione generale pre-alpha, 2 novembre 2026

Seguito autorizzato: preparati auditor dell'intero APK (incluse stdlib Chaquopy), contratto ABI dei consumatori e ricette sorgenti per risolvere i sei moduli a 4 KB: pydantic-core 2.41.4 con linker 16 KB, FreeType 2.15.0, libpng 1.6.59, OpenBLAS 0.3.34 con LAPACK e LP64. [Procedura e gate](ANDROID_NATIVE_16KB.md). Ancora da eseguire sul builder e qualificare; pin e manifest nativi dell'app invariati in questa fase, nessun nuovo APK con le dipendenze candidate.

Aggiornamento Pillow: due wheel 13.0.0 cp313/API26 compilate dall'utente su Fedora e trasferite su Windows; checksum, CRC, RECORD, dieci moduli ELF e segmenti LOAD a 16 KB verificati localmente. Pin Android, gate di otto wheel, manifest/provenienza e avvisi legali aggiornati; controllo strumentale immagini/font/Matplotlib/ReportLab integrato. [Procedura e criteri](ANDROID_PILLOW.md), [esiti build/runtime](VERIFICA.md). Restano telefono, firma, flussi completi e audit nativo: Matplotlib conserva dipendenze Chaquopy separate, incluse vecchie FreeType/libpng. Nessuna modifica ai metodi scientifici.

Richiesta: verificare problemi, errori e vulnerabilità prima della prima alpha e correggere quanto riscontrato. Implementati rifiuto esplicito dei ZIP cifrati/non supportati e aggiornamenti di sicurezza delle dipendenze Windows/frontend; aggiornato python-multipart Android nei requisiti. Verifiche automatiche e smoke riusciti, dettagli in [REVISIONE_ALPHA.md](REVISIONE_ALPHA.md). **Parziale per la distribuzione**: Pillow Android 11.0.0 con avvisi noti richiede wheel corrette/backport verificato per entrambe le ABI e collaudo; audit nativo più ampio ancora aperto. Occorre un nuovo candidato, poi i gate operativi del pilot. Nessuna pubblicazione o modifica dei pacchetti esistenti.

## PILOT-01 — preparazione prima alpha, 2 novembre 2026

Richiesta: verificare installer e APK rispetto al codice e allinearli in preparazione della prima alpha. Il confronto dello snapshot e del frontend ricompilato conferma il codice dell'installer `pilot-20261101-01`; l'APK del 31 ottobre precede UI-SUITE-001 e viene ricompilato. Versione prodotto 0.10.0 e candidato di preparazione separato, nessuna pubblicazione. Conservare un APK debug per il percorso di test esistente e un release non firmato per la successiva firma del titolare. Criteri: integrità, asset correnti, ABI, firma debug invariata, release non firmato, allineamento e manifest/checksum; esiti effettivi in VERIFICA.md. Restano i gate operativi della checklist COLLAUDO_PILOT.md prima della distribuzione alpha.

## VO2-01 — consumo di ossigeno, 31 ottobre 2026

Richiesta originale: «fuorigiri dovrebbe supportare anche i dati di VO2 oltre al lattato. Implementa.»

Integrazione del supporto gas già esistente: inserimento di osservazioni VO₂ temporizzate con fonte/nota, import nello stesso CSV dei segnali, mantenimento dell’import gas dedicato. Unità esplicite L/min; normalizzazione mL/kg/min dal peso associato al test. Non si ricava VO₂ da watt o FC. Un’unica fonte per prova evita la fusione accidentale di misure incompatibili. Analisi VO₂peak con finestre/copertura/esclusioni del preset; dati isolati visibili senza fabbricare un picco medio. VO₂max resta distinto e richiede verifica dichiarata con evidenze. Grafico comune, selettore nello storico del profilo, report/CSV estesi con provenienza, osservazioni e revisioni. Implementato e incluso nel candidato Windows pilot-20261031-01 e nell’APK debug pixel9-test-20261031-01; prove e limiti in VERIFICA.md. Nessuna pubblicazione o qualifica su dispositivi fisici.

## UI-ORDER-01 — integrazione del 27 ottobre 2026

Ripristinare Soglia relativa in W/kg fra i KPI aerobici, accanto alla soglia in W, anche nell’anteprima. Implementato in ReferenceSummary usando analysis.threshold_wkg già salvato; valore mancante esplicito, senza deduzione dal peso corrente del profilo. Il grafico disponibile resta in apertura. Correzione ai sorgenti successiva ai pacchetti 20261027-01.

## UI-ORDER-01 — ordine delle informazioni, 26 ottobre 2026

Richiesta: razionalizzare la presentazione delle pagine e riunire i KPI del dettaglio test. Implementato nei sorgenti: un solo riepilogo aerobico (MAP operativa, MAP relativa, soglia, FTHR, FC massima), senza doppione MAP, seguito da zone, recupero e approfondimenti. Nota integrativa recepita: quando esiste un grafico temporale con osservazioni effettive, viene prima del riepilogo, subito dopo testata/comandi; senza campioni/valori rappresentabili il riepilogo rimane in alto e la spiegazione sul tracciato mancante segue i risultati. Vale per tutte le famiglie e anche per soli prelievi lattato temporizzati. Un semplice allegato non basta a produrre un grafico. Fonte e coefficiente conservati, stessa sintesi nell’anteprima. Anaerobici: quattro indicatori principali senza ripetizioni nella tabella Altri risultati richiudibile. Profilo: riepilogo, zone, MAP storiche, elenco test, antropometria con grafico adiacente, maturazione, appartenenze. Pagina test: elenco prima della guida richiudibile. Storici: analisi principale prima della ripetibilità. Archivio: report conservati accanto alla generazione. Atleti, protocolli e gruppi conservano contesto/comandi/filtri prima degli elenchi, già coerenti con il criterio. Nessuna modifica a calcoli, dati, filtri o autorizzazioni. Verifiche e limiti in VERIFICA.md; queste modifiche non sono negli installer precedenti.

## ZONE-03, SYNC-UX-02, AND-START-01 — 26 ottobre 2026

Richiesta: Scegli zone apparentemente inattivo, MAP storiche subito dopo le zone, percentuali poco chiare; spinner scompare cambiando scheda e durata/esito/incrementalità dello scambio non comprensibili; blocchi Android sia Preparazione motore locale sia Apertura interfaccia. Implementati Dialog editor, riepilogo compatto e colonna percentuali; stato job globale con fase, tempo, conteggi ed esiti, backend non bloccante, recupero dello stato al reload. Android background non trattiene Runtime.lock sulle attese di rete; deadline/retry e watchdog espliciti. La causa concreta identificata nel codice è un percorso di blocco tra rete e UI/avvio, non una diagnosi completa del telefono senza log. Prova Pixel fisico e provider reale rimangono distinta qualificazione.

## ZONE-02 — zone su tutti i test aerobici e adozione sul profilo, 25 ottobre 2026

Richiesta: mostrare le zone FC/watt anche senza FIT, ultime versioni sul profilo e scelta fra zone di un test o custom. Implementato: lettura compatibile degli storici senza modifica degli originali, snapshot sui nuovi import, nessun tempo di permanenza senza campioni; dati mancanti espliciti. Profilo automatico per ultimo canale disponibile oppure snapshot da test/revisione scelti con anteprima, oppure schemi percentuali/riferimenti personalizzati con nuova versione. Persistenza nel record atleta, controlli concorrenza/atleta/società e ruolo, modifica anagrafica conservativa. Renderer individuale aggiornato per gli stessi intervalli.

## SYNC-UX-01, DEVICE-PREF-01 e SOCIETY-LOCAL-01 — 25 ottobre 2026

Richieste: configurazione WebDAV Android, dubbio sul fuso degli orari, spinner fino al termine della sincronizzazione, riapertura nell'ultima lingua e rimozione della società dal solo dispositivo. L'utente sceglie scollegamento con ripristino, senza cancellare file locali. Implementazione: stato operativo e blocco richieste/configurazione; fuso esplicito e preferenze locali persistenti; bootstrap della lingua prima dei moduli UI; registro locale con flag detached, ripristino senza nuova identità e protezione dei percorsi riservati. Nessuna modifica ai formati di sync, revoca remota o cancellazione dati. Guida WebDAV con invito e password applicazione, distinta dalla password dell'invito.

## REPORT-SAVED-02 e AND-TEST-01 — 25 ottobre 2026

Richiesta: rendere Report conservati richiudibile come Condivisione e collaboratori; installare l'app sul telefono per testare la sincronizzazione. Telefono indicato: Android Google Pixel 9; disponibile solo Google Drive, senza WebDAV. Implementata sezione inizialmente chiusa con stato dei filtri e pagina conservato. Preparato APK debug personale e guida; firma/allineamento verificati, installazione fisica e sincronizzazione cloud non eseguite. La cartella del client cloud è solo desktop: per lo scambio con Android occorrono WebDAV oppure registrazioni OAuth dei provider API; il vincolo Drive senza GCP resta irrisolto e non va dichiarato supportato.

## AEROBIC-REF-01 — coefficiente della potenza di soglia, 25 ottobre 2026

Richiesta: mostrare nel dettaglio aerobico il coefficiente usato per la potenza di soglia. Causa nei CSV: `coeff_soglia` conservato nei campi storici ma assente nelle impostazioni lette dal riepilogo. Lettura compatibile con originali, senza inferenze dai watt; impostazioni corrette esplicitamente (anche null) prevalgono sull'import originale. Coefficiente e percentuale visibili, assenza dichiarata, soglia dichiarata distinta da stima MAP. Nuovi import copiano il coefficiente valido nelle impostazioni senza ricalcolare risultati storici.

## REPORT-SAVED-01 — organizzare i report conservati, 25 ottobre 2026

Richiesta: evitare una lista infinita; successiva indicazione esplicita: 5 report per pagina. Implementazione: RecordCards comune, ordine dal più recente, ricerca per ambito/data/riferimento e filtro formato; azzeramento pagina sui filtri e cambio archivio. Metadati di contesto per distinguere società, gruppo, stagione, atleta e data test; data di creazione ricavata dalla revisione, assenti mostrati senza inventare valori. Nessuna cancellazione o modifica dei report originali. Nessuna modifica al formato di sincronizzazione.

## REPORT-ARCHIVE-01, GRUPPI-04 e DOC-DRIVE-01 — 25 ottobre 2026

Implementati e verificati nel browser: indicatore animato e stato accessibile per le tre azioni report, blocco invii concorrenti e ripristino dei controlli al termine; apertura delle rose stagionali con filtro Tutti e ricerca vuota, inclusi gli atleti archiviati. PDF con indice iniziale navigabile, numeri pagina, capitoli e schede atleta separate; dimensioni leggibili, intestazioni ripetute e larghezze entro i margini. Conservati dati, metodi e risultati. Test automatici su indice, ambito individuale e tabelle lunghe, più ispezione delle pagine renderizzate di un archivio sintetico. Guida Drive pronta; consenso reale e sincronizzazione fra account/dispositivi restano da collaudare con le registrazioni del titolare.

## GRUPPI-01 — assegnazione singola e multipla

Richiesta: aggiungere appartenenze dal profilo e dal gruppo, selezionando più atleti dal gruppo. Implementato nei sorgenti: azione in testa al profilo, su gruppo/stagione e lista filtrata; ricerca, selezione multipla e selezione di tutti i risultati; periodo/anno di categoria espliciti. Salvataggio atomico con controllo società, stato attivo e sovrapposizioni sullo stesso gruppo. Selezioni già coperte non duplicate; storico conservato, accesso visualizzatore bloccato.

## IMPORT-03 — import test e modelli CSV vuoti

Richiesta: correggere anteprime aerobici/anaerobici, offrire CSV vuoti compilabili dalla sezione import e generalizzare il nome/metodo anaerobico. Implementato: preview test con atleta, data, protocollo e metriche; nuovi protocolli separati da righe pronte. Quattro modelli scaricabili con sole intestazioni canoniche. Sprint 3–10 s, Wingate 15/30 con tipo e durata espliciti; compatibilità storico ANA-15-070 senza reinterpretazioni. Mancanti non trasformati in zero; import rimane riepilogo dichiarato e non ricostruisce campioni.

## IMPORT-02 — anteprima e provenienza antropometria

Richiesta: rendere leggibile l’importazione antropometrica. Implementato: atleta riconciliato, data e misure con unità, fonte e origine; conteggio record visibili nell’anteprima limitata a 20. Preservare misurato, arrotondato, dichiarato, derivato e stimato senza conversioni silenziose; origine anche nelle correzioni e nell’export. I modelli di crescita continuano a richiedere misure misurate e valide. Nessuna correzione retroattiva automatica degli import precedenti.

## IMPORT-01 — anteprima anagrafica CSV

Anteprima specifica per atleti con identità, nascita e provenienza, stato e note; nessuna Data generica. Errori visualizzati solo se presenti. Implementato nei sorgenti il 22 ottobre 2026; importatore e archivi invariati.

## PROTOCOLLI-01 — codice modificabile, 22 ottobre 2026

Richiesta: Codice precompilato ma modificabile anche per Wingate e altre famiglie. Implementato nei sorgenti per incrementali manuali/ERG, Sprint, Wingate 15/30 e personalizzati. Proposta iniziale dal tipo, codice salvato riproposto nelle nuove versioni; metodo anaerobico indipendente dal codice. API precedenti compatibili, storici intatti e duplicati codice/versione rifiutati. Contratto e limiti delle revisioni in [Protocolli e campi](PROTOCOLLI_E_CAMPI_CUSTOM.md). Verifiche in VERIFICA.md.

## DESKTOP-01 — ultima società alla riapertura, 22 ottobre 2026

**Implementato nei sorgenti.** All’avvio desktop riaprire l’ultima società visualizzata, inclusa quella appena creata, senza ripetere la selezione. Preferenza del dispositivo (soli ID di archivio e società), indipendente dalla porta HTTP, esclusa dai dati condivisi. Validazione contro inventario e stato; archivio ricordato assente: selettore con avviso, senza scegliere un’altra società. Funziona anche per il visualizzatore senza concedere scritture societarie. Android mantiene il comportamento esistente. Accettazione sull’installer aggiornato ancora da eseguire.

## PILOT-01 — candidato e accettazione Windows/Android, 21 ottobre 2026

Richiesta: preparare un candidato e una checklist Markdown con completamenti. Versione prodotto conservata 0.10.0, ID candidato separato. Build isolate, Windows dipendenze incluse/installer/portabile; Android release non firmato su scelta esplicita del titolare, con procedura per chiave stabile e firma. Sorgenti/wheel/provenienza e checksum a corredo, nessuna pubblicazione. Criteri: regressione locale, smoke congelato, integrità pacchetti e checklist tracciata; PC pulito, firma, telefono, provider reali e validazione esterna restano gate distinti prima della promozione. [Collaudo](COLLAUDO_PILOT.md), [firma](FIRMA_ANDROID.md).

## TD-106–107 — marchio e grafico immersivo Android, 21 ottobre 2026

- **TD-106 — implementato, corretto su indicazione dell’utente:** nella testata Android scritta Fuorigiri/Performance Lab allineata a destra, seguita dal logo alla sua destra; intero gruppo sul bordo destro, hamburger a sinistra. Variante comune brand-end dalla UI 0.2.8. Sostituisce la precedente indicazione “logo a sinistra” nella testata; bootstrap centrati e sidebar desktop conservano la propria composizione. Il logo societario resta distinto e fisso.
- **TD-107 — implementato e verificato su emulatore:** Vista ampia orizzontale usa l’intera WebView, senza cornice o intestazione visibile “Esplora grafico”. Titolo accessibile conservato; X flottante e pannello Comandi grafico richiamabile, chiuso di default. Grafico alto quanto il viewport; comandi/dati non sottraggono una fascia permanente. Barre Android temporaneamente nascoste, richiamabili con swipe di sistema; ripristino della visibilità/politica precedente alla chiusura insieme all’orientamento. Back esce prima dall’esplorazione, poi chiude il pannello aperto, poi la vista. I comandi restano sotto il grafico nella vista normale. Cutout/insets di sicurezza rispettati; telefono/TalkBack/tablet da qualificare.

## TD-105 — Vista ampia orizzontale Android, 21 ottobre 2026

**Implementato e verificato su emulatore:** Vista ampia richiede temporaneamente sensorLandscape tramite bridge nativo di origine fidata; memorizza la precedente politica di orientamento e la ripristina alla chiusura, allo smontaggio della vista o al reload della WebView. La rotazione non ricarica il test e il grafico adatta altezza/larghezza al viewport. Scorri pagina rimane il default; un Back esce da Esplora/Zoom restando in orizzontale, il successivo chiude la vista e ripristina l’orientamento. Nessuna modifica all’orientamento globale delle altre schermate. Telefono e finestre/tablet rimangono da qualificare.

## TD-102–104 — grafici touch, avvio e contesto Android, 21 ottobre 2026

- **TD-102 — implementato, collaudo emulatore:** hamburger sempre a sinistra, nessuna freccia Indietro duplicata nella testata; ritorno tramite tasto/gesture di sistema. Padding e margini Android moderatamente ridotti, senza ridurre i controlli sotto 48 CSS px. Grafici in Scorri pagina per default, anche nella vista ampia: comandi Esplora, Zoom, Ripristina e Vista ampia sotto la figura. Un solo Indietro esce da Esplora/Zoom, mantenendo aperto il dettaglio; successivamente chiude l’ultimo dialogo e poi segue la cronologia. Dialoghi annidati isolano cancel. Zoom/pan riservano le gesture al grafico soltanto dopo attivazione esplicita; nessuna modifica ai campioni/calcoli.
- **TD-103 — implementato:** apertura nativa con indicatore indeterminato e fase reale; caricamento interfaccia/archivio distinto, stato leggibile e Riprova in caso di errore, senza suggerire reset. Plotly in chunk locale differito e caricato quando un grafico raggiunge il viewport; nessun download Internet necessario. Non equivale a runtime Python istantaneo né a riduzione del peso complessivo dell’APK.
- **TD-104 — implementato, accessibilità completa da qualificare:** testata Android persistente con società/sezione e operatore/ruolo, contesto atleta/data nel dettaglio; focus sul titolo al cambio pagina, lingua documento IT/EN, controlli grafici con stato premuto leggibile e movimento ridotto nel common. Alternativa tabellare ai grafici con serie/unità, min/max/conteggio dei valori numerici, mancanti distinti da zero e 30 righe per pagina. Coordinate di serie diverse non vengono equiparate. Telefono, TalkBack, testo di sistema ingrandito e ulteriori configurazioni rimangono gate distinti dalle prove DOM/emulatore.

**Riutilizzo:** UI comune 0.2.6, ChartFrame e LoadingState; logica scientifica, scelta dei modi touch, caricamento Plotly, route e contenuti rimangono di Fuorigiri. Nessun aggiornamento automatico di Ammiraglia. Prove effettive in VERIFICA.md; guida suite aggiornata nello stesso intervento.

## TD-99–101 — ergonomia Android e pratiche suite, 20 ottobre 2026

- **TD-99 — implementato:** Indietro chiude prima menu/dialoghi con conferma delle modifiche; altrimenti torna tra sezione/profilo/elenco, con pagina, filtri e scroll conservati nella sessione. Solo la radice consente uscita. Cronologia limitata e azzerata al cambio archivio. Atleti/test Android in schede da 20 record, ricerca e filtri richiudibili, ritorno alla prima pagina dopo un filtro; niente tabelle orizzontali per questi due elenchi. Moduli principali (atleta/gruppo, misura, protocolli, manuale/incrementale/anaerobico/custom/revisione storica) con FormActions comuni; azioni originali e validazioni preservate, campi numerici non negativi con tastiera appropriata, tempi manuali con TimeInput, riferimenti/recupero facoltativi richiudibili. Riepilogo società e guida test richiudibili su Android. Tabelle desktop e viste analitiche restano distinte.
- **TD-100 — implementato:** all’avvio Android si ricorda l’ultima coppia archivio/società mediante preferenza locale persistente. Non memorizza dati sportivi o credenziali. Ogni apertura riconcilia l’ID con l’inventario; un archivio sparito porta alla selezione, senza aprire un’altra società. Test per morte sessione/preferenze malformate/risposte obsolete, prova di force-stop sull’emulatore.
- **TD-101 — documentato e adottato dove indicato:** guida canonica delle best practice Android in cycling-suite-common/docs/ANDROID_BEST_PRACTICES.md; fonte unica dei componenti RecordCards, CollapsibleFilters e FormActions nella UI comune 0.2.4. Consegna versionata locale a Fuorigiri, senza aggiornamento implicito delle altre app o pubblicazione. Adozioni/verifiche specifiche nel registro Fuorigiri; telefono, TalkBack e IME completo sono gate separati.

Criteri: elenco filtrato/pagina conservati tornando dal profilo; dettaglio test si chiude sull’elenco; bozza sporca protetta; selezione riaperta dopo arresto; nessun fallback su società diversa se rimossa. Le prove effettive e le limitazioni sono in VERIFICA.md.

## TD-98 — navigazione Android compatta, 20 ottobre 2026

**Richiesta:** Gestisci società, sezioni e lingua nel menu hamburger; informazioni del footer in una sezione Info.

**Implementato:** su Android testata con pulsante Apri menu e identità prodotto. Il menu raccoglie selezione società/Gestisci società, Atleti, Test e analisi, Protocolli, Società e gruppi, Storici e confronti, Archivio e scambio, Info e lingua. Info è raggiungibile anche senza società e contiene versione, stato locale/offline, logo/attribuzione fissi e licenza/limiti. Questi contenuti non sono ripetuti nel footer delle altre pagine Android. Navigazione desktop e componenti comuni conservati: menu di prodotto composto con Dialog e controlli della suite, nessuna copia dei suoi stili o nuova dipendenza dalla repository sorella.

**Accettazione verificata su emulatore API 35 x86_64:** apertura menu, Indietro chiude senza uscire dall’app, scelta Info chiude il menu, Gestisci società apre un solo dialogo, licenza raggiungibile, etichette IT/EN e lingua ripristinata. Screenshot reali nella galleria. Telefono e prove tattili/accessibilità complete rimangono distinti.

## Avanzamento Android — 20 ottobre 2026

**Ultimo esito:** corretto collegamento ABI3 delle wheel cryptography, APK installato e avviato su emulatore API 35 x86_64, test nativo import/cifratura/firma/API/Keystore passato. Corrette sovrapposizioni con barre Android e invalidazione cache wheel Gradle. TD-57 resta aperto per telefono ARM64, report/import/test completi, cloud e accettazione. Le note successive conservano gli stati precedenti.

**Aggiornamento:** trasferimento e hash delle sei wheel verificati localmente, dipendenze Chaquopy risolte per entrambe le ABI, APK debug prodotto su Windows. TD-57 ancora aperto: emulatore non rilevato all’ultimo controllo ADB, installazione/import nativi e flussi applicativi da collaudare. I paragrafi successivi descrivono il gate precedente.

Procedura ripetibile documentata in [ANDROID_WHEEL_FEDORA.md](ANDROID_WHEEL_FEDORA.md); versioni degli strumenti host non completamente registrate nel log, quindi nessuna garanzia di identità binaria.

TD-57 resta aperto: builder Fedora autorizzato per wheel Android, sei artefatti prodotti e digest ricevuti. Gate di packaging esteso a CFFI 2.0.0, oltre a pydantic-core/cryptography. Accettazione residua: trasferimento e hash locali, risoluzione dipendenze Chaquopy, APK, import nativi e collaudo prima su emulatore poi telefono. Il packaging applicativo Linux resta rinviato.

## Versionamento prodotto — 20 ottobre 2026

- **REL-VERSION-01 — implementato:** versione sorgenti 0.10.0 coerente fra backend/API, UI e lockfile, Android (`versionCode` 1000), installer Windows e AppStream Linux. `scripts/verify_versions.py` blocca build/release incoerenti; UI, header HTTP e nomi APK derivano dalle rispettive fonti correnti. Versioni di motori, renderer, protocolli e formati dati rimangono indipendenti. Nessuna pubblicazione o ricompilazione di installer implicita.

## Documentazione corrente — 19 ottobre 2026

- **DOC-01 — implementato:** indice delle guide, separazione dei documenti storici in `archivio/`, nomi delle guide indipendenti dalle release, README italiano con presentazione in inglese e link operativi; roadmap corrente distinta dai piani originali. Le analisi e i commenti originali restano conservati. [Indice](README.md), [roadmap](PROSSIMI_PASSI.md).

## Correzioni profilo e demo — 19 ottobre 2026

- **UI-PROFILE-01 — implementato:** dal dettaglio di ogni famiglia di test si può aprire direttamente il profilo dell’atleta associato, chiudendo il dettaglio; nessun permesso di modifica richiesto.
- **DEMO-MAT-01 — implementato:** corpus standard completo e ridotto includono quattro profili maturativi per società, casi maschile/femminile con indici avanzati, dati insufficienti e adulto. Snapshot e misure presenti nelle repliche e nei backup iniziali; manifest con risultati attesi. Rigenerazione conservativa esplicita, nessuna migrazione silenziosa delle demo esistenti.

**Attuazione TD-83–97, 19 ottobre 2026:** implementati nei sorgenti flussi test/glossario/riferimenti/tempi, avvisi licenza, stati cloud e crescita/maturazione con snapshot, export e report. Rimangono collaudo provider reale, revisione giuridica e validazione scientifica esterna; nessun nuovo installer. [Registro e accettazione](#osservazioni-manuali-acquisite--19-ottobre-2026), [specifica maturazione](MATURAZIONE.md), [verifiche](VERIFICA.md). Le sezioni datate conservano lo stato storico; non prevalgono su aggiornamenti successivi.

## Revisione e isolamento degli archivi — 19 ottobre 2026

- **REV-01 — implementato:** spazi/metadati protocolli, persistenza e concorrenza della selezione società, confronti con origine soglia assente, W/kg stimati esclusi dai delta, metriche dinamiche e selezione delle serie nel profilo.
- **SYNC-ISO-01 — implementato:** un archivio gestito per società, identità vincolata, canali/connessioni/inviti distinti. Vecchi archivi multi-società consultabili ma bloccati per sync e inviti; nessuna separazione automatica. La selezione UI non è un filtro di condivisione. Usare cartelle cloud con ACL distinte per collaboratori diversi.
- **SYNC-PERF-01 — implementato parziale:** sync ordinaria salta pacchetti già verificati; verifica completa esplicita. Restano duplicazione degli allegati/campioni per revisione e inventario completo del canale.
- **SYNC-V2-01 — implementato nei sorgenti:** blocchi cifrati riutilizzabili, campioni separati nell’involucro remoto, pagine leggere, ricevute/cursore locale e checkpoint di bootstrap; attivazione esplicita del fondatore con avviso firmato, lettura v1/v2 e storico conservato. Il database locale resta canonico; inventario remoto ancora completo e nessuna pulizia automatica. [Contratto e limiti](SYNC_V2_E_BACKUP.md).
- **BACKUP-SCALE-01 — implementato nei sorgenti:** ZIP64 schema 3 con snapshot SQLite, inventario JSONL, hash e file elaborati su disco; upload/anteprima/ripristino progressivi, pubblicazione atomica e lettura dei backup precedenti. Prova effettiva oltre 100 MB; limiti superiori non qualificati in produzione. Salvataggio diretto desktop evita il buffering del download nel browser.
- **SYNC-MIG-01 — implementato nei sorgenti:** anteprima e impronta, estrazione per società con dipendenze e tutte le revisioni, conflitti e file propri, nuova autorità/canale/inviti e originale intatto. Riferimenti incoerenti o non attribuibili bloccano la procedura; editor di riconciliazione dei casi ambigui non implementato.
- **QA-RELEASE-01 — da completare:** flusso GUI automatizzato completo, FIT reali anonimizzati, account cloud distinti, interruzioni/revoche/conflitti; candidato Windows su VM pulita. Fedora resta rinviato; Android dispone di build locali e precedenti prove emulatore, con firma release e collaudo fisico ancora distinti. Traduzione e accessibilità da completare.

Dettagli: [revisione generale](archivio/REVISIONE_GENERALE_2026-10-19.md), [dimensioni e strategia sync](SYNC_DIMENSIONI_E_SCALABILITA.md). Le stime derivano da registrazioni sintetiche misurate, non da un archivio reale pluriennale.

## Suite comune — prima estrazione, 18 ottobre 2026

- **TD-79 / SUITE-02 — implementato:** repository autonoma `cycling-suite-common`, ramo main, tag UI 0.1.0, GPL-3.0-or-later. Le app conservano repository/build/versioni proprie; nessuna pubblicazione GitHub/npm eseguita.
- **TD-80 / UI-26 — implementato iniziale:** pacchetto React tema/Field/DataTable/SortableTable/branding fisso, catalogo e test; Fuorigiri lo utilizza tramite artefatto versionato, con sorgenti/licenza/logo e provenienza verificati. Sidebar, shell e modali ancora da estrarre.
- **TD-81 / SUITE-03 — da sviluppare:** integrazione e collaudo in Ammiraglia, catalogo completo e verifiche tastiera/focus/mobile; versioni comuni aggiornate esplicitamente dalle singole app.
- **TD-82 / SUITE-04 — da progettare/estrarre:** client, contratti dati, servizi Python condivisi e interoperabilità degli archivi. Nessun SQLite/credenziale condiviso automaticamente; motori dei test e pianificazione distinti. [Guida](SUITE_CONDIVISA.md).

## 0.8 / architettura 1.6 - richiesta corpus e flussi di creazione

- **TD-74 / UI-25:** creazione e versionamento di tutte le famiglie in Protocolli; incrementali manuali senza ERG o solo catalogo, Sprint/Wingate e custom. Filtri nome/famiglia/stato. Nuovo test sceglie protocollo/versione e modalità manuale/FIT/CSV; rimossa la creazione dei protocolli da Test e analisi.
- **TD-75 / DATA-04:** campi opzionali definiti dall’utente, tipizzati, con unità/limiti/scelte e scheda protocollo oppure prova. Aggiunta di campi alla sola esecuzione, senza mutazione del protocollo; snapshot, revisioni e validazione backend. Null/zero/false distinti. Nessuna formula arbitraria, nessuna equivalenza fisiologica implicita.
- **TD-76 / ANA-04:** importatore FIT comune con scelta sessione e gestione esplicita duplicati; inizio su grafico, zoom sullo sforzo, riepilogo protocollo e esclusioni motivate. Nuova versione parte dal metodo precedente in Protocolli. Revisione conserva atleta/protocollo e può correggere un record riferito ad archivio storico.
- **TD-77 / REPORT-05:** campi custom nei PDF/Markdown del singolo e dell’archivio, CSV esteso long-form tipizzato e backup; metriche numeriche custom in grafici/medie/mediane, separate per protocollo e identità del campo.
- **TD-78 / QA-04:** corpus sintetico completo su due società, 24 profili, tre stagioni, 192 record test, gruppi/anni, antropometria, FIT/CSV, gas/lattato/recupero, zone a 7, metodi distinti, revisioni e dati mancanti. Fixture errate separate, oracoli numerici indipendenti, repliche Admin/Viewer, revoca, backup/recupero SOLO DEMO e conflitto offline da esercitare. [Matrice dei casi](DATI_SINTETICI.md).

Non inclusi: codice/formule caricate dall’utente, import generico di schemi da CSV long-form, certificazione scientifica dei metodi custom, provider reali o nuova build Android/Linux. Per ripristino fedele dei protocolli custom usare il backup. La qualifica scientifica e la verifica dei dispositivi rimangono distinte dai test del software.

## 0.7 / architettura 1.5 - implementazione richiesta il 18 ottobre 2026

- **TD-68 / CLOUD-04:** implementati i tre adapter API Drive/Dropbox/OneDrive oltre a WebDAV, UI avanzata con destinazione, registrazione OAuth, stato/collegamento/scollegamento, token OS e callback desktop. Shared backend e sorgenti native Android: PKCE per Dropbox/OneDrive, autorizzazione Google Play services per Drive, rinnovo e background sui trasporti diretti. Test simulati presenti; APK e collaudo Android non eseguiti. Restano registrazioni OAuth della distribuzione, consenso/verifica provider e test reali con due account. [Guida e contratto](CONFIGURARE_LA_SINCRONIZZAZIONE.md).
- **TD-69 / SYNC-02:** predisposizione servizio dedicato implementata come adapter/client HTTPS v1, selezionabile nella UI. Server, hosting, account del relay, amministrazione e deployment rimangono successivi; nessun obbligo di backend Fuorigiri per usare i quattro provider.
- **TD-70 / ANA-01:** Sprint breve (default 6 s), Wingate 30 s, Wingate 15 s implementati in protocolli versionati e flussi manuale/tracciato. Carico, dispositivo, partenza, posizione, riscaldamento e finestre espliciti. Nessuna equivalenza universale fra famiglie, finestre, strumenti o risultati dichiarati/calcolati.
- **TD-71 / ANA-02:** import test_anaerobico con schema storico, preview/commit atomico e annullamento lotto; ANA-15-070 confermato dall’utente come 15 s e 0,70 N·m/kg. Dati mancanti e peso derivato conservati; lavoro/media incoerenti segnalati. Formula indice W/s, dispositivo/partenza/finestre storici non verificati. Nessun CSV privato distribuito.
- **TD-72 / ANA-03:** integrali temporali, picco con finestra, migliori 1/5 s, media completa, lavoro osservato, potenza finale, calo percentuale e pendenza separati, FC/cadenza, W/kg e qualità. Snapshot di metodo e chiave comparabilità conservativa. Revisione delle prove nuove con motivo e controllo concorrenza.
- **TD-73 / UI-24 / REPORT-04:** sezione anaerobici, grafico del singolo test, metriche negli storici e nel profilo atleta, aggregazioni/medie/mediane separate, CSV base/esteso, PDF/Markdown e report società/gruppo/anno/atleta con sezioni proprie. Tre FIT sintetici e documentazione di prova inclusi. [Metodi e limiti](TEST_ANAEROBICI.md).

I precedenti step di validazione/distribuzione 1-6 non vengono considerati completati da queste funzionalità. Restano da affrontare quando l’utente dispone di ambienti e corpus: collaudo scientifico esterno, provider reali, PC pulito, Fedora e Android. Per l’anaerobico: verificare le formule/dispositivo dello storico, corpus reale e ripetibilità; acquisizione/controllo ergometro e modelli fra protocolli restano sviluppi ulteriori, senza inferenze automatiche.

## Chiarimento cloud Android — 18 ottobre 2026

**TD-67 / CLOUD-03:** Android deve supportare sincronizzazione diretta tramite **WebDAV, Google Drive, Dropbox e OneDrive**. OneDrive passa da candidato a requisito del prodotto; Drive/Dropbox restano requisiti da implementare. La sincronizzazione cartella dei client desktop non soddisfa da sola il requisito Android. Stato reale 0.6: cartella/WebDAV nel codice, nessun adapter API Drive/Dropbox/OneDrive; nessun APK collaudato. Le build Linux/Android rimangono rimandate come richiesto, non riattivate da questo chiarimento.

Mantenere un solo protocollo di scambio/revisioni/conflitti, con adapter distinti per provider e autenticazione nativa. Ogni società sceglie una destinazione condivisa; non promettere replica simultanea fra provider diversi. Accettazione per ciascun provider: due account distinti sulla stessa società, due dispositivi, permessi effettivi, rinnovo/revoca token, coda offline, allegati, duplicati e conflitti. Un test con un solo account non dimostra collaborazione fra operatori.

Per una prima sincronizzazione desktop/mobile contenendo il lavoro di integrazione, privilegiare il collaudo WebDAV già presente con un servizio Nextcloud gestito; un server remoto è compatibile con il lavoro locale offline. Un futuro servizio di sincronizzazione dedicato è un’alternativa architetturale da valutare, non una sostituzione già approvata dell’archivio locale o delle integrazioni richieste.

## Software 0.6 / architettura 1.4 — sincronizzazione, distribuzione e avvio Android

Consegna concordata: Windows e sorgenti; build Linux/Android rimandate dall’utente il 18 ottobre 2026. Nessuna pipeline remota avviata o release pubblicata.

- **TD-63 / SYNC-01 / UI-22:** trasporti cartella/WebDAV comuni, credenziali OS senza fallback in chiaro, retry per oggetto, pubblicazione condizionale/rilettura, controlli firmati immutabili, registro operativo e gestione esplicita degli errori. Implementato; regressioni/server WebDAV locale verificati. Collaudo Nextcloud reale e tre piattaforme ancora aperto.
- **TD-64 / SYNC-02:** rotazione della chiave del canale con journal e avviso firmato, inviti rinnovati e recupero accessi aggiornato. Implementato e testata l’interruzione; upgrade di tutti i client alla 0.6 richiesto. Non cancella dati già ricevuti né recupera automaticamente modifiche non inviate da autori revocati.
- **TD-65 / DIST-01/02:** utente finale senza Python/Node/Qt da installare: installer Windows per utente con bundle completo; Flatpak con runtime per Fedora e distribuzione offline con runtime separatamente inclusi. Installer e pipeline sorgente aggiunti; prove su OS puliti, build Fedora, firma prodotto e completamento degli avvisi di licenza prima del rilascio.
- **TD-66 / UI-23:** icona minimale Fuorigiri in SVG/PNG/ICO e vettore Android, usata da installer/eseguibile/finestra/launcher/testata/favicon. Il logo originale della società e l’attribuzione fissa restano invariati nei footer.
- **TD-57 / AND-01–05:** dopo il consolidamento desktop, avviata shell Android e bridge al medesimo backend; SAF/Keystore/WorkManager/layout touch nel sorgente. Contratto testato su Windows, non dispositivo. Gate aperto su wheel native aggiornate, builder Linux/macOS, SDK/JDK/Gradle, APK e collaudo fisico. Non chiudere il requisito con il solo sorgente o con i test ASGI su PC.

Dettagli e limiti: [consolidamento 0.6](DISTRIBUZIONE.md), [Android attuale](ANDROID.md). Nessuna modifica alle formule scientifiche o agli storici in questa fase. Dopo accettazione Android restano nell’ordine Sprint breve → Wingate 30 s → Wingate 15 s. Drive/Dropbox API, compattazione dei canali grandi, rotazione dell’autorità (distinta dalla chiave del canale), audit esterno e collaudo delle librerie native rimangono requisiti aperti.

## Software 0.5 / architettura 1.3 — incrementale e report gerarchici

Autorizzati gli step 1–4 della lista operativa nel messaggio: preset/migrazioni, motore, GUI/FIT/report e metodi specialistici, scegliendo i metodi con riferimento scientifico quando l’utente non ne dispone. [Implementazione, formule, fonti e limiti](archivio/IMPLEMENTAZIONE_INCREMENTALE_05.md).

| ID | Requisito | Stato |
|---|---|---|
| TD-60 / SCI-01 | Scegliere metodi incrementali basati su fonti scientifiche, senza attendere formule proprie dell’utente e senza inventare un consenso unico. | **Implementato**: step costanti, finestre versionate, rampe/discontinui descrittivi, lattato lineare/Dmax/Dmax modificato, VO2peak, grafici gas e marker ventilatori, ripetibilità. Stime esplorative/valori dichiarati distinti; validazione fisiologica esterna non dichiarata. |
| TD-61 / UI-20 | Report completo di società ispirato all’allegato, con aggregazioni e grafici; gruppo, gruppo per anno/stagione e atleta con storico come viste dello stesso modello. | **Implementato**: PDF/MD, copertura, aggregazioni, schede e misure, fonti, viste equivalenti e avvertenze accorpate, logo/credito fissi. Nessuna importazione dei dati personali allegati. Motori anaerobici restano nella fase prevista. |
| TD-62 / UI-21 | Rendere operativi i preset e le correzioni riproducibili nell’interfaccia e nei report. | **Implementato**: schema 3 con copia pre-migrazione, preset immutabili, metadati/hash, nessun ricalcolo legacy, selezione sessione FIT, correzione duplicati con motivo, marker/esclusioni, condizioni, import gas e report specialistici. |

Stato INC aggiornato: INC-02/03/06/07 attuati nella versione locale; INC-01 ha nuove funzioni di import ma richiede ancora corpus reale degli esportatori. INC-04 ha un metodo descrittivo esplicito, non conversione fisiologica automatica. INC-05/08/09 hanno algoritmi e UI/report, con i limiti scientifici e di validazione documentati; gas in CSV canonico e suggerimenti ventilatori da revisione esperta, non una certificazione del laboratorio. INC-10 mantiene originali/provenienza e confronti separati, ma la riconciliazione di ogni archivio reale richiede collaudo. INC-11, WebDAV e Android non sono chiusi da questa iterazione.

Le sezioni precedenti sotto conservano la cronologia e sono superate dove descrivono funzioni ora sviluppate. [Guida di prova](TESTARE_IL_PROGETTO.md).

## Architettura 1.2 — WebDAV confermato e passi successivi

**TD-59 / CLOUD-02:** supportare **WebDAV su Windows, Fedora e Android**, con la stessa semantica di pacchetti cifrati/firmati, uso offline, ruoli e conflitti. **Requisito confermato, non implementato.** Comprende configurazione URL/cartella, credenziali protette, verifica accessi, ripresa e diagnostica, migrazione dal trasporto cartella e collaudo multipiattaforma. Nextcloud proposto come primo server di riferimento, senza promettere compatibilità con qualsiasi server WebDAV. AND-04 e INC-11 includono questa accettazione.

Ordine tecnico raccomandato: interfaccia di trasporto comune → WebDAV desktop → collaudo/porting Android nella fase mobile; lo spike Drive può procedere indipendentemente. Supporto WebDAV non subordinato a OAuth o alla scelta di Google/Dropbox. [Piano operativo aggiornato](PROSSIMI_PASSI.md). Software invariato 0.4.1.

## Aggiornamento architettura 1.1 — accesso diretto alle API cloud

**TD-58 / CLOUD-01 — Verificare e progettare lo scambio tramite API ufficiali**, senza dipendenza dal client cartella su Android o dal server Fuorigiri. Ricerca completata in [SINCRONIZZAZIONE_CLOUD_API.md](archivio/SINCRONIZZAZIONE_CLOUD_API.md): Drive e Dropbox fattibili come trasporto, con permessi differenti. Proposta: spike Drive con `drive.file` e due account, adapter comune, gestione OAuth/portachiavi, poi Dropbox condiviso; OneDrive candidato; WebDAV ora confermato per desktop e Android in TD-59. **Ricerca/disegno completati; integrazioni e prove autenticate non implementate.**

Il lavoro entra in INC-11/TD-50 e AND-04, con prima verifica sul desktop prima della fase Android. UI-19 esplicita account, cartella, consenso e stato; il ruolo della società resta distinto dall’account cloud. Migrazione dal trasporto cartella da collaudare, soprattutto per file aggiunti esternamente e accesso Drive per-app. Software invariato 0.4.1.

## Aggiornamento 0.4.1 / architettura 1.0 — metodi e Android

Step 2 eseguito come **definizione**, non come implementazione dei nuovi motori: [METODI_INCREMENTALE.md](METODI_INCREMENTALE.md). Confermati durata/copertura ≥95% separati dall’aderenza e assenza di un coefficiente universale di soglia/FTHR. Finestre attuali esplicitate come convenzioni; scostamenti numerici del codice e decisioni specialistiche residue documentati. INC-01–10 restano da implementare e collaudare, INC-11 parziale.

| ID | Requisito / decisione | Stato e accettazione |
|---|---|---|
| TD-55 | Definire precisamente metodi incrementali, fonti, finestre, qualità, preset/versioni e casi limite. | **Specifica 1.0 redatta**; convenzioni costanti confermate. Varianti lattato/gas/rampa da validare prima del relativo motore. Successiva attuazione in INC-01–10; nessun ricalcolo storico automatico. |
| TD-56 | Uniformare il nome Fuorigiri in sorgenti, documenti, package, comandi, header, ambiente e distribuzione. | **Implementato**: `Fuorigiri.exe`, `dist/Fuorigiri/`, `FUORIGIRI_*`, `X-Fuorigiri-*`. Riconoscimento conservativo dei percorsi/canali preesistenti con test. |
| TD-57 | Sviluppare l’app **Android** offline first per telefoni/tablet, con società, test, storici, report e scambio interoperabile. | **Richiesto, non implementato**. AND-01–05 e UI-18 in [ANDROID.md](ANDROID.md); stack Capacitor + Python incorporato proposto, subordinato allo spike. |

Ordine aggiornato: **(1)** completare e consolidare l’incrementale desktop, predisponendo i contratti portabili; **(2)** fattibilità e sviluppo Android con collaudo offline e scambio desktop/mobile; **(3)** Sprint breve / potenza neuromuscolare, Wingate 30 s, Wingate 15 s. La fattibilità Android può iniziare durante il consolidamento; non si anticipano i nuovi motori prima della copertura incrementale. I candidati ulteriori restano distinti.

## Stato corrente 0.4 — società, ripristino e accessi

17 ottobre 2026. Implementata la prima iterazione TD-45–49: percorsi separati, anteprima/ripristino ZIP, recupero cifrato del fondatore, copia indipendente e di consultazione, prima sincronizzazione da invito anche senza dati, ruoli visibili e rinnovo con nuovo invito. Guida operativa e limiti in [SOCIETA_BACKUP_E_ACCESSI.md](SOCIETA_BACKUP_E_ACCESSI.md). TD-50 rimane parziale per audit completo/rotazione/portachiavi; INC-11 non è completato nel suo insieme. Validazione locale: 45 test, TypeScript/Vite, GUI con dati sintetici; nessun collaudo cloud remoto o Fedora dichiarato.

## Pianificazione confermata e stato aggiornato dei requisiti

Aggiornamento documentale del 17 ottobre 2026, successivo alla preview 0.3. La pianificazione iniziale era documentale; la preview 0.4 implementa ora TD-45–49 e parte di TD-50. Le altre voci rimangono acquisite e da implementare, secondo gli stati della tabella. I dettagli della copertura sono in [COPERTURA_TEST_E_ROADMAP.md](archivio/COPERTURA_TEST_E_ROADMAP.md).

Ordine confermato: completare il prodotto per i test incrementali, includendo **tutte** le lacune INC-01–11, quindi affrontare sprint breve/potenza neuromuscolare, Wingate 30 s e Wingate 15 s. Le priorità P0/P1/P2 ordinano il lavoro interno alla prima fase: non rendono facoltative le voci meno urgenti. Il supporto agli scambi gassosi durante un incrementale rientra in questa fase; gli altri test di laboratorio autonomi restano distinti.

| ID | Requisito e criterio di completamento | Stato |
|---|---|---|
| TD-45 | Separare in Gestisci società le azioni **Crea nuova società**, **Collega tramite invito** e **Ripristina da backup**, spiegando file richiesto, risultato e passaggio successivo. La password dell'invito non deve sembrare necessaria per creare una società. | **Implementato 0.4**: tre percorsi separati, spiegazioni e selezione automatica dopo l’operazione. |
| TD-46 | Ripristinare un backup dati ZIP in un archivio locale, con anteprima società/contenuto, verifica formato/versione/integrità, gestione ID già presenti, destinazione isolata e registrazione nel selettore Società. Nessuna sovrascrittura silenziosa; errore o annullamento non devono lasciare un archivio parziale. | **Implementato 0.4**: anteprima, manifest/checksum, SQLite ricostruito in cartella temporanea, copie di consultazione/indipendenti e recupero originale. ID già presenti e cartelle occupate rifiutati; rollback verificato. |
| TD-47 | Distinguere **recupero dei dati** da **recupero degli accessi e del fondatore**. Un backup dati non concede privilegi di amministrazione. Prevedere un percorso protetto per salvare/ripristinare l'identità e le credenziali necessarie, con spiegazione dei limiti se mancano. Documentare il passaggio a un nuovo PC e il recupero dopo perdita del dispositivo. | **Implementato 0.4**: JSON di recupero del fondatore cifrato con password, distinto dallo ZIP dati; firme verificate prima del recupero. Senza credenziali: consultazione o copia indipendente, nessun privilegio originale. Portachiavi e trasferimento esclusivo dell’autorità restano INC-11. |
| TD-48 | Completare la prima associazione di una società: dopo l'invito mostrare la società anche se ancora senza dati, il proprio ruolo, la configurazione della cartella condivisa e l'azione **Acquisisci dati / Prima sincronizzazione**. Gestire cartella offline, vuota o non valida e operazione ripetuta senza duplicati. | **Corretto 0.4**: onboarding della società collegata ma vuota, azione di prima sincronizzazione accessibile anche al visualizzatore, errori e ultimo scambio visibili; GUI e API collaudate su archivi isolati. |
| TD-49 | Rendere chiari e gestibili **Fondatore**, **Admin dati**, **Visualizzatore** e dispositivo associato. Mostrare ruolo corrente, operatori/dispositivi, stato degli inviti e azioni consentite; distinguere identità locale da login e password d'invito. Definire un flusso tracciato di rinnovo/cambio ruolo senza modifiche manuali ai file. Verificare permessi in GUI, API e dati sincronizzati. | **Implementato 0.4 per identità operatore/dispositivo**: badge corrente, elenco pubblico firmato, spiegazione dei ruoli e rinnovo/cambio ruolo tramite sostituzione e applicazione dell’invito sulla stessa copia locale. Accettazione remota non dedotta. Non è richiesto implicitamente un servizio di account online. |
| TD-50 | Esplicitare effetto e limiti della revoca offline: ultimo scambio, propagazione ai dispositivi, operazioni rifiutate e dati già scaricati. Integrare audit, rinnovo/rotazione credenziali e percorso di recupero coerenti con INC-11. | **Parziale 0.4**: revoca propagata, ultimo scambio e limiti visibili; preservati solo gli eventi già acquisiti e fissati per hash alla revoca. Rinnovo e recupero presenti. Audit storico completo, rotazione del canale e portachiavi ancora INC-11; nessuna cancellazione delle copie già ricevute. |
| TD-51 | Implementare e verificare **tutte le lacune INC-01–11** della copertura incrementale: file reali, qualità/aderenza, selezione temporale, rampe/discontinui, lattato, contesto, finestre FC, gas, ripetibilità, riconciliazione storica e consolidamento operativo/distributivo. | **Da implementare e validare**; elenco completo e criteri per ciascuna voce nella roadmap. Non basta documentare le formule o aggiungere campi. |
| TD-52 | Dopo il completamento della fase incrementale, sviluppare e collaudare **Sprint breve / potenza neuromuscolare**, con protocollo e metodo versionati, dati/qualità, metriche di potenza breve, report e storici dedicati. | **Pianificato, non implementato**. Durata e modalità esecutive da specificare prima del motore; 6 s è un esempio, non un default già approvato. |
| TD-53 | Nella fase successiva sviluppare e collaudare **Wingate 30 s**, con carico/dispositivo, delimitazione dello sforzo, metriche/metodo dichiarati, import manuale o con tracciato, report e confronti coerenti. | **Pianificato, non implementato**. Sprint ripetuti restano un'estensione distinta, non automaticamente inclusa. |
| TD-54 | Nella stessa fase sviluppare e collaudare **Wingate 15 s**, come protocollo distinto già usato in passato dalla società, con ricostruzione documentata del metodo storico e possibilità di archiviare risultati incompleti senza inventare i campioni. | **Pianificato, non implementato**. Acquisire durata effettiva, carico, modalità di partenza, dispositivo, formule e formato dei referti storici. Non estrapolare 15 s in 30 s e non aggregare automaticamente i due protocolli. |

La scelta dei tre test successivi è confermata dall'utente; i dettagli dei metodi non lo sono ancora. La fase successiva è uno sviluppo con collaudo e validazione, non una promessa di equivalenza con protocolli o valori normativi esterni. Gli altri candidati della roadmap restano fuori dal perimetro confermato per quella fase.

## Stato precedente 0.3 — Fuorigiri Performance Lab

Nuovi requisiti **TD-30–44** implementati/documentati nel [registro della revisione 0.3](archivio/REVISIONE_FUORIGIRI_03.md), con scelte **UI-11–16**, contratto CSV e criteri di accettazione. La collocazione della gestione società è presente, ma il percorso completo di collegamento/ripristino non lo è: TD-45–50 precisano il lavoro residuo. [Copertura e mancanze del motore](archivio/COPERTURA_TEST_E_ROADMAP.md) distingue la fase incrementale obbligatoria dai test successivi. Le sezioni 0.2 sottostanti restano storico del progetto; il nome prodotto è ora confermato.

## Stato del codice 0.2 — 17 ottobre 2026

Aggiornamento successivo all'implementazione e alla ripresa del lavoro. La tabella descrive ora il codice 0.2; le note di disegno 0.5 sottostanti restano contesto storico. [Guida di prova con GUI](TESTARE_IL_PROGETTO.md) e [verifiche](VERIFICA.md) distinguono test eseguiti e collaudi ancora necessari.

**Branding fisso:** logo incluso nel bundle e testo «Sviluppato da Luca Bontempi per Progetto Ciclismo - Rodengo Saiano A.S.D.». Nessuna personalizzazione di logo/credito per società o workspace. ZONE-01 implementato a lista dinamica, con prove a 3/5/7 zone. ANA-01 resta un'estensione candidata, non sviluppata.

## Decisioni della revisione documentale 0.5 (storico)

17 ottobre 2026, architettura **0.5**. Convenzioni funzionali accettate; dettaglio e criteri in [Storico, zone e branding](archivio/STORICO_ZONE_E_BRANDING.md). Queste note descrivevano il disegno prima dello sviluppo; lo stato corrente è nella tabella aggiornata:

- **TD-02/03:** logo di riferimento fornito; colori del file identificati. Resta da implementare il tema e verificarne la leggibilità.
- **TD-04/13/16/17:** definite nove viste HIST-01–09 dal PDF, includendo anno di categoria distinto da stagione e coorte; default per atleta accettato e modalità tutti i test per continuità con l'archivio.
- **TD-18:** riferimento storico acquisito; consente progressione prestativa e peso, ma non crescita in statura (misure assenti) o modelli di maturazione.
- **TD-19/20 e SUITE-01:** accettati isolamento per società, admin/visualizzatore e separazione DB delle app con librerie comuni.
- **TD-28:** percentuali e confini del preset FTHR/Watt Soglia confermati. Nuovo requisito **ZONE-01**: numero N di zone configurabile, anche oltre cinque, distinto per FC e potenza; editor, grafici, report ed export dinamici. Da sviluppare, con verifiche sui confini e schemi a 3/5/7 zone.
- **Estensione candidata ANA-01:** import/consultazione dei risultati anaerobici dello storico; non ancora assunta come implementazione del motore anaerobico.

Ancora aperti: formule dei riferimenti di soglia/FTP, criteri di completamento step, finestre FC, fonti dei valori medi, nome suite e resa finale del tema. Il PDF non viene importato automaticamente e non è copiato nei dati pubblici.

Revisione del 17 ottobre 2026. I 29 identificatori seguono l'ordine dei [commenti originali](archivio/COMMENTI_ORIGINALI_2026-10-17.md). Questo documento distingue **integrazione nel progetto** da **implementazione nel programma**. La revisione 0.2 include modifiche al codice; i commenti originali rimangono conservati per tracciabilità.

Stati: **presente** = funzionalità riscontrata nel codice; **parziale** = solo una parte disponibile; **da sviluppare** = requisito acquisito, non implementato; **da definire** = scelta o riferimento necessario. Il riscontro è sul codice della preview locale, non una certificazione su Windows/Fedora puliti. Riferimento principale: [architettura 0.6](../ARCHITETTURA_PROPOSTA.md).

| ID | Requisito riscritto e criterio di completamento | Stato e riscontro attuale | Disegno |
|---|---|---|---|
| TD-01 | Segnalare esplicitamente ciò che è già implementato, separando le parti di una richiesta composta. | **Presente**: stato puntuale aggiornato qui; dettagli di prova in VERIFICA.md. | §14 |
| TD-02 | Adottare i colori di Progetto Ciclismo con superfici neutre e accenti poco invasivi; mantenere leggibilità e contrasto. | **Presente**: tema neutro/blu con accento giallo; verificato visivamente. Accessibilità sistematica da consolidare. | §5.1, UI-02 |
| TD-03 | Inserire discretamente in basso logo e collegamento della società, nome Luca Bontempi e collegamento personale. | **Presente**: logo locale, link e attribuzione fissa in GUI/PDF/Markdown; non personalizzabili. | §5.1, UI-03 |
| TD-04 | Calcolare aggregati storici per gruppo, anno e gruppo/anno, indicando popolazione, filtri e dati mancanti. | **Presente**: history.py, filtri e aggregati per stagione/categoria/coorte/anno di categoria, conteggi e mancanti per metrica. | §6.1, §8.2 |
| TD-05 | Nella scheda atleta selezionare MAP o FTP, W o W/kg; aggiungere grafici di peso e statura. | **Presente**: selettori MAP/soglia/FTP, W/Wkg e grafici peso/statura. FTP assente non stimata implicitamente. | §5.1, §8.1 |
| TD-06 | Rendere disponibili italiano e inglese in interfaccia, grafici e report. | **Parziale**: selettore IT/EN, catalogo UI e titoli principali report; diagnostiche, alcuni controlli Plotly e testi secondari ancora da completare. | §5.1, UI-05 |
| TD-07 | Importare anagrafiche, test storici e antropometria da CSV con anteprima, riconciliazione ed errori per riga. | **Presente per i tre profili concordati**: anteprima, ID esterni, errori per riga e commit atomico. Mappatura interattiva arbitraria di colonne ancora assente. | §7 |
| TD-08 | Nell'import ERG riconoscere step/rampe, indicare il riscaldamento e salvare codice protocollo distinto dal nome. | **Presente**: import ERG e editor manuale con fasi, codice e nome distinti. | §7 |
| TD-09 | Archiviare atleti inattivi mantenendoli negli storici; eliminarli escludendoli dai nuovi calcoli storici. | **Presente**: active/archived/deleted, filtri e ripristino; eliminato escluso dai nuovi aggregati. | §6.1 |
| TD-10 | Archiviare o eliminare protocolli senza perdere i riferimenti dei test esistenti. | **Presente**: stati reversibili; le definizioni usate dai test restano conservate. | §6.1 |
| TD-11 | Creare e modificare protocolli dall'interfaccia, esportare ERG e pubblicare nuove versioni con differenze e motivazione. | **Presente**: editor tabellare, nuove versioni con genitore/motivo, export ERG e definizione JSON. Confronto grafico delle differenze ancora da sviluppare. | §7 |
| TD-12 | Ordinare le tabelle per ogni colonna di dati, con indicatore del verso e comportamento coerente per valori mancanti. | **Presente**: SortableTable e DataTable con ordinamento interattivo tipizzato e indicatori; colonne di azioni escluse. | §5.1, UI-06 |
| TD-13 | Mostrare un gruppo stabile, per esempio Allievi, con sottogruppi per anno/stagione. | **Presente**: categoria padre, stagioni figlie e visualizzazione gerarchica; anno di categoria nelle appartenenze. | §6.1 |
| TD-14 | Modificare il profilo atleta dalla UI e inserire manualmente rilevazioni antropometriche datate. | **Presente**: modifica profilo dalla UI e inserimento antropometrico datato. | §5, §6 |
| TD-15 | Nell'import FIT o CSV raccogliere lattato, coefficienti, FC, antropometria e altri dati mancanti; proporre le ultime rilevazioni e consentire correzioni successive. | **Presente**: FIT/CSV, osservazioni manuali, proposta storica/stimata e revisione. Nessuna formula lattato→soglia non concordata. | §7, §8.1 |
| TD-16 | Esportare MD/PDF dello storico atleta, categoria e categoria/anno, con grafici, filtri e criteri statistici. | **Presente**: MD/PDF degli aggregati e dell’atleta filtrato; manifest con revisioni sorgente e artefatti conservati. | §9.1 |
| TD-17 | Confrontare gruppi su una stagione o sullo storico con criteri espliciti di confrontabilità. | **Presente**: viste per gruppi/stagioni, popolazioni esplicite e confronto appaiato per stesso protocollo/fonte. | §8.2 |
| TD-18 | Calcolare statistiche di crescita antropometrica e progressione prestativa, distinguendole. | **Presente per statistiche descrittive**: delta peso/statura, giorni e annualizzazione; delta prestativi. Maturazione/PHV e benchmark richiedono specifiche ulteriori. | §8.2 |
| TD-19 | Configurare percorsi locali e cartelle di scambio distinti per società, condivisibili con collaboratori diversi. | **Presente nei nuovi workspace**: percorsi, DB, originali e canali separati. Archivio precedente mantenuto, migrazione automatica non implementata. | §10.1 |
| TD-20 | Gestire operatori admin e visualizzatori per società, applicando i permessi anche alle API e ai dati ricevuti. | **Presente in forma operatore/dispositivo**: inviti cifrati, admin/visualizzatore, firme e controlli API/sync. Fondatore gestisce inviti/revoche; portachiavi e recupero guidato ancora assenti. | §10.3 |
| TD-21 | Registrare FC a 60, 90 e 120 secondi e a tempi personalizzati, specificando l'evento da cui decorrono. | **Presente**: automatico 60/90/120 s e osservazioni manuali personalizzate, con fonte distinta dal sensore; riposo pre-test separato. | §8.1 |
| TD-22 | Inserire RPE da 1 a 10, associata al test e alla scala dichiarata. | **Presente**: RPE intera 1–10, scala conservata negli input. | §8.1 |
| TD-23 | In assenza di storico proporre valori medi configurati per i dati manuali, con fonte e conferma esplicita. | **Presente come configurazione facoltativa**: preset con fonte/popolazione, proposto su scelta esplicita e marcato stimato. Nessun valore numerico universale precompilato. | §8.1 |
| TD-24 | Richiedere data di nascita facoltativa; continuare ad accettare anno soltanto o dato assente. | **Presente**: data facoltativa, solo anno o assenza; verifica coerenza data/anno. | §6.1 |
| TD-25 | Scegliere un nome legato alla cultura ciclistica italiana, mantenendo Performance Lab e prevedendo nomi coordinati per la suite. | **Confermato: Fuorigiri Performance Lab**, rinomina tecnica completata nella 0.4.1. | §15 |
| TD-26 | Usare il testo «Strumenti aperti a supporto del ciclismo giovanile» nella parte bassa dell'app. | **Presente**: motto nel footer accanto all’attribuzione fissa richiesta. | §5.1, UI-03 |
| TD-27 | Confrontare prodotti open source e commerciali e ricavarne funzionalità candidate. | **Completato come prima ricognizione**: CONFRONTO_PRODOTTI.md; nessuna estensione automatica del perimetro. | §12 |
| TD-28 | Configurare zone FC e potenza in percentuale di riferimenti selezionati e riportarle nei report. | **Presente**: preset confermato, schemi N zone per canale, riferimenti espliciti, tempi in zona e report/export dinamici; metodi dei riferimenti restano espliciti. | §8.1, §9 |
| TD-29 | Correggere input manuali e fine sforzo dopo aver visto il grafico, ricalcolando in una nuova revisione. | **Presente**: revisione da UI, ricalcolo dopo fine sforzo, motivo e protezione da aggiornamenti persi; correzione dei risultati storici tramite flusso dedicato. | §8.1 |
| SUITE-01 | Registrare decisioni UI e condividere componenti con una futura app di gestione allenamenti della stessa suite. | **Parziale**: moduli UI condivisibili, branding fisso e servizi separati; estrazione in pacchetti indipendenti e seconda app future. | §5.1, §15 |

## Ordine proposto di sviluppo (storico, prima della pianificazione TD-45–54)

1. Modello dati e migrazioni: nascita, categorie/stagioni, stati di archivio, revisioni test, osservazioni e provenienza.
2. Flussi locali: modifica atleta/test, import CSV, editor protocolli, campi manuali e configurazione dei metodi.
3. Componenti UI condivisi, branding, traduzioni e tabelle ordinabili; preparazione parallela alle schermate locali, senza duplicarne la logica.
4. Storici, aggregati, crescita descrittiva, zone e report multipli dopo validazione delle definizioni.
5. Workspace isolati, identità e autorizzazioni, sincronizzazione con conflitti e revoca; prove fra PC e account diversi.
6. Distribuzione verificata Windows/Fedora; seconda app pianificata separatamente sul nucleo condiviso.

## Riferimenti ancora necessari

- Formule per soglie e crescita avanzata: il PDF è ora esaminato, ma non le definisce. Le percentuali delle zone sono invece confermate nella specifica 0.5.
- Gerarchia accettata: stagione, anno di categoria e anno di nascita distinti; restano da configurare le regole della società.
- Preset dei valori medi, destinatari e fonte; nessun riempimento automatico dei dati reali.
- Scelta del nome della suite e palette definitiva. Il logo è ora fornito dall'utente; i colori rilevati nel file non sostituiscono una specifica di stampa.

## Come mantenere il registro

Conservare gli ID; per richieste composte aggiornare lo stato di ogni parte. Segnare «completato» solo dopo implementazione e verifica del criterio, citando file/test o versione. Registrare ogni variazione significativa nel [changelog](../CHANGELOG.md), con motivazione, ID coinvolti e distinzione fra progetto e software.

## Dettaglio test: visibilità dei tracciati — 18 ottobre 2026

- [x] Grafico dei campioni FIT/CSV in cima al dettaglio incrementale, anaerobico e custom, con potenza, FC e cadenza sovrapposte su un unico asse temporale, mantenendo scale e unità indipendenti.
- [x] Canali opzionali con unità esplicite: velocità, temperatura, quota; lattato come osservazioni puntuali nel tempo. Restano disponibili i grafici specialistici gas/lattato-carico.
- [x] Distinzione e filtro tracciato/riepilogo nello storico; spiegazione nei test senza campioni, nessuna ricostruzione da medie/massimi o interpolazione delle lacune.
- [x] Recupero dei campioni dall'oggetto del tracciato quando non inclusi nel record, senza ricalcoli automatici. Guida ed esempi in TESTARE_IL_PROGETTO.md.

## Grafici sovrapposti e confronti leggibili — 18 ottobre 2026

- [x] Un solo grafico temporale per potenza/FC/cadenza e lattato misurato, scale fisiche indipendenti, selettore per i canali aggiuntivi. Nessuna normalizzazione implicita delle grandezze.
- [x] Storici: una curva per serie omogenea, non una voce di legenda per aggregato. Esclusione delle serie prive di valori per la metrica scelta, una sola serie iniziale e selezione esplicita di massimo quattro.
- [x] Identità delle serie basata sulle separazioni esistenti del backend: protocollo/versione, metodo/condizioni/schema e origine soglia. Affiancamento descrittivo fra protocolli, senza aggregarli né dichiarare equivalenze automatiche.
- [x] Metrica e protocollo prima dei filtri secondari; legenda breve, metodi nella chiave, tabella riferita alle serie visualizzate, zero/null distinti. Esportazioni complete dell'archivio filtrato chiaramente separate dalla selezione interattiva.
- [x] Modelli grafici verificati con 12 test Node e GUI sul corpus completo, senza rigenerazione dei dati.

## Lattato configurabile e chiarimento Android — 18 ottobre 2026

- [x] Livelli di lattato configurabili per prova, default 2/3/4 mmol/L: interpolazione lineare locale W, W/kg e FC, senza estrapolazione o equivalenze automatiche con soglie fisiologiche.
- [x] FC da finestra finale dello step completo costante e copertura del preset; bpm indisponibili se mancano step/FC validi. Metodi e prelievi di supporto salvati; vecchie revisioni preservate e metodi distinti negli storici.
- [x] GUI di configurazione/risultati e grafici, metriche storiche dinamiche per livelli decimali, MD/PDF e CSV esteso, mantenendo lo standard CSV storico.
- [x] Verifica numerica, casi ambigui/mancanti e report; PDF renderizzato e ispezionato, cache aggiornata per il nuovo renderer.
- [x] Chiarimento Android: Kotlin già presente nella shell/credenziali/worker; Python incorporato con Chaquopy per riuso, ASGI in-process senza listener HTTP. Decisione e limiti descritti in ANDROID.md.
- [ ] Build e collaudo Android su dispositivo fisico: restano rinviati come concordato; toolchain e wheel native non ancora disponibili. Confermare compatibilità dipendenze/ABI, prestazioni e ciclo di vita prima di dichiarare il prodotto Android pronto.

## Osservazioni manuali acquisite — 19 ottobre 2026

Le 11 osservazioni originali sono conservate in [COMMENTI_ORIGINALI_2026-10-19.md](archivio/COMMENTI_ORIGINALI_2026-10-19.md). Analisi, dipendenze, fonti e criteri di accettazione: [ANALISI_TODO_MANUALI_2026-10-19.md](archivio/ANALISI_TODO_MANUALI_2026-10-19.md). I 15 requisiti sotto sono stati attuati nei sorgenti con gli stati puntuali aggiornati. L’analisi originale resta storica; metodi effettivi in MATURAZIONE.md. Nessuna implementazione equivale a validazione scientifica esterna o rilascio di un nuovo installer.

| ID | Requisito normalizzato | Stato, priorità e accettazione |
|---|---|---|
| TD-83 / UI-27 | Avviare «Correggi test» con un pulsante esplicito, anziché aprire il modulo dentro una sezione espandibile. Uniformare incrementali, anaerobici e custom. | **Implementato e verificato localmente.** Editor dedicato con conferma/annullamento, motivo e nuova revisione; permessi e protezione da modifiche concorrenti preservati. |
| TD-84 / UI-28 | Collocare i campi personalizzati in coda al modulo e alla scheda test, prima delle azioni finali. | **Implementato e verificato localmente.** Sezione riconoscibile e coerente nelle famiglie; campi standard prioritari, validazione e valori conservati. |
| TD-85 / UI-29 | Inserire in fondo a ogni pagina un glossario contestuale per acronimi e termini tecnici effettivamente usati. | **Implementato e verificato localmente.** Definizioni/unità/origine dei valori, IT/EN, accessibile anche da tastiera; nessun glossario vuoto o enciclopedia ripetuta. |
| TD-86 / UI-30 | Dare a potenza di soglia e FTHR pari evidenza rispetto alla MAP e affiancarle alle zone. Riordinare le sezioni del dettaglio. | **Implementato e verificato localmente.** Riferimenti distinti, fonte e indisponibilità visibili; zone legate al riferimento esatto. Ordine proposto nell'analisi, adattato alla famiglia di test. |
| TD-87 / SCI-02 | Mostrare subito sotto ogni soglia il metodo e l'eventuale coefficiente realmente applicato. | **Implementato nella GUI:** fonte, base/coefficiente effettivo e risultato accanto alle zone. Nessun coefficiente automatico; livelli lattato distinti dalle soglie fisiologiche. |
| TD-88 / LEGAL-01 | Esporre insieme alla licenza l'assenza di garanzia e i limiti, compreso il rischio di perdita dati. | **Implementato:** avvisi persistenti, pannello licenza/garanzia/backup e testi GPL/dipendenze originali. Revisione giuridica del distributore ancora necessaria; nessuna esenzione assoluta dichiarata. |
| TD-89 / UI-31 | Rendere semplice impostare i tempi guardando il grafico: minuti leggibili e secondi esatti coerenti nei campi. | **Implementato e verificato:** TimeInput secondi/mm:ss, hover in secondi, marker e selezione per incrementali/custom; inizio anaerobico con durata del protocollo. 23:45 = 1.425 s; nessuna nuova revisione al solo click. |
| TD-90 / UI-32 | Spiegare lo scopo del grafico lattato-carico e collegarlo chiaramente a watt e FC ai livelli richiesti. | **Implementato e verificato:** spiegazione W–mmol/L, livello e punto selezionabili, guide grafiche e riga evidenziata con W/W/kg/FC. Tracciato temporale distinto; nessuna nuova equazione o estrapolazione. |
| TD-91 / UI-33 | Mantenere sempre raggiungibile la chiusura del dettaglio test durante lo scorrimento. | **Implementato e verificato localmente.** Testata con X persistente, nome accessibile, Esc e gestione focus; nessuna perdita silenziosa di modifiche, nessuna trasparenza verso la lista sottostante. |
| TD-92 / CLOUD-05 | Rendere comprensibili disponibilità e prerequisiti di «Collega account» per Drive/Dropbox/OneDrive. | **Implementato per stati/prerequisiti:** comando disabilitato con spiegazione quando incompleto, fallback browser e distinzione token/accesso destinazione. L’ultimo accesso verificato è vincolato alla connessione. **Aperti** registrazione OAuth della distribuzione e collaudo con account reali. |
| TD-93 / MAT-01 | Estendere l'antropometria datata con dati necessari ai metodi maturativi, mantenendo facoltativi statura dei genitori, apertura braccia e lunghezza arti inferiori. | **Implementato:** modello misura additivo con qualità/precisione e misure avanzate facoltative, fonte della previsione esterna, correzione con motivo/revisione, UI/CSV/backup. Nessun dato opzionale diventa obbligatorio per una rilevazione. |
| TD-94 / MAT-02 | Calcolare e mostrare la velocità di crescita staturale (HV) e la sua storia separatamente dai risultati prestativi. | **Implementato e verificato:** HV qualificata 90–400 giorni, fonti/qualità/precisione, delta e motivi; zero mantenuto, calo statura e intervalli inadeguati non annualizzati. Regole prudenziali versionate del prodotto, non criteri diagnostici. |
| TD-95 / MAT-03 | Aggiungere metodi espliciti/versionati per maturity offset, PHV/APHV e, quando possibile, statura adulta prevista, %PAH e crescita residua. | **Implementato con perimetro esplicito:** Moore standing, Mirwald, APHV stimata e PHV quadratico longitudinale esplorativo, %PAH/residuo da previsione adulta **esterna** tracciata. Khamis–Roche automatico non incluso, tabelle corrette non verificate. Domini/SEE/limiti in MATURAZIONE.md; validazione esterna ancora aperta. |
| TD-96 / MAT-04 | Evidenziare gli indici pertinenti all'età e disponibili, conservando tutti i risultati e lo storico nella pagina atleta. | **Implementato:** fasce non sovrapposte alla data scelta, HV/PHV disponibili in evidenza e offset sotto 16 anni; tabelle di tutte le stime e snapshot precedenti sempre consultabili. Indici opzionali in area secondaria; nessuna maturazione dedotta dalla sola età. |
| TD-97 / MAT-05 | Integrare dati e analisi maturative in storico atleta, CSV esteso, report gerarchici, backup e sincronizzazione per società. | **Implementato e verificato localmente:** snapshot con input completi/metodo/hash, CSV estesi e report gerarchici da analisi conservate; backup/ripristino reale e sync firmata con visualizzatore testati. Schema storico preservato; oracoli indipendenti e corpus crescita dedicato. |

P0 = condizione di accettazione prima del rilascio della funzione; P1 = prossima revisione di usabilità/trasparenza; P2 = nuova area funzionale dopo specifica e consolidamento. La numerazione non impone l'ordine di implementazione. Sync v2, backup scalabili e separazione legacy rimangono priorità infrastrutturali già registrate; questa acquisizione non le dichiara concluse.

## 20 ottobre 2026 — riallineamento UI della suite

Implementato il consumo di `@cycling-suite/ui` 0.2.2, derivato dall'interfaccia corrente di Fuorigiri 0.10.0: shell/controlli responsive, liste/tabelle/riepiloghi, finestre con testata fissa, focus/Esc e protezione delle modifiche, tempi in secondi/mm:ss. Common è la fonte delle parti condivise; i moduli locali delegano alla libreria. Menu, contenuti e layout specifici, archivi e motori rimangono separati. Aggiornamento locale di sorgenti e dipendenza, senza nuovi installer o pubblicazioni.

## 20 ottobre 2026 — galleria dell’interfaccia

**DOC-GALLERY-01 — Implementato.** README con schermate reali delle funzionalità principali, versionate in `docs/screenshots/`, testi alternativi e didascalie; esclusivamente dati sintetici. Sette viste acquisite e ispezionate: atleti, protocolli, incrementale, Wingate, storici con aggregati, crescita/maturazione, report ed esportazioni. [Procedura e provenienza](screenshots/README.md). Accettazione continuativa: aggiornare nello stesso intervento le immagini delle schermate modificate, comprese dipendenze UI comuni; revisione prima delle release, data/versione dichiarate, nessuna credenziale o dato personale. Non è automazione periodica né collaudo di piattaforme non distribuite.

## 25 ottobre 2026 — GRUPPI-02: stagioni sorelle e pianificazione

Richiesta: [osservazioni originali](archivio/COMMENTI_ORIGINALI_2026-10-25.md). L'utente riferisce collaudo personale di creazione societa/protocolli, import bulk anagrafica/antropometria/storici aerobici e anaerobici, assegnazioni ai gruppi: evidenza dichiarata dall'utente, distinta dalle prove automatiche.

**Implementato e verificato localmente sul web.** Allievi/Esordienti sono contenitori; 2026 e 2027 hanno schede stagione sorelle, con indicazione Futura. La stagione gia salvata sul padre viene rappresentata senza cambiare ID, parent_id o appartenenze. Nuove categorie senza stagione incorporata; aggiunta stagione sotto una categoria esplicita. Gruppi senza stagione con appartenenze dirette ancora visibili.

Accettazione: conteggio distinto degli atleti per appartenenze sovrapposte all'anno selezionato (confini inclusivi), elenco filtrato coerente e consultabile prima dell'inizio del 2027. Categoria attuale aggregata separatamente. Assegnazione proposta dal 1 gennaio al 31 dicembre della stagione, date modificabili anche dal profilo; cambio gruppo aggiorna il periodo. Le etichette legacy non annuali mantengono la vista odierna e richiedono date esplicite: nessuna interpretazione arbitraria di 2026/27. Nessuna modifica retroattiva o copia tra societa. Prove e limiti in VERIFICA.md.

## 25 ottobre 2026 — GRUPPI-03 e IMPORT-04

Richieste originali aggiunte in [COMMENTI_ORIGINALI_2026-10-25.md](archivio/COMMENTI_ORIGINALI_2026-10-25.md).

- **GRUPPI-03 — implementato e verificato localmente sul web.** Modifica di nome categoria, nome/anno/categoria padre della stagione; stesso ID e appartenenze invariate. Eliminazione recuperabile e Ripristina visibili agli Admin dati. Niente eliminazione di atleti, test, misure o appartenenze storiche. Eliminare una categoria con stagioni attive richiede prima spostamento/eliminazione delle figlie; ripristinare prima il padre. Una stagione legacy sulla radice usa season_status separato e non elimina categoria o figlie.
- **IMPORT-04 — implementato e verificato localmente sul web.** Quinto profilo CSV Appartenenze storiche e future, modello vuoto ed esempio scaricabili. Identita tramite atleta_id (ID esterno o ID interno), controllo nome/cognome e societa; date esplicite, fine facoltativa, gruppo categoria, sottogruppo stagione, anno di categoria e note. Anteprima di appartenenze e gruppi nuovi, salvataggio atomico, duplicati esatti saltati e sovrapposizioni diverse segnalate. Nessuna riscrittura dello storico o deduzione di date dalla stagione. Guida: IMPORT_CSV.md.

Verifiche e consegna binaria aggiornate separatamente in VERIFICA.md; una schermata web non prova il bridge Android o il telefono.

## UI-SUITE-001 — coerenza organizzativa, 1 novembre 2026

Richiesta: verificare e allineare la collocazione delle funzionalità omologhe fra Ammiraglia, Fuorigiri e A Ruota. Implementati accessi contestuali CSV da Atleti/Gruppi/Test/Antropometria, con tracciati limitati al contesto; punto completo in Archivio espandibile e istruzioni dopo i comandi. Appartenenze collettive in Gruppi, individuali nel profilo; responsabilità e permessi preservati. [Uso](IMPORT_CSV.md), [verifiche](VERIFICA.md). Nessun nuovo installer/APK né qualifica provider.
