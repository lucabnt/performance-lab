# Metodi dell’incrementale — specifica 1.0

**Aggiornamento 0.5:** questa specifica 1.0 è ora attuata per il nucleo costante. I metodi specialistici sono stati scelti e implementati come descritto in [IMPLEMENTAZIONE_INCREMENTALE_05.md](archivio/IMPLEMENTAZIONE_INCREMENTALE_05.md), su autorizzazione dell’utente a usare fonti scientifiche. Le indicazioni sottostanti «da implementare» descrivono lo stato alla redazione della 1.0; per capacità e limiti attuali prevale il documento 0.5. Motore nuovo `0.5.0`, risultati precedenti conservati.


17 ottobre 2026. Step 2 del piano di lavoro di Fuorigiri Performance Lab. Questo documento definisce il contratto da implementare nelle successive iterazioni INC-01–10; **non dichiara già sviluppati i nuovi algoritmi**. Il motore corrente resta `0.2.0`, con le differenze elencate sotto. Nessuna analisi archiviata viene ricalcolata o sovrascritta da questo aggiornamento.

## Decisioni e significato dei risultati

Confermato dall’utente: ultimo step costante completo come risultato primario, interpolazione distinta; completezza basata su durata e copertura potenza ≥95%, **aderenza al target separata**. Nessun coefficiente universale per Watt Soglia o FTHR: valori dichiarati/misurati, oppure stima esplicita con coefficiente documentato e versionato per protocollo. Confermati i confini delle zone e un numero configurabile di zone, anche superiore a cinque.

Il campo storico `map_w` rimane compatibile, ma nella presentazione va letto come **Potenza dell’ultimo step completo (MAP operativa)**: è il carico programmato, non la maggiore potenza istantanea misurata e non una misura diretta della potenza a VO₂max. Riportare sempre aderenza, protocollo e metodo accanto al risultato. Un tracciato a 100 W durante uno step programmato a 200 W può essere temporalmente completo: il valore nominale va accompagnato dall’avviso di aderenza, mai presentato come 200 W effettivamente sostenuti.

Durata degli step e analisi possono influenzare soglie e risultati; non trasferire automaticamente conclusioni da ciclisti adulti allenati a categorie giovanili. Riferimenti primari: [Jamnick et al., 2018](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0199794), [Pallarés et al., 2016](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0163389).

## 1. Protocollo, metodo e provenienza

Distinguere tre oggetti immutabili: **protocollo** (carichi, durate e modalità di esecuzione), **preset di analisi** (finestre, coperture e algoritmi), **revisione dell’analisi** (input effettivi, risultati e autore). Modificare un preset crea una versione nuova; non cambia i test già refertati. Un protocollo di solo catalogo può taggare un risultato manuale, ma non abilita il calcolo automatico degli step.

Ogni revisione deve conservare: ID/versione/hash di protocollo e preset, versione motore/decoder, hash del file originale e dei campioni normalizzati, sessione scelta, allineamento, intervalli esclusi e motivi, fine sforzo, dati manuali con autore/data/fonte, massa e misura di origine, dispositivi e condizioni, avvisi e stato di revisione. Il riferimento a un preset da solo non basta: conservare anche i parametri risolti e la specifica matematica/versione.

Ogni metrica restituisce `value`, `unit`, `method_id`, `source`, `coverage` quando applicabile, `status` e `reason`. Stati: `computed`, `declared`, `estimated`, `unavailable`, `needs_review`; i motivi sono codici traducibili. Mancante è `null`, non zero. Esportazioni e confronti devono distinguere metodi e fonti; i vecchi test senza informazioni rimangono `legacy_unknown`, senza attribuire retroattivamente il preset nuovo.

Identità proposta dei metodi:

| ID / versione | Risultato | Stato |
|---|---|---|
| `incremental.constant.last-complete/1` | Ultimo step completo | Convenzione confermata, contratto formalizzato qui |
| `incremental.constant.partial-linear/1` | Interpolazione dello step parziale | Indicatore secondario separato |
| `signal.time-weighted-hold/1` | Medie, integrali e copertura | Convenzione numerica esplicita |
| `hr.end-stage.mean/1` | Media FC finale di step | Preset di continuità con il motore attuale |
| `hr.recovery.delta/1` | FC e decremento nel recupero | Preset di continuità, contesto obbligatorio |
| `threshold.declared/1`, `threshold.map-coefficient/1` | Soglia dichiarata o stimata | Nessun coefficiente precompilato |
| `lactate.fixed-crossing/1` | Potenza a concentrazione esplicita | Primo algoritmo lattato proposto |
| `repeatability.paired/1` | Errore tipico e MDC descrittivi | Contratto proposto, dati adeguati necessari |

Le versioni qui non corrispondono a funzioni già disponibili nell’API. INC-07 introdurrà il registro eseguibile e l’associazione persistente; prima serviranno migrazione e gestione dei valori legacy. Un [esempio JSON del contratto](../examples/methods/incremental-constant-v1.example.json) rende espliciti i parametri; è marcato `specification_only` e non viene caricato dal motore attuale.

## 2. Asse temporale e qualità dei campioni

Tempo `t` in secondi trascorsi dal primo campione della sessione selezionata; conservare anche timestamp assoluto e fuso originale se disponibile. Nessuna compressione automatica delle pause. `offset_s` allinea il tempo zero del protocollo; `effort_end_s` è la fine dello sforzo confermata dall’operatore, distinta da fine FIT e recupero. Intervalli semichiusi `[a,b)`, con il campione a `b` utile come estremo temporale ma non come valore dello step precedente.

La normalizzazione deve separare dati originali, correzioni approvate e dati analizzati. Duplicati discordanti, salti dell’orologio, multisessione e unità ambigue richiedono scelta assistita; non mediare né unire sessioni automaticamente. Registrare timer stop/start e lap. CRC non valido o file troncato: errore esplicito, mai importazione apparentemente completa. Il decoder corrente ordina i record, rifiuta duplicati e più sessioni; il supporto guidato è ancora INC-01.

Per ogni coppia di campioni consecutivi `(tᵢ,xᵢ),(tᵢ₊₁,xᵢ₊₁)`, il valore `xᵢ` vale nell’intervallo `[tᵢ,tᵢ₊₁)` soltanto se finito, nel dominio del canale, non in pausa/esclusione e `0 < Δt ≤ 5 s`. Nessuna estensione oltre l’ultimo campione; nessun riempimento di dropout, interpolazione o ricampionamento implicito. Potenza e cadenza zero sono valori misurati validi; valori negativi e FC ≤0 non sono utilizzabili. I limiti superiori plausibili saranno avvisi configurabili, non clipping nascosto. Le esclusioni con motivo creano una revisione, non cancellano gli originali.

Per una finestra `W=[a,b)`: `dᵢ = durata(intersezione dell’intervallo valido con W)`, `T_valid=Σdᵢ`, `coverage=T_valid/(b−a)`, `integral=Σxᵢdᵢ`, `mean=integral/T_valid` se `T_valid>0`. La copertura usa come denominatore **tutta la finestra richiesta**, comprese pause, esclusioni e parti senza registrazione. Sottrarre le unioni degli intervalli esclusi, senza contarle due volte. Conservare copertura e valori non arrotondati per decisioni e derivazioni; arrotondare solo nella presentazione.

Una pausa timer che cade tra due record deve dividere l’intervallo al timestamp dell’evento. Il codice corrente propaga lo stato al record successivo: questa precisione è un lavoro INC-01/03 ancora da fare. Non interrompere automaticamente la ricostruzione temporale per far combaciare il piano: eventuali ripartenze richiedono marker espliciti e revisione dell’allineamento.

## 3. Step completi e aderenza

