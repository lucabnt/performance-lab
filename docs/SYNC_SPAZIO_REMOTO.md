# Spazio occupato dallo scambio remoto — SYNC-SPAZIO-01

**Stato al 20 novembre 2026:** fasi 0 e 1 **implementate nei sorgenti e verificate localmente** (test automatici, misure su archivi sintetici, pannello provato nella GUI web su un archivio QA nuovo con scambio in cartella). Fasi 2 e 3 restano una proposta. Nessun EXE/APK ricompilato; nessun archivio reale o provider WebDAV analizzato. Contratto in [SYNC_V2_E_BACKUP.md](SYNC_V2_E_BACKUP.md), prove in [VERIFICA.md](VERIFICA.md).

**Nome del formato:** resta **v2**. La fase 1 cambia cosa pubblica un dispositivo, non il formato delle pagine (`schema: 2`): i client v2 già distribuiti leggono le pagine nuove senza avvisi né nuove attivazioni. Il nome v3 è riservato a un cambio di formato incompatibile, come la compressione della fase 3.

## Segnalazione

L’utente riferisce circa 50 MB su WebDAV per un archivio senza FIT, solo con valori storici, e chiede perché. L’analisi ha trovato cause diverse a seconda del formato di scambio attivo. La v2 si attiva solo su conferma esplicita del fondatore; senza l’avviso firmato `format2.json` la società usa ancora la v1. Il primo passo è quindi capire quale formato e quali file occupano lo spazio.

## Cause individuate nel codice

### Formato v1 (predefinito)

Un file `<id-evento>.ctsync` per ogni revisione (`sync.py`). La crescita è lineare, ma con fattori costanti alti:

- ogni revisione contiene il record completo, anche se cambia un solo campo;
- negli archivi gestiti ogni evento include certificato, firma del certificato e firma: nella misura circa 490 byte su 1.250 (≈40%);
- nessuna compressione; Fernet codifica in base64 (+33%);
- gli allegati sono codificati in base64 dentro il JSON e poi di nuovo da Fernet: ≈1,78× la dimensione originale;
- i report esportati (`save_report`) sono record con il file come allegato. Il riuso avviene per chiave, ma la chiave contiene le revisioni sorgente: un nuovo export dopo una modifica dei dati produce un nuovo PDF/CSV sincronizzato.

### Formato v2

Quando è attiva, `exchange_v2` (`sync_v2.py`) moltiplica lo spazio oltre ai fattori precedenti:

| Causa | Meccanismo | Effetto |
|---|---|---|
| C1 — coda ripubblicata | Le pagine raggruppano 32 eventi dello storico locale; il nome è un HMAC del contenuto. Ogni scambio con nuovi eventi crea una nuova versione dell’ultima pagina incompleta, e le versioni precedenti restano. | Fino a 32 copie crescenti per pagina (≈16× in media se si sincronizza a ogni modifica). La sync automatica (SYNC-AUTO-01) ogni ~10 s rende frequente questo caso. |
| C2 — cataloghi | A ogni scambio con l’elenco delle pagine cambiato viene pubblicato un `checkpoint2-*.ctindex` con tutte le pagine. | Crescita quadratica nel numero di scambi. |
| C3 — un editore per dispositivo | Ogni admin pubblica **l’intero storico** locale, compresi gli eventi ricevuti, in pagine firmate con il proprio certificato, quindi con nomi diversi da quelle degli altri. | Lo storico moltiplicato per il numero di dispositivi admin. |
| C4 — v1 conservata | L’attivazione ripubblica lo storico in v2 senza cancellare la v1 (scelta documentata). | Somma dei due formati. |
| C5 — bootstrap | Un nuovo dispositivo scarica tutte le pagine elencate, comprese quelle superate. | Il traffico cresce come lo spazio. |

La firma Ed25519 è deterministica e la cache `sync-v2/` conserva i descrittori, quindi le pagine piene già pubblicate non cambiano nome a ogni scambio. Il problema riguarda la coda, i cataloghi e i dispositivi diversi.

### Misure (simulazioni locali, 20 novembre 2026)

Record sintetico di test storico con 10 step, senza campioni né allegati.

| Scenario | Eventi locali | Remoto | File |
|---|---|---|---|
| Archivio non gestito, 320 eventi, un solo scambio | 206 KB | 294 KB | 10 pagine, 1 catalogo |
| Stesso archivio, scambio dopo ogni evento | 206 KB | 5.091 KB (×17) | 320 pagine, 320 cataloghi |
| Archivio gestito, 200 eventi in blocco, un admin | 232 KB | 327 KB | 7 pagine |
| Poi 20 modifiche alternate fra due admin con scambio | 254 KB | 1.261 KB | 33 pagine, 22 cataloghi |

