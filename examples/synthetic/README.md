# Esempi interamente sintetici

Quattro esecuzioni FIT simulate, senza persone reali. Gli ERG originali di riferimento sono in `../protocols/`. I file non dichiarano di essere esportati da GoldenCheetah, MyWhoosh o Zwift e non ne certificano la compatibilità.

| File | Protocollo | Fine sforzo (s) | Ultimo step completo (W) |
|---|---|---:|---:|
| SIM-ALL-01.fit | AER-RULLO-ALL | 2145 | 280 |
| SIM-ALL-02.fit | AER-RULLO-ALL | 2435 | 310 |
| SIM-ESO-01.fit | AER-RULLO-ESO | 2120 | 180 |
| SIM-ESO-02.fit | AER-RULLO-ESO | 2405 | 200 |

Ogni FIT contiene riscaldamento, step, step finale parziale e 180 s di recupero. La fine del file **non coincide** con la fine dello sforzo. Potenza con ritardo/rumore, FC con risposta esponenziale e deriva, cadenza variabile; modello illustrativo, non fisiologicamente validato. Campioni ogni secondo, messaggi FIT file_id/record/session, timestamp e CRC. Il manifest indica valori manuali e durata da usare nell'importazione.

Rigenerazione deterministica dalla radice: `python scripts/generate_examples.py` nell'ambiente installato del progetto.

I tre CSV di esempio mostrano il formato standard e i campi omessi. `test_aerobico.csv` rappresenta una **modalità alternativa** di archiviazione dei medesimi risultati senza campioni: non importarlo dopo aver già archiviato i quattro FIT se non vuoi creare una seconda rappresentazione degli stessi test. Per provare il CSV usare un archivio demo separato. Nessun dato allegato originale degli atleti viene incluso.