Per lo step `j`, `aⱼ=offset+start_s`, `bⱼ=offset+end_s`, `Dⱼ=bⱼ−aⱼ`; durata tentata `max(0,min(effort_end,bⱼ)−aⱼ)`. Uno step è **completo secondo il metodo** se raggiunge `bⱼ` e la potenza valida copre almeno `0.95 Dⱼ`. Non applicare prima arrotondamenti alla copertura. Riscaldamento e recupero sono fasi distinte, non incrementi; una loro anomalia è visibile ma non sostituisce questa regola.

Considerare la sequenza contigua degli step incrementali completi a partire dal primo incremento: un buco in uno step richiesto impedisce di usare uno step successivo come ultimo completo. Il metodo per step costanti richiede carichi costanti, positivi e crescenti nella sequenza incrementale; rampe, discontinuità o riduzioni del carico vanno al rispettivo metodo, non vengono adattate silenziosamente. Se nessuno step è completo, risultato non disponibile.

`P_primary=P_target` dell’ultimo step della sequenza. Restituire anche numero dello step, durata, copertura, potenza misurata e stato di aderenza. Cadenza, RPE e FC non invalidano automaticamente questo risultato. Durata raggiunta non prova esaurimento: conservare motivo di arresto e valutazione dell’operatore.

**Aderenza descrittiva senza soglia nascosta:** per ogni step mostrare potenza media misurata, differenza in W e %, errore assoluto medio temporale `Σ|Pᵢ−target|dᵢ/T_valid` e RMSE `sqrt(Σ(Pᵢ−target)²dᵢ/T_valid)`, con la stessa copertura. Se non è configurata una tolleranza, stato `non_valutata`, senza bollino verde/rosso. Una tolleranza opzionale deve dichiarare se assoluta, relativa o combinata, limiti inclusivi, eventuale tempo di assestamento, denominatore e quota richiesta; solo allora calcolare la quota entro banda. Nessuna banda universale viene scelta qui. Se in futuro si richiederà un risultato subordinato all’aderenza, sarà un **altro metodo versionato**, non una reinterpretazione della convenzione confermata.

Il suggerimento nella guida allegata «cadenza <60 rpm per oltre 10 s» è contesto operativo da confermare per protocollo, non una nuova istruzione vincolante. Prima di automatizzarlo definire continuità, campioni mancanti e superamento strettamente maggiore di 10 s. Analogamente «test <12 minuti» non diventa uno scarto automatico: manca la definizione di fase inclusa e non è applicabile indistintamente a ogni incrementale. Annotare la scala RPE realmente usata: CR10 e Borg 6–20 non sono intercambiabili.

## 4. Interpolazione e normalizzazione per massa

Solo se esiste un primario valido e lo step immediatamente seguente è costante, crescente, tentato e non completato per termine anticipato, con copertura della parte tentata ≥95%:

`P_interpolated=P_primary+(P_next−P_primary) × T_attempted/D_next`, con `0<T_attempted<D_next`.

Lo step interamente trascorso ma incompleto per dropout non si interpola. Non saltare uno step, non estrapolare oltre il piano e non interpolare se il primo incremento è parziale. Non sostituire questa stima al primario nelle zone o nelle medie storiche senza scelta esplicita del campo. Esempio: 200 W completi, poi 100/240 s di uno step a 230 W → primario **200 W**, secondario **212,5 W**.

`W/kg=P/massa_kg` usando la massa associata al test, positiva e con data/fonte. Il disegno prevede proposta dell’ultima misura antecedente, con conferma dell’operatore e visibilità dell’anzianità, senza pescare una misura futura. Una massa stimata resta etichettata ed è esclusa dagli aggregati standard; senza massa il relativo è indisponibile. Nessun arrotondamento intermedio; UI 2 decimali W/kg, export con precisione sufficiente e unità. Gli attuali 2/3 decimali divergenti saranno uniformati nel nuovo preset.

## 5. FC, riposo e recupero

FC di fine step: media temporale sugli ultimi `min(30,D_effettiva)` secondi dello step tentato; distinguere step parziale/completo. Preset nuovo: pubblicare il valore come utilizzabile con copertura FC ≥80%, altrimenti mantenere diagnostica e valore ufficiale nullo. Parametri finestra/copertura versionati, indipendenti dalla copertura potenza. FC massima del test: massimo campione FC valido in `[offset,effort_end)` con timestamp, sorgente e avviso sugli artefatti; nessuna formula anagrafica e nessuna chiamata a «FC massima fisiologica».

