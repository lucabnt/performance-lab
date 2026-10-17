# Incrementale e report di archivio — versione 0.5

17 ottobre 2026. Attuazione degli step 1–4 autorizzata dall’utente, con scelta dei metodi sulla base delle fonti scientifiche disponibili. Il riferimento allegato è stato letto come esempio di struttura e aggregazioni, non come istruzione a importare dati personali né come fonte di formule validate. Nessun dato del PDF è stato inserito negli esempi o nell’archivio operativo.

## 1. Preset, migrazione e revisioni

Schema SQLite 3. Prima dell’aggiornamento di un database esistente con schema precedente viene creata `migrations/before-v3.sqlite`; i collegamenti SQLite sono chiusi prima di spostamenti/ripristini. Migrazione additiva: **nessun record o evento storico riscritto**, nessun risultato ricalcolato. Per tornare al vecchio software ripristinare la copia precedente in una destinazione separata, non abbassare manualmente `user_version`. Backup/ripristino supportano schema 3 e conservano il controllo di integrità.

Registro `analysis_preset`, con preset incorporati costante e rampa/discontinuo descrittivo. Le versioni personalizzate sono nuove pubblicazioni immutabili; non esiste PUT del preset. Ogni nuova analisi salva preset risolto e hash, versione motore, identità/hash protocollo, file originale/normalizzato, sessione, allineamento ed esclusioni. I test precedenti senza preset restano `legacy_unknown` nei confronti, mantenendo la versione motore nota quando presente. Protocollo, origine soglia, preset, motore e condizioni distinguono gli insiemi confrontabili.

API: GET/POST `/api/v1/analysis-presets`; il POST richiede nome, famiglia, versione, motivo, metodo e tutti i parametri. La GUI permette di selezionare un preset e pubblicarne una nuova versione. Nuovo risultato o revisione con motivo per applicarlo: nessuna modifica retroattiva automatica.

## 2. Motore costante e qualità

Attuata la [specifica incrementale](METODI_INCREMENTALE.md): campione mantenuto a sinistra, intervalli semichiusi, nessun riempimento di buchi >5 s o estensione dell’ultimo campione. Valori negativi/non finiti inutilizzabili; zero potenza/cadenza valido, zero FC/gas non valido. Medie/integrali e coperture non arrotondati prima delle decisioni. Le esclusioni con motivo sottraggono gli intervalli senza comprimere l’asse temporale né sottrarli dal denominatore della copertura.

Ultimo step incrementale costante completo della sequenza contigua, con durata prevista raggiunta e potenza valida ≥95%. Aderenza separata: errore medio W/%, MAE e RMSE; banda facoltativa in ±W e quota dei secondi validi in banda, senza invalidazione automatica. Nessun bollino di aderenza se la banda non è configurata. L’interpolazione dello step parziale rimane secondaria. Il risultato primario è il target nominale dello step, da leggere insieme alla potenza realmente osservata.

FC fine step: ultimi 30 s effettivi, copertura minima 80%; riferimento recupero ultimi 5 s, finestre marker −2/+3 s a 60/90/120 s, stessi gate di copertura. Parametri modificabili mediante nuovo preset. FC massima osservata escluso il campione al termine dello sforzo; non è una stima della FC massima fisiologica. Valori manuali e sensore restano distinguibili. Nessun coefficiente universale MAP→soglia/FTHR. Il coefficiente esplicito può essere documentato con provenienza e un avviso segnala l’assenza di calibrazione.

La scelta 95%/80%, il massimo gap e le finestre FC sono convenzioni software dichiarate, non soglie fisiologiche universali. Per rampe, fasi interrotte da recuperi o carichi non crescenti il metodo costante è inapplicabile: restituiti target terminale e media misurata degli ultimi 30 s, distinti dalla MAP per step. Nessuna conversione automatica fra protocolli.

## 3. FIT, allineamento e interfaccia

Import FIT con anteprima delle sessioni e scelta esplicita; duplicati e disordine temporale rifiutati per default. La correzione opzionale conserva l’ultimo record per timestamp e ordina i dati, con motivo registrato e originale conservato. CRC non valido/troncamento restano errori. Eventi timer fra record dividono intervalli osservati senza riempire dropout; lap e sessione conservati nella provenienza del tracciato.