Attivazione su un archivio gestito con 300 eventi in v1 (499 KB remoti): la v1 resta e la v2 aggiunge 488 KB. Poi 40 modifiche singole, ognuna seguita da uno scambio, aggiungono 1.146 KB in v2 contro 66 KB nella stessa sequenza rimasta in v1; il primo scambio di un secondo admin aggiunge altri 575 KB. Senza allegati la v2 attuale non riduce lo spazio. Il suo vantaggio è nei file (pagine da 32 eventi invece di un file per evento) e negli allegati grandi (blocchi deduplicati, una sola codifica base64).

Nel caso con due admin 221 eventi distinti sono presenti sul server in 764 copie; ciascun admin ha pubblicato 382 eventi. Comprimendo con zlib il contenuto in chiaro delle pagine si ottiene un rapporto di 6,7, gonfiato dalla ripetizione del certificato in ogni evento.

## Diagnosi dell'archivio segnalato — 20 novembre 2026

Analisi eseguita dall'utente con il pannello della fase 0 sull'archivio reale (formato v2 attivo): **66,9 MB in 443 file**.

| Contenuto | Dimensione |
|---|---|
| Pacchetti v1 (365) | 45,6 MB, di cui **10 report: 44,7 MB** (PDF in base64 dentro Fernet) |
| Blocchi v2 (48) | 19,5 MB: gli stessi PDF ripubblicati dopo l'attivazione |
| Pagine v2 (24) | 1,7 MB: 365 revisioni in 730 copie, una per ciascuno dei due dispositivi |
| Tutti gli altri record v1 | circa 0,9 MB (89 test, 147 misure, 36 atleti, appartenenze, protocolli, gruppi) |

La causa principale non è la sync ma i **report esportati**: ogni export con input diversi salva un nuovo record con il file allegato, che viaggia con lo scambio (circa 2,5 MB per PDF, soprattutto grafici PNG a 150 dpi). La duplicazione fra dispositivi (C3) qui vale circa 0,9 MB. Decisione dell'utente: sincronizzare solo i metadati dei report (REPORT-LOCALE-01, sotto).

## Report: solo metadati nello scambio (REPORT-LOCALE-01, implementato)

Richiesta dell'utente: «sincronizzare solo i metadati del report, senza il file: il PDF resta sul dispositivo che l'ha creato. Mi sembra questa la strada».

- I report salvati da ora in poi (`save_report`) registrano nel record firmato solo i metadati, `file_sha256` e `file_bytes`, senza la lista `objects`. Gli scambi v1 e v2 trasferiscono solo gli oggetti di quella lista, quindi il file non viaggia; resta nella cartella `objects/` del dispositivo che l'ha creato, inclusa nei suoi backup v3. Nessun cambio di protocollo né di formato.
- Elenco «Report conservati»: per ogni report indica se il file è su questo dispositivo o solo su quello di chi l'ha salvato (nome dal certificato che ha firmato la revisione). Il download di un file assente restituisce un messaggio chiaro; i report di un singolo test vengono semplicemente rigenerati.
- I report salvati prima restano invariati e continuano a viaggiare con lo scambio; per loro un allegato mancante resta un errore. La separazione delle società copia anche i file dei report presenti sul dispositivo.
- Limiti: i client precedenti mostrano i report nuovi ma non ne scaricano il file, e il report di un test con un record nuovo senza file locale li fa fallire finché non vengono aggiornati. Lo spazio già occupato dai report vecchi si recupera solo con la fase 2. La modifica **non è nei binari di `v0.10.0-alpha.1`** (commit `8e9de2d`).

## Vincoli

- Nessuna perdita di eventi, firme originali, revoche, conflitti o allegati. Sync non è backup: prima di qualsiasi cancellazione remota va proposto un backup v3.
- Le pagine v2 già pubblicate devono restare leggibili e i client v2 già distribuiti devono continuare a leggere ciò che pubblicano i client nuovi, dove il formato non cambia.
- Nessuna cancellazione automatica o implicita ([architettura](../ARCHITETTURA_PROPOSTA.md), [prossimi passi](PROSSIMI_PASSI.md)): ogni rimozione richiede un comando esplicito, una politica per i dispositivi offline e una verifica prima di cancellare.
- Nessuna rete sotto `Runtime.lock` su Android; job, avanzamento e ritentativi passano dal motore `sync_jobs` esistente.
- WebDAV e cartella sono i trasporti supportati (PERIMETRO-01). Drive, Dropbox e OneDrive restano sperimentali: le fasi che cancellano non vengono offerte su questi provider.