FC a riposo: osservazione manuale o finestra sensore esplicitamente selezionata **prima dello sforzo**, con tempo trascorso dall’inizio del riposo, posizione e copertura quando calcolata. Non usare il minimo del FIT come equivalente del riposo. `rest_after_s` è tempo dall’inizio del riposo, non offset del protocollo; visualizzare minuti e secondi.

Preset di continuità per recupero: `HR_ref=media FC negli ultimi min(5,durata sforzo) s`; `HR_τ=media in [end+τ−2,end+τ+3)` per `τ=60,90,120 s`. Ogni finestra richiede copertura ≥80%. `HRR_τ=HR_ref−HR_τ` in bpm, anche negativa; non troncare a zero. Se manca il riferimento, FC al recupero può esserci mentre HRR resta nulla. Il centro operativo della finestra asimmetrica è dichiarato, non spacciato per un singolo campione al secondo esatto.

Recupero attivo/passivo, postura, carico e interruzioni vanno registrati e separati nei confronti. La guida propone 90 s seduto: non basta per produrre automaticamente un HRR120 valido. Nessun cut-off diagnostico o confronto con norme cliniche implicito. Una misura manuale allo stesso tempo ha precedenza nel referto se scelta dall’operatore, ma conservare e mostrare il valore sensore; senza tracciato non inventare `HR_ref` né un decremento a partire dalla sola FC massima.

## 6. Soglia, FTP, FTHR e lattato

Gerarchia: un valore esplicitamente inserito prevale sulla stima; fonte dichiarata o referto misurato devono essere distinguibili. In assenza di un valore, consentire `threshold_w=k × P_primary` solo con coefficiente esplicito, origine, data, atleta e versione del protocollo/preset. Nessun valore iniziale di `k`. Una calibrazione individuale `k=P_soglia_riferimento/P_primary_riferimento` deve collegare entrambi i risultati e il metodo di soglia; non trasferirla automaticamente tra rullo/Cyclus, protocolli o dispositivi differenti. Un’eventuale scadenza richiede una politica esplicita; nessuna durata universale inventata.

FTP, Watt Soglia, LT, VT1, VT2 e FTHR sono campi distinti: non riempire l’uno con l’altro. FTHR non è derivata automaticamente da MAP, età o FC massima. Un valore ottenuto da una percentuale rimane una stima, non una misura di lattato o scambio gassoso.

INC-05 implementerà curva lattato-potenza e collegamento del prelievo a step, timestamp, ritardo di prelievo, carico nominale/misurato scelto, unità mmol/L, dispositivo e qualità. Nessuna associazione basata solo sull’ordine di inserimento. Primo metodo proposto `fixed-crossing/1`: concentrazione `L*` esplicita (4 mmol/L è una scelta possibile, non la soglia universale), primo attraversamento crescente tra due punti validi adiacenti `Lᵢ < L* ≤ Lᵢ₊₁`; `P*=Pᵢ+(Pᵢ₊₁−Pᵢ)(L*−Lᵢ)/(Lᵢ₊₁−Lᵢ)`. Un punto esattamente sul riferimento restituisce quel carico; plateau di più punti esatti, molteplici attraversamenti o curva non monotona richiedono revisione e presentazione delle alternative. Meno di due punti o nessun attraversamento: indisponibile, nessuna estrapolazione.

Dmax e Dmax modificato restano parte della copertura richiesta, ma il loro **metodo esatto è da selezionare prima dell’implementazione**: regressione, grado, ancoraggi, dominio, minimi punti, gestione outlier e scelta del massimo devono identificare un algoritmo riproducibile con dataset di riferimento. Non chiamare genericamente Dmax una curva polinomiale scelta dal programmatore. Il tecnico deve confermare quali varianti usa; il valore dichiarato dal laboratorio resta archiviabile nell’attesa.

