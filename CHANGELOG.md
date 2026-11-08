# Changelog

## 8 novembre 2026 — candidato antro-incrementale-20261108-01

- Nuove build Windows e Android 0.10.0 con import antropometrico incrementale, altezza perineale e rapporto nel profilo, oltre a eliminazione/ripristino e aggiornamenti precedenti. Installer/portabile, APK debug, release non firmato, supporto strumentale, sorgenti/wheel e 25 checksum verificati in nuova consegna locale.
- Smoke e scansioni Windows correnti riusciti; firma debug, allineamento e contenuti APK verificati. Nessuna pubblicazione, firma release o prova runtime Android; i gate di accettazione e i problemi nativi 16 KB restano aperti. [Registro](docs/VERIFICA.md).

## 8 novembre 2026 — import antropometrico incrementale

- Reimport CSV completa i campi mancanti di una rilevazione univocamente compatibile per atleta/data, conservando ID, provenienza e nuova revisione. Ripetizioni già acquisite saltate; discordanza o ambiguità bloccano il lotto senza sovrascritture.
- Anteprima con operazione e campi da integrare; conferma legata al piano visualizzato e alle revisioni. Creazioni e aggiornamenti sono atomici e usano firme/sync esistenti. Test e prova GUI sintetica riusciti; nessuna nuova build nativa.

## 8 novembre 2026 — altezza perineale e rapporto nel profilo

- Standard CSV antropometrico esteso con `altezza_perineale_cm`, presente anche in modello, anteprima ed export; compatibilità con file precedenti. Misura modificabile nell’editor e distinta dalla lunghezza arti.
- Colonne altezza perineale e rapporto percentuale sulla statura nel profilo, calcolato esclusivamente nella stessa rilevazione. Nessun aggiornamento automatico delle rilevazioni precedenti durante l’import. Verifiche automatiche e GUI su dati sintetici; EXE/APK esistenti invariati.

## 8 novembre 2026 — candidato record-lifecycle-20261108-01

- Nuove build Windows e Android 0.10.0 con eliminazione/ripristino di rilevazioni e test, oltre agli aggiornamenti precedenti. Consegna locale separata: installer, portabile, debug firmato per test, release non firmato, supporto strumentale, sorgenti, wheel e checksum verificati.
- Smoke Windows e scansioni correnti riusciti; nessuna pubblicazione o firma release implicita. Restano accettazione Windows pulito, WIN-AV-01 del vecchio candidato, runtime Android della nuova build e gate nativo 16 KB. [Prove](docs/VERIFICA.md).

## 8 novembre 2026 — eliminazione recuperabile di rilevazioni e test

- Comandi Elimina nelle rispettive finestre di correzione, con conferma separata e recupero da Rilevazioni eliminate / Test eliminati. Funziona anche senza compilare una correzione; permessi Admin dati e controllo della revisione preservati.
- Esteso il ciclo di vita alle misure antropometriche senza eliminazione fisica di revisioni o file. Esclusione da dati correnti, defaults e anteprima maturazione; analisi e report già conservati invariati. Catture QA e documentazione aggiornate; nessun nuovo pacchetto nativo.

## 8 novembre 2026 — nuovi candidati Windows e Android

- Confezionato `sync-intervals-20261107-01` (prodotto 0.10.0), con sincronizzazione automatica, Intervals.icu e modifiche locali correnti: installer, portabile completo, debug Android con firma di test invariata, release non firmato, sorgenti e wheel native. Build del 7, consegna verificata l’8; nessuna pubblicazione.
- Scansioni correnti Defender e smoke Windows riusciti; il precedente rilevamento resta aperto e Windows pulito non collaudato. Firma/debug/allineamento e contenuti APK verificati, nessun nuovo runtime su emulatore/telefono; sei moduli nativi ancora non qualificati 16 KB. Manifest e 24 checksum inclusi. [Riscontri e limiti](docs/VERIFICA.md).

## 7 novembre 2026 — sincronizzazione automatica e Intervals.icu

- SYNC-AUTO-01: avvio automatico dello scambio configurato all’apertura della società, circa 10 secondi dopo le modifiche e ogni 5 minuti mentre l’interfaccia è aperta. Preferenza locale per dispositivo/archivio (predefinita attiva), tentativi da 30 secondi fino a 30 minuti, nessuna sovrapposizione con i lavori manuali. Ultimo scambio riuscito distinto dall’ultimo tentativo; le bozze della connessione non sono sostituite dal completamento automatico.
- INT-ICU-01: ID facoltativo Intervals.icu nel profilo, sempre modificabile; interruttore condiviso della società in Archivio e scambio, predefinito disattivato. Nasconde soltanto il collegamento esterno. ID e opzione seguono revisioni, sincronizzazione e backup; client precedenti che omettono il campo lo preservano. Nessuna API o credenziale Intervals.icu.
- Modifiche ai sorgenti e frontend compilato; nessun nuovo EXE/APK o pubblicazione.

## 7 novembre 2026 — diagnosi blocco antivirus Windows

- WIN-AV-01: confermata rimozione dell'EXE da Microsoft Defender sul PC destinatario; candidato `windows-alpha-review-20261102-01` bloccato in attesa di revisione. Documentati rilevamento e criteri per risolverlo in `docs/WINDOWS_DEFENDER.md`. Nessuna modifica al binario, esclusione antivirus o nuova consegna.

## 7 novembre 2026 — aggiunta collettiva dal filtro e IMC

- Aggiungi atleti al gruppo anche nell’elenco filtrato per categoria, oltre alla stagione; scelta esplicita della destinazione nella categoria, rosa già popolata supportata e flusso atomico/permessi invariati.
- IMC (BMI) descrittivo nella tabella antropometrica e grafico storico espandibile da due valori: solo peso e statura nella stessa rilevazione, fonte conservata, nessuna classificazione automatica. Aggiornate guide e catture QA; frontend compilato, nessun nuovo EXE/APK o rilascio.

## 7 novembre 2026 — collegamenti dell’andamento antropometrico

- Nel profilo atleta peso e statura collegano le rispettive misure disponibili anche quando una rilevazione intermedia contiene soltanto l’altra grandezza. Nessun valore mancante viene sostituito o salvato come interpolazione; modifica al frontend, senza nuova build EXE/APK.

## 2 novembre 2026 — seguito native 16 KB e candidato Windows

- Nuovo auditor ELF legge anche la stdlib nelle `.imy` Chaquopy: 222 oggetti nel candidato Pillow e sei problemi confermati. Contratto dei simboli richiesti da Matplotlib/NumPy, verifica wheel native e test degli strumenti.
- Kit sorgenti e ricette Fedora per pydantic-core 2.41.4 ricompilato, FreeType 2.15.0, libpng 1.6.59 e OpenBLAS 0.3.34 con LAPACK/LP64; controllo runtime numerico predisposto. Nessuna nuova wheel di questa fase adottata, nessun pin o formula cambiato. [Procedura](docs/ANDROID_NATIVE_16KB.md).
- Ricompilazione Windows isolata dopo regressione completa; [prove e limiti](docs/VERIFICA.md). Nessuna pubblicazione, firma implicita o build Linux desktop.

## 2 novembre 2026 — integrazione Pillow Android 13

- Candidato Android separato `android-pillow-20261102-01`: debug con firma abituale, release non firmato e test; emulatore API35 x86_64, **2 test passati**, immagini/logo/font, PDF scritto e renderizzato da Android. Telefono, export tramite UI e firma ancora aperti. Audit di 106 ELF/APK: sei moduli ulteriori non qualificati LOAD 16 KB; Pillow supera il controllo. Nessuna pubblicazione o nuova build Windows.

