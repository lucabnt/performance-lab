# Come testare il progetto, inclusa l'interfaccia

## Verifica 0.6: WebDAV, distribuzione e Android

Eseguire prima `python -m pytest -q`, quindi `npm run build` in frontend. I test WebDAV avviano un server di fixture locale con rete loopback; la configurazione di produzione ammette solo HTTPS. Il test di Credential Manager reale richiede la sessione utente Windows; la sandbox di sviluppo può non avere un logon utilizzabile. La suite non legge password reali.

Per la GUI: `python scripts/serve.py --data .local/qa-06 --port 8768`, aprire l’URL completo con token stampato dal comando. Creare una società sintetica, poi Archivio e scambio → Condivisione e collaboratori. Provare cartella separata e scambio ripetuto; URL WebDAV invalido, password mancante/portachiavi bloccato, server HTTPS di prova, invito visualizzatore, due modifiche concorrenti, risoluzione esplicita. Mai usare dati operativi per questi casi.

Prova WebDAV reale: due account sulla stessa cartella Nextcloud, due archivi/identità, admin e viewer (anche sola lettura sul server), allegati FIT e PDF, perdita rete prima/dopo PUT, doppio invio, credenziale revocata, pacchetto alterato e ripresa. La rotazione richiede prima tutte le modifiche ricevute: provare chiusura del vecchio canale, nuovi inviti, arresto dopo avviso remoto, riavvio e completamento, quindi nuovo recupero accessi. L’esito server fixture non certifica Nextcloud.

Windows: `python scripts/build.py`, compilare `packaging/windows/Fuorigiri.iss`, installare su un PC/VM senza strumenti di sviluppo, avviare offline, creare test e produrre PDF, aggiornare, riaprire l’archivio e disinstallare verificando che il backup/dati restino. Il bundle completo deve avviarsi anche con PATH privo di Python/Node; `Fuorigiri.exe --smoke-test --data <cartella-di-prova>` verifica import, logo, icona, portachiavi importabile e backend. Provare due avvii sullo stesso archivio: il secondo deve essere respinto.

Fedora: seguire [la build Flatpak](CONSOLIDAMENTO_DISTRIBUZIONE_06.md), installare su Fedora pulita, provare Wayland e fallback X11, Secret Service, picker, report, WebDAV e cartella client cloud. Testare anche installazione offline con runtime disponibili sul supporto; la sola `.flatpak` non basta.

Android: `python scripts/build_android.py --check` elenca i gate reali; non scarica librerie né produce un APK fittizio. Dopo compilazione su builder adatto: `gradle -p android connectedDebugAndroidTest`, modalità aereo dopo installazione, riavvio/processo terminato, import ERG/FIT/CSV e report PDF/MD/CSV, invito viewer/admin, Keystore e scambio WebDAV con desktop. Controllare tutte le wheel native, ABI/16 KB, memoria su file grandi, tastiera/grafici/touch, WorkManager con rete/batteria e recupero da errori. I quattro test `test_mobile_runtime.py` verificano il contratto sul PC, non sostituiscono questi casi.

## Versione 0.5 — preset, metodi e report completi

`.venv/Scripts/python.exe -m pytest -q` verifica il nucleo e le API. Compilare TypeScript/Vite con i comandi sotto. Schema 3: alla prima apertura di un database precedente viene salvata `migrations/before-v3.sqlite`; la storia delle analisi resta invariata. Dettagli e limiti in [IMPLEMENTAZIONE_INCREMENTALE_05.md](IMPLEMENTAZIONE_INCREMENTALE_05.md).

Per una prova isolata completa: `.venv/Scripts/python.exe scripts/qa_incremental.py --data .local/qa-incrementale-05-nuova`, poi `.venv/Scripts/python.exe scripts/serve.py --data .local/qa-incrementale-05-nuova --port 8766`; aprire l’URL con token stampato. Solo quattro atleti/otto test sintetici, due stagioni. Non usare un archivio reale per questi comandi; lo script rifiuta destinazioni già popolate.

Checklist GUI: «Archivio e scambio → Report completo dell’archivio», anteprima società, gruppo, stagione e atleta; controllare i conteggi e scaricare PDF/MD. «Test e analisi»: dettaglio dei metodi/aderenza, curve lattato e gas del primo atleta 2026. Per un nuovo import scegliere file e sessione, quindi «Importa sessione selezionata»; calcolare anteprima dopo aver impostato fine sforzo. Nel form creare un preset nuovo, aggiungere marker/esclusioni con motivo, condizioni e gas CSV quando disponibili. In «Storici e confronti», la ripetibilità richiede coppie confrontabili e conferma esplicita di condizioni stabili, con export PDF/MD+CSV.