## 7. Zone, lavoro e medie

Classificazione con rapporto non arrotondato `100 × valore/riferimento`. FC su FTHR: `<81`, `81–<90`, `90–<100`, `100–105`, `>105%`. Potenza su Watt Soglia: `≤55`, `>55–75`, `>75–90`, `>90–105`, `>105%`. Ogni valore valido appartiene a una sola zona; mancante e negativo non diventano Z1. Schemi personalizzati da 2 a 100 zone nel codice attuale, versionati, con perno, inclusività e unità espliciti.

Durata in zona: somma degli intervalli validi classificati col valore iniziale; tempo non classificato distinto, denominatore e fase sempre visibili. Limiti assoluti presentati con inclusività e precisione sufficienti: arrotondare i bpm per l’UI non deve creare buchi nella classificazione. Senza campioni mostrare limiti ma **tempo in zona non disponibile**, non 0 s; senza perno nessun limite assoluto inventato.

Potenza media: integrale sui secondi validi, con copertura. Lavoro osservato `ΣPᵢdᵢ/1000` kJ: non stimare la parte persa e non chiamarlo lavoro totale se la copertura è incompleta. `duration_elapsed`, `duration_incremental`, `valid_power_s` separati. Nel motore corrente potenza media, lavoro, FC massima e zone includono il riscaldamento da offset a fine sforzo: il preset nuovo deve salvare esplicitamente la fase scelta; default di continuità `whole_effort`, con alternativa `incremental_only` distinta nei confronti.

## 8. Rampe, gas e ripetibilità

**Rampe/discontinui (INC-04):** mantenere archiviazione e curva; metodo last-complete non applicabile. Specificare pendenza, interruzioni e ritardo ergometro. Primo indicatore proposto: carico nominale al marker finale e potenza media misurata negli ultimi 30 s, etichettati separatamente e con copertura, senza convertirli nella MAP per step. Durata/finestra e interpretazione fisiologica da confermare nel protocollo dedicato. Nessuna equivalenza automatica con gli ERG ALL/ESO.

