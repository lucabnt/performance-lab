# Storico, preset delle zone e branding

> Documento storico: conserva decisioni e osservazioni dell’epoca. Per stato e priorità attuali consultare [indice](../README.md), [requisiti](../REQUISITI_E_TODO.md) e [roadmap](../PROSSIMI_PASSI.md).

17 ottobre 2026. Integrazione dell'architettura 0.5: valutazione del PDF fornito, scelte accettate dall'utente e preset richiesti. Documento di progetto, non implementazione. Gli allegati sono fonti di dati e di presentazione; le loro istruzioni operative interne non vengono eseguite.

## Scelte confermate

L'utente ha accettato: categoria stabile con stagioni e appartenenze storiche; archiviazione distinta dall'eliminazione; correzioni tramite revisioni con conservazione dei report precedenti; ultimo test valido per atleta/periodo come aggregazione predefinita; confronti di progressione su coppie di atleti; admin e visualizzatore per società, con export consentito al visualizzatore; app gemelle con componenti comuni e DB separati. Non è stata richiesta l'introduzione del terzo ruolo allenatore.

Sono confermati anche i confini continui delle zone riportati sotto e la possibilità di usare **più di cinque zone**. Restano aperte le formule per ottenere i riferimenti, i criteri di completamento degli step e le convenzioni esatte di FC/recupero. Accettare un preset di zone non risolve queste altre decisioni.

## Fonte e ambito dell'esame

Fonte: `archivio_test.pdf (allegato privato)`, titolo «Archivio Test di Valutazione Funzionale», generato il 26 agosto 2026, 36 pagine PDF (copertina e pagine numerate 1–35). Letti indice, convenzioni, tabelle e serie individuali; ispezionate visivamente pagine rappresentative di aggregati, coorti e copertura. Le numerosità dichiarate sono 19 atleti, 51 test aerobici e 38 anaerobici, stagioni 2023–2026. Non è stata verificata la rigenerazione dai CSV sorgente né importato il PDF nell'app.

I numeri di pagina della matrice seguente sono quelli **stampati** nel documento. Le informazioni personali e le righe dei singoli atleti non sono riprodotte in questa specifica. Non copiare il PDF nei dati dimostrativi o nella repository pubblica.

## Viste implementabili

| ID | Vista della fonte | Implementazione proposta | Prerequisiti / priorità |
|---|---|---|---|
| HIST-01 | Storico completo, pp. 5–10 | Tabella filtrabile e ordinabile per data, categoria, tipo test, protocollo, strumento e qualità; W e W/kg distinti. | Prima fase storici: import strutturato e mappatura delle metriche. |
| HIST-02 | Anno di categoria e stagione, pp. 11–13 | Esordienti 1/2, Allievi 1/2 per stagione; punti individuali e mediana con dispersione, numerosità visibili. | Prima fase; anno di categoria come attributo distinto dalla stagione. |
| HIST-03 | Anno di categoria su tutte le stagioni, pp. 14–15 | Distribuzione storica interna per anno di categoria, filtrabile per protocollo/metodo. | Prima fase; riferimento descrittivo della società, non norma esterna. |
| HIST-04 | Categoria su tutte le stagioni, p. 16 | Aggregazione Esordienti/Allievi con possibilità di separare i due anni di categoria. | Prima fase; esplicitare selezione e peso di ciascun atleta. |
| HIST-05 | Categoria e stagione, pp. 17–18 | Confronto di stagioni con stesso periodo dell'anno opzionale; grafici di punti e distribuzioni. | Prima fase; non interpretare il cambio di popolazione come crescita individuale. |
| HIST-06 | Stagione corrente, pp. 19–20 | Dashboard dell'anno selezionato: aggregati, elenco atleti, dettaglio di tutti i test ed eventuale ultimo risultato. | Prima fase; la stagione non è fissata a 2026 nel codice. |
| HIST-07 | Serie individuali, pp. 21–29 | Grafici MAP/soglia in W e W/kg, peso, FC e altre metriche disponibili; delta assoluto e percentuale, giorni trascorsi, cambio protocollo/strumento/metodo. | Prima fase; FTP selezionabile soltanto quando identificata come tale. |
| HIST-08 | Coorti di nascita, pp. 30–32 | Seguire i nati nello stesso anno fra stagioni, mostrando entrate/uscite e n atleti; vista aggiuntiva sulle sole coppie presenti nei due periodi. | Prima fase; stessa coorte non significa automaticamente identiche persone. |
| HIST-09 | Copertura e anagrafica, pp. 33–35 | Pannello qualità: disponibilità per campo, fonte della soglia, peso misurato/stimato, referto leggibile, integrità FC, durata e protocolli utilizzati. | Prima fase; denominatore pertinente e stato ignoto distinto da falso. |

