# Sprint breve e Wingate - metodo 1, software 0.7

## Aggiornamento UI 0.8

Definire Sprint/Wingate in **Protocolli → Crea protocollo**; nuove versioni dalla scheda corrispondente. Registrare esecuzioni in **Test e analisi → Nuovo test**, scegliendo protocollo e modalità. Importatore con sessioni/duplicati, click sul grafico per l’inizio, zoom ed esclusioni motivate. Campi facoltativi disponibili anche sui protocolli supportati. [Flusso e campi custom](PROTOCOLLI_E_CAMPI_CUSTOM.md); [corpus completo per il collaudo](CORPUS_SINTETICO_08.md). Le indicazioni UI 0.7 successive sono superate da questo flusso; le formule rimangono quelle del metodo 1.

## Scelta proposta e implementata

Tre famiglie distinte: Sprint breve (durata configurabile 3-10 s, default 6 s), Wingate 30 s e Wingate 15 s. Lo storico incrementale conserva il proprio motore e le proprie metriche; un picco anaerobico non diventa MAP, FTP o soglia. Nessuna conversione automatica fra durate, formule di previsione della prova da 30 s o classificazione normativa per età.

Il protocollo è una versione immutabile. Memorizza durata, coppia frenante specifica se disponibile, descrizione del carico, partenza, posizione, dispositivo, riscaldamento, finestra del picco, finestra finale, copertura minima e intervallo massimo accettato fra campioni. Un’altra modalità di frenata si descrive esplicitamente: non viene convertita automaticamente in coppia o percentuale del peso. Nuove versioni possono riferirsi alla precedente e richiedono una motivazione.

UI: **Test e analisi → Test anaerobici e potenza neuromuscolare → Nuova prova / protocollo**. Prima definire un protocollo, poi scegliere atleta, data, peso e fonte. Inserire risultati manuali oppure caricare FIT/CSV temporale e indicare l’inizio effettivo dello sforzo in secondi. Calcolare l’anteprima prima del salvataggio. Il dettaglio archiviato mostra risultati, tracciato, provenienza e condizioni; le correzioni richiedono motivo e revisione corrente. Per riepiloghi CSV la correzione conserva protocollo e provenienza storica; originale nella prima revisione e nel lotto di importazione. Il registro delle revisioni e la sincronizzazione sono comuni al resto dell’app.

## Storico fornito

Il CSV privato contiene 38 prove, 16 atleti e il codice ANA-15-070. L’utente ha confermato: **Wingate di 15 s con coppia frenante di 0,70 N·m/kg**. Questa è coppia specifica, non 0,070 kp/kg. Dispositivo, tipo di partenza, posizione, finestra del picco e formula dell’indice di fatica rimangono non documentati.

Profilo di importazione `test_anaerobico`: intestazione compatibile con il file fornito. Obbligatori test_id, atleta_id, data ISO e protocollo_id; tutti i risultati sono facoltativi. Prima importare le anagrafiche con ID esterni coincidenti. Anteprima con errori per riga, conferma atomica, controllo duplicati e annullamento lotto riusano il sistema esistente. Le righe originali rimangono in historical_fields e il file originale nel lotto, senza modificare i valori mancanti in zero. La fonte del peso `derivato` resta distinta da `misurato`.

L’indice storico `indice_fatica_ws` conserva unità W/s e formula non verificata; non viene trasformato in percentuale e non è equiparato alla nuova pendenza calcolata. Nel file fornito lavoro/media implicano durate circa 15,08-15,41 s. L’app segnala l’incoerenza rispetto alla durata nominale, conserva i valori e non corregge automaticamente lavoro, media o durata. La formula storica non è dedotta dalla corrispondenza numerica dei risultati.

I dati privati non sono copiati nella repository o nella distribuzione. Gli esempi pubblici sono sintetici.

## Formule e qualità del tracciato

Motore `anaerobic-1`. Intervallo analizzato: [offset, offset + durata protocollo]. Ogni campione valido rappresenta il tratto fino al campione successivo; nessuna estrapolazione oltre l’ultimo timestamp. Pause, esclusioni motivate e intervalli superiori al limite del protocollo non contribuiscono. Default intervallo massimo 2 s: è una convenzione del software, non una garanzia di risoluzione del misuratore.

