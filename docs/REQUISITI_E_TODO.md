# Requisiti e to-do

## Aggiornamento successivo: storico, logo e zone

17 ottobre 2026, architettura **0.5**. Convenzioni funzionali accettate; dettaglio e criteri in [Storico, zone e branding](STORICO_ZONE_E_BRANDING.md). Le righe della tabella sottostante descrivono lo stato del codice, invariato; per le decisioni questi aggiornamenti prevalgono:

- **TD-02/03:** logo di riferimento fornito; colori del file identificati. Resta da implementare il tema e verificarne la leggibilità.
- **TD-04/13/16/17:** definite nove viste HIST-01–09 dal PDF, includendo anno di categoria distinto da stagione e coorte; default per atleta accettato e modalità tutti i test per continuità con l'archivio.
- **TD-18:** riferimento storico acquisito; consente progressione prestativa e peso, ma non crescita in statura (misure assenti) o modelli di maturazione.
- **TD-19/20 e SUITE-01:** accettati isolamento per società, admin/visualizzatore e separazione DB delle app con librerie comuni.
- **TD-28:** percentuali e confini del preset FTHR/Watt Soglia confermati. Nuovo requisito **ZONE-01**: numero N di zone configurabile, anche oltre cinque, distinto per FC e potenza; editor, grafici, report ed export dinamici. Da sviluppare, con verifiche sui confini e schemi a 3/5/7 zone.
- **Estensione candidata ANA-01:** import/consultazione dei risultati anaerobici dello storico; non ancora assunta come implementazione del motore anaerobico.

Ancora aperti: formule dei riferimenti di soglia/FTP, criteri di completamento step, finestre FC, fonti dei valori medi, nome suite e resa finale del tema. Il PDF non viene importato automaticamente e non è copiato nei dati pubblici.

Revisione del 17 ottobre 2026. I 29 identificatori seguono l'ordine dei [commenti originali](COMMENTI_ORIGINALI_2026-10-17.md). Questo documento distingue **integrazione nel progetto** da **implementazione nel programma**. Il presente intervento aggiorna la documentazione, non realizza le funzioni mancanti.

Stati: **presente** = funzionalità riscontrata nel codice; **parziale** = solo una parte disponibile; **da sviluppare** = requisito acquisito, non implementato; **da definire** = scelta o riferimento necessario. Il riscontro è sul codice della preview locale, non una certificazione su Windows/Fedora puliti. Riferimento principale: [architettura 0.4](../ARCHITETTURA_PROPOSTA.md).