- Ricevute e verificate localmente le due wheel Fedora cp313/API26: SHA-256, ZIP/RECORD e dieci moduli ELF con dipendenza Python e LOAD a 16 KB. Pin Pillow 13.0.0 e gate aggiornato a otto wheel; provenienza in android/wheels/PILLOW_BUILD.json, inclusa nella confezione native.
- Avvisi originali Pillow/libjpeg-turbo/FreeType nel documento legale canonico; aggiunto test strumentale da script unico per PNG/JPEG, font, Matplotlib Agg e PDF ReportLab. [Esiti effettivi build/runtime e limiti](docs/VERIFICA.md); altre dipendenze native Matplotlib/Chaquopy rimangono da qualificare.

## 2 novembre 2026 — preparazione Pillow Android

- Primo risultato Fedora comunicato dall'utente: wheel Pillow 13.0.0 cp313/API26 x86_64 prodotta; digest e CRC confermati sul builder, cinque moduli ELF con libpython3.13.so e LOAD a 16 KB. Trasferimento, ARM64, runtime e APK restano aperti; manifest dell'app invariato.

- Corretto il primo errore riscontrato su Fedora con cibuildwheel 4.3.1: `--only` determina la piattaforma e non può essere combinato con `--platform`. Compilazione Pillow e qualifica ancora aperte; log del primo tentativo conservato.

- Verificata disponibilità: nessuna wheel Android PyPI, Chaquopy cp313 fermo a 11.0.0. Kit sorgenti con Pillow 13.0.0, libjpeg-turbo 3.2.0 e FreeType 2.14.3, provenienza/digest e builder Fedora sperimentale per ABI separate.
- Preparato controllo runtime Android immagini/font/Matplotlib/ReportLab; quattro regressioni sugli strumenti di build. Ricetta ancora da eseguire dall'utente su Fedora, nessuna nuova wheel/APK, firma o modifica ai dati e ai pin dell'app. [Procedura](docs/ANDROID_PILLOW.md).

## 2 novembre 2026 — revisione pre-alpha ALPHA-REVIEW-01

- Ripristino: ZIP cifrati o con compressione non supportata rifiutati prima della lettura; regressioni legacy/v3/API, senza archivi parziali.
- Aggiornati Vite, certifi, Pillow Windows, pypdf e setuptools per gli avvisi di sicurezza; lock e minimi allineati. Android: python-multipart 0.0.32 nei requisiti, Pillow nativo ancora da aggiornare e qualificare.
- [Revisione e limiti](docs/REVISIONE_ALPHA.md): nessun nuovo EXE/APK o rilascio. Il candidato precedente richiede un successore; versione prodotto invariata.

## 2 novembre 2026 — allineamento pacchetti per la prima alpha

- Verificato l'installer Windows `pilot-20261101-01`: codice corrente, 19 asset frontend ricompilati identici e nuovo smoke EXE riuscito. Riutilizzato senza ricompilazione, conservando provenienza e consegna originale.
- Ricompilati APK debug e release con i sorgenti correnti, inclusi gli import contestuali UI-SUITE-001. Firma debug esistente confermata; release intenzionalmente non firmato, senza generazione di chiavi.
- Preparazione locale `alpha-prep-20261102-01`, versione prodotto 0.10.0 invariata: manifest, sorgenti, wheel native e checksum. Non è una release pubblicata; firma release, Windows pulito, telefono e flussi operativi restano gate distinti. Guida firma aggiornata con alternativa Android Studio.

## 1 novembre 2026 — trasferimento del checkout locale

- Checkout operativo in `performance-lab`: trasferiti dalla precedente cartella `test-analysis` i file locali mancanti, inclusi dati, ambiente di sviluppo e consegne già prodotte, senza sostituire i file presenti. Nessuna modifica alla versione prodotto o nuova build di distribuzione.
- Aggiornati i percorsi nelle guide operative; ripristinati nell'ambiente locale i riferimenti Python e i collegamenti dello staging comune. Residui originali e metadati Git conservati sotto `.local/repo-migration-2026-11-01/`, esclusi dal versionamento.

## 31 ottobre 2026 — pacchetti con supporto VO₂

- Nuovo installer Windows `pilot-20261031-01` e APK debug `pixel9-test-20261031-01`, versione prodotto 0.10.0: includono VO2-01 e tutte le correzioni precedenti. Build in directory nuove; consegne precedenti conservate.
- Bundle Windows con dipendenze e smoke EXE riuscito; installer Inno Setup non firmato Authenticode. APK con la stessa firma debug dei test precedenti, senza generare una chiave release.
- Sorgenti del working tree, licenze, guide, manifest e SHA-256 accompagnano entrambe le consegne. Nessuna installazione automatica, pubblicazione, prova su Windows pulito o telefono fisico.

## 31 ottobre 2026 — supporto VO₂ integrato

- VO2-01: misure VO₂ temporizzate nell’editor incrementale (L/min, istante e fonte/nota), CSV temporale con VO₂ e gas opzionali accanto a potenza/FC/lattato; conservato l’import gas separato con offset esplicito.
- Una sola fonte gas per analisi, validazione di valori/tempi, grafico temporale con asse VO₂ indipendente e lacune visibili. Misure manuali visualizzate come punti. VO₂peak usa il motore e le finestre già esistenti; VO₂max richiede conferma/evidenze del laboratorio.
- VO₂peak assoluto/relativo nel selettore del profilo; fonti manuali e importate separate nei confronti. CSV estesi `vo2.csv` e `vo2_osservazioni.csv`, report con provenienza e numerosità, revisioni conservate. Nessun ricalcolo degli storici; nuova versione del renderer individuale per la cache dei report.
- Modifiche ai sorgenti e frontend compilato; nessun nuovo EXE/APK prodotto o pubblicato.

## 27 ottobre 2026 — pacchetti con soglia relativa ripristinata

- Nuovi candidato Windows `pilot-20261027-02` e APK debug `pixel9-test-20261027-02`, versione prodotto 0.10.0: includono il KPI Soglia relativa (W/kg) nel dettaglio aerobico e nell’anteprima, insieme a tutte le correzioni precedenti. Firma Android debug invariata; pacchetti precedenti conservati.

## 27 ottobre 2026 — soglia relativa nel riepilogo test

- Ripristinato il KPI Soglia relativa (W/kg) accanto alla potenza di soglia in watt, nel dettaglio aerobico e nell’anteprima. Usa il risultato salvato, con peso associato al test; nessun ricalcolo dello storico o modifica all’ordine del grafico.
- Correzione successiva ai pacchetti `20261027-01`, che non la includono.

## 27 ottobre 2026 — pacchetti con pagine e KPI riordinati

- Nuovi candidato Windows `pilot-20261027-01` e APK debug `pixel9-test-20261027-01`, versione prodotto 0.10.0: includono UI-ORDER-01, grafico del test in alto quando disponibile, KPI unificati e tutte le correzioni precedenti. Firma debug Android esistente, aggiornamento senza disinstallazione; pacchetti precedenti conservati.
- Verifiche dei pacchetti in VERIFICA.md; nessuna installazione o pubblicazione automatica, prova sul Pixel fisico ancora da eseguire.

## 26 ottobre 2026 — ordine delle pagine e riepilogo test

- UI-ORDER-01: KPI aerobici riuniti in un solo riepilogo, MAP senza duplicati e fonti/coefficiente conservati. Grafico in apertura quando ci sono osservazioni rappresentabili, poi KPI/zone e approfondimenti; senza grafico, riepilogo in alto. Stessa sintesi KPI nell’anteprima.
- Anaerobici con indicatori principali in apertura e Altri risultati richiudibile, senza ripetere i KPI nella tabella.
- Profilo con elenco test dopo zone/MAP, misure e grafico antropometrico adiacenti. Elenco prove prima della guida richiudibile; storico principale prima della ripetibilità; report conservati vicini alla generazione.
- Modifiche ai sorgenti/frontend compilato; installer e APK `20261026-01` precedenti non contengono questo riordino.

## 26 ottobre 2026 — editor zone, stato sync e avvio Android

