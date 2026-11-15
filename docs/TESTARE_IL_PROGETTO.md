# Come testare il progetto, inclusa l'interfaccia

## Sync v2, backup v3 e migrazione delle società

[Guida e contratto completi](SYNC_V2_E_BACKUP.md). Su copie sintetiche, aggiornare tutti i client, attivare v2 come fondatore e verificare che la replica acquisisca tracciato e successive correzioni senza duplicare i blocchi. Togliere un blocco dal solo canale QA, verificare errore e ritentare dopo averlo ripristinato; usare Verifica completa per controllare anche i blocchi noti.

Per il backup scegliere v3; su desktop usare Salva direttamente su disco per file grandi. Ripristinare realmente in copia indipendente e confrontare revisioni e allegati. In un legacy sintetico con due società usare Analizza archivio aperto → Separa società: verificare una sola società nella copia e originale intatto. La procedura si blocca su riferimenti incrociati o non attribuibili.

```powershell
.venv/Scripts/python.exe scripts/verify_storage_v2.py --data .local/qa-streaming-nuovo --large
```

Genera 101 MB sintetici non comprimibili e prova backup, verifica e ripristino oltre il vecchio limite. Usare una cartella nuova; servono circa 1 GB libero e tempo per le copie. Non rigenera gli archivi dell’utente.

## Nuovi requisiti TD-83–97: dettaglio test e maturazione

Per provare insieme test esistenti e nuovi casi di crescita, creare **una cartella nuova**:

```powershell
.venv/Scripts/python.exe scripts/demo_maturation.py --data .local/demo-crescita-nuovo
npm --prefix frontend run build
.venv/Scripts/python.exe scripts/serve.py --data .local/demo-crescita-nuovo
```

Aprire l'URL completo con token stampato dal server. **Anche `demo_suite.py`, completo o `--small`, ora include la maturazione**; `demo_maturation.py` rimane un alias della versione ridotta. In entrambe le società sono presenti quattro profili «Crescita DEMO»: picco maschile, crescita femminile, dati insufficienti e adulto. I primi due includono peso variabile, statura seduta, apertura delle braccia, arti inferiori, stature genitoriali e previsione adulta esterna esplicitamente fittizia. Manifest `growth_cases`, misure avanzate e analisi conservate sono inclusi fin dall'inizio nelle repliche admin/visualizzatore, backup e ZIP portabili.

Gli archivi già generati non vengono aggiornati automaticamente. Per rigenerare la demo standard chiudere app/server e usare `.venv/Scripts/python.exe scripts/demo_suite.py --data .local/ui-test --reset`: la vecchia cartella viene conservata. Per non toccare alcun archivio esistente usare un percorso nuovo. L'alias `demo_maturation.py` rifiuta destinazioni esistenti e non offre `--reset`.

Checklist funzionale:

1. Dal dettaglio di qualsiasi test usare «Apri profilo atleta»: si chiude la finestra e si apre il profilo corretto, anche per un visualizzatore. Aprire un incrementale con tracciato: MAP, potenza di soglia e FTHR insieme alle zone; fonte e coefficiente realmente applicato leggibili. Selezionare un livello lattato e verificare guide/punto/riga W–FC. Non aspettarsi FC se non disponibile.
2. Scorrere fino in fondo al dettaglio: X rimane visibile. «Correggi test» apre l'editor dedicato; verificare anche Sprint/Wingate, custom e storico manuale. Cambiare un dato e chiudere: deve chiedere se continuare o scartare, senza modificare il test salvato.

3. Nell'editor digitare `23:45` come fine dal file: il campo secondi deve diventare `1425`. Provare `23:60`: deve essere segnalato, non salvato come il vecchio valore. Il grafico indica l'origine dal file; il recupero rimane relativo alla fine sforzo. Verificare input da tastiera e selezione di un campione.
4. Controllare campi personalizzati finali e glossario contestuale in ogni pagina. Verificare anche IT/EN per i nuovi componenti; restano testi legacy da completare.
5. Dal footer aprire «Licenza, limiti e backup»: leggere GPL originale, avvisi delle dipendenze, assenza di garanzia e limiti backup. Nessuna EULA bloccante aggiunta. La build copia automaticamente i testi legali negli asset, senza modificarne gli originali.
6. In Archivio e scambio → Condivisione selezionare un provider senza registrazione OAuth: comando non avviabile e spiegazione dei prerequisiti. Account collegato non significa cartella verificata; l'evidenza di accesso precedente non vale per una nuova destinazione. Non inserire credenziali reali nel corpus SOLO DEMO.
7. Nel profilo «Crescita DEMO peak» verificare circa `8,96 cm/anno` al `01/01/2024`. Selezionare l'analisi conservata; poi una diversa data di anteprima. Nelle misure facoltative verificare statura seduta e indici avanzati senza campi obbligatori aggiuntivi. Nel profilo «female» verificare circa `7,96 cm/anno` al `01/01/2024`, Moore/Mirwald nelle date ammesse e indici opzionali. Il caso «missing» spiega le assenze; «adult» non applica i modelli adolescenti fuori dominio.
8. Conservare una nuova analisi con motivo su una copia QA; correggere una rilevazione con motivo. La nuova anteprima può cambiare, l'analisi precedente deve rimanere identica. Verificare CSV estesi, PDF/MD atleta/società e vero ripristino del backup.

Metodi e gate: [MATURAZIONE.md](MATURAZIONE.md). %PAH/residuo richiedono una previsione adulta esterna con fonte/metodo; non è presente un calcolatore automatico Khamis–Roche. I test con curve sintetiche non certificano accuratezza biologica.

### Eliminare e ripristinare test e misure — 8 novembre 2026

Nel dettaglio test aprire **Correggi test → Elimina test**; per le misure usare **Correggi rilevazione → Elimina rilevazione**. La conferma è separata dal salvataggio della correzione: non occorre inserire il motivo di revisione o completare campi non validi della bozza. **Annulla** ritorna all’editor senza modificare il record. **Conferma eliminazione** lo esclude dagli elenchi/calcoli correnti ma conserva revisioni e file originali.

Nel profilo aprire **Rilevazioni eliminate** oppure **Test eliminati → Ripristina**; i test sono recuperabili anche da **Test e analisi → Test eliminati**. Provare su un archivio sintetico nuovo: eliminare, verificare assenza nei grafici/IMC e nelle proposte antropometriche, ripristinare e confrontare valori e riferimenti originali. I test già salvati mantengono i propri input anche eliminando una rilevazione collegata; report e snapshot conservati non vengono riscritti. Ripetere con revisione obsoleta (conflitto, nessuna sovrascrittura) e accesso visualizzatore (scrittura vietata). Per il collaudo grafico delle varie famiglie usare i loro editor dedicati; le sole prove API non attestano il rendering di tutti gli editor.

## Aggiornare le schermate del README

La [guida della galleria](screenshots/README.md) descrive acquisizione, dati sintetici, inquadrature e aggiornamento delle immagini in `docs/screenshots/`. Quando cambia una schermata rappresentata, aggiornare anche la sua immagine e didascalia nello stesso intervento. Non serve rigenerare o svuotare una demo esistente: usare un archivio QA nuovo quando occorre un corpus pulito.

## Quali dati sintetici usare

Per provare tutte le funzionalità usare **`scripts/demo_suite.py`**, il generatore del corpus completo. Il comando che hai eseguito, `scripts/demo.py`, genera invece la vecchia demo minima incrementale e non include tutti i casi nuovi.

| Comando | Contenuto | Uso |
|---|---|---|
| `scripts/demo_suite.py --data <cartella>` | 2 società, 32 atleti, 264 rilevazioni, 192 test su 2024–2026 (190 non eliminati), 12 versioni di protocollo per società; 8 profili crescita con snapshot e dati avanzati; FIT/CSV, Sprint/Wingate/custom, gas/lattato/recupero, gruppi/anni, ruoli e conflitti | Scelta consigliata per il collaudo completo, inclusa maturazione |
| `scripts/demo_suite.py --small --data <cartella>` | Stessi tipi di scenari, meno atleti e prove | Verifiche rapide e test automatici |
| `scripts/demo.py --data <cartella>` | 4 atleti e 4 test incrementali da FIT, 2 ERG originali | Demo minima storica |

Tutte le persone, misure e prove generate sono fittizie. Il generatore completo non importa i CSV personali allegati. [Composizione e matrice dei casi](DATI_SINTETICI.md).

## Usare il corpus già presente

