# Pillow Android: sorgenti, build e qualifica

Stato del **2 novembre 2026**, **ALPHA-REVIEW-01**, prodotto 0.10.0. **Pillow 13.0.0 compilata su Fedora per entrambe le ABI, trasferita e verificata localmente su Windows**: checksum, CRC, RECORD, dieci moduli ELF, libpython3.13.so esplicita, LOAD a 16 KB. Pin e gate dell'app aggiornati; provenienza in [PILLOW_BUILD.json](../android/wheels/PILLOW_BUILD.json). Stato delle nuove build e prove runtime nel [registro verifiche](VERIFICA.md). Formule, archivi e dati degli atleti non sono coinvolti.

Nuovi APK debug/release non firmato prodotti; due test strumentali passati su emulatore API35 x86_64 a pagine 4 KB, inclusi versione codecs, logo, PNG/JPEG, Matplotlib, scrittura PDF e apertura/rendering Android PdfRenderer. Telefono e export tramite UI/app esterna ancora aperti. Audit dell'intero APK: sei oggetti ELF ulteriori non superano il controllo LOAD 16 KB (pydantic-core e FreeType nelle due ABI; OpenBLAS/libpng x86_64), pur con zipalign valido. Non promuovere questi APK come qualificati 16 KB o pronti alla distribuzione alpha.

**Primo riscontro Fedora:** ambiente ripristinato, FreeType statica compilata; cibuildwheel 4.3.1 ha rifiutato `--platform` insieme a `--only`, prima della compilazione Pillow. Script corretto rimuovendo `--platform`; usare il comando corretto anche nei kit già preparati, che restano immutati. Nessuna wheel Pillow qualificata; dettagli e limiti nel [registro](VERIFICA.md).

## Disponibilità verificata

