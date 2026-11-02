# Firma dell’APK Android per alpha e pilot

Il candidato contiene un **APK release non firmato**. Per scelta dell’utente non è stata creata alcuna chiave: questo file non si installa finché non viene firmato. Non sostituire la firma release con quella debug per avviare un pilot operativo.

La chiave identifica il titolare degli aggiornamenti. Conservarne una copia di recupero distinta dal PC e custodire la password separatamente. Non inserirla nella repository, negli allegati o nei log. Scegliere il canale futuro (APK diretto/Google Play) prima della prima distribuzione: con Play App Signing distinguere chiave di caricamento e chiave di firma applicativa. Fonti: [firma Android](https://developer.android.com/studio/publish/app-signing), [apksigner](https://developer.android.com/tools/apksigner), [zipalign](https://developer.android.com/tools/zipalign).

## 1. Creare una chiave stabile — solo il titolare, una volta

Android Studio è facoltativo. La procedura sotto firma con `apksigner` l'APK già compilato e verificato, senza ricostruirlo. In alternativa, aprire il progetto `android/` in Android Studio e usare **Build → Generate Signed Bundle / APK → APK**, selezionare o creare la chiave del titolare e scegliere `release`: questa procedura produce una nuova build firmata, da verificare e identificare con un proprio digest. Per questo progetto usare JDK 21 con Gradle 8.13; non sostituire automaticamente il JDK con quello più recente incluso nell'IDE. Conservare keystore e password fuori dalla repository. Il debug già firmato serve al percorso di test e non sostituisce la firma release.

PowerShell, con JDK configurato. I comandi seguenti **non sono stati eseguiti dall’agente**. Le password vanno digitate nei prompt locali, senza passarle sulla riga di comando.

```powershell
$signingDir = Join-Path $env:USERPROFILE 'Fuorigiri-signing'
New-Item -ItemType Directory -Path $signingDir -Force | Out-Null
$keystore = Join-Path $signingDir 'fuorigiri-release.p12'
if (Test-Path -LiteralPath $keystore) { throw 'Keystore già presente: non sovrascriverlo.' }
& "$env:JAVA_HOME/bin/keytool.exe" -genkeypair -v -storetype PKCS12 -keystore $keystore -alias fuorigiri-release -keyalg RSA -keysize 3072 -validity 10000
if ($LASTEXITCODE -ne 0) { throw 'Creazione chiave non riuscita.' }
& "$env:JAVA_HOME/bin/keytool.exe" -list -v -keystore $keystore -alias fuorigiri-release
```

Verificare alias e impronta SHA-256 del certificato. Fare e verificare una copia di recupero del file; conservare password e copia in luoghi separati. Non generare una nuova chiave per ogni build. Per un APK diretto la continuità della firma è necessaria agli aggiornamenti; la rotazione richiede una procedura distinta.

## 2. Verificare l’input, firmare una copia e verificarla

Dalla radice del progetto; se si usa una copia della consegna su un altro PC, impostare `$candidate` sulla sua cartella. Installare soltanto gli strumenti di firma sul PC del titolare, non sui PC dei tester.

```powershell
$candidate = (Resolve-Path 'dist/candidates/Fuorigiri-0.10.0-alpha-prep-20261102-01').Path
$sdk = $env:ANDROID_HOME
if (-not $sdk) { $sdk = Join-Path $env:LOCALAPPDATA 'Android/Sdk' }
$tools = Join-Path $sdk 'build-tools/35.0.0'
$keystore = Join-Path $env:USERPROFILE 'Fuorigiri-signing/fuorigiri-release.p12'
$unsigned = Join-Path $candidate 'Fuorigiri-0.10.0-android-release-unsigned.apk'
$signed = Join-Path $candidate 'Fuorigiri-0.10.0-android-release-signed.apk'
if (Test-Path -LiteralPath $signed) { throw 'Output firmato già presente: non sovrascriverlo.' }
Get-FileHash -Algorithm SHA256 -LiteralPath $unsigned
# Confrontare il digest con SHA256SUMS.txt prima di proseguire.
& "$tools/zipalign.exe" -c -P 16 -v 4 $unsigned
if ($LASTEXITCODE -ne 0) { throw 'Allineamento non valido: fermarsi prima della firma.' }
& "$tools/apksigner.bat" sign --ks $keystore --ks-key-alias fuorigiri-release --out $signed $unsigned
if ($LASTEXITCODE -ne 0) { throw 'Firma non riuscita.' }
& "$tools/apksigner.bat" verify --verbose --print-certs $signed
if ($LASTEXITCODE -ne 0) { throw 'Verifica firma fallita: non distribuire.' }
& "$tools/zipalign.exe" -c -P 16 -v 4 $signed
if ($LASTEXITCODE -ne 0) { throw 'Allineamento del firmato non valido.' }
Get-FileHash -Algorithm SHA256 -LiteralPath $signed
```

L’APK prodotto da Gradle dovrebbe essere già allineato. Se non lo è, non limitarsi a ignorare il controllo: correggere la build o creare un nuovo input allineato **prima** della firma e registrarne l’impronta. Qualsiasi modifica al file dopo la firma può invalidarla.

Registrare impronta del certificato e digest del nuovo APK nel verbale di [COLLAUDO_PILOT.md](COLLAUDO_PILOT.md). Il manifest e i checksum originali descrivono il candidato non firmato: non cambiarli per far sembrare il firmato già verificato. Conservare il firmato con una propria ricevuta/digest e collaudarlo effettivamente.

## 3. Installazione e aggiornamenti

- Prima installazione: copiare l’APK firmato sul telefono e installarlo con il gestore pacchetti, oppure `adb install <file-firmato>` da un PC autorizzato.
- Un’app debug già installata con il medesimo applicationId ma firma diversa non è aggiornabile direttamente con questo APK. Prima di qualsiasi rimozione, creare backup dati e materiali di recupero degli accessi e provarli su copia QA. Non dare `adb uninstall` come scorciatoia su un telefono con dati da conservare.
- Gli aggiornamenti release devono conservare applicationId e firma appropriata e incrementare versionCode. In Fuorigiri deriva da major/minor/patch: cambiare metadati in modo coerente con verify_versions.py, senza aumentare solo il numero Android.
- Non retrocedere il database per installare un vecchio APK. Il recupero dei dati richiede backup e compatibilità, non solo il vecchio eseguibile.
- Firmare non certifica funzionamento del backend ARM64, compatibilità 16 KB, provider o correttezza scientifica. Completare i check Android del pilot.