| ID | Requisito riscritto e criterio di completamento | Stato e riscontro attuale | Disegno |
|---|---|---|---|
| TD-01 | Segnalare esplicitamente ciò che è già implementato, separando le parti di una richiesta composta. | **Completato per questa revisione documentale** con la presente tabella. | §14 |
| TD-02 | Adottare i colori di Progetto Ciclismo con superfici neutre e accenti poco invasivi; mantenere leggibilità e contrasto. | **Da sviluppare**: il tema attuale è verde; palette finale da validare sul logo. | §5.1, UI-02 |
| TD-03 | Inserire discretamente in basso logo e collegamento della società, nome Luca Bontempi e collegamento personale. | **Da sviluppare**: asset definitivo e dimensioni da verificare in UI. Link e collocazione definiti. | §5.1, UI-03 |
| TD-04 | Calcolare aggregati storici per gruppo, anno e gruppo/anno, indicando popolazione, filtri e dati mancanti. | **Da sviluppare**: esistono gruppi e test, non il servizio di aggregazione. | §6.1, §8.2 |
| TD-05 | Nella scheda atleta selezionare MAP o FTP, W o W/kg; aggiungere grafici di peso e statura. | **Parziale**: grafico MAP in W e tabella antropometrica; mancano selettori, FTP e grafici antropometrici. FTP va distinta da altre soglie stimate. | §5.1, §8.1 |
| TD-06 | Rendere disponibili italiano e inglese in interfaccia, grafici e report. | **Da sviluppare**: stringhe UI italiane non ancora internazionalizzate; alcuni controlli Plotly in inglese. | §5.1, UI-05 |
| TD-07 | Importare anagrafiche, test storici e antropometria da CSV con anteprima, riconciliazione ed errori per riga. | **Da sviluppare**: presenti i tre export CSV, non l'import. Distinguerlo dal CSV con campioni di un test. | §7 |
| TD-08 | Nell'import ERG riconoscere step/rampe, indicare il riscaldamento e salvare codice protocollo distinto dal nome. | **Presente nel flusso ERG**: parser automatico, codice famiglia e nome, durata iniziale di riscaldamento. Il tag riguarda il prefisso iniziale con confine su step; editor di fasi arbitrarie incluso in TD-11. | §7 |
| TD-09 | Archiviare atleti inattivi mantenendoli negli storici; eliminarli escludendoli dai nuovi calcoli storici. | **Da sviluppare**: mancano stati di ciclo di vita e relativi filtri. | §6.1 |
| TD-10 | Archiviare o eliminare protocolli senza perdere i riferimenti dei test esistenti. | **Da sviluppare**: le versioni esistono, non il ciclo di vita. | §6.1 |
| TD-11 | Creare e modificare protocolli dall'interfaccia, esportare ERG e pubblicare nuove versioni con differenze e motivazione. | **Parziale**: nuove versioni da import ERG con genitore e motivo; assenti editor manuale ed export ERG. | §7 |
| TD-12 | Ordinare le tabelle per ogni colonna di dati, con indicatore del verso e comportamento coerente per valori mancanti. | **Da sviluppare**: ordinamenti predefiniti non equivalgono all'ordinamento interattivo. Colonne di sole azioni escluse. | §5.1, UI-06 |
| TD-13 | Mostrare un gruppo stabile, per esempio Allievi, con sottogruppi per anno/stagione. | **Parziale**: gruppo con campo stagione, ma struttura piatta senza categoria padre. | §6.1 |
| TD-14 | Modificare il profilo atleta dalla UI e inserire manualmente rilevazioni antropometriche datate. | **Parziale**: modifica atleta disponibile nell'API ma non nella UI. **Inserimento manuale antropometrico già presente**, con data, peso, statura e fonte. | §5, §6 |
| TD-15 | Nell'import FIT o CSV raccogliere lattato, coefficienti, FC, antropometria e altri dati mancanti; proporre le ultime rilevazioni e consentire correzioni successive. | **Parziale**: FIT, peso/statura, FC pre-test e tempi sono inseribili; mancano CSV temporali, lattato, coefficienti, proposta storica e revisioni successive. TD-21/22/23/29 dettagliano il flusso. | §7, §8.1 |
| TD-16 | Esportare MD/PDF dello storico atleta, categoria e categoria/anno, con grafici, filtri e criteri statistici. | **Da sviluppare**: disponibili report del singolo test. | §9.1 |
| TD-17 | Confrontare gruppi su una stagione o sullo storico con criteri espliciti di confrontabilità. | **Da sviluppare**: nessuna vista di confronto aggregato. | §8.2 |
| TD-18 | Calcolare statistiche di crescita antropometrica e progressione prestativa, distinguendole. | **Da sviluppare; metodo avanzato da definire**: PDF esaminato: statistiche descrittive fattibili; mancano statura e specifiche dei modelli di maturazione. | §8.2 |
| TD-19 | Configurare percorsi locali e cartelle di scambio distinti per società, condivisibili con collaboratori diversi. | **Parziale**: sync sperimentale dell'intero archivio; isolamento per società non ancora implementato. | §10.1 |
| TD-20 | Gestire operatori admin e visualizzatori per società, applicando i permessi anche alle API e ai dati ricevuti. | **Da sviluppare**: il token locale identifica una sessione tecnica, non un ruolo utente. | §10.3 |
| TD-21 | Registrare FC a 60, 90 e 120 secondi e a tempi personalizzati, specificando l'evento da cui decorrono. | **Parziale**: recupero automatico a 60/90/120 s e singola FC pre-test con durata; manca la serie manuale personalizzata. Riposo e recupero restano distinti. | §8.1 |
| TD-22 | Inserire RPE da 1 a 10, associata al test e alla scala dichiarata. | **Da sviluppare**: nessun campo RPE corrente. | §8.1 |
| TD-23 | In assenza di storico proporre valori medi configurati per i dati manuali, con fonte e conferma esplicita. | **Da definire e sviluppare**: nessun valore medio universale assunto. Proposte e stime non devono diventare misure reali implicite. | §8.1 |
| TD-24 | Richiedere data di nascita facoltativa; continuare ad accettare anno soltanto o dato assente. | **Parziale**: anno facoltativo già presente; manca data completa con precisione esplicita. | §6.1 |
| TD-25 | Scegliere un nome legato alla cultura ciclistica italiana, mantenendo Performance Lab e prevedendo nomi coordinati per la suite. | **Da scegliere**: proposte in §15; nessuna rinomina del programma eseguita. | §15 |
| TD-26 | Usare il testo «Strumenti aperti a supporto del ciclismo giovanile» nella parte bassa dell'app. | **Da sviluppare**: testo acquisito nel disegno UI, non ancora sostituito nel codice. | §5.1, UI-03 |
| TD-27 | Confrontare prodotti open source e commerciali e ricavarne funzionalità candidate. | **Prima ricognizione documentale completata** in [Confronto prodotti](CONFRONTO_PRODOTTI.md); non è una prova pratica né una graduatoria di mercato. Funzioni candidate non automaticamente approvate. | §12 |
| TD-28 | Configurare zone FC e potenza in percentuale di riferimenti selezionati e riportarle nei report. | **Da sviluppare; preset confermato**: vedi aggiornamento 0.5 e ZONE-01. Formule dei riferimenti ancora da definire. | §8.1, §9 |
| TD-29 | Correggere input manuali e fine sforzo dopo aver visto il grafico, ricalcolando in una nuova revisione. | **Da sviluppare**: anteprima prima del salvataggio presente, ma test salvato non revisionabile dalla UI. | §8.1 |
| SUITE-01 | Registrare decisioni UI e condividere componenti con una futura app di gestione allenamenti della stessa suite. | **Disegno documentato**, estrazione dei pacchetti e seconda app da sviluppare. | §5.1, §15 |

