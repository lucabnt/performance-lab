# Primo scambio WebDAV fra Windows e Android

25 ottobre 2026. Stessa società tramite invito personale; ogni dispositivo conserva il proprio archivio locale e le proprie credenziali cloud. Non copiare il database SQLite aperto nella cartella cloud.

## Koofr e collegamento del telefono

1. Nel sito Koofr crea la cartella di scambio, se non esiste già. In Preferenze → Password → Password applicazione genera una password dedicata al telefono; non usare la password principale dell'account. Koofr richiede password applicazione per WebDAV.
2. Su Windows seleziona la società originale e apri Archivio e scambio → Condivisione e collaboratori. Configura WebDAV con l'URL finale della cartella già condivisa e accessibile; ad esempio `https://app.koofr.net/dav/Koofr/Fuorigiri-QA/`. Maiuscole e minuscole del percorso devono corrispondere. Salva connessione e sincronizza.
3. Dal dispositivo fondatore crea un invito personale per il telefono. Scegli Admin dati per testare scritture da entrambi; Visualizzatore per sola consultazione. Trasferisci il JSON e comunica la password dell'invito separatamente. La password dell'invito e quella WebDAV sono cose diverse.
4. Sul telefono apri Gestisci società → Collega tramite invito. Importa il JSON e inserisci la password dell'invito. Non creare una società omonima e non usare il backup al posto dell'invito.
5. Apri la società collegata → Archivio e scambio → Condivisione e collaboratori. Scegli WebDAV e inserisci lo stesso URL della cartella, l'email del tuo account Koofr e la password applicazione dedicata al telefono. Se usi un altro account cloud, deve avere accesso effettivo alla medesima destinazione; non basta una cartella omonima nel suo spazio.
6. Premi Salva connessione e sincronizza. Attendi il termine e controlla stato, conteggi e assenza di errori. Prova poi una modifica innocua in una società QA sul telefono, sincronizza, sincronizza il PC e verifica il ritorno. Ripeti in direzione opposta. Il collegamento alla cartella da solo non dimostra ricezione da parte dell'altro dispositivo.

Il formato v1 già in uso può essere mantenuto per il primo test. Attivare v2 è una scelta separata del fondatore, dopo aver aggiornato tutti i dispositivi. Non creare un nuovo canale o nuovi accessi solo per cambiare trasporto dalla cartella desktop a WebDAV.

Fonte: [parametri WebDAV ufficiali Koofr](https://koofr.eu/help/koofr_with_webdav/how-do-i-connect-a-service-to-koofr-through-webdav/). Nessun account o password reale utilizzato nei test automatici del progetto.

## Orari, lingua e stato dello scambio

Gli istanti vengono conservati in UTC con offset; l'interfaccia li converte nel fuso scelto per il dispositivo. Il pannello permette Fuso del dispositivo, Europe/Rome oppure UTC, e mostra anche la sigla del fuso. Il 25 ottobre 2026 alle 16:23 UTC corrisponde alle 17:23 in Europe/Rome; in estate il distacco è due ore. I timestamp legacy privi di offset vengono segnalati, senza inventare il fuso.

La rotellina e il messaggio Sincronizzazione in corso rimangono fino al termine della richiesta, del ricaricamento dello stato o dell'errore; comandi e configurazione sono disabilitati durante l'operazione, senza percentuali fittizie. Il registro usa lo stesso fuso. Ultimo tentativo indica l'inizio dell'ultimo tentativo, non una conferma che tutti gli altri dispositivi abbiano ricevuto i dati.

Aggiornamento 26 ottobre: lo scambio viene avviato come attività locale indipendente dalla pagina. Il riepilogo globale resta visibile cambiando scheda o ricaricando l'interfaccia; riporta fase reale, tempo trascorso, file letti/scritti ed esito. La chiusura del processo può interrompere il lavoro: alla riapertura viene segnalato come interrotto, senza dichiararlo riuscito. Riprovare riutilizza revisioni/pacchetti già acquisiti.

**Sincronizza ora è incrementale:** non ripubblica i pacchetti già presenti e non riscarica quelli già acquisiti. Inventario e controlli firmati degli accessi vengono comunque letti; metadati, primo trasferimento, allegati e limiti di rete possono richiedere tempo. L'esito distingue pubblicati, revisioni ricevute, pacchetti letti, già noti saltati, elementi in attesa e conflitti. **Verifica completa del canale** rilegge anche i pacchetti conosciuti ed è più lenta. Nessuna pulizia automatica dello storico remoto viene introdotta.

Lingua e fuso sono preferenze del dispositivo, in `device-preferences.json` nella radice dati: fuori dai database, dai backup societari e dalla sincronizzazione. La lingua viene letta prima di caricare l'interfaccia, anche se cambia la porta del backend Windows. Un salvataggio della lingua non sovrascrive la preferenza del fuso.

## Scollegare e ripristinare una società sul solo dispositivo

Gestisci società → Società su questo dispositivo → Scollega dal dispositivo. La società sparisce dal selettore e dai futuri scambi automatici, ma i file e gli accessi locali rimangono per il recupero. La destinazione cloud, gli altri dispositivi e gli inviti non vengono eliminati o revocati. Questa operazione non libera spazio e non è una cancellazione sicura dei dati.

Per recuperarla: nella stessa sezione, Società scollegate → Ripristina collegamento. Non viene creata una nuova identità. Lo scollegamento attende lo scambio locale già in corso; il ripristino richiede che database e accessi della copia locale siano ancora disponibili. Le cartelle delle società scollegate restano riservate per impedire sovrapposizioni accidentali durante creazione o recupero di altre società.
