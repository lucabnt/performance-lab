# Società, backup e accessi — guida 0.4

17 ottobre 2026. Flusso locale della preview Fuorigiri Performance Lab 0.4. Gli accessi sono associati all'operatore su un dispositivo; non esiste un account online con login remoto. La password dell'invito protegge il file JSON, non è una password da inserire ogni volta che si apre il programma.

Backup scalabile v3 e separazione dei legacy multi-società sono ora disponibili: [guida corrente](SYNC_V2_E_BACKUP.md). Le tre modalità di ripristino sotto restano valide; i limiti dei vecchi ZIP non descrivono v3.

## Scegliere l'operazione giusta

Aprire **Gestisci società**, accanto al selettore laterale. I tre percorsi sono separati:

| Percorso | Quando usarlo | Cosa serve | Risultato |
|---|---|---|---|
| Crea nuova società | Si parte da zero | Nome società e nome del fondatore | Archivio vuoto, fondatore locale e nuove credenziali. Nessuna password d'invito richiesta. |
| Collega tramite invito | La società è già usata su un altro PC | Invito JSON personale e password ricevuti dal fondatore | Stessa società, con il ruolo assegnato. Prima sincronizzazione disponibile subito, anche senza record locali. |
| Ripristina da backup | Si devono recuperare dati da uno ZIP | Backup dati; altri elementi dipendono dalla modalità scelta | Anteprima e destinazione nuova, senza sovrascrivere archivi già presenti. |

Il programma seleziona automaticamente la società appena aggiunta. La cartella locale facoltativa deve essere vuota e separata dalla cartella di scambio cloud; lasciandola vuota il programma sceglie il percorso. L'archivio precedente rimane accessibile dal selettore.

## Collegare un collaboratore o un secondo PC

1. Sul PC fondatore selezionare la società e aprire **Archivio e scambio → Condivisione e collaboratori**.
2. Indicare nome operatore/dispositivo, ruolo e password dell'invito (almeno 12 caratteri), quindi **Scarica invito cifrato**. Usare un invito distinto per ogni dispositivo.
3. Comunicare file e password separatamente. Configurare sul PC fondatore una cartella condivisa disponibile offline, quindi premere **Scambia modifiche** per pubblicare i dati.
4. Sul secondo PC usare **Gestisci società → Collega tramite invito**, caricare il JSON e inserire la password. Il backup ZIP non sostituisce l'invito.
5. La società inizialmente vuota mostra **Prima sincronizzazione — acquisisci i dati**. Indicare il percorso locale della stessa cartella condivisa e premere **Acquisisci dati / Prima sincronizzazione**.
6. Dopo l'arrivo dei dati sono disponibili le pagine ordinarie. Il ruolo corrente è visibile; gli ultimi scambi sono consultabili in Condivisione e collaboratori.

I percorsi della cartella condivisa possono essere diversi sui due PC: conta che il client cloud li sincronizzi con lo stesso contenuto. L'app conferma soltanto lo scambio nella cartella locale, non l'upload remoto del client. Se non arriva nulla, controllare disponibilità offline, completamento del client e pubblicazione iniziale del fondatore. Errori e ultimo tentativo rimangono visibili; lo scambio è ripetibile senza duplicare gli eventi già acquisiti.

## Ruoli, rinnovo e cambio di ruolo

| Ruolo | Consulta ed esporta | Modifica dati | Gestisce inviti/revoche | Esporta recupero fondatore |
|---|---|---|---|---|
| Fondatore | Sì | Sì | Sì | Sì |
| Admin dati | Sì | Sì | No | No |
| Visualizzatore | Sì | No | No | No |
| Copia di consultazione | Sì | No | No | No |

L'elenco **Operatori e dispositivi** identifica il dispositivo corrente, il fondatore quando noto, gli accessi e le revoche. “Invito emesso” non significa che il destinatario lo abbia già usato: non è presente un servizio online di tracciamento delle accettazioni. L'elenco pubblico firmato viene ricevuto dagli altri PC al prossimo scambio.

Per rinnovare un accesso o cambiare ruolo, il fondatore seleziona **Rinnova / cambia ruolo** sulla riga interessata e genera un nuovo invito. La generazione revoca il vecchio accesso: consegnare il nuovo file al destinatario. Sul PC destinatario aprire **Applica nuovo invito a questo dispositivo**, nella stessa sezione, e caricarlo con la password. I dati locali sono conservati; non si crea un altro archivio. Un invito di un'altra società è rifiutato. Il fondatore non può sostituire la propria identità con un invito collaboratore da questo percorso.

La revoca viene pubblicata dal fondatore con uno scambio e recepita dai PC quando si sincronizzano. Restano accettati gli eventi già acquisiti dal fondatore e registrati esattamente al momento della revoca; scritture sconosciute o modificate vengono respinte, anche se retrodatate. Un PC offline può quindi produrre modifiche locali che saranno rifiutate dopo la revoca: sincronizzare prima di revocare se occorre conservare modifiche legittime. La revoca non cancella copie già scaricate e non ruota automaticamente la chiave di lettura. Rotazione completa e portachiavi rimangono lavoro INC-11.

## Due file distinti per il recupero