Cinque esempi PDF e quattro ZIP generati in `output/pdf/`: società, gruppo, gruppo/2026, atleta e singolo test specialistico. Sono dimostrazioni sintetiche, non referti degli atleti dell’allegato. Il bundle Windows rimane `dist/Fuorigiri/Fuorigiri.exe`; va distribuita tutta la directory. Fedora e corpus FIT reali richiedono prove dedicate.


## Rinomina 0.4.1 e specifica dei metodi

Avvio da sorgenti e procedura GUI restano quelli sotto. Distribuzione aggiornata: `dist/Fuorigiri/Fuorigiri.exe` su Windows, `dist/Fuorigiri/Fuorigiri` su Linux dopo build nativa. Comandi installati `fuorigiri` e `fuorigiri-performance-lab`; variabili `FUORIGIRI_DATA`, `FUORIGIRI_TOKEN`, `FUORIGIRI_API_URL`. Header interni `X-Fuorigiri-Token` e `X-Fuorigiri-Workspace`: frontend e backend devono essere aggiornati insieme. Riaprire l’app dopo l’aggiornamento per ottenere una nuova sessione; impostazione lingua e selezione società nel browser usano nuove chiavi.

Nuove installazioni: `%LOCALAPPDATA%/Fuorigiri` o `~/.local/share/Fuorigiri`. Se esiste soltanto la directory storica, il programma la riusa senza rinominarla: il registro contiene percorsi assoluti. Se esistono entrambe, usa Fuorigiri; per aprire l’altra passare `--data` esplicito. Non spostare archivi a mano. Lo stesso vale per un canale cloud precedente già presente: viene riutilizzato con le stesse chiavi; i nuovi canali hanno prefisso `fuorigiri-`. Due canali con la stessa chiave sono segnalati come errore invece di dividerne la storia. Per un canale nuovo aggiornare tutti i collaboratori alla stessa versione prima dello scambio. Il formato cifrato e l’estensione `.ctsync` rimangono compatibili.

La [specifica 1.0](METODI_INCREMENTALE.md) contiene i risultati attesi per lo sviluppo del motore successivo: **non tutti i suoi casi passano già nel motore 0.2.0**. Non confondere i test della rinomina con la validazione dei futuri algoritmi. Android è soltanto pianificato in [ANDROID.md](ANDROID.md).


Aggiornato il 17 ottobre 2026. I comandi partono dalla cartella del progetto. Le prove usano archivi sintetici separati dai dati operativi. L'interfaccia e il motore funzionano senza collegamenti a servizi esterni.

## Novità della preview 0.4 — società, backup e accessi

Guida dettagliata: [SOCIETA_BACKUP_E_ACCESSI.md](SOCIETA_BACKUP_E_ACCESSI.md). Suite corrente: **45 test passati**. Creare due archivi isolati su porte diverse, poi provare il flusso dal fondatore al visualizzatore/admin; nessun dato reale necessario.

1. Gestisci società → Crea nuova società: soltanto nome società/fondatore obbligatori; apertura automatica. Aggiungere un atleta sintetico.
2. In Condivisione e collaboratori generare un invito Visualizzatore e pubblicare i dati su una cartella locale condivisa di prova.
3. Nell’altra istanza usare Collega tramite invito. Prima di acquisire record, verificare che la società abbia già nome/ruolo e pulsante Prima sincronizzazione. Acquisire e controllare comparsa atleta e vincoli di modifica.
4. Dal fondatore usare Rinnova / cambia ruolo → Admin dati, scaricare il nuovo invito e pubblicare la revoca. Sul destinatario Applica nuovo invito: stesso archivio, nuovo ruolo, scrittura ora consentita. Provare anche la revoca e verificare che gli eventi già autorizzati rimangano disponibili su un terzo dispositivo appena collegato.
5. Esportare backup dati ZIP e recupero accessi cifrato separatamente. Usare una terza directory di avvio vuota per recuperare il fondatore: anteprima ZIP, modalità originale, file recupero e password. Verificare dati, possibilità di creare inviti e successiva sincronizzazione.
6. Provare lo stesso ZIP come copia di consultazione (nessuna modifica/canale) e come copia indipendente (nuovo fondatore/canale, nessun invito originale). Se contiene più società, verificarne la selezione.
7. Password errata, file di altra società, ZIP corrotto, destinazione occupata e società originale già registrata devono fallire senza sovrascrivere dati. Dopo errore la prova deve essere ripetibile; un annullamento prima della conferma non crea un archivio registrato.

