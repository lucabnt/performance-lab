# Wheel native Android

## Stato al 20 ottobre 2026

**Aggiornamento runtime:** le due wheel cryptography originali richiedono riparazione DT_NEEDED libpython3.so tramite scripts/repair_android_abi3.py; originali conservati, provenienza in [ABI3_REPAIR.json](ABI3_REPAIR.json), manifest SHA256 aggiornato ai binari corretti. LIEF è solo uno strumento di build. La variante x86_64 è stata caricata sull’emulatore API 35 e il test nativo import/Fernet/Ed25519/Keystore/API è passato; ARM64 riparata ma non eseguita. La guida include questa fase obbligatoria per i binari originali ricevuti. Gradle traccia ora file wheel e manifest come input.

Il builder Fedora Kinoite/Toolbox dell’utente ha prodotto sei wheel API 26: pydantic-core 2.41.4, CFFI 2.0.0 e cryptography 50.0.2 per Python 3.13, entrambe le ABI x86_64 e arm64-v8a. Sei file successivamente trasferiti e verificati localmente contro il manifest; Chaquopy li ha risolti per entrambe le ABI e la build Windows ha prodotto il primo APK debug. Il primo avvio è stato poi verificato su x86_64; i flussi completi restano da collaudare. Cryptography x86_64 ha superato abi3audit strict; per ARM64 è stato ricevuto elenco/hash.

La procedura operativa corretta è [Compilare le wheel Android su Fedora Kinoite](../../docs/ANDROID_WHEEL_FEDORA.md). Contiene prerequisiti, comandi in ordine, hook before-build verificati e diagnosi. I tentativi intermedi sono conservati in [VERIFICA.md](../../docs/VERIFICA.md); non ripetere gli override CFLAGS/LDFLAGS/PKG_CONFIG risultati insufficienti.

## File e controlli

Questa directory riceve i sei `.whl` dal builder autorizzato, senza rinominarli. [SHA256.json](SHA256.json) contiene la mappa nome file → SHA-256 comunicata dal builder. Il gate `scripts/build_android.py` verifica versioni/ABI richieste e digest dei file presenti. CFFI 2.0.0 è fissato nei requisiti Android. Il gate non esegue test di import né certifica il runtime; una ricompilazione con hash diversi richiede provenienza e verifica esplicita prima di aggiornare il manifest.

Le wheel binarie sono ignorate da Git; il manifest è versionato. Non usare wheel manylinux/Windows rinominate, librerie Fedora come target Android o downgrade della crittografia per ottenere l’APK. Le dipendenze build host devono restare eseguibili su Linux, quelle distribuite nell’app devono essere Android.

Dalla radice eseguire `python scripts/build_android.py --check --gradle <percorso-wrapper>` con SDK/JDK configurati. Per il controllo delle sole wheel e la compilazione Gradle diretta vedere la guida. La presenza delle sei wheel non garantisce la risoluzione di tutte le dipendenze transitive: NumPy, Matplotlib, renderer PDF e altre estensioni rimangono da collaudare, insieme alle pagine da 16 KB. TD-57 rimane aperto fino al collaudo effettivo dell’app.
