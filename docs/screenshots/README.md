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