Se esiste `.local/demo-fuorigiri-completo/manifest-demo.json`, non occorre generarlo di nuovo:

```powershell
.venv/Scripts/python.exe scripts/serve.py --data .local/demo-fuorigiri-completo --port 8771
```

Aprire il link **completo con token** stampato dal server e selezionare **Velodromo Aurora - SIMULAZIONE** oppure **Pedale del Lago - SIMULAZIONE**. La scelta della società determina il suo archivio: non importa automaticamente i dati nell’archivio operativo abituale.

Per la finestra desktop, con dipendenze desktop installate:

```powershell
.venv/Scripts/python.exe desktop_entry.py --data .local/demo-fuorigiri-completo
```

In alternativa l’eseguibile distribuito accetta `Fuorigiri.exe --data ".local\demo-fuorigiri-completo"`, adattando il percorso. Usare lo stesso percorso di dati nei comandi di generazione e avvio. Il programma senza `--data` potrebbe aprire il normale archivio personale anziché la demo.

## Trovare e verificare i grafici del singolo test

In **Test e analisi**, impostare **Dati disponibili → Con tracciato FIT/CSV**, poi **Analizza**. Lo stesso filtro è disponibile nello storico del profilo atleta. La colonna Dati disponibili distingue i tracciati dai soli riepiloghi. Nel corpus completo attuale ci sono **44 record con campioni** e 148 riepiloghi manuali (192 record totali, inclusi i due eliminati): non tutte le righe devono quindi avere una curva. Un CSV di storico con medie/massimi è un riepilogo, non un CSV temporale.

Per un esempio completo selezionare **Velodromo Aurora - SIMULAZIONE → Riva Giulia → 15 marzo 2026 → AER-RULLO-ALL laboratorio**. In cima al dettaglio devono comparire potenza, FC e cadenza, sovrapposte in un unico grafico, ciascuna con la propria scala e tutte visibili. Gli eventuali prelievi di lattato compaiono come punti sullo stesso asse temporale, con scala in mmol/L. I controlli Canali sovrapposti permettono di mostrare/nascondere i segnali e attivare velocità, temperatura e quota, se presenti. Più sotto rimangono l'analisi lattato/carico e gli scambi gassosi quando disponibili. Aprire anche un Wingate con tracciato: deve mostrare gli stessi canali disponibili, non solo la potenza. Nei test manuali compare la spiegazione dell'assenza di campioni; valori medi e massimi non sono trasformati in curve inventate.

L'importazione di un **CSV temporale** accetta questi campi (tempo in secondi crescente e almeno due campioni; canali mancanti lasciati vuoti):

```csv
t,power,hr,cadence,lactate_mmol_l,speed_kmh,temperature_c,altitude_m
0,100,100,80,,25,20,130
1,110,102,82,1.5,26,20,130
2,120,104,84,,27,20,131
```

Alias italiani: `tempo_s`, `potenza_w`, `fc_bpm`, `cadenza_rpm`, `lattato_mmol_l`, `velocita_kmh`, `temperatura_c`, `quota_m`. Il lattato viene rappresentato solo agli istanti misurati, senza interpolazione. I prelievi manuali usano l'istante di raccolta; l'eventuale ritardo serve all'associazione al carico, senza spostare il punto nel grafico temporale. Le interruzioni oltre l'intervallo massimo ammesso interrompono la linea; un dato mancante non diventa zero.

I FIT conservano anche velocità (convertita da m/s a km/h), temperatura e quota, se registrate. I canali aggiuntivi scartati da precedenti versioni del decoder richiedono una nuova importazione del file originale: questa modifica non ricalcola né riscrive automaticamente i test archiviati. I campioni già conservati nell'oggetto tracciato sono recuperati dal dettaglio anche se non incorporati nel record del test.

Dopo aggiornamenti ai sorgenti, ricompilare la GUI con `npm.cmd --prefix frontend run build`, riavviare il server e ricaricare la pagina. Un vecchio eseguibile non acquisisce queste modifiche automaticamente. Verifica automatica del modello grafico: `npm.cmd --prefix frontend run test:signals` (Node 22.18+ oppure 24).

## Interpolazione del lattato: livelli, FC e report

Nel modulo di analisi incrementale, **Metodo e qualità → Livelli di lattato da stimare** permette di scegliere da 1 a 20 concentrazioni (default 2, 3 e 4 mmol/L, fino a tre decimali). Inserire i prelievi con istante e concentrazione e associarli a uno step oppure a un carico esplicito, indicando il ritardo se necessario. I prelievi nel CSV temporale vengono acquisiti automaticamente; una misura manuale allo stesso istante ha precedenza. Il carico automatico è il target dello step costante: non viene confuso con una potenza istantanea misurata.

Dopo anteprima/calcolo, **Lattato: potenza e FC ai livelli richiesti** presenta punti osservati, interpolazione lineare e valori stimati W/W/kg/bpm. La FC usa la media finale dello step completo a carico costante secondo il preset (default ultimi 30 s, copertura almeno 80%); non il battito durante il prelievo o recupero. La tabella mostra separatamente le ragioni di indisponibilità: un prelievo con carico esplicito ma senza step/FC validi può dare watt senza bpm. Peso assente o stimato non produce W/kg. Attraversamenti ambigui, carichi duplicati e curve decrescenti richiedono revisione; nessuna estrapolazione oltre i prelievi.

I risultati contengono metodo `lactate.fixed-linear/2`, parametri FC e prelievi di supporto. I livelli configurati e il metodo sono salvati nella revisione; modificare una prova richiede una correzione esplicita. I vecchi test non vengono ricalcolati all'apertura e possono mostrare solo watt a 2/4 mmol/L. Le nuove identità di metodo restano separate negli storici. Le concentrazioni fisse non sono automaticamente LT1/LT2, FTP o MLSS.

In **Storici e confronti**, le metriche dei livelli calcolati (anche decimali, es. FC a 3.5 mmol/L) diventano disponibili. PDF e Markdown riportano stime e metodo; il CSV standard mantiene le colonne originali a 2/4 mmol/L e il file aggiuntivo **`extended/lattato_livelli.csv`** include ogni livello, W/W/kg/FC, revisione, metodo e motivi di indisponibilità. I report societari e le loro sottosezioni includono le nuove metriche disponibili.

Verifiche automatiche: `.venv/Scripts/python.exe -m pytest tests/test_lactate_levels.py -q`. Caso numerico indipendente: 3 mmol/L a 200 W e 150 bpm, 5 mmol/L a 240 W e 160 bpm → 4 mmol/L a 220 W e 155 bpm. L'archivio QA separato `.local/qa-lattato-livelli-20261018` contiene una prova fittizia con livelli 2/3/3.5/4/6; il livello 6 è intenzionalmente fuori intervallo e deve risultare indisponibile. Per aprirlo: `.venv/Scripts/python.exe scripts/serve.py --data .local/qa-lattato-livelli-20261018 --port 8792`. Il PDF di verifica è in `output/pdf/lattato-livelli-esempio.pdf`. Nessuna rigenerazione dell'archivio demo abituale è necessaria.

## Verificare Storici e confronti con molti protocolli

1. Aprire **Storici e confronti** nel corpus completo Aurora, selezionare MAP operativa, Vista Stagione e Mediana. Metrica e protocollo sono i controlli principali; atleti/categorie/stagioni rimangono nel pannello espandibile, che segnala eventuali filtri attivi.
2. All'apertura compare **una sola serie**, quella con più valori validi. Le aggregazioni 2024/2025/2026 dello stesso protocollo/metodo formano un'unica voce di legenda. Wingate e custom senza MAP non producono serie vuote. Le metriche indicano quanti valori sono presenti nell'archivio filtrato, prima della selezione ultimo test per atleta.
3. Aprire **Scegli le serie da confrontare** e scegliere fino a quattro serie. La quinta scelta deve essere disabilitata; deselezionando una serie torna disponibile. Deselezionando tutte, compare un invito a sceglierne almeno una. Il pulsante Serie principale ripristina la scelta iniziale.
4. Ogni serie mantiene protocollo/versione, metodo/condizioni e origine della soglia distinti. Le sigle S1/S2 rimandano alla chiave sotto il grafico e alla tabella con media, mediana, estremi e numerosità. Affiancare ALL ed ESO mostra un avviso: il confronto è descrittivo, senza media comune o coefficienti automatici di equivalenza. Sprint, Wingate 15 s e 30 s restano anch'essi separati.
5. Passare a un'altra metrica: la selezione si ripristina sulla serie con più valori utili per quella metrica. Un filtro senza risultati mostra una spiegazione, non un grafico vuoto con molte legende. Le categorie temporali rimangono ordinate anche quando le serie coprono anni diversi; le viste nominali usano punti senza linee fra atleti o categorie.

