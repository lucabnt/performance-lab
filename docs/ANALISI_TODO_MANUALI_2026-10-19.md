# Analisi delle osservazioni manuali — 19 ottobre 2026

**Attuazione successiva alla presente analisi:** i requisiti sono stati sviluppati nei sorgenti; vedere lo stato aggiornato in [REQUISITI_E_TODO.md](REQUISITI_E_TODO.md), le prove in [VERIFICA.md](VERIFICA.md) e i metodi effettivamente adottati in [MATURAZIONE.md](MATURAZIONE.md). Le proposte sotto restano la traccia della fase di analisi, non sostituiscono la specifica implementata.

Acquisite le **11 osservazioni** inserite dall'utente in coda a REQUISITI_E_TODO.md; testo intatto in [COMMENTI_ORIGINALI_2026-10-19.md](COMMENTI_ORIGINALI_2026-10-19.md). Sono state scomposte in **15 requisiti TD-83–97**, con stato, priorità e accettazione nel [registro](REQUISITI_E_TODO.md#osservazioni-manuali-acquisite--19-ottobre-2026).

Questa revisione modifica soltanto i documenti. Il riscontro funzionale deriva dalla lettura del codice attuale; non sono stati ripetuti collaudi UI, collegamenti cloud o test scientifici. Richieste dell'utente, riscontri e proposte tecniche sono distinti sotto. Non viene assunto come già approvato un particolare modello di maturazione.

## Tracciabilità

| Osservazione originale, nell'ordine | Requisiti | Esito dell'analisi |
|---|---|---|
| 1. Correggi prova come pulsante | TD-83 | Miglioria del flusso, preservando revisioni e annullamento |
| 2. Campi personalizzati in coda | TD-84 | Ordinamento coerente di inserimento e consultazione |
| 3. Legenda a fondo pagina | TD-85 | Glossario contestuale riusabile nella suite |
| 4. Soglie evidenti, coefficienti e zone | TD-86–87 | Gerarchia visiva e provenienza dei valori, senza nuove formule implicite |
| 5. Garanzia e rischio perdita dati | TD-88 | Avvisi applicativi coerenti con GPL, testo da revisionare prima della distribuzione |
| 6. Secondi da leggere sul grafico | TD-89 | Completare e uniformare una selezione grafica già parzialmente presente |
| 7. Utilità grafico lattato | TD-90 | Mantenerlo come vista lattato-carico, spiegare e collegare la FC della tabella |
| 8. X sempre visibile | TD-91 | Testata persistente del dettaglio/editor, accessibile e opaca |
| 9. Pulsanti collegamento cloud | TD-92 | Codice presente, operatività della distribuzione non ancora qualificata |
| 10. Indici maturativi e priorità per età | TD-93–97 | Nuova area con dati datati, metodi/versioni e limiti espliciti |
| 11. Dati opzionali non previsti nella raccolta | TD-93, TD-95–96 | Nessun obbligo di raccolta né evidenza prioritaria degli indici che ne dipendono |

## Dettaglio test: azioni, gerarchia e spiegazioni

**Riscontro:** `frontend/src/main.tsx` contiene ancora sezioni espandibili «Correggi prova», fra cui quella anaerobica; le famiglie non hanno un unico flusso di correzione. Il pulsante richiesto deve aprire un editor con stato proprio, titolo «Correggi test», azioni finali Salva revisione/Annulla e motivazione. Il dettaglio resta consultabile senza visualizzare un intero modulo. La X deve restare nel bordo superiore del pannello mentre scorre il contenuto; Esc e ritorno del focus all'elemento di apertura completano il comportamento. In presenza di modifiche non salvate va gestita l'uscita, evitando perdita silenziosa.

