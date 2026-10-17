# Copertura dei test e sviluppi futuri

## Aggiornamento software 0.5

Nuove funzioni sviluppate per INC-01–10: preset/migrazioni, motore costante, correzioni e allineamento, metodi lattato/gas/ripetibilità, report completi gerarchici e grafici. La tabella sottostante conserva le lacune della 0.4: gli stati attuali e le distinzioni fra implementazione e collaudo sono nel [registro requisiti](REQUISITI_E_TODO.md) e nel [dettaglio 0.5](IMPLEMENTAZIONE_INCREMENTALE_05.md). Corpus FIT reali, validazione specialistica esterna e consolidamento INC-11 non sono dichiarati completati.


Stato della preview Fuorigiri Performance Lab 0.4, aggiornamento del 17 ottobre 2026. L'utente ha confermato che **tutte le lacune dell'incrementale elencate sotto sono da implementare**, comprese quelle di priorità P2. Successivamente si procederà con Sprint breve / potenza neuromuscolare, Wingate 30 s e Wingate 15 s. Questa pianificazione non prescrive protocolli di esercizio e non dichiara validazione fisiologica. Nessuna lacuna INC è completata nel suo insieme: la 0.4 realizza il primo sottoinsieme operativo di INC-11 (TD-45–49 e parte di TD-50), come descritto nella [guida società/accessi](SOCIETA_BACKUP_E_ACCESSI.md).

## Sequenza di sviluppo confermata

1. **Fase 1 — Copertura completa dell'incrementale e consolidamento del prodotto:** INC-01–11, con ripristino, prima sincronizzazione e ruoli descritti in TD-45–50 del [registro requisiti](REQUISITI_E_TODO.md). Ogni voce deve superare il suo criterio di accettazione; formule, corpus reale e prove sulle piattaforme sono dipendenze da acquisire, non esclusioni dal perimetro.
2. **Fase 2 — Android:** fattibilità, sviluppo e collaudo dell’app autonoma offline (TD-57/AND-01–05), con report e scambio interoperabile con desktop. Contratti e spike possono essere preparati già durante il consolidamento della fase 1. [Architettura Android](ANDROID.md).
3. **Fase 3 — Primi motori aggiuntivi:** Sprint breve / potenza neuromuscolare (TD-52), Wingate 30 s (TD-53), Wingate 15 s (TD-54). Il 15 s è stato usato in passato dalla società e deve avere una propria identità/versione, con metodo storico documentato. Prima di implementarli servono specifiche del protocollo e risultati attesi; non si deducono automaticamente dal nome del test.
4. **Dopo la fase 3 — Candidati ulteriori:** CP/W′, time trial/FTP, sprint ripetuti, test submassimali e altri protocolli di laboratorio rimangono candidati, senza impegno di implementazione in questa fase. L'integrazione dei gas in un **test incrementale**, invece, è già inclusa in INC-08.

## Inserimento Android e step 2 — revisione 1.0

La [specifica dei metodi](METODI_INCREMENTALE.md) formalizza lo step 2 senza dichiarare completate le lacune software: regola degli step confermata, aderenza separata e nessun coefficiente universale di soglia/FTHR. Gli scostamenti rilevati e i metodi specialistici ancora da selezionare sono espliciti.

La nuova richiesta inserisce **Android fra l’incrementale desktop e i nuovi test**. Contratti portabili e spike possono procedere durante il consolidamento; il rilascio mobile richiede archivio autonomo offline, report, ruoli e scambio interoperabile. Non esclude nessun INC né cambia l’ordine Sprint breve → Wingate 30 s → Wingate 15 s.

## Cosa copre oggi

Import ERG e protocolli versionati anche senza step, FIT/CSV di campioni, scelta esplicita offset/fine sforzo, medie temporali e copertura dei canali, MAP operativa dall'ultimo step costante completato, interpolazione separata, FC osservata, recupero, antropometria datata, valori manuali, soglia dichiarata o stimata da coefficiente esplicito, FTP dichiarata, N zone, report e storici aggregati. Nei test senza campioni i risultati sono dichiarati. Un coefficiente della MAP non misura automaticamente la FTP o una soglia ventilatoria.