**Copertura dati ed esportazione dell'archivio filtrato** contiene i report completi dei filtri correnti, non solo delle quattro serie del confronto interattivo. Questo ambito è indicato nell'interfaccia. La selezione grafica non modifica archivi o risultati.

I test del modello di confronto sono inclusi in `npm.cmd --prefix frontend run test:signals`.

## Creare i dati nuovi oppure svuotare e ripopolare `.local/ui-test`

Dalla radice del progetto, per una destinazione che ancora non esiste:

```powershell
.venv/Scripts/python.exe scripts/demo_suite.py --data .local/ui-test
.venv/Scripts/python.exe scripts/serve.py --data .local/ui-test --port 8766
```

Se `.local/ui-test` esiste già e ricevi «Archivio non vuoto», **chiudi prima Fuorigiri, le vecchie schede del browser e tutti i server/repliche che usano quella demo**. Per arrestare il server nel suo terminale usa `Ctrl+C`. Poi:

```powershell
.venv/Scripts/python.exe scripts/demo_suite.py --data .local/ui-test --reset
.venv/Scripts/python.exe scripts/serve.py --data .local/ui-test --port 8766
```

Questo è il comando consigliato anche per sostituire la vecchia demo da quattro test con il corpus completo. Attendere il riepilogo finale del generatore prima di avviare il server: la preparazione delle società, delle repliche e dello scambio iniziale può richiedere qualche minuto.

Aprire il **nuovo URL con token in una nuova scheda** e scegliere la società. La rigenerazione ricrea gli identificativi e le identità dimostrative: una vecchia scheda può conservare la selezione di una società che non esiste più.

Anche il comando originale ora supporta il reset, ma continua a produrre soltanto i quattro test della demo minima:

```powershell
.venv/Scripts/python.exe scripts/demo.py --data .local/ui-test --reset
```

Per una prova rapida dello stesso meccanismo con il generatore completo: `python scripts/demo_suite.py --data .local/ui-test --small --reset`. Per tornare al corpus completo ripetere senza `--small`.

## Cosa fa `--reset` e come recuperare la cartella precedente

`--reset` non cancella definitivamente il contenuto: sposta l’intera cartella precedente in **`.local/demo-backups/<nome>-<dataUTC>-<identificatore>`**, stampa il percorso e ricrea i dati nel percorso originario. Ogni reset conserva una copia distinta, comprese le modifiche manuali fatte durante le prove. Il nome del backup usa UTC, indicato dalla Z.

Il reset accetta solo una cartella **direttamente sotto la `.local` di questo progetto**, per esempio `.local/ui-test` o `.local/demo-fuorigiri-completo`. Rifiuta la radice `.local`, la cartella dei backup, destinazioni esterne, sottocartelle degli archivi, link/junction e archivi aperti tramite app/server aggiornati. Il controllo vale anche per le repliche interne. Il server di test ora usa lo stesso blocco dell’app desktop.

Non vengono seguiti i percorsi del registro delle società: eventuali archivi o cartelle cloud **esterni** non vengono svuotati né spostati. Le repliche e lo scambio contenuti nella cartella demo vengono conservati insieme a essa e ricreati dal generatore. Non usare il reset su una demo collegata a dati operativi.

La copia conservata è una copia completa della directory, **non un backup portabile da aprire direttamente come nuovo archivio**: nei corpus con più società, registro, manifest e configurazioni contengono percorsi assoluti. Per tornare allo stato precedente, arrestare tutto, conservare altrove la nuova directory e rimettere la vecchia copia **nel suo percorso originale**. Per un ripristino indipendente usare invece i backup ZIP dall’interfaccia. Non è prevista una pulizia automatica delle copie: rimuoverle solo quando non servono più.

Se la generazione si interrompe dopo lo spostamento, la copia precedente rimane nel percorso stampato. Dopo aver risolto la causa, ripetere il comando con `--reset` conserva anche il tentativo incompleto. Senza `--reset` i generatori continuano a rifiutare destinazioni già popolate; il generatore completo richiede una cartella nuova anche se quella esistente è vuota.

## Come utilizzare il corpus nel collaudo

- **Atleti / Società e gruppi:** categorie, stagioni, appartenenze storiche, antropometria, omonimi, dati mancanti e stati archiviato/eliminato.
- **Protocolli:** ERG originali, definizioni manuali senza ERG o senza step, Sprint/Wingate, versioni e protocolli custom con campi facoltativi.
- **Test e analisi:** aprire le prove già archiviate oppure registrare nuove prove manuali/da file. I FIT/CSV da importare si trovano in `<cartella-demo>/fixtures`; consultare `manifest-demo.json` per protocollo, offset, termine sforzo ed esito atteso. Alcune fixture sono volutamente invalide: non vanno tutte importate con successo.
- **Storici e confronti:** scegliere protocollo/versione, categoria, stagione, media/mediana e metriche anche personalizzate; metodi distinti rimangono separati.
- **Report / export:** singolo test, atleta, gruppo/anno e società; controllare PDF/Markdown, CSV base/estesi, valori zero/No distinti dai mancanti e footer societario.
- **Import CSV:** provare prima anagrafiche, poi misure e storico; le fixture includono ID già presenti, un nuovo atleta e righe errate. Consultare la matrice per idempotenza e rifiuto atomico dei lotti.
- **Risultati attesi indipendenti:** usare `oracoli-numerici.json` e le fixture `oracolo-*` per controllare MAP, potenza/lavoro Wingate e media/mediana.

Il seed 481516 riproduce gli scenari e i valori; UUID, identità, firme e percorsi sono ricreati e non coincidono byte per byte. I quattro test minimi precedenti non coprono questo insieme di funzioni.

## Provare Admin, Visualizzatore e conflitti offline

Con la demo principale chiusa, avviare le tre istanze su **radici e porte differenti**:

```powershell
# Terminale 1: fondatore
.venv/Scripts/python.exe scripts/serve.py --data .local/ui-test --port 8766
# Terminale 2: admin
.venv/Scripts/python.exe scripts/serve.py --data .local/ui-test/repliche/admin --port 8767
# Terminale 3: visualizzatore
.venv/Scripts/python.exe scripts/serve.py --data .local/ui-test/repliche/viewer --port 8768
```

Aprire ciascun URL con il suo token e selezionare la società collegata. Le repliche sono già predisposte sulla prima società. Il Visualizzatore consulta e riceve ma non modifica. Per il conflitto previsto dal corpus: sincronizzare prima Admin, poi Fondatore, osservare e risolvere il conflitto, quindi sincronizzare di nuovo entrambe le parti e il Visualizzatore. Non copiare SQLite fra le istanze. **Prima di un reset arrestare tutte e tre le istanze.**

Gli inviti e il recupero SOLO DEMO usano la password pubblica `SoloDemo-NonUsareInProduzione-2026`; non usarli per archivi operativi. Il corpus non collega account cloud reali.

## Usare i dati con un installer o creare uno ZIP portabile

Se disponibile, estrarre il pacchetto demo della versione interessata (per esempio il precedente `dist/release/Fuorigiri-0.8.0-demo-sintetica.zip`, che non viene rigenerato cambiando il numero prodotto): contiene due ZIP nella cartella `backups`. Nell’app usare **Gestisci società → Ripristina da backup → Copia indipendente**, importandoli separatamente e assegnando un fondatore dimostrativo. Non usare «recupero originale» per questi backup dimostrativi. La copia indipendente non include le repliche già collegate: per quelle usare il corpus locale o rigenerarlo.

Per creare un nuovo corpus e il suo ZIP portabile nello stesso passaggio:

```powershell
.venv/Scripts/python.exe scripts/demo_suite.py --data .local/demo-da-esportare --export .local/fuorigiri-demo.zip
```

Se quella cartella esiste già, aggiungere `--reset` secondo le regole sopra. Lo ZIP contiene backup, protocolli, fixture e controlli attesi, senza le identità private delle repliche. I report e i backup esportati dall’app derivano dalla società attualmente selezionata.

## Build dell’interfaccia e UI condivisa con Ammiraglia

Se frontend/dist non è presente o hai cambiato il frontend, compilare prima dell’avvio:

```powershell
Set-Location frontend
npm ci
npm run build
Set-Location ..
```

La build usa il pacchetto versionato in frontend/vendor e non richiede il clone della repository comune. Dalla radice `python scripts/verify_suite_ui.py` ne verifica la provenienza; catalogo e procedura Ammiraglia sono in [Suite condivisa](SUITE_CONDIVISA.md). Per sviluppo con Vite e per le dipendenze Python/desktop vedere le sezioni di installazione sotto.

Il corpus copre i percorsi offline e gli errori controllabili sul PC. Account cloud reali, Fedora, Android, dispositivi di misura, PC pulito e qualifica scientifica richiedono verifiche proprie. Gli installer 0.8 già presenti precedono l’estrazione UI comune e questi nuovi comandi di sviluppo: non sono stati ricompilati in questo passaggio.

Le sezioni 0.3–0.7 seguenti sono cronologia e fixture minime di regressione, non il percorso consigliato per i nuovi dati.

## Novità 0.7: test anaerobici e cloud diretti

- Preparare il frontend come descritto sotto, poi `python scripts/generate_anaerobic_examples.py` e `python scripts/qa_anaerobic.py`. Avviare `python scripts/serve.py --data .local/qa-07 --port 8769` e usare l’URL completo con token stampato dal comando. Il primo comando genera solo esempi sintetici; il secondo si ferma se l’archivio ha già test.
- Test e analisi: aprire un Wingate e verificare metriche, copertura, metodo e PDF; aprire Nuova prova / protocollo per registrare una prova manuale o caricare uno dei tre FIT, con offset 60 s. Protocolli storici e nuove prove restano distinti. Per le correzioni compilare il motivo; due salvataggi dalla stessa revisione devono produrre un conflitto, senza sovrascrittura.
- Archivio e scambio: importare prima atleti_anaerobico.csv, poi test_anaerobico.csv con il nuovo profilo; ripetere l’importazione deve saltare i test già presenti. Il CSV esteso nello ZIP esportato permette l’importazione dei nuovi protocolli con durata esplicita. Backup e CSV hanno scopi diversi.
- Storici e confronti: scegliere picco, media, lavoro o calo; ogni insieme conserva famiglia, durata, finestre e provenienza. Un campo non applicabile a una famiglia non viene contato come misura mancante di quella prova.
- I quattro connettori sono disponibili per una società con accesso personale in Condivisione e collaboratori. Usare un archivio dimostrativo e cartella remota dedicata per il collaudo. Non usare dati personali per lo spike. [Configurazione OAuth e checklist inter-account](CONFIGURARE_LA_SINCRONIZZAZIONE.md).
- Test software: `python -m pytest -q`; test mirati in tests/test_anaerobic.py e tests/test_cloud.py. Nuovi sorgenti Kotlin non compilati: non interpretare i test Python/ASGI su PC come test Android.


## Verifica 0.6: WebDAV, distribuzione e Android

Eseguire prima `python -m pytest -q`, quindi `npm run build` in frontend. I test WebDAV avviano un server di fixture locale con rete loopback; la configurazione di produzione ammette solo HTTPS. Il test di Credential Manager reale richiede la sessione utente Windows; la sandbox di sviluppo può non avere un logon utilizzabile. La suite non legge password reali.

Per la GUI: `python scripts/serve.py --data .local/qa-06 --port 8768`, aprire l’URL completo con token stampato dal comando. Creare una società sintetica, poi Archivio e scambio → Condivisione e collaboratori. Provare cartella separata e scambio ripetuto; URL WebDAV invalido, password mancante/portachiavi bloccato, server HTTPS di prova, invito visualizzatore, due modifiche concorrenti, risoluzione esplicita. Mai usare dati operativi per questi casi.

Prova WebDAV reale: due account sulla stessa cartella Nextcloud, due archivi/identità, admin e viewer (anche sola lettura sul server), allegati FIT e PDF, perdita rete prima/dopo PUT, doppio invio, credenziale revocata, pacchetto alterato e ripresa. La rotazione richiede prima tutte le modifiche ricevute: provare chiusura del vecchio canale, nuovi inviti, arresto dopo avviso remoto, riavvio e completamento, quindi nuovo recupero accessi. L’esito server fixture non certifica Nextcloud.

Windows: `python scripts/build.py`, compilare `packaging/windows/Fuorigiri.iss`, installare su un PC/VM senza strumenti di sviluppo, avviare offline, creare test e produrre PDF, aggiornare, riaprire l’archivio e disinstallare verificando che il backup/dati restino. Il bundle completo deve avviarsi anche con PATH privo di Python/Node; `Fuorigiri.exe --smoke-test --data <cartella-di-prova>` verifica import, logo, icona, portachiavi importabile e backend. Provare due avvii sullo stesso archivio: il secondo deve essere respinto.

Fedora: seguire [la build Flatpak](DISTRIBUZIONE.md), installare su Fedora pulita, provare Wayland e fallback X11, Secret Service, picker, report, WebDAV e cartella client cloud. Testare anche installazione offline con runtime disponibili sul supporto; la sola `.flatpak` non basta.

Android: `python scripts/build_android.py --check` elenca i gate reali; non scarica librerie né produce un APK fittizio. Dopo compilazione su builder adatto: `gradle -p android connectedDebugAndroidTest`, modalità aereo dopo installazione, riavvio/processo terminato, import ERG/FIT/CSV e report PDF/MD/CSV, invito viewer/admin, Keystore e scambio WebDAV con desktop. Controllare tutte le wheel native, ABI/16 KB, memoria su file grandi, tastiera/grafici/touch, WorkManager con rete/batteria e recupero da errori. I quattro test `test_mobile_runtime.py` verificano il contratto sul PC, non sostituiscono questi casi.

## Versione 0.5 — preset, metodi e report completi

`.venv/Scripts/python.exe scripts/verify_versions.py
.venv/Scripts/python.exe -m pytest -q` verifica il nucleo e le API. Compilare TypeScript/Vite con i comandi sotto. Schema 3: alla prima apertura di un database precedente viene salvata `migrations/before-v3.sqlite`; la storia delle analisi resta invariata. Dettagli e limiti in [IMPLEMENTAZIONE_INCREMENTALE_05.md](archivio/IMPLEMENTAZIONE_INCREMENTALE_05.md).

Per una prova isolata completa: `.venv/Scripts/python.exe scripts/qa_incremental.py --data .local/qa-incrementale-05-nuova`, poi `.venv/Scripts/python.exe scripts/serve.py --data .local/qa-incrementale-05-nuova --port 8766`; aprire l’URL con token stampato. Solo quattro atleti/otto test sintetici, due stagioni. Non usare un archivio reale per questi comandi; lo script rifiuta destinazioni già popolate.

Checklist GUI: «Archivio e scambio → Report completo dell’archivio», anteprima società, gruppo, stagione e atleta; controllare i conteggi e scaricare PDF/MD. «Test e analisi»: dettaglio dei metodi/aderenza, curve lattato e gas del primo atleta 2026. Per un nuovo import scegliere file e sessione, quindi «Importa sessione selezionata»; calcolare anteprima dopo aver impostato fine sforzo. Nel form creare un preset nuovo, aggiungere marker/esclusioni con motivo, condizioni e gas CSV quando disponibili. In «Storici e confronti», la ripetibilità richiede coppie confrontabili e conferma esplicita di condizioni stabili, con export PDF/MD+CSV.

Cinque esempi PDF e quattro ZIP generati in `output/pdf/`: società, gruppo, gruppo/2026, atleta e singolo test specialistico. Sono dimostrazioni sintetiche, non referti degli atleti dell’allegato. Il bundle Windows rimane `dist/Fuorigiri/Fuorigiri.exe`; va distribuita tutta la directory. Fedora e corpus FIT reali richiedono prove dedicate.


## Rinomina 0.4.1 e specifica dei metodi

Avvio da sorgenti e procedura GUI restano quelli sotto. Distribuzione aggiornata: `dist/Fuorigiri/Fuorigiri.exe` su Windows, `dist/Fuorigiri/Fuorigiri` su Linux dopo build nativa. Comandi installati `fuorigiri` e `fuorigiri-performance-lab`; variabili `FUORIGIRI_DATA`, `FUORIGIRI_TOKEN`, `FUORIGIRI_API_URL`. Header interni `X-Fuorigiri-Token` e `X-Fuorigiri-Workspace`: frontend e backend devono essere aggiornati insieme. Riaprire l’app dopo l’aggiornamento per ottenere una nuova sessione; impostazione lingua e selezione società nel browser usano nuove chiavi.

