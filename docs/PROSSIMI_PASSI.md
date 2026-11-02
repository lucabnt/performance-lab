# Prossimi passi

## Esito revisione pre-alpha — 2 novembre 2026

Prima di promuovere la preparazione precedente, risolvere il gate Pillow Android e l'audit nativo descritto in [REVISIONE_ALPHA.md](REVISIONE_ALPHA.md), poi generare un nuovo candidato con correzione backup e dipendenze aggiornate. Non riusare l'installer precedente come equivalente ai sorgenti: l'allineamento verificato prima della revisione è ora storico. Restano firma e gate operativi della checklist pilot.

Pillow: primo passo eseguito, kit sorgenti pronto; prossima azione dell'utente nella Toolbox Fedora, prima ABI x86_64 e poi ARM64. [Comandi](ANDROID_PILLOW.md). Riprendere l'integrazione dopo i log e le wheel; non avviare nuove build APK con la vecchia Pillow per dichiarare risolto il gate.

## Priorità aggiornata — preparazione prima alpha, 2 novembre 2026

Preparare la prima release alpha di Fuorigiri, verificando prima che installer e APK corrispondano ai sorgenti. Versione prodotto 0.10.0 invariata: l'identificativo del candidato distingue questa preparazione, senza dichiarare una release pubblicata. L'installer `pilot-20261101-01` contiene già il codice corrente; Android richiede una nuova build con UI-SUITE-001. Esiti effettivi e provenienza in [VERIFICA.md](VERIFICA.md).

Prima della distribuzione: firma Android stabile del titolare, installazione/aggiornamento su telefono ARM64 e Windows pulito, backup/ripristino e verifica dei flussi previsti per i tester. Qualificare provider e collaborazione reale se inclusi nel perimetro alpha; dichiarare esplicitamente le funzioni non qualificate. La [checklist pilot](COLLAUDO_PILOT.md) resta il registro di accettazione; preparare i pacchetti non completa i suoi gate. Nessuna pubblicazione automatica o generazione di chiavi.

Stato dei sorgenti **0.10.0** al **21 ottobre 2026**. Le funzioni sviluppate e le prove eseguite sono tracciate in [requisiti](REQUISITI_E_TODO.md) e [verifiche](VERIFICA.md). Il [piano precedente](archivio/PIANO_STORICO_2026-10-19.md) resta disponibile come cronologia.

Incrementale, Sprint/Wingate, protocolli custom, report gerarchici e maturazione sono già implementati con i limiti documentati: non sono attività da ricominciare. Sync v2, backup streaming v3 e separazione assistita sono stati aggiunti: [contratto](SYNC_V2_E_BACKUP.md). Il prossimo obiettivo è qualificarli con dati/ambienti reali e rendere distribuibile il prodotto attuale.

## Priorità attuale: candidato pilot Windows + Android, 21 ottobre

Candidato locale preparato; qualificare il prodotto corrente prima di nuove funzioni. [Checklist con check e verbale](COLLAUDO_PILOT.md). Windows: bundle/installer aggiornato e PC pulito; Android: release non firmato su richiesta dell’utente, [chiave e firma del titolare](FIRMA_ANDROID.md), poi telefono ARM64. Seguire con un solo provider e due account reali fra Windows/Android, backup/recupero e aggiornamento. Nessuna pubblicazione o CI remota avviata implicitamente.

Regressione locale: 201 Python passati/1 skip e 25 frontend passati; prove precedenti su emulatore e sorgenti nel registro. La checklist distingue questi risultati dai gate esterni ancora aperti. Le sezioni sotto dettagliano il lavoro residuo, non rinviano nuovamente il collaudo Android già riaperto.

## 1. Qualificare e far evolvere la sincronizzazione v2

**SYNC-V2-01 — nucleo implementato e verificato localmente.** Blocchi cifrati riutilizzabili, pagine firmate, firme originali, ricevute e checkpoint sono presenti, con attivazione esplicita e lettura v1/v2. Nessuno storico è stato cancellato.