- Lavoro meccanico osservato: somma P × dt / 1000, in kJ. Non è una misura diretta della capacità anaerobica metabolica.
- Copertura: secondi di potenza validi / durata nominale. Completezza ≥95%, distinta dalla disponibilità di una media completa.
- Media dell’intera prova: lavoro / durata, soltanto con copertura integrale; altrimenti assente. La media sui soli secondi osservati resta un dato tecnico separato.
- Picco: migliore media temporale sulla finestra del protocollo, default 1 s. Finestre valide solo se completamente osservate; vengono valutati i punti di variazione e i punti traslati della durata della finestra. Non si presenta il massimo campione a 1 Hz come picco istantaneo.
- Migliori 1 s e 5 s: finestre esplicite, indipendenti dal picco primario. Il tempo al picco è l’inizio della prima finestra migliore, relativo all’inizio dello sforzo.
- Potenza finale: media sull’ultima finestra, default 1 s; assente se non integralmente osservata.
- Calo picco-finale: 100 × (picco - finale) / picco. Pendenza: (picco - finale) / (inizio finestra finale - inizio finestra picco), W/s, se il denominatore è positivo. Sono definizioni operative versionate, non una formula universale di fatigue index.
- W/kg da peso registrato con fonte; masse stimate escluse dagli aggregati W/kg come negli incrementali. Cadenza media ponderata nel tempo; massimi FC e cadenza solo entro la prova osservata. Una lacuna può nascondere il vero massimo: avviso sempre visibile.

I riepiloghi manuali non sovrascrivono i risultati calcolati da tracciato. Una prova è manuale oppure calcolata; entrambe conservano un proprio snapshot del protocollo.

## Comparabilità e report

La chiave conservativa include snapshot del metodo, durata, carico, dispositivo, partenza/posizione, finestre, motore, origine manuale/calcolata/storica e condizioni registrate. Storici, medie, mediane e variazioni non uniscono automaticamente prove con chiavi diverse, neppure dello stesso atleta. Questo può separare versioni equivalenti: una futura equivalenza deve essere una decisione esplicita e documentata, non una somiglianza di nome.

Lo storico ANA-15-070 può mostrare andamenti e aggregati **descrittivi**, ma l’omogeneità delle condizioni non è verificata. Un grafico non certifica comparabilità scientifica. È separato dalle nuove prove con protocollo dichiarato. Neppure i picchi di Sprint/15/30 s sono uniti automaticamente: possono essere confrontati esplorativamente solo discutendo carico, accelerazione, dispositivo e finestre.

Report singolo PDF e Markdown con grafico, metriche, peso, carico e qualità. Report società/gruppo/stagione/atleta riutilizzano il medesimo albero di selezione, con sezioni anaerobiche, aggregazioni separate e storici di picco/media; niente colonne MAP riempite con risultati anaerobici. Logo societario e attribuzione fissi nel footer.

CSV ZIP: `test_anaerobico.csv` conserva l’intestazione storica; `extended/test_anaerobico.csv` aggiunge tipo, durata, coppia, dispositivo, finestre e metriche esplicite. Per reimportare nuovi protocolli usare il file esteso: protocollo_id da solo non permette di indovinarne durata o significato. Anche l’importazione estesa è un riepilogo dichiarato, non ricrea campioni o certificazione del metodo originario. Per un ripristino fedele usare il backup dell’archivio.

## Basi scientifiche e limiti

La letteratura supporta la distinzione fra picco, media e calo e la necessità di standardizzare la prova; non offre un unico coefficiente universale per equiparare protocolli diversi. Lo studio sul Wingate abbreviato ha osservato affidabilità migliore per picco/media che per indice di fatica nella popolazione studiata; non valida automaticamente giovani ciclisti, qualunque carico o qualunque software. [Studio primario 15 s, PMID 22516906](https://pubmed.ncbi.nlm.nih.gov/22516906/).

Il test di 6 s è documentato come strumento per la potenza di picco in atleti di endurance; ciò motiva il default Sprint, senza renderlo equivalente al Wingate. [Studio primario, PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0307325).

Le finestre di 1 s e la pendenza qui definite sono convenzioni esplicite del software. Non si stimano VO2max, contributi energetici, fibre muscolari, diagnosi o percentile da queste prove. La gestione operativa del test fisico resta dell’operatore qualificato.

Restano da validare con apparecchiatura e corpus reali: inizio applicazione del carico, risoluzione temporale, compensazione inerziale del dispositivo, calibrazione, validità test-retest e significato della formula storica W/s. Non si dichiara supporto verificato a ogni esportatore FIT. Non sono implementati acquisizione/controllo in diretta dell’ergometro né confronto statistico fra famiglie o conversioni predittive; non sono necessari per archiviare e analizzare le tre famiglie richieste.

## Verifica riproducibile

`python scripts/generate_anaerobic_examples.py` crea tre FIT sintetici (inizio sforzo 60 s), manifest e CSV storico fittizio in examples/synthetic. Importare prima atleti_anaerobico.csv, poi test_anaerobico.csv. Per FIT definire i tre protocolli corrispondenti; usare offset 60 s e peso 60 kg. `python scripts/qa_anaerobic.py` prepara un archivio isolato .local/qa-07 e due PDF sotto output/pdf. `python scripts/serve.py --data .local/qa-07 --port 8769` stampa il link completo della GUI, dopo la compilazione frontend. Il comando QA si ferma se l’archivio contiene già test.

Test automatici: `python -m pytest -q tests/test_anaerobic.py`; coprono integrali, finestre, copertura, esclusioni, offset, tre FIT, provenienza, CSV, revisioni e report. La verifica software non sostituisce una validazione scientifica esterna.
