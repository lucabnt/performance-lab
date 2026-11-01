# Importazione in blocco da CSV

Aprire **Importa CSV** nella testata di **Atleti**, **Società e gruppi** o **Test e analisi**; per le rilevazioni usare lo stesso comando nel riquadro **Antropometria** del profilo. Ogni finestra propone solo i tracciati pertinenti (nei test, aerobico/anaerobico). Tutti e cinque i tracciati restano disponibili in **Archivio e scambio → Importazioni CSV**, sezione espandibile. Premere **Scarica modello CSV vuoto**. Ogni modello contiene soltanto la riga delle intestazioni; non contiene persone o misure dimostrative. Compilare e salvare in CSV UTF-8, poi scegliere il file dalla stessa sezione. Importare prima le anagrafiche: le associazioni usano gli ID, non i nomi.

| Tipo | Campi sempre obbligatori | Contenuto |
|---|---|---|
| Anagrafiche atleti | atleta_id, cognome, nome | Nascita, conferma, fonte, sesso, stato e note facoltativi |
| Antropometria | atleta_id, data | Almeno peso_kg o statura_cm; peso_fonte e origine conservati |
| Test aerobici | test_id, atleta_id, data, protocollo_id | Risultati dichiarati, dati mancanti vuoti |
| Appartenenze storiche e future | atleta_id, nome, cognome, data_inizio, gruppo | Fine, sottogruppo/stagione, anno categoria e note facoltativi |
| Test anaerobici | test_id, atleta_id, data, protocollo_id | tipo_test e durata_s richiesti per codici diversi dallo storico ANA-15-070 |

Date nel formato `AAAA-MM-GG`. Sono accettati CSV con virgola o punto e virgola; un numero con virgola decimale deve essere correttamente racchiuso fra virgolette quando il separatore è la virgola. Il modello scaricato usa virgole e UTF-8 con BOM. Lasciare vuoti i risultati non rilevati: zero significa zero. Tutte le colonne opzionali sono elencate e presenti nel modello.

## Test anaerobici

Compilare `tipo_test` con `sprint`, `wingate15` o `wingate30`, e `durata_s` rispettivamente fra 3 e 10, 15 o 30 secondi. Dichiarare codice protocollo, dispositivo, partenza, posizione, coppia e finestre quando disponibili; usare codici diversi quando cambiano le condizioni. I risultati importati sono riepiloghi dichiarati e conservano il file originale; non viene ricostruito un tracciato o ricalcolato un test dai soli risultati.

Il codice storico `ANA-15-070` resta associato a 15 s e 0,70 N·m/kg anche nei CSV privi di tipo e durata. Se tali colonne vengono compilate, devono essere coerenti; un altro tipo o carico richiede un codice distinto. Non estendere quelle condizioni agli altri protocolli.

## Anteprima e conferma

Le cinque anteprime mostrano colonne adatte ai dati: per i test, ID, atleta riconciliato, data, protocollo e risultati principali; per antropometria, peso, statura, fonte e origine. La vista mostra fino a 20 record e ne dichiara il numero; il lotto conserva tutte le righe. I protocolli d’archivio da creare sono elencati separatamente e non aumentano il conteggio delle righe pronte mostrato all’operatore.

Correggere tutti gli errori prima di **Conferma importazione atomica**. I duplicati riconosciuti vengono saltati. Il caricamento per anteprima non salva atleti, misure o test; il file viene conservato nello staging locale. CSV e modelli non sostituiscono un backup completo dell’archivio.

Per antropometria sono conservate le fonti misurato, arrotondato, dichiarato, derivato e stimato. Fonte vuota significa dichiarato; fonte sconosciuta genera errore. La classificazione originale degli import già effettuati non viene riscritta automaticamente.

## Appartenenze storiche e future

In Archivio e scambio selezionare **Appartenenze storiche e future**. Sono disponibili **Scarica modello CSV vuoto** e **Scarica CSV di esempio**. Copie nei sorgenti: [modello](../examples/import-appartenenze/appartenenze-modello.csv) e [esempio sintetico](../examples/import-appartenenze/appartenenze-esempio.csv).

| Colonna | Significato |
|---|---|
| atleta_id | Obbligatorio: ID esterno gia usato per importare l'anagrafica; accettato anche l'ID interno esatto |
| nome, cognome | Obbligatori e corrispondenti all'ID; mai riconciliazione per solo nome |
| data_inizio | Obbligatoria, AAAA-MM-GG |
| data_fine | Facoltativa, AAAA-MM-GG; vuota significa appartenenza in corso |
| gruppo | Obbligatorio: nome della categoria, per esempio Allievi |
| sottogruppo | Stagione, per esempio 2024; vuoto per appartenenza diretta a categoria senza stagione incorporata |
| anno_categoria | Facoltativo: 1, 2, ecc.; non e l'anno della stagione |
| note | Facoltative, conservate sull'appartenenza |

Una riga per appartenenza: lo stesso atleta puo figurare in stagioni/categorie diverse, per anni passati o futuri. L'esempio usa persone e ID sintetici: sostituirli con quelli della propria anagrafica. Sono ammesse anagrafiche archiviate per caricare lo storico; quelle eliminate devono essere ripristinate. ID sconosciuti o di un'altra societa, nomi discordanti, date invertite e categorie/stagioni ambigue sono errori.

Le categorie e stagioni mancanti vengono proposte in anteprima, senza scritture prima della conferma; dopo la conferma sono salvate insieme alle appartenenze in un unico lotto atomico. Gli ID delle anagrafiche non vengono cambiati e nessun atleta viene creato, spostato di societa o eliminato. La stagione gia salvata sulla categoria viene riutilizzata quando coincide con sottogruppo; se il padre ha una stagione preesistente, compilare sottogruppo esplicitamente.

I duplicati con stesso atleta, gruppo, periodo e anno_categoria vengono saltati anche al reimport. Sovrapposizioni inclusive nello stesso gruppo con periodi o anni di categoria diversi sono errori da riconciliare: non riscrivere automaticamente i dati esistenti. Gruppi diversi possono avere periodi sovrapposti. Gruppi/stagioni eliminati non vengono ricreati o ripristinati implicitamente. Una data finale vuota puo sovrapporsi a periodi successivi: controllarla con attenzione. Le date non sono dedotte dal nome della stagione e cambiare la stagione non riscrive le date gia registrate.

Annullamento lotto: conserva gli originali e marca eliminati i soli record del lotto; bloccato se sono stati modificati o se altri record dipendono dai gruppi/atleti creati nel lotto. Test e report preesistenti non vengono riscritti dall'import.

## Organizzazione della suite — 1 novembre 2026

Comandi contestuali prima di elenchi/risultati, creazione come azione primaria e import come secondaria; modello/scelta file prima delle istruzioni estese espandibili. Le appartenenze collettive si gestiscono in Società e gruppi e quelle individuali dal profilo. A Ruota adotta lo stesso schema di disposizione per i suoi import anagrafici/appartenenze; Ammiraglia conserva gli import KSport di Persone/Eventi. Tracciati e responsabilità rimangono distinti. Le scorciatoie Fuorigiri riusano `ImportPanel`, API e conferma atomica esistenti; non sono parser nuovi o un filtro di sicurezza diverso. [Esiti](VERIFICA.md).