Le prove automatiche simulano archivi diversi sullo stesso PC; i client cloud reali e Fedora richiedono ancora collaudo. Il recupero originale è una sostituzione/recupero del fondatore, non una procedura per clonarne l’identità su PC usati contemporaneamente. I segreti delle fixture rimangono fuori dai dati di produzione e dalla repository pubblica.

## Novità della preview 0.3 (precedenti)

Nome dell'app **Fuorigiri Performance Lab**; dalla 0.4.1 anche il bundle si chiama Fuorigiri. La sezione seguente conserva la procedura 0.3 (32 casi allora disponibili). Per provare la GUI con i nuovi esempi usare un percorso nuovo:

```powershell
.venv/Scripts/python.exe scripts/demo.py --data .local/demo-fuorigiri
.venv/Scripts/python.exe scripts/serve.py --data .local/demo-fuorigiri --port 8766
```

Aprire l'URL completo stampato (con token). Stesso comando `python scripts/demo.py ...` / `python scripts/serve.py ...` nell'ambiente attivo su Fedora. La demo contiene **quattro atleti, due ERG originali, due categorie con stagione e quattro FIT realmente decodificati**. Le esecuzioni sono simulate. Genera PDF di QA in `tmp/qa-fuorigiri/test.pdf` e `storico.pdf`.

Checklist aggiuntiva:

1. Selettore Società unico; Gestisci società apre creazione/associazione, Società e gruppi contiene solo categorie.
2. Crea gruppo con padre Allievi, stagione 2027 e nome vuoto: deve ereditare Allievi. Categoria principale senza nome deve essere rifiutata.
3. Protocolli → Crea protocollo manuale → Solo scheda d'archivio, senza step; salvare identità/versione. ERG disabilitato, JSON disponibile.
4. Nuovo test → Inserisci solo dati manuali: scegliere la scheda, data, MAP 230 e peso 50; risultato dichiarato 4,6 W/kg, nessun FIT obbligatorio. Lasciare FTP/FC vuote: non devono diventare zero. Correggere creando una revisione.
5. Storici: scegliere categoria/totale, media/mediana, metrica e protocollo; nella demo i due protocolli restano separati e le medie MAP sono 295 e 190 W. I test automatici includono una distribuzione asimmetrica con media 200 e mediana 100.
6. Esportare PDF e Markdown dello storico: metrica e statistica devono coincidere con la vista. Il PDF ha logo/credito nel footer di ogni pagina; niente sovrapposizioni.
7. Nel dettaglio di un FIT scorrere fino in fondo e tornare su: la lista sotto non deve muoversi né attraversare la superficie opaca. Chiudendo, lo scroll della pagina deve funzionare di nuovo.
8. Archivio e scambio: importazione, export/backup e report prima delle sezioni espandibili. I campi CSV richiesti sono indicati per ciascun profilo.

Esempi persistenti in `examples/synthetic/`: quattro `.fit`, manifest e CSV `atleti.csv`, `antropometria.csv`, `test_aerobico.csv`. Per provare il bulk CSV usare **un altro archivio vuoto**, importare prima atleti, poi antropometria e storico, confermando ciascun lotto dopo l'anteprima. I CSV storici rappresentano gli stessi test dei FIT: non importare entrambi nello stesso archivio. Per il percorso FIT usare gli ERG in `examples/protocols/`, riscaldamento 600 s, fine sforzo dal manifest (il file include 180 s di recupero). Peso/FC/RPE sono dati sintetici dichiarati nel manifest.

Le sezioni seguenti spiegano installazione, desktop, Vite e bundle; dove riportano fixture della 0.2 valgono gli aggiornamenti qui sopra.

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

Lo script corrente crea quattro atleti e quattro test basati sugli ERG originali. Si arresta su archivi già popolati. Esempi FIT/CSV in `examples/synthetic`, PDF di QA in `tmp/qa-fuorigiri`; vedere la checklist 0.3 sopra. Gli allegati personali originali non vengono copiati nelle fixture.

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

Aprire l'URL **Vite sviluppo** stampato dal server Python, incluso il suo token. Vite usa `127.0.0.1:5173` e inoltra `/api` al backend `127.0.0.1:8766`. Per un backend su un'altra porta configurare `FUORIGIRI_API_URL` prima di avviare Vite:

```powershell
$env:FUORIGIRI_API_URL = 'http://127.0.0.1:8767'
npm run dev
```