Sul grafico si possono impostare inizio protocollo e fine sforzo con un clic. Marker per numero di step permettono di inserire pause di calibrazione/allineamenti di fase; sovrapposizioni rifiutate. Intervalli esclusi evidenziati e motivati. Target grafico e PDF seguono i marker. Campi strutturati per dispositivo, firmware, calibrazione, temperatura, cadenza prescritta, pre-test, arresto e modalità/postura del recupero. RPE CR10 o Borg 6–20, senza equiparazione automatica delle scale.

**Limite di collaudo:** i nuovi casi sono verificati con FIT sintetici controllati. Non sono ancora disponibili in questa sessione file autorizzati reali di ogni versione GoldenCheetah/MyWhoosh/Zwift: non si dichiara certificazione generale degli esportatori. L’aggiunta delle funzioni di import non sostituisce quel corpus INC-01.

## 4. Metodi specialistici: scelta scientifica e limiti

Non esiste un singolo algoritmo di soglia applicabile senza distinguere protocollo, popolazione e misura. Le indicazioni cliniche CPET sono usate per separare i risultati e documentare le misure; non per attribuire norme cliniche o pediatriche ai ragazzi della società.

### Lattato

Prelievo associato allo step o a carico esplicito; ritardo di prelievo dichiarato. Nessuna inferenza del carico per una rampa dal solo timestamp. Risultati distinti:

- potenza a 2 e 4 mmol/L con interpolazione lineare fra punti adiacenti, senza estrapolazione;
- Dmax con regressione cubica e massimo interno della distanza dalla corda degli estremi della curva;
- Dmax modificato cubico, corda dal punto osservato precedente il primo incremento >0,4 mmol/L all’ultimo punto.

Il codice risolve i punti stazionari del polinomio, senza scegliere il risultato da una griglia grafica. Almeno cinque carichi distinti e andamento non decrescente per i metodi cubici: è una scelta conservativa di qualità della versione 1, non un minimo universalmente validato. Attraversamenti ambigui, carichi duplicati, ancora mancante o fit senza massimo interno producono indisponibilità/motivo, non una falsa soglia. Nessun risultato sostituisce automaticamente Watt Soglia, FTP o MLSS. Fonte metodologica e dipendenza dal protocollo: [Jamnick et al., 2018](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0199794). Quello studio non valida ogni variante su soggetti giovani.

### Scambi gassosi

CSV canonico: `t,vo2_l_min`, opzionali `vco2_l_min,ve_l_min,peto2_mmhg,petco2_mmhg`. Unità esplicite, tempi strettamente crescenti, offset FIT/gas. Originale e normalizzato conservati e inclusi negli allegati del test. API POST `/api/v1/gas-traces`.

