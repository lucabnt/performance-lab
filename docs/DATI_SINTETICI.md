# Dati sintetici e scenari di collaudo

Corpus standard aggiornato con crescita/maturazione; i vecchi archivi generati non si aggiornano automaticamente. [Avvio e rigenerazione conservativa](TESTARE_IL_PROGETTO.md).

Persone, società, misure, risultati e condizioni sono **interamente fittizi**. I nomi possono coincidere casualmente con persone reali. Il corpus non legge CSV privati, non contiene token cloud e non rappresenta una validazione clinica o un modello di allenamento.

## Avvio immediato e rigenerazione

Archivio di una generazione precedente (per i nuovi casi maturativi rigenerarlo esplicitamente o usare una cartella nuova): `.local/demo-fuorigiri-completo`. Per avviarlo da sorgenti:

```powershell
.venv/Scripts/python.exe scripts/serve.py --data .local/demo-fuorigiri-completo --port 8771
```

Aprire l’URL **completo con token** stampato dal comando e selezionare Velodromo Aurora - SIMULAZIONE oppure Pedale del Lago - SIMULAZIONE. Anche l’eseguibile può aprire questo corpus senza Python/Node: `Fuorigiri.exe --data ".local\demo-fuorigiri-completo"` (adattare il percorso al proprio checkout).

Per creare un’altra copia usare una destinazione **nuova**:

```powershell
.venv/Scripts/python.exe scripts/demo_suite.py --data .local/demo-fuorigiri-completo-nuovo
.venv/Scripts/python.exe scripts/serve.py --data .local/demo-fuorigiri-completo-nuovo --port 8771
```

Per svuotare e ripopolare lo stesso percorso, dopo aver chiuso app, server e repliche:

```powershell
.venv/Scripts/python.exe scripts/demo_suite.py --data .local/demo-fuorigiri-completo --reset
```

La cartella precedente viene conservata in `.local/demo-backups`, senza cancellazione definitiva. Sono ammesse soltanto destinazioni dirette nella `.local` del progetto; radici, sottocartelle, link e archivi aperti vengono rifiutati. I backup raw vanno ripristinati al percorso originale, perché il registro contiene percorsi assoluti. [Procedura completa, avvio, ZIP e controlli](TESTARE_IL_PROGETTO.md).

Su Linux usare Python dell’ambiente attivo. Senza `--reset` la generazione rifiuta cartelle già esistenti e non sovrascrive archivi. Il seed 481516 rende riproducibili gli scenari e le misure; identità, firme, revisioni e percorsi sono generati per l’istanza e non sono identici byte per byte. Lo scambio iniziale delle repliche può richiedere qualche minuto: attendere il riepilogo finale e `manifest-demo.json` prima di iniziare le modifiche.

Il set ridotto `--small` serve ai test automatici, non sostituisce il corpus completo. I precedenti script demo/QA 0.3-0.7 restano fixture minime di regressione.

## Composizione

| Dati | Contenuto |
|---|---|
| Società | 2 archivi indipendenti, 22 + 10 atleti |
| Persone | 32 profili, M/F, anni di nascita diversi e uno ignoto, omonimi con ID distinti, attivi/archiviati/eliminati |
| Periodi | Test 2024–2026; misure ordinarie a febbraio, giugno e ottobre e serie maturative dal 2022 |
| Antropometria | 264 rilevazioni; pesi/stature mancanti in casi selezionati, crescita plausibile, masse misurate/arrotondate/dichiarate/stimate |
| Maturazione | 4 casi per società: picco maschile/femminile, dati insufficienti, adulto; 48 misure aggiuntive totali, antropometria avanzata e 8 snapshot; repliche e backup inclusi |
| Gruppi | Categorie con sottogruppi annuali, appartenenze datate e passaggi di categoria |
| Prove | 192 record: 150 + 42, inclusi 2 eliminati logicamente; 190 visibili nella lista ordinaria |
| Protocolli | 12 versioni per società: ERG originali, scheda manuale senza step, Sprint, Wingate 15/30, Wingate 15 con finestra diversa, custom, rampa, discontinuo e versioni archiviate |
| Tracciati | FIT decodificati, CSV temporali, riscaldamento/sforzo/recupero; potenza rumorosa, risposta FC ritardata, calo di cadenza |
| Specialistici | Lattato associato agli step, gas sintetici, recupero FC, RPE, soglie dichiarate, preset e schema a 7 zone |
| Metadati custom | Parametri di protocollo, temperatura/sonno, risultati numerici con unità, scelte e booleani con valori false e assenti |
| Accessi | Fondatore, replica Admin, replica Visualizzatore, invito revocato |
| Ripristino | Backup dati e recupero accessi SOLO DEMO; mai usare le credenziali dimostrative su dati reali |

Conteggi e identificativi esatti dell’istanza sono in `manifest-demo.json`. I record eliminati e gli atleti senza prove servono a verificare assenze, filtri e copertura; non sono errori da correggere automaticamente.

## Matrice di verifica