- [PyPI JSON](https://pypi.org/pypi/Pillow/json): versione corrente 13.0.0, Python 3.13 supportato, nessuna wheel Android nell'inventario delle release interrogato.
- [Chaquopy](https://chaquo.com/pypi-13.1/pillow/): per cp313 soltanto Pillow 11.0.0, Android API 24, arm64-v8a e x86_64. Non inserire subito un pin 13.0.0 nell'app.
- [Chaquopy: compilazione](https://github.com/chaquo/chaquopy/blob/master/server/pypi/README.md): cibuildwheel su Linux/macOS per Python 3.13+. La Toolbox Fedora già usata è un candidato adatto; la fattibilità effettiva richiede una prima compilazione e revisione dei log.
- [Vecchia ricetta](https://github.com/chaquo/chaquopy/blob/master/server/pypi/packages/pillow/meta.yaml): libjpeg 1.5.3 e FreeType 2.9.1. Aggiornare Pillow da solo non completa l'audit delle librerie distribuite.

La nuova Pillow incorpora libjpeg/FreeType statiche aggiornate; Matplotlib continua a richiedere separatamente chaquopy-freetype 2.9.1 e altre librerie native Chaquopy. L'aggiornamento Pillow non le sostituisce e non chiude l'audit nativo complessivo.

Il kit propone Pillow **13.0.0**, libjpeg-turbo **3.2.0** e FreeType **2.14.3**, le ultime due versioni corrispondenti al [file dipendenze di Pillow 13](https://github.com/python-pillow/Pillow/blob/13.0.0/.github/dependencies.json). FreeType 2.15.0 è successiva: la scelta 2.14.3 segue la combinazione upstream, non afferma che sia l'ultima disponibile o priva di avvisi. Audit e licenze di tutte le librerie restano da completare.

Pillow usa lo sdist verificato contro SHA-256 PyPI. libjpeg-turbo usa l'archivio ufficiale di release e il digest dell'API GitHub, non il tarball automatico dichiarato non supportato dal produttore. FreeType usa un commit fissato del mirror ufficiale; il digest è calcolato sul download, **non è una firma o un checksum indipendente del produttore**. `sources.json` distingue queste provenienze. La preparazione conserva anche le risposte originali PyPI/Chaquopy.

## Preparare e trasferire il kit

Da Windows, per rigenerarlo in una directory nuova (richiede rete):

```powershell
.venv/Scripts/python.exe scripts/prepare_android_pillow.py --output tmp/pillow-android-kit-nuovo
```

Il kit già preparato per questa attività è consegnato come `tmp/pillow-android-kit-20261102-02.zip`, con digest separato. Trasferire lo ZIP su Fedora e confrontarne SHA-256 prima di estrarre. Contiene i tre archivi sorgente, manifest, risposte degli indici, builder Python e controllo runtime. La venv Fedora deve già contenere cibuildwheel; il suo backend potrà scaricare ulteriori strumenti/dipendenze di build. Non è un mirror offline completo.

## Comandi nella Toolbox Fedora

Sull'host entrare nella Toolbox esistente:

```bash
toolbox enter --container fuorigiri-android
```

Dentro la Toolbox, sostituire soltanto il percorso dello ZIP se diverso:

```bash
source "$HOME/fuorigiri-android-build/ambiente.sh"
python -c "import sys, importlib.metadata; print(sys.version); print(importlib.metadata.version('cibuildwheel'))"
command -v cmake ninja rustc cargo rustup
java -version
test -f "$ANDROID_NDK_ROOT/build/cmake/android.toolchain.cmake"
sha256sum "$HOME/Downloads/pillow-android-kit-20261102-02.zip"
```

Confrontare il digest con quello consegnato. Se manca un prerequisito, fermarsi e inviare l'errore; per ripristinare l'ambiente seguire [la guida Fedora](ANDROID_WHEEL_FEDORA.md), senza ricreare la venv o aggiornare indiscriminatamente gli strumenti. Poi estrarre in una destinazione nuova:

```bash
test ! -e "$HOME/fuorigiri-android-build/pillow-kit-20261102-02" && unzip "$HOME/Downloads/pillow-android-kit-20261102-02.zip" -d "$HOME/fuorigiri-android-build/pillow-kit-20261102-02"
```

Prima compilare x86_64:

```bash
python "$HOME/fuorigiri-android-build/pillow-kit-20261102-02/build_android_pillow.py" --abi x86_64 --output "$HOME/fuorigiri-android-build/pillow-x86_64-20261102-01"
```

**Fermarsi al primo errore** e inviare `build.log` dalla directory di output; non cancellarla o rilanciare sulla stessa destinazione. Soltanto dopo il successo compilare ARM64:

```bash
python "$HOME/fuorigiri-android-build/pillow-kit-20261102-02/build_android_pillow.py" --abi arm64_v8a --output "$HOME/fuorigiri-android-build/pillow-arm64-20261102-01"
```

Il builder registra gli strumenti nel log, verifica i sorgenti, compila libjpeg/FreeType statiche API 26 con NDK e PIC, prepara il prefisso Python target per cibuildwheel, compila Pillow cp313 e raccoglie `llvm-readelf` per ogni `.so`. Conserva output e log in caso di errore; non tocca la wheelhouse precedente o `android/wheels`.

Profilo iniziale: PNG/zlib, JPEG e FreeType obbligatori; librerie opzionali TIFF, WebP, LCMS, JPEG2000, RAQM, AVIF, XCB e imagequant disabilitate esplicitamente. In FreeType non sono abilitati font compressi o HarfBuzz; JPEG SIMD disabilitato per ridurre i prerequisiti host. Questa è una configurazione da confrontare con le funzioni richieste dall'app, **non equivalenza già dimostrata**. Zlib proviene dagli header/stub NDK e dalla libreria di sistema Android, non da Fedora. Il flag 16 KB non certifica l'APK.

## Cosa riportare e cosa resta

Per ciascuna ABI trasferire `wheelhouse/*.whl`, `build.json`, `build.log`, `elf.txt`, `cibuildwheel.toml` e `prepare_target.py`; conservare anche il kit originale. `build.json` contiene i checksum prodotti, non approva automaticamente le wheel. Esaminare macchina ELF, DT_NEEDED, chiusura delle dipendenze, collegamento a libpython corretto e segmenti LOAD a 16 KB. Non applicare automaticamente la riparazione ABI3 di cryptography a Pillow cp313.

Dopo questa revisione: introdurre pin e gate Pillow per entrambe le ABI, aggiornare manifest/provenienza e testi legali pertinenti, generare APK debug e release non firmato in un nuovo candidato. Verificare Pillow/multipart realmente inclusi, CRC, firme, asset e allineamento. Non riusare i vecchi APK come prova.

`check_android_pillow_runtime.py` è pronto per l'esecuzione **nel Python dell'app Android**, tramite il test strumentale da integrare insieme alle wheel: controlla versione/codecs, PNG/JPEG, font accentati, Matplotlib Agg e PDF ReportLab in memoria. Rifiuta l'esecuzione desktop come prova Android. Non dimostra esportazione/apertura del file, grafica dell'app o conservazione dei dati.

Collaudo successivo su emulatore e telefono ARM64: avvio, logo/immagini, report reali con dati sintetici, export/apertura PDF, aggiornamento con dati QA conservati e verifica delle pagine 16 KB. Nessun dispositivo ADB collegato durante questa preparazione. Firma release del titolare dopo i controlli, con chiave stabile e senza segreti nei log: [firma](FIRMA_ANDROID.md), [pilot](COLLAUDO_PILOT.md). Restano separati Windows pulito e provider/due account reali.