Linux: `FUORIGIRI_API_URL=http://127.0.0.1:8767 npm run dev`. Non basta aprire `frontend/index.html` direttamente dal filesystem: serve il backend e, in sviluppo, Vite.

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
| CSV storico | Archivio e scambio → importare prima `xamples/synthetic/atleti.csv`, poi antropometria e storico; verificare anteprima prima della conferma. | Riconciliazione tramite ID; import ripetuto senza duplicati. Una riga errata blocca il lotto. |
| Aggregazioni | Storici e confronti → cambiare vista, stagione, categoria, atleta, metrica e modalità. | Media, mediana e conteggi aggiornati. La demo iniziale contiene un test per ciascuno dei quattro atleti: le due modalità hanno perciò lo stesso conteggio; aggiungere un secondo test dello stesso atleta/protocollo per verificarne la differenza. |
| Crescita/confronti | Consultare Variazioni antropometriche; scegliere due stagioni in Confronto sugli stessi atleti. | Delta e intervallo dichiarati; nessuna coppia inventata se manca una stagione. Per provare una coppia aggiungere un test con lo stesso protocollo in un'altra stagione. |
| Report | Scaricare PDF/Markdown di test e storico, poi CSV. | File leggibili; logo e credito fissi; zone dinamiche nei report; ZIP Markdown con immagini e manifest. CSV compatibili e dati estesi separati. |
| Ciclo di vita | Archiviare un atleta, controllare gli storici; eliminarlo e poi ripristinarlo dal filtro Eliminati. | Archiviato conservato negli storici; eliminato escluso dai nuovi calcoli; ripristino possibile. |
| Lingua | Selezionare English e poi Italiano. | Navigazione e form cambiano lingua. Il cambio ricarica la pagina: salvare prima eventuali bozze. Dati, codici e attribuzione fissa restano identici. |
| Offline e tastiera | Scollegare Internet mantenendo attivo il server locale; usare Tab/Invio e zoom browser. | Archivio, grafici e report locali utilizzabili; focus visibile, link esterni facoltativi. |

## 6. Provare due dispositivi, ruoli e conflitti senza cloud

**Corretto nella 0.4:** la società appena associata espone ora la prima sincronizzazione anche senza record locali. Il percorso seguente è disponibile dalla GUI. Il backup ZIP rimane distinto dall’invito e dal file di recupero accessi: vedere la guida collegata sopra.

Usare due directory di avvio diverse e due sessioni browser separate. Per evitare contaminazioni del token utilizzare profili/browser distinti oppure una sessione privata. Prima istanza `.local/pc-a` sulla porta 8766, seconda `.local/pc-b` sulla porta 8767. Basta una cartella locale vuota esterna a entrambe, per esempio `.local/scambio-test`, per simulare il trasporto; non serve un account cloud per questa prova.

1. Dal primo dispositivo creare una società separata in Gestisci società e selezionarla dal menu Società. Il dispositivo diventa fondatore.
2. Creare dati sintetici nella società. Specificare nome del collaboratore, ruolo e password di almeno 12 caratteri; scaricare l'invito cifrato.
3. Nel secondo dispositivo associare il file d'invito con la password e selezionare la società ricevuta. Inizialmente può essere vuoto: i dati arrivano con lo scambio.
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
dist/Fuorigiri/Fuorigiri.exe --smoke-test --data .local/smoke-02
dist/Fuorigiri/Fuorigiri.exe --data .local/ui-test
```

Controllare che `.local/smoke-02/smoke-ok.txt` esista. La prova smoke verifica import, logo e avvio del backend HTTP senza aprire finestre; aprire anche l'app per verificare la GUI. Distribuire tutta `dist/Fuorigiri/`, non il solo EXE. Ripetere su un PC pulito, senza Python/Node. La build non equivale ancora a installer firmato. Un bundle Linux va costruito e verificato su Linux.

Usare lo script di build del progetto: su Windows isola il PATH del sottoprocesso per evitare che DLL di altri programmi finiscano nel bundle. Nel collaudo è stata individuata una copia ICU di Poppler che impediva a Qt di caricarsi; la correzione è nello script, senza modifiche al PATH di sistema. Se si sta usando un bundle precedente alla correzione, ricostruirlo interamente prima di ripetere lo smoke test.

## 8. Registrare l'esito

Annotare versione app, sistema operativo, versioni Python/Node, percorso dell'archivio di prova, risultato dei comandi e checklist eseguita. Per anomalie riportare passaggi minimi, risultato atteso/ottenuto e messaggio; usare screenshot privi di dati reali. Lo stato delle verifiche effettuate è in [VERIFICA.md](VERIFICA.md); requisiti e scelte ancora aperte in [REQUISITI_E_TODO.md](REQUISITI_E_TODO.md).