**Backup dati ZIP**, da Archivio e scambio → Scarica backup: database consistente, revisioni, conflitti e allegati originali. È **non cifrato** e non contiene chiavi private o identità operative. Il manifest 0.4 aggiunge checksum, data e metadati pubblici della società. Sono leggibili anche i precedenti backup schema 1, privi di checksum del database.

**Recupero accessi JSON cifrato**, da Condivisione e collaboratori → Proteggi il recupero degli accessi del fondatore: contiene identità, chiavi e metadati degli accessi del fondatore. Richiede una password dedicata di almeno 12 caratteri. Va custodito separatamente dai dati e la password separatamente dal file. Chi possiede file e password può recuperare i privilegi del fondatore. Non caricarlo nella cartella condivisa dei pacchetti.

Conservare entrambi e aggiornarli dopo modifiche agli accessi. Il file di recupero può essere usato con backup dati successivi della stessa società: il ripristino verifica le firme degli eventi e i metadati pubblici più recenti. Un file del fondatore di un'altra società, una password errata o uno storico non autenticabile vengono rifiutati. Il backup dati ordinario continua a escludere le credenziali.

## Proteggere i dati sul dispositivo

Archivio locale, allegati e backup ZIP **non sono cifrati** dall'app; `identity.json` contiene le chiavi dell'operatore in chiaro nella cartella dati. Contengono dati sanitari di atleti, spesso minorenni. La protezione a riposo è affidata al sistema (decisione del 14 novembre 2026, [revisione tecnica](REVISIONE_TECNICA.md) RT-11):

- **Windows:** attivare BitLocker o *Crittografia dispositivo* (Impostazioni → Privacy e sicurezza) sul disco che contiene la cartella dati; usare un account con password o PIN, senza accesso automatico, e non condividerlo.
- **Android:** impostare un blocco schermo (PIN, password o sequenza); sui dispositivi recenti la cifratura dell'archivio è attiva e legata al blocco. Il backup automatico Android dell'app è disattivato.
- **Backup:** usare l'opzione «Proteggi con password» (file `.fgbak`, vedi [Backup protetto da password](BACKUP_CIFRATO.md)) oppure conservarli su un supporto cifrato o in una posizione ad accesso controllato, separata dalla cartella di scambio. Chi ottiene una copia di un backup ZIP non protetto ne legge il contenuto; senza la password un `.fgbak` non è recuperabile.

## Tre modalità di ripristino

Dopo il caricamento ZIP l'anteprima mostra società, conteggi, allegati e verifiche di integrità. Il ripristino ricostruisce uno schema SQLite noto in una cartella temporanea, conserva dati/revisioni e pubblica il nuovo archivio solo a operazione completa. Rifiuta percorsi ZIP non previsti, allegati mancanti/corrotti, schemi non supportati e destinazioni occupate o sovrapposte. Limiti attuali: 100 MB compressi, 1 GB espanso e 10.002 voci ZIP. Non estrae percorsi arbitrari e non esegue definizioni SQL provenienti dal file caricato.

| Modalità | Accessi ottenuti | Collegamento alla società originale |
|---|---|---|
| Copia di consultazione — sola lettura | Lettura/esportazione | Nessuno. Non possiede le credenziali originali. |
| Nuova copia indipendente — nuovo fondatore | Modifica e gestione della nuova copia | Nessuno. Nuovo identificatore archivio, nuove chiavi e nuovo canale; collaboratori originali non ereditati. |
| Recupera la società originale e gli accessi | Recupero del fondatore originale | Sì, con backup dati e file recupero accessi cifrato/password corrispondenti. |

Nella copia indipendente i dati e i loro identificatori/revisioni sono conservati, ma gli eventi vengono rifirmati dalla nuova autorità e riportano l'impronta della provenienza. Non si tratta di una validazione scientifica dei dati importati né del recupero del controllo sulla società originale. I conflitti del precedente canale non diventano conflitti del nuovo canale; lo storico originario rimane nel backup sorgente. Se il backup contiene più società, sono selezionabili separatamente nel nuovo archivio.

Il recupero originale ricrea il contesto del fondatore e assegna un nuovo identificativo di installazione al database; la sua identità crittografica è quella recuperata. È una procedura per recuperare/sostituire il PC, non per aggiungere un collaboratore. Evitare l'uso contemporaneo della stessa identità su vecchio e nuovo PC. Se la società è già registrata nell'installazione destinataria il ripristino originale viene rifiutato: non sostituisce silenziosamente l'archivio attivo. Dopo il recupero configurare il nuovo percorso della cartella condivisa e sincronizzare.

Senza file di recupero o senza password si possono consultare i dati oppure creare una copia indipendente; non si ricavano le chiavi originali dal database. Per continuare a collaborare nella società originale occorre un nuovo invito da un fondatore ancora disponibile.

## Limiti e verifiche

Le prove automatiche coprono i tre ripristini, vecchi ZIP, più società, integrità, password errata, credenziali di un'altra società, destinazione occupata, rollback, bootstrap, permessi, rinnovo e revoca con conservazione degli eventi autorizzati. Prove GUI su archivi sintetici separati. Non equivalgono a un audit crittografico esterno o a un collaudo di tutti i client cloud; portachiavi, rotazione automatica delle chiavi, trasferimento guidato dell'autorità con disattivazione del vecchio fondatore e sincronizzazione automatica restano aperti. Questi limiti non impediscono il flusso di recupero e collegamento locale della 0.4.