- Compilati installer Windows `pilot-20261026-01` e APK debug `pixel9-test-20261026-01`, con smoke Windows, asset correnti, firma e allineamento Android verificati. Stessa versione 0.10.0 e firma debug precedente; collaudo sul telefono ancora da eseguire.

- ZONE-03: Scegli zone apre un Dialog visibile, con indicazioni per modificare percentuali e riferimenti; tabelle con percentuali esplicite. Riepilogo zone compatto e MAP storiche subito dopo, con metrica iniziale MAP indipendente dagli altri storici.
- SYNC-UX-02: avvio/polling di job locali, deduplicazione degli avvii, progressi da operazioni reali, stato persistente al cambio scheda e riepilogo esito/incrementale vs verifica completa. I job interrotti dalla chiusura del processo non vengono mostrati riusciti.
- AND-START-01: attese di rete fuori dal lock di avvio/interfaccia, anche per WorkManager; preferenze con deadline, caricamento dati con retry, bootstrap con messaggio di errore e watchdog nativo con codice AVVIO. Asset WebView letti dall'APK senza cache HTML obsoleta. Nessun reset degli archivi o delle credenziali.

## 25 ottobre 2026 — zone aerobiche e scelta sul profilo

- Compilati candidato Windows `pilot-20261025-06` e APK debug personale `pixel9-test-20261025-03`, mantenendo versione prodotto 0.10.0 e firma debug precedente; smoke Windows, asset correnti, firma/allineamento Android verificati. Pacchetti precedenti preservati, nessuna installazione automatica.

- ZONE-02: zone FC/watt anche per i vecchi CSV senza FIT, derivate in lettura solo da riferimenti disponibili; nuovi import conservano lo snapshot. Schemi e tempi già archiviati preservati, nessun tempo inventato senza campioni. Canali privi di riferimento esplicitamente non disponibili.
- Profilo atleta con ultime zone disponibili per canale, adozione con anteprima di un preciso test/revisione oppure schemi e riferimenti custom. Scelta versionata nel record atleta, sincronizzata, modificabile da Admin dati e conservata nelle modifiche anagrafiche.
- Report individuale renderer `0.10-training-zones-1` con intervalli compatibili per gli import precedenti, senza riscrivere i test o cancellare i report già conservati.

## 25 ottobre 2026 — sincronizzazione, preferenze e società locali

- SYNC-UX-01: spinner e stato accessibile per l'intera sincronizzazione, protezione invii concorrenti e blocco configurazione; orari con fuso esplicito, selezione Fuso del dispositivo/Europe-Rome/UTC e conversione coerente anche nel registro.
- DEVICE-PREF-01: lingua e fuso persistono nella radice dati del dispositivo, indipendenti da porta HTTP e società; lingua caricata prima dell'interfaccia, preferenze fuori dai dati sincronizzati.
- SOCIETY-LOCAL-01: Gestisci società permette scollegamento recuperabile locale e ripristino, senza cancellare file, accessi o dati remoti; esclusione da inventario attivo e background, protezione percorsi delle copie scollegate.
- Guida WebDAV Windows/Android con invito personale e password applicazione Koofr. Nessuna connessione ad account reali eseguita dall'agente.

## 25 ottobre 2026 — report richiudibili e prova Pixel 9

- REPORT-SAVED-02: Report conservati richiudibile con details/summary, inizialmente chiuso come Condivisione e collaboratori; ricerca, filtro e pagina conservati durante chiusura/riapertura. Verificato nel browser.
- APK debug aggiornato per test personale su Pixel 9, firma debug esistente e allineamento verificati. Nessuna chiave release creata né installazione fisica eseguita. Il candidato Windows 04 precedente non include la sezione richiudibile.
- Guida installazione Android e distinzione fra trasferimento APK via Drive, cartella cloud desktop e sincronizzazione tramite API/WebDAV; con solo Drive e senza GCP lo scambio Windows/Android non è configurabile con la cartella desktop.

## 25 ottobre 2026 — coefficiente della soglia aerobica

- Candidato Windows `pilot-20261025-04`: bundle aggiornato con coefficiente e tutte le modifiche precedenti, inclusa paginazione a 5 report; smoke EXE riuscito. Versione prodotto 0.10.0 invariata; nessun APK aggiornato in questa consegna.

- Correggi test precompila anche il coefficiente dei vecchi import; per ricalcolare la soglia occorre svuotare il valore dichiarato, che ha precedenza. Verificata revisione esplicita da 0,8 a 0,75 con MAP 250 W e soglia 187,5 W.

- AEROBIC-REF-01: il dettaglio mostra esplicitamente coefficiente MAP → soglia e percentuale; per import CSV precedenti legge il valore originale `coeff_soglia` quando manca nelle impostazioni. Assenza esplicita se non disponibile, nessuna deduzione dal rapporto tra watt arrotondati. Un coefficiente conservato su soglia dichiarata è indicato come non applicato.
- Nuovi import aerobici conservano il coefficiente nelle impostazioni con validazione coerente con l'inserimento manuale; potenza di soglia storica invariata. Nessuna migrazione o riscrittura dei test esistenti. Installer precedente invariato.

## 25 ottobre 2026 — organizzazione report conservati

- REPORT-SAVED-01: elenco con 5 report per pagina tramite RecordCards della UI comune, ricerca e filtro per formato; cambio filtri riporta alla prima pagina. Ordine dal più recente, data di creazione, società/gruppo/stagione/atleta quando disponibili e riferimento breve per distinguere le copie.
- Metadati di presentazione ricavati dai record e dalle revisioni esistenti, senza riscritture degli originali firmati. Download JSON conservati come JSON. Modifica nei sorgenti; installer candidato 03 precedente invariato.

## 25 ottobre 2026 — report archivio e accesso alle rose storiche

- REPORT-ARCHIVE-01: feedback immediato con rotellina e testo durante anteprima, PDF e Markdown; comandi e filtri disabilitati fino al termine per evitare doppi invii.
- Renderer archivio `archive-5`: indice cliccabile con pagine e segnalibri, capitoli distinti, nuova pagina per atleta, font incorporati e tabelle entro i margini. Metriche aggregate nella stessa tabella per protocollo/metodo; grafici individuali solo con almeno due osservazioni. Dati e criteri scientifici invariati.
- GRUPPI-04: Mostra gli atleti imposta Tutti e azzera la ricerca precedente, conservando il gruppo/stagione selezionato.
- DOC-DRIVE-01: guida al primo collegamento Google Drive, scope, OAuth Desktop/Android e collaudo con due dispositivi. Nessun account reale collegato.

## 25 ottobre 2026 — gestione gruppi e import appartenenze

- Compilato candidato locale `pilot-20261025-02` con installer Windows, portabile, APK non firmato e sorgenti; smoke EXE e integrita pacchetti verificati. Include tutte le modifiche funzionali sotto; candidato 01 preservato.

- GRUPPI-03: modifica categoria/stagione e genitore della stagione; eliminazione recuperabile e ripristino senza cancellare atleti, test o appartenenze storiche. Protezione delle categorie con figli attivi e gestione distinta della stagione legacy sul padre. Permessi Admin dati e revisioni preservati.
- IMPORT-04: quinto profilo CSV per appartenenze passate, attuali e future; modello vuoto ed esempio scaricabili. Riconciliazione ID/nome/cognome, date esplicite, anteprima gruppi mancanti e salvataggio atomico, duplicati esatti saltati e altre sovrapposizioni bloccate. Annullamento protetto dalle dipendenze successive.

## 25 ottobre 2026 — compilazione candidato per aggiornamento locale

- Prodotto il candidato `Fuorigiri-0.10.0-pilot-20261025-01` con correzioni GRUPPI-02: bundle EXE, installer Windows, portabile e APK release non firmato, sorgenti e checksum. Smoke dell'EXE e integrita dei pacchetti verificati; firma Android del titolare e collaudo del dispositivo restano separati. Precedenti consegne conservate, nessuna pubblicazione o installazione automatica.

