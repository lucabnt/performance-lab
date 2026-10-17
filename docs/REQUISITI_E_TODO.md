# Requisiti e to-do

## Stato corrente 0.3 — Fuorigiri Performance Lab

Nuovi requisiti **TD-30–44** implementati/documentati nel [registro della revisione 0.3](REVISIONE_FUORIGIRI_03.md), con scelte **UI-11–16**, contratto CSV e criteri di accettazione. [Copertura e mancanze del motore](COPERTURA_TEST_E_ROADMAP.md) distingue le priorità incrementali dai test futuri. Le sezioni 0.2 sottostanti restano storico del progetto; il nome prodotto è ora confermato.


## Stato del codice 0.2 — 17 ottobre 2026

Aggiornamento successivo all'implementazione e alla ripresa del lavoro. La tabella descrive ora il codice 0.2; le note di disegno 0.5 sottostanti restano contesto storico. [Guida di prova con GUI](TESTARE_IL_PROGETTO.md) e [verifiche](VERIFICA.md) distinguono test eseguiti e collaudi ancora necessari.

**Branding fisso:** logo incluso nel bundle e testo «Sviluppato da Luca Bontempi per Progetto CIclismo - Rodengo Saiano A.S.D.». Nessuna personalizzazione di logo/credito per società o workspace. ZONE-01 implementato a lista dinamica, con prove a 3/5/7 zone. ANA-01 resta un'estensione candidata, non sviluppata.

## Decisioni della revisione documentale 0.5 (storico)

17 ottobre 2026, architettura **0.5**. Convenzioni funzionali accettate; dettaglio e criteri in [Storico, zone e branding](STORICO_ZONE_E_BRANDING.md). Queste note descrivevano il disegno prima dello sviluppo; lo stato corrente è nella tabella aggiornata:

- **TD-02/03:** logo di riferimento fornito; colori del file identificati. Resta da implementare il tema e verificarne la leggibilità.
- **TD-04/13/16/17:** definite nove viste HIST-01–09 dal PDF, includendo anno di categoria distinto da stagione e coorte; default per atleta accettato e modalità tutti i test per continuità con l'archivio.
- **TD-18:** riferimento storico acquisito; consente progressione prestativa e peso, ma non crescita in statura (misure assenti) o modelli di maturazione.
- **TD-19/20 e SUITE-01:** accettati isolamento per società, admin/visualizzatore e separazione DB delle app con librerie comuni.
- **TD-28:** percentuali e confini del preset FTHR/Watt Soglia confermati. Nuovo requisito **ZONE-01**: numero N di zone configurabile, anche oltre cinque, distinto per FC e potenza; editor, grafici, report ed export dinamici. Da sviluppare, con verifiche sui confini e schemi a 3/5/7 zone.
- **Estensione candidata ANA-01:** import/consultazione dei risultati anaerobici dello storico; non ancora assunta come implementazione del motore anaerobico.

Ancora aperti: formule dei riferimenti di soglia/FTP, criteri di completamento step, finestre FC, fonti dei valori medi, nome suite e resa finale del tema. Il PDF non viene importato automaticamente e non è copiato nei dati pubblici.

Revisione del 17 ottobre 2026. I 29 identificatori seguono l'ordine dei [commenti originali](COMMENTI_ORIGINALI_2026-10-17.md). Questo documento distingue **integrazione nel progetto** da **implementazione nel programma**. La revisione 0.2 include modifiche al codice; i commenti originali rimangono conservati per tracciabilità.

Stati: **presente** = funzionalità riscontrata nel codice; **parziale** = solo una parte disponibile; **da sviluppare** = requisito acquisito, non implementato; **da definire** = scelta o riferimento necessario. Il riscontro è sul codice della preview locale, non una certificazione su Windows/Fedora puliti. Riferimento principale: [architettura 0.6](../ARCHITETTURA_PROPOSTA.md).

