# Prossimi passi

## Perimetro dell'alpha — 18 novembre 2026

Decisioni PERIMETRO-01 ([requisiti](REQUISITI_E_TODO.md), [analisi](analisi-alternative-2026-11-18.md)), che aggiornano l'ordine dei lavori sotto:

- Provider: per l'alpha si qualifica soltanto **WebDAV**. Google Drive, Dropbox e OneDrive sono sperimentali: nessun nuovo sviluppo, registrazione OAuth o collaudo con account reali in programma.
- Android resta nell'alpha come **app completa**; i gate rimangono quelli dei punti 1–2.
- Fuori dal piano attivo: app allenamenti (sospesa; resta il pulsante Intervals.icu) e server opzionale (sviluppo futuro da considerare, non in sviluppo).

## Alpha con Windows e Android — 13 novembre 2026

L’utente vuole Windows e Android nell’alpha. Ordine dei lavori:

1. **Fedora:** ~~ricostruire le sei wheel da radice neutra~~ **fatto il 19 novembre** ([procedura](ANDROID_WHEEL_FEDORA.md), kit `android-neutral-kit-20261119-02`): riparazione ABI3, provenienza, scanner `--strict` e APK release con scansione dei percorsi pulita; restano 4 moduli LOAD non a 16 KB (FreeType, OpenBLAS/libpng x86_64) e il runtime ARM64 su dispositivo reale (x86_64 verificato su emulatore; la traduzione ARM dell’emulatore non avvia Chaquopy, né con le wheel nuove né con le precedenti, 20 novembre).
2. **Android:** chiave del titolare ([firma](FIRMA_ANDROID.md)), `build_android.py --release` da snapshot committato, firma, prove A-04…A-08 e A-11 sul telefono. Gli utenti dell’APK debug devono fare un backup e disinstallarlo.
3. **Windows:** installare il candidato `core020-20261119-01` (19 novembre: avvisi Qt, bootloader locale WIN-AV-02, core 0.2.0) e riaprirlo con Defender attivo (WIN-AV-01/02), poi prove W-01…W-07 in Windows Sandbox. Firma Authenticode da decidere.
4. **Licenze:** decidere se allegare alla release gli archivi sorgente Qt o affidarsi ai link ufficiali.
5. **Pubblicazione:** nuovo snapshot sorgenti, allegati e `SHA256SUMS.txt` ricalcolati sullo stesso commit. Nelle note: solo WebDAV provato; Drive, Dropbox e OneDrive sperimentali; 16 KB come limite noto.

## Prima alpha pubblica — 10 novembre 2026

Usare lo snapshot sorgenti controllato e la [selezione degli allegati](DISTRIBUZIONE.md). La storia privata resta separata. Prima dei binari completare il materiale di licenza Windows e la bonifica delle wheel Android, poi ricompilare e firmare l’APK.

## Candidato corrente — 19 novembre 2026

Windows: `dist/candidates/Fuorigiri-0.10.0-core020-20261119-01/` (commit `73c562d`, solo Windows). Android: `dist/candidates/Fuorigiri-0.10.0-android-neutre-20261120-01/` (20 novembre, wheel neutre, debug di test e release non firmato da firmare). I candidati del 15 novembre e precedenti restano conservati come storici. [Checklist](COLLAUDO_PILOT.md), [prove](VERIFICA.md).

## Candidato precedente — ordine e maturazione, 9 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-ordine-maturazione-20261109-01/`: nuove build Windows/Android **0.10.0** con **UI-ORDINE-02** (cognome/nome, test e misure dal più recente in pagine indipendenti da 15) e **MAT-AVVISI-01** (stime datate decrescenti e indici antropometrici con avvisi, motore growth-maturity/2), oltre alle funzioni precedenti; UI comune **0.2.9** invariata. Installer/portabile completi, APK debug firmato per i test, release non firmato, supporto strumentale, sorgenti/wheel e **25 checksum finali verificati**. Avvio Windows, scansioni Defender attivo e controlli di contenuti/firme/allineamento riusciti. [Prove e digest](VERIFICA.md).

Nessuna pubblicazione, chiave nuova o installazione sopra dati operativi. Restano Windows pulito/aggiornamento, firma release e runtime Android/telefono, sei problemi LOAD 16 KB, provider reali e validazione esterna. La documentazione congelata nei pacchetti precede questa annotazione conclusiva.

## Candidato precedente — import-avvisi, 8 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-import-avvisi-20261108-01/`: nuove build Windows/Android **0.10.0** con avvisi CSV non bloccanti, riconoscimento duplicati e correzione dello scorrimento dei dialoghi tramite UI comune **0.2.9**, oltre alle funzioni precedenti. Installer e portabile completi, APK debug firmato per i test, release non firmato, supporto strumentale, sorgenti/wheel e **25 checksum verificati**. Smoke Windows e scansioni correnti riusciti, firme/allineamento/contenuti APK verificati. [Prove e digest](VERIFICA.md).

Nessuna pubblicazione, nuova chiave o installazione sopra dati operativi. Restano WIN-AV-01 storico, Windows pulito/aggiornamento, firma release, runtime della nuova build Android e telefono, provider reali e sei problemi LOAD 16 KB. Zipalign e smoke non sostituiscono tali gate. La documentazione congelata nei pacchetti precede questa annotazione finale.

## Candidato precedente — antro-incrementale, 8 novembre 2026