Nuove installazioni: `%LOCALAPPDATA%/Fuorigiri` o `~/.local/share/Fuorigiri`. Se esiste soltanto la directory storica, il programma la riusa senza rinominarla: il registro contiene percorsi assoluti. Se esistono entrambe, usa Fuorigiri; per aprire l’altra passare `--data` esplicito. Non spostare archivi a mano. Lo stesso vale per un canale cloud precedente già presente: viene riutilizzato con le stesse chiavi; i nuovi canali hanno prefisso `fuorigiri-`. Due canali con la stessa chiave sono segnalati come errore invece di dividerne la storia. Per un canale nuovo aggiornare tutti i collaboratori alla stessa versione prima dello scambio. Il formato cifrato e l’estensione `.ctsync` rimangono compatibili.

La [specifica 1.0](METODI_INCREMENTALE.md) contiene i risultati attesi per lo sviluppo del motore successivo: **non tutti i suoi casi passano già nel motore 0.2.0**. Non confondere i test della rinomina con la validazione dei futuri algoritmi. Android è soltanto pianificato in [ANDROID.md](ANDROID.md).


Aggiornato il 17 ottobre 2026. I comandi partono dalla cartella del progetto. Le prove usano archivi sintetici separati dai dati operativi. L'interfaccia e il motore funzionano senza collegamenti a servizi esterni.

## Novità della preview 0.4 — società, backup e accessi

Guida dettagliata: [SOCIETA_BACKUP_E_ACCESSI.md](SOCIETA_BACKUP_E_ACCESSI.md). Suite corrente: **45 test passati**. Creare due archivi isolati su porte diverse, poi provare il flusso dal fondatore al visualizzatore/admin; nessun dato reale necessario.

1. Gestisci società → Crea nuova società: soltanto nome società/fondatore obbligatori; apertura automatica. Aggiungere un atleta sintetico.
2. In Condivisione e collaboratori generare un invito Visualizzatore e pubblicare i dati su una cartella locale condivisa di prova.
3. Nell’altra istanza usare Collega tramite invito. Prima di acquisire record, verificare che la società abbia già nome/ruolo e pulsante Prima sincronizzazione. Acquisire e controllare comparsa atleta e vincoli di modifica.
4. Dal fondatore usare Rinnova / cambia ruolo → Admin dati, scaricare il nuovo invito e pubblicare la revoca. Sul destinatario Applica nuovo invito: stesso archivio, nuovo ruolo, scrittura ora consentita. Provare anche la revoca e verificare che gli eventi già autorizzati rimangano disponibili su un terzo dispositivo appena collegato.
5. Esportare backup dati ZIP e recupero accessi cifrato separatamente. Usare una terza directory di avvio vuota per recuperare il fondatore: anteprima ZIP, modalità originale, file recupero e password. Verificare dati, possibilità di creare inviti e successiva sincronizzazione.
6. Provare lo stesso ZIP come copia di consultazione (nessuna modifica/canale) e come copia indipendente (nuovo fondatore/canale, nessun invito originale). Se contiene più società, verificarne la selezione.
7. Password errata, file di altra società, ZIP corrotto, destinazione occupata e società originale già registrata devono fallire senza sovrascrivere dati. Dopo errore la prova deve essere ripetibile; un annullamento prima della conferma non crea un archivio registrato.

Le prove automatiche simulano archivi diversi sullo stesso PC; i client cloud reali e Fedora richiedono ancora collaudo. Il recupero originale è una sostituzione/recupero del fondatore, non una procedura per clonarne l’identità su PC usati contemporaneamente. I segreti delle fixture rimangono fuori dai dati di produzione e dalla repository pubblica.

## Novità della preview 0.3 (precedenti)

Nome dell'app **Fuorigiri Performance Lab**; dalla 0.4.1 anche il bundle si chiama Fuorigiri. La sezione seguente conserva la procedura 0.3 (32 casi allora disponibili). Per provare la GUI con i nuovi esempi usare un percorso nuovo:

```powershell
.venv/Scripts/python.exe scripts/demo.py --data .local/demo-fuorigiri
.venv/Scripts/python.exe scripts/serve.py --data .local/demo-fuorigiri --port 8766
```

Aprire l'URL completo stampato (con token). Stesso comando `python scripts/demo.py ...` / `python scripts/serve.py ...` nell'ambiente attivo su Fedora. La demo contiene **quattro atleti, due ERG originali, due categorie con stagione e quattro FIT realmente decodificati**. Le esecuzioni sono simulate. Genera PDF di QA in `tmp/qa-fuorigiri/test.pdf` e `storico.pdf`.

Checklist aggiuntiva:

1. Selettore Società unico; Gestisci società apre creazione/associazione, Società e gruppi contiene solo categorie.
2. Crea gruppo con padre Allievi, stagione 2027 e nome vuoto: deve ereditare Allievi. Categoria principale senza nome deve essere rifiutata.
3. Protocolli → Crea protocollo manuale → Solo scheda d'archivio, senza step; salvare identità/versione. ERG disabilitato, JSON disponibile.
4. Nuovo test → Inserisci solo dati manuali: scegliere la scheda, data, MAP 230 e peso 50; risultato dichiarato 4,6 W/kg, nessun FIT obbligatorio. Lasciare FTP/FC vuote: non devono diventare zero. Correggere creando una revisione.
5. Storici: scegliere categoria/totale, media/mediana, metrica e protocollo; nella demo i due protocolli restano separati e le medie MAP sono 295 e 190 W. I test automatici includono una distribuzione asimmetrica con media 200 e mediana 100.
6. Esportare PDF e Markdown dello storico: metrica e statistica devono coincidere con la vista. Il PDF ha logo/credito nel footer di ogni pagina; niente sovrapposizioni.
7. Nel dettaglio di un FIT scorrere fino in fondo e tornare su: la lista sotto non deve muoversi né attraversare la superficie opaca. Chiudendo, lo scroll della pagina deve funzionare di nuovo.
8. Archivio e scambio: importazione, export/backup e report prima delle sezioni espandibili. I campi CSV richiesti sono indicati per ciascun profilo.

Esempi persistenti in `examples/synthetic/`: quattro `.fit`, manifest e CSV `atleti.csv`, `antropometria.csv`, `test_aerobico.csv`. Per provare il bulk CSV usare **un altro archivio vuoto**, importare prima atleti, poi antropometria e storico, confermando ciascun lotto dopo l'anteprima. I CSV storici rappresentano gli stessi test dei FIT: non importare entrambi nello stesso archivio. Per il percorso FIT usare gli ERG in `examples/protocols/`, riscaldamento 600 s, fine sforzo dal manifest (il file include 180 s di recupero). Peso/FC/RPE sono dati sintetici dichiarati nel manifest.

Le sezioni seguenti spiegano installazione, desktop, Vite e bundle; dove riportano fixture della 0.2 valgono gli aggiornamenti qui sopra.

## 1. Preparare l'ambiente

Servono Python 3.12 o successivo e Node.js 22 o successivo. Per la finestra desktop installare anche le dipendenze `desktop`; usando il browser è sufficiente il backend. Per lo sviluppo sono necessari entrambi i runtime; il bundle finale include Python e le risorse della GUI.

Windows PowerShell:

```powershell
# Eseguire dalla radice della repository.
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[desktop,dev]"
Set-Location frontend
npm ci
npm run build
Set-Location ..
```

Fedora, dalla directory in cui è stato copiato il progetto:

```bash
sudo dnf install python3 python3-pip nodejs npm
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[desktop,dev]'
cd frontend
npm ci
npm run build
cd ..
```

La prova Fedora deve verificare anche librerie grafiche richieste dalla versione Qt/PySide6 installata, Wayland e dialoghi file. Un errore del plugin di piattaforma Qt va risolto installando le dipendenze riportate dalla diagnostica, senza disabilitare la sandbox di Chromium. I test Fedora non sono ancora stati eseguiti in questa sessione.

Il lockfile npm viene usato da `npm ci`. `requirements-lock-windows.txt` descrive l'ambiente Windows iniziale e non è un lock portabile per Fedora; per una verifica riproducibile annotare le versioni effettive con `python -m pip freeze` e la versione Node.

## 2. Test automatici e compilazione della GUI

Windows:

