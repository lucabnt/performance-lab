# Primo collegamento Google Drive in Fuorigiri

Procedura aggiornata il 25 ottobre 2026, riferita ai comandi presenti in Fuorigiri 0.10.0. Adapter, cifratura, firme e flussi OAuth esistono nei sorgenti; i test automatici usano risposte simulate. Questa guida non documenta un collegamento eseguito con account reali.

**Stato al 18 novembre 2026: Google Drive diretto è sperimentale** (PERIMETRO-01). Non riceve nuovi sviluppi e non fa parte dei controlli dell'alpha. Il trasporto consigliato per condividere una società fra Windows e Android è WebDAV: vedere [Primo scambio WebDAV](WEBDAV_ANDROID_PRIMO_SCAMBIO.md) e lo [stato dei trasporti](CONFIGURARE_LA_SINCRONIZZAZIONE.md#stato-del-supporto--18-novembre-2026). La procedura sotto resta valida per prove su una società QA.

## Percorso consigliato

Per provare Google Drive con la stessa società su Windows e Android, partire dal collegamento **Google Drive diretto in Fuorigiri**, con un progetto Google Cloud sotto il controllo del titolare e una cartella di scambio dedicata per società. I database rimangono locali; nella cartella transitano i pacchetti di scambio cifrati. Il backup dati resta separato dal canale di sincronizzazione.

Per il primo collaudo usare una società QA con dati sintetici e una cartella `Fuorigiri - QA`. La selezione attuale della cartella avviene tramite ID: il Google Picker non è implementato. Il permesso minimo `drive.file` non rende automaticamente accessibile una cartella esistente con tutti i file dei collaboratori. Nel codice attuale il pilot su quella cartella può usare la scelta esplicita **Drive completo**, che autorizza l'intero Drive dell'account, non soltanto la cartella. Per circoscrivere il contenuto esposto in questo pilot è preferibile un account dedicato con soli dati di prova, senza condividere password fra operatori. È una scelta operativa, non una restrizione OAuth alla cartella.

Per una distribuzione più ampia il percorso preferibile è qualificare un flusso con Picker e `drive.file` e completare i requisiti Google applicabili. Non descrivere tale flusso come già disponibile o collaudato in Fuorigiri.

## 1. Preparare Google Cloud