Consegna locale `dist/candidates/Fuorigiri-0.10.0-antro-incrementale-20261108-01/`: nuove build Windows/Android 0.10.0 con import CSV incrementale, altezza perineale e rapporto sulla statura nel profilo; include eliminazione/ripristino di misure e test e le funzioni precedenti. Installer/portabile completi, APK debug firmato per i test, release non firmato per il titolare, APK strumentale, sorgenti e wheel. Smoke Windows e scansioni correnti riusciti, contenuti e **25 checksum finali verificati**. [Registro e digest](VERIFICA.md). Nessuna pubblicazione o nuova chiave.

Restano Windows pulito/aggiornamento, WIN-AV-01 del candidato storico, firma release, runtime della nuova build Android e telefono, provider reali e sei problemi LOAD nativi a 16 KB. Non confondere zipalign con qualifica 16 KB; le scansioni correnti non dimostrano un falso positivo sul vecchio candidato. La documentazione congelata nei pacchetti precede questa annotazione finale.

## Consegna precedente — record-lifecycle, 8 novembre 2026

Nuovo candidato locale `dist/candidates/Fuorigiri-0.10.0-record-lifecycle-20261108-01/`, successivo a sync-intervals: include eliminazione e ripristino dagli editor di misure e test e gli aggiornamenti precedenti. Installer/portabile, debug di test, release non firmato, sorgenti e wheel in cartella nuova, senza sostituire consegne esistenti. Smoke e scansioni Windows correnti riusciti; integrità e contenuti APK verificati. [Registro](VERIFICA.md), [accettazione residua](COLLAUDO_PILOT.md). Non chiude WIN-AV-01 del vecchio candidato, Windows pulito, firma release, runtime della nuova build Android, provider reali o i sei problemi LOAD a 16 KB.

## Consegna locale aggiornata — 8 novembre 2026

Disponibile `dist/candidates/Fuorigiri-0.10.0-sync-intervals-20261107-01/`, con nuove build Windows/Android e SYNC-AUTO-01 / INT-ICU-01. Scansioni correnti e smoke Windows riusciti, firma debug/allineamento/contenuti APK verificati. Non promuovere il candidato precedente bloccato né dichiarare chiuso WIN-AV-01: restano revisione e accettazione Windows con protezioni attive. Restano firma release Android, prova runtime della nuova build, provider reali e i sei moduli non qualificati 16 KB. [Registro](VERIFICA.md), [checklist](COLLAUDO_PILOT.md).

## Blocco Windows — 7 novembre 2026

Risolvere WIN-AV-01 prima di qualificare il candidato Windows: Defender rimuove l'EXE di `windows-alpha-review-20261102-01`. [Diagnosi e criteri](WINDOWS_DEFENDER.md). Gli altri lavori Android rimangono distinti.

## Seguito operativo native e Windows — 2 novembre 2026

Auditor esteso a tutte le `.imy` (222 ELF nel candidato Pillow, stessi sei problemi), contratto simboli e kit sorgenti Fedora preparati: [guida](ANDROID_NATIVE_16KB.md). Prima azione sul builder: pydantic-core x86_64 con output nuovo e revisione del log; poi seconda ABI e i tre provider condivisi, un componente alla volta. Non aggiornare i pin finché non arrivano binari verificati. Nuovi APK dipendono da questo passaggio. Prova grafico sul telefono rimandata come concordato.

Nel frattempo regressione Python Windows completa e nuova build isolata eseguite; esiti e consegna corrente in [VERIFICA.md](VERIFICA.md). Preparazione locale distinta da Windows pulito, firma e distribuzione. Non sostituire le consegne precedenti.

Consegna Windows corrente per questa revisione: `windows-alpha-review-20261102-01`, installer/portabile/sorgenti nuovi e checksum verificati; non riusare alpha-prep come equivalente. Android attende il kit Fedora `native16k-kit-20261102-02`: prima pydantic-core x86_64 e riscontro, poi gli altri binari. Nessuna nuova firma o pubblicazione.

## Esito revisione pre-alpha — 2 novembre 2026

Prima di promuovere la preparazione precedente, risolvere il gate Pillow Android e l'audit nativo descritto in [REVISIONE_ALPHA.md](REVISIONE_ALPHA.md), poi generare un nuovo candidato con correzione backup e dipendenze aggiornate. Non riusare l'installer precedente come equivalente ai sorgenti: l'allineamento verificato prima della revisione è ora storico. Restano firma e gate operativi della checklist pilot.

Pillow: entrambe le ABI Fedora ricevute e verificate su Windows; pin 13.0.0, gate, provenienza e test strumentale integrati. [Procedura](ANDROID_PILLOW.md), [esiti correnti di APK e runtime](VERIFICA.md). Completare telefono ARM64, flussi operativi e audit delle altre dipendenze native Chaquopy; non qualificare l'intero stack dal solo aggiornamento Pillow.

Candidato Android `android-pillow-20261102-01` pronto, due test su emulatore passati. Sul telefono l'utente riferisce aggiornamento/avvio ed export PDF riusciti; allegato senza grafici verificato sul PC. **Prova del report con grafico sul telefono rimandata per scelta dell'utente**, che accetta per questa fase il riscontro dell'emulatore: non preparare ora un corpus QA aggiuntivo né richiedere debug USB per questa prova. Release ancora non firmato. Audit ELF ha individuato sei moduli non qualificati LOAD 16 KB (pydantic-core/FreeType entrambe le ABI, OpenBLAS/libpng x86_64): risolvere questa matrice prima di dichiarare compatibilità 16 KB. Restano audit di sicurezza nativo e altri gate pilot.

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
