# Android: pratiche condivise e adozione in Fuorigiri

La guida canonica per le nuove app è `docs/ANDROID_BEST_PRACTICES.md` nella repository **cycling-suite-common**, aggiornata nello stesso intervento. [Percorso nei sorgenti comuni](https://github.com/lucabnt/cycling-suite-common/blob/main/docs/ANDROID_BEST_PRACTICES.md). Le modifiche sono locali finché non vengono committate/pubblicate dal titolare; il riferimento remoto non implica una pubblicazione eseguita dall’agente.

Il documento raccoglie: confini tra app e common, navigazione hamburger/Indietro, cronologia limitata, preferenza persistente della società, schede/paginazione/filtri, azioni e validazioni dei moduli, tastiere e tempi, insets/IME, accessibilità, file privati/SAF, offline/sync/backup, dipendenze native e gate distinti di build/runtime/dispositivo. Contiene anche i problemi realmente scoperti in Fuorigiri (sessionStorage volatile, DT_NEEDED libpython, wheel non tracciate dalla cache Gradle).

## Componenti e responsabilità

`@cycling-suite/ui` **0.2.6** fornisce RecordCards con paginazione controllabile, CollapsibleFilters, FormActions, ChartFrame, LoadingState e gli adattamenti Android di Dialog. I consumatori installano il tarball versionato; nessuna dipendenza runtime dal clone fratello. Menu, etichette, struttura dei record, criteri dei filtri, route e scelta della persistenza rimangono del prodotto. Questa consegna aggiorna soltanto Fuorigiri: nessuna pubblicazione o aggiornamento automatico di Ammiraglia.

Fuorigiri conserva in localStorage soltanto workspace/organization, come coppia, per Android; sessionStorage rimane lo specchio delle richieste correnti. Il bootstrap verifica l’inventario prima di aprire i dati. Cronologia di schermate e stato degli elenchi rimangono in memoria della sessione, con scroll e pagina; non si conservano copie di dati dei test nella cronologia.

## Applicazione e verifica

TD-98 definisce menu/Info; TD-99 elenchi, moduli e Indietro; TD-100 ultima società; TD-101 guida per le app future. [Collaudo](TESTARE_IL_PROGETTO.md) e [risultati effettivi](VERIFICA.md). Le raccomandazioni sul caricamento differito dei grafici, tutte le schermate analitiche mobili, TalkBack, telefono ARM64 e tastiere su configurazioni diverse non diventano complete per la sola disponibilità della guida.

## Adozione aggiuntiva — TD-102–104

Hamburger a sinistra, ritorno soltanto dal sistema. Contesto persistente società/sezione/ruolo, testo e focus accessibili. Spaziature moderate e bersagli touch conservati. Scorri pagina è il default; comandi sotto il grafico, Esplora/Zoom espliciti e un Back per disattivarli prima di chiudere il dettaglio. Cancel del dialogo figlio non deve raggiungere il genitore. Plotly locale differito; fasi d’avvio reali, riprova senza reset e alternativa tabellare paginata alle figure. La cattura delle gesture appartiene alla politica del grafico nel prodotto, non a ogni superficie grafica del common.

TD-105: Vista ampia richiede landscape al contenitore nativo e rilascia la richiesta alla chiusura/smontaggio/reload, ripristinando la politica precedente. Conservare il test e ridimensionare la figura; non ruotare il DOM con CSS. Back da Esplora disattiva solo il modo; la chiusura della vista ripristina l’orientamento.

TD-106–107 (UI comune 0.2.7): marchio orizzontale con icona a sinistra; Dialog/ChartFrame fullscreen e FloatingPanel riutilizzabili. Il contenitore nativo conserva/ripristina visibilità e comportamento delle barre. Niente fascia permanente per il titolo: nome accessibile conservato, X e pannello flottanti; tabella e istruzioni disponibili nel pannello.

Correzione TD-106, 21 ottobre 2026: testata Android con nome/tagline allineati a destra, prima dell’icona che sta sul lato destro. Gruppo a destra e hamburger a sinistra. Variante brand-end nel common UI 0.2.8; sostituisce l’indicazione precedente sul lato dell’icona nella testata, senza cambiare bootstrap centrati o sidebar desktop.
