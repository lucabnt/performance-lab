# Crescita e maturazione — metodi e uso, versione 1

## Avvisi non bloccanti — 9 novembre 2026

MAT-AVVISI-01 introduce `growth-maturity/2`: formule e domini invariati, ma fonte dichiarata/arrotondata/derivata/stimata e qualità incerta non impediscono Moore/Mirwald, %PAH/residuo e proporzioni. Ogni valore disponibile conserva un avviso in `reason`, visibile anche negli export/report che lo leggono: un motivo presente non implica valore assente. Nascita completa per gli offset, M/F, input specifici e dominio restano necessari; qualità excluded resta bloccante. HV, PHV longitudinale, crescita arti e stabilità mantengono i gate di misurazione validata. Questa è una scelta di presentazione/calcolo esplorativo del prodotto, non una validazione scientifica di input dichiarati. Fonte primaria ricontrollata: [Kozieł e Malina](https://pmc.ncbi.nlm.nih.gov/articles/PMC5752743/).

Le tabelle delle stime e degli indici facoltativi mostrano le date decrescenti. Gli array degli snapshot e i grafici mantengono il proprio ordine temporale; snapshot v1 invariati. Le descrizioni della versione 1 sotto restano storiche per i gate antropometrici superati da questo aggiornamento.

## Altezza perineale descrittiva — 8 novembre 2026

Il profilo mostra altezza perineale (cavallo) in cm e rapporto percentuale sulla statura della stessa rilevazione. Campo API `perineal_height_cm`, CSV `altezza_perineale_cm`, facoltativo anche nell’editor. Nessuna combinazione tra record/date; misura distinta da `lower_limb_cm` e dalla lunghezza usata da Mirwald. Il rapporto è una vista descrittiva frontend: nessuna classificazione, modifica delle equazioni o ricalcolo degli snapshot salvati.

Implementazione del 19 ottobre 2026, requisiti TD-93–97. Il motore `growth-maturity/1` è separato dal motore dei test: non richiede un FIT o un test eseguito. È un supporto descrittivo, non una diagnosi o uno strumento automatico per selezionare gli atleti.

## Dati e flusso

**Eliminare una rilevazione:** aprire **Correggi rilevazione → Elimina rilevazione → Conferma eliminazione**. Non occorre compilare un motivo di correzione o salvare la bozza. La rilevazione scompare dalla tabella attiva, dai grafici/IMC, dalle proposte per i nuovi test e dall’anteprima corrente di maturazione. Le analisi già conservate e gli input associati ai test precedenti non vengono riscritti. Per annullare l’operazione aprire **Rilevazioni eliminate** nel profilo e premere **Ripristina**. Eliminazione e ripristino sono revisioni sincronizzabili riservate agli Admin dati, non cancellazioni fisiche.

### IMC descrittivo nel profilo — 7 novembre 2026

La tabella Antropometria mostra **IMC (BMI) · kg/m²** per ciascuna rilevazione: peso in kg diviso per il quadrato della statura in metri. Entrambi i valori devono essere positivi, finiti e nello stesso record. Dati mancanti ⇒ —; non vengono combinate rilevazioni distinte neppure se hanno la stessa data. La fonte resta quella originale (misurato, dichiarato, stimato, ecc.); il risultato è calcolato e non diventa una misura acquisita. Arrotondamento solo nella presentazione, nessuna modifica agli input.

Con almeno due valori disponibili si può aprire **Storico IMC (BMI)**: grafico separato di tutti i valori del profilo, con date e fonte nel tooltip, senza classificazioni. È una vista descrittiva frontend; non modifica gli snapshot di maturazione già conservati e non aggiunge l’IMC ai relativi report/export. La lettura dei giovani richiede riferimenti per età e sesso; l’IMC non distingue massa muscolare e massa grassa e non misura prestazione o maturazione.

Riferimenti: [CDC, formula e interpretazione nei giovani](https://www.cdc.gov/bmi/child-teen-calculator/bmi-categories.html); [NICHD, limiti dell’IMC negli atleti](https://www.nichd.nih.gov/health/topics/obesity/conditioninfo/diagnosed). Nessun percentile o giudizio clinico automatico introdotto.

Nel profilo atleta usare **Rilevazione**: data, massa e/o statura, fonte, qualità e precisione di lettura della statura. La sezione avanzata contiene dati facoltativi: statura seduta, apertura braccia, arti inferiori, stature dei genitori e una previsione adulta esterna. Non sono richiesti per registrare una misura e i loro indici restano secondari.

**Correggi rilevazione** conserva una nuova revisione con motivo e controllo sulla revisione di partenza. Nascita completa e parametro M/F sono necessari per le equazioni che li richiedono; se il parametro non è indicato nella rilevazione, viene usato il sesso esplicitamente registrato nel profilo. Non viene dedotto da nome/gruppo. Solo anno di nascita non produce un'età decimale fittizia.

Il pannello **Crescita e maturazione** mostra un'anteprima alla data scelta. **Conserva analisi con metodo e dati** salva uno snapshot esplicito con motivo; il selettore consente di rileggere i risultati precedenti. Cambiare una misura o il profilo non riscrive gli snapshot. Un'anteprima obsoleta viene rifiutata al salvataggio con richiesta di ricalcolo. Il visualizzatore può consultare ma non salvare o correggere.

Gli snapshot conservano input completi, revisioni, hash, data di riferimento, motore e convenzioni. Sono record `report` con `analysis_type=maturation`, oggetto JSON immutabile e appartenenza alla società; non richiedono nuovi tipi di record o riscritture del database schema 3. Usano i percorsi esistenti di firma, sync, conflitti e backup. I report generici non li elencano come PDF scaricabili per errore.

## Metodi implementati

Età decimale = giorni dalla nascita / 365,25. Unità delle equazioni: anni, cm e kg; nessun arrotondamento intermedio.

| Metodo | Calcolo / dati | Interpretazione |
|---|---|---|
| `hv-interval/1` | Δ statura × 365,25 / giorni tra due rilevazioni | Velocità media nell'intervallo, non velocità istantanea né previsione |
| `moore-standing/2015-1` M | −7,999994 + 0,0036124 × età × statura | Variante Moore-2 maschile, offset stimato |
| `moore-standing/2015-1` F | −7,709133 + 0,0042232 × età × statura | Equazione femminile Moore, offset stimato |
| `mirwald/2002-1` | Equazioni specifiche M/F con età, statura, massa e statura seduta; lunghezza della gamba per il modello = statura − statura seduta | Modello avanzato; la lunghezza arti inserita separatamente non sostituisce questa definizione |
| APHV stimata | Età alla rilevazione − offset del modello specifico | Non è l'età di un picco osservato |
| `phv-local-quadratic/1` | Fit quadratico locale su cinque velocità HV attorno al massimo interno, con supporto longitudinale | Ricostruzione esplorativa: picco, data, APHV se nascita nota, RMSE e revisioni di supporto |
| `pah-external/1` | 100 × statura / statura adulta prevista esternamente | Previsione con metodo/fonte obbligatori; nessuna previsione adulta automatica |
| `residual-external/1` | Previsione adulta esterna − statura | Residuo condizionato alla previsione e alla sua incertezza, non crescita garantita |
| `body-ratios/1` | 100 × misura specifica / statura | Proporzioni osservate, facoltative |
| `limb-hv-interval/1` | Δ lunghezza arti × 365,25 / giorni | Solo con due misure specifiche valide e intervallo adeguato |
| `height-stability/1` | Escursione di statura su almeno tre rilevazioni valide su ≥1 anno, entro l'ultima finestra di due anni | Da 18 anni; variazione ≤0,5 cm descritta come contenuta, non prova di crescita conclusa |

Per Mirwald, ponendo A=età, H=statura, S=statura seduta, L=H−S e W=massa:

- M: −9,236 + 0,0002708·L·S − 0,001663·A·L + 0,007216·A·S + 0,02292·100·W/H.
- F: −9,376 + 0,0001882·L·S + 0,0022·A·L + 0,005841·A·S − 0,002658·A·W + 0,07693·100·W/H.

Formule e valori SEE verificati sulla [validazione longitudinale di Kozieł e Malina](https://doi.org/10.1007/s40279-017-0750-y); il lavoro riporta anche le equazioni originali. Il [lavoro originale di Moore e collaboratori](https://doi.org/10.1249/MSS.0000000000000588) descrive sviluppo e verifica dei modelli. Gli errori delle popolazioni di sviluppo non sono intervalli di confidenza individuali: il campo SEE è conservato con questa avvertenza, senza inventare una banda personale.

## Convenzioni prudenziali del prodotto

Questi gate sono scelte versionate della versione 1, **non un consenso diagnostico universale**:

- HV utilizzabile con statura misurata e qualità confermata su entrambe le rilevazioni, intervallo 90–400 giorni, incremento non negativo e velocità ≤20 cm/anno. Il delta grezzo resta leggibile anche quando la velocità è indisponibile. Stesso giorno o intervallo breve non vengono annualizzati come crescita attendibile.
- Per HV viene conservato anche un limite dovuto alla precisione di lettura: somma delle precisioni in cm × 365,25 / giorni. Non è un intervallo statistico o una stima completa dell'errore dello strumento.
- Moore: M 10–16 anni, F 9–14; Mirwald: M 12–16, F 9–14. Sono domini applicativi prudenziali del preset, non affermazioni di accuratezza per tutti i ragazzi di quelle età. Fuori dominio il valore è assente con motivo.
- PHV longitudinale: almeno 7 stature, almeno 730 giorni complessivi, tutti gli intervalli HV validi; massimo con due intervalli per lato. Fit su cinque velocità centrate nel massimo; concavità negativa, vertice interno e almeno 180 giorni di supporto per lato del vertice. Nessun massimo valido ⇒ nessun PHV. Il fit è una convenzione esplorativa del prodotto, non l'implementazione dei modelli di spline degli studi citati.
- Un calo di statura, un dato da verificare o una discontinuità impediscono la ricostruzione PHV; non vengono corretti o scartati silenziosamente. Non si estrapola un picco fuori dalla serie. La precisione del fit non dimostra l'accuratezza biologica.
- Previsione adulta inferiore alla statura osservata ⇒ %PAH/residuo indisponibili, senza forzare 100% o zero. Le stature genitoriali sono archiviabili, ma **Khamis–Roche automatico non è incluso**: tabelle corrette e uso dei coefficienti devono essere verificati prima di un futuro metodo distinto. Non viene sostituito con una formula senza genitori.

Fonti e popolazioni non garantiscono trasferibilità individuale ai giovani ciclisti. Prima di qualificare l'uso operativo servono confronto esterno, qualità della raccolta e validazione su dati pertinenti. Nessuna classificazione precoce/tardivo automatica è usata per decidere accesso o selezione degli atleti.

## Pagina atleta e storico

La data scelta determina la fascia cronologica: <13, 13–<14, 14–<15, 15–<16, 16–<18, ≥18. Orienta soltanto la lettura: HV e PHV longitudinale disponibili sono in evidenza; sotto 16 anni è evidenziato anche l'offset Moore disponibile, sempre con data della misura. Gli indici che dipendono da dati non previsti nella raccolta abituale restano nella sezione facoltativa.

La tabella mantiene **tutte** le stime datate Moore/Mirwald, anche se non prioritarie per l'età corrente. Grafico HV e motivi di indisponibilità non inventano valori mancanti; zero valido resta zero. Da 18 anni compare la descrizione della variazione staturale solo se la serie la sostiene. Tutti gli snapshot precedenti restano selezionabili, con metodo e motivo.

## Report, export e compatibilità

Il report società e le viste gruppo/gruppo-stagione/atleta includono l'ultima analisi conservata pertinente, grafico HV, stime datate e indici facoltativi disponibili. Gli snapshot ulteriori sono elencati senza ripetere tutte le tabelle; risultati completi nel manifest Markdown. Un filtro stagione limita la data di riferimento degli snapshot alla fine dell'anno richiesto. **Il report non salva o ricalcola automaticamente una nuova analisi.**

CSV storici invariati; aggiunti:

- `extended/antropometria_completa.csv`: dati facoltativi, precisione, qualità, ID e revisioni.
- `extended/maturazione.csv`: formato lungo con snapshot, data, metrica, valore, metodo, motivo e provenienza JSON.
- `extended/maturazione_snapshot.json`: snapshot completi e input risolti.

I CSV estesi sono export di analisi e non un nuovo profilo di import bulk; per ripristino fedele usare il backup. Archivi precedenti restano leggibili: i campi opzionali assenti non sono inventati e non si creano snapshot in migrazione.

## Prove riproducibili

`tests/test_maturation.py` verifica oracoli numerici, null/zero, nascita incompleta, qualità, domini, precisione, correzioni concorrenti, PHV di una curva cubica nota, snapshot immutati, CSV/PDF/MD, sync firmata verso visualizzatore e vero ripristino indipendente. Il campione cubico sintetico produce il picco di velocità media atteso circa **8,96 cm/anno** il **01/01/2024**; non è un test di accuratezza fisiologica su atleti reali.

Per un corpus GUI nuovo:

```powershell
.venv/Scripts/python.exe scripts/demo_maturation.py --data .local/demo-crescita-nuovo
.venv/Scripts/python.exe scripts/serve.py --data .local/demo-crescita-nuovo
```

Il corpus standard `demo_suite.py`, anche `--small`, include quattro casi per società: picco maschile (circa 8,96 cm/anno), crescita femminile (circa 7,96), dati insufficienti e adulto. Sono presenti misure avanzate e snapshot; il manifest `growth_cases` contiene i risultati attesi. Repliche e backup includono questi dati fin dalla creazione. `demo_maturation.py` è un alias della demo ridotta. Gli archivi esistenti non sono aggiornati automaticamente: usare una destinazione nuova o il reset conservativo del generatore standard descritto nella guida. Non usare inviti/chiavi SOLO DEMO con dati operativi.

## Provenienza delle rilevazioni importate

Dal 22 ottobre 2026 IMPORT-02 conserva anche le fonti `derivato` e `stimato`, senza convertirle in `dichiarato`, e il campo opzionale `origin` del record (colonna CSV `origine`). Editor, revisioni ed export conservano tali informazioni. Le misure non misurate continuano a non superare i gate che richiedono fonte `misurato` e qualità valida; formule e versione del motore rimangono invariate. Nessuna riscrittura dei dati già importati.