## Ordine proposto di sviluppo

1. Modello dati e migrazioni: nascita, categorie/stagioni, stati di archivio, revisioni test, osservazioni e provenienza.
2. Flussi locali: modifica atleta/test, import CSV, editor protocolli, campi manuali e configurazione dei metodi.
3. Componenti UI condivisi, branding, traduzioni e tabelle ordinabili; preparazione parallela alle schermate locali, senza duplicarne la logica.
4. Storici, aggregati, crescita descrittiva, zone e report multipli dopo validazione delle definizioni.
5. Workspace isolati, identità e autorizzazioni, sincronizzazione con conflitti e revoca; prove fra PC e account diversi.
6. Distribuzione verificata Windows/Fedora; seconda app pianificata separatamente sul nucleo condiviso.

## Riferimenti ancora necessari

- Formule per soglie e crescita avanzata: il PDF è ora esaminato, ma non le definisce. Le percentuali delle zone sono invece confermate nella specifica 0.5.
- Gerarchia accettata: stagione, anno di categoria e anno di nascita distinti; restano da configurare le regole della società.
- Preset dei valori medi, destinatari e fonte; nessun riempimento automatico dei dati reali.
- Scelta del nome della suite e palette definitiva. Il logo è ora fornito dall'utente; i colori rilevati nel file non sostituiscono una specifica di stampa.

## Come mantenere il registro

Conservare gli ID; per richieste composte aggiornare lo stato di ogni parte. Segnare «completato» solo dopo implementazione e verifica del criterio, citando file/test o versione. Registrare ogni variazione significativa nel [changelog](../CHANGELOG.md), con motivazione, ID coinvolti e distinzione fra progetto e software.
