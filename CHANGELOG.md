# Changelog

Le versioni dell'architettura sono distinte da quelle del programma. Ogni voce deve indicare data, natura della modifica, motivo e identificatori di requisiti/decisioni. Una modifica documentale non certifica l'implementazione della funzione.

## Architettura 0.5 — 2026-10-17

**Tipo: conferme, valutazione allegati e specifica; nessuna modifica funzionale al software.**

- Registrata accettazione delle convenzioni per categorie/stagioni, ciclo di vita, revisioni, aggregazioni per atleta, ruoli e confini della suite.
- Esaminato archivio_test.pdf e aggiunta [specifica storico, zone e branding](docs/STORICO_ZONE_E_BRANDING.md): nove viste HIST-01–09, fattibilità e prerequisiti, modalità tutti i test distinta dal default per atleta, anno di categoria distinto da stagione/coorte, copertura per metrica e confrontabilità.
- Documentati limiti: soglie storiche stimate da distinguere da misure; nessuna statura disponibile per crescita in altezza; risultati anaerobici importabili come estensione candidata ANA-01, senza assumere approvato un nuovo motore di calcolo. Non copiati dati personali nei documenti di progetto.
- Acquisito il logo fornito dall'utente come riferimento UI-02/03, con colori rilevati nel file e regole d'uso; nessuna modifica all'asset o alla UI.
- Registrate le tabelle originali delle zone e la normalizzazione dei confini confermata dall'utente, incluso il 55% di potenza in Z1 (TD-28/D26). Esempi numerici sintetici e controlli attesi.
- Aggiunto ZONE-01: numero di zone configurabile oltre cinque, indipendente per FC/potenza; schema a lista, editor, rendering ed export esteso dinamici. Cinque zone restano il preset iniziale, non il limite del programma.
- Aggiornati architettura, decisioni e backlog. Verificati collegamenti locali e calcoli degli esempi ai confini; nessun test applicativo necessario per questa modifica documentale.

## Architettura 0.4 — 2026-10-17

**Tipo: documentazione e disegno; nessuna modifica funzionale al software.** Revisione richiesta dopo i commenti dell'utente nella sezione To-Do.

- Trasferiti tutti i 29 commenti in [Requisiti e to-do](docs/REQUISITI_E_TODO.md), riscritti con ID TD-01–29, stato e criteri verificabili; conservata la [trascrizione originale](docs/COMMENTI_ORIGINALI_2026-10-17.md). Aggiunto SUITE-01 per l'app gemella.
- Registrate le parti già presenti: flusso ERG con codice/step/riscaldamento iniziale e inserimento manuale antropometrico; distinte dalle richieste composte ancora incomplete (TD-01/08/14).
- Esteso il modello con categorie/stagioni, nascita completa facoltativa, ciclo di vita di atleti/protocolli e revisioni manuali dei test (TD-09/10/13/24/29; D20–22).
- Promosso l'import CSV da estensione futura a requisito, distinguendo risultati storici e serie temporali; dettagliato editor/export ERG (TD-07/11/15; D19).
- Integrati lattato, coefficienti, FC pre-test/recupero, RPE e proposte da storico/preset, con provenienza e separazione fra stime e misure; introdotto il contratto delle zone (TD-15/21/22/23/28; D26). Preset numerici e metodi avanzati restano da validare.
- Definiti aggregati, confronti, crescita descrittiva e report di atleta/categoria/stagione con popolazione e revisioni congelate (TD-04/05/16/17/18; D23).
- Aggiornata la collaborazione: archivi e cartelle per società, ruoli admin/visualizzatore e verifica delle scritture ricevute. Esplicitati limiti della revoca offline e differenza fra cifratura e autorizzazione (TD-19/20; D07).
- Aggiunto nell'architettura il registro UI-01–10: branding blu/giallo proposto, logo e crediti, nuovo motto, IT/EN, grafici, tabelle ordinabili, accessibilità e componenti comuni (TD-02/03/05/06/12/25/26; D24).
- Disegnati confini della suite, librerie e contratti condivisi con DB separati; proposti nomi coordinati senza rinominare la preview (SUITE-01; D25).
- Aggiunta [ricognizione dei prodotti](docs/CONFRONTO_PRODOTTI.md) con fonti ufficiali e candidati separati dai requisiti approvati (TD-27).
- Aggiornati piano e verifiche attese. Verificata la copertura dei 29 commenti, i collegamenti locali dei documenti e la coerenza del registro. Non rieseguiti test applicativi: intervento solo documentale.

## Stato precedente

Il documento di partenza era Architettura 0.3 del 16 ottobre 2026, con preview locale 0.1. Questo changelog viene istituito il 17 ottobre: non ricostruisce retroattivamente un elenco completo di modifiche o rilasci precedenti. Lo stato tecnico precedente resta descritto in [README](README.md), [decisioni](docs/DECISIONI.md) e [verifiche](docs/VERIFICA.md).