Il seguito riguarda collaudo con due dispositivi/provider reali, misure di spazio e trasferimento su corpus più grandi e inventari remoti paginati oltre l’attuale elenco completo. Un’eventuale compattazione richiede prima una politica per recupero e dispositivi offline; non va aggiunta come pulizia automatica. [Contratto e limiti](SYNC_V2_E_BACKUP.md).

## 2. Qualificare backup grandi e migrazione legacy

**BACKUP-SCALE-01 / SYNC-MIG-01 — implementati nei sorgenti.** ZIP64 v3 streaming e separazione conservativa disponibili; verificato anche il ripristino reale di 101 MB non comprimibili. L’originale delle società estratte rimane intatto, con nuove identità e canali per le copie.

Il seguito riguarda volumi maggiori e molti file, interruzioni del processo, spazio disco insufficiente e qualificazione dei percorsi nativi mobili. L’estrazione blocca riferimenti incoerenti e non attribuibili: per gestire gli archivi legacy più problematici servirà un editor esplicito di riconciliazione con anteprima e provenienza, senza indovinare la società dei record.

## 3. Collaudo operativo e scientifico

**QA-RELEASE-01 — parziale.** Automatizzare il percorso GUI archivio vuoto → protocollo → import/manuale → correzione → report → backup/ripristino → seconda replica. Completare traduzioni IT/EN, tastiera, focus, contrasto e touch; misurare caricamento e grafici prima di ottimizzare Plotly o estrarre ulteriori flussi React.

Acquisire FIT reali autorizzati/anonimizzati da GoldenCheetah, MyWhoosh e Zwift e risultati indipendenti di riferimento. Qualificare incrementale, lattato/gas, Sprint/Wingate e modelli maturativi nei rispettivi domini. I dati sintetici verificano la logica, non l’accuratezza biologica. Khamis–Roche automatico resta eventuale: richiede fonti e tabelle corrette verificate; %PAH/residuo da previsione esterna sono già disponibili.

## 4. Connessioni reali e candidato Windows

Registrare le app OAuth della distribuzione e provare WebDAV, Drive, Dropbox e OneDrive con due account distinti, permessi della cartella, token scaduti/revocati e rete interrotta. Nessuna credenziale operativa va inclusa nella repository. Verificare anche i client cloud per il trasporto a cartella.

Ricompilare il candidato Windows dopo il consolidamento e provarlo su VM pulita: installazione senza Python/Node, aggiornamento, avvio offline, portachiavi, report, recupero e disinstallazione senza perdita di dati. Firma del prodotto quando disponibile. Registrazione provider, revisione giuridica e validazione esterna richiedono materiali/ambienti dedicati: non sono risolti dai test simulati.

## 5. Fedora e Android

**Fedora:** packaging e collaudo ancora rimandati. **Android:** APK debug e runtime verificati su emulatore; candidato release non firmato prodotto, con firma, telefono e qualifica completa ancora aperti. Non usare il rinvio storico per descrivere lo stato attuale. [Stato Android](ANDROID.md), [distribuzione](DISTRIBUZIONE.md), [pilot](COLLAUDO_PILOT.md).

## 6. Evoluzioni successive

- **Suite comune:** consolidare contratti e pacchetti versionati per Ammiraglia, mantenendo repository e dati separati. Estrarre componenti ulteriori solo dove entrambe le app condividono davvero comportamento e responsabilità.
- **Servizio dedicato:** dal contratto/client già predisposto a un backend effettivo, autenticazione, isolamento delle società, storage, operatività e distribuzione. È un’alternativa futura ai provider, non un servizio già ospitato.
- **Nuovi test candidati:** CP/W′, time trial/FTP, sprint ripetuti e submassimali. Prima definire protocolli, input, formule, confrontabilità e riferimenti; non attivare un motore dal solo nome del test. Non sono ancora impegni di implementazione prioritari.

Il lavoro immediato consigliato è il collaudo operativo del punto 3 e la qualificazione delle nuove procedure su altri volumi e due dispositivi, poi il candidato Windows del punto 4. I test operativi possono crescere in parallelo; non cambiare contemporaneamente formato di scambio e formule scientifiche.