**Ordine proposto per l'incrementale:** identità/data/protocollo e azioni; grafico temporale; riepilogo MAP e riferimenti di soglia; zone immediatamente sotto ai riferimenti; dettaglio step e qualità; analisi lattato/gas quando presenti; recupero e condizioni; note e campi personalizzati in coda; glossario. I riepiloghi senza tracciato mantengono un avviso al posto del grafico. Nei test anaerobici/custom si usano le metriche pertinenti: non vanno introdotte MAP o soglie fittizie per uniformare il layout. Le osservazioni su ordine e componenti sono proposte di disegno, da verificare nel prototipo.

**Soglie:** MAP, Watt Soglia e FTHR hanno la stessa evidenza visiva ma restano grandezze distinte. Una scheda deve indicare valore/unità, fonte e metodo; quando un coefficiente è effettivamente applicato, la riga sotto mostra base × coefficiente = risultato e identità/versione del preset. Il coefficiente della potenza non si applica automaticamente alla FC. Un valore dichiarato rimane dichiarato; un livello fisso di lattato non viene rinominato automaticamente soglia fisiologica. Zone e loro riferimento devono essere leggibili insieme, con data/provenienza; valori assenti non valgono zero.

**Campi personalizzati:** collocazione finale in editor e dettaglio, mantenendo validazione, ordine del protocollo, unità e distinzione null/zero/false. La richiesta non implica spostare i campi fuori dal modello di protocollo o renderli tutti obbligatori. Riferimento esistente TD-75.

**Glossario:** un catalogo di termini con chiavi stabili e testi IT/EN, più l'elenco dei termini usati da ciascuna pagina. In fondo si mostrano solo le spiegazioni pertinenti, con unità e distinzione misurato/calcolato/stimato. Esempi: MAP, FTHR, RPE, mmol/L, HV, PHV, APHV, %PAH. Il componente grafico e la struttura sono candidati alla libreria comune; definizioni scientifiche e regole di applicabilità rimangono in Fuorigiri. Il riferimento a Intervals.icu è un esempio di stile fornito dall'utente, non una richiesta di copiarne formule o interfaccia.

## Tempi sul grafico: processo consigliato

**Riscontro:** la creazione incrementale dispone già di «Selezione sul grafico → Imposta fine sforzo/inizio protocollo» e converte la selezione nei secondi archiviati. Il grafico unificato del dettaglio usa invece minuti senza un cursore esplicito in secondi. È quindi un problema di scoperta e uniformità oltre che di presentazione.

Flusso proposto: attivare «Imposta fine sforzo», zoomare, puntare/selezionare il campione, leggere **23:45 · 1.425 s dal file**, verificare il marker verticale e il campo aggiornato, quindi confermare. Il campo può accettare secondi e una vista mm:ss sincronizzata; nessuna conversione mentale richiesta. Il click non deve salvare direttamente la revisione. Rendere disponibile anche il solo input da tastiera, indicando precisione dei campioni e origine temporale.

Offset, fine sforzo, marker e prelievi devono dichiarare se sono relativi all'inizio del file o del protocollo; tempi di recupero relativi alla fine sforzo distinti dai precedenti. Non cambiare silenziosamente gli attuali secondi negli archivi/API. Collaudo: 23:45 corrisponde a 1.425 s; 23,45 minuti decimali è un valore diverso; selezione e revisione devono conservare lo stesso istante anche con offset non nullo.

## Il grafico del lattato è utile?

**Sì, se è chiaro che cosa rappresenta.** La vista corrente in `LactateResults.tsx` ha già la potenza sull'asse X e il lattato sull'asse Y; non è priva di potenza. Mostra prelievi, andamento e attraversamenti dei livelli. La FC è nei dettagli dei punti stimati e nella tabella W/W/kg/bpm; non è una linea continua del grafico lattato-carico.

Proposta: sottotitolo esplicativo, selezione collegata fra punto/livello e riga della tabella, guide verso watt e concentrazione, FC in tooltip e riga selezionata. Mantenere visibile il grafico temporale per correlare potenza/FC/cadenza e tempi dei prelievi. Un eventuale grafico lattato–FC è una vista secondaria e usa solo associazioni valide: non basta aggiungere una linea FC su una scala priva di significato.

