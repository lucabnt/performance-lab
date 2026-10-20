# Società, sincronizzazione e dimensioni — 19 ottobre 2026

## Aggiornamento: v2 e backup v3 implementati

Il [contratto attuale](SYNC_V2_E_BACKUP.md) descrive blocchi cifrati riutilizzabili e pagine v2, attivazione e compatibilità, ZIP64 streaming v3 e separazione assistita delle società legacy. Le misure v1 sotto restano il confronto storico, non una stima delle nuove pubblicazioni. Il database locale conserva i record canonici; inventario remoto completo e assenza di garbage collection rimangono limiti. Le procedure non riscrivono né cancellano automaticamente archivi e pacchetti precedenti.

I limiti ZIP 100 MB/1 GB/10.000 oggetti riportati sotto si applicano al **formato legacy**. V3 usa elaborazione su disco con protezioni 64 GB compressi/256 GB espansi/1.000.000 file dati e richiede spazio temporaneo. La separazione assistita è ora disponibile per riferimenti coerenti; i casi ambigui vengono bloccati e segnalati. Prove in [VERIFICA.md](VERIFICA.md).

## Che cosa viene sincronizzato

L'unità è **l'archivio della singola società**, non tutto il programma e non il gruppo selezionato nel grafico. Ogni società creata con Gestisci società ha SQLite/allegati, identità/chiave, inviti/ruoli, configurazione di connessione e credenziali separati. Le credenziali sono indicizzate dal percorso dell'archivio. Il canale remoto deriva dalla chiave della società: due società non condividono il canale solo perché usano lo stesso account o la stessa cartella padre.

Su Android il worker può eseguire più sync in background, ma invoca separatamente ogni archivio configurato con i suoi accessi. Non produce un archivio comune. Un invito di A non dà accesso a B. **Con collaboratori diversi configurare cartelle/condivisioni cloud diverse**: le ACL del provider sono distinte dall'autorizzazione interna Fuorigiri. Il nome opaco del canale e la cifratura non sostituiscono i permessi cloud; alcuni metadati di controllo degli accessi sono firmati ma non cifrati.

L'eccezione era l'archivio legacy o un backup ripristinato con più società: la tendina mostrava una società, ma lo scambio riguardava tutto quel database. Ora sync, inviti e configurazione sono bloccati per questi archivi; il controllo avviene prima della pubblicazione. Non sono stati divisi o cancellati dati. Per migrare serve un'estrazione per società che conservi riferimenti e storia; il semplice filtro sulla vista non basta.

## Non esiste un solo file società

- `archive.sqlite`: record correnti, revisioni, conflitti e registro locale.
- `objects/`: FIT/CSV originali, tracciati decodificati, PDF/MD e allegati deduplicati **localmente per hash**.
- Cartella/canale cloud: pacchetti cifrati immutabili e controlli firmati. Non è il database SQLite aperto sincronizzato dal client cloud.
- Backup ZIP: copia portabile compressa. La dimensione ZIP non è quella del canale cloud, già cifrato e poco comprimibile.

## Misure effettive

Unità decimali: MB = 1.000.000 byte, GB = 1.000 MB. Dati sintetici, non misure su società reali.

La società Aurora del corpus esistente contiene 150 record test, 22 con campioni, e 424 revisioni complessive. SQLite circa **5,20 MB**, allegati **1,68 MB**, directory complessiva **6,88 MB**. I pacchetti v1 corrispondenti sono stimati in **7,95 MB**; il più grande circa **1,18 MB**. Questa demo contiene molti riepiloghi manuali: non va usata da sola per dimensionare anni di FIT.

Modelli sintetici: un test incrementale di 60 minuti più 3 minuti di recupero, potenza/FC/cadenza, originali e tracciato decodificato, nessun PDF/gas/foto. Seconda revisione: solo una nota modificata, stesso tracciato.

| Modello | Directory locale, 1 revisione | Canale v1, 1 revisione | Canale v1, 2 revisioni | Backup ZIP, 2 revisioni |
|---|---:|---:|---:|---:|
| 1 Hz, 3.781 campioni | 0,82 MB | 0,82 MB | 1,63 MB | 0,12 MB |
| 5 Hz, 18.901 campioni | 4,28 MB | 4,63 MB | 9,26 MB | 0,33 MB |