## Lacune per una copertura completa dell'incrementale

Tutte le righe sono **da completare e validare nella fase 1**; soltanto INC-11 ha il sottoinsieme operativo 0.4 implementato. P0/P1/P2 indicano urgenza relativa, non opzionalità. Gli ID INC sono stabili e dettagliano TD-51.

| ID | Priorità | Mancanza attuale | Criterio per considerarla risolta |
|---|---|---|---|
| INC-01 | P0 | Validazione su FIT **reali** esportati da GoldenCheetah, MyWhoosh e Zwift | Corpus anonimizzato e autorizzato con pause, più sessioni, lap, dropout, orologi, sensori e confronto con risultati attesi. Implementare i casi oggi rifiutati quando necessari ai file supportati, con scelta esplicita della sessione. I quattro FIT sintetici non sostituiscono questo collaudo. |
| INC-02 | P0 | Completamento step controlla durata e copertura ≥95%, non l'aderenza al target | Regola condivisa/versionata su tolleranza W/%, tempo valido, overshoot e cadenza; casi di arresto, mancata esecuzione e rullo in ritardo. Il requisito “ultimo step completo” non basta a scegliere queste tolleranze. |
| INC-03 | P0 | Correzione temporale solo con offset e fine sforzo numerici | Selezione visuale, avviso sull'allineamento, anteprima degli step, pause e segmenti esclusi riproducibili; motivi di interruzione. |
| INC-04 | P1 | Rampe visualizzabili, ma MAP per rampa non definita; nessun motore dedicato a protocolli discontinui | Tipo di protocollo esplicito e algoritmo specifico, senza applicare la convenzione degli step costanti. |
| INC-05 | P1 | Acquisizione prelievi di lattato senza curva/algoritmo di soglia | Associazione certa al carico, grafico lattato-potenza, metodi scelti/versionati e revisionabili; intervalli, qualità e limiti. Valore a 4 mmol/L, Dmax e soglie individuali non sono sinonimi. [Studio originale sulle soglie nei ciclisti](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0163389). |
| INC-06 | P1 | Condizioni, dispositivo, calibrazione, ambiente e motivi di arresto soprattutto nelle note | Campi strutturati, taratura, tipo rullo/powermeter, temperatura, cadenza prescritta, stato pre-test e deviazioni dal protocollo; confrontabilità resa visibile. |
| INC-07 | P1 | FC fine step e recupero hanno finestre convenzionali fisse | Preset di analisi versionati, finestre configurabili, confronto manuale/sensore e riepilogo della copertura per metrica nei report. |
| INC-08 | P1 | Assenza di misure di scambio gassoso | Import sincronizzato VO2, VCO2, ventilazione e marker; supporto separato per VO2peak/VO2max e VT1/VT2 nell'incrementale con dati adeguati. Un FIT con soli watt/FC/cadenza non misura VO2max. [Dichiarazione ATS/ACCP sul CPET](https://www.thoracic.org/statements/resources/pfet/cardioexercise.pdf). |
| INC-09 | P1 | Confronti descrittivi, senza errore tipico o minima variazione rilevabile | Ripetibilità intra-atleta per metodo/dispositivo, intervalli con n adeguato, separazione cambiamento reale/rumore; niente percentili o diagnosi pediatriche inventati. |
| INC-10 | P1 | Dati storici senza versione e origine talvolta incompleta | Riconciliazione assistita del protocollo, provenienza campo per campo e filtri di confrontabilità; mantenere sempre l'originale. |
| INC-11 | P2 | Interoperabilità e distribuzione ancora da consolidare | Completare **tutti** i punti operativi della checklist seguente, oltre ai flussi TD-45–50; una sola funzione non chiude la voce. |