```powershell
.venv/Scripts/python.exe scripts/verify_versions.py
.venv/Scripts/python.exe -m pytest -q
Set-Location frontend
npm run build
Set-Location ..
```

Linux: sostituire `.venv/Scripts/python.exe` con `.venv/bin/python`.

`pytest` verifica il motore, i contratti API, le revisioni, i CSV, gli aggregati e lo scambio fra archivi temporanei. Non apre finestre. `npm run build` controlla TypeScript e genera la GUI in `frontend/dist/`; non avvia il backend e non dimostra da solo che tutte le interazioni funzionino. Il bundle Plotly è voluminoso: il relativo avviso di Vite non è un fallimento della build.

## 3. Creare dati dimostrativi

```powershell
.venv/Scripts/python.exe scripts/demo.py --data .local/ui-test
```

Lo script corrente crea quattro atleti e quattro test basati sugli ERG originali. Si arresta su archivi già popolati. Esempi FIT/CSV in `examples/synthetic`, PDF di QA in `tmp/qa-fuorigiri`; vedere la checklist 0.3 sopra. Gli allegati personali originali non vengono copiati nelle fixture.

## 4. Aprire l'interfaccia

Finestra desktop Qt:

```powershell
.venv/Scripts/python.exe -m cycling_test.desktop --data .local/ui-test
```

Browser di sistema, stessa applicazione compilata:

```powershell
.venv/Scripts/python.exe -m cycling_test.desktop --data .local/ui-test --browser
```

Server senza apertura automatica di finestre:

```powershell
.venv/Scripts/python.exe scripts/serve.py --data .local/ui-test --port 8766
```

Aprire l'URL completo **GUI compilata** stampato nel terminale, incluso `#token=...`. Il token è generato a ogni avvio e salvato soltanto nella sessione del browser. Se si apre un nuovo browser o viene riavviato il backend, usare il nuovo URL completo. Un vecchio token causa «Sessione non autorizzata». Nella modalità desktop senza console la diagnostica del server viene scritta in `server.log` nella directory dati; il token non viene scritto nel log.

Il server ascolta soltanto su `127.0.0.1`. `Ctrl+C` lo arresta. Non avviare due server sulla stessa porta; scegliere per esempio `--port 8767` per una seconda istanza. Il database persistente è quello passato a `--data`.

### Sviluppo con aggiornamento automatico della GUI

Tenere in esecuzione il server precedente sulla porta 8766. In un secondo terminale:

```powershell
Set-Location frontend
npm run dev
```

Aprire l'URL **Vite sviluppo** stampato dal server Python, incluso il suo token. Vite usa `127.0.0.1:5173` e inoltra `/api` al backend `127.0.0.1:8766`. Per un backend su un'altra porta configurare `FUORIGIRI_API_URL` prima di avviare Vite:

```powershell
$env:FUORIGIRI_API_URL = 'http://127.0.0.1:8767'
npm run dev
```

Linux: `FUORIGIRI_API_URL=http://127.0.0.1:8767 npm run dev`. Non basta aprire `frontend/index.html` direttamente dal filesystem: serve il backend e, in sviluppo, Vite.

## 5. Checklist manuale della GUI

| Prova | Passaggi | Risultato atteso |
|---|---|---|
| Avvio e branding | Aprire l'elenco atleti e scorrere fino in basso. | Quattro profili sintetici; logo locale e testo fisso «Sviluppato da Luca Bontempi per Progetto Ciclismo - Rodengo Saiano A.S.D.». Nessun controllo per cambiarli. |
| Ordinamento | Cliccare due volte ATLETA; provare DATA e valori numerici nelle tabelle. | Indicatore crescente/decrescente e ordine coerente. I mancanti rimangono in fondo. |
| Profilo | Aprire un atleta, usare Modifica profilo, inserire data completa di nascita coerente con l'anno. | Modifica salvata; nome, anno e data disponibili dopo riapertura. Data/anno incoerenti sono rifiutati. |
| Antropometria | Aggiungere una rilevazione datata. | Tabella aggiornata e grafico peso/statura su assi con unità distinte. |
| Gruppi | Creare categoria e stagione figlia, assegnare l'atleta con date e anno di categoria. | Atleta unico con appartenenza storica; filtri e aggregati trovano la stagione selezionata. |
| Protocollo | Aprire Protocolli → Crea protocollo manuale; aggiungere fasi costanti o rampe e pubblicare. | Carico visibile; export ERG e JSON disponibili. Modifica tramite Nuova versione, senza alterare la precedente. |
| Import test | Nuovo test → scegliere atleta/protocollo → aprire `demo.fit` o `demo-trace.csv`. | Tracciato visibile prima del salvataggio. Per il protocollo `demo.erg`, fine sforzo 1440 s e peso 50 kg producono MAP 120 W; l'interpolazione è distinta. |
| Dati manuali | Inserire RPE 7, FTHR 180, Watt Soglia 200, FC a riposo e durata, recupero manuale o lattato. | Campi conservati; lattato non trasformato automaticamente in soglia. Le zone usano i riferimenti selezionati. |
| Ultima misura/default | Premere Proponi ultima antropometria; usare una data precedente a tutte le misure per verificare l'assenza di storico. | Proposta datata esplicita; nessuna misura futura presa automaticamente. Un preset configurato appare come stima. |
| Numero di zone | Aggiungere due zone nell'editor, controllare ordine e limiti, calcolare l'anteprima. | Anche sette zone funzionano. Limiti duplicati o decrescenti sono rifiutati. FC e potenza possono avere numeri diversi di zone. |
| Revisioni | Aprire un test → Correggi input e fine sforzo → cambiare RPE/fine sforzo, indicare motivo, ricalcolare e salvare. | Nuova revisione, risultati ricalcolati. I report precedentemente conservati restano scaricabili da Archivio e scambio. |
| CSV storico | Archivio e scambio → importare prima `xamples/synthetic/atleti.csv`, poi antropometria e storico; verificare anteprima prima della conferma. | Riconciliazione tramite ID; import ripetuto senza duplicati. Una riga errata blocca il lotto. |
| Aggregazioni | Storici e confronti → cambiare vista, stagione, categoria, atleta, metrica e modalità. | Media, mediana e conteggi aggiornati. La demo iniziale contiene un test per ciascuno dei quattro atleti: le due modalità hanno perciò lo stesso conteggio; aggiungere un secondo test dello stesso atleta/protocollo per verificarne la differenza. |
| Crescita/confronti | Consultare Variazioni antropometriche; scegliere due stagioni in Confronto sugli stessi atleti. | Delta e intervallo dichiarati; nessuna coppia inventata se manca una stagione. Per provare una coppia aggiungere un test con lo stesso protocollo in un'altra stagione. |
| Report | Scaricare PDF/Markdown di test e storico, poi CSV. | File leggibili; logo e credito fissi; zone dinamiche nei report; ZIP Markdown con immagini e manifest. CSV compatibili e dati estesi separati. |
| Ciclo di vita | Archiviare un atleta, controllare gli storici; eliminarlo e poi ripristinarlo dal filtro Eliminati. | Archiviato conservato negli storici; eliminato escluso dai nuovi calcoli; ripristino possibile. |
| Lingua | Selezionare English e poi Italiano. | Navigazione e form cambiano lingua. Il cambio ricarica la pagina: salvare prima eventuali bozze. Dati, codici e attribuzione fissa restano identici. |
| Offline e tastiera | Scollegare Internet mantenendo attivo il server locale; usare Tab/Invio e zoom browser. | Archivio, grafici e report locali utilizzabili; focus visibile, link esterni facoltativi. |

## 6. Provare due dispositivi, ruoli e conflitti senza cloud

**Corretto nella 0.4:** la società appena associata espone ora la prima sincronizzazione anche senza record locali. Il percorso seguente è disponibile dalla GUI. Il backup ZIP rimane distinto dall’invito e dal file di recupero accessi: vedere la guida collegata sopra.

Usare due directory di avvio diverse e due sessioni browser separate. Per evitare contaminazioni del token utilizzare profili/browser distinti oppure una sessione privata. Prima istanza `.local/pc-a` sulla porta 8766, seconda `.local/pc-b` sulla porta 8767. Basta una cartella locale vuota esterna a entrambe, per esempio `.local/scambio-test`, per simulare il trasporto; non serve un account cloud per questa prova.