| Funzionalità | Caso da usare | Esito atteso |
|---|---|---|
| Società e isolamento | Cambiare società nel selettore | Persone, prove, protocolli e aggregati del relativo archivio |
| Omonimie | Due Andrea Villa nella prima società | Profili distinti per ID e nascita; nessuna fusione per nome |
| Gruppi/anni/coorti | Confrontare 2024-2026 | Appartenenza relativa alla data del test, passaggi di categoria |
| Stato e assenze | Filtri atleti e protocolli; profilo senza prove | Archiviati/eliminati separati, nessun risultato inventato |
| Incrementale | FIT SIM-1-001 e SIM-1-002, tre stagioni | Step, FC/recupero, lattato, crescita e progressione |
| Lacune | Incrementale SIM-1-002 del 2025 | Mancanze FC e potenza, coperture e avvisi; niente riempimento con zero |
| Gas | Primo atleta 2026; gas-simulati.csv | VO2peak e grafici gas; VO2max non attribuito automaticamente |
| Zone | Primo atleta 2025 | Schema potenza con 7 zone, distinto dal default a 5 |
| Ripetibilità | 15 e 18 marzo 2026, stesso atleta/protocollo | Coppie confrontabili; conferma manuale delle condizioni stabili |
| Rampa/discontinuo | Due prove descrittive di ottobre 2026 | Carico e media terminali; niente MAP da step attribuita impropriamente |
| Scheda senza ERG | Incrementale storico senza programma | Nuova prova manuale disponibile; file disabilitato finché mancano step |
| Sprint/Wingate | Prima e seconda persona, file per famiglia | Offset 60 s, durata dal protocollo, picco/media/lavoro/calo |
| Copertura anaerobica | SIM-1-003-wingate15.fit | Copertura incompleta e media dell’intera prova non disponibile |
| Versioni | Wingate 15 v1 e v2 | Finestre 1 e 5 s separate negli aggregati |
| Storico Wingate | societa-1-wingate-storico.csv | Duplicati già presenti saltati; W/s dichiarati non convertiti in % |
| Custom | Sprint ripetuti 5 × 6 s, 2025/2026 | Risultati dichiarati, booleani false conservati, campi mancanti distinti da zero |
| Media/mediana | Storici → metrica custom e Tutti i test | n/media/mediana separati per protocollo, versione e schema |
| Revisioni | Primo incrementale 2024; correzione di una nuova prova | Motivo e vecchia revisione conservati; salvataggio concorrente respinto |
| CSV validi | import-atleti-nuovi → import-antropometria → import-aerobico | Import nell’ordine, conferma atomica, duplicati saltati al secondo passaggio |
| CSV errati | import-errori.csv | Anteprima con errori; nessuna importazione parziale |
| FIT multiplo | fit-due-sessioni.fit | Due sessioni da selezionare; è una fixture del decoder, non due attività reali |
| FIT duplicati | fit-timestamp-duplicati.fit | Rifiuto; keep_last richiede motivo esplicito |
| FIT corrotto | fit-crc-corrotto.fit | Rifiuto CRC senza test parzialmente salvato |
| Timer | tracciato-pausa.csv | Intervalli in pausa esclusi dai calcoli |
| Report | Società, categoria, anno, atleta e singolo | Selezione coerente, campi custom inclusi, footer e unità leggibili |
| Export | ZIP CSV e backup | CSV base + campi custom JSON tipizzati nel CSV esteso; backup fedele per ripristino |

## Controlli numerici indipendenti

`oracoli-numerici.json` contiene valori attesi dedotti dalla costruzione, non ricalcolati dal motore:

- Wingate 15 s costante 500 W, massa 50 kg, offset 0: picco/media 500 W, 10 W/kg, lavoro 7,5 kJ, calo 0%, copertura 100%.
- Incrementale con step 100/150/200 W di 60 s; fine sforzo 150 s e peso 50 kg: ultimo step completo 150 W, 3 W/kg, interpolazione separata 175 W. Importare prima oracolo-incrementale.erg con riscaldamento 0.
- Tre valori custom 700/700/1300 W: media 900, mediana 700, n=3 con modalità Tutti i test.

Questi pochi file sono controlli didattici volutamente semplici, separati dai tracciati rumorosi realistici.

## Repliche, conflitti e recupero

Avviare altre istanze sulle radici `repliche/admin` e `repliche/viewer`, con porte diverse. Entrambe sono associate alla prima società; il Visualizzatore riceve ma non modifica. La cartella `scambio` è locale, separata dai database operativi e già configurata.

Fondatore e Admin contengono due modifiche offline concorrenti alle note dello stesso atleta. Per esercitare la risoluzione: sincronizzare prima Admin, poi Fondatore, quindi osservare e risolvere esplicitamente il conflitto. Sincronizzare di nuovo entrambe le parti e il Viewer. Non unire gli archivi copiando SQLite e non usare questa cartella con società operative.

Gli inviti e il recupero dimostrativi usano la password pubblica `SoloDemo-NonUsareInProduzione-2026`. L’invito revocato deve restare non autorizzato dopo l’acquisizione del controllo di revoca. Il backup della società può essere provato come copia indipendente o di consultazione; il recupero originale richiede il suo file di recupero e una destinazione senza l’originale già registrato.

Lo ZIP portabile della demo contiene backup per **copia indipendente** e fixture, non identità private o registri con percorsi assoluti. Le repliche già collegate sono disponibili nel corpus locale o si rigenerano da sorgenti.

## Perimetro delle prove

Il corpus copre i percorsi dati/UI offline e le condizioni di errore controllabili sul PC. Le API cloud usano i test con server/risposte simulate già presenti: nessun dataset può sostituire registrazioni OAuth e verifica con account reali. Analogamente non certifica driver, misuratori, dati fisiologici, PC pulito, Fedora o Android. I riferimenti a consenso/metodi scientifici restano nei documenti del motore; le misure inventate non sono una nuova fonte scientifica.