Checklist di accettazione INC-11: i primi due punti sono implementati e collaudati localmente nella 0.4, gli altri rimangono da completare:

- [x] Ripristino backup dati e recupero degli accessi distinti, con prove di integrità, annullamento e archivio già presente (TD-45–47).
- [x] Prima sincronizzazione di una società associata ma vuota, ruoli/dispositivi visibili e revoche comprensibili (TD-48–50).
- [ ] Migrazioni testate, compatibilità con archivi e versioni precedenti e gestione del fallimento senza corruzione dei dati.
- [ ] Integrazione con portachiavi delle piattaforme supportate e recupero delle credenziali secondo un disegno esplicito.
- [ ] Rotazione delle chiavi e gestione di dispositivi persi/revocati, senza promettere di eliminare copie già scaricate.
- [ ] Sincronizzazione automatica con audit, conflitti, errori e ripresa dopo indisponibilità della cartella/client cloud.
- [ ] CI e collaudo su Windows/Fedora puliti, distribuzione e firma dei pacchetti secondo le procedure delle piattaforme.
- [ ] Localizzazione completa di interfaccia, diagnostiche, grafici e report nelle lingue supportate.

Per ciascun INC, il completamento comprende input e validazioni, algoritmo o servizio, GUI, report/esportazione ove applicabili, provenienza/versionamento e prove con risultati attesi. La definizione scientifica dei metodi e la disponibilità di dati strumentali restano prerequisiti da risolvere prima di dichiararne il supporto.

Il disegno del protocollo e il metodo di analisi influenzano i risultati: non basta cambiare un'etichetta per rendere equivalenti test diversi. [Studio sperimentale sulle variabili del test incrementale](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0199794).

## Fase 2 — test successivi selezionati

Questi tre test sono scelti per lo sviluppo successivo all'incrementale. Sono **pianificati, non implementati**; prima dei calcoli si documenterà il protocollo reale, soprattutto il Wingate 15 s storico della società.

| ID | Test | Requisiti per sviluppo e collaudo |
|---|---|---|
| TD-52 | Sprint breve / potenza neuromuscolare | Definire durata, partenza, rapporto, resistenza e dispositivo; conservare campioni/frequenza/smoothing; delimitare lo sprint; calcolare picchi e medie su finestre dichiarate, anche relativi al peso quando disponibile. Durata di 6 s soltanto esemplificativa finché non concordata. |
| TD-53 | Wingate 30 s | Protocollo e carico versionati, finestra effettiva di 30 s, potenza di picco/media/minima, lavoro e indice di fatica secondo formula e finestre approvate; qualità dei campioni, cadenza e recupero disponibili. Niente identificazione automatica di un generico sprint come Wingate. |
| TD-54 | Wingate 15 s | Protocollo distinto, usato in passato dalla società secondo la testimonianza dell'utente. Acquisire documentazione/referti e regole esecutive storiche, ricostruire le metriche con provenienza esplicita e gestire risultati manuali privi di tracciato. Definire formule/finestre per 15 s senza derivarle automaticamente da 30 s; niente conversione o aggregazione implicita fra durate. |

Criteri comuni: percorso con tracciato e inserimento manuale, dati mancanti distinti da zero, originali conservati, revisioni, grafici del singolo test, report MD/PDF, CSV e confronti storici omogenei per durata/protocollo/metodo. Registrare massa e data/fonte della misura per W/kg, condizioni e carico; non attribuire precisione temporale o picchi che la frequenza del file non consente. I metodi per gli indici derivati sono da specificare, non già approvati da questo documento.

Le fonti già raccolte per sprint di 6 s e Wingate 30 s sono rispettivamente lo [studio originale sullo sprint breve](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0307325) e il [protocollo sperimentale di Wingate ripetuti](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0242439). **Non sono una validazione del protocollo Wingate 15 s della società**, la cui fonte iniziale è il ricordo operativo dell'utente e il cui metodo deve essere documentato prima dell'implementazione.

