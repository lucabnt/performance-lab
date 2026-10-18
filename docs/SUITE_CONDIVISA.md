# Librerie condivise con Ammiraglia

## Decisione confermata

Fuorigiri, Ammiraglia e il codice comune hanno repository separate. La repository locale delle librerie è `F:\GitHub\cycling-suite-common`, ramo main, primo tag `ui-v0.1.0`. Non è stata pubblicata su GitHub e non ha un remote configurato. Non sono stati creati account o scope su npm.

Questa scelta sostituisce la proposta conversazionale di una monorepo con entrambe le applicazioni. I workspaces npm nella repository comune organizzano soltanto libreria ed esempi: non inglobano le app.

## Cosa è già condiviso

`@cycling-suite/ui` 0.1.0: tema a variabili CSS, Field, DataTable, SortableTable e SuiteBranding, con catalogo interattivo, test e build/pacchetto. Fuorigiri importa questi componenti; non mantiene più le loro implementazioni duplicate nei moduli locali. Conserva piccoli wrapper per gli import precedenti e il proprio nome nel footer. Logo e attribuzione societaria rimangono fissi; il logo per PDF/backend rimane l’originale in Fuorigiri.

Il catalogo consente di scegliere il nome Ammiraglia, ma non è l’integrazione nell’app Ammiraglia. Per quella usare README e docs/INTEGRAZIONE.md della repository comune, disponibili all’agente che sviluppa il secondo prodotto.

## Consumo riproducibile

Fuorigiri include il tarball in `frontend/vendor` e lo referenzia con `file:vendor/...` nel package.json e lockfile. Il pacchetto contiene anche sorgenti, script, dichiarazioni, licenza e avvisi. Una nuova clonazione non richiede una repository sorella né una rete raggiungibile durante l’esecuzione del prodotto. L’installazione di sviluppo delle altre dipendenze segue la normale procedura npm.

`suite-ui-provenance.json` registra versione, commit/tag e SHA256. Per verificare:

```powershell
python scripts/verify_suite_ui.py
cd frontend
npm ci
npm run build
```

Le build desktop verificano anche la provenienza prima del packaging. Non si usa npm link né un percorso assoluto verso la libreria nei rilasci. Per aggiornare una dipendenza: rilasciare una nuova versione comune, aggiornare artefatto/provenienza/lockfile e verificare ogni applicazione separatamente. Nessun aggiornamento automatico da main.

## Avvio del catalogo

Dalla repository comune:

```powershell
npm ci
npm test
npm run build
npm run dev
```

Aprire http://127.0.0.1:8782. Testare nomi applicativi, branding fisso, filtri, ordinamento crescente/decrescente, zero/mancanti e campi disabilitati. I dati sono fittizi, non vengono salvati e non esiste un’autorizzazione backend nel catalogo.

## Successivi passi

1. Integrare il pacchetto nella repository Ammiraglia, senza copiare i sorgenti delle pagine Fuorigiri.
2. Estrarre shell, navigazione e modali con verifica tastiera/focus/mobile; le voci del menu rimangono specifiche per app.
3. Definire contratti dati/client condivisi e una matrice di compatibilità.
4. Estrarre servizi Python soltanto con test di archivi, revisioni, accessi, backup e sincronizzazione.

I motori fisiologici rimangono in Fuorigiri e la pianificazione in Ammiraglia. Nessuna condivisione automatica di SQLite, credenziali o autorizzazioni deriva dalla libreria UI. Lo scambio dei dati richiede un progetto separato e identificativi/provenienza/versioni verificabili.

## Verifiche e limiti di questa estrazione

Repository comune installata dalla cache locale con npm ci e verificata autonomamente: 4 test UI, compilazione TypeScript, build catalogo e tarball. Fuorigiri: TypeScript/Vite e 117 test backend passati; GUI browser verificata su dati sintetici per tabelle e modulo atleta. Rimane l’avviso Vite sul chunk Plotly grande e il warning Starlette/httpx già presente.

Nessun installer nuovo, pubblicazione remota, integrazione Ammiraglia, build Linux/Android o modifica dello schema dati eseguiti in questo passaggio.
