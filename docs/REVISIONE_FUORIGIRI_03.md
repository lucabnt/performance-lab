# Fuorigiri Performance Lab — requisiti e scelte UI 0.3

Richieste del 17 ottobre 2026. Questo documento esternalizza le osservazioni dell'utente; integra il registro TD precedente senza sostituire i commenti originali. Implementazione nella preview 0.3, non certificazione di rilascio.

**Precisazione successiva:** la collocazione della gestione società è implementata, ma non il percorso completo di recupero/collegamento. Ripristino ZIP assente, recupero delle identità distinto e prima sincronizzazione di società ancora vuota non correttamente esposta: vedere TD-45–50 nel [registro](REQUISITI_E_TODO.md). L'utente ha inoltre confermato come lavoro da implementare tutte le lacune incrementali INC-01–11, poi Sprint breve, Wingate 30 s e Wingate 15 s (TD-51–54). La documentazione di questi punti non ne certifica l'implementazione.

| ID | Richiesta riscritta / criterio verificabile | Esito |
|---|---|---|
| TD-30 | Nome prodotto **Fuorigiri Performance Lab** in interfaccia, titolo finestra e report. Crediti e logo societario fissi. | Implementato |
| TD-31 | Un solo selettore **Società**, senza doppia scelta workspace/archivio attivo. Distinguere archivio locale e cartella di scambio. | Implementato; compatibilità con archivio precedente conservata |
| TD-32 | Creazione/associazione società in **Gestisci società**, accanto al selettore globale; pagina gruppi dedicata alle categorie. | Implementato |
| TD-33 | Nomi leggibili e unità nei grafici, selettori di metriche e riferimenti delle zone; chiavi DB solo nei contratti tecnici. | Implementato con dizionari di presentazione IT/EN |
| TD-34 | Archivio ordinato per uso: import CSV, esportazione e backup, report conservati; condivisione e impostazioni meno frequenti espandibili. | Implementato |
| TD-35 | Storici: prima filtri/aggregazione, poi grafico e tabella con **media e mediana**, conteggi e mancanti; copertura e confronti secondari dopo. | Implementato; protocollo/versione e origine soglia separati |
| TD-36 | PDF semplici, titoli chiari, tabelle leggere, grafici leggibili; logo e attribuzione nel footer di ogni pagina. | Implementato per test e aggregati; cache report precedenti preservata, nuovo renderer 0.3 |
| TD-37 | Il dettaglio test non deve mostrare o far scorrere la lista sottostante durante lo scroll. | Blocco scroll pagina, superfici opache, isolamento del dialogo, rimozione blur del backdrop |
| TD-38 | Gruppo figlio: basta categoria padre + stagione; nome facoltativo ereditato dalla categoria. Nome obbligatorio per categorie principali. | Implementato e validato nel backend |
| TD-39 | Protocollo anche senza step: identità, famiglia, versione e motivo di evoluzione. Niente ERG o calcoli inventati. | Implementato; nuova versione con step abilita analisi automatica |
| TD-40 | Test senza FIT, con soli dati manuali facoltativi e provenienza dichiarata, correggibile con revisioni. | Implementato; atleta, data e protocollo obbligatori |
| TD-41 | Importazione in blocco di antropometria e storico nei formati originali; colonne obbligatorie e facoltative esplicite, anteprima errori prima del salvataggio atomico. | Implementato; un CSV per profilo/lotto con molte righe |
| TD-42 | ERG originali come esempi e almeno quattro esecuzioni FIT plausibili, riproducibili e dichiaratamente sintetiche. | Implementato in `examples/synthetic`, generatore e archivio demo |
| TD-43 | Elenco verificabile delle lacune per copertura completa dei test incrementali. | Documentato in COPERTURA_TEST_E_ROADMAP.md |
| TD-44 | Candidati non prioritari oltre agli incrementali, requisiti dati e separazione dei motori. | Documentato nello stesso documento; motori futuri non implementati |

## Decisioni di interazione