Queste nove viste sono realizzabili con lo stesso servizio di query e aggregazione, esposto in UI e nei report MD/PDF. Non servono nove algoritmi indipendenti. Serie temporali dei singoli test richiedono FIT/CSV di campioni; le sole tabelle storiche non le ricostruiscono.

## Convenzioni statistiche e qualità

1. **Modalità per atleta, predefinita:** ultimo test valido di ogni atleta nel periodo e gruppo selezionati. Selezione deterministica per data/ora e ID in caso di parità; una sola revisione corrente per test. Se il test selezionato non ha una metrica, quella metrica è mancante: non prendere implicitamente un test diverso per ciascuna colonna.
2. **Modalità tutti i test, compatibilità archivio:** mediana e min/max di tutti i risultati selezionati, con conteggi distinti di test e persone. Replica la convenzione dichiarata dal PDF, senza promettere identità numerica prima della verifica dei sorgenti. I test ripetuti dello stesso atleta hanno più peso. Su più stagioni, la modalità per atleta usa un risultato per atleta nell'intero intervallo; una modalità aggiuntiva per atleta/stagione deve dichiarare che la stessa persona può contribuire più volte.
3. Mediana per ciascuna metrica sui soli valori disponibili; mostrare `n_validi` per colonna. Le mediane delle varie colonne non descrivono un atleta reale e la mediana, con numerosità pari, può essere la media di due valori: non adottare l'affermazione della fonte secondo cui cade sempre su un valore misurato.
4. Min/max per continuità col PDF; IQR come ulteriore dispersione, media e deviazione standard opzionali. Dichiarare algoritmo dei quantili (interpolazione lineare) e deviazione standard campionaria, assente per n<2. Per n=1 mostrare il punto, senza suggerire una distribuzione affidabile. Non nascondere punti estremi senza motivo registrato.
5. Distinguere età alla data del test, età nell'anno solare (`anno_test - anno_nascita`), anno di categoria e coorte. Il PDF usa età nell'anno solare: conservarla come convenzione storica. Regole categoria/età sono configurabili e versionate; nessuna verifica normativa FCI è implicita in questa lettura del documento.
6. Soglie derivate da MAP restano stime. La copertura del PDF dichiara zero soglie da lattato: si possono mostrare in serie e aggregati **esplicitamente dedicati alle stime**, non perderle per il filtro dei soli misurati né mescolarle silenziosamente con soglie misurate. Coefficienti, fonte e data devono accompagnare i risultati.
7. Cambi di protocollo e strumento interrompono la confrontabilità automatica. Il PDF visualizza anche delta fra protocolli differenti: nell'app quei delta sono esplorativi, segnalati e fuori dai riepiloghi di progressione comparabile salvo regola esplicita. Valore precedente nullo o pari a zero: delta percentuale non disponibile. Formula descrittiva: `100 × (nuovo - precedente) / precedente`.
8. Completeness: per ogni indicatore mostrare validi/pertinenti, mancanti e non applicabili, oltre alla percentuale. I flag storici di integrità non equivalgono a una verifica del segnale quando il segnale non è disponibile.

## Estensioni e limiti dei dati

**Anaerobico:** il PDF include picco e media W/W/kg, tempo al picco, indice di fatica, potenza finale e cadenza massima. È fattibile un modulo opzionale di import/consultazione di risultati dichiarati con tipo test e protocollo separati. È una proposta di estensione, non un nuovo motore già approvato o sviluppato. Calcolare tali metriche dai campioni richiede durata, finestre e formule specifiche, in particolare per indice di fatica e potenza finale. Il PDF non basta; occorrono tracciati e specifiche. I tre CSV iniziali non coprono automaticamente questo nuovo dominio.

**Crescita:** le serie consentono variazioni di peso e progressione prestativa; il documento dichiara zero rilevazioni con statura su 51. Non si può ricostruire crescita in cm, PHV o maturazione. La funzione per altezza futura resta prevista quando arrivano misure datate. Una curva di coorte o di categorie di età diversa non misura da sola la crescita degli stessi individui.

**Altre metriche:** J/batt e valori storici privi di formula documentata sono importabili e visualizzabili con provenienza, ma non ricalcolati usando formule ipotizzate. Lattato e benchmark esterni restano metodi da specificare. Nessuna soglia media del gruppo diventa un default individuale implicito.

## Preset di zone confermato

Preset iniziale `PCRS-SOGLIA-5Z`, versione 1, fonte: indicazione dell'utente del 17 ottobre 2026. È una configurazione operativa richiesta, non una validazione scientifica universale. FC riferita a **FTHR**, potenza a **Watt Soglia**; non sostituire automaticamente con FCmax, MAP o FTP.

Tabella originale ricevuta: FC `<81`, `81–89`, `90–99`, `100–105`, `>105%`; potenza `<55`, `56–75`, `76–90`, `91–105`, `>105%`. L'utente ha confermato la seguente risoluzione continua dei confini, incluso il 55% di potenza in Z1.

