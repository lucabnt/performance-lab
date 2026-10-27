# Installare Fuorigiri sul Pixel 9 per un test

27 ottobre 2026. APK debug locale di Fuorigiri 0.10.0, compilato con le modifiche correnti e firma debug già esistente. Nessuna chiave release creata. Ultima destinazione: `dist/android-tests/Fuorigiri-0.10.0-pixel9-test-20261027-02/Fuorigiri-0.10.0-android-test.apk`, con la stessa firma dei test precedenti, grafico dei test in apertura quando disponibile, KPI unificati con soglia relativa in W/kg, pagine riordinate, editor zone visibile, stato sync persistente e correzioni di avvio. Questa è una prova personale, distinta dal pilot operativo con firma del titolare descritto in [FIRMA_ANDROID.md](FIRMA_ANDROID.md). Per il servizio Koofr ora disponibile vedere [primo scambio WebDAV](WEBDAV_ANDROID_PRIMO_SCAMBIO.md).

## Installazione

1. Copia l'APK dal PC al telefono con USB (modalità Trasferimento file), per esempio in Download. In alternativa trasferisci il solo APK tramite il tuo Drive: il trasferimento dell'installatore non configura la sincronizzazione dei dati.
2. Sul Pixel apri Files, poi Download, e tocca l'APK.
3. Se richiesto, apri Impostazioni e abilita **Consenti da questa origine** per l'app con cui stai aprendo l'APK, poi torna all'installazione e premi Installa. Non serve attivare Opzioni sviluppatore o Debug USB per questa procedura. Lascia Play Protect attivo; un eventuale blocco di sicurezza va diagnosticato prima di procedere.
4. Apri Fuorigiri. Per una prima prova crea una società dimostrativa. Puoi anche importare un backup Windows come **Copia di consultazione**, per controllare leggibilità di atleti, test e report senza collegarla alla sincronizzazione della società originale.
5. Prova chiusura/riapertura, modalità aereo, navigazione, grafici e download PDF. Annota modello, versione Android, schermata e messaggio di eventuali errori.
6. Puoi disattivare nuovamente Consenti da questa origine dopo l'installazione, da Impostazioni → App → Accesso speciale per le app → Installa app sconosciute.

Se Fuorigiri è già installato e Android segnala un conflitto di firma, fermati e conserva i dati: non disinstallare come scorciatoia. L'APK debug usa lo stesso applicationId della release; passare a una firma definitiva richiede una procedura con backup dati e recupero accessi. Non usare questa build come archivio operativo unico.

Fonti ufficiali: [installare app su Pixel](https://support.google.com/pixelphone/answer/7391672?hl=it), [firma e aggiornamenti Android](https://developer.android.com/studio/publish/app-signing), [Play Protect](https://support.google.com/android/answer/2812853?hl=it).

## Sincronizzazione con Windows: limite attuale con Google Drive

La modalità **Cartella locale del client cloud** è desktop: Android non espone questa destinazione in Fuorigiri. Installare Google Drive sul telefono non rende quella cartella utilizzabile dal motore di sincronizzazione. Con il solo Google Drive e senza configurazione Google Cloud/OAuth, questo APK permette di provare l'app, ma non uno scambio automatico Windows ↔ Pixel.

I trasporti comuni già implementati sono:

- **WebDAV:** stesso server/cartella HTTPS accessibile da entrambi i dispositivi, account e password applicazione. Nessun progetto Google Cloud, ma serve un servizio WebDAV effettivamente disponibile.
- **Google Drive API:** registrazione OAuth Desktop e Android con package/certificato del file effettivamente installato. Vedere [primo collegamento Drive](GOOGLE_DRIVE_PRIMO_COLLEGAMENTO.md). Non basta incollare un link Drive.

Quando il trasporto è disponibile, sul PC usa la società originale, crea un invito personale per il telefono (Admin dati se vuoi provare modifiche da entrambi), trasferisci invito e password separatamente, quindi sul Pixel scegli **Collega tramite invito**. Configura la stessa destinazione su entrambi. Prova Sincronizza ora, acquisizione dei dati, una modifica innocua e il ritorno sul PC; continua con offline, conflitti e revoche su una società QA. Non creare una seconda società omonima per collegarti e non usare il backup al posto dell'invito.

Per un'esperienza futura senza configurazione GCP a carico di ogni utente, il distributore può predisporre una propria integrazione Google registrata: questo richiede comunque una registrazione e qualifica iniziale del prodotto. La selezione guidata della cartella con Google Picker non è ancora implementata. Nessuna nuova modalità Drive senza GCP è stata aggiunta con questa modifica.

## Verifiche di questa consegna

Per blocchi all'avvio, non cancellare dati o disinstallare come primo tentativo. L'aggiornamento distingue AVVIO-01 (inizializzazione non riuscita), AVVIO-02 (interfaccia non caricata) e AVVIO-03 (motore locale oltre 30 s) con Riprova. Le letture di apertura hanno un limite esplicito; dopo errore conservano l'archivio e permettono nuovo tentativo. La rete dello scambio non deve trattenere il lock di avvio. Se ricapita sul Pixel, annota messaggio/codice, versione Android e se era in corso una sincronizzazione; le modifiche non equivalgono a una diagnosi dei log del telefono.

Build assembleDebug riuscita, firma APK v2 valida con certificato Android Debug esistente, zipalign con pagine 16 KB superato, ZIP integro, runtime ARM64 presente e 19 file frontend corrispondenti alla build. Questi controlli non equivalgono ad avvio su Pixel fisico, caricamento ARM64 di tutte le wheel o scambio cloud fra due dispositivi: restano prove da effettuare sul telefono.
