# Sync v2, backup scalabili e separazione delle società

Implementazione nei sorgenti, **19 ottobre 2026**. Nessun installer aggiornato e nessun provider reale qualificato da questo intervento. Le prove effettive sono nel [registro verifiche](VERIFICA.md).

## Attivazione e compatibilità

In Archivio e scambio → Condivisione e collaboratori → Formato dello scambio, il fondatore conferma di aver aggiornato tutti i dispositivi e attiva v2. Il prossimo scambio pubblica `format2.json`, firmato dall’autorità della società; i client aggiornati ne verificano firma e società e adottano il formato. Gli inviti successivi riportano il formato attivo.

**Prima aggiornare tutti i collaboratori.** I client precedenti non possono essere aggiornati o fermati a distanza da questo codice: ignorano le nuove pagine e non vedono le nuove modifiche. Il riconoscimento dell’avviso è nei client aggiornati. La compatibilità consiste nella lettura di v1 e v2 da parte della nuova app; non nella lettura di v2 da parte delle vecchie app.

L’attivazione conserva i pacchetti v1 e ripubblica lo storico autorizzato nel formato v2. Non modifica ID, risultati o firme originali. Nessuna cancellazione, compattazione o rotazione implicita; ruoli, revoche e avvisi di rotazione del canale restano applicati prima della pubblicazione. Il passaggio iniziale richiede spazio aggiuntivo perché mantiene v1. Non fare downgrade dopo nuove scritture v2.

## Formato v2

- Allegati e liste grandi del record, inclusi i campioni, separati dall’involucro trasmesso. Gli allegati sono letti progressivamente; le liste JSON passano da uno spool su disco quando necessario.
- Blocchi da 1 MiB cifrati con Fernet. Il nome remoto è un HMAC del contenuto con la chiave del canale: non espone l’hash del contenuto fra società diverse. I descrittori cifrati conservano SHA-256, dimensione e ordine dei blocchi.
- Pagine di massimo 32 eventi con descrittori leggeri, firmate da un certificato admin verificato prima di ricostruire i campi separati. La firma dell’involucro non autorizza da sola le revisioni: firme e revoche degli autori originali vengono comunque controllate. Una correzione della nota può produrre una nuova pagina, ma riutilizza i blocchi del medesimo tracciato. Le pagine parziali possono essere ripubblicate con un nuovo nome immutabile; cresce la sola parte descrittiva.
- Cataloghi checkpoint descrivono le pagine dello storico autorizzato e ne ordinano il bootstrap. L’inventario completo resta un fallback: un indice non autorizza eventi e non sostituisce la verifica delle firme.
- Il ricevente ricostruisce ogni evento originale e verifica firma, certificato, revoca, società, dipendenze e checksum prima di applicarlo. Mantiene gli stessi conflitti e revisioni del formato precedente.
- Ricevute locali per canale evitano di rileggere pagine note. Una pagina non completa non viene acquisita come completata; il tentativo successivo riusa i blocchi già validati. I blocchi cifrati parziali restano nella cache locale `parts/` fino alla ricostruzione verificata dell’oggetto e vengono poi rimossi dalla cache, senza toccare originali o storico. Un file remoto immutabile pubblicato contemporaneamente viene accettato solo se il contenuto decifrato coincide.
- La verifica completa rilegge pagine e blocchi referenziati, anche se già noti. Non è un controllo di tutti i file orfani presenti sul provider.

La separazione riguarda il **formato di scambio**: il database locale conserva attualmente gli eventi canonici e i campioni ricostruiti per mantenere firme e compatibilità con il resto dell’app. Non è stata effettuata una riscrittura fisica delle vecchie revisioni SQLite. La cache `sync-v2/` contiene descrittori locali, non è una copia di recupero né un luogo per credenziali.

### Limiti residui

L’inventario del trasporto è ancora completo, con limite di 100.000 file. Le ricevute sono un cursore locale di acquisizione, non una paginazione remota del provider. Per archivi ulteriormente grandi serviranno inventari remoti paginati, compattazione concordata e una politica per dispositivi offline. Non è stata introdotta garbage collection automatica.

Un blocco è 1 MiB; un oggetto può arrivare al limite di sicurezza di 16 GB, mentre un campo JSON separato è limitato a 80 MB. Le pagine raggruppano al massimo 32 eventi: memoria e firma includono la ricostruzione dei relativi record, non soltanto il blocco. I controlli e l’inventario conservano i limiti del trasporto. Questi valori sono protezioni, non benchmark di produzione.

## Backup v3 ZIP64

In Archivio e scambio → Copia dell’archivio scegliere **Scarica backup scalabile · v3**. Il backup dati è non cifrato e non contiene chiavi o privilegi del fondatore; il recupero accessi cifrato rimane un file separato.

Il formato contiene uno snapshot SQLite consistente, gli oggetti, un inventario JSONL con hash/dimensioni e un piccolo manifest. Scrittura e controllo dei contenuti avvengono a blocchi; l’inventario di verifica è su SQLite temporaneo. Il database caricato viene letto con schema non attendibile disabilitato e viene ricostruito nelle tabelle note: non viene eseguito SQL fornito dal backup.