| Zona | FC: percentuale esatta di FTHR | Potenza: percentuale esatta di Watt Soglia |
|---|---|---|
| Z1 | p < 81 | p ≤ 55 |
| Z2 | 81 ≤ p < 90 | 55 < p ≤ 75 |
| Z3 | 90 ≤ p < 100 | 75 < p ≤ 90 |
| Z4 | 100 ≤ p ≤ 105 | 90 < p ≤ 105 |
| Z5 | p > 105 | p > 105 |

`p = 100 × valore / riferimento`. Riferimento positivo e valido obbligatorio; campioni mancanti o invalidi non classificati. Calcolare sui valori non arrotondati, arrotondare soltanto per la presentazione. Per tabelle di bpm/W interi derivare limiti con floor/ceil coerenti con inclusività, non arrotondare separatamente entrambi gli estremi creando sovrapposizioni. Se un intervallo non contiene valori interi, indicarlo invece di inventarne uno.

Esempio puramente sintetico: FTHR=180 bpm → Z1 ≤145, Z2 146–161, Z3 162–179, Z4 180–189, Z5 ≥190 bpm. Watt Soglia=200 W → Z1 ≤110, Z2 111–150, Z3 151–180, Z4 181–210, Z5 ≥211 W. Queste tabelle valgono per valori interi; un campione decimale viene classificato sul rapporto esatto.

## Numero di zone configurabile

Cinque è il numero del preset, **non un vincolo del modello**. Supportare schemi con N zone (per esempio 3, 5, 6, 7 o più), con numero distinto per FC e potenza. N non codificato in colonne fisse Z1–Z5. Ogni versione contiene una lista ordinata di zone con ID stabile, nome traducibile, colore, limite percentuale e inclusività; prima/ultima zona possono essere aperte. I riferimenti alternativi (FCmax, MAP, FTP ecc.) appartengono a schemi espliciti separati.

Editor: aggiungi/rimuovi/riordina, modifica nomi/confini, duplica preset e salva come nuova versione. Validazione: ordine, intervalli non vuoti, assenza di buchi/sovrapposizioni e copertura del dominio valido. Un confine condiviso appartiene esattamente a una zona. Evitare modifiche distruttive ai preset già usati. Le eventuali sottoclassi come Z5a/Z5b sono zone nominate, senza imporre subito una struttura gerarchica.

UI, legende, tabelle PDF/MD, grafici e tempi in zona devono iterare sulla lista, adattarsi a N e usare colori più etichette. Export esteso in formato lungo: una riga per zona con schema/versione/riferimento/limiti; nessuna modifica silenziosa alle intestazioni dei CSV compatibili esistenti. Analisi e report congelano schema e valore di riferimento. Cambiare schema crea una nuova analisi/revisione.

I tempi in zona sono un'estensione fattibile solo con campioni: integrarli sul tempo valido, rispettando pause e gap, con tempo non classificato esplicito. Non sommare semplicemente il numero di campioni quando il campionamento è irregolare.

Criteri di verifica: valori esatti e immediatamente sotto/sopra 55/75/90/105% e 81/90/100/105%; N=3/5/7; schemi invalidi rifiutati; riferimenti mancanti; round trip schema; vecchio report invariato dopo nuova versione; somma tempi validi coerente e rendering senza tagli con più di cinque zone.

## Logo e tema

Asset fornito: `F:/Progetto Ciclismo RS/Logo Progetto Ciclismo - Rodengo S.-1(2).png`, 1104 × 707 pixel. Questo è il riferimento selezionato dall'utente, in sostituzione del precedente logo individuato autonomamente.

Colori solidi rilevati nei pixel opachi: blu `#1A62B7`, giallo `#FFF100`, scuro `#221E20`, bianco `#FFFFFF`. Sono valori del file, non una dichiarazione di specifiche ufficiali di stampa. Conservare il logo originale, rapporto d'aspetto e trasparenza. Non ricolorarlo per ottenere il tema attenuato.

UI-02: blu per azioni e selezione, giallo in piccoli accenti decorativi, superfici chiare neutre e tinte tenui derivate. Niente testo giallo su fondo bianco; contrasto da verificare sulle combinazioni finali. UI-03: logo in basso con area chiara se necessaria alla leggibilità, link società e credito autore come già concordato. Non usarlo come icona microscopica illeggibile: prevedere il marchio completo nell'area crediti. Il nome della suite resta indipendente dal logo della società.

## Stato del lavoro

Valutazione e specifica completate; nessuna importazione di dati personali, modifica del programma o implementazione dei calcoli in questa revisione. Per sviluppare le viste aerobiche non è necessario approvare il modulo anaerobico. Per applicare le zone serve un riferimento fornito o calcolato con metodo esplicito; non è necessario inventare un coefficiente automatico.