1. Dal primo dispositivo creare una società separata in Gestisci società e selezionarla dal menu Società. Il dispositivo diventa fondatore.
2. Creare dati sintetici nella società. Specificare nome del collaboratore, ruolo e password di almeno 12 caratteri; scaricare l'invito cifrato.
3. Nel secondo dispositivo associare il file d'invito con la password e selezionare la società ricevuta. Inizialmente può essere vuoto: i dati arrivano con lo scambio.
4. Indicare in entrambi la stessa cartella di scambio, esterna ai database. Scambiare prima dal fondatore e poi dal ricevente. Verificare arrivo di società, atleta e protocollo.
5. Con un visualizzatore verificare consultazione ed export; tentativi di modifica devono essere rifiutati dal backend. Per il conflitto usare invece un invito Admin dati in un terzo archivio/profilo separato.
6. Per un conflitto, sincronizzare due admin, modificare offline lo stesso campo dello stesso atleta in entrambi, poi scambiare. In Archivio e scambio confrontare il record ricevuto e scegliere Mantieni locale o Accetta ricevuto. Scambiare di nuovo su entrambi: verificare convergenza.
7. Dal fondatore revocare un admin, scambiare e provare nuove scritture del dispositivo revocato. Le operazioni successive devono essere rifiutate/quarantinate. Le copie già ricevute e le chiavi di lettura esistenti non vengono cancellate da una revoca delle scritture.

L'associazione è per operatore/dispositivo tramite invito; non è un servizio di login remoto. Soltanto il fondatore gestisce inviti e revoche. `identity.json` contiene segreti locali: proteggere l'account e la cartella. Il backup dati ZIP attuale non include automaticamente le credenziali del fondatore: conservare separatamente e in modo protetto la cartella completa del workspace a programma chiuso prima di spostare il dispositivo fondatore.

Ripetere poi su due PC reali con il client cloud scelto: cartella disponibile offline, arrivi fuori ordine, interruzione client, copie conflittuali e riavvio. La prova locale non certifica il funzionamento di Google Drive/Dropbox né la compatibilità Fedora. L'app conferma scrittura/acquisizione locale, senza conoscere lo stato effettivo dell'upload cloud.

## 7. Verificare il pacchetto Windows

Dopo la build frontend:

```powershell
.venv/Scripts/python.exe scripts/build.py
dist/Fuorigiri/Fuorigiri.exe --smoke-test --data .local/smoke-02
dist/Fuorigiri/Fuorigiri.exe --data .local/ui-test
```

Controllare che `.local/smoke-02/smoke-ok.txt` esista. La prova smoke verifica import, logo e avvio del backend HTTP senza aprire finestre; aprire anche l'app per verificare la GUI. Distribuire tutta `dist/Fuorigiri/`, non il solo EXE. Ripetere su un PC pulito, senza Python/Node. La build non equivale ancora a installer firmato. Un bundle Linux va costruito e verificato su Linux.

Usare lo script di build del progetto: su Windows isola il PATH del sottoprocesso per evitare che DLL di altri programmi finiscano nel bundle. Nel collaudo è stata individuata una copia ICU di Poppler che impediva a Qt di caricarsi; la correzione è nello script, senza modifiche al PATH di sistema. Se si sta usando un bundle precedente alla correzione, ricostruirlo interamente prima di ripetere lo smoke test.

## 8. Registrare l'esito

Per le verifiche della revisione del 19 ottobre vedere anche la sezione seguente e [la relazione completa](archivio/REVISIONE_GENERALE_2026-10-19.md).

Annotare versione app, sistema operativo, versioni Python/Node, percorso dell'archivio di prova, risultato dei comandi e checklist eseguita. Per anomalie riportare passaggi minimi, risultato atteso/ottenuto e messaggio; usare screenshot privi di dati reali. Lo stato delle verifiche effettuate è in [VERIFICA.md](VERIFICA.md); requisiti e scelte ancora aperte in [REQUISITI_E_TODO.md](REQUISITI_E_TODO.md).

## 9. Isolamento società e dimensioni dell'archivio

Usare società e repliche sintetiche separate. La connessione in Archivio e scambio riguarda la società aperta; per collaboratori diversi usare cartelle cloud con permessi distinti. Un vecchio archivio multi-società deve essere bloccato per sync/inviti: scegliere una società nel menu non filtra lo scambio.

1. Cambiare società e ricaricare: la selezione deve rimanere; cambi rapidi durante il caricamento non devono riportare all'archivio precedente.
2. Nei protocolli verificare spazi tra numeri/unità, stati leggibili, durata dello sforzo Sprint/Wingate e assenza di durate inventate per protocolli di sola archiviazione.
3. Nel profilo controllare una serie iniziale e selezione fino a quattro, separate per protocollo/metodo. W/kg con peso stimato non deve produrre miglioramenti numerici nei confronti.
4. Su repliche di prova fare due sync senza modifiche: la seconda evita i pacchetti già acquisiti. «Verifica completa del canale» li rilegge; accessi/revoche vengono acquisiti anche nella sync ordinaria. Non alterare pacchetti reali per il collaudo.
5. Verificare che sincronizzare una società non aggiunga dati dell'altra e che le connessioni rimangano distinte.

Verifiche automatiche dai sorgenti, senza rigenerare dati. Un solo comando esegue in sequenza versioni, UI comune, common Python, linter `ruff`, controllo del formato (`ruff format --check`, `prettier --check`), `pytest`, `test:signals`, build frontend con `tsc` e `git diff --check`; continua dopo un errore e termina con un riepilogo (`--list` elenca i passi, `--skip build` ne salta uno). Richiede `ruff` dalle dipendenze di sviluppo (`requirements-lock-windows.txt` o `pip install -e .[dev]`):

```powershell
.venv/Scripts/python.exe scripts/verify.py
```

Lo stesso script gira nel workflow GitHub «Verify» (`.github/workflows/verify.yml`), per ora solo ad avvio manuale. I singoli comandi restano utilizzabili:

```powershell
.venv/Scripts/python.exe scripts/verify_versions.py
.venv/Scripts/python.exe -m pytest -q
npm --prefix frontend run test:signals
npm --prefix frontend run build
.venv/Scripts/python.exe scripts/verify_suite_ui.py
.venv/Scripts/python.exe desktop_entry.py --smoke-test --data .local/qa-smoke-nuovo
```

Misura in sola lettura di una società, senza chiavi o contatti cloud:

```powershell
.venv/Scripts/python.exe scripts/measure_archive_size.py --data ".local/demo-fuorigiri-completo/workspaces/<id-workspace-demo>" --out output/misure-archivio-aurora.json
```

Sostituire l'identificatore con quello della propria cartella società: cambia rigenerando la demo. Non usare la cartella contenitore di più società. La stima v1 richiede gli oggetti disponibili ed esclude versioni del provider e vecchi canali. [Misure e limiti](SYNC_DIMENSIONI_E_SCALABILITA.md). L'installer precedente non acquisisce automaticamente le modifiche ai sorgenti.


## Collaudo del menu Android — TD-98

Dopo aver compilato il frontend e ricostruito/installato l’APK secondo [la guida Android](ANDROID.md), aprire l’app nell’emulatore. Non basta aggiornare il browser o il frontend dist per aggiornare l’APK già installato.

1. Verificare testata compatta con pulsante Apri menu; società/sezioni/lingua non occupano più la pagina chiusa. Il primo avvio senza società continua a proporre la creazione o il collegamento come contenuto iniziale.
2. Aprire il menu: controllare selezione società, Gestisci società, tutte le sezioni, Info e lingua. Indietro deve chiudere il menu lasciando l’app aperta; riaprire e verificare il pulsante Chiudi finestra.
3. Da Gestisci società aprire il gestore: deve esserci un solo dialogo, senza menu ancora sotto. Chiudere senza creare o cambiare dati operativi.
4. Aprire Info anche senza società: versione, stato locale/offline, logo societario, attribuzione e licenza/limiti presenti. Sulle altre pagine Android nessun footer con questi elementi.
5. Aprire licenza/limiti da Info e chiudere con Indietro. Verificare lingua EN nel menu (Open menu/About), quindi ripristinare la lingua iniziale.
6. Su desktop verificare che sidebar, lingua nella testata e footer siano rimasti. Il layout Android dipende dal bridge nativo, non dalla sola dimensione del browser.

Catture attuali e provenienza in [screenshots/README.md](screenshots/README.md). Non usare credenziali o archivi reali per i fotogrammi.


## Collaudo Indietro, schede, moduli e riapertura — TD-99–101

