# Prossimi passi

Stato dei sorgenti **0.10.0** al **20 ottobre 2026**. Le funzioni sviluppate e le prove eseguite sono tracciate in [requisiti](REQUISITI_E_TODO.md) e [verifiche](VERIFICA.md). Il [piano precedente](archivio/PIANO_STORICO_2026-10-19.md) resta disponibile come cronologia.

Incrementale, Sprint/Wingate, protocolli custom, report gerarchici e maturazione sono già implementati con i limiti documentati: non sono attività da ricominciare. Sync v2, backup streaming v3 e separazione assistita sono stati aggiunti: [contratto](SYNC_V2_E_BACKUP.md). Il prossimo obiettivo è qualificarli con dati/ambienti reali e rendere distribuibile il prodotto attuale.

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

**Build rinviate dall’utente:** riprenderle quando sarà disponibile il builder adatto. Fedora: produrre e collaudare il pacchetto con runtime. Android: wheel native aggiornate, SDK/JDK/Gradle, APK, emulatore e dispositivo fisico; verificare file, Keystore, report, lavoro in background e scambio tra mobile e desktop per tutti i trasporti previsti.

L’architettura Kotlin/React/Python e gli adapter sono nei sorgenti; non equivalgono a un’app mobile collaudata. [Stato Android](ANDROID.md), [distribuzione](DISTRIBUZIONE.md).

## 6. Evoluzioni successive

- **Suite comune:** consolidare contratti e pacchetti versionati per Ammiraglia, mantenendo repository e dati separati. Estrarre componenti ulteriori solo dove entrambe le app condividono davvero comportamento e responsabilità.
- **Servizio dedicato:** dal contratto/client già predisposto a un backend effettivo, autenticazione, isolamento delle società, storage, operatività e distribuzione. È un’alternativa futura ai provider, non un servizio già ospitato.
- **Nuovi test candidati:** CP/W′, time trial/FTP, sprint ripetuti e submassimali. Prima definire protocolli, input, formule, confrontabilità e riferimenti; non attivare un motore dal solo nome del test. Non sono ancora impegni di implementazione prioritari.

Il lavoro immediato consigliato è il collaudo operativo del punto 3 e la qualificazione delle nuove procedure su altri volumi e due dispositivi, poi il candidato Windows del punto 4. I test operativi possono crescere in parallelo; non cambiare contemporaneamente formato di scambio e formule scientifiche.
