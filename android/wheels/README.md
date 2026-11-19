# Wheel native Android

## Ricostruzione da radice neutra — 19 novembre 2026

Sostituite sei wheel con la ricostruzione Fedora Toolbox in `/build/fuorigiri-20261119-01` (kit `android-neutral-kit-20261119-02`): pydantic-core 2.41.4, cryptography 50.0.2 e Pillow 13.0.0, entrambe le ABI. CFFI 2.0.0 invariata (stessi digest). Home del builder mappata su `/build/tools`; OpenSSL 3.5.9 statico compilato **senza** `-ffile-prefix-map`, perché OpenSSL incorpora i propri flag di compilazione nella stringa `compiler:`. pydantic-core e cryptography collegate con `max-page-size=16384`. Cryptography riparata con `repair_android_abi3.py` (report in [ABI3_REPAIR.json](ABI3_REPAIR.json), che sostituisce quelli del 20 ottobre conservati nella cronologia Git); Pillow in [PILLOW_BUILD.json](PILLOW_BUILD.json). `scan_build_paths.py --strict` pulito su builder e Windows; CRC, RECORD, macchina ELF e LOAD 16 KB verificati per 14 moduli. Runtime x86_64 verificato su emulatore API 35 (2 test strumentali, avvio app); ARM64 non eseguito. Le wheel precedenti sono conservate fuori dal repository.

## Pillow — 2 novembre 2026

Ricevute e verificate localmente due wheel Pillow 13.0.0 cp313/API 26, ARM64 e x86_64, prodotte sulla Toolbox Fedora. Ora il gate richiede **otto wheel**, con Pillow fissata in `android/requirements.txt`. Provenienza di sorgenti/libjpeg-turbo 3.2.0/FreeType 2.14.3, digest del trasferimento e rapporto dei dieci moduli ELF in [PILLOW_BUILD.json](PILLOW_BUILD.json). Verificati checksum, CRC, RECORD, macchine, DT_NEEDED libpython3.13.so e allineamento/congruenza dei segmenti LOAD a 16 KB. Questa è una verifica strutturale, distinta da runtime e APK. Non applicare la riparazione ABI3 di cryptography a queste wheel cp313.

Ricetta e stato aggiornato in [ANDROID_PILLOW.md](../../docs/ANDROID_PILLOW.md). Gli avvisi originali delle librerie statiche sono inclusi nel documento canonico THIRD_PARTY.md e quindi negli asset legali dell'app. Il manifest nativo non qualifica tutte le altre librerie Chaquopy o le pagine 16 KB del dispositivo.

## Stato al 20 ottobre 2026

**Aggiornamento runtime:** le due wheel cryptography originali richiedono riparazione DT_NEEDED libpython3.so tramite scripts/repair_android_abi3.py; originali conservati, provenienza in [ABI3_REPAIR.json](ABI3_REPAIR.json), manifest SHA256 aggiornato ai binari corretti. LIEF è solo uno strumento di build. La variante x86_64 è stata caricata sull’emulatore API 35 e il test nativo import/Fernet/Ed25519/Keystore/API è passato; ARM64 riparata ma non eseguita. La guida include questa fase obbligatoria per i binari originali ricevuti. Gradle traccia ora file wheel e manifest come input.

Il builder Fedora Kinoite/Toolbox dell’utente ha prodotto sei wheel API 26: pydantic-core 2.41.4, CFFI 2.0.0 e cryptography 50.0.2 per Python 3.13, entrambe le ABI x86_64 e arm64-v8a. Sei file successivamente trasferiti e verificati localmente contro il manifest; Chaquopy li ha risolti per entrambe le ABI e la build Windows ha prodotto il primo APK debug. Il primo avvio è stato poi verificato su x86_64; i flussi completi restano da collaudare. Cryptography x86_64 ha superato abi3audit strict; per ARM64 è stato ricevuto elenco/hash.

La procedura operativa corretta è [Compilare le wheel Android su Fedora Kinoite](../../docs/ANDROID_WHEEL_FEDORA.md). Contiene prerequisiti, comandi in ordine, hook before-build verificati e diagnosi. I tentativi intermedi sono conservati in [VERIFICA.md](../../docs/VERIFICA.md); non ripetere gli override CFLAGS/LDFLAGS/PKG_CONFIG risultati insufficienti.

## File e controlli

Questa directory riceve i sei `.whl` dal builder autorizzato, senza rinominarli. [SHA256.json](SHA256.json) contiene la mappa nome file → SHA-256 comunicata dal builder. Il gate `scripts/build_android.py` verifica versioni/ABI richieste e digest dei file presenti. CFFI 2.0.0 è fissato nei requisiti Android. Il gate non esegue test di import né certifica il runtime; una ricompilazione con hash diversi richiede provenienza e verifica esplicita prima di aggiornare il manifest.

Le wheel binarie sono ignorate da Git; il manifest è versionato. Non usare wheel manylinux/Windows rinominate, librerie Fedora come target Android o downgrade della crittografia per ottenere l’APK. Le dipendenze build host devono restare eseguibili su Linux, quelle distribuite nell’app devono essere Android.

Dalla radice eseguire `python scripts/build_android.py --check --gradle <percorso-wrapper>` con SDK/JDK configurati. Per il controllo delle sole wheel e la compilazione Gradle diretta vedere la guida. La presenza delle sei wheel non garantisce la risoluzione di tutte le dipendenze transitive: NumPy, Matplotlib, renderer PDF e altre estensioni rimangono da collaudare, insieme alle pagine da 16 KB. TD-57 rimane aperto fino al collaudo effettivo dell’app.