## 25 ottobre 2026 — categorie e stagioni future

- GRUPPI-02: categorie con stagioni allo stesso livello, anche quando il 2026 era salvato direttamente sulla categoria. Compatibilita di sola presentazione: nessuna migrazione o riscrittura delle appartenenze.
- Rosa annuale e conteggi basati sulla sovrapposizione inclusiva al periodo 1 gennaio / 31 dicembre, compresi gli inserimenti futuri. La vista attuale della categoria resta distinta. Date proposte per l'assegnazione coerenti con la stagione e modificabili; nuove categorie senza stagione incorporata, comando Aggiungi stagione dedicato. Traduzioni IT/EN.
- Verifiche locali e limiti in docs/VERIFICA.md; nessun installer o APK aggiornato.


## 22 ottobre 2026 — assegnazione atleti ai gruppi

- GRUPPI-01: comando visibile nel profilo atleta e Aggiungi atleti su gruppi, stagioni ed elenco filtrato. Ricerca e selezione multipla, periodo e anno di categoria, esclusione di appartenenze sovrapposte già presenti; salvataggio atomico e permessi Admin dati. Nessuna modifica retroattiva alle appartenenze esistenti.

## 22 ottobre 2026 — importazioni test e modelli CSV

- IMPORT-03: anteprime specifiche di test aerobici e anaerobici con atleta, codice protocollo e risultati; protocolli nuovi separati dal conteggio delle righe. Modelli CSV vuoti scaricabili per tutti e quattro i profili dalla sezione import. Import anaerobico generale per Sprint e Wingate 15/30 s con tipo/durata espliciti; compatibilità ANA-15-070 e rifiuto di metadati in conflitto. Include IMPORT-02 antropometria. Candidato finale successivo alle build già consegnate.

## 22 ottobre 2026 — importazione antropometria

- IMPORT-02: anteprima specifica con ID atleta, nome completo, data, peso, statura, fonte e origine, senza identificativi tecnici della rilevazione. Fonti derivato/stimato conservate in import, editor ed export; origine preservata. Valori fonte sconosciuti segnalati, assenze mantenute vuote. Nessuna riscrittura degli archivi già importati.

## 22 ottobre 2026 — aggiornamento candidato Windows e Android

- Preparazione candidato `pilot-20261022-02` dai sorgenti correnti: riapertura desktop, codice protocolli e anteprima anagrafica CSV. Installer e portabile Windows, APK release non firmato e debug per collaudo separati dalle consegne precedenti; versione prodotto 0.10.0 invariata. Nessuna pubblicazione o installazione automatica.

## 22 ottobre 2026 — anteprima importazione anagrafica

- Anteprima CSV atleti con cognome, nome, anno di nascita, conferma, fonte, sesso, stato e note. Eliminata la colonna Data non pertinente e sostituita la tabella errori vuota con un messaggio esplicito. Correzione nei sorgenti, non negli installer esistenti.

## 22 ottobre 2026 — codice dei protocolli

- PROTOCOLLI-01: Codice visibile, precompilato e modificabile per tutte le famiglie e per import ERG; nuove versioni inizializzate dal codice salvato. Negli anaerobici codice operativo separato dal tipo di test, con compatibilità delle chiamate precedenti e controllo duplicati codice/versione. Nessuna modifica agli storici o ai metodi scientifici; modifica ai sorgenti, non agli installer già consegnati.

## 22 ottobre 2026 — riapertura desktop

- DESKTOP-01: Windows/Linux ricordano l’ultima società nelle preferenze locali del backend, indipendentemente dalla porta HTTP e dalla sessione WebEngine. Ripristino verificato contro inventario, nessun cambio automatico verso un altro archivio se quello ricordato manca; preferenza di soli ID, anche per visualizzatori. Modifica ai sorgenti; preparazione di una nuova consegna Windows `windows-20261022-01` per collaudare l’aggiornamento. Il candidato e gli installer precedenti restano invariati.

- 21 ottobre, revisione conservativa dei sorgenti: token HTTP non ASCII rifiutati senza errore interno; export antropometrico coerente con l'eliminazione delle misure; CSV malformati e campi oltre limite producono errori gestiti, mantenendo i CSV multilinea validi. Nessun cambiamento UI, schema o metodo scientifico; correzioni non ancora incluse nei candidati compilati. Prove in `docs/VERIFICA.md`.

## 0.10.0 — 20–21 ottobre 2026 (sorgenti; distribuzione non pubblicata)

- 21 ottobre, PILOT-01: preparazione candidato locale Windows/Android 0.10.0 con ID separato, build Windows isolate e output Inno configurabile, packager con sorgenti/wheel/checksum; checklist di collaudo e istruzioni firma Android del titolare. Nessuna chiave generata o pubblicazione; APK release non firmato per scelta dell’utente.

- 21 ottobre, correzione TD-106: nella testata Android logo alla destra della scritta, testo e marchio allineati a destra; hamburger invariato a sinistra. UI comune 0.2.8, senza modificare i bootstrap centrati o la sidebar desktop.

- 21 ottobre, TD-106–107: logo applicativo a sinistra del nome anche all’avvio; grafico orizzontale immersivo senza intestazione o cornice, barre Android nascoste temporaneamente, X e comandi flottanti. Ripristino barre/orientamento e Back verificati su emulatore; UI comune 0.2.7 consegnata solo a Fuorigiri.

- 21 ottobre, TD-105: Vista ampia Android apre il grafico in orizzontale e ripristina l’orientamento precedente alla chiusura, conservando il dettaglio test; dimensioni adattive alla rotazione, Back da Esplora separato dalla chiusura. APK aggiornato e prova reale su emulatore, screenshot orizzontale nella galleria.

- 21 ottobre, TD-102–104: hamburger a sinistra e Back di sistema; spaziature Android compatte, contesto persistente, grafici con comandi sotto la figura e Scorri pagina predefinito. Un Back esce dall’esplorazione; cancel dei dialoghi annidati corretto nel common 0.2.6. Plotly differito, avvio con fasi/riprova, valori tabellari accessibili e paginati; API e risultati scientifici invariati.

- 21 ottobre, completamento Android TD-99–101: ritorno tra sezioni/profili/elenchi con pagina e filtri conservati, ultima società persistente dopo chiusura, schede paginate e filtri richiudibili, moduli con azioni sticky e campi facoltativi raggruppati. Componenti comuni consegnati come UI 0.2.4, guida delle best practice per le app future nella repository comune; nessun aggiornamento implicito di Ammiraglia o pubblicazione.

- Android: società, sezioni e lingua nel menu hamburger; nuova vista Info per versione, stato offline, logo/attribuzione fissi e licenza. Indietro chiude prima i dialoghi. APK debug aggiornato e verificato visivamente su emulatore, galleria con screenshot reali; navigazione desktop conservata.

- Corretto il primo avvio Android: wheel cryptography ABI3 con dipendenza libpython esplicita, strumento di repair con originali/hash tracciati e RECORD valido; Gradle rileva cambi delle wheel locali. Insets WebView e messaggio di errore corretti. APK installato/avviato su emulatore x86_64 e test nativo import, cifratura/firma, API e Keystore passato; telefono e collaudo completo ancora aperti.

- Primo APK debug locale Android prodotto su Windows: dipendenze risolte per entrambe le ABI, sei wheel trasferite e digest verificati. Pacchetto di circa 96 MiB con frontend incluso; installazione e avvio su dispositivo ancora da collaudare, nessuna release pubblicata.

- Guida consolidata per ricostruire le sei wheel Android su Fedora Kinoite/Toolbox: toolchain, ambiente di sessione, OpenSSL/libffi, hook riusciti, checksum e trasferimento Windows. Guide Android e indice riallineati; cronologia dei tentativi mantenuta nel registro verifiche. Nessuna nuova build eseguita da questa documentazione.

