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

## Assegnazione gruppi del 22 ottobre 2026

`gruppi-aggiungi-atleti.png`: app completa compilata 0.10.0, UI comune 0.2.8, backend reale e archivio QA sintetico. Dialogo Aggiungi atleti con due selezioni, atleta già assegnato disabilitato e conferma. Verificati salvataggio multiplo nella stagione e singolo dal profilo; non è collaudo Android nativo. Immagine reale senza ritocchi o dati personali.

## Categorie e stagioni future — 25 ottobre 2026

`gruppi-stagioni.png`: nuova cattura reale della build web Fuorigiri 0.10.0 con GRUPPI-02, common UI 0.2.8. Archivio QA nuovo interamente sintetico, categoria Esordienti con stagioni 2026 e 2027 affiancate, etichetta Futura, conteggi e periodi espliciti. Allievi sotto segue la stessa struttura; verificata anche la stagione 2028 creata nel browser.

Rinnovato `gruppi-aggiungi-atleti.png`: sostituisce la cattura del 22 ottobre per questo file. Dialogo Esordienti 2027 con date proposte 01/01/2027 e 31/12/2027, un atleta selezionato e quello gia assegnato disabilitato. La selezione della cattura non e stata salvata; il salvataggio reale e stato verificato separatamente su Allievi 2027.

Immagini integrali del viewport del browser locale, nessun ritocco o dato reale. Nessuna provenienza APK o verifica del bridge/telefono implicita. Le altre immagini mantengono date e provenienze precedenti.

## Gestione gruppi e CSV appartenenze — 25 ottobre 2026

Fuorigiri web compilato 0.10.0, common UI 0.2.8, working tree con GRUPPI-03 e IMPORT-04, backend reale e archivio QA nuovo Societa DEMO appartenenze. Persone interamente sintetiche, nessun ritocco o token nelle immagini. Nessuna prova APK/IME/telefono implicita.

- `gruppi-eliminazione-ripristino.png`: stagione 2026 sulla categoria rimossa dalle scelte attive e disponibile per Ripristina; 2027 rimasto attivo.
- `import-csv-appartenenze.png`: quinto profilo, modello/esempio scaricabili, tre appartenenze storiche/future in anteprima e gruppi da creare separati dalle righe. Salvataggio verificato dopo la cattura.
- Rinnovati `gruppi-stagioni.png` e `gruppi-aggiungi-atleti.png` nello stesso intervento: gerarchia dopo import con comandi Modifica/Elimina e dialogo assegnazione futura. Sostituiscono le precedenti catture per questi file; le altre mantengono la propria provenienza.

Cattura finale `import-csv-appartenenze.png`: rigenerata dopo l'ultimo affinamento dei testi sul nuovo archivio QA Societa DEMO CSV storico, con il file esempio completo (4 appartenenze, 6 categorie/stagioni da creare). Sostituisce la precedente cattura del lotto da 3 righe per questo file; non mostra un salvataggio. Download reale del CSV verificato dal pulsante.

## Report archivio e filtro storico — 25 ottobre 2026

Build web compilata 0.10.0, common UI 0.2.8, backend reale e società QA interamente sintetica con 19 atleti, 89 test e 51 misure. Catture integrali senza ritocchi; nessuna verifica Android implicita.

- `gruppi-stagione-tutti.png`: apertura Esordienti 2023 con Tutti, ricerca vuota e tre atleti archiviati visibili.
- `report-esportazione-in-corso.png`: esportazione PDF effettiva, spinner e controlli disabilitati.
- Rinnovato `report-esportazioni.jpg`: anteprima conclusa, conteggi e controlli nuovamente disponibili. Conversione del solo formato PNG/JPEG, contenuti immutati; sostituisce la precedente cattura di questo file.


## Ordine delle pagine e KPI — 26 ottobre 2026

Fuorigiri 0.10.0, UI comune 0.2.8, build web con UI-ORDER-01 e nota integrativa sul grafico in apertura. Backend reale e soli dati sintetici. Rinnovati `test-incrementale.jpg` e `test-wingate.jpg`: grafico temporale prima dei KPI quando ci sono campioni rappresentabili; test Ferri Matteo 18/03/2026 e Moretti Elena 10/06/2026 del corpus completo. Rinnovato `storici-confronti.jpg`: pannello principale prima degli approfondimenti di ripetibilità. Catture del viewport circa 1280 × 900, sola conversione PNG/JPEG, nessun ritocco.

Nuovi `test-riepilogo-unificato.png` e `test-riepilogo-stretto.png`: test manuale sintetico Ada Esempio, cinque KPI in un solo blocco, MAP senza duplicato; nessun grafico ricostruito dai riepiloghi. Seconda cattura con viewport 412 × 915 per il layout stretto. È una prova web responsive, non del bridge Android né di un APK/telefono. Queste catture sostituiscono la provenienza precedente solo per i file nominati; gli altri mantengono le proprie date.


### Soglia relativa ripristinata — 27 ottobre 2026

Rinnovati test-riepilogo-unificato.png e test-riepilogo-stretto.png: stesso archivio QA sintetico e build web corrente con sei KPI, inclusa Soglia relativa 2,66 W/kg accanto a 141 W. Valore salvato nel solo record QA con peso test 53 kg; nessun dato reale. Sostituiscono le due catture del 26 ottobre per questi file. Nessuna prova nativa Android implicita.
