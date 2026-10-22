# Requisiti e to-do

## DESKTOP-01 — ultima società alla riapertura, 22 ottobre 2026

**Implementato nei sorgenti.** All’avvio desktop riaprire l’ultima società visualizzata, inclusa quella appena creata, senza ripetere la selezione. Preferenza del dispositivo (soli ID di archivio e società), indipendente dalla porta HTTP, esclusa dai dati condivisi. Validazione contro inventario e stato; archivio ricordato assente: selettore con avviso, senza scegliere un’altra società. Funziona anche per il visualizzatore senza concedere scritture societarie. Android mantiene il comportamento esistente. Accettazione sull’installer aggiornato ancora da eseguire.

## PILOT-01 — candidato e accettazione Windows/Android, 21 ottobre 2026

Richiesta: preparare un candidato e una checklist Markdown con completamenti. Versione prodotto conservata 0.10.0, ID candidato separato. Build isolate, Windows dipendenze incluse/installer/portabile; Android release non firmato su scelta esplicita del titolare, con procedura per chiave stabile e firma. Sorgenti/wheel/provenienza e checksum a corredo, nessuna pubblicazione. Criteri: regressione locale, smoke congelato, integrità pacchetti e checklist tracciata; PC pulito, firma, telefono, provider reali e validazione esterna restano gate distinti prima della promozione. [Collaudo](COLLAUDO_PILOT.md), [firma](FIRMA_ANDROID.md).

## TD-106–107 — marchio e grafico immersivo Android, 21 ottobre 2026

- **TD-106 — implementato, corretto su indicazione dell’utente:** nella testata Android scritta Fuorigiri/Performance Lab allineata a destra, seguita dal logo alla sua destra; intero gruppo sul bordo destro, hamburger a sinistra. Variante comune brand-end dalla UI 0.2.8. Sostituisce la precedente indicazione “logo a sinistra” nella testata; bootstrap centrati e sidebar desktop conservano la propria composizione. Il logo societario resta distinto e fisso.
- **TD-107 — implementato e verificato su emulatore:** Vista ampia orizzontale usa l’intera WebView, senza cornice o intestazione visibile “Esplora grafico”. Titolo accessibile conservato; X flottante e pannello Comandi grafico richiamabile, chiuso di default. Grafico alto quanto il viewport; comandi/dati non sottraggono una fascia permanente. Barre Android temporaneamente nascoste, richiamabili con swipe di sistema; ripristino della visibilità/politica precedente alla chiusura insieme all’orientamento. Back esce prima dall’esplorazione, poi chiude il pannello aperto, poi la vista. I comandi restano sotto il grafico nella vista normale. Cutout/insets di sicurezza rispettati; telefono/TalkBack/tablet da qualificare.

## TD-105 — Vista ampia orizzontale Android, 21 ottobre 2026

**Implementato e verificato su emulatore:** Vista ampia richiede temporaneamente sensorLandscape tramite bridge nativo di origine fidata; memorizza la precedente politica di orientamento e la ripristina alla chiusura, allo smontaggio della vista o al reload della WebView. La rotazione non ricarica il test e il grafico adatta altezza/larghezza al viewport. Scorri pagina rimane il default; un Back esce da Esplora/Zoom restando in orizzontale, il successivo chiude la vista e ripristina l’orientamento. Nessuna modifica all’orientamento globale delle altre schermate. Telefono e finestre/tablet rimangono da qualificare.

## TD-102–104 — grafici touch, avvio e contesto Android, 21 ottobre 2026

- **TD-102 — implementato, collaudo emulatore:** hamburger sempre a sinistra, nessuna freccia Indietro duplicata nella testata; ritorno tramite tasto/gesture di sistema. Padding e margini Android moderatamente ridotti, senza ridurre i controlli sotto 48 CSS px. Grafici in Scorri pagina per default, anche nella vista ampia: comandi Esplora, Zoom, Ripristina e Vista ampia sotto la figura. Un solo Indietro esce da Esplora/Zoom, mantenendo aperto il dettaglio; successivamente chiude l’ultimo dialogo e poi segue la cronologia. Dialoghi annidati isolano cancel. Zoom/pan riservano le gesture al grafico soltanto dopo attivazione esplicita; nessuna modifica ai campioni/calcoli.
- **TD-103 — implementato:** apertura nativa con indicatore indeterminato e fase reale; caricamento interfaccia/archivio distinto, stato leggibile e Riprova in caso di errore, senza suggerire reset. Plotly in chunk locale differito e caricato quando un grafico raggiunge il viewport; nessun download Internet necessario. Non equivale a runtime Python istantaneo né a riduzione del peso complessivo dell’APK.
- **TD-104 — implementato, accessibilità completa da qualificare:** testata Android persistente con società/sezione e operatore/ruolo, contesto atleta/data nel dettaglio; focus sul titolo al cambio pagina, lingua documento IT/EN, controlli grafici con stato premuto leggibile e movimento ridotto nel common. Alternativa tabellare ai grafici con serie/unità, min/max/conteggio dei valori numerici, mancanti distinti da zero e 30 righe per pagina. Coordinate di serie diverse non vengono equiparate. Telefono, TalkBack, testo di sistema ingrandito e ulteriori configurazioni rimangono gate distinti dalle prove DOM/emulatore.

**Riutilizzo:** UI comune 0.2.6, ChartFrame e LoadingState; logica scientifica, scelta dei modi touch, caricamento Plotly, route e contenuti rimangono di Fuorigiri. Nessun aggiornamento automatico di Ammiraglia. Prove effettive in VERIFICA.md; guida suite aggiornata nello stesso intervento.


## TD-99–101 — ergonomia Android e pratiche suite, 20 ottobre 2026

- **TD-99 — implementato:** Indietro chiude prima menu/dialoghi con conferma delle modifiche; altrimenti torna tra sezione/profilo/elenco, con pagina, filtri e scroll conservati nella sessione. Solo la radice consente uscita. Cronologia limitata e azzerata al cambio archivio. Atleti/test Android in schede da 20 record, ricerca e filtri richiudibili, ritorno alla prima pagina dopo un filtro; niente tabelle orizzontali per questi due elenchi. Moduli principali (atleta/gruppo, misura, protocolli, manuale/incrementale/anaerobico/custom/revisione storica) con FormActions comuni; azioni originali e validazioni preservate, campi numerici non negativi con tastiera appropriata, tempi manuali con TimeInput, riferimenti/recupero facoltativi richiudibili. Riepilogo società e guida test richiudibili su Android. Tabelle desktop e viste analitiche restano distinte.
- **TD-100 — implementato:** all’avvio Android si ricorda l’ultima coppia archivio/società mediante preferenza locale persistente. Non memorizza dati sportivi o credenziali. Ogni apertura riconcilia l’ID con l’inventario; un archivio sparito porta alla selezione, senza aprire un’altra società. Test per morte sessione/preferenze malformate/risposte obsolete, prova di force-stop sull’emulatore.
- **TD-101 — documentato e adottato dove indicato:** guida canonica delle best practice Android in cycling-suite-common/docs/ANDROID_BEST_PRACTICES.md; fonte unica dei componenti RecordCards, CollapsibleFilters e FormActions nella UI comune 0.2.4. Consegna versionata locale a Fuorigiri, senza aggiornamento implicito delle altre app o pubblicazione. Adozioni/verifiche specifiche nel registro Fuorigiri; telefono, TalkBack e IME completo sono gate separati.

Criteri: elenco filtrato/pagina conservati tornando dal profilo; dettaglio test si chiude sull’elenco; bozza sporca protetta; selezione riaperta dopo arresto; nessun fallback su società diversa se rimossa. Le prove effettive e le limitazioni sono in VERIFICA.md.

## TD-98 — navigazione Android compatta, 20 ottobre 2026

**Richiesta:** Gestisci società, sezioni e lingua nel menu hamburger; informazioni del footer in una sezione Info.

