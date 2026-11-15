# Importazione in blocco da CSV

## Integrazione incrementale antropometrica — 8 novembre 2026

Reimportare il CSV può completare una rilevazione esistente, senza duplicarla. Esempio: una riga già acquisita con statura 168 cm riceve peso 56 kg e altezza perineale 80 cm; dopo conferma il profilo conserva una sola rilevazione, con rapporto 47,62%. È possibile indicare solo i campi da aggiungere, lasciando vuoti gli altri.

- La ricerca usa atleta e data. È aggiornata solo una rilevazione attiva compatibile e univoca: i valori già presenti devono coincidere con quelli compilati nel CSV. Se i valori compilati sono già acquisiti, la riga viene saltata anche in presenza di più rilevazioni compatibili. Per aggiungere misure mancanti, fonte e origine possono distinguere i candidati (corrispondenza completa, altrimenti fonte poi origine quando discriminanti); solo se la destinazione resta ambigua l’import segnala errore. Nessuna rilevazione nella data ⇒ nuova registrazione.
- Si completano solo peso, statura e altezza perineale mancanti. Un valore diverso da quello già registrato è una discordanza: correggere dal profilo. Non vengono fusi i duplicati storici già esistenti né ripristinati record eliminati.
- Fonte e origine esistenti sono preservate; se nel CSV sono diverse compare un avviso non bloccante con riga, atleta, data, valore conservato e valore CSV. Non occorre modificarle per procedere con l’importazione. Per una nuova rilevazione la fonte vuota resta dichiarato. Campi avanzati, qualità e note non sono sostituiti dai default CSV.
- Le righe complementari nel medesimo lotto confluiscono in un solo record; reimport identici o sottoinsiemi già acquisiti vengono saltati. I campi vuoti non cancellano valori.

L’anteprima mostra **Operazione** (Nuova rilevazione / Integra rilevazione), **Campi da integrare** e risultato complessivo. La conferma atomica conserva ID, nuova revisione, motivo e CSV originale del lotto; anche un solo errore blocca il salvataggio dell’intero lotto. Se i dati cambiano dopo l’anteprima viene richiesta una nuova anteprima. I client precedenti che non trasmettono il piano di conferma possono ancora creare record, ma non effettuare integrazioni senza un’anteprima aggiornata.

## Altezza perineale — standard dell’8 novembre 2026

```csv
atleta_id,data,peso_kg,statura_cm,altezza_perineale_cm,peso_fonte,origine
```

`altezza_perineale_cm` indica il cavallo in cm ed è facoltativa. Sono accettati anche i vecchi file senza la colonna. Ogni riga deve contenere almeno peso, statura o altezza perineale; valori mancanti restano vuoti. La misura perineale deve essere positiva, finita, ≤180 cm e inferiore alla statura se presente. Nel profilo il rapporto è `100 × altezza_perineale_cm / statura_cm`, disponibile solo se entrambi appartengono alla stessa rilevazione. Non vengono abbinate righe distinte, neppure della stessa data.

La rilevazione può essere corretta nell’editor, conservando revisioni e provenienza. Per l’integrazione tramite reimport vale la procedura incrementale seguente. Non confondere questa misura con gli arti inferiori o con statura meno statura seduta.

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

## Testi protetti dalle formule — 14 novembre 2026

Negli export CSV di Fuorigiri i testi che iniziano con `=`, `+`, `-`, `@`, tabulazione o a capo sono preceduti da un apice (`'`), così un foglio di calcolo li mostra come testo invece di eseguirli come formule. I numeri restano invariati, anche quelli negativi. L'import rimuove l'apice: esportare e reimportare restituisce gli stessi testi. Un testo che inizia per apice seguito da uno di quei caratteri va quindi scritto con un apice in più.

## Anteprima e conferma

Le cinque anteprime mostrano colonne adatte ai dati: per i test, ID, atleta riconciliato, data, protocollo e risultati principali; per antropometria, peso, statura, fonte e origine. La vista mostra fino a 20 record e ne dichiara il numero; il lotto conserva tutte le righe. I protocolli d’archivio da creare sono elencati separatamente e non aumentano il conteggio delle righe pronte mostrato all’operatore.

Correggere tutti gli errori prima di **Conferma importazione atomica**. I duplicati riconosciuti vengono saltati. Il caricamento per anteprima non salva atleti, misure o test; il file viene conservato nello staging locale. CSV e modelli non sostituiscono un backup completo dell’archivio.

Per antropometria sono conservate le fonti misurato, arrotondato, dichiarato, derivato e stimato. Fonte vuota significa dichiarato; fonte sconosciuta genera errore. La classificazione originale degli import già effettuati non viene riscritta automaticamente.

## Appartenenze storiche e future

Per assegnare atleti già presenti senza CSV: **Società e gruppi → Aggiungi atleti** nella stagione, oppure **Mostra gli atleti → Aggiungi atleti al gruppo** nell’elenco filtrato. Il comando resta disponibile anche per rose già popolate. Nel filtro di categoria occorre scegliere esplicitamente il gruppo/stagione; nel filtro di stagione la destinazione è già impostata. Selezionare gli atleti, verificare Dal/Al e premere **Conferma assegnazione**. Il dialogo comprende tutti gli atleti attivi della società e disabilita quelli già assegnati nel periodo; richiede Admin dati. La ricerca e il filtro dell’elenco restano conservati dopo il salvataggio.

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