**UI-11 — Società come contesto di lavoro.** Una società separata possiede un database locale e file originali. “Workspace” resta il nome interno di API e registro; non è un secondo oggetto che l'operatore deve selezionare. L'archivio precedente rimane accessibile per compatibilità: nessuna migrazione automatica dei dati. La cartella Google Drive/Dropbox contiene pacchetti di scambio cifrati, mai il database SQLite aperto.

**UI-12 — Operazioni globali nel contesto globale.** Gestisci società è nel menu laterale, vicino alla selezione. La pagina Società e gruppi gestisce categorie, stagioni e appartenenze. Le identità di chi può vedere/modificare si gestiscono nella sezione Condivisione e collaboratori.

**UI-13 — Analisi aggregata prima dei dettagli.** Aggregazione per stagione, categoria, anno di categoria, coorte, atleta o totale; modalità ultimo test per atleta predefinita, tutti i test esplicita. Il selettore statistica cambia il grafico; tabella e report mostrano entrambe le statistiche. Conteggi sempre visibili. Non si aggregano implicitamente versioni diverse o soglie di origine diversa. Gli aggregati non dimostrano effetti causali di allenamento o crescita.

**UI-14 — Acquisizione con o senza campioni.** Nuovo test offre il percorso con tracciato e l'azione Inserisci solo dati manuali. Protocollo senza step è una scheda d'archivio, non un carico pari a zero. MAP dichiarata e MAP calcolata restano distinguibili; il valore manuale non riceve una falsa copertura dei campioni. Le zone assolute possono essere definite anche senza campioni, mentre il tempo in zona non è misurabile.

**UI-15 — Report di suite.** Identità prodotto in testa; nome atleta, data e protocollo immediatamente leggibili. Sintesi numerica e tracciato prima del dettaglio. Footer comune con logo originale, credito fisso e numero pagina. La futura app allenamenti potrà riusare stile, crediti e componenti, mantenendo DB e motore separati secondo SUITE-01.

**UI-16 — Compatibilità tecnica.** Nome visuale nuovo; directory dati `CicloTest`, package Python `cycling_test`, comando `ciclo-test` e header di API precedenti restano stabili per non abbandonare gli archivi esistenti. Aggiunto alias `fuorigiri-performance-lab`. Il bundle conserva per ora il percorso `dist/CicloTest`; questo è un nome tecnico, non il titolo dell'app.

## Contratto CSV

UTF-8 (BOM ammesso), separatore virgola o punto e virgola, date `YYYY-MM-DD`, numeri in unità indicate nei nomi delle colonne. Virgola decimale ammessa se il delimitatore/quoting non è ambiguo. Intestazioni duplicate, righe disallineate e valori non finiti sono rifiutati. I modelli completi sono scaricabili con Esporta CSV e gli esempi sintetici sono in `examples/synthetic`.

| Profilo | Obbligatori | Facoltativi / regole |
|---|---|---|
| atleti | atleta_id, cognome, nome | anno_nascita, conferma/fonte, sesso, stato, note |
| antropometria | atleta_id, data | peso_kg e/o statura_cm: almeno uno. peso_fonte e origine facoltativi. |
| test_aerobico | test_id, atleta_id, data, protocollo_id | Risultati, antropometria, soglia, FC, cadenza, lattato storico, indicatori di qualità e note possono essere vuoti. |

Importare prima le anagrafiche. La riconciliazione usa ID, mai omonimie. Ogni file è un lotto atomico: errori bloccano tutte le righe, duplicati sono saltati e il resoconto lo indica. Non è un import automatico di tutti i file di una cartella. Sono mantenuti i campi storici originali anche quando il motore non li analizza. Nel profilo storico `protocollo_id` identifica la famiglia, **non una versione ricostruita**: se il CSV non documenta il carico si crea una scheda storica separata, senza fingere che coincida con l'ERG attuale. Archivio completo e versioni sono disponibili anche nel manifest/JSON di esportazione.