## Fase 0 — Diagnosi in sola lettura (implementata)

In Archivio e scambio → Condivisione e collaboratori → **Spazio occupato dallo scambio**, pulsante «Analizza lo spazio» (`sync_space.py`, `SyncSpace.tsx`). Gira come job di dispositivo separato dalla sync (`POST /api/v1/sync/space/start`, `GET /api/v1/sync/space/job`, stato in `sync-space-job.json`), quindi su Android la rete non passa dalla richiesta. Disponibile anche ai visualizzatori: non firma, non pubblica, non scrive sulla destinazione e non tocca lo storico locale.

Scarica e decifra pacchetti v1, pagine, cataloghi e controlli. Per i blocchi referenziati la dimensione si ricava dai descrittori delle pagine (lunghezza esatta del token Fernet), quindi non vengono scaricati; i blocchi non referenziati invece sì. I nomi di pagine e cataloghi vengono confrontati con il loro indirizzo HMAC; le firme non vengono verificate, perché nulla viene accettato. Mostra:

- totale, file e dimensione per categoria (pacchetti v1, pagine, cataloghi, blocchi, controlli e avvisi);
- v1: revisioni, quante sono presenti anche in v2, ripartizione per tipo di record, allegati contenuti;
- v2: revisioni distinte e copie, dimensione stimata di una copia consolidata, pagine per dispositivo editore;
- spazio ridondante (pagine duplicate rispetto alla copia consolidata, cataloghi precedenti all'ultimo, blocchi non referenziati), file illeggibili o alterati e blocchi mancanti.

Il risultato resta locale al dispositivo. Il comando per recuperare lo spazio non esiste ancora (fase 2): il pannello lo dice esplicitamente.

**Accettazione (verificata):** con v1 e v2 nella stessa cartella i conteggi coincidono con il journal locale e il totale coincide con i byte su disco; la cartella resta identica (hash prima e dopo); una pagina rinominata è segnalata come alterata senza interrompere l'analisi; duplicati e blocchi orfani vengono contati.

## Fase 1 — Pubblicare senza duplicare (implementata, nessuna cancellazione)

Il formato delle pagine resta `schema: 2`, quindi i lettori v2 già distribuiti leggono tutto.

1. **Prima la ricezione, poi la pubblicazione.** Le pagine degli altri dispositivi vengono lette e verificate prima di decidere cosa pubblicare. Gli eventi ricevuti dai pacchetti v1 entrano in v2 una sola volta, pubblicati dal primo admin che li trova scoperti.
2. **Indice di copertura locale** per canale (`sync-v2/coverage-<canale>.json`): nome pagina → ID degli eventi, per le pagine pubblicate da questo dispositivo e per quelle lette con tutti gli eventi autenticati. Un evento è *coperto* se compare in una pagina presente nell'elenco attuale del trasporto; le pagine assenti vengono ignorate e rimosse dall'indice, quindi una nuova destinazione riceve tutto lo storico. È un cursore di pubblicazione, non un'autorità.
3. **Pagine delta:** si pubblicano solo gli eventi locali autenticati e non coperti, in ordine locale, in pagine nuove da massimo 32. Le pagine pubblicate non vengono riscritte e un admin non ripubblica con la propria firma eventi già presenti.
4. **Nessuna migrazione esplicita.** Raggruppamento e firme Ed25519 sono deterministici: al primo scambio dopo l'aggiornamento un dispositivo ricalcola le stesse pagine che aveva già pubblicato e non carica nulla di nuovo, salvo gli eventi arrivati dopo l'ultimo scambio.
5. **Cataloghi geometrici:** un nuovo checkpoint solo quando le pagine note sono cresciute almeno della metà (minimo 32) dall'ultimo, o se manca. Ogni catalogo elenca tutte le pagine, quindi lo spazio totale dei cataloghi resta proporzionale alle pagine. L'inventario completo resta il fallback.
6. **Ricevute ripulite** dai nomi non più elencati; le pagine appena pubblicate entrano nelle ricevute senza essere riscaricate.
7. **Blocchi ripristinati:** per le pagine che pubblica, il dispositivo ricorda i blocchi referenziati e, se uno sparisce dal server, lo ricarica ricostruendo la pagina, come faceva la ripubblicazione completa.

I client precedenti, se admin, continuano a ripubblicare il proprio storico a ogni scambio, ma con nomi stabili: lo spreco smette di crescere del tutto solo quando tutti gli admin sono aggiornati. I file già presenti sul server restano: lo spazio accumulato prima dell'aggiornamento si recupera solo con la fase 2.

**Accettazione (verificata):** una sync per modifica pubblica ogni evento una sola volta e non riscrive pagine; un secondo admin non ripubblica lo storico ricevuto, né da pagine v2 né da pacchetti v1; dopo l'aggiornamento le pagine già pubblicate non vengono ricaricate; una nuova destinazione riceve tutto lo storico; un blocco rimosso viene ripristinato; i test v2 esistenti (firme, revoche, conflitti, ripresa dopo interruzione, pagine contraffatte) restano verdi.

### Misure dopo la fase 1 (simulazioni locali, 20 novembre 2026)

Stessi scenari e stessi dati della tabella iniziale.

| Scenario | Prima | Dopo |
|---|---|---|
| 320 eventi, scambio dopo ogni evento (non gestito) | 5.091 KB | 393 KB (scambio unico: 294 KB) |
| 40 modifiche singole dopo l'attivazione (gestito) | +1.146 KB | +99 KB |
| Primo scambio di un secondo admin | +575 KB | +0 KB |
| Due admin, 20 modifiche alternate: copie per 221 eventi | 764 | 221 |

## Fase 2 — Consolidamento esplicito (con cancellazione)

Comando del **fondatore**, mai automatico. Prerequisiti:

- metodo `delete(name)` nei trasporti cartella e WebDAV, nel core comune con nuova versione e adattatori Fuorigiri; i provider sperimentali non lo offrono e il comando risulta non disponibile;
- avviso firmato dall’autorità (`exchange-policy.json`, modellato su `format2.json`) che dichiara la fase 1 attiva, dopo conferma del fondatore che tutti i dispositivi admin sono aggiornati;
- backup v3 recente proposto prima dell’avvio.

Procedura in due tempi:

1. **Piano:** il job legge e verifica tutte le pagine (inclusi i v1, se richiesto), scrive pagine consolidate da 32 eventi in ordine stabile firmate dal fondatore, le rilegge e le verifica dopo l’upload. Pubblica poi un piano firmato `compaction-<n>.json` con pagine consolidate, pagine e cataloghi superati con gli ID evento coperti, blocchi senza riferimenti, pacchetti v1 coperti, data e attesa minima.
2. **Esecuzione**, solo dopo l’attesa (proposta: 30 giorni, minimo 7): riverifica che ogni evento delle pagine superate sia in pagine consolidate presenti e integre e che i blocchi candidati siano ancora senza riferimenti in **entrambe** le osservazioni. Solo allora cancella. L’operazione è idempotente e ripetibile dopo un’interruzione; ogni cancellazione finisce nel registro di audit locale.

Dispositivi offline: gli eventi che conoscono ma che non hanno pubblicato restano nel loro database locale e vengono pubblicati come non coperti al rientro. Quelli già presenti arrivano dalle pagine consolidate e vengono riconosciuti come duplicati identici. Al rientro serve solo più traffico, nessun ripristino. Le revisioni locali non vengono mai riscritte. Un admin con client precedente alla fase 1 ricaricherebbe le pagine cancellate: per questo serve l’avviso con la conferma del fondatore.

**Accettazione:** su copie QA con v1+v2 e due admin, dopo il consolidamento ogni dispositivo, compreso uno rimasto offline durante l’intera procedura, converge allo stesso stato, con conflitti e revoche invariati. Un upload in corso durante il piano non perde blocchi. Un’interruzione tra le cancellazioni si riprende senza errori. Su provider sperimentali il comando non è disponibile.

## Fase 3 — Compressione (opzionale, nuovo formato)

Pagine `schema: 3` e campi JSON separati compressi (zlib) prima di Fernet; certificato dell’editore degli eventi deduplicato per pagina e reinserito prima della verifica, come avviene oggi per i campi separati, così che l’evento firmato resti identico byte per byte. Richiede un nuovo avviso di formato con la stessa procedura della v2, perché i client precedenti non leggono le pagine nuove. Gli allegati già compressi (PDF) non si comprimono. Rischio di attacchi basati sulla lunghezza compressa trascurabile: le pagine non mescolano segreti con contenuti scelti da terzi. Va comunque rivalutato in revisione.

## Decisioni aperte per l’utente

1. Fasi 0 e 1 approvate e implementate il 20 novembre («Procedi con 0 e 1»). Resta da decidere se procedere con la fase 2 e/o la 3, dopo la diagnosi sull'archivio reale.
2. Attesa del consolidamento (proposta 30 giorni) e se includere i pacchetti v1 coperti.
3. Report esportati: deciso il 20 novembre dopo la diagnosi, solo metadati nello scambio (REPORT-LOCALE-01, sopra).