- Aggiornamento Android: sei wheel native costruite sul builder utente; digest attesi registrati, gate esteso a CFFI e dipendenza Android fissata a 2.0.0. Trasferimento e integrità locale ancora da verificare, nessun APK collaudato.

- Primo risultato del builder Android Fedora Kinoite/Toolbox: dal log dell’utente, pydantic_core 2.41.4 cp313 Android x86_64 compilato e riparato con auditwheel. Procedura documentata; wheel ancora da trasferire e provare nell’app, ARM64/cryptography aperti, nessun APK prodotto.
- Ripresa richiesta della preparazione Android Studio: documentati flusso Windows/telefono, SDK/Gradle e blocco reale delle wheel native; quattro test del bridge passati su Windows. Nessun APK compilato o dispositivo collaudato.
- README con sette screenshot reali dell’interfaccia: atleti, protocolli, incrementale, Wingate, storici, crescita/maturazione e report. Solo dati sintetici; immagini versionate e procedura di manutenzione legata alle modifiche UI, senza nuovi artefatti applicativi.
- Riallineate le versioni Python, API, frontend/lockfile, Android (`versionCode` 1000), installer Windows e metadati Linux. Versione UI e nomi APK derivati dai metadati, con controllo di coerenza prima delle build.
- Le modifiche successive alla 0.8 sono raccolte qui; i titoli dei commit V0.9/V0.10 non avevano aggiornato la versione del programma. Nessuna release 0.9.0 dichiarata retroattivamente, nessun tag o installer creato da questo riallineamento.

### Sync v2, backup e migrazione, 19 ottobre 2026

- Formato di scambio v2: blocchi cifrati riutilizzabili, campioni separati nelle pubblicazioni, pagine leggere e ricevute/checkpoint; firme originali ricostruite e verificate. Attivazione esplicita, avviso firmato e lettura v1 conservata, senza cancellazione della storia.
- Backup ZIP64 v3 scritto/verificato/ripristinato progressivamente su disco, hash e inventario JSONL; download e salvataggio diretto desktop, compatibilità con i backup legacy. Prova reale su 101 MB sintetici non comprimibili.
- Separazione assistita per società con anteprima, impronta, dipendenze e revisioni complete, conflitti, oggetti propri e nuove identità/chiavi; originale conservato e blocco dei casi ambigui.
- Ripristino indipendente conserva i conflitti; firma durante import/migrazione usa la transazione corrente, evitando blocchi SQLite sui lotti grandi. CLI di manutenzione e prova di scala riproducibile. Nessun installer ricompilato né provider reale qualificato.

### Documentazione — riordino e presentazione, 19 ottobre 2026

- README riscritto con presentazione in inglese, funzioni attuali, limiti reali, avvio del corpus completo e link alle guide pertinenti.
- Indice `docs/README.md`; analisi, revisioni e piani superati conservati in `docs/archivio/` con collegamenti aggiornati. Guide cloud, distribuzione e dati sintetici rinominate senza numero di release.
- Roadmap corrente riscritta con priorità, dipendenze e accettazione; nessuna funzione o build aggiunta da questo riordino.

### profilo da test e corpus maturazione, 19 ottobre 2026

- Collegamento «Apri profilo atleta» nel dettaglio di qualsiasi test, disponibile anche in sola lettura.
- Demo standard completa/ridotta include quattro casi maturativi per società, con profilo femminile, antropometria avanzata e snapshot. Inclusione prima della creazione delle repliche e dei backup; alias `demo_maturation.py` conservato. Archivi esistenti non modificati automaticamente.

### attuazione TD-83–97, 19 ottobre 2026

- Editor test dedicati, testata/chiusura persistenti, focus/Esc e conferma dell'uscita con modifiche non salvate. Campi custom in coda; glossario contestuale e avvisi di licenza/garanzia/conservazione dati.
- Riferimenti MAP/potenza di soglia/FTHR con pari evidenza e zone adiacenti; coefficiente effettivo leggibile. Tempi sincronizzati secondi/mm:ss e hover esatti, selezione inizio/fine anche per custom; vista lattato-carico spiegata e collegata alla tabella.
- Stati cloud distinguono configurazione, account e verifica della destinazione; evidenza dell'ultimo scambio vincolata alla connessione. Non creati registrazioni OAuth né collegati account reali.
- Rilevazioni antropometriche estese e correggibili; motore crescita/maturazione versionato con HV, Moore/Mirwald, PHV longitudinale esplorativo, proporzioni e indici facoltativi. %PAH/residuo da previsione esterna esplicita, senza Khamis–Roche automatico non verificato.
- Snapshot maturativi immutati dopo correzioni, permessi per società, CSV estesi, report PDF/MD gerarchici e backup/sync. Corpus aggiuntivo `demo_maturation.py`, oracoli numerici e test di replica/ripristino. [Metodi e limiti](docs/MATURAZIONE.md).
- Nessun installer ricompilato; validazione scientifica esterna e collaudi reali restano necessari. Specifiche e AGENTS.md aggiornati.

### Documentazione — istruzioni della repository, 19 ottobre 2026

- Aggiunto `AGENTS.md` nella radice: vincoli del prodotto, fonti dei requisiti, lavoro sicuro sugli archivi, metodi scientifici, suite comune, verifiche e limiti della distribuzione.
- Definito l'obbligo di mantenerlo aggiornato quando cambiano regole, struttura, comandi o stato dei vincoli citati; risultati e backlog dettagliati restano nei documenti dedicati.

### Documentazione — acquisizione to-do manuali, 19 ottobre 2026

- Conservate integralmente le 11 osservazioni in `docs/archivio/COMMENTI_ORIGINALI_2026-10-19.md`; normalizzate in 15 requisiti TD-83–97 con stato, priorità e criteri di accettazione.
- Analizzati flusso correzione/chiusura test, ordine sezioni/campi custom, glossario, tempi del grafico, evidenza soglie/zone e provenienza dei coefficienti; spiegata l'utilità della vista lattato-carico già presente.
- Distinta implementazione OAuth da operatività della distribuzione/account reali; registrati messaggi e collaudi mancanti. Avvisi GPL/garanzia/perdita dati richiesti senza modificare la licenza o promettere esenzioni assolute.
- Definita la nuova area crescita/maturazione: HV prima delle stime, metodi e risultati osservati/stimati distinti, fasce d'età orientative, dati aggiuntivi opzionali non prioritari, storico/export e validazione. Fonti e decisioni residue nell'analisi dedicata.
- Aggiornati disegno architetturale e prossimi passi. Solo documenti: nessuna modifica al programma, ai dati o ai pacchetti distribuiti.

### revisione e isolamento società, 19 ottobre 2026

- Corretti spazi e metadati dei protocolli, etichette di stato e navigazione; selezione della società conservata e protetta da risposte asincrone obsolete.
- Profilo atleta con selezione di serie confrontabili; corretti confronti con origine soglia mancante, W/kg con peso stimato e metriche lattato dinamiche.
- Sync e inviti bloccati per archivi multi-società; identità e record vincolati alla società. Connessioni e canali restano separati per archivio; cartelle cloud con permessi distinti necessarie per collaboratori diversi.
- Sync gestita ordinaria evita i pacchetti già acquisiti; nuova verifica completa esplicita. Nessuna deduplicazione remota o migrazione del formato v1 ancora introdotta.
- Backup esportati soltanto entro i limiti accettati dal ripristino; misura dimensioni in sola lettura e piano per sync/backup scalabili documentati.
- 156 test backend passati, uno saltato; 18 test frontend passati e build riuscita. [Revisione e prossimi passi](docs/archivio/REVISIONE_GENERALE_2026-10-19.md). Nessun installer ricompilato.

### livelli di lattato e FC interpolata