1. Aprire [Google Cloud Console](https://console.cloud.google.com/) con l'account del titolare. Creare o selezionare un progetto dedicato, per esempio `Fuorigiri Performance Lab`.
2. In **API e servizi → Libreria** abilitare **Google Drive API**.
3. Aprire **Google Auth Platform**. In **Branding** compilare nome dell'app, email di assistenza e contatto del titolare. In **Audience** usare External se i partecipanti hanno account Gmail/personali o esterni all'organizzazione; Internal è pertinente soltanto agli utenti della propria organizzazione Workspace, quando disponibile.
4. Per il collaudo External mantenere lo stato Testing e aggiungere in **Test users** tutti gli account che proveranno il collegamento. In **Data Access** dichiarare gli scope richiesti dalla scelta che si userà nell'app: per il pilot Drive completo è `https://www.googleapis.com/auth/drive`.
5. In **Clients → Create client** scegliere **Desktop app**, con un nome come `Fuorigiri Windows`. Conservare client ID e client secret in un posto protetto. Non creare un client Web application per questo flusso. La callback loopback usata da Fuorigiri è `http://127.0.0.1:53682/oauth/callback`; la gestisce l'app durante il consenso, senza una pagina pubblica da ospitare.

Le app desktop sono client pubblici: il client secret non sostituisce una credenziale privata di server. Fuorigiri usa anche PKCE e conserva i token nel portachiavi di sistema. Non incollare client secret, token o file identità nella chat o nella repository.

## 2. Preparare la cartella Drive

1. In Drive creare `Fuorigiri - QA`. Non selezionare la cartella che contiene il database locale di Fuorigiri.
2. Se il collaudo coinvolge altri account, condividere la cartella con quegli account specifici e permessi che consentano lo scambio dei file. Non usare un link pubblico. I permessi Drive sono distinti dal ruolo Admin dati/Visualizzatore in Fuorigiri.
3. Copiare l'ID dalla URL `https://drive.google.com/drive/folders/ID_CARTELLA`: nel campo dell'app va solo `ID_CARTELLA`, senza URL o parametri.

## 3. Collegare il primo PC

1. Aprire la società QA in Fuorigiri. Da **Archivio e scambio → Condivisione e collaboratori**, selezionare il trasporto Google Drive.
2. Inserire **Client ID / App key OAuth**, **ID cartella condivisa** e, nel campo protetto **Client secret della registrazione desktop Google**, il secret del client Desktop appena creato.
3. Per il pilot descritto sopra selezionare consapevolmente **Autorizzazione Google Drive → Drive completo (richiede consenso esteso)**. Lasciare `drive.file` non risolve da solo l'accesso alla cartella incollata.
4. Premere **Collega account Google Drive** e completare il consenso nel browser di sistema, controllando l'account selezionato. Tornare a Fuorigiri quando il browser conferma il collegamento. Se il browser non si apre, usare il collegamento di autorizzazione mostrato dall'app.
5. Premere **Salva connessione e sincronizza** e verificare l'esito. **Account collegato** dimostra il consenso; **destinazione verificata all'ultimo scambio riuscito** documenta anche l'accesso alla cartella per quello scambio.

Se il callback risulta occupato, completare o chiudere il precedente tentativo e riprovare. Per un archivio precedente senza accesso personale, seguire il percorso di copia indipendente da backup descritto in [società e accessi](SOCIETA_BACKUP_E_ACCESSI.md), preservando l'originale: non creare nuove identità direttamente nei dati esistenti.

## 4. Collegare il secondo dispositivo alla stessa società

Dal fondatore generare un invito personale per l'altro operatore/dispositivo. Sul secondo dispositivo usare **Gestisci società → Accedi alla stessa società di un altro computer**, con invito e password. Non creare una seconda società omonima e non usare un normale backup come invito.

Sul secondo dispositivo configurare la stessa cartella Drive e collegare l'account autorizzato di quel dispositivo. La configurazione e i token sono locali: non vengono ereditati automaticamente dal primo PC. Se entrambi sono Windows, si può usare la stessa registrazione OAuth Desktop del progetto. Sincronizzare prima il fondatore e poi il dispositivo invitato.

Per Android occorre anche la registrazione OAuth nativa nello **stesso progetto Google Cloud**, con package `org.fuorigiri.performancelab` e impronta SHA-1 del certificato con cui l'APK installato è effettivamente firmato. Il client Desktop non sostituisce questa registrazione. Il flusso Android usa Google Play services e autorizzazione nativa; il secret Desktop non va copiato nel telefono. Il candidato release non firmato richiede prima la [firma del titolare](FIRMA_ANDROID.md). Cambiare certificato può impedire l'aggiornamento dell'app installata: preservare la continuità della firma e i dati.

## 5. Collaudo minimo prima dei dati operativi

Con due account e due dispositivi sulla società QA:

1. Creare un atleta sintetico sul primo, sincronizzare entrambi e verificarlo sul secondo.
2. Creare una misura o correggere un dato sintetico sul secondo; sincronizzare e verificare il ritorno al primo.
3. Chiudere e riaprire le app, ripetere lo scambio e controllare che non compaiano duplicati.
4. Verificare un allegato/test, una modifica concorrente con conflitto esplicito e un'interruzione di rete con successivo recupero. Confrontare anche gli ID della società, non soltanto il nome.
5. Creare un backup separato e provarne il ripristino su una copia. Soltanto dopo il collaudo configurare una cartella operativa distinta per la società reale.

Aggiornare tutti i dispositivi prima di attivare il [formato sync v2](SYNC_V2_E_BACKUP.md). Le prove su un account o su cartelle locali non certificano la collaborazione fra due account Google o fra Windows e telefono.

## Durata del consenso e uso continuativo

Per un progetto External in stato Testing, con gli scope Drive, Google emette refresh token che scadono dopo sette giorni. La necessità di ricollegare in quel caso non va confusa con perdita dei dati locali. Prima dell'uso continuativo definire lo stato di pubblicazione e completare i requisiti Google applicabili alla propria distribuzione: passare a Production non equivale automaticamente a verifica o qualifica del prodotto.

## Fonti ufficiali

- [Configurare consenso, pubblico e utenti di test](https://developers.google.com/workspace/guides/configure-oauth-consent).
- [Client Desktop, PKCE e callback loopback](https://developers.google.com/identity/protocols/oauth2/native-app).
- [Scope Drive e differenza fra drive.file e Drive completo](https://developers.google.com/workspace/drive/api/guides/api-specific-auth).
- [Scadenza dei refresh token in Testing](https://developers.google.com/identity/protocols/oauth2/).
- [Autorizzazione nativa Android](https://developer.android.com/identity/authorization).

Per le proprietà del protocollo Fuorigiri e le altre destinazioni vedere [Configurare la sincronizzazione](CONFIGURARE_LA_SINCRONIZZAZIONE.md).
