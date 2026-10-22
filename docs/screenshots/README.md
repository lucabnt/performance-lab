# Schermate dell’interfaccia

Galleria incorporata nel [README principale](../../README.md). Acquisizione: **20 ottobre 2026**, Fuorigiri **0.10.0**, sorgenti al commit `50d242b`, UI comune `@cycling-suite/ui` **0.2.2**. Immagini JPEG reali del browser locale (circa 1230 × 950 pixel), senza ritocchi ai contenuti. L’interfaccia è la stessa inclusa nella finestra desktop; queste immagini non documentano una build Linux o Android.

Sono stati usati soltanto archivi sintetici già disponibili: corpus completo per le funzioni prestative e corpus ridotto con casi crescita per la maturazione. I conteggi fotografano quelle demo e non sono requisiti del prodotto. Non sono stati rigenerati archivi, corretti risultati o eseguite sincronizzazioni per realizzare le immagini.

## Riprodurre la galleria

Seguire [Testare il progetto](../TESTARE_IL_PROGETTO.md) per predisporre l’ambiente. Compilare il frontend corrente e generare un corpus **in una destinazione nuova**; non svuotare la demo abituale per aggiornare gli screenshot:

```powershell
npm --prefix frontend run build
.venv/Scripts/python.exe scripts/demo_suite.py --data .local/qa-galleria-nuova
.venv/Scripts/python.exe scripts/serve.py --data .local/qa-galleria-nuova --port 8766
```

Su Linux usare `.venv/bin/python`. Aprire l’URL completo con token stampato dal server, selezionare **Velodromo Aurora - SIMULAZIONE** e la lingua italiana. Il generatore completo corrente include anche i casi crescita: non serve un secondo generatore. Attendere che caricamenti e grafici siano completati prima di acquisire ogni vista.

| File stabile | Percorso nell’interfaccia e inquadratura |
|---|---|
| `atleti.jpg` | Atleti, nessun filtro: intestazione, riepiloghi e prime righe della squadra. |
| `protocolli.jpg` | Protocolli, famiglie Tutte e stato Attivi: comandi di creazione/import e prime schede con grafico. |
| `test-incrementale.jpg` | Test e analisi → Dati disponibili → Con tracciato FIT/CSV → Riva Giulia, 15/03/2026, AER-RULLO-ALL → Analizza. Inquadrare testata e intero grafico; lasciare potenza, FC e cadenza abilitate. |
| `test-wingate.jpg` | Stesso filtro → Moretti Elena, 10/06/2026, Wingate 30 s → Analizza. Inquadrare testata, tracciato e inizio del riepilogo. |
| `storici-confronti.jpg` | Storici e confronti → MAP operativa, Vista Stagione, Mediana. Lasciare la serie principale proposta; scorrere fino a includere titolo del grafico, curva, chiave della serie e tabella con media/mediana/numerosità. |
| `crescita-maturazione.jpg` | Atleti → Crescita DEMO peak Andrea → Crescita e maturazione. Inquadrare data di riferimento, selettore dell’analisi, HV/PHV, curva e inizio delle stime datate. La cattura corrente usa l’anteprima al 20/10/2026. |
| `report-esportazioni.jpg` | Archivio e scambio, inizio pagina: ambito del report società/gruppo/stagione/atleta, comandi PDF/Markdown e importazione CSV. |

Usare una normale finestra desktop e zoom browser al 100%, inquadrature comparabili e testo leggibile. Conservare abbastanza contesto per riconoscere la pagina o il dettaglio. Acquisire il solo contenuto dell’app, senza barra degli indirizzi, token, finestre del sistema o tool di sviluppo. Non aprire nei fotogrammi identità, inviti, credenziali o percorsi personali. Nessun account cloud reale è necessario.

## Quando aggiornare

- Nello **stesso intervento** che modifica una schermata rappresentata, acquisire di nuovo le immagini interessate con il frontend ricompilato, comprese le modifiche alla libreria UI comune.
- Prima di una release, rivedere tutte le immagini e aggiornare quelle non più rappresentative. Per un cambio di versione acquisire nuovamente le viste che espongono il numero prodotto; non ritoccare digitalmente il numero in un vecchio screenshot.
- Sostituire i file mantenendo i nomi stabili, così i link del README rimangono validi. Aggiornare data/versione/commit qui e nel testo della galleria; se si aggiorna solo una parte, indicare per file le date e versioni diverse.
- Controllare ogni immagine a dimensione originale e nell’anteprima Markdown: grafici disegnati, nessun caricamento/errore, niente tooltip che coprono i dati, nessuna informazione personale. Le immagini non devono presentare funzioni progettate come già implementate.
- Registrare l’aggiornamento nel changelog e le verifiche effettive in VERIFICA.md. Il rinnovo è una verifica redazionale **manuale**, non un job automatico né una prova funzionale completa.