- Livelli configurabili per prova, default 2/3/4 mmol/L, con W/W/kg/bpm stimati tramite interpolazione lineare locale; FC dalla finestra finale degli step completi e coperti, secondo preset. Nessuna estrapolazione o ricostruzione di FC mancanti.
- Metodo lattato v2 e prelievi di supporto tracciabili, metriche dinamiche negli storici, UI e grafici, PDF/MD e CSV lungo `extended/lattato_livelli.csv`. Conservati schema CSV storico e revisioni precedenti; aggiornato il renderer/cache dei report.
- Documentata l'architettura Android effettiva: Kotlin già presente con WebView/Chaquopy, API in-process e WorkManager. Chiariti costi e prerequisiti; nessuna build APK o modifica dei pin Android in questo intervento.

### grafico unico e confronti leggibili

- Linee potenza/FC/cadenza sovrapposte nel dettaglio con scale/unità indipendenti; lattato misurato sullo stesso grafico, canali aggiuntivi attivabili tramite selettore.
- Storici: una curva per protocollo/metodo anziché per singolo aggregato; eliminazione delle serie vuote per la metrica, scelta iniziale della più numerosa, confronto esplicito fino a quattro serie con legenda breve e tabella coerente.
- Protocolli diversi affiancabili senza unire medie/mediane; chiavi del backend preservate e avviso sulla diversa comparabilità. Metrica/protocollo prioritari, filtri secondari espandibili, ambito delle esportazioni esplicito.
- Ordine globale delle categorie e colori delle serie stabili; modelli grafici verificati da 12 test Node, guida e decisioni architetturali aggiornate.

### tracciati nel dettaglio test

- Grafici in evidenza e uniformi per incrementali, Sprint/Wingate e protocolli custom: potenza, FC e cadenza visibili con scale separate, più velocità/temperatura/quota se disponibili. Lattato misurato nel tempo distinto dall'analisi rispetto al carico; interruzioni senza valori inventati.
- Filtro e indicazione della disponibilità del tracciato nello storico; spiegazione esplicita per i soli riepiloghi manuali.
- Import CSV temporale con canali aggiuntivi e unità esplicite; decoder FIT conserva velocità, temperatura e quota. Recupero campioni dagli oggetti tracciato nel dettaglio, senza modificare revisioni o analisi archiviate.
- Guida per individuare i test dimostrativi con grafici e verifiche automatiche/UI; installer da ricompilare separatamente.

### rigenerazione dati dimostrativi

- `--reset` per demo minima e corpus completo: conservazione della vecchia directory in `.local/demo-backups`, controlli di percorso/link e archivi aperti, nessuna cancellazione definitiva o accesso ai riferimenti esterni.
- Il server di sviluppo usa il blocco istanza come il desktop; ZIP portabile del corpus generabile con `--export`.
- Guida di test riordinata con distinzione demo minima/completa, comandi sullo stesso percorso, uso GUI, repliche, ripristino ed esiti attesi.

### estrazione UI della suite

- Prima libreria condivisa nella repository autonoma cycling-suite-common, UI 0.1.0. Fuorigiri usa tema/campi/tabelle/footer comuni tramite tarball locale versionato, senza dipendenza da una repository sorella durante la build.
- Sorgenti/licenza inclusi nel pacchetto; provenienza, checksum, lockfile e logo originale verificati prima del packaging. Nuovo catalogo e guida per Ammiraglia nella repository comune.
- Repository applicative e archivi separati; backend scientifico invariato. Nessun nuovo installer o pubblicazione remota in questo passaggio.

## 0.8.0 - 18 ottobre 2026

- Catalogo Protocolli unificato: creazione manuale o ERG, incrementali anche senza step, Sprint/Wingate e protocolli custom, versionamento da scheda e filtri.
- Nuovo test sceglie protocollo/versione e modalità manuale o file; rimossa la definizione dei protocolli dal modulo anaerobico.
- Campi facoltativi tipizzati per protocollo/prova e per singola esecuzione; snapshot, validazione, revisioni, export e report. Metriche numeriche custom aggregate senza unire definizioni/unità diverse; nessuna formula fisiologica implicita.
- Anaerobici: scelta sessione FIT, gestione duplicati, inizio su grafico, zoom e esclusioni motivate; correzioni con riferimenti archiviati mantenuti.
- Corpus sintetico ampliato a due società e tre stagioni, con scenari realistici, errori controllati, repliche/ruoli/conflitto, backup e oracoli indipendenti. Guida di test aggiornata.
- Ripristino dei backup successivi alla sincronizzazione: ammesso il registro locale con schema verificato; nuovo registro sul dispositivo ripristinato. MAP in elenco atleti ricavata dall’ultima prova incrementale con risultato disponibile.
- Versione dello smoke test ricavata dal modulo del prodotto, anziché testo fisso. Motori fisiologici e schema SQLite invariati; build Android/Linux ancora rimandate.

## 0.7.0 - 18 ottobre 2026

- Adapter diretti Google Drive, Dropbox e OneDrive oltre a WebDAV/cartella; OAuth PKCE desktop, token nel portachiavi, rinnovo e stato account, caricamenti immutabili con rilettura e gestione di eventi cifrati concorrenti equivalenti. Test dei contratti simulati; account reali non collegati.
- Predisposizione client e contratto v1 per futuro servizio dedicato, senza server ospitato.
- Sorgenti Android con callback Dropbox/OneDrive, autorizzazione nativa Google e background condiviso; build Linux/Android restano rimandate.
- Sprint breve, Wingate 30 s e Wingate 15 s: protocolli versionati, FIT/CSV temporale o risultati manuali, finestre e formule esplicite, copertura, provenienza e comparabilità conservativa.
- Importazione storico Wingate 15 s ANA-15-070 (coppia frenante 0,70 N·m/kg confermata dall’utente), campi mancanti/fonti originali e indice W/s non convertiti; CSV base/esteso, report PDF/MD e storici/aggregazioni anaerobiche.
- Esempi FIT sintetici, nuovi test e documentazione operativa/scientifica. Nessun dato personale del CSV allegato distribuito; motore incrementale e schema SQLite invariati.

## 0.6.0 — 18 ottobre 2026

- Trasporto WebDAV HTTPS e cartella dietro il medesimo contratto, credenziali protette, retry/pubblicazione condizionale/rilettura e nuovo pannello connessione/stato/audit.
- Controlli accessi/revoche firmati in versioni immutabili, lettura prima della pubblicazione, blocco delle versioni divergenti, rotazione recuperabile del canale e lock di doppia apertura desktop.
- Icona minimale Fuorigiri mantenuta in SVG, PNG/ICO e vettore Android; integrazione in exe, finestra, installer, web e launcher. Logo societario/credito fissi preservati.
- Installer Windows per utente; manifest/build Flatpak, checksum/sorgenti e pipeline manuali. Nessuna dipendenza Python/Node/Qt da installare sul PC utente; runtime Flatpak acquisito all’installazione o incluso sul supporto offline.
- Android: shell Kotlin/WebView, adapter React/native, backend ASGI in-process, SAF per file/report, Keystore e WorkManager; layout compatto. Test del contratto su PC. **APK non disponibile:** gate wheel native aggiornate, toolchain POSIX e test dispositivo ancora aperti.
- Formule scientifiche, engine 0.5.0, schema 3 e revisioni storiche invariati. [Stato e limiti](docs/DISTRIBUZIONE.md).

## 0.5.0 — 17 ottobre 2026 / architettura 1.3

- Schema 3 con copia del database pre-migrazione, preset immutabili e identità dell’analisi salvata, risultati legacy invariati e separati nei confronti.
- Motore incrementale versionato: coperture senza arrotondamento, aderenza separata, finestre FC/recupero, marker/esclusioni, rampe/discontinui descrittivi, condizioni e RPE per scala.
- Import FIT con scelta sessione, correzioni esplicite e timer; import gas CSV; lattato a 2/4 mmol, Dmax cubico/modificato, VO2peak, grafici e suggerimenti ventilatori da revisione, ripetibilità con incertezza descrittiva ed export.
- Report società/gruppo/stagione/atleta da modello comune, PDF e Markdown con grafici, copertura, aggregati, schede e provenienza; qualità e analisi specialistiche anche nel singolo test.
- Fixture sintetiche e verifiche aggiunte; fonti scientifiche e limiti documentati. Nessuna importazione dei dati personali del PDF, validazione clinica o certificazione generale degli esportatori dichiarata.