Prima della pubblicazione si controllano integrità, dipendenze, oggetti storici e schema. La pubblicazione finale del file non sovrascrive un backup esistente. Il ripristino verifica tutto prima di registrare la nuova società e lavora in una cartella temporanea: un errore non rende visibile un archivio parziale.

Limiti v3: **64 GB compressi, 256 GB espansi, 1.000.000 di file dati**. Serve spazio per snapshot, verifica, copie di staging e destinazione: il formato evita l’accumulo dei payload in RAM, non la necessità di spazio su disco. La directory centrale ZIP continua a occupare memoria proporzionale al numero di file. Non è un formato multipart e l’export interrotto va ricominciato.

Il backup legacy v1/v2 resta leggibile e scaricabile, con i suoi limiti precedenti di 100 MB ZIP, 1 GB espanso e 10.000 allegati. Non si accetta un vecchio ZIP sovradimensionato fingendo che sia v3: aprire l’archivio originale con l’app aggiornata ed esportarlo nuovamente.

### File molto grandi su desktop

Il server invia il download v3 da file, ma il normale comando di download del frontend può ancora accumulare il file nel browser. Per archivi grandi usare **Salva direttamente su disco**, con un nuovo percorso assoluto `.zip` fuori dalla cartella dati della società, oppure la CLI. Su Android il percorso del server incorporato non equivale alla destinazione SAF: la procedura nativa per backup molto grandi richiede collaudo e il salvataggio diretto non viene mostrato.

Le tre modalità di ripristino rimangono consultazione, copia indipendente e recupero originale con credenziali. I conflitti pendenti sono conservati anche nelle copie indipendenti, ricollegati agli eventi firmati dalla nuova autorità. L’anteprima del caricamento e il commit elaborano il file su disco; un errore lascia il file in staging per ritentare, senza modificare società già presenti.

## Separare società legacy

Aprire l’archivio precedente, poi Archivio e scambio → Copia dell’archivio → **Separa una società da un archivio precedente**. Analizzare, scegliere la società e il nuovo fondatore, quindi creare la copia indipendente. Per partire da un backup multi-società si può prima ripristinarlo in consultazione e poi separarlo.

L’anteprima ricostruisce l’appartenenza usando tutte le revisioni e le dipendenze, non soltanto la società selezionata nella schermata. L’impronta dell’archivio deve coincidere al commit. Riferimenti fra società diverse, riferimenti mancanti, record trasferiti fra società e record non attribuibili bloccano l’estrazione: correggere prima l’archivio, senza inventare appartenenze né omettere record silenziosamente. Non c’è ancora un editor di assegnazione per casi legacy ambigui.

L’estrazione usa uno snapshot consistente. Conserva ID e revisioni dei dati selezionati, tutte le loro versioni, i conflitti e soltanto gli oggetti richiesti da quelle versioni. La nuova autorità firma lo storico importato con l’hash dell’evento di origine come provenienza. Genera nuove chiavi, un nuovo canale v2 e richiede nuovi inviti; non eredita accessi o configurazione cloud. L’originale e le altre società non vengono modificati. Ripetere la procedura per ciascuna società; le copie rappresentano lo stato al momento dell’estrazione.

## Comandi e prove riproducibili

Da un ambiente di sviluppo predisposto:

```powershell
.venv/Scripts/python.exe scripts/archive_tools.py --data .local/mia-app --workspace ID-SOCIETA backup --out F:/Backup/fuorigiri-v3.zip
.venv/Scripts/python.exe scripts/archive_tools.py --data .local/mia-app inspect --file F:/Backup/fuorigiri-v3.zip
.venv/Scripts/python.exe scripts/archive_tools.py --data .local/mia-app restore --file F:/Backup/fuorigiri-v3.zip --operator "Nuovo fondatore"
.venv/Scripts/python.exe scripts/archive_tools.py --data .local/mia-app split-preview
.venv/Scripts/python.exe scripts/archive_tools.py --data .local/mia-app split --organization ID-SOCIETA --source-hash IMPRONTA-ANTEPRIMA --operator "Nuovo fondatore"
```

`--data` è la radice dell’app, `--workspace` seleziona la società gestita e si omette per il legacy. La CLI restore crea soltanto copie indipendenti; per recupero originale usare il flusso nell’interfaccia con il file accessi. I percorsi sono esempi, non cartelle create automaticamente per l’utente.

```powershell
.venv/Scripts/python.exe -m pytest tests/test_sync_v2.py tests/test_backup_stream_migration.py tests/test_recovery.py tests/test_workspaces.py -q
.venv/Scripts/python.exe scripts/verify_storage_v2.py --data .local/qa-streaming-nuovo --large
```

La seconda prova genera 101 MB sintetici non comprimibili, esporta oltre il limite precedente, verifica e ripristina realmente, confronta SHA-256 e registra dimensioni, tempi e picco delle allocazioni Python. Richiede una cartella nuova e circa 1 GB libero; non usa archivi reali. Il picco Python non comprende tutte le allocazioni native o la cache del sistema operativo. Nessuna prova locale equivale a una qualificazione di 64/256 GB o di un milione di file.