**Gas (INC-08):** dati VO₂/VCO₂/VE con unità, base temporale respiro-per-respiro o media dichiarata, calibrazione e correzione del ritardo sensore. Proposta VO₂peak: massimo della media temporale mobile su 30 s interamente contenuti nella fase incrementale, copertura ≥95%, espresso in L/min e mL/kg/min se massa valida; il pretrattamento dei respiri e i limiti del canale richiedono validazione. Non ricostruire valori respiro-per-respiro da medie già aggregate. Per VO₂max richiedere evidenza e criteri di conferma documentati dal laboratorio; non rinominare automaticamente VO₂peak. VT1/VT2: marker del valutatore con evidenze e metodo; successivi algoritmi V-slope/equivalenti richiedono definizione e confronto di riferimento. Il marker manuale è una funzione utile ma non chiude il requisito di analisi. [ATS/ACCP, CPET](https://www.thoracic.org/statements/resources/pfet/cardioexercise.pdf).

**Ripetibilità (INC-09):** soltanto coppie di prove giudicate ripetute in condizioni stabili e con stesso metodo/protocollo/dispositivo, non qualsiasi cambiamento stagionale. Per differenze `dᵢ=x₂ᵢ−x₁ᵢ`: bias `mean(d)`, SD campionaria delle differenze (`n−1`), errore tipico `TE=SD(d)/sqrt(2)`, `MDC95=1.96 × sqrt(2) × TE`. Se `n<2`, nessuna stima; con pochi soggetti segnalare instabilità e mostrare sempre n. Non usare MDC come diagnosi o certezza di adattamento individuale. Coppie ripetute dello stesso atleta non sono indipendenti: separare stime intra-atleta o adottare un modello esplicito, senza aumentarne artificialmente n. Per un indicatore percentuale/eteroschedasticità servirà specificare trasformazione e modello; niente CV derivato implicitamente dalle medie di gruppo.

Per l’errore tipico, riferimento metodologico dell’autore: [Hopkins, 2000](https://sportsci.org/resource/stats/Hopkins_SportsMed_rely_00.pdf). Le formule sono un modello descrittivo con ipotesi di errori indipendenti, stabili e approssimativamente normali; non sono una soglia universale di miglioramento. Distinguere sempre variazione rilevabile e variazione sportivamente importante.

## 9. Protocolli di esempio e ambiguità risolte

| File | Riscaldamento | Primo incremento | Incrementi successivi |
|---|---|---|---|
| `AER-RULLO-ALL.erg` | 600 s a 100 W | 130 W per 240 s | +30 W ogni 240 s |
| `AER-RULLO-ESO.erg` | 600 s a 60 W | 80 W per 240 s | +20 W ogni 240 s |

I file sono l’evidenza del piano; la formulazione abbreviata della guida «poi +20/+30» non aggiunge un ulteriore step a 60/100 W dopo i 10 minuti. La calibrazione inserita tra riscaldamento e incrementi non è contenuta negli ERG: se avviene durante la registrazione serve allineamento per fase/marker, senza fingere un protocollo continuo perfettamente rispettato.

## 10. Casi di accettazione e differenze da implementare

| Caso | Risultato richiesto |
|---|---|
| Step 240 s, 228 s validi | Completo se raggiunta fine: copertura esatta 95% |
| Step 240 s, 227,99 s validi | Incompleto; arrotondare a 95% nell’UI non lo rende valido |
| 200 W completi + 100/240 s a 230 W | Primario 200 W; interpolato 212,5 W |
| Step a 200 W registrato interamente a 100 W | Completezza sì, scostamento −100 W/−50%; aderenza visibile separata |
| Primo incremento parziale o buco in un incremento precedente | Primario indisponibile; nessun salto al successivo |
| Campioni a 0 e 6 s | Nessuna integrazione dei 6 s mancanti |
| Ultimo campione esattamente alla fine dello step | Estremo della finestra; non contribuisce col suo valore allo step prima |
| Finestra recupero 5 s, validi 4 s / 3,99 s | Valore disponibile / indisponibile |
| Potenza riferimento 200 W, campione 110 W | 55% esatto: Z1 |
| FC riferimento 200 bpm, campione 162 bpm | 81% esatto: Z2 |
| Test manuale con sola FC120 e nessuna FC finale | FC120 dichiarata; HRR120 indisponibile |
| Protocollo catalogo o rampa | Risultati manuali/descrittivi, nessuna MAP last-complete automatica |

Scostamenti rilevati nel codice attuale da correggere con test e nuova versione del motore: copertura arrotondata prima delle soglie; medie già arrotondate usate in alcune derivazioni; FC finale pubblicata senza gate di copertura; FC massima include il campione al termine; validazione del dominio dei canali incompleta; gestione timer solo sui record; aderenza e provenienza per metrica non ancora presenti; controllo carichi crescenti incompleto; finestre fisse e non associate a un preset persistente. I risultati storici vanno conservati e confrontati con una nuova revisione, non modificati in-place.

## 11. Decisioni residue e ordine di attuazione

Lo step 2 chiude la definizione della convenzione degli step costanti, dell’interpolazione e della separazione delle fonti. Non chiude INC-02/07 dal punto di vista del software. Le soglie 95%/80% e le finestre attuali sono convenzioni operative esplicite, non criteri fisiologici validati universalmente.

Ordine tecnico successivo: registro preset/versioni e migrazione legacy → finestre numeriche esatte e metadati per metrica → GUI allineamento/qualità/aderenza → report e confrontabilità → corpus reali e metodi specialistici. Prima di ciascun metodo specialistico servono: variante lattato del laboratorio, file gas e criteri VO₂max/VT, protocolli rampa/discontinui e dati di ripetibilità; si può procedere sul nucleo costante senza attendere questi materiali. Le proposte specialistiche qui sono verificabili e delimitate, ma non sostituiscono la scelta con il tecnico. La guida allegata rimane fonte di contesto, non approvazione automatica delle sue prescrizioni.
