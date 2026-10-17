# Come testare il progetto, inclusa l'interfaccia

Aggiornato il 17 ottobre 2026. I comandi partono dalla cartella del progetto. Le prove usano archivi sintetici separati dai dati operativi. L'interfaccia e il motore funzionano senza collegamenti a servizi esterni.

## 1. Preparare l'ambiente

Servono Python 3.12 o successivo e Node.js 22 o successivo. Per la finestra desktop installare anche le dipendenze `desktop`; usando il browser è sufficiente il backend. Per lo sviluppo sono necessari entrambi i runtime; il bundle finale include Python e le risorse della GUI.

Windows PowerShell:

```powershell
cd F:\GitHub\test-analysis
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[desktop,dev]"
Set-Location frontend
npm ci
npm run build
Set-Location ..
```

Fedora, dalla directory in cui è stato copiato il progetto:

```bash
sudo dnf install python3 python3-pip nodejs npm
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[desktop,dev]'
cd frontend
npm ci
npm run build
cd ..
```

La prova Fedora deve verificare anche librerie grafiche richieste dalla versione Qt/PySide6 installata, Wayland e dialoghi file. Un errore del plugin di piattaforma Qt va risolto installando le dipendenze riportate dalla diagnostica, senza disabilitare la sandbox di Chromium. I test Fedora non sono ancora stati eseguiti in questa sessione.

Il lockfile npm viene usato da `npm ci`. `requirements-lock-windows.txt` descrive l'ambiente Windows iniziale e non è un lock portabile per Fedora; per una verifica riproducibile annotare le versioni effettive con `python -m pip freeze` e la versione Node.

## 2. Test automatici e compilazione della GUI

Windows:

```powershell
.venv/Scripts/python.exe -m pytest -q
Set-Location frontend
npm run build
Set-Location ..
```

Linux: sostituire `.venv/Scripts/python.exe` con `.venv/bin/python`.

`pytest` verifica il motore, i contratti API, le revisioni, i CSV, gli aggregati e lo scambio fra archivi temporanei. Non apre finestre. `npm run build` controlla TypeScript e genera la GUI in `frontend/dist/`; non avvia il backend e non dimostra da solo che tutte le interazioni funzionino. Il bundle Plotly è voluminoso: il relativo avviso di Vite non è un fallimento della build.

## 3. Creare dati dimostrativi

```powershell
.venv/Scripts/python.exe scripts/demo.py --data .local/ui-test
```

Lo script crea quattro atleti sintetici, una categoria con stagione, misure antropometriche, un protocollo e dodici test. Si arresta se l'archivio contiene già una società: per ripetere la prova usare un altro percorso, per esempio `.local/ui-test-2`. Non è necessario cancellare gli archivi precedenti.

Genera anche questi file di prova in `tmp/qa/`:

| File | Uso |
|---|---|
| `demo.fit` | Import del test eseguito con potenza, FC e cadenza |
| `demo.erg` | Definizione del protocollo sintetico |
| `demo-trace.csv` | Stesso tipo di serie temporale, colonne t/power/hr/cadence |
| `demo-atleti.csv` | Anagrafica con ID esterno `CSV-DEMO` |
| `demo-antropometria.csv` | Misura collegata all'anagrafica importata |
| `demo-storico.csv` | Risultato storico dichiarato, senza campioni |
| `report-demo.pdf` | Esempio di report del singolo test |

Sono esclusi dalla repository i dati runtime e gli artefatti di prova. Il PDF storico reale fornito dall'utente non viene usato come fixture.

## 4. Aprire l'interfaccia

Finestra desktop Qt:

```powershell
.venv/Scripts/python.exe -m cycling_test.desktop --data .local/ui-test
```

Browser di sistema, stessa applicazione compilata:

```powershell
.venv/Scripts/python.exe -m cycling_test.desktop --data .local/ui-test --browser
```

Server senza apertura automatica di finestre:

```powershell
.venv/Scripts/python.exe scripts/serve.py --data .local/ui-test --port 8766
```

Aprire l'URL completo **GUI compilata** stampato nel terminale, incluso `#token=...`. Il token è generato a ogni avvio e salvato soltanto nella sessione del browser. Se si apre un nuovo browser o viene riavviato il backend, usare il nuovo URL completo. Un vecchio token causa «Sessione non autorizzata». Nella modalità desktop senza console la diagnostica del server viene scritta in `server.log` nella directory dati; il token non viene scritto nel log.

Il server ascolta soltanto su `127.0.0.1`. `Ctrl+C` lo arresta. Non avviare due server sulla stessa porta; scegliere per esempio `--port 8767` per una seconda istanza. Il database persistente è quello passato a `--data`.

### Sviluppo con aggiornamento automatico della GUI

