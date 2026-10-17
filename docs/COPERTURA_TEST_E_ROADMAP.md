# Copertura dei test e sviluppi futuri

Stato della preview Fuorigiri Performance Lab 0.3, 17 ottobre 2026. Le priorità seguenti sono proposte di prodotto; non prescrivono protocolli di esercizio né dichiarano validazione fisiologica.

## Cosa copre oggi

Import ERG e protocolli versionati anche senza step, FIT/CSV di campioni, scelta esplicita offset/fine sforzo, medie temporali e copertura dei canali, MAP operativa dall'ultimo step costante completato, interpolazione separata, FC osservata, recupero, antropometria datata, valori manuali, soglia dichiarata o stimata da coefficiente esplicito, FTP dichiarata, N zone, report e storici aggregati. Nei test senza campioni i risultati sono dichiarati. Un coefficiente della MAP non misura automaticamente la FTP o una soglia ventilatoria.

## Lacune per una copertura completa dell'incrementale

| Priorità | Mancanza attuale | Criterio per considerarla risolta |
|---|---|---|
| P0 | Validazione su FIT **reali** esportati da GoldenCheetah, MyWhoosh e Zwift | Corpus anonimizzato e autorizzato con pause, più sessioni, lap, dropout, orologi, sensori e confronto con risultati attesi. I quattro FIT sintetici non sostituiscono questo collaudo. |
| P0 | Completamento step controlla durata e copertura ≥95%, non l'aderenza al target | Regola condivisa/versionata su tolleranza W/%, tempo valido, overshoot e cadenza; casi di arresto, mancata esecuzione e rullo in ritardo. Il requisito “ultimo step completo” non basta a scegliere queste tolleranze. |
| P0 | Correzione temporale solo con offset e fine sforzo numerici | Selezione visuale, avviso sull'allineamento, anteprima degli step, pause e segmenti esclusi riproducibili; motivi di interruzione. |
| P1 | Rampe visualizzabili, ma MAP per rampa non definita; nessun motore dedicato a protocolli discontinui | Tipo di protocollo esplicito e algoritmo specifico, senza applicare la convenzione degli step costanti. |
| P1 | Acquisizione prelievi di lattato senza curva/algoritmo di soglia | Associazione certa al carico, grafico lattato-potenza, metodi scelti/versionati e revisionabili; intervalli, qualità e limiti. Valore a 4 mmol/L, Dmax e soglie individuali non sono sinonimi. [Studio originale sulle soglie nei ciclisti](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0163389). |
| P1 | Condizioni, dispositivo, calibrazione, ambiente e motivi di arresto soprattutto nelle note | Campi strutturati, taratura, tipo rullo/powermeter, temperatura, cadenza prescritta, stato pre-test e deviazioni dal protocollo; confrontabilità resa visibile. |
| P1 | FC fine step e recupero hanno finestre convenzionali fisse | Preset di analisi versionati, finestre configurabili, confronto manuale/sensore e riepilogo della copertura per metrica nei report. |
| P1 | Assenza di misure di scambio gassoso | Import sincronizzato VO2, VCO2, ventilazione e marker; supporto separato per VO2peak/VO2max e VT1/VT2. Un FIT con soli watt/FC/cadenza non misura VO2max. [Dichiarazione ATS/ACCP sul CPET](https://www.thoracic.org/statements/resources/pfet/cardioexercise.pdf). |
| P1 | Confronti descrittivi, senza errore tipico o minima variazione rilevabile | Ripetibilità intra-atleta per metodo/dispositivo, intervalli con n adeguato, separazione cambiamento reale/rumore; niente percentili o diagnosi pediatriche inventati. |
| P1 | Dati storici senza versione e origine talvolta incompleta | Riconciliazione assistita del protocollo, provenienza campo per campo e filtri di confrontabilità; mantenere sempre l'originale. |
| P2 | Interoperabilità e distribuzione ancora da consolidare | Ripristino backup guidato, migrazioni testate, keychain, rotazione chiavi, sincronizzazione automatica con audit, CI Windows/Fedora su installazioni pulite, firma/distribuzione pacchetti e localizzazione completa. |

Il disegno del protocollo e il metodo di analisi influenzano i risultati: non basta cambiare un'etichetta per rendere equivalenti test diversi. [Studio sperimentale sulle variabili del test incrementale](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0199794).

## Test non prioritari candidati

| Candidato | Valore per la società | Dati / analisi da aggiungere | Priorità proposta |
|---|---|---|---|
| Sprint breve / potenza neuromuscolare (es. 6 s) | Seguire picco e potenza su finestre brevi | Segmenti di sprint, partenza, rapporto, resistenza, cadenza, picco 1 s/5 s/6 s; frequenza campioni e smoothing espliciti. [Studio originale su sprint di 6 s](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0307325). | Dopo completamento incrementali |
| Wingate 30 s e sprint ripetuti | Profilo di potenza breve e decremento tra ripetizioni | Carico del dispositivo, durata, picco/media/minimo, lavoro e definizione dell'indice di fatica; recuperi tra sprint. Non etichettare genericamente ogni sprint su smart trainer come Wingate. [Protocollo sperimentale di Wingate ripetuti](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0242439). | P2 |
| Profilo potenza-durata / Critical Power e W′ | Confrontare prove massimali di diversa durata | Più prove, durata e condizioni, fitting CP/W′, residui e incertezza. Test 3 min all-out come metodo distinto, non conversione universale della MAP. [Studio originale 3 min all-out](https://pubmed.ncbi.nlm.nih.gov/17473782/), [limiti nei ciclisti élite](https://pubmed.ncbi.nlm.nih.gov/27834562/). | P2 |
| Time trial / test FTP | Monitoraggio pratico sul campo | Durata effettiva, potenza media, pacing e metodo dichiarato. Eventuale coefficiente di conversione esplicito e validato per quel preset, non applicato a tutti i test. | P2 |
| VO2peak/VO2max e soglie ventilatorie | Analisi di laboratorio con dati adeguati | Flussi respiratori, calibrazione, elaborazione respiro per respiro, finestre medie e criteri di verifica; supervisione e interpretazione competenti. Vedi fonte ATS sopra. | P3: richiede integrazione strumentale |
| Submassimale a carico costante / recupero | Confrontare risposta FC e stabilità a carico ripetuto | Segmenti steady-state, durata, deriva, condizioni standard e recupero. Sono descrittori di risposta, non stime universali di VO2max. | P2 |
| Lattato a carico costante / MLSS | Approfondire il comportamento del lattato su prove ripetute | Serie datate di prelievi e carichi, criterio dichiarato, più sedute e confronto con incrementale. [Ricerca originale su durata e metodi di soglia](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0199794). | P3 |

Le priorità sono una **valutazione progettuale**, non un risultato delle fonti. Per gli atleti giovani non si trasferiscono automaticamente protocolli o valori normativi di adulti; la scelta esecutiva resta al professionista competente.

## Estensione architetturale

Prima dei nuovi motori introdurre `test_type`, `analysis_method` versionato e un contratto comune di risultati con unità, fonte, validità e incertezza. L'attuale campo MAP non deve diventare un contenitore per peak sprint, CP o VO2max. Protocolli, importazioni e libreria di grafici rimangono condivisibili; ogni motore deve dichiarare canali richiesti e metriche realmente calcolabili. Report e storici devono aggregare soltanto metriche omogenee per tipo, metodo e versione. Nessun motore per questi test aggiuntivi è incluso nella 0.3.