**Implementato:** su Android testata con pulsante Apri menu e identità prodotto. Il menu raccoglie selezione società/Gestisci società, Atleti, Test e analisi, Protocolli, Società e gruppi, Storici e confronti, Archivio e scambio, Info e lingua. Info è raggiungibile anche senza società e contiene versione, stato locale/offline, logo/attribuzione fissi e licenza/limiti. Questi contenuti non sono ripetuti nel footer delle altre pagine Android. Navigazione desktop e componenti comuni conservati: menu di prodotto composto con Dialog e controlli della suite, nessuna copia dei suoi stili o nuova dipendenza dalla repository sorella.

**Accettazione verificata su emulatore API 35 x86_64:** apertura menu, Indietro chiude senza uscire dall’app, scelta Info chiude il menu, Gestisci società apre un solo dialogo, licenza raggiungibile, etichette IT/EN e lingua ripristinata. Screenshot reali nella galleria. Telefono e prove tattili/accessibilità complete rimangono distinti.

## Avanzamento Android — 20 ottobre 2026

**Ultimo esito:** corretto collegamento ABI3 delle wheel cryptography, APK installato e avviato su emulatore API 35 x86_64, test nativo import/cifratura/firma/API/Keystore passato. Corrette sovrapposizioni con barre Android e invalidazione cache wheel Gradle. TD-57 resta aperto per telefono ARM64, report/import/test completi, cloud e accettazione. Le note successive conservano gli stati precedenti.

**Aggiornamento:** trasferimento e hash delle sei wheel verificati localmente, dipendenze Chaquopy risolte per entrambe le ABI, APK debug prodotto su Windows. TD-57 ancora aperto: emulatore non rilevato all’ultimo controllo ADB, installazione/import nativi e flussi applicativi da collaudare. I paragrafi successivi descrivono il gate precedente.

Procedura ripetibile documentata in [ANDROID_WHEEL_FEDORA.md](ANDROID_WHEEL_FEDORA.md); versioni degli strumenti host non completamente registrate nel log, quindi nessuna garanzia di identità binaria.

TD-57 resta aperto: builder Fedora autorizzato per wheel Android, sei artefatti prodotti e digest ricevuti. Gate di packaging esteso a CFFI 2.0.0, oltre a pydantic-core/cryptography. Accettazione residua: trasferimento e hash locali, risoluzione dipendenze Chaquopy, APK, import nativi e collaudo prima su emulatore poi telefono. Il packaging applicativo Linux resta rinviato.

## Versionamento prodotto — 20 ottobre 2026

- **REL-VERSION-01 — implementato:** versione sorgenti 0.10.0 coerente fra backend/API, UI e lockfile, Android (`versionCode` 1000), installer Windows e AppStream Linux. `scripts/verify_versions.py` blocca build/release incoerenti; UI, header HTTP e nomi APK derivano dalle rispettive fonti correnti. Versioni di motori, renderer, protocolli e formati dati rimangono indipendenti. Nessuna pubblicazione o ricompilazione di installer implicita.

## Documentazione corrente — 19 ottobre 2026

- **DOC-01 — implementato:** indice delle guide, separazione dei documenti storici in `archivio/`, nomi delle guide indipendenti dalle release, README italiano con presentazione in inglese e link operativi; roadmap corrente distinta dai piani originali. Le analisi e i commenti originali restano conservati. [Indice](README.md), [roadmap](PROSSIMI_PASSI.md).

## Correzioni profilo e demo — 19 ottobre 2026

- **UI-PROFILE-01 — implementato:** dal dettaglio di ogni famiglia di test si può aprire direttamente il profilo dell’atleta associato, chiudendo il dettaglio; nessun permesso di modifica richiesto.
- **DEMO-MAT-01 — implementato:** corpus standard completo e ridotto includono quattro profili maturativi per società, casi maschile/femminile con indici avanzati, dati insufficienti e adulto. Snapshot e misure presenti nelle repliche e nei backup iniziali; manifest con risultati attesi. Rigenerazione conservativa esplicita, nessuna migrazione silenziosa delle demo esistenti.