Nel modello a 1 Hz la directory locale con due revisioni è circa 1,08 MB, a 5 Hz circa 5,59 MB. Il ZIP comprime bene i dati sintetici ripetuti; PDF, rumore dei sensori, più canali e formati differenti possono comprimersi meno. Questi numeri non sono un tetto garantito.

### Proiezioni, non benchmark di produzione

Usando il modello a 1 Hz, senza aggiungere PDF/MD/gas e senza considerare versioni mantenute dal provider:

| Società / periodo | Test | Canale v1 con 1 revisione/test | Con 2 revisioni/test |
|---|---:|---:|---:|
| 50 atleti × 4 test/anno × 10 anni | 2.000 | circa 1,6 GB | circa 3,3 GB |
| 100 atleti × 6 test/anno × 10 anni | 6.000 | circa 4,9 GB | circa 9,8 GB |

A 5 Hz gli stessi 2.000 test valgono circa 9,3 GB con una revisione o 18,5 GB con due. Sprint/Wingate brevi occupano meno se il file contiene solo la prova; una lunga registrazione di riscaldamento/recupero può dominare il volume. I PDF/MD si aggiungono: anche 0,2–1 MB di allegati per test sono ulteriori 0,4–2 GB su 2.000 test, prima dell'overhead della sync. Gli originali non vanno eliminati per far tornare queste stime.

## Problemi reali del formato v1 e mitigazioni attuali

Ogni revisione conserva il record completo, compresi i campioni. Ogni pacchetto incorpora di nuovo gli allegati necessari, pur già presenti in pacchetti precedenti; il base64 degli allegati e dell'involucro aggiunge spazio. La deduplicazione locale non implica deduplicazione dei pacchetti remoti. Anche cambiare una nota può quindi pubblicare quasi quanto il test originale.

È stato eliminato un costo evitabile: la sync ordinaria gestita non riscarica i pacchetti il cui ID immutabile è già presente nel database locale. Legge ancora l'inventario e i controlli accessi/revoche; un dispositivo nuovo acquisisce l'intera storia. **Verifica completa del canale** rilegge e verifica anche i pacchetti noti. Questo è il controllo da usare per rilevare alterazioni remote successive: la sync incrementale non promette un audit completo del contenuto remoto. I file non vengono cancellati né compattati automaticamente; il protocollo sul cloud resta compatibile v1.

## Limiti da affrontare prima della crescita

- Pacchetto di scambio: 80 MB; inventario: 100.000 file.
- Ripristino ZIP: 100 MB compressi, 1 GB espanso, fino a 10.000 allegati. L'export ora rifiuta esplicitamente un backup che il ripristino non accetterebbe. Non è ancora disponibile un backup scalabile in parti/streaming: è una priorità, non un problema risolto alzando arbitrariamente il limite.
- Backup e verifica lavorano oggi in memoria; telefoni e PC modesti richiedono streaming e limiti ragionati.
- I costi di banda/operazioni dipendono dal provider. La sync è un'applicazione offline first con revisione/conflitti su object storage, non un database distribuito che riceve queste proprietà automaticamente da Drive.

## Strada più efficiente

Mantenere una società per archivio e separare i permessi cloud. Introdurre poi v2 con campioni referenziati una volta, oggetti cifrati immutabili identificati da hash e riutilizzabili fra revisioni, pacchetti di soli metadati, indici/cursori e snapshot per il primo collegamento. Aggiungere backup streaming/in parti e migrazione assistita dei legacy multi-società. Conservare lettura v1 e pianificare esplicitamente il passaggio di tutti i dispositivi; non cambiare silenziosamente il formato né cancellare la storia dei dispositivi offline.

## Misurare il proprio archivio

```powershell
.venv/Scripts/python.exe scripts/measure_archive_size.py --data ".local/workspaces/ID-SOCIETA" --out output/misure-societa.json
```

Usare il percorso mostrato nelle informazioni della società. Il comando apre SQLite in sola lettura, non legge le chiavi e non si collega al cloud; stima i pacchetti dal formato e dalle dimensioni degli allegati. Riporta anche oggetti mancanti e pacchetti stimati oltre 80 MB. La stima è verificata da un test confrontando i byte con veri pacchetti cifrati.

Risultati locali di questo collaudo: `output/misure-archivio-aurora.json` e `output/misure-scenari-sync.json`. Non includono chiavi, nomi di atleti o contenuti dei file.