## Architettura 1.2 — 17 ottobre 2026 / software invariato 0.4.1

- WebDAV confermato per Windows/Fedora e Android: TD-59/CLOUD-02, non più candidato.
- Aggiornati ordine degli adapter, criteri desktop/mobile e piano dei prossimi passi; nessuna integrazione o credenziale attivata.


## Architettura 1.1 — 17 ottobre 2026 / software invariato 0.4.1

- Verificate API ufficiali Drive, Dropbox, OneDrive e Nextcloud/WebDAV; documentati consenso OAuth, limiti dell’accesso per cartella, collaborazione con account distinti e sincronizzazione offline.
- Aggiunti CLOUD-01/UI-19 e TD-58: adapter comuni, spike Drive con permessi minimi e due account, migrazione/scambio, test di accettazione; Dropbox condiviso distinto da App Folder.
- Aggiornato il disegno Android: API cloud come obiettivo ordinario, SAF/import-export come alternative. Nessuna integrazione attivata, account collegato o prova autenticata eseguita.

## 0.4.1 — 17 ottobre 2026 / architettura 1.0

- Formalizzati metodi incrementali, convenzioni confermate, formule, finestre, provenienza/versioni, casi di accettazione e scostamenti dal motore corrente. Nessun cambio di algoritmo o ricalcolo dei test in questo step.
- Nome Fuorigiri esteso a pacchetto, comandi, header, variabili, nomi scaricati e bundle/eseguibile; riconoscimento di archivi e canali precedenti senza modificare identità o chiavi. Superata la precedente scelta UI-16.
- Aggiunto sviluppo Android TD-57/AND-01–05, dopo consolidamento incrementale desktop e prima di Sprint breve/Wingate; proposta architetturale, limiti del cloud su Android, UI-18 e criteri di collaudo.
- Aggiornati requisiti, decisioni, architettura e guida di prova. I nuovi metodi specialistici e l’app Android non sono ancora implementati.


## Software 0.4.0 / architettura 0.9 — 17 ottobre 2026

- TD-45/UI-17: tre percorsi distinti Crea nuova società, Collega tramite invito, Ripristina da backup; selezione automatica e crediti societari fissi conservati.
- TD-46/47/REC-01: backup dati schema 2 con checksum, lettura schema 1, anteprima e ripristino validato/atomico in destinazione nuova. Consultazione senza privilegi, copia indipendente con nuove credenziali e provenienza, oppure recupero originale con file del fondatore cifrato separatamente. Verifica delle firme, password e società; nessun segreto nel normale ZIP dati.
- TD-48: corretta la prima sincronizzazione della società associata ancora vuota; cartella, errori e ultimo scambio visibili.
- TD-49: ruolo/dispositivo correnti visibili, controlli di scrittura in UI/API, elenco pubblico firmato, rinnovo/cambio ruolo con nuovo invito applicabile alla stessa copia; un visualizzatore può gestire l’aggiunta di archivi indipendenti senza ottenere diritti sulla società selezionata.
- TD-50 parziale: revoca conservativa con hash esatti degli eventi già acquisiti; restano da sviluppare audit completo, portachiavi e rotazione del canale in INC-11.
- Ripristini e creazioni pubblicati solo a operazione completa; percorsi occupati/sovrapposti rifiutati. Ridotto il nome temporaneo degli allegati per evitare MAX_PATH su Windows.
- Aggiunte 13 prove automatiche (45 totali) e guida SOCIETA_BACKUP_E_ACCESSI.md; collaudo GUI su fixture sintetiche. Nessun nuovo motore di analisi dell’incrementale o dei test successivi.


## Architettura 0.8 / requisiti — 17 ottobre 2026

**Tipo: aggiornamento documentale; software invariato alla 0.3.0.** Recepita la richiesta di registrare le osservazioni sugli accessi e confermare il perimetro dei prossimi sviluppi.

- TD-45–50: distinti creazione società, collegamento con invito e ripristino ZIP; registrati ripristino dati mancante, recupero identità del fondatore separato, difetto della prima sincronizzazione con archivio vuoto, gestione comprensibile di operatori/dispositivi/ruoli e limiti della revoca offline. Scelte UI-17 e REC-01.
- TD-51 / INC-01–11: tutte le lacune per la copertura completa dell'incrementale diventano requisiti confermati da implementare, comprese priorità P2, scambi gassosi nell'incrementale e tutti i punti di consolidamento operativo/distributivo. Aggiunti ID stabili e checklist di accettazione; nessuna voce dichiarata completata.
- TD-52–54: fase successiva riservata a Sprint breve / potenza neuromuscolare, Wingate 30 s e Wingate 15 s. Registrato l'uso storico del 15 s nella società, con necessità di ricostruire il protocollo e mantenere separate durate, versioni e confronti; nessuna equivalenza fisiologica o conversione presunta.
- Allineati registro principale, roadmap, decisioni e architettura. Gli altri test rimangono candidati, senza implementazione autorizzata da questa pianificazione documentale.

## Software 0.3.0 / architettura 0.7 — 17 ottobre 2026

- Nome Fuorigiri Performance Lab in UI, finestra e report; dati e identificatori tecnici compatibili.
- Selettore Società unico, gestione società globale e pagine archivio/storici riordinate; dialoghi opachi con blocco dello scorrimento sottostante.
- Nomi delle metriche leggibili, unità e aggregati con media/mediana; report storico sulla metrica/statistica selezionata.
- Protocollo d'archivio senza step, test manuale senza FIT, nome figlio ereditato dalla categoria.
- Contratto CSV con campi richiesti/facoltativi e controlli su intestazioni, righe e valori mancanti; import a lotti con anteprima e commit atomico.
- PDF uniformati con blu societario, tabelle compatte, logo e attribuzione fissa nel footer di tutte le pagine; nuova versione della cache report.
- Quattro FIT simulati riproducibili dagli ERG originali, CSV sintetici e demo costruita dai medesimi file; sei nuovi casi automatici.
- Registro TD-30–44, scelte UI-11–16, lacune del motore incrementale e roadmap di sprint/CP/FTP/lattato/VO2 con fonti primarie.


Le versioni dell'architettura sono distinte da quelle del programma. Ogni voce deve indicare data, natura della modifica, motivo e identificatori di requisiti/decisioni. Una modifica documentale non certifica l'implementazione della funzione.

## Software 0.2.0 / Architettura 0.6 — 2026-10-17

**Tipo: implementazione e collaudo locale**, dopo approvazione delle scelte e ripresa del lavoro interrotto.