## Ricognizione degli altri test e candidati ulteriori

La tabella conserva il contesto della ricognizione precedente. Per sprint breve e Wingate 30 s prevale la fase 3 aggiornata sopra, dopo Android; gli sprint ripetuti e gli altri candidati restano fuori dal perimetro confermato. Le vecchie priorità sono indicative e non superano la sequenza concordata.

| Candidato | Valore per la società | Dati / analisi da aggiungere | Priorità proposta |
|---|---|---|---|
| Sprint breve / potenza neuromuscolare (es. 6 s) | Seguire picco e potenza su finestre brevi | Segmenti di sprint, partenza, rapporto, resistenza, cadenza, picco 1 s/5 s/6 s; frequenza campioni e smoothing espliciti. [Studio originale su sprint di 6 s](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0307325). | Dopo completamento incrementali |
| Wingate 30 s e sprint ripetuti | Profilo di potenza breve e decremento tra ripetizioni | Carico del dispositivo, durata, picco/media/minimo, lavoro e definizione dell'indice di fatica; recuperi tra sprint. Non etichettare genericamente ogni sprint su smart trainer come Wingate. [Protocollo sperimentale di Wingate ripetuti](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0242439). | P2 |
| Profilo potenza-durata / Critical Power e W′ | Confrontare prove massimali di diversa durata | Più prove, durata e condizioni, fitting CP/W′, residui e incertezza. Test 3 min all-out come metodo distinto, non conversione universale della MAP. [Studio originale 3 min all-out](https://pubmed.ncbi.nlm.nih.gov/17473782/), [limiti nei ciclisti élite](https://pubmed.ncbi.nlm.nih.gov/27834562/). | P2 |
| Time trial / test FTP | Monitoraggio pratico sul campo | Durata effettiva, potenza media, pacing e metodo dichiarato. Eventuale coefficiente di conversione esplicito e validato per quel preset, non applicato a tutti i test. | P2 |
| VO2peak/VO2max e soglie ventilatorie | Analisi di laboratorio con dati adeguati | Flussi respiratori, calibrazione, elaborazione respiro per respiro, finestre medie e criteri di verifica; supervisione e interpretazione competenti. Vedi fonte ATS sopra. | P3: richiede integrazione strumentale |
| Submassimale a carico costante / recupero | Confrontare risposta FC e stabilità a carico ripetuto | Segmenti steady-state, durata, deriva, condizioni standard e recupero. Sono descrittori di risposta, non stime universali di VO2max. | P2 |
| Lattato a carico costante / MLSS | Approfondire il comportamento del lattato su prove ripetute | Serie datate di prelievi e carichi, criterio dichiarato, più sedute e confronto con incrementale. [Ricerca originale su durata e metodi di soglia](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0199794). | P3 |

La sequenza di sviluppo è una **decisione dell'utente**; i dettagli tecnici e le priorità interne restano valutazioni progettuali, non risultati delle fonti. Per gli atleti giovani non si trasferiscono automaticamente protocolli o valori normativi di adulti; la scelta esecutiva resta al professionista competente.

## Estensione architetturale

Prima dei nuovi motori introdurre `test_type`, `analysis_method` versionato e un contratto comune di risultati con unità, fonte, validità e incertezza, anticipando nella fase 1 ciò che serve a rampe, lattato e gas. L'attuale campo MAP non deve diventare un contenitore per peak sprint, CP o VO2max. Protocolli, importazioni e libreria di grafici rimangono condivisibili; ogni motore deve dichiarare canali richiesti e metriche realmente calcolabili. Per Wingate registrare esplicitamente la durata (15 s o 30 s) e la versione del protocollo, senza usare il solo nome della famiglia come criterio di confronto. Report e storici devono aggregare soltanto metriche omogenee per tipo, durata, metodo e versione. Nessun motore per questi test aggiuntivi è incluso nella 0.3.
