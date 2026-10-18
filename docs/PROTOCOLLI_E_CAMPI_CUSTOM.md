# Protocolli, prove e campi facoltativi - 0.8

## Flusso della UI

**Protocolli** contiene la creazione di tutti i metodi: incrementale aerobico manuale o da ERG, Sprint breve, Wingate 30/15 s e Personalizzato. Il catalogo filtra per nome/codice, famiglia e stato. Una nuova versione parte dai dati della precedente, mantiene il collegamento e richiede una motivazione. Anche senza ERG si può descrivere una sequenza di step o conservare una scheda d’archivio senza carichi.

**Test e analisi → Nuovo test** sceglie un protocollo attivo e la modalità Manuale oppure FIT/CSV. La definizione del protocollo non è più contenuta nel modulo della prova. Un incrementale senza step accetta risultati manuali; per analizzarne il file serve una versione con carichi. I protocolli custom possono conservare tracciati osservati anche senza una sequenza di carichi o un motore fisiologico dedicato.

Per gli anaerobici: riepilogo di durata/carico/finestre, scelta della sessione FIT, trattamento esplicito dei duplicati, click sul grafico per impostare l’inizio, zoom sullo sforzo e intervalli esclusi con motivo. La durata deriva dal protocollo. Inserimenti manuali e calcoli da file restano distinti; revisione con motivo e controllo della concorrenza. La nuova prova richiede atleta/protocollo attivi; una correzione può conservare i riferimenti archiviati del record originale.

## Schema estensibile, non codice eseguibile

Ogni protocollo può definire fino a 50 campi facoltativi complessivi, con identificatore stabile, etichetta leggibile, tipo e unità. Tipi: numero finito, testo, sì/no, data ISO o scelta da elenco. Per i numeri si possono impostare minimo/massimo; per gli elenchi si dichiarano le scelte. Gli identificatori sono lettere minuscole, numeri e underscore e non coincidono con colonne fisiologiche del database.

Il campo appartiene a una delle due schede:

- **Protocollo:** parametro fissato nella versione, es. numero di ripetizioni, pendenza o lunghezza del percorso. Il valore viene copiato nello snapshot della prova.
- **Test:** misura/osservazione della singola esecuzione, es. tempo, picco dichiarato, temperatura o difficoltà percepita.

Durante una prova si possono aggiungere campi opzionali per quella sola esecuzione. La definizione resta nel record della prova; non modifica retroattivamente il protocollo. Per rendere un campo comune alle prove successive pubblicare una nuova versione del protocollo.

Tutti i campi sono facoltativi: null/assenza significa non rilevato, zero rimane zero e false rimane No. Booleani e numeri non vengono convertiti silenziosamente fra loro. Il backend verifica tipo, intervalli, scelte, date, duplicati di identificatore e coerenza della scheda, anche per chiamate che bypassano la UI.

Non vengono eseguite formule inserite dall’utente, Python, JavaScript o SQL. Un protocollo custom registra risultati dichiarati e osservazioni; caricare un FIT non lo trasforma automaticamente in un Wingate o incrementale. Aggiungere un campo chiamato “VO2max” non gli attribuisce un metodo di misura validato.

## Archiviazione, confronti ed esportazioni

L’estensione è additiva nei documenti JSON già archiviati in SQLite: nessuna riscrittura dei test precedenti e nessuna nuova colonna per ciascun campo. Il motore conserva schema, unità, valori e parametri di protocollo nello snapshot di analisi. Le revisioni e i pacchetti di sincronizzazione proteggono questi dati come il resto del record.

Le misure numeriche custom sono disponibili in Storici e confronti e nel grafico del profilo atleta. La chiave della metrica include protocollo e identità della definizione: cambiare unità/tipo non unisce le serie. Schema, versione, origine e condizioni rimangono separati. La scelta è conservativa e può separare versioni equivalenti: non è una dichiarazione di equivalenza scientifica tra metodi diversi.

I report PDF/Markdown del singolo e dell’archivio includono etichette e unità leggibili. L’export ZIP aggiunge `extended/campi_personalizzati.csv` con test/protocollo, scheda, identificatore, etichetta, tipo, unità e valore JSON, così false, numero e null restano distinguibili. `extended/archive.json` conserva i record completi. Questo CSV esteso non è un importatore generico di protocolli: per ripristino fedele usare il backup, per nuove prove usare la UI/API.

Identità e versioni appartengono al nucleo comune della suite: un’eventuale app allenamenti può riusare schemi, archivi/accessi e trasporti senza duplicare il motore di analisi o permettere modifiche al branding societario.