| ID | Requisito riscritto e criterio di completamento | Stato e riscontro attuale | Disegno |
|---|---|---|---|
| TD-01 | Segnalare esplicitamente ciò che è già implementato, separando le parti di una richiesta composta. | **Presente**: stato puntuale aggiornato qui; dettagli di prova in VERIFICA.md. | §14 |
| TD-02 | Adottare i colori di Progetto Ciclismo con superfici neutre e accenti poco invasivi; mantenere leggibilità e contrasto. | **Presente**: tema neutro/blu con accento giallo; verificato visivamente. Accessibilità sistematica da consolidare. | §5.1, UI-02 |
| TD-03 | Inserire discretamente in basso logo e collegamento della società, nome Luca Bontempi e collegamento personale. | **Presente**: logo locale, link e attribuzione fissa in GUI/PDF/Markdown; non personalizzabili. | §5.1, UI-03 |
| TD-04 | Calcolare aggregati storici per gruppo, anno e gruppo/anno, indicando popolazione, filtri e dati mancanti. | **Presente**: history.py, filtri e aggregati per stagione/categoria/coorte/anno di categoria, conteggi e mancanti per metrica. | §6.1, §8.2 |
| TD-05 | Nella scheda atleta selezionare MAP o FTP, W o W/kg; aggiungere grafici di peso e statura. | **Presente**: selettori MAP/soglia/FTP, W/Wkg e grafici peso/statura. FTP assente non stimata implicitamente. | §5.1, §8.1 |
| TD-06 | Rendere disponibili italiano e inglese in interfaccia, grafici e report. | **Parziale**: selettore IT/EN, catalogo UI e titoli principali report; diagnostiche, alcuni controlli Plotly e testi secondari ancora da completare. | §5.1, UI-05 |
| TD-07 | Importare anagrafiche, test storici e antropometria da CSV con anteprima, riconciliazione ed errori per riga. | **Presente per i tre profili concordati**: anteprima, ID esterni, errori per riga e commit atomico. Mappatura interattiva arbitraria di colonne ancora assente. | §7 |
| TD-08 | Nell'import ERG riconoscere step/rampe, indicare il riscaldamento e salvare codice protocollo distinto dal nome. | **Presente**: import ERG e editor manuale con fasi, codice e nome distinti. | §7 |
| TD-09 | Archiviare atleti inattivi mantenendoli negli storici; eliminarli escludendoli dai nuovi calcoli storici. | **Presente**: active/archived/deleted, filtri e ripristino; eliminato escluso dai nuovi aggregati. | §6.1 |
| TD-10 | Archiviare o eliminare protocolli senza perdere i riferimenti dei test esistenti. | **Presente**: stati reversibili; le definizioni usate dai test restano conservate. | §6.1 |
| TD-11 | Creare e modificare protocolli dall'interfaccia, esportare ERG e pubblicare nuove versioni con differenze e motivazione. | **Presente**: editor tabellare, nuove versioni con genitore/motivo, export ERG e definizione JSON. Confronto grafico delle differenze ancora da sviluppare. | §7 |
| TD-12 | Ordinare le tabelle per ogni colonna di dati, con indicatore del verso e comportamento coerente per valori mancanti. | **Presente**: SortableTable e DataTable con ordinamento interattivo tipizzato e indicatori; colonne di azioni escluse. | §5.1, UI-06 |
| TD-13 | Mostrare un gruppo stabile, per esempio Allievi, con sottogruppi per anno/stagione. | **Presente**: categoria padre, stagioni figlie e visualizzazione gerarchica; anno di categoria nelle appartenenze. | §6.1 |
| TD-14 | Modificare il profilo atleta dalla UI e inserire manualmente rilevazioni antropometriche datate. | **Presente**: modifica profilo dalla UI e inserimento antropometrico datato. | §5, §6 |
| TD-15 | Nell'import FIT o CSV raccogliere lattato, coefficienti, FC, antropometria e altri dati mancanti; proporre le ultime rilevazioni e consentire correzioni successive. | **Presente**: FIT/CSV, osservazioni manuali, proposta storica/stimata e revisione. Nessuna formula lattato→soglia non concordata. | §7, §8.1 |
| TD-16 | Esportare MD/PDF dello storico atleta, categoria e categoria/anno, con grafici, filtri e criteri statistici. | **Presente**: MD/PDF degli aggregati e dell’atleta filtrato; manifest con revisioni sorgente e artefatti conservati. | §9.1 |
| TD-17 | Confrontare gruppi su una stagione o sullo storico con criteri espliciti di confrontabilità. | **Presente**: viste per gruppi/stagioni, popolazioni esplicite e confronto appaiato per stesso protocollo/fonte. | §8.2 |
| TD-18 | Calcolare statistiche di crescita antropometrica e progressione prestativa, distinguendole. | **Presente per statistiche descrittive**: delta peso/statura, giorni e annualizzazione; delta prestativi. Maturazione/PHV e benchmark richiedono specifiche ulteriori. | §8.2 |
| TD-19 | Configurare percorsi locali e cartelle di scambio distinti per società, condivisibili con collaboratori diversi. | **Presente nei nuovi workspace**: percorsi, DB, originali e canali separati. Archivio precedente mantenuto, migrazione automatica non implementata. | §10.1 |
| TD-20 | Gestire operatori admin e visualizzatori per società, applicando i permessi anche alle API e ai dati ricevuti. | **Presente in forma operatore/dispositivo**: inviti cifrati, admin/visualizzatore, firme e controlli API/sync. Fondatore gestisce inviti/revoche; portachiavi e recupero guidato ancora assenti. | §10.3 |
| TD-21 | Registrare FC a 60, 90 e 120 secondi e a tempi personalizzati, specificando l'evento da cui decorrono. | **Presente**: automatico 60/90/120 s e osservazioni manuali personalizzate, con fonte distinta dal sensore; riposo pre-test separato. | §8.1 |
| TD-22 | Inserire RPE da 1 a 10, associata al test e alla scala dichiarata. | **Presente**: RPE intera 1–10, scala conservata negli input. | §8.1 |
| TD-23 | In assenza di storico proporre valori medi configurati per i dati manuali, con fonte e conferma esplicita. | **Presente come configurazione facoltativa**: preset con fonte/popolazione, proposto su scelta esplicita e marcato stimato. Nessun valore numerico universale precompilato. | §8.1 |
| TD-24 | Richiedere data di nascita facoltativa; continuare ad accettare anno soltanto o dato assente. | **Presente**: data facoltativa, solo anno o assenza; verifica coerenza data/anno. | §6.1 |
| TD-25 | Scegliere un nome legato alla cultura ciclistica italiana, mantenendo Performance Lab e prevedendo nomi coordinati per la suite. | **Da scegliere**: proposte documentate; nome della preview ancora Ciclo Test. | §15 |
| TD-26 | Usare il testo «Strumenti aperti a supporto del ciclismo giovanile» nella parte bassa dell'app. | **Presente**: motto nel footer accanto all’attribuzione fissa richiesta. | §5.1, UI-03 |
| TD-27 | Confrontare prodotti open source e commerciali e ricavarne funzionalità candidate. | **Completato come prima ricognizione**: CONFRONTO_PRODOTTI.md; nessuna estensione automatica del perimetro. | §12 |
| TD-28 | Configurare zone FC e potenza in percentuale di riferimenti selezionati e riportarle nei report. | **Presente**: preset confermato, schemi N zone per canale, riferimenti espliciti, tempi in zona e report/export dinamici; metodi dei riferimenti restano espliciti. | §8.1, §9 |
| TD-29 | Correggere input manuali e fine sforzo dopo aver visto il grafico, ricalcolando in una nuova revisione. | **Presente**: revisione da UI, ricalcolo dopo fine sforzo, motivo e protezione da aggiornamenti persi; correzione dei risultati storici tramite flusso dedicato. | §8.1 |
| SUITE-01 | Registrare decisioni UI e condividere componenti con una futura app di gestione allenamenti della stessa suite. | **Parziale**: moduli UI condivisibili, branding fisso e servizi separati; estrazione in pacchetti indipendenti e seconda app future. | §5.1, §15 |

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