**Attuazione TD-83–97, 19 ottobre 2026:** implementati nei sorgenti flussi test/glossario/riferimenti/tempi, avvisi licenza, stati cloud e crescita/maturazione con snapshot, export e report. Rimangono collaudo provider reale, revisione giuridica e validazione scientifica esterna; nessun nuovo installer. [Registro e accettazione](#osservazioni-manuali-acquisite--19-ottobre-2026), [specifica maturazione](MATURAZIONE.md), [verifiche](VERIFICA.md). Le sezioni datate conservano lo stato storico; non prevalgono su aggiornamenti successivi.

## Revisione e isolamento degli archivi — 19 ottobre 2026

- **REV-01 — implementato:** spazi/metadati protocolli, persistenza e concorrenza della selezione società, confronti con origine soglia assente, W/kg stimati esclusi dai delta, metriche dinamiche e selezione delle serie nel profilo.
- **SYNC-ISO-01 — implementato:** un archivio gestito per società, identità vincolata, canali/connessioni/inviti distinti. Vecchi archivi multi-società consultabili ma bloccati per sync e inviti; nessuna separazione automatica. La selezione UI non è un filtro di condivisione. Usare cartelle cloud con ACL distinte per collaboratori diversi.
- **SYNC-PERF-01 — implementato parziale:** sync ordinaria salta pacchetti già verificati; verifica completa esplicita. Restano duplicazione degli allegati/campioni per revisione e inventario completo del canale.
- **SYNC-V2-01 — implementato nei sorgenti:** blocchi cifrati riutilizzabili, campioni separati nell’involucro remoto, pagine leggere, ricevute/cursore locale e checkpoint di bootstrap; attivazione esplicita del fondatore con avviso firmato, lettura v1/v2 e storico conservato. Il database locale resta canonico; inventario remoto ancora completo e nessuna pulizia automatica. [Contratto e limiti](SYNC_V2_E_BACKUP.md).
- **BACKUP-SCALE-01 — implementato nei sorgenti:** ZIP64 schema 3 con snapshot SQLite, inventario JSONL, hash e file elaborati su disco; upload/anteprima/ripristino progressivi, pubblicazione atomica e lettura dei backup precedenti. Prova effettiva oltre 100 MB; limiti superiori non qualificati in produzione. Salvataggio diretto desktop evita il buffering del download nel browser.
- **SYNC-MIG-01 — implementato nei sorgenti:** anteprima e impronta, estrazione per società con dipendenze e tutte le revisioni, conflitti e file propri, nuova autorità/canale/inviti e originale intatto. Riferimenti incoerenti o non attribuibili bloccano la procedura; editor di riconciliazione dei casi ambigui non implementato.
- **QA-RELEASE-01 — da completare:** flusso GUI automatizzato completo, FIT reali anonimizzati, account cloud distinti, interruzioni/revoche/conflitti; candidato Windows su VM pulita. Fedora/Android restano rinviati al builder disponibile. Traduzione e accessibilità da completare.

Dettagli: [revisione generale](archivio/REVISIONE_GENERALE_2026-10-19.md), [dimensioni e strategia sync](SYNC_DIMENSIONI_E_SCALABILITA.md). Le stime derivano da registrazioni sintetiche misurate, non da un archivio reale pluriennale.

## Suite comune — prima estrazione, 18 ottobre 2026

- **TD-79 / SUITE-02 — implementato:** repository autonoma `cycling-suite-common`, ramo main, tag UI 0.1.0, GPL-3.0-or-later. Le app conservano repository/build/versioni proprie; nessuna pubblicazione GitHub/npm eseguita.
- **TD-80 / UI-26 — implementato iniziale:** pacchetto React tema/Field/DataTable/SortableTable/branding fisso, catalogo e test; Fuorigiri lo utilizza tramite artefatto versionato, con sorgenti/licenza/logo e provenienza verificati. Sidebar, shell e modali ancora da estrarre.
- **TD-81 / SUITE-03 — da sviluppare:** integrazione e collaudo in Ammiraglia, catalogo completo e verifiche tastiera/focus/mobile; versioni comuni aggiornate esplicitamente dalle singole app.
- **TD-82 / SUITE-04 — da progettare/estrarre:** client, contratti dati, servizi Python condivisi e interoperabilità degli archivi. Nessun SQLite/credenziale condiviso automaticamente; motori dei test e pianificazione distinti. [Guida](SUITE_CONDIVISA.md).

## 0.8 / architettura 1.6 - richiesta corpus e flussi di creazione

- **TD-74 / UI-25:** creazione e versionamento di tutte le famiglie in Protocolli; incrementali manuali senza ERG o solo catalogo, Sprint/Wingate e custom. Filtri nome/famiglia/stato. Nuovo test sceglie protocollo/versione e modalità manuale/FIT/CSV; rimossa la creazione dei protocolli da Test e analisi.
- **TD-75 / DATA-04:** campi opzionali definiti dall’utente, tipizzati, con unità/limiti/scelte e scheda protocollo oppure prova. Aggiunta di campi alla sola esecuzione, senza mutazione del protocollo; snapshot, revisioni e validazione backend. Null/zero/false distinti. Nessuna formula arbitraria, nessuna equivalenza fisiologica implicita.
- **TD-76 / ANA-04:** importatore FIT comune con scelta sessione e gestione esplicita duplicati; inizio su grafico, zoom sullo sforzo, riepilogo protocollo e esclusioni motivate. Nuova versione parte dal metodo precedente in Protocolli. Revisione conserva atleta/protocollo e può correggere un record riferito ad archivio storico.
- **TD-77 / REPORT-05:** campi custom nei PDF/Markdown del singolo e dell’archivio, CSV esteso long-form tipizzato e backup; metriche numeriche custom in grafici/medie/mediane, separate per protocollo e identità del campo.
- **TD-78 / QA-04:** corpus sintetico completo su due società, 24 profili, tre stagioni, 192 record test, gruppi/anni, antropometria, FIT/CSV, gas/lattato/recupero, zone a 7, metodi distinti, revisioni e dati mancanti. Fixture errate separate, oracoli numerici indipendenti, repliche Admin/Viewer, revoca, backup/recupero SOLO DEMO e conflitto offline da esercitare. [Matrice dei casi](DATI_SINTETICI.md).

Non inclusi: codice/formule caricate dall’utente, import generico di schemi da CSV long-form, certificazione scientifica dei metodi custom, provider reali o nuova build Android/Linux. Per ripristino fedele dei protocolli custom usare il backup. La qualifica scientifica e la verifica dei dispositivi rimangono distinte dai test del software.

## 0.7 / architettura 1.5 - implementazione richiesta il 18 ottobre 2026

- **TD-68 / CLOUD-04:** implementati i tre adapter API Drive/Dropbox/OneDrive oltre a WebDAV, UI avanzata con destinazione, registrazione OAuth, stato/collegamento/scollegamento, token OS e callback desktop. Shared backend e sorgenti native Android: PKCE per Dropbox/OneDrive, autorizzazione Google Play services per Drive, rinnovo e background sui trasporti diretti. Test simulati presenti; APK e collaudo Android non eseguiti. Restano registrazioni OAuth della distribuzione, consenso/verifica provider e test reali con due account. [Guida e contratto](CONFIGURARE_LA_SINCRONIZZAZIONE.md).
- **TD-69 / SYNC-02:** predisposizione servizio dedicato implementata come adapter/client HTTPS v1, selezionabile nella UI. Server, hosting, account del relay, amministrazione e deployment rimangono successivi; nessun obbligo di backend Fuorigiri per usare i quattro provider.
- **TD-70 / ANA-01:** Sprint breve (default 6 s), Wingate 30 s, Wingate 15 s implementati in protocolli versionati e flussi manuale/tracciato. Carico, dispositivo, partenza, posizione, riscaldamento e finestre espliciti. Nessuna equivalenza universale fra famiglie, finestre, strumenti o risultati dichiarati/calcolati.
- **TD-71 / ANA-02:** import test_anaerobico con schema storico, preview/commit atomico e annullamento lotto; ANA-15-070 confermato dall’utente come 15 s e 0,70 N·m/kg. Dati mancanti e peso derivato conservati; lavoro/media incoerenti segnalati. Formula indice W/s, dispositivo/partenza/finestre storici non verificati. Nessun CSV privato distribuito.
- **TD-72 / ANA-03:** integrali temporali, picco con finestra, migliori 1/5 s, media completa, lavoro osservato, potenza finale, calo percentuale e pendenza separati, FC/cadenza, W/kg e qualità. Snapshot di metodo e chiave comparabilità conservativa. Revisione delle prove nuove con motivo e controllo concorrenza.
- **TD-73 / UI-24 / REPORT-04:** sezione anaerobici, grafico del singolo test, metriche negli storici e nel profilo atleta, aggregazioni/medie/mediane separate, CSV base/esteso, PDF/Markdown e report società/gruppo/anno/atleta con sezioni proprie. Tre FIT sintetici e documentazione di prova inclusi. [Metodi e limiti](TEST_ANAEROBICI.md).

I precedenti step di validazione/distribuzione 1-6 non vengono considerati completati da queste funzionalità. Restano da affrontare quando l’utente dispone di ambienti e corpus: collaudo scientifico esterno, provider reali, PC pulito, Fedora e Android. Per l’anaerobico: verificare le formule/dispositivo dello storico, corpus reale e ripetibilità; acquisizione/controllo ergometro e modelli fra protocolli restano sviluppi ulteriori, senza inferenze automatiche.

## Chiarimento cloud Android — 18 ottobre 2026

**TD-67 / CLOUD-03:** Android deve supportare sincronizzazione diretta tramite **WebDAV, Google Drive, Dropbox e OneDrive**. OneDrive passa da candidato a requisito del prodotto; Drive/Dropbox restano requisiti da implementare. La sincronizzazione cartella dei client desktop non soddisfa da sola il requisito Android. Stato reale 0.6: cartella/WebDAV nel codice, nessun adapter API Drive/Dropbox/OneDrive; nessun APK collaudato. Le build Linux/Android rimangono rimandate come richiesto, non riattivate da questo chiarimento.

Mantenere un solo protocollo di scambio/revisioni/conflitti, con adapter distinti per provider e autenticazione nativa. Ogni società sceglie una destinazione condivisa; non promettere replica simultanea fra provider diversi. Accettazione per ciascun provider: due account distinti sulla stessa società, due dispositivi, permessi effettivi, rinnovo/revoca token, coda offline, allegati, duplicati e conflitti. Un test con un solo account non dimostra collaborazione fra operatori.

Per una prima sincronizzazione desktop/mobile contenendo il lavoro di integrazione, privilegiare il collaudo WebDAV già presente con un servizio Nextcloud gestito; un server remoto è compatibile con il lavoro locale offline. Un futuro servizio di sincronizzazione dedicato è un’alternativa architetturale da valutare, non una sostituzione già approvata dell’archivio locale o delle integrazioni richieste.

## Software 0.6 / architettura 1.4 — sincronizzazione, distribuzione e avvio Android

Consegna concordata: Windows e sorgenti; build Linux/Android rimandate dall’utente il 18 ottobre 2026. Nessuna pipeline remota avviata o release pubblicata.

- **TD-63 / SYNC-01 / UI-22:** trasporti cartella/WebDAV comuni, credenziali OS senza fallback in chiaro, retry per oggetto, pubblicazione condizionale/rilettura, controlli firmati immutabili, registro operativo e gestione esplicita degli errori. Implementato; regressioni/server WebDAV locale verificati. Collaudo Nextcloud reale e tre piattaforme ancora aperto.
- **TD-64 / SYNC-02:** rotazione della chiave del canale con journal e avviso firmato, inviti rinnovati e recupero accessi aggiornato. Implementato e testata l’interruzione; upgrade di tutti i client alla 0.6 richiesto. Non cancella dati già ricevuti né recupera automaticamente modifiche non inviate da autori revocati.
- **TD-65 / DIST-01/02:** utente finale senza Python/Node/Qt da installare: installer Windows per utente con bundle completo; Flatpak con runtime per Fedora e distribuzione offline con runtime separatamente inclusi. Installer e pipeline sorgente aggiunti; prove su OS puliti, build Fedora, firma prodotto e completamento degli avvisi di licenza prima del rilascio.
- **TD-66 / UI-23:** icona minimale Fuorigiri in SVG/PNG/ICO e vettore Android, usata da installer/eseguibile/finestra/launcher/testata/favicon. Il logo originale della società e l’attribuzione fissa restano invariati nei footer.
- **TD-57 / AND-01–05:** dopo il consolidamento desktop, avviata shell Android e bridge al medesimo backend; SAF/Keystore/WorkManager/layout touch nel sorgente. Contratto testato su Windows, non dispositivo. Gate aperto su wheel native aggiornate, builder Linux/macOS, SDK/JDK/Gradle, APK e collaudo fisico. Non chiudere il requisito con il solo sorgente o con i test ASGI su PC.

Dettagli e limiti: [consolidamento 0.6](DISTRIBUZIONE.md), [Android attuale](ANDROID.md). Nessuna modifica alle formule scientifiche o agli storici in questa fase. Dopo accettazione Android restano nell’ordine Sprint breve → Wingate 30 s → Wingate 15 s. Drive/Dropbox API, compattazione dei canali grandi, rotazione dell’autorità (distinta dalla chiave del canale), audit esterno e collaudo delle librerie native rimangono requisiti aperti.

## Software 0.5 / architettura 1.3 — incrementale e report gerarchici

Autorizzati gli step 1–4 della lista operativa nel messaggio: preset/migrazioni, motore, GUI/FIT/report e metodi specialistici, scegliendo i metodi con riferimento scientifico quando l’utente non ne dispone. [Implementazione, formule, fonti e limiti](archivio/IMPLEMENTAZIONE_INCREMENTALE_05.md).

| ID | Requisito | Stato |
|---|---|---|
| TD-60 / SCI-01 | Scegliere metodi incrementali basati su fonti scientifiche, senza attendere formule proprie dell’utente e senza inventare un consenso unico. | **Implementato**: step costanti, finestre versionate, rampe/discontinui descrittivi, lattato lineare/Dmax/Dmax modificato, VO2peak, grafici gas e marker ventilatori, ripetibilità. Stime esplorative/valori dichiarati distinti; validazione fisiologica esterna non dichiarata. |
| TD-61 / UI-20 | Report completo di società ispirato all’allegato, con aggregazioni e grafici; gruppo, gruppo per anno/stagione e atleta con storico come viste dello stesso modello. | **Implementato**: PDF/MD, copertura, aggregazioni, schede e misure, fonti, viste equivalenti e avvertenze accorpate, logo/credito fissi. Nessuna importazione dei dati personali allegati. Motori anaerobici restano nella fase prevista. |
| TD-62 / UI-21 | Rendere operativi i preset e le correzioni riproducibili nell’interfaccia e nei report. | **Implementato**: schema 3 con copia pre-migrazione, preset immutabili, metadati/hash, nessun ricalcolo legacy, selezione sessione FIT, correzione duplicati con motivo, marker/esclusioni, condizioni, import gas e report specialistici. |

Stato INC aggiornato: INC-02/03/06/07 attuati nella versione locale; INC-01 ha nuove funzioni di import ma richiede ancora corpus reale degli esportatori. INC-04 ha un metodo descrittivo esplicito, non conversione fisiologica automatica. INC-05/08/09 hanno algoritmi e UI/report, con i limiti scientifici e di validazione documentati; gas in CSV canonico e suggerimenti ventilatori da revisione esperta, non una certificazione del laboratorio. INC-10 mantiene originali/provenienza e confronti separati, ma la riconciliazione di ogni archivio reale richiede collaudo. INC-11, WebDAV e Android non sono chiusi da questa iterazione.

Le sezioni precedenti sotto conservano la cronologia e sono superate dove descrivono funzioni ora sviluppate. [Guida di prova](TESTARE_IL_PROGETTO.md).


## Architettura 1.2 — WebDAV confermato e passi successivi

**TD-59 / CLOUD-02:** supportare **WebDAV su Windows, Fedora e Android**, con la stessa semantica di pacchetti cifrati/firmati, uso offline, ruoli e conflitti. **Requisito confermato, non implementato.** Comprende configurazione URL/cartella, credenziali protette, verifica accessi, ripresa e diagnostica, migrazione dal trasporto cartella e collaudo multipiattaforma. Nextcloud proposto come primo server di riferimento, senza promettere compatibilità con qualsiasi server WebDAV. AND-04 e INC-11 includono questa accettazione.

Ordine tecnico raccomandato: interfaccia di trasporto comune → WebDAV desktop → collaudo/porting Android nella fase mobile; lo spike Drive può procedere indipendentemente. Supporto WebDAV non subordinato a OAuth o alla scelta di Google/Dropbox. [Piano operativo aggiornato](PROSSIMI_PASSI.md). Software invariato 0.4.1.


## Aggiornamento architettura 1.1 — accesso diretto alle API cloud

**TD-58 / CLOUD-01 — Verificare e progettare lo scambio tramite API ufficiali**, senza dipendenza dal client cartella su Android o dal server Fuorigiri. Ricerca completata in [SINCRONIZZAZIONE_CLOUD_API.md](archivio/SINCRONIZZAZIONE_CLOUD_API.md): Drive e Dropbox fattibili come trasporto, con permessi differenti. Proposta: spike Drive con `drive.file` e due account, adapter comune, gestione OAuth/portachiavi, poi Dropbox condiviso; OneDrive candidato; WebDAV ora confermato per desktop e Android in TD-59. **Ricerca/disegno completati; integrazioni e prove autenticate non implementate.**

Il lavoro entra in INC-11/TD-50 e AND-04, con prima verifica sul desktop prima della fase Android. UI-19 esplicita account, cartella, consenso e stato; il ruolo della società resta distinto dall’account cloud. Migrazione dal trasporto cartella da collaudare, soprattutto per file aggiunti esternamente e accesso Drive per-app. Software invariato 0.4.1.

## Aggiornamento 0.4.1 / architettura 1.0 — metodi e Android

Step 2 eseguito come **definizione**, non come implementazione dei nuovi motori: [METODI_INCREMENTALE.md](METODI_INCREMENTALE.md). Confermati durata/copertura ≥95% separati dall’aderenza e assenza di un coefficiente universale di soglia/FTHR. Finestre attuali esplicitate come convenzioni; scostamenti numerici del codice e decisioni specialistiche residue documentati. INC-01–10 restano da implementare e collaudare, INC-11 parziale.

| ID | Requisito / decisione | Stato e accettazione |
|---|---|---|
| TD-55 | Definire precisamente metodi incrementali, fonti, finestre, qualità, preset/versioni e casi limite. | **Specifica 1.0 redatta**; convenzioni costanti confermate. Varianti lattato/gas/rampa da validare prima del relativo motore. Successiva attuazione in INC-01–10; nessun ricalcolo storico automatico. |
| TD-56 | Uniformare il nome Fuorigiri in sorgenti, documenti, package, comandi, header, ambiente e distribuzione. | **Implementato**: `Fuorigiri.exe`, `dist/Fuorigiri/`, `FUORIGIRI_*`, `X-Fuorigiri-*`. Riconoscimento conservativo dei percorsi/canali preesistenti con test. |
| TD-57 | Sviluppare l’app **Android** offline first per telefoni/tablet, con società, test, storici, report e scambio interoperabile. | **Richiesto, non implementato**. AND-01–05 e UI-18 in [ANDROID.md](ANDROID.md); stack Capacitor + Python incorporato proposto, subordinato allo spike. |

Ordine aggiornato: **(1)** completare e consolidare l’incrementale desktop, predisponendo i contratti portabili; **(2)** fattibilità e sviluppo Android con collaudo offline e scambio desktop/mobile; **(3)** Sprint breve / potenza neuromuscolare, Wingate 30 s, Wingate 15 s. La fattibilità Android può iniziare durante il consolidamento; non si anticipano i nuovi motori prima della copertura incrementale. I candidati ulteriori restano distinti.


## Stato corrente 0.4 — società, ripristino e accessi

17 ottobre 2026. Implementata la prima iterazione TD-45–49: percorsi separati, anteprima/ripristino ZIP, recupero cifrato del fondatore, copia indipendente e di consultazione, prima sincronizzazione da invito anche senza dati, ruoli visibili e rinnovo con nuovo invito. Guida operativa e limiti in [SOCIETA_BACKUP_E_ACCESSI.md](SOCIETA_BACKUP_E_ACCESSI.md). TD-50 rimane parziale per audit completo/rotazione/portachiavi; INC-11 non è completato nel suo insieme. Validazione locale: 45 test, TypeScript/Vite, GUI con dati sintetici; nessun collaudo cloud remoto o Fedora dichiarato.


## Pianificazione confermata e stato aggiornato dei requisiti

Aggiornamento documentale del 17 ottobre 2026, successivo alla preview 0.3. La pianificazione iniziale era documentale; la preview 0.4 implementa ora TD-45–49 e parte di TD-50. Le altre voci rimangono acquisite e da implementare, secondo gli stati della tabella. I dettagli della copertura sono in [COPERTURA_TEST_E_ROADMAP.md](archivio/COPERTURA_TEST_E_ROADMAP.md).

Ordine confermato: completare il prodotto per i test incrementali, includendo **tutte** le lacune INC-01–11, quindi affrontare sprint breve/potenza neuromuscolare, Wingate 30 s e Wingate 15 s. Le priorità P0/P1/P2 ordinano il lavoro interno alla prima fase: non rendono facoltative le voci meno urgenti. Il supporto agli scambi gassosi durante un incrementale rientra in questa fase; gli altri test di laboratorio autonomi restano distinti.

| ID | Requisito e criterio di completamento | Stato |
|---|---|---|
| TD-45 | Separare in Gestisci società le azioni **Crea nuova società**, **Collega tramite invito** e **Ripristina da backup**, spiegando file richiesto, risultato e passaggio successivo. La password dell'invito non deve sembrare necessaria per creare una società. | **Implementato 0.4**: tre percorsi separati, spiegazioni e selezione automatica dopo l’operazione. |
| TD-46 | Ripristinare un backup dati ZIP in un archivio locale, con anteprima società/contenuto, verifica formato/versione/integrità, gestione ID già presenti, destinazione isolata e registrazione nel selettore Società. Nessuna sovrascrittura silenziosa; errore o annullamento non devono lasciare un archivio parziale. | **Implementato 0.4**: anteprima, manifest/checksum, SQLite ricostruito in cartella temporanea, copie di consultazione/indipendenti e recupero originale. ID già presenti e cartelle occupate rifiutati; rollback verificato. |
| TD-47 | Distinguere **recupero dei dati** da **recupero degli accessi e del fondatore**. Un backup dati non concede privilegi di amministrazione. Prevedere un percorso protetto per salvare/ripristinare l'identità e le credenziali necessarie, con spiegazione dei limiti se mancano. Documentare il passaggio a un nuovo PC e il recupero dopo perdita del dispositivo. | **Implementato 0.4**: JSON di recupero del fondatore cifrato con password, distinto dallo ZIP dati; firme verificate prima del recupero. Senza credenziali: consultazione o copia indipendente, nessun privilegio originale. Portachiavi e trasferimento esclusivo dell’autorità restano INC-11. |
| TD-48 | Completare la prima associazione di una società: dopo l'invito mostrare la società anche se ancora senza dati, il proprio ruolo, la configurazione della cartella condivisa e l'azione **Acquisisci dati / Prima sincronizzazione**. Gestire cartella offline, vuota o non valida e operazione ripetuta senza duplicati. | **Corretto 0.4**: onboarding della società collegata ma vuota, azione di prima sincronizzazione accessibile anche al visualizzatore, errori e ultimo scambio visibili; GUI e API collaudate su archivi isolati. |
| TD-49 | Rendere chiari e gestibili **Fondatore**, **Admin dati**, **Visualizzatore** e dispositivo associato. Mostrare ruolo corrente, operatori/dispositivi, stato degli inviti e azioni consentite; distinguere identità locale da login e password d'invito. Definire un flusso tracciato di rinnovo/cambio ruolo senza modifiche manuali ai file. Verificare permessi in GUI, API e dati sincronizzati. | **Implementato 0.4 per identità operatore/dispositivo**: badge corrente, elenco pubblico firmato, spiegazione dei ruoli e rinnovo/cambio ruolo tramite sostituzione e applicazione dell’invito sulla stessa copia locale. Accettazione remota non dedotta. Non è richiesto implicitamente un servizio di account online. |
| TD-50 | Esplicitare effetto e limiti della revoca offline: ultimo scambio, propagazione ai dispositivi, operazioni rifiutate e dati già scaricati. Integrare audit, rinnovo/rotazione credenziali e percorso di recupero coerenti con INC-11. | **Parziale 0.4**: revoca propagata, ultimo scambio e limiti visibili; preservati solo gli eventi già acquisiti e fissati per hash alla revoca. Rinnovo e recupero presenti. Audit storico completo, rotazione del canale e portachiavi ancora INC-11; nessuna cancellazione delle copie già ricevute. |
| TD-51 | Implementare e verificare **tutte le lacune INC-01–11** della copertura incrementale: file reali, qualità/aderenza, selezione temporale, rampe/discontinui, lattato, contesto, finestre FC, gas, ripetibilità, riconciliazione storica e consolidamento operativo/distributivo. | **Da implementare e validare**; elenco completo e criteri per ciascuna voce nella roadmap. Non basta documentare le formule o aggiungere campi. |
| TD-52 | Dopo il completamento della fase incrementale, sviluppare e collaudare **Sprint breve / potenza neuromuscolare**, con protocollo e metodo versionati, dati/qualità, metriche di potenza breve, report e storici dedicati. | **Pianificato, non implementato**. Durata e modalità esecutive da specificare prima del motore; 6 s è un esempio, non un default già approvato. |
| TD-53 | Nella fase successiva sviluppare e collaudare **Wingate 30 s**, con carico/dispositivo, delimitazione dello sforzo, metriche/metodo dichiarati, import manuale o con tracciato, report e confronti coerenti. | **Pianificato, non implementato**. Sprint ripetuti restano un'estensione distinta, non automaticamente inclusa. |
| TD-54 | Nella stessa fase sviluppare e collaudare **Wingate 15 s**, come protocollo distinto già usato in passato dalla società, con ricostruzione documentata del metodo storico e possibilità di archiviare risultati incompleti senza inventare i campioni. | **Pianificato, non implementato**. Acquisire durata effettiva, carico, modalità di partenza, dispositivo, formule e formato dei referti storici. Non estrapolare 15 s in 30 s e non aggregare automaticamente i due protocolli. |

La scelta dei tre test successivi è confermata dall'utente; i dettagli dei metodi non lo sono ancora. La fase successiva è uno sviluppo con collaudo e validazione, non una promessa di equivalenza con protocolli o valori normativi esterni. Gli altri candidati della roadmap restano fuori dal perimetro confermato per quella fase.

## Stato precedente 0.3 — Fuorigiri Performance Lab

Nuovi requisiti **TD-30–44** implementati/documentati nel [registro della revisione 0.3](archivio/REVISIONE_FUORIGIRI_03.md), con scelte **UI-11–16**, contratto CSV e criteri di accettazione. La collocazione della gestione società è presente, ma il percorso completo di collegamento/ripristino non lo è: TD-45–50 precisano il lavoro residuo. [Copertura e mancanze del motore](archivio/COPERTURA_TEST_E_ROADMAP.md) distingue la fase incrementale obbligatoria dai test successivi. Le sezioni 0.2 sottostanti restano storico del progetto; il nome prodotto è ora confermato.


## Stato del codice 0.2 — 17 ottobre 2026

Aggiornamento successivo all'implementazione e alla ripresa del lavoro. La tabella descrive ora il codice 0.2; le note di disegno 0.5 sottostanti restano contesto storico. [Guida di prova con GUI](TESTARE_IL_PROGETTO.md) e [verifiche](VERIFICA.md) distinguono test eseguiti e collaudi ancora necessari.

**Branding fisso:** logo incluso nel bundle e testo «Sviluppato da Luca Bontempi per Progetto Ciclismo - Rodengo Saiano A.S.D.». Nessuna personalizzazione di logo/credito per società o workspace. ZONE-01 implementato a lista dinamica, con prove a 3/5/7 zone. ANA-01 resta un'estensione candidata, non sviluppata.

## Decisioni della revisione documentale 0.5 (storico)

17 ottobre 2026, architettura **0.5**. Convenzioni funzionali accettate; dettaglio e criteri in [Storico, zone e branding](archivio/STORICO_ZONE_E_BRANDING.md). Queste note descrivevano il disegno prima dello sviluppo; lo stato corrente è nella tabella aggiornata:

- **TD-02/03:** logo di riferimento fornito; colori del file identificati. Resta da implementare il tema e verificarne la leggibilità.
- **TD-04/13/16/17:** definite nove viste HIST-01–09 dal PDF, includendo anno di categoria distinto da stagione e coorte; default per atleta accettato e modalità tutti i test per continuità con l'archivio.
- **TD-18:** riferimento storico acquisito; consente progressione prestativa e peso, ma non crescita in statura (misure assenti) o modelli di maturazione.
- **TD-19/20 e SUITE-01:** accettati isolamento per società, admin/visualizzatore e separazione DB delle app con librerie comuni.
- **TD-28:** percentuali e confini del preset FTHR/Watt Soglia confermati. Nuovo requisito **ZONE-01**: numero N di zone configurabile, anche oltre cinque, distinto per FC e potenza; editor, grafici, report ed export dinamici. Da sviluppare, con verifiche sui confini e schemi a 3/5/7 zone.
- **Estensione candidata ANA-01:** import/consultazione dei risultati anaerobici dello storico; non ancora assunta come implementazione del motore anaerobico.

Ancora aperti: formule dei riferimenti di soglia/FTP, criteri di completamento step, finestre FC, fonti dei valori medi, nome suite e resa finale del tema. Il PDF non viene importato automaticamente e non è copiato nei dati pubblici.

Revisione del 17 ottobre 2026. I 29 identificatori seguono l'ordine dei [commenti originali](archivio/COMMENTI_ORIGINALI_2026-10-17.md). Questo documento distingue **integrazione nel progetto** da **implementazione nel programma**. La revisione 0.2 include modifiche al codice; i commenti originali rimangono conservati per tracciabilità.

Stati: **presente** = funzionalità riscontrata nel codice; **parziale** = solo una parte disponibile; **da sviluppare** = requisito acquisito, non implementato; **da definire** = scelta o riferimento necessario. Il riscontro è sul codice della preview locale, non una certificazione su Windows/Fedora puliti. Riferimento principale: [architettura 0.6](../ARCHITETTURA_PROPOSTA.md).

| ID | Requisito riscritto e criterio di completamento | Stato e riscontro attuale | Disegno |
|---|---|---|---|
| TD-01 | Segnalare esplicitamente ciò che è già implementato, separando le parti di una richiesta composta. | **Presente**: stato puntuale aggiornato qui; dettagli di prova in VERIFICA.md. | §14 |
| TD-02 | Adottare i colori di Progetto Ciclismo con superfici neutre e accenti poco invasivi; mantenere leggibilità e contrasto. | **Presente**: tema neutro/blu con accento giallo; verificato visivamente. Accessibilità sistematica da consolidare. | §5.1, UI-02 |
| TD-03 | Inserire discretamente in basso logo e collegamento della società, nome Luca Bontempi e collegamento personale. | **Presente**: logo locale, link e attribuzione fissa in GUI/PDF/Markdown; non personalizzabili. | §5.1, UI-03 |
| TD-04 | Calcolare aggregati storici per gruppo, anno e gruppo/anno, indicando popolazione, filtri e dati mancanti. | **Presente**: history.py, filtri e aggregati per stagione/categoria/coorte/anno di categoria, conteggi e mancanti per metrica. | §6.1, §8.2 |
| TD-05 | Nella scheda atleta selezionare MAP o FTP, W o W/kg; aggiungere grafici di peso e statura. | **Presente**: selettori MAP/soglia/FTP, W/Wkg e grafici peso/statura. FTP assente non stimata implicitamente. | §5.1, §8.1 |
| TD-06 | Rendere disponibili italiano e inglese in interfaccia, grafici e report. | **Parziale**: selettore IT/EN, catalogo UI e titoli principali report; diagnostiche, alcuni controlli Plotly e testi secondari ancora da completare. | §5.1, UI-05 |
| TD-07 | Importare anagrafiche, test storici e antropometria da CSV con anteprima, riconciliazione ed errori per riga. | **Presente per i tre profili concordati**: anteprima, ID esterni, errori per riga e commit atomico. Mappatura interattiva arbitraria di colonne ancora assente. | §7 |
| TD-08 | Nell'import ERG riconoscere step/rampe, indicare il riscaldamento e salvare codice protocollo distinto dal nome. | **Presente**: import ERG e editor manuale con fasi, codice e nome distinti. | §7 |
| TD-09 | Archiviare atleti inattivi mantenendoli negli storici; eliminarli escludendoli dai nuovi calcoli storici. | **Presente**: active/archived/deleted, filtri e ripristino; eliminato escluso dai nuovi aggregati. | §6.1 |
| TD-10 | Archiviare o eliminare protocolli senza perdere i riferimenti dei test esistenti. | **Presente**: stati reversibili; le definizioni usate dai test restano conservate. | §6.1 |
| TD-11 | Creare e modificare protocolli dall'interfaccia, esportare ERG e pubblicare nuove versioni con differenze e motivazione. | **Presente**: editor tabellare, nuove versioni con genitore/motivo, export ERG e definizione JSON. Confronto grafico delle differenze ancora da sviluppare. | §7 |
| TD-12 | Ordinare le tabelle per ogni colonna di dati, con indicatore del verso e comportamento coerente per valori mancanti. | **Presente**: SortableTable e DataTable con ordinamento interattivo tipizzato e indicatori; colonne di azioni escluse. | §5.1, UI-06 |
| TD-13 | Mostrare un gruppo stabile, per esempio Allievi, con sottogruppi per anno/stagione. | **Presente**: categoria padre, stagioni figlie e visualizzazione gerarchica; anno di categoria nelle appartenenze. | §6.1 |
| TD-14 | Modificare il profilo atleta dalla UI e inserire manualmente rilevazioni antropometriche datate. | **Presente**: modifica profilo dalla UI e inserimento antropometrico datato. | §5, §6 |
| TD-15 | Nell'import FIT o CSV raccogliere lattato, coefficienti, FC, antropometria e altri dati mancanti; proporre le ultime rilevazioni e consentire correzioni successive. | **Presente**: FIT/CSV, osservazioni manuali, proposta storica/stimata e revisione. Nessuna formula lattato→soglia non concordata. | §7, §8.1 |
| TD-16 | Esportare MD/PDF dello storico atleta, categoria e categoria/anno, con grafici, filtri e criteri statistici. | **Presente**: MD/PDF degli aggregati e dell’atleta filtrato; manifest con revisioni sorgente e artefatti conservati. | §9.1 |
| TD-17 | Confrontare gruppi su una stagione o sullo storico con criteri espliciti di confrontabilità. | **Presente**: viste per gruppi/stagioni, popolazioni esplicite e confronto appaiato per stesso protocollo/fonte. | §8.2 |
| TD-18 | Calcolare statistiche di crescita antropometrica e progressione prestativa, distinguendole. | **Presente per statistiche descrittive**: delta peso/statura, giorni e annualizzazione; delta prestativi. Maturazione/PHV e benchmark richiedono specifiche ulteriori. | §8.2 |
| TD-19 | Configurare percorsi locali e cartelle di scambio distinti per società, condivisibili con collaboratori diversi. | **Presente nei nuovi workspace**: percorsi, DB, originali e canali separati. Archivio precedente mantenuto, migrazione automatica non implementata. | §10.1 |
| TD-20 | Gestire operatori admin e visualizzatori per società, applicando i permessi anche alle API e ai dati ricevuti. | **Presente in forma operatore/dispositivo**: inviti cifrati, admin/visualizzatore, firme e controlli API/sync. Fondatore gestisce inviti/revoche; portachiavi e recupero guidato ancora assenti. | §10.3 |
| TD-21 | Registrare FC a 60, 90 e 120 secondi e a tempi personalizzati, specificando l'evento da cui decorrono. | **Presente**: automatico 60/90/120 s e osservazioni manuali personalizzate, con fonte distinta dal sensore; riposo pre-test separato. | §8.1 |
| TD-22 | Inserire RPE da 1 a 10, associata al test e alla scala dichiarata. | **Presente**: RPE intera 1–10, scala conservata negli input. | §8.1 |
| TD-23 | In assenza di storico proporre valori medi configurati per i dati manuali, con fonte e conferma esplicita. | **Presente come configurazione facoltativa**: preset con fonte/popolazione, proposto su scelta esplicita e marcato stimato. Nessun valore numerico universale precompilato. | §8.1 |
| TD-24 | Richiedere data di nascita facoltativa; continuare ad accettare anno soltanto o dato assente. | **Presente**: data facoltativa, solo anno o assenza; verifica coerenza data/anno. | §6.1 |
| TD-25 | Scegliere un nome legato alla cultura ciclistica italiana, mantenendo Performance Lab e prevedendo nomi coordinati per la suite. | **Confermato: Fuorigiri Performance Lab**, rinomina tecnica completata nella 0.4.1. | §15 |
| TD-26 | Usare il testo «Strumenti aperti a supporto del ciclismo giovanile» nella parte bassa dell'app. | **Presente**: motto nel footer accanto all’attribuzione fissa richiesta. | §5.1, UI-03 |
| TD-27 | Confrontare prodotti open source e commerciali e ricavarne funzionalità candidate. | **Completato come prima ricognizione**: CONFRONTO_PRODOTTI.md; nessuna estensione automatica del perimetro. | §12 |
| TD-28 | Configurare zone FC e potenza in percentuale di riferimenti selezionati e riportarle nei report. | **Presente**: preset confermato, schemi N zone per canale, riferimenti espliciti, tempi in zona e report/export dinamici; metodi dei riferimenti restano espliciti. | §8.1, §9 |
| TD-29 | Correggere input manuali e fine sforzo dopo aver visto il grafico, ricalcolando in una nuova revisione. | **Presente**: revisione da UI, ricalcolo dopo fine sforzo, motivo e protezione da aggiornamenti persi; correzione dei risultati storici tramite flusso dedicato. | §8.1 |
| SUITE-01 | Registrare decisioni UI e condividere componenti con una futura app di gestione allenamenti della stessa suite. | **Parziale**: moduli UI condivisibili, branding fisso e servizi separati; estrazione in pacchetti indipendenti e seconda app future. | §5.1, §15 |

## Ordine proposto di sviluppo (storico, prima della pianificazione TD-45–54)

1. Modello dati e migrazioni: nascita, categorie/stagioni, stati di archivio, revisioni test, osservazioni e provenienza.
2. Flussi locali: modifica atleta/test, import CSV, editor protocolli, campi manuali e configurazione dei metodi.
3. Componenti UI condivisi, branding, traduzioni e tabelle ordinabili; preparazione parallela alle schermate locali, senza duplicarne la logica.
4. Storici, aggregati, crescita descrittiva, zone e report multipli dopo validazione delle definizioni.
5. Workspace isolati, identità e autorizzazioni, sincronizzazione con conflitti e revoca; prove fra PC e account diversi.
6. Distribuzione verificata Windows/Fedora; seconda app pianificata separatamente sul nucleo condiviso.

## Riferimenti ancora necessari

- Formule per soglie e crescita avanzata: il PDF è ora esaminato, ma non le definisce. Le percentuali delle zone sono invece confermate nella specifica 0.5.
- Gerarchia accettata: stagione, anno di categoria e anno di nascita distinti; restano da configurare le regole della società.
- Preset dei valori medi, destinatari e fonte; nessun riempimento automatico dei dati reali.
- Scelta del nome della suite e palette definitiva. Il logo è ora fornito dall'utente; i colori rilevati nel file non sostituiscono una specifica di stampa.

## Come mantenere il registro

Conservare gli ID; per richieste composte aggiornare lo stato di ogni parte. Segnare «completato» solo dopo implementazione e verifica del criterio, citando file/test o versione. Registrare ogni variazione significativa nel [changelog](../CHANGELOG.md), con motivazione, ID coinvolti e distinzione fra progetto e software.


## Dettaglio test: visibilità dei tracciati — 18 ottobre 2026

- [x] Grafico dei campioni FIT/CSV in cima al dettaglio incrementale, anaerobico e custom, con potenza, FC e cadenza sovrapposte su un unico asse temporale, mantenendo scale e unità indipendenti.
- [x] Canali opzionali con unità esplicite: velocità, temperatura, quota; lattato come osservazioni puntuali nel tempo. Restano disponibili i grafici specialistici gas/lattato-carico.
- [x] Distinzione e filtro tracciato/riepilogo nello storico; spiegazione nei test senza campioni, nessuna ricostruzione da medie/massimi o interpolazione delle lacune.
- [x] Recupero dei campioni dall'oggetto del tracciato quando non inclusi nel record, senza ricalcoli automatici. Guida ed esempi in TESTARE_IL_PROGETTO.md.


## Grafici sovrapposti e confronti leggibili — 18 ottobre 2026

- [x] Un solo grafico temporale per potenza/FC/cadenza e lattato misurato, scale fisiche indipendenti, selettore per i canali aggiuntivi. Nessuna normalizzazione implicita delle grandezze.
- [x] Storici: una curva per serie omogenea, non una voce di legenda per aggregato. Esclusione delle serie prive di valori per la metrica scelta, una sola serie iniziale e selezione esplicita di massimo quattro.
- [x] Identità delle serie basata sulle separazioni esistenti del backend: protocollo/versione, metodo/condizioni/schema e origine soglia. Affiancamento descrittivo fra protocolli, senza aggregarli né dichiarare equivalenze automatiche.
- [x] Metrica e protocollo prima dei filtri secondari; legenda breve, metodi nella chiave, tabella riferita alle serie visualizzate, zero/null distinti. Esportazioni complete dell'archivio filtrato chiaramente separate dalla selezione interattiva.
- [x] Modelli grafici verificati con 12 test Node e GUI sul corpus completo, senza rigenerazione dei dati.


## Lattato configurabile e chiarimento Android — 18 ottobre 2026

- [x] Livelli di lattato configurabili per prova, default 2/3/4 mmol/L: interpolazione lineare locale W, W/kg e FC, senza estrapolazione o equivalenze automatiche con soglie fisiologiche.
- [x] FC da finestra finale dello step completo costante e copertura del preset; bpm indisponibili se mancano step/FC validi. Metodi e prelievi di supporto salvati; vecchie revisioni preservate e metodi distinti negli storici.
- [x] GUI di configurazione/risultati e grafici, metriche storiche dinamiche per livelli decimali, MD/PDF e CSV esteso, mantenendo lo standard CSV storico.
- [x] Verifica numerica, casi ambigui/mancanti e report; PDF renderizzato e ispezionato, cache aggiornata per il nuovo renderer.
- [x] Chiarimento Android: Kotlin già presente nella shell/credenziali/worker; Python incorporato con Chaquopy per riuso, ASGI in-process senza listener HTTP. Decisione e limiti descritti in ANDROID.md.
- [ ] Build e collaudo Android su dispositivo fisico: restano rinviati come concordato; toolchain e wheel native non ancora disponibili. Confermare compatibilità dipendenze/ABI, prestazioni e ciclo di vita prima di dichiarare il prodotto Android pronto.


## Osservazioni manuali acquisite — 19 ottobre 2026

Le 11 osservazioni originali sono conservate in [COMMENTI_ORIGINALI_2026-10-19.md](archivio/COMMENTI_ORIGINALI_2026-10-19.md). Analisi, dipendenze, fonti e criteri di accettazione: [ANALISI_TODO_MANUALI_2026-10-19.md](archivio/ANALISI_TODO_MANUALI_2026-10-19.md). I 15 requisiti sotto sono stati attuati nei sorgenti con gli stati puntuali aggiornati. L’analisi originale resta storica; metodi effettivi in MATURAZIONE.md. Nessuna implementazione equivale a validazione scientifica esterna o rilascio di un nuovo installer.

| ID | Requisito normalizzato | Stato, priorità e accettazione |
|---|---|---|
| TD-83 / UI-27 | Avviare «Correggi test» con un pulsante esplicito, anziché aprire il modulo dentro una sezione espandibile. Uniformare incrementali, anaerobici e custom. | **Implementato e verificato localmente.** Editor dedicato con conferma/annullamento, motivo e nuova revisione; permessi e protezione da modifiche concorrenti preservati. |
| TD-84 / UI-28 | Collocare i campi personalizzati in coda al modulo e alla scheda test, prima delle azioni finali. | **Implementato e verificato localmente.** Sezione riconoscibile e coerente nelle famiglie; campi standard prioritari, validazione e valori conservati. |
| TD-85 / UI-29 | Inserire in fondo a ogni pagina un glossario contestuale per acronimi e termini tecnici effettivamente usati. | **Implementato e verificato localmente.** Definizioni/unità/origine dei valori, IT/EN, accessibile anche da tastiera; nessun glossario vuoto o enciclopedia ripetuta. |
| TD-86 / UI-30 | Dare a potenza di soglia e FTHR pari evidenza rispetto alla MAP e affiancarle alle zone. Riordinare le sezioni del dettaglio. | **Implementato e verificato localmente.** Riferimenti distinti, fonte e indisponibilità visibili; zone legate al riferimento esatto. Ordine proposto nell'analisi, adattato alla famiglia di test. |
| TD-87 / SCI-02 | Mostrare subito sotto ogni soglia il metodo e l'eventuale coefficiente realmente applicato. | **Implementato nella GUI:** fonte, base/coefficiente effettivo e risultato accanto alle zone. Nessun coefficiente automatico; livelli lattato distinti dalle soglie fisiologiche. |
| TD-88 / LEGAL-01 | Esporre insieme alla licenza l'assenza di garanzia e i limiti, compreso il rischio di perdita dati. | **Implementato:** avvisi persistenti, pannello licenza/garanzia/backup e testi GPL/dipendenze originali. Revisione giuridica del distributore ancora necessaria; nessuna esenzione assoluta dichiarata. |
| TD-89 / UI-31 | Rendere semplice impostare i tempi guardando il grafico: minuti leggibili e secondi esatti coerenti nei campi. | **Implementato e verificato:** TimeInput secondi/mm:ss, hover in secondi, marker e selezione per incrementali/custom; inizio anaerobico con durata del protocollo. 23:45 = 1.425 s; nessuna nuova revisione al solo click. |
| TD-90 / UI-32 | Spiegare lo scopo del grafico lattato-carico e collegarlo chiaramente a watt e FC ai livelli richiesti. | **Implementato e verificato:** spiegazione W–mmol/L, livello e punto selezionabili, guide grafiche e riga evidenziata con W/W/kg/FC. Tracciato temporale distinto; nessuna nuova equazione o estrapolazione. |
| TD-91 / UI-33 | Mantenere sempre raggiungibile la chiusura del dettaglio test durante lo scorrimento. | **Implementato e verificato localmente.** Testata con X persistente, nome accessibile, Esc e gestione focus; nessuna perdita silenziosa di modifiche, nessuna trasparenza verso la lista sottostante. |
| TD-92 / CLOUD-05 | Rendere comprensibili disponibilità e prerequisiti di «Collega account» per Drive/Dropbox/OneDrive. | **Implementato per stati/prerequisiti:** comando disabilitato con spiegazione quando incompleto, fallback browser e distinzione token/accesso destinazione. L’ultimo accesso verificato è vincolato alla connessione. **Aperti** registrazione OAuth della distribuzione e collaudo con account reali. |
| TD-93 / MAT-01 | Estendere l'antropometria datata con dati necessari ai metodi maturativi, mantenendo facoltativi statura dei genitori, apertura braccia e lunghezza arti inferiori. | **Implementato:** modello misura additivo con qualità/precisione e misure avanzate facoltative, fonte della previsione esterna, correzione con motivo/revisione, UI/CSV/backup. Nessun dato opzionale diventa obbligatorio per una rilevazione. |
| TD-94 / MAT-02 | Calcolare e mostrare la velocità di crescita staturale (HV) e la sua storia separatamente dai risultati prestativi. | **Implementato e verificato:** HV qualificata 90–400 giorni, fonti/qualità/precisione, delta e motivi; zero mantenuto, calo statura e intervalli inadeguati non annualizzati. Regole prudenziali versionate del prodotto, non criteri diagnostici. |
| TD-95 / MAT-03 | Aggiungere metodi espliciti/versionati per maturity offset, PHV/APHV e, quando possibile, statura adulta prevista, %PAH e crescita residua. | **Implementato con perimetro esplicito:** Moore standing, Mirwald, APHV stimata e PHV quadratico longitudinale esplorativo, %PAH/residuo da previsione adulta **esterna** tracciata. Khamis–Roche automatico non incluso, tabelle corrette non verificate. Domini/SEE/limiti in MATURAZIONE.md; validazione esterna ancora aperta. |
| TD-96 / MAT-04 | Evidenziare gli indici pertinenti all'età e disponibili, conservando tutti i risultati e lo storico nella pagina atleta. | **Implementato:** fasce non sovrapposte alla data scelta, HV/PHV disponibili in evidenza e offset sotto 16 anni; tabelle di tutte le stime e snapshot precedenti sempre consultabili. Indici opzionali in area secondaria; nessuna maturazione dedotta dalla sola età. |
| TD-97 / MAT-05 | Integrare dati e analisi maturative in storico atleta, CSV esteso, report gerarchici, backup e sincronizzazione per società. | **Implementato e verificato localmente:** snapshot con input completi/metodo/hash, CSV estesi e report gerarchici da analisi conservate; backup/ripristino reale e sync firmata con visualizzatore testati. Schema storico preservato; oracoli indipendenti e corpus crescita dedicato. |

P0 = condizione di accettazione prima del rilascio della funzione; P1 = prossima revisione di usabilità/trasparenza; P2 = nuova area funzionale dopo specifica e consolidamento. La numerazione non impone l'ordine di implementazione. Sync v2, backup scalabili e separazione legacy rimangono priorità infrastrutturali già registrate; questa acquisizione non le dichiara concluse.


## 20 ottobre 2026 — riallineamento UI della suite

Implementato il consumo di `@cycling-suite/ui` 0.2.2, derivato dall'interfaccia corrente di Fuorigiri 0.10.0: shell/controlli responsive, liste/tabelle/riepiloghi, finestre con testata fissa, focus/Esc e protezione delle modifiche, tempi in secondi/mm:ss. Common è la fonte delle parti condivise; i moduli locali delegano alla libreria. Menu, contenuti e layout specifici, archivi e motori rimangono separati. Aggiornamento locale di sorgenti e dipendenza, senza nuovi installer o pubblicazioni.

## 20 ottobre 2026 — galleria dell’interfaccia

**DOC-GALLERY-01 — Implementato.** README con schermate reali delle funzionalità principali, versionate in `docs/screenshots/`, testi alternativi e didascalie; esclusivamente dati sintetici. Sette viste acquisite e ispezionate: atleti, protocolli, incrementale, Wingate, storici con aggregati, crescita/maturazione, report ed esportazioni. [Procedura e provenienza](screenshots/README.md). Accettazione continuativa: aggiornare nello stesso intervento le immagini delle schermate modificate, comprese dipendenze UI comuni; revisione prima delle release, data/versione dichiarate, nessuna credenziale o dato personale. Non è automazione periodica né collaudo di piattaforme non distribuite.