Tenere in esecuzione il server precedente sulla porta 8766. In un secondo terminale:

```powershell
Set-Location frontend
npm run dev
```

Aprire l'URL **Vite sviluppo** stampato dal server Python, incluso il suo token. Vite usa `127.0.0.1:5173` e inoltra `/api` al backend `127.0.0.1:8766`. Per un backend su un'altra porta configurare `CICLO_API_URL` prima di avviare Vite:

```powershell
$env:CICLO_API_URL = 'http://127.0.0.1:8767'
npm run dev
```

Linux: `CICLO_API_URL=http://127.0.0.1:8767 npm run dev`. Non basta aprire `frontend/index.html` direttamente dal filesystem: serve il backend e, in sviluppo, Vite.

## 5. Checklist manuale della GUI

| Prova | Passaggi | Risultato atteso |
|---|---|---|
| Avvio e branding | Aprire l'elenco atleti e scorrere fino in basso. | Quattro profili sintetici; logo locale e testo fisso «Sviluppato da Luca Bontempi per Progetto CIclismo - Rodengo Saiano A.S.D.». Nessun controllo per cambiarli. |
| Ordinamento | Cliccare due volte ATLETA; provare DATA e valori numerici nelle tabelle. | Indicatore crescente/decrescente e ordine coerente. I mancanti rimangono in fondo. |
| Profilo | Aprire un atleta, usare Modifica profilo, inserire data completa di nascita coerente con l'anno. | Modifica salvata; nome, anno e data disponibili dopo riapertura. Data/anno incoerenti sono rifiutati. |
| Antropometria | Aggiungere una rilevazione datata. | Tabella aggiornata e grafico peso/statura su assi con unità distinte. |
| Gruppi | Creare categoria e stagione figlia, assegnare l'atleta con date e anno di categoria. | Atleta unico con appartenenza storica; filtri e aggregati trovano la stagione selezionata. |
| Protocollo | Aprire Protocolli → Crea protocollo manuale; aggiungere fasi costanti o rampe e pubblicare. | Carico visibile; export ERG e JSON disponibili. Modifica tramite Nuova versione, senza alterare la precedente. |
| Import test | Nuovo test → scegliere atleta/protocollo → aprire `demo.fit` o `demo-trace.csv`. | Tracciato visibile prima del salvataggio. Per il protocollo `demo.erg`, fine sforzo 1440 s e peso 50 kg producono MAP 120 W; l'interpolazione è distinta. |
| Dati manuali | Inserire RPE 7, FTHR 180, Watt Soglia 200, FC a riposo e durata, recupero manuale o lattato. | Campi conservati; lattato non trasformato automaticamente in soglia. Le zone usano i riferimenti selezionati. |
| Ultima misura/default | Premere Proponi ultima antropometria; usare una data precedente a tutte le misure per verificare l'assenza di storico. | Proposta datata esplicita; nessuna misura futura presa automaticamente. Un preset configurato appare come stima. |
| Numero di zone | Aggiungere due zone nell'editor, controllare ordine e limiti, calcolare l'anteprima. | Anche sette zone funzionano. Limiti duplicati o decrescenti sono rifiutati. FC e potenza possono avere numeri diversi di zone. |
| Revisioni | Aprire un test → Correggi input e fine sforzo → cambiare RPE/fine sforzo, indicare motivo, ricalcolare e salvare. | Nuova revisione, risultati ricalcolati. I report precedentemente conservati restano scaricabili da Archivio e scambio. |
| CSV storico | Archivio e scambio → importare prima `demo-atleti.csv`, poi antropometria e storico; verificare anteprima prima della conferma. | Riconciliazione tramite ID; import ripetuto senza duplicati. Una riga errata blocca il lotto. |
| Aggregazioni | Storici e confronti → cambiare vista, stagione, categoria, atleta, metrica e modalità. | Mediane e conteggi aggiornati. Per la demo 12 test totali diventano 4 selezionati nel default per atleta; modalità Tutti i test ne usa 12. |
| Crescita/confronti | Consultare Variazioni antropometriche; scegliere due stagioni in Confronto sugli stessi atleti. | Delta e intervallo dichiarati; nessuna coppia inventata se manca una stagione. Per provare una coppia aggiungere un test con lo stesso protocollo in un'altra stagione. |
| Report | Scaricare PDF/Markdown di test e storico, poi CSV. | File leggibili; logo e credito fissi; zone dinamiche nei report; ZIP Markdown con immagini e manifest. CSV compatibili e dati estesi separati. |
| Ciclo di vita | Archiviare un atleta, controllare gli storici; eliminarlo e poi ripristinarlo dal filtro Eliminati. | Archiviato conservato negli storici; eliminato escluso dai nuovi calcoli; ripristino possibile. |
| Lingua | Selezionare English e poi Italiano. | Navigazione e form cambiano lingua. Il cambio ricarica la pagina: salvare prima eventuali bozze. Dati, codici e attribuzione fissa restano identici. |
| Offline e tastiera | Scollegare Internet mantenendo attivo il server locale; usare Tab/Invio e zoom browser. | Archivio, grafici e report locali utilizzabili; focus visibile, link esterni facoltativi. |

