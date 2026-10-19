# Prossimi passi

Stato dei sorgenti al **19 ottobre 2026**. Le funzioni sviluppate e le prove eseguite sono tracciate in [requisiti](REQUISITI_E_TODO.md) e [verifiche](VERIFICA.md). Il [piano precedente](archivio/PIANO_STORICO_2026-10-19.md) resta disponibile come cronologia.

Incrementale, Sprint/Wingate, protocolli custom, report gerarchici e maturazione sono già implementati con i limiti documentati: non sono attività da ricominciare. Il prossimo obiettivo è rendere affidabile e distribuibile il prodotto attuale.

## 1. Formato di sincronizzazione v2

**SYNC-V2-01 — da implementare.** Separare campioni e allegati dai record, cifrare e caricare gli oggetti una sola volta, introdurre manifest/cursori e uno snapshot iniziale per nuovi dispositivi. Definire indirizzamento degli oggetti e deduplicazione senza esporre dati oltre il canale autorizzato.

Procedere con specifica del formato e migrazione compatibile v1/v2, poi trasporto locale e test di interruzione, replica e conflitto, infine adapter remoti. Conservare gli originali; nessuna pulizia delle revisioni prima di una politica per recupero e dispositivi rimasti offline. **Completato quando:** stessi dati e cronologia dopo migrazione/ripristino, trasferimenti riprendibili e crescita dello spazio misurata su corpus grande. [Dimensioni e limiti](SYNC_DIMENSIONI_E_SCALABILITA.md).

## 2. Backup scalabili e archivi legacy

**BACKUP-SCALE-01 / SYNC-MIG-01 — da implementare.** Export/import in streaming o in parti, verifica integrità e recupero oltre i limiti attuali; separazione assistita delle società dai vecchi archivi multipli, con dipendenze e revisioni complete, nuove identità/chiavi e originale conservato.

Sviluppare insieme al contratto v2, mantenendo il ripristino dei backup precedenti. **Completato quando:** ripristino reale di un archivio grande, gestione degli errori senza import parziale e isolamento effettivo delle società estratte. Non basta alzare i limiti in memoria.

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

Il lavoro immediato consigliato è il punto 1, con il disegno dei backup del punto 2. I test operativi possono crescere in parallelo; non cambiare contemporaneamente formato di scambio e formule scientifiche.