- Logo originale aggiunto in `frontend/public/branding/`, incluso nel bundle Vite/PyInstaller e nei report. Branding reso fisso su richiesta successiva: «Sviluppato da Luca Bontempi per Progetto Ciclismo - Rodengo Saiano A.S.D.» (TD-02/03/26; UI-02/03). Le società non possono personalizzarlo.
- Implementati modifica profilo, nascita completa facoltativa, categorie/stagioni e anno di categoria, ciclo di vita reversibile di atleti/protocolli e filtri storici (TD-09/10/13/14/24).
- Aggiunti editor protocolli con fasi e versioni, export ERG/JSON e tabelle ordinabili (TD-08/11/12). Confronto grafico delle differenze ancora futuro.
- Import FIT/CSV temporale, lattato/RPE/recupero manuale, coefficienti e riferimenti, proposta ultima antropometria e preset stimati con fonte; revisioni successive di test con campioni e risultati storici (TD-15/21/22/23/29).
- Zone a numero variabile per FC/potenza, confini concordati senza arrotondamento preventivo, tempi validi in zona, report dinamici ed export lungo separato (TD-28; ZONE-01).
- Import CSV dei tre profili con anteprima, riconciliazione ID, errori per riga, commit atomico e riconoscimento duplicati (TD-07). Adapter di colonne arbitrarie ancora futuro.
- Storici per atleta/categoria/anno/stagione/coorte, statistiche per metrica, modalità ultimo test per atleta o tutti i test, variazioni antropometriche e confronto appaiato (TD-04/05/17/18).
- Report MD/PDF di storico con manifest, branding e revisioni; conservazione degli artefatti e download delle versioni precedenti; CSV compatibili più formato esteso (TD-16).
- Workspace separati, inviti cifrati per operatore/dispositivo, ruoli admin/visualizzatore, firma delle operazioni e risoluzione conflitti. Revoca delle scritture propagata allo scambio; limiti di lettura e credenziali locali documentati (TD-19/20).
- Aggiunta infrastruttura IT/EN, selettore GUI e titoli dei report; localizzazione completa delle diagnostiche ancora parziale (TD-06).
- Aggiunta [guida per testare anche la GUI](docs/TESTARE_IL_PROGETTO.md), script server locale, fixture sintetiche FIT/ERG/CSV e istruzioni Vite. Aggiornati README, registro requisiti, decisioni e verifiche.
- Nessuna formula scientifica non concordata introdotta. Nome suite, modelli avanzati di maturazione, modulo anaerobico, portachiavi/recupero, rilascio Fedora e verifiche cloud reali restano esplicitamente aperti.
- Nel collaudo del bundle Windows individuata una DLL ICU di Poppler raccolta dal PATH, incompatibile con Qt. Isolato il PATH del sottoprocesso di build; il PATH del sistema non viene modificato. La verifica del bundle comprende caricamento Qt WebEngine, presenza del logo e avvio/health del backend HTTP. Logging desktop reso indipendente dalla console, con errore di avvio esplicito e test senza stdout/stderr.

## Architettura 0.5 — 2026-10-17

**Tipo: conferme, valutazione allegati e specifica; nessuna modifica funzionale al software.**

- Registrata accettazione delle convenzioni per categorie/stagioni, ciclo di vita, revisioni, aggregazioni per atleta, ruoli e confini della suite.
- Esaminato archivio_test.pdf e aggiunta [specifica storico, zone e branding](docs/archivio/STORICO_ZONE_E_BRANDING.md): nove viste HIST-01–09, fattibilità e prerequisiti, modalità tutti i test distinta dal default per atleta, anno di categoria distinto da stagione/coorte, copertura per metrica e confrontabilità.
- Documentati limiti: soglie storiche stimate da distinguere da misure; nessuna statura disponibile per crescita in altezza; risultati anaerobici importabili come estensione candidata ANA-01, senza assumere approvato un nuovo motore di calcolo. Non copiati dati personali nei documenti di progetto.
- Acquisito il logo fornito dall'utente come riferimento UI-02/03, con colori rilevati nel file e regole d'uso; nessuna modifica all'asset o alla UI.
- Registrate le tabelle originali delle zone e la normalizzazione dei confini confermata dall'utente, incluso il 55% di potenza in Z1 (TD-28/D26). Esempi numerici sintetici e controlli attesi.
- Aggiunto ZONE-01: numero di zone configurabile oltre cinque, indipendente per FC/potenza; schema a lista, editor, rendering ed export esteso dinamici. Cinque zone restano il preset iniziale, non il limite del programma.
- Aggiornati architettura, decisioni e backlog. Verificati collegamenti locali e calcoli degli esempi ai confini; nessun test applicativo necessario per questa modifica documentale.

## Architettura 0.4 — 2026-10-17

**Tipo: documentazione e disegno; nessuna modifica funzionale al software.** Revisione richiesta dopo i commenti dell'utente nella sezione To-Do.

- Trasferiti tutti i 29 commenti in [Requisiti e to-do](docs/REQUISITI_E_TODO.md), riscritti con ID TD-01–29, stato e criteri verificabili; conservata la [trascrizione originale](docs/archivio/COMMENTI_ORIGINALI_2026-10-17.md). Aggiunto SUITE-01 per l'app gemella.
- Registrate le parti già presenti: flusso ERG con codice/step/riscaldamento iniziale e inserimento manuale antropometrico; distinte dalle richieste composte ancora incomplete (TD-01/08/14).
- Esteso il modello con categorie/stagioni, nascita completa facoltativa, ciclo di vita di atleti/protocolli e revisioni manuali dei test (TD-09/10/13/24/29; D20–22).
- Promosso l'import CSV da estensione futura a requisito, distinguendo risultati storici e serie temporali; dettagliato editor/export ERG (TD-07/11/15; D19).
- Integrati lattato, coefficienti, FC pre-test/recupero, RPE e proposte da storico/preset, con provenienza e separazione fra stime e misure; introdotto il contratto delle zone (TD-15/21/22/23/28; D26). Preset numerici e metodi avanzati restano da validare.
- Definiti aggregati, confronti, crescita descrittiva e report di atleta/categoria/stagione con popolazione e revisioni congelate (TD-04/05/16/17/18; D23).
- Aggiornata la collaborazione: archivi e cartelle per società, ruoli admin/visualizzatore e verifica delle scritture ricevute. Esplicitati limiti della revoca offline e differenza fra cifratura e autorizzazione (TD-19/20; D07).
- Aggiunto nell'architettura il registro UI-01–10: branding blu/giallo proposto, logo e crediti, nuovo motto, IT/EN, grafici, tabelle ordinabili, accessibilità e componenti comuni (TD-02/03/05/06/12/25/26; D24).
- Disegnati confini della suite, librerie e contratti condivisi con DB separati; proposti nomi coordinati senza rinominare la preview (SUITE-01; D25).
- Aggiunta [ricognizione dei prodotti](docs/archivio/CONFRONTO_PRODOTTI.md) con fonti ufficiali e candidati separati dai requisiti approvati (TD-27).
- Aggiornati piano e verifiche attese. Verificata la copertura dei 29 commenti, i collegamenti locali dei documenti e la coerenza del registro. Non rieseguiti test applicativi: intervento solo documentale.

## Stato precedente

Il documento di partenza era Architettura 0.3 del 16 ottobre 2026, con preview locale 0.1. Questo changelog viene istituito il 17 ottobre: non ricostruisce retroattivamente un elenco completo di modifiche o rilasci precedenti. Lo stato tecnico precedente resta descritto in [README](README.md), [decisioni](docs/archivio/DECISIONI.md) e [verifiche](docs/VERIFICA.md).


## 20 ottobre 2026 — riallineamento UI della suite

Implementato il consumo di `@cycling-suite/ui` 0.2.2, derivato dall'interfaccia corrente di Fuorigiri 0.10.0: shell/controlli responsive, liste/tabelle/riepiloghi, finestre con testata fissa, focus/Esc e protezione delle modifiche, tempi in secondi/mm:ss. Common è la fonte delle parti condivise; i moduli locali delegano alla libreria. Menu, contenuti e layout specifici, archivi e motori rimangono separati. Aggiornamento locale di sorgenti e dipendenza, senza nuovi installer o pubblicazioni.

## Sorgenti del 1 novembre 2026 — organizzazione delle schede

- Import CSV nelle testate Atleti, Società e gruppi, Test e analisi e nel riquadro Antropometria: solo tracciati pertinenti, con componente/anteprima/conferma esistenti.
- Punto completo Importazioni CSV espandibile in Archivio e scambio; modello/file prima delle istruzioni estese. Allineamento con A Ruota e con i comandi contestuali già presenti in Ammiraglia.
- Testi aggiunti anche in inglese; nessuna modifica a dati, motori, permessi o versioni. Nuovi installer/APK non prodotti.
