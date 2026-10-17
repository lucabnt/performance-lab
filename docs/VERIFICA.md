# Verifiche locali — software 0.2

17 ottobre 2026. Ambiente Windows, Python 3.14 e Node.js 24. I risultati descrivono prove locali su dati sintetici; non costituiscono validazione fisiologica del metodo. Per ripeterle: [guida completa, inclusa GUI](TESTARE_IL_PROGETTO.md).

## Automatiche

`python -m pytest -q`: **26 test passati**. Copertura dei comportamenti principali:

- avvio completo del backend HTTP senza stdout/stderr, come nel bundle Windows senza console;
- ERG forniti, salti e rampe, validazione dei punti e confini degli step;
- ultimo step completo, interpolazione distinta, dati mancanti, campionamento irregolare e recupero;
- FIT sintetico con CRC e rifiuto dei file alterati;
- aggiornamenti concorrenti, revisioni di test con campioni e risultati storici;
- preset zone ai confini esatti, schemi a 3/5/7 zone e tempi non classificati;
- CSV con anteprima, commit atomico, blocco del lotto errato, ID e reimportazioni;
- storico per atleta rispetto a tutti i test, crescita descrittiva e confronto appaiato;
- report MD/PDF, lingua dei titoli, logo incluso e attribuzione fissa; rifiuto di un campo logo nell'anagrafica società;
- workspace separati, visualizzatore bloccato, inviti cifrati, verifica delle firme anche con pacchetto alterato usando la chiave di lettura;
- conflitto fra due admin e convergenza dopo risoluzione.

È presente un avviso di deprecazione dell'integrazione Starlette/httpx; i test passano. Non è un errore del metodo o dei dati.

Controllo TypeScript `tsc -b`: riuscito. Build Vite di produzione: riuscita. Asset PNG copiato in `frontend/dist/branding/progetto-ciclismo.png`; bundle JavaScript circa 5,17 MB prima della compressione. Avviso Vite sul chunk grande dovuto soprattutto a Plotly, da ottimizzare nel consolidamento.

## Interfaccia

Verificata nel browser locale su archivio sintetico separato `.local/qa-02`:

- elenco atleti, pulsanti di ordinamento, profilo e grafici della MAP/peso/statura;
- logo leggibile nel footer e dicitura fissa richiesta;
- categoria Allievi con sottogruppo Stagione 2026;
- pagina storici: 4 atleti e 4 test selezionati nel default, 12 test nella modalità Tutti i test;
- pannello copertura, variazioni antropometriche e disponibilità del confronto appaiato;
- cambio IT → EN → IT, con branding invariato;
- apertura Nuovo test e aggiunta di due zone FC: 7 zone FC e 5 potenza, con 12 campi nome zona complessivi.

Durante il collaudo è stato individuato un ridimensionamento Plotly su un elemento non più visualizzato: gestione aggiornata con stato del rendering, controllo di visibilità e pulizia dell'observer. La navigazione non deve generare errori di resize quando i grafici vengono rimossi.

I test API coprono salvataggio e revisione; la checklist GUI completa rimane necessaria per ogni rilascio e sistema operativo. Non tutte le righe della guida sono state eseguite manualmente in questa sessione.

## Report

Report sintetico con logo, attribuzione e zone renderizzato in tre pagine PNG e ispezionato visivamente: tabelle, grafico, crediti e cambi pagina leggibili. Verificati anche export Markdown con asset e manifest e generazione del report storico via API. I PDF di prova sono sotto `tmp/qa/`, esclusi dalla repository.

## Limiti del collaudo

Nessun FIT reale di GoldenCheetah/MyWhoosh/Zwift fornito. Nessuna prova su Fedora, PC Windows pulito o client cloud reale eseguita. Lo scambio testato fra directory locali non certifica affidabilità di Google Drive/Dropbox o consegna su due PC reali.

La regola provvisoria di step completo richiede durata prevista e almeno 95% di copertura potenza, senza controllo dell'aderenza al target. I riferimenti per le zone derivano dagli input/metodi dichiarati; nessun coefficiente fisiologico universale viene validato dai test software.

## Avvio senza finestra e risorse

Smoke test della shell da sorgente eseguito con `--smoke-test --data .local/smoke-02-source`: riuscito. Verificato che il logo originale, quello in repository e quello nel frontend compilato siano identici byte per byte. Collegamenti locali e blocchi Markdown della documentazione verificati.

## Correzioni del packaging Windows

Individuata e rimossa dalla ricerca delle dipendenze una DLL ICU di Poppler introdotta dal PATH degli strumenti. La build usa ora un PATH isolato per il solo sottoprocesso. Lo smoke test è stato esteso: importa Qt WebEngine, controlla il logo, avvia il backend e verifica `/health`. Logging desktop indipendente dalla console e diagnostica locale in `server.log`; avvio del backend fallito segnalato esplicitamente. Il test automatico senza stdout/stderr passa.

## Esito finale del bundle Windows

Build pulita riuscita con PATH isolato. Eseguito `CicloTest.exe --smoke-test` sul bundle finale: import, logo e backend HTTP verificati, marker in `.local/smoke-02-final/smoke-ok.txt`. Avviata anche la finestra sul desktop Windows: interfaccia caricata e footer con logo/attribuzione verificati visivamente e tramite accessibilità. Non equivale ancora al collaudo su un PC pulito.
