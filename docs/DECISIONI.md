# Decisioni e stato dell'implementazione

## Architettura 1.2 — CLOUD-02 / TD-59

L’utente conferma **WebDAV per desktop e mobile Android**. Superata la classificazione come candidato nella revisione 1.1. Il contratto di scambio rimane comune ai trasporti e indipendente dai provider proprietari. Proposto WebDAV come primo adapter remoto dopo il refactoring della cartella locale; Nextcloud come server iniziale di collaudo, senza presumerne adozione o disponibilità di credenziali. Riferimenti: [specifica cloud](SINCRONIZZAZIONE_CLOUD_API.md), [prossimi passi](PROSSIMI_PASSI.md). Requisito acquisito, sviluppo non ancora eseguito.


## Architettura 1.1 — CLOUD-01 / UI-19

Verificate le API ufficiali in [SINCRONIZZAZIONE_CLOUD_API.md](SINCRONIZZAZIONE_CLOUD_API.md). Corretto il disegno Android: trasporto API diretto come obiettivo ordinario, cartella locale e SAF/import-export come alternative, nessun server Fuorigiri necessario per principio. Drive primo adapter proposto; `drive.file` richiede uno spike inter-account e con file provenienti da client esterno. Dropbox App Folder non soddisfa una società con account distinti: per cartella condivisa considerare Full Dropbox e consenso dichiarato. OneDrive e WebDAV documentati come candidati.

Separati consenso cloud, condivisione della cartella e autorizzazione/ruolo Fuorigiri. UI-19 e TD-58 acquisiscono onboarding provider, token locali protetti, migrazione, stato e prove. Nessun account collegato o provider implementato in questa verifica; software resta 0.4.1. La scelta del primo adapter è una raccomandazione, non un consenso già dato a scope ampi.

## Architettura 1.0 / software 0.4.1 — step 2 e portabilità

**MET-01:** specifica [METODI_INCREMENTALE](METODI_INCREMENTALE.md) con algoritmi, unità, coperture, null, fonti, finestre e vettori di accettazione. Conferma utente: completezza temporale/copertura separata dall’aderenza e nessun coefficiente universale dalla MAP a soglia/FTHR. Il motore corrente non viene reinterpretato né sostituito in questo step documentale. Prima dell’implementazione specialistica restano da scegliere varianti lattato, gas e rampe.

**NAME-01:** richiesta di rinomina tecnica completa; superata la compatibilità dei vecchi nomi pubblici UI-16. Package/comandi/header/configurazione/distribuzione ora Fuorigiri; modulo generico `cycling_test` invariato. Vecchi archivi e canali su disco riconosciuti per non perdere dati: nessun rename automatico di directory con percorsi assoluti, nessuna rigenerazione di identità o chiavi.

**MOB-01 / UI-18:** Android acquisito come sviluppo, dopo completamento incrementale/consolidamento desktop e prima dei motori sprint/Wingate. Raccomandazione da verificare: React/Capacitor + bridge Kotlin + nucleo Python incorporato, archivio privato e trasporto astratto; desktop FastAPI/Qt rimane confermato. API cloud o SAF Android da provare, nessuna presunzione di cartelle locali Drive identiche al PC. [Alternative, dipendenze e accettazione](ANDROID.md).


## Software 0.4 / architettura 0.9 — ripristino e accessi

Adottati e implementati UI-17/REC-01: operazioni società separate, bootstrap prima dei dati, recupero credenziali cifrato distinto dal backup ZIP, copie di consultazione e indipendenti senza privilegi della società originale. Rinnovo/cambio ruolo tramite invito sostitutivo e revoca, applicato sul medesimo archivio locale; stati degli inviti dichiarati come emessi, senza presumere accettazione remota. Revoca con eventi già ricevuti fissati per hash; nessuna promessa di eliminare copie o ruotare automaticamente la chiave di lettura. [Guida operativa](SOCIETA_BACKUP_E_ACCESSI.md). TD-45–49 presenti; TD-50 e INC-11 restano parziali. I test successivi mantengono l’ordine confermato.


## Pianificazione confermata / architettura 0.8 — software invariato 0.3

Decisione dell'utente del 17 ottobre 2026: completare **tutte** le lacune incrementali INC-01–11, poi sviluppare Sprint breve / potenza neuromuscolare, Wingate 30 s e Wingate 15 s. Il 15 s è un protocollo usato in passato dalla società; la sua definizione storica va acquisita prima di scegliere formule e criteri. Gli altri test rimangono candidati; scambi gassosi nell'incrementale già inclusi nella prima fase. Dettagli e criteri in [COPERTURA_TEST_E_ROADMAP.md](COPERTURA_TEST_E_ROADMAP.md).

Registrate le lacune di gestione società: tre percorsi distinti (creazione, invito, backup), ripristino dati separato dal recupero degli accessi del fondatore, prima sincronizzazione di archivio ancora vuoto, chiarezza dei ruoli e dei dispositivi, rinnovo e revoca. TD-45–54 nel [registro requisiti](REQUISITI_E_TODO.md); scelte UI-17 e REC-01 nell'[architettura](../ARCHITETTURA_PROPOSTA.md). Aggiornamento soltanto documentale: nessuna nuova funzione o credenziale creata e nessuna equivalenza tra Wingate 15 s e 30 s assunta.

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