Non includere backup o archivi di generazione nella repository. Terminato il lavoro chiudere il browser QA e arrestare il server locale con Ctrl+C.


## Android: navigazione, elenchi e moduli — 21 ottobre 2026

`android-menu.png`, `android-info.png`, `android-atleti.png`, `android-modulo.png` e `android-grafico.png` e `android-grafico.png` documentano l’APK debug reale su emulatore API 35 x86_64: Fuorigiri 0.10.0, UI comune 0.2.6, HEAD `d67afad` più modifiche locali TD-98–104. Catture PNG integrali 1080 × 2424, senza ritocchi. Società sintetica Velodromo Aurora - SIMULAZIONE ripristinata come copia QA indipendente; nessun account cloud o dato personale. Le immagini desktop sopra conservano provenienza distinta. Non rappresentano il collaudo su telefono.

- `android-menu.png`: Apri menu; società, sezioni, Info e lingua.
- `android-info.png`: sezione Info con versione, stato locale/offline, logo e attribuzione fissi, licenza.
- `android-atleti.png`: elenco atleti, riepilogo e filtri chiusi, schede e comandi touch.
- `android-modulo.png`: Aggiungi atleta, modulo vuoto senza salvataggio; checkbox allineata e azione Salva persistente. Chiudere senza creare record.
- `android-grafico.png`: Test e analisi → dati Con tracciato → primo Riva Giulia, 01/10/2026, Discontinuo descrittiva DEMO. Scorrere alla figura completa e comandi sottostanti; Scorri pagina attivo, nessun tooltip. Potenza/FC/cadenza selezionate.

Ripetere le catture interessate dopo modifiche Android. Verificare anche Indietro, mantenimento di filtri/pagina, conferma delle modifiche non salvate e riapertura della società. Non sostituire le immagini desktop con quelle Android.

### Aggiornamento TD-105, 21 ottobre 2026

`android-grafico-orizzontale.png`: nuova cattura reale della Vista ampia sull’emulatore API 35 x86_64, APK TD-105 (UI comune invariata 0.2.6), 2424×1080. Stesso test sintetico Riva Giulia 01/10/2026 indicato sopra, Scorri pagina attivo e motore grafico pronto. Aprire Vista ampia e attendere rotazione/resize prima della cattura. Immagine integrale senza ritocchi; non rappresenta un telefono fisico. Le altre catture conservano la provenienza TD-102–104.

### Aggiornamento TD-106–107, 21 ottobre 2026

Sostituiti `android-grafico-orizzontale.png` e `android-atleti.png` con catture integrali reali dell’APK TD-106–107, UI comune 0.2.7, stessa società sintetica e stesso emulatore. Vista ampia ora immersiva, priva della testata visiva, con X e pannello Comandi grafico chiuso; barre Android nascoste, cutout rispettato. Dismiss dell’istruzione fullscreen del sistema prima della foto; nessun ritocco delle immagini. Le altre catture mantengono la provenienza precedente.

### Correzione logo a destra, 21 ottobre 2026

Rinnovati android-atleti.png, android-menu.png e android-info.png: APK con common UI 0.2.8, logo dopo la scritta e allineamento a destra nella testata. Stesso emulatore/società sintetica, foto integrali ispezionate. Le catture dei grafici mantengono la propria provenienza.

## Codice dei protocolli — 22 ottobre 2026

`protocollo-codice.png`: browser locale, Fuorigiri 0.10.0 con modifiche PROTOCOLLI-01, UI comune 0.2.8. Archivio QA nuovo e società interamente sintetica. Nuova versione Wingate 15 s: campo Codice modificabile con `ANA-DEMO-15` ereditato dalla scheda appena salvata. Immagine reale senza ritocchi; nessun installer aggiornato o collaudo Android implicito.

## Import CSV del 22 ottobre 2026

`import-csv-anaerobici.png`: componente ImportPanel reale in pagina QA locale dedicata, con backend FastAPI reale e archivio sintetico nuovo. Mostra modello vuoto scaricabile e preview di Sprint e Wingate 30 s nello stesso lotto, protocolli separati dalle righe. Fonte frontend corrente 0.10.0 e UI comune 0.2.8; screenshot senza ritocchi, non una cattura del bridge Android o del telefono. Verificati anche gli altri tre profili e tutti i download; guide e prove in IMPORT_CSV.md e VERIFICA.md.