Usare una società sintetica ripristinata come **Nuova copia indipendente**, mai un archivio operativo. Il backup completo di Velodromo Aurora include 22 profili e 150 test (gli elenchi operativi escludono gli eliminati e possono mostrarne meno). Nell’emulatore QA è stata creata una copia con fondatore QA Android, senza alterare le demo desktop.

1. In Atleti aprire Riepilogo società e Filtri atleti. Verificare ricerca, gruppo e stato; le schede mostrano anno, ultimo test e MAP solo quando disponibile. Massimo 20 schede per pagina.
2. In Test e analisi cercare Wingate, andare alla seconda pagina e aprire un test. Indietro chiude il dettaglio mantenendo pagina/filtro. Dal dettaglio aprire il profilo atleta e usare Indietro: tornare al medesimo elenco filtrato/pagina. Cambiare filtro riparte dalla prima pagina.
3. Aprire Nuovo atleta senza salvare; verificare campi e azione Salva raggiungibile. Modificare un campo, usare Indietro e provare Continua a modificare/Scarta e chiudi. Non deve sparire la bozza senza conferma. Non chiudere durante un salvataggio in corso.
4. Aprire una nuova prova manuale: campi essenziali davanti, altri risultati e recupero richiudibili, tempi con TimeInput in mm:ss/secondi e payload in secondi. Non salvare soltanto per provare il layout; fare vere prove di creazione solo nella copia QA.
5. Aprire una misura e una prova anaerobica/custom per verificare barra delle azioni, tastiere numeriche, validazioni e protezione della bozza. Controllare telefono verticale/orizzontale, tastiera estesa e TalkBack sul dispositivo reale: la prova con tastiera flottante dell’emulatore non li sostituisce.
6. Selezionare la società QA, arrestare completamente il processo (adb shell am force-stop org.fuorigiri.performancelab), riaprire dall’icona/Android Studio: stessa società e dati. Il numero della società non va confuso con l’operatore. Cancellare dati dell’app non è equivalente a chiuderla e cancella anche la preferenza.
7. Per l’ID ricordato non più presente usare un test di modello o un archivio QA dedicato; mai cancellare una società operativa. L’app deve mostrare la selezione esplicita, senza entrare in un’altra società.

Le pratiche riutilizzabili sono in [ANDROID_PRATICHE_SUITE.md](ANDROID_PRATICHE_SUITE.md), che rimanda al documento canonico del common. Le schede di telefono non cambiano la confrontabilità dei dati o i calcoli.

## Grafici touch, avvio e contesto Android — TD-102–104

1. Arrestare e riaprire l’app senza cancellarne i dati. Osservare fase nativa e lettura dell’archivio; controllare l’ultima società, hamburger a sinistra, contesto e ruolo. Nell’elenco senza figure Plotly non deve comparire tra le risorse caricate della WebView.
2. Aprire un test con tracciato: Scorri pagina deve essere selezionato. Trascinare sul grafico: scorre il dialogo, nessuno zoom involontario. I comandi sono sotto la figura. Attivare Esplora o Zoom e provare trascinamento/tocco; ripristinare la vista. Indietro deve tornare a Scorri pagina senza chiudere il test.
3. Aprire Vista ampia: parte in Scorri pagina. Indietro chiude solo la vista ampia; se è attivo Esplora/Zoom, la prima pressione disattiva il modo. Il test sottostante rimane aperto. Controllare che bozza e filtri non siano persi.
4. Aprire Valori e riepilogo del grafico: min/max/conteggi e dati originali, unità e — leggibili, massimo 30 righe per pagina. Verificare anche zero e assenze, senza equivalenza automatica di ascisse tra serie.
5. Provare lingua EN, focus e testo ingrandito. Verificare su telefono TalkBack, contrasto, gesture e tastiera: il solo emulatore non certifica questi comportamenti. Provare anche avvio senza Internet; per un errore controllato usare una copia QA, senza corrompere l’archivio abituale. Riprova deve mantenere i dati e non proporre reset.

Il chunk grafico differito riduce il JavaScript iniziale; l’APK contiene comunque Plotly. Misurare separatamente tempo del runtime Python, prima pagina utilizzabile e prima figura. L’indicatore è indeterminato perché non esiste una percentuale affidabile del lavoro completato.

### Vista ampia orizzontale — TD-105

Da telefono/emulatore verticale aprire un test con tracciato e Vista ampia: deve passare in orizzontale senza ricaricare la pagina o perdere il test. Attendere il ridimensionamento della figura. Attivare Esplora: il primo Back torna a Scorri pagina restando orizzontale, il successivo chiude la vista e ripristina l’orientamento precedente. Ripetere con X, verificare il test sottostante e provare anche partenza già orizzontale/autorotazione abilitata. Reload della WebView deve rilasciare la richiesta temporanea. Tablet/multiwindow e politiche di orientamento del sistema richiedono prove dedicate.

### Fullscreen e marchio — TD-106–107

Verificare logo Fuorigiri a sinistra del nome, senza wrap né schiacciamento, anche nei bootstrap. In Vista ampia devono sparire cornice, intestazione visiva e barre Android: rimangono figura, X flottante e Comandi grafico. Chiudere l’eventuale guida fullscreen del sistema prima delle foto. Aprire il pannello, provare dati e modi touch; Back esce dal modo prima di chiudere pannello/vista. Uscire con X e Back, verificando barre e orientamento precedenti ripristinati e test aperto. Provare swipe dal bordo per barre transitorie, lettore schermo e configurazioni diverse su dispositivo reale.

## Importazione antropometrica IMPORT-02

Importare prima atleti sintetici; nel CSV antropometria provare peso senza statura, fonti misurato/arrotondato/derivato/stimato, origine e fonte mancante (dichiarato). Verificare in anteprima nome completo e ID atleta, data, unità, fonte e origine; mai ID tecnico della rilevazione. Dopo commit, riaprire e correggere una misura derivata conservando origine, esportare CSV e verificare provenienza; reimport identico deve saltare duplicati. Fonte sconosciuta deve bloccare il lotto. Le misure derivate/stimate non diventano idonee ai modelli di crescita che richiedono misure misurate e valide. Gli import precedenti non vengono riscritti automaticamente.

## Assegnazione atleti GRUPPI-01

Dal profilo usare Aggiungi a un gruppo. Da Società e gruppi usare Aggiungi atleti su categoria o stagione: cercare, selezionare più atleti e confermare periodo e anno di categoria. Seleziona tutti riguarda i risultati della ricerca; le scelte precedenti restano selezionate anche cambiando ricerca. Un atleta già assegnato nello stesso gruppo in un periodo sovrapposto non è selezionabile. Verificare assegnazione dalla lista filtrata, conteggi aggiornati, appartenenze nel profilo e conservazione dei periodi storici. Il visualizzatore deve vedere i comandi disabilitati; un lotto con un riferimento invalido non deve salvare le altre righe.


## VO₂ nell’incrementale — 31 ottobre 2026

Nell’editor, **Consumo di ossigeno misurato · VO₂** consente misure temporizzate in L/min con fonte/nota e tempo mm:ss/secondi. Per serie lunghe preferire CSV. Il CSV temporale accetta `vo2_l_min`, oltre a `vco2_l_min`, `ve_l_min`, `peto2_mmhg`, `petco2_mmhg` opzionali; usare valori vuoti per dati mancanti. Esempio di intestazioni: `t,power,hr,lactate_mmol_l,vo2_l_min,vco2_l_min`. Tempo in secondi crescente, VO₂ positivo. In alternativa usare **VO₂: importazione gas e valutazione ventilatoria** per il CSV separato (`t,vo2_l_min`) e il suo offset rispetto al tracciato. Le fonti sono alternative: non associare misure manuali/file separato se il CSV temporale contiene già VO₂.

Il grafico principale permette di selezionare VO₂ con asse L/min indipendente. I punti manuali rimangono puntuali. VO₂peak è la massima media temporale nella finestra del preset (default 30 s), con copertura richiesta: due misure distanti non bastano. La relativa mL/kg/min richiede il peso del test. VO₂max non viene dedotto dal solo picco: conferma ed evidenze del laboratorio rimangono esplicite. Nel profilo scegliere VO₂peak dal selettore dello storico. L’export conserva `extended/vo2.csv` (risultati, finestra, copertura, fonte) e `extended/vo2_osservazioni.csv` (osservazioni, tempi, note). La modifica di un test crea una nuova revisione; gli storici non sono ricalcolati automaticamente.