Conservare le salvaguardie del metodo corrente: FC dalla finestra dello step associato, non dal battito al prelievo; assenze esplicite, nessuna estrapolazione, prelievi osservati distinti dai livelli interpolati. La modifica richiesta è di spiegazione/lettura, non autorizza una nuova equazione di soglia.

## Collegamento cloud: cosa funziona e cosa manca

**Riscontro:** `frontend/src/cloud.tsx`, `backend/cycling_test/cloud.py` e `sync_service.py` implementano avvio OAuth, callback/stato, credenziali e adapter. Non sono pulsanti fittizi; tuttavia non esiste ancora una configurazione OAuth della distribuzione verificata con account reali. Client ID/app key, eventuali parametri, destinazione e permessi sono prerequisiti. Non è possibile dedurre dal codice l'esito del tentativo specifico dell'utente.

Registrare uno stato comprensibile prima del click: «Integrazione da configurare» con azione di configurazione, «Account da collegare», «Account collegato», «Cartella non accessibile», «Sincronizzazione riuscita/da completare». Se non si può avviare il consenso, spiegare il motivo accanto al comando; su errore mostrare come recuperare. Rilevare il browser di autorizzazione non aperto e offrire un collegamento alternativo. Non inserire segreti distribuiti universalmente per mascherare il problema.

L'accettazione richiede configurazione del distributore, due account sulla stessa società, verifica effettiva della cartella, rinnovo/revoca e comportamento offline. Usare il test locale simulato come prova del contratto, non come prova della collaborazione reale. Rimangono validi [CLOUD_CONFIGURAZIONE_07.md](CLOUD_CONFIGURAZIONE_07.md) e l'isolamento per società; nessuna nuova autorizzazione cloud eseguita in questa revisione.

## Licenza, garanzia e conservazione dei dati