VO2peak: massimo di medie temporali mobili da 30 s nella fase incrementale, copertura 95%, finestra e massimo gap versionati; relativo alla massa solo se disponibile. Non usare i soli watt/FC per produrre VO2. La finestra è esplicita e modificabile: medie diverse producono risultati differenti; non è l’unica scelta scientificamente possibile. Riferimenti: [ATS/ACCP sul CPET](https://www.thoracic.org/statements/resources/pfet/cardioexercise.pdf), [studio in adolescenti su verifica e medie temporali, 2026](https://pubmed.ncbi.nlm.nih.gov/41543569/).

V-slope, equivalenti ventilatori, VO2/VCO2 nel tempo e gas end-tidal disponibili in grafici. Breakpoint esplorativi su medie di 30 s mediante regressione segmentata continua a due pendenze, con almeno quattro punti per lato e dieci intervalli validi: **non è una replica validata dell’algoritmo originale Beaver**. Produce suggerimenti `needs_review`, da confrontare con equivalenti/end-tidal e confermare mediante marker con evidenze. VT1/VT2 confermate e suggerimenti conservati separati. Fonte per il principio V-slope: [Beaver, Wasserman e Whipp, 1986](https://pubmed.ncbi.nlm.nih.gov/3087938/).

VO2max viene riportato solo come valore **verificato dichiarato dal valutatore**, con evidenza registrata; nessuna conferma automatica dal solo RER, età o superamento di un picco. La qualità delle evidenze non viene certificata dal software. È una distinzione deliberata: dati adeguati e giudizio esperto non possono essere sostituiti da una formula universale.

### Ripetibilità

Coppie scelte esplicitamente, stesso atleta/protocollo/metodo/condizioni/fonte, conferma di stabilità e motivo. Una coppia per atleta nello stesso insieme per evitare pseudo-replicazioni; massa stimata esclusa per W/kg. Errore tipico `SD(differenze)/sqrt(2)`, MDC95 `1,96 × SD(differenze)`, bias separato. Con meno di due coppie TE/MDC indisponibili; con almeno sei coppie disponibile nel risultato API un intervallo bootstrap percentile descrittivo a 2.000 repliche, seed conservato. Il limite di sei è una scelta operativa, non garanzia di precisione; campioni piccoli esplicitamente segnalati.

Le differenze stagionali non sono automaticamente ripetibilità. Nessuna soglia di miglioramento clinicamente importante dedotta da MDC. Riferimenti: [Hopkins, calcoli di affidabilità](https://sportscience.sportsci.org/resource/stats/relycalc.html), [Efron, 1979](https://doi.org/10.1214/aos/1176344552). API POST `/api/v1/repeatability`; GUI in Storici e confronti.

## 5. Report completi e sottoinsiemi

Modello unico `archive_report.build`, con filtri `organization`, `group`, `season`, `athlete`. Il gruppo padre include le edizioni figlie; le appartenenze storiche sono riferite alla data del test. Report atleta completo oppure limitato allo stesso ambito gruppo/stagione, quando questi filtri sono selezionati. Società include anche gli iscritti senza test; filtri esterni alla società rifiutati.

Contenuti: sintesi, copertura, indice delle sezioni, viste per stagione/età/categoria/anno di categoria/coorte e combinazioni, schede individuali con tutti i test e antropometria datata, riferimenti di protocollo/metodo. Medie, mediane, numerosità, assenti e intervalli descrittivi; grafici di mediana/IQR e traiettorie individuali. I confronti mantengono distinti protocollo, preset, motore, condizioni e origine soglia. Età per anno di nascita esplicitamente distinta dall’età esatta.

Viste con identica selezione di revisioni accorpate, con le altre prospettive indicate; avvertenze comuni riportate una volta, dati individuali non ricopiati in uno storico generale duplicato. Nessuna sezione anaerobica riempita con risultati incrementali: i relativi motori rimangono nella fase successiva confermata. Il formato è predisposto per estensione, senza dichiarare dati oggi assenti.

PDF e Markdown/ZIP con grafici e manifest completo; logo e attribuzione fissi nel footer PDF. API GET `/api/v1/archive/{org}/report-data` e `/report/pdf|md`; GUI «Archivio e scambio → Report completo dell’archivio». I filtri definiscono viste dello stesso modello, non copie indipendenti dell’archivio. Export singolo test comprende qualità, aderenza e grafici lattato/gas quando presenti.

## Verifica riproducibile

`python -m pytest -q`; TypeScript/Vite come nella guida di test. `python scripts/qa_incremental.py --data .local/qa-incrementale-05-nuova` crea **solo dati sintetici**: quattro atleti, otto test, due stagioni, cinque PDF e quattro ZIP in `output/pdf/`. Rifiuta un archivio già occupato. Avvio GUI con `python scripts/serve.py --data .local/qa-incrementale-05-nuova --port 8766`. Distribuire l’intera directory `dist/Fuorigiri` dopo build nativa.

Le prove software e i controlli visivi dei PDF non equivalgono a validazione fisiologica, interoperabilità con tutti i laboratori o collaudo Fedora. Lo stato di INC va letto con questi limiti: le funzioni sono sviluppate, il corpus reale e la validazione esterna non vengono inventati per dichiarare chiusa una voce.