## 6. Provare due dispositivi, ruoli e conflitti senza cloud

Usare due directory di avvio diverse e due sessioni browser separate. Per evitare contaminazioni del token utilizzare profili/browser distinti oppure una sessione privata. Prima istanza `.local/pc-a` sulla porta 8766, seconda `.local/pc-b` sulla porta 8767. Basta una cartella locale vuota esterna a entrambe, per esempio `.local/scambio-test`, per simulare il trasporto; non serve un account cloud per questa prova.

1. Dal primo dispositivo creare una società separata nel pannello Workspace e collaboratori e selezionarla dal menu Workspace. Il dispositivo diventa fondatore.
2. Creare dati sintetici nella società. Specificare nome del collaboratore, ruolo e password di almeno 12 caratteri; scaricare l'invito cifrato.
3. Nel secondo dispositivo associare il file d'invito con la password e selezionare il workspace ricevuto. Inizialmente può essere vuoto: i dati arrivano con lo scambio.
4. Indicare in entrambi la stessa cartella di scambio, esterna ai database. Scambiare prima dal fondatore e poi dal ricevente. Verificare arrivo di società, atleta e protocollo.
5. Con un visualizzatore verificare consultazione ed export; tentativi di modifica devono essere rifiutati dal backend. Per il conflitto usare invece un invito Admin dati in un terzo archivio/profilo separato.
6. Per un conflitto, sincronizzare due admin, modificare offline lo stesso campo dello stesso atleta in entrambi, poi scambiare. In Archivio e scambio confrontare il record ricevuto e scegliere Mantieni locale o Accetta ricevuto. Scambiare di nuovo su entrambi: verificare convergenza.
7. Dal fondatore revocare un admin, scambiare e provare nuove scritture del dispositivo revocato. Le operazioni successive devono essere rifiutate/quarantinate. Le copie già ricevute e le chiavi di lettura esistenti non vengono cancellate da una revoca delle scritture.

L'associazione è per operatore/dispositivo tramite invito; non è un servizio di login remoto. Soltanto il fondatore gestisce inviti e revoche. `identity.json` contiene segreti locali: proteggere l'account e la cartella. Il backup dati ZIP attuale non include automaticamente le credenziali del fondatore: conservare separatamente e in modo protetto la cartella completa del workspace a programma chiuso prima di spostare il dispositivo fondatore.

Ripetere poi su due PC reali con il client cloud scelto: cartella disponibile offline, arrivi fuori ordine, interruzione client, copie conflittuali e riavvio. La prova locale non certifica il funzionamento di Google Drive/Dropbox né la compatibilità Fedora. L'app conferma scrittura/acquisizione locale, senza conoscere lo stato effettivo dell'upload cloud.

## 7. Verificare il pacchetto Windows

Dopo la build frontend:

```powershell
.venv/Scripts/python.exe scripts/build.py
dist/CicloTest/CicloTest.exe --smoke-test --data .local/smoke-02
dist/CicloTest/CicloTest.exe --data .local/ui-test
```

Controllare che `.local/smoke-02/smoke-ok.txt` esista. La prova smoke verifica import, logo e avvio del backend HTTP senza aprire finestre; aprire anche l'app per verificare la GUI. Distribuire tutta `dist/CicloTest/`, non il solo EXE. Ripetere su un PC pulito, senza Python/Node. La build non equivale ancora a installer firmato. Un bundle Linux va costruito e verificato su Linux.

Usare lo script di build del progetto: su Windows isola il PATH del sottoprocesso per evitare che DLL di altri programmi finiscano nel bundle. Nel collaudo è stata individuata una copia ICU di Poppler che impediva a Qt di caricarsi; la correzione è nello script, senza modifiche al PATH di sistema. Se si sta usando un bundle precedente alla correzione, ricostruirlo interamente prima di ripetere lo smoke test.

## 8. Registrare l'esito

Annotare versione app, sistema operativo, versioni Python/Node, percorso dell'archivio di prova, risultato dei comandi e checklist eseguita. Per anomalie riportare passaggi minimi, risultato atteso/ottenuto e messaggio; usare screenshot privi di dati reali. Lo stato delle verifiche effettuate è in [VERIFICA.md](VERIFICA.md); requisiti e scelte ancora aperte in [REQUISITI_E_TODO.md](REQUISITI_E_TODO.md).