Il file [LICENSE](../LICENSE) contiene già GPLv3, §§15–17: assenza di garanzia, limitazione di responsabilità e interpretazione secondo legge applicabile. Va resa raggiungibile dalla GUI insieme a copyright, versione e avvisi delle dipendenze. La [GPL ufficiale](https://www.gnu.org/licenses/gpl-3.0.html) resta la fonte del testo; non modificarla né aggiungere restrizioni incompatibili.

La richiesta diventa anche un requisito di comunicazione: evidenziare che conservazione/integrità dei dati non sono garantite, distinguere sync da backup e indicare come creare **e provare a ripristinare** copie indipendenti. Gli attuali limiti del backup devono essere visibili e non nascosti dietro l'avviso. Specificare limiti delle stime e uso del software senza presentarlo come diagnosi medica. Il branding fisso resta invariato.

«Tutte le tutele necessarie» non può essere tradotto in una promessa di esenzione assoluta. Il testo per la distribuzione deve rispettare le norme applicabili e richiede revisione giuridica prima del rilascio; non viene introdotta adesso una nuova EULA o una presa visione bloccante ad ogni avvio. Questa è un'analisi dei requisiti, non un parere legale sul singolo distributore.

## Crescita e maturazione: piano sostenibile con i dati raccolti

**Riscontro:** `Measurement` conserva ora massa/statura/data/fonte; `history.growth()` calcola delta e annualizzazione fra misure consecutive. Non è presente un motore maturativo. I campi custom del test non sostituiscono una serie antropometrica indipendente e strutturata. Le ultime due osservazioni estendono TD-18, che prima copriva statistiche descrittive soltanto.

### Separare osservazioni, stime e ricostruzioni longitudinali

| Indicatore | Dati e interpretazione | Priorità proposta |
|---|---|---|
| HV, velocità di crescita staturale | Due stature datate producono una velocità media nell'intervallo: Δcm × 365,25 / giorni. Servono controlli su qualità, intervallo e duplicati; non è una velocità istantanea. | Primo sviluppo: compatibile con la raccolta abituale |
| Maturity offset / APHV stimata | Modello antropometrico esplicito, età decimale e parametri richiesti. APHV stimata = età alla misura − offset. Dominio e popolazione del modello contano; non è PHV osservato. | Secondo sviluppo, dopo specifica e confronto indipendente |
| PHV / APHV da curva longitudinale | Picco di velocità e sua età da una serie sufficientemente estesa attorno al picco; modello/smoothing e copertura espliciti. Il massimo di due sole differenze non dimostra il PHV. | Successivo, con serie adeguate; indisponibile se picco non documentato |
| Statura adulta prevista, %PAH e residuo | La %PAH dipende dalla previsione: 100 × statura attuale / statura adulta prevista; residuo come differenza, con incertezza del modello. Khamis–Roche richiede anche stature dei genitori. | Opzionale, non evidenziato nel flusso abituale |
| Proporzioni corporee, crescita arti, apertura braccia | Richiedono misure specifiche datate; dati genitoriali/segmentali non vanno ricavati arbitrariamente dalla sola statura. | Avanzato, facoltativo e non in evidenza |

**Metodi candidati, non ancora selezionati:** valutare Mirwald e le varianti Moore soltanto dove i dati e il dominio lo consentono. Alcune varianti riducono gli input, ma non eliminano i limiti individuali. Non applicare la stessa formula indistintamente a tutti, né inferire parametri dal nome o dal gruppo. Per le equazioni che lo richiedono occorre un parametro esplicito relativo al modello, distinto dalle altre informazioni anagrafiche. Data di nascita completa e data della misura per l'età decimale: anno soltanto non va convertito in precisione fittizia.

Uno [studio di validazione longitudinale](https://pubmed.ncbi.nlm.nih.gov/38377009/) su 124 calciatori ha rilevato classificazioni errate sostanziali con diversi metodi di offset; è un motivo per non trattare la stima individuale come certezza o trasferirla automaticamente ai ciclisti. La [validazione delle equazioni modificate](https://pmc.ncbi.nlm.nih.gov/articles/PMC5752743/) documenta dipendenza da età e timing maturativo. Il metodo [Khamis–Roche](https://pubmed.ncbi.nlm.nih.gov/7936860/) ha una popolazione di sviluppo specifica; prima di implementarlo occorre acquisire le tabelle corrette, inclusa l'[errata corrige](https://publications.aap.org/pediatrics/article/95/3/457/59792/ERRATUM), e verificarne uso/riproducibilità. Nessun calcolo di questo tipo viene introdotto da questa revisione documentale.

**Conseguenza pratica della preferenza dell'utente:** con statura, massa e date si inizia da HV e andamento antropometrico. Genitori, apertura braccia e lunghezza arti rimangono campi possibili nella sezione avanzata, e gli indici dipendenti non vengono messi in evidenza. La statura seduta è un ulteriore dato da valutare, non un obbligo già richiesto. Se manca un input di un modello, mostrare «non calcolabile» e il motivo; non riempirlo con medie o formule alternative silenziose. Non stimare la statura residua per tutti come 18 anni meno età attuale.

### Evidenza per età e disponibilità

La tabella dell'utente è recepita come orientamento della UI. Per evitare sovrapposizioni si propone età alla data selezionata con intervalli [13,14), [14,15), [15,16), [16,18), ≥18; sotto 13 anni rimangono misure/andamento e soli modelli applicabili. L'inclusione dei 18 anni nell'ultima fascia è una convenzione UI proposta, non un criterio biologico.

| Fascia proposta | In evidenza quando disponibili e validi | Secondari / limitazioni |
|---|---|---|
| 13–<14 | HV; offset se applicabile al modello e ai dati | %PAH e proporzioni solo avanzati, secondo preferenza espressa |
| 14–<15 | HV; picco/APHV se documentato longitudinalmente, oppure APHV stimata chiaramente distinta | Non dichiarare che il picco deve avvenire in questa fascia; %PAH secondaria |
| 15–<16 | HV, andamento nel tempo e APHV con fonte distinta | Crescita arti solo con serie specifica, non in evidenza; nessuna diagnosi di maturazione tardiva |
| 16–<18 | HV e andamento staturale | Residuo e %PAH restano opzionali; non obbligare l'uso di un modello fuori dominio |
| ≥18 | Andamento antropometrico; eventuale stabilizzazione supportata dai dati | Non considerare conclusa la crescita per sola età; modelli adolescenziali non estesi arbitrariamente |

Il dominio del metodo e la qualità dei dati prevalgono sulla fascia grafica. Non cancellare né nascondere risultati storici cambiando età. La pagina atleta deve conservare l'intera serie e tutti i risultati validi in una sezione dedicata, con «misura», «stima da modello» o «ricostruzione longitudinale», metodo/versione, input e motivo delle assenze. Fasce cronologiche identiche non impongono lo stesso timing maturativo a tutti.

### Dati, revisioni e accettazione del motore

Prevedere misure datate indipendenti dal test, valori/unità/qualità/fonte, nuovi campi opzionali e parametri del modello con provenienza. Correggere una misura con cronologia, senza ricalcolare silenziosamente risultati già esportati. Ogni analisi conserva input risolti e versione del metodo; aggiornamenti espliciti generano nuove revisioni.

Prima del motore definire: dominio per metodo, precisione delle misure, intervallo minimo per annualizzazione utilizzabile, serie minima e copertura per PHV, modello di smoothing, incertezza e gestione dati incoerenti. Questi numeri non sono fissati arbitrariamente come consenso scientifico. I criteri scelti saranno versionati e visibili, con output non disponibile quando non soddisfatti.

Accettazione: casi numerici indipendenti dalle funzioni implementate, dati mancanti, solo anno nascita, misure nello stesso giorno, intervalli brevi, calo statura, picco fuori dalla serie, età fuori dominio, revisione e vecchio backup. Serie sintetiche con picco noto per la ricostruzione; confronto esterno prima di qualificare le stime. CSV esteso/report/backup/sync includono provenienza e null; schema CSV storico preservato. Nessun punteggio maturativo usato per selezionare/escludere automaticamente atleti.

## Sequenza raccomandata e scelte residue

1. **Rifinitura del dettaglio** (TD-83–91): flusso correzione/chiusura, tempi dal grafico, gerarchia soglie/zone, campi in coda e glossario. Prototipo comune alle famiglie prima del codice; riusare primitive della suite mantenendo qui il dominio scientifico.
2. **Trasparenza cloud e distribuzione** (TD-88, TD-92): messaggi e prerequisiti reali, avvisi licenza/dati. Il collaudo cloud resta condizione di accettazione; continua il lavoro prioritario già registrato su sync v2/backup grandi/separazione legacy.
3. **Antropometria e HV** (TD-93–94, TD-97): estensione minima dei dati, storico e controlli qualità, prima delle stime maturative.
4. **Metodi maturativi uno alla volta** (TD-95–97): specifica, vettori di riferimento, risultati con incertezza e integrazione nello storico. PHV longitudinale dopo la disponibilità di serie adatte; indici con dati opzionali restano avanzati.

Non occorrono nuove scelte di stack o nuove repository. Restano da definire prima dei relativi calcoli: quali misure aggiuntive raccogliere (in particolare statura seduta), metodo/popolazione di validazione e domini, criteri di qualità/campionamento e politica di incertezza. La richiesta già chiarisce che genitori/braccia/arti non devono essere obbligatori o prioritari; non è necessario richiederne conferma.
