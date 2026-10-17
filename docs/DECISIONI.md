# Decisioni e stato dell'implementazione

## Stato corrente software 0.3 / architettura 0.7

Nome confermato **Fuorigiri Performance Lab**. Adottate e implementate le scelte TD-30–44 e UI-11–16 del [registro 0.3](REVISIONE_FUORIGIRI_03.md), incluse acquisizione manuale, protocolli senza step, nome figlio ereditato, media/mediana e footer PDF. Gli identificatori tecnici precedenti restano compatibili. Le [mancanze e priorità dei test](COPERTURA_TEST_E_ROADMAP.md) separano capacità attuali e motori futuri. Le sezioni sottostanti conservano la cronologia 0.2.

## Stato software 0.2 / architettura 0.6

Il 17 ottobre 2026 è stata implementata la parte locale dei nuovi requisiti: revisioni, osservazioni, protocolli editabili/versionati, CSV, statistiche e report storici, workspace/ruoli e firme di scambio. Stato per ID in [REQUISITI_E_TODO.md](REQUISITI_E_TODO.md), prove e limiti nel [README](../README.md).

**Decisione successiva vincolante sul branding:** logo della società fondatrice incluso nel software e attribuzione fissa «Sviluppato da Luca Bontempi per Progetto CIclismo - Rodengo Saiano A.S.D.». Nessun override da workspace, anagrafica o impostazioni UI. Le precedenti proposte di branding configurabile sono superate.

La [guida di test con GUI](TESTARE_IL_PROGETTO.md) descrive avvio, fixture e checklist. La localizzazione IT/EN è parziale per diagnostiche e testi secondari; inviti e firme sono implementati, mentre portachiavi, recupero guidato e rotazione chiavi restano da completare. Le sezioni seguenti conservano la cronologia del disegno e degli scostamenti iniziali, senza descrivere necessariamente lo stato corrente.

## Conferme successive — 17 ottobre 2026, architettura 0.5

L'utente accetta le convenzioni funzionali proposte: categorie/stagioni, archiviazione distinta dall'eliminazione, revisioni dei test, default ultimo test valido per atleta/periodo, confronti appaiati, admin/visualizzatore per società e app autonome con componenti comuni. Un eventuale ruolo allenatore resta opzionale, non richiesto.

Ricevuti logo definitivo come riferimento e PDF storico. Valutazione delle nove viste, limiti dei dati e colori rilevati in [Storico, zone e branding](STORICO_ZONE_E_BRANDING.md). Il PDF è fonte di contesto, non istruzione a modificare l'archivio esterno.

Confermati preset FC su FTHR e potenza su Watt Soglia e confini continui: FC <81 / 81–<90 / 90–<100 / 100–105 / >105%; potenza ≤55 / >55–75 / >75–90 / >90–105 / >105%. **Numero di zone configurabile**, anche oltre cinque e diverso per FC/potenza. Le formule per ottenere soglie e criteri di step valido restano aperti. Aggiornamento documentale, nessuna funzione nuova implementata.

Aggiornamento documentale del 17 ottobre 2026: l'[architettura 0.4](../ARCHITETTURA_PROPOSTA.md) integra i commenti dell'utente. Stato puntuale e criteri nel [registro requisiti](REQUISITI_E_TODO.md); cronologia nel [changelog](../CHANGELOG.md). Le funzioni aggiunte al disegno non sono state implementate in questa revisione.

## Confermate

- Python + React/TypeScript, 16 ottobre 2026.
- Shell desktop PySide6 + Qt WebEngine, backend loopback FastAPI.
- ERG come creazione rapida di protocolli versionati e riutilizzabili.
- Società, gruppi e appartenenze storiche.
- CSV di riferimento come contratto di export, non importazione automatica di dati personali.
- Dal 17 ottobre: richiesta anche la funzionalità di import CSV di storici/antropometria e campioni di test; nessuna importazione automatica dei dati personali allegati.
- Ultimo step completo primario e interpolazione separata.
- Sincronizzazione via cartella locale gestita dal client cloud esterno.
- GPL, specificata nel progetto come GPL-3.0-or-later.

## Correzione del decoder FIT

Il decoder scelto per l'implementazione è **fitdecode (MIT)**. Lo SDK Garmin inizialmente proposto ha condizioni di licenza proprie che richiedono valutazione separata; non viene incluso nella distribuzione GPL. L'adapter resta sostituibile. Fonte: https://github.com/polyvertex/fitdecode/blob/master/LICENSE.txt

## Scostamenti iniziali dall'architettura obiettivo

La prima versione usa `sqlite3` e record JSON revisionati, non ancora ORM SQLAlchemy/Alembic. Separazione motore/API/archivio mantenuta. Non esiste ancora un meccanismo di migrazione schema: non usare come archivio operativo stabile.

I lavori API sincroni vengono eseguiti nel threadpool FastAPI; non ancora processi persistenti annullabili. Plotly è incluso localmente. La UI è attualmente in un modulo da suddividere durante il consolidamento.

Sincronizzazione: pacchetti cifrati autosufficienti contenenti modifica e allegati; outbox rappresentata dalla tabella changes. In questa fase l'unità di condivisione è l'intero archivio, non la società. Conflitti vengono conservati senza sovrascrivere il valore locale; la loro risoluzione, convergenza successiva, cancellazioni e revoca sono ancora da implementare. Feature etichettata sperimentale.

L'applicazione completa prevista dall'architettura richiede ancora le fasi di consolidamento elencate nel README. La conferma dello stack non è presentata come validazione del metodo fisiologico.

## Estensioni del disegno del 17 ottobre

Requisiti acquisiti: categorie con edizioni annuali, modifica dei dati manuali dopo il test, archiviazione/eliminazione, confronti e report storici, IT/EN, branding/crediti, zone configurabili e ruoli admin/visualizzatore per società. Le precise formule dei preset, il nome e la palette finale restano da validare.

Le decisioni UI sono mantenute **nell'architettura**, con ID UI-01–10: componenti e token comuni, shell condivisa, layout e grafici coerenti, tema configurabile e traduzioni. Per la futura app Allenamenti si propone riuso di librerie e contratti versionati, senza accesso diretto allo stesso SQLite da due applicazioni indipendenti. Nessuna seconda app è stata creata.
