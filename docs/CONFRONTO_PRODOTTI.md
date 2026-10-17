# Confronto di prodotti e funzionalità candidate

Ricognizione del 17 ottobre 2026 per TD-27, basata sulle pagine ufficiali consultate. Selezione di riferimenti pertinenti, non classifica dei prodotti più diffusi né verifica pratica di tutte le funzioni. Le descrizioni commerciali non validano i metodi fisiologici. Le idee seguenti non cambiano automaticamente il perimetro di sviluppo.

| Prodotto e modello | Funzioni descritte dalla fonte | Indicazioni per la suite |
|---|---|---|
| [GoldenCheetah](https://www.goldencheetah.org/), open source | Analisi delle attività, modelli di potenza critica, intervalli, editor dei dati, grafici e integrazione Python/R. | Priorità Test: evidenza degli errori, selezione degli intervalli e correzioni tracciabili. Futuro: analisi avanzate configurabili; evitare inizialmente script arbitrari eseguibili. |
| [Intervals.icu](https://www.intervals.icu/), servizio ospitato con accesso gratuito e supporter | Storici di carico, stime eFTP, grafici personalizzati, calendario e creazione di allenamenti; gestione di più atleti. La pagina consultata non basta a stabilire una licenza open source dell'intero prodotto. | Test: filtri e confronti longitudinali. Allenamenti: calendario, libreria sedute e confronto tra programma ed esecuzione. Non confondere eFTP con una misura diretta. |
| [TrainingPeaks WKO5](https://www.trainingpeaks.com/wko5/), software commerciale | Analisi desktop, modello potenza/durata, zone individualizzate e grafici per approfondire le prestazioni. | Test: separare valori osservati e modelli, rendere espliciti parametri e provenienza. Modelli potenza/durata sono candidati successivi, non necessari al protocollo incrementale iniziale. |
| [TrainingPeaks per allenatori](https://www.trainingpeaks.com/become-a-coach/), piattaforma commerciale | Pianificazione, gestione atleti, dashboard, monitoraggio dell'esecuzione e feedback. | Allenamenti: assegnazione a gruppi, calendario, note e feedback. Accesso online continuativo e messaggistica richiederebbero un disegno ulteriore rispetto al solo scambio di cartelle. |

## Priorità proposte

- **Già richieste e da sviluppare/consolidare:** revisione dopo il grafico, gruppi/stagioni, confronti, zone configurabili, report longitudinali e import CSV. Vedi TD-04–29 nel [registro requisiti](REQUISITI_E_TODO.md).
- **Candidate per l'app Allenamenti:** calendario per atleta/gruppo, modelli di seduta, editor strutturato, assegnazione e confronto programmato/eseguito; applicare le zone di una revisione esplicita del test.
- **Da valutare in seguito:** modelli potenza/durata, dashboard personalizzabili, carico/fatica, feedback collaborativo e integrazioni dirette con piattaforme. Richiedono definizioni, licenze delle eventuali dipendenze, dati e prove specifiche.

La combinazione distintiva proposta è il percorso riproducibile ERG → test → revisione → report, con storico giovanile e funzionamento offline. È una scelta progettuale del nostro prodotto, non un'affermazione che gli altri programmi siano privi di queste capacità.
