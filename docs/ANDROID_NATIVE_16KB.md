# Dipendenze native Android e pagine da 16 KB

Stato del **2 novembre 2026**, ALPHA-REVIEW-01, Fuorigiri **0.10.0**. Questa fase segue [Pillow](ANDROID_PILLOW.md): sei oggetti ELF dell'APK restano non qualificati a 16 KB. **Kit sorgenti e ricette preparati; nessuna nuova wheel di questa fase ancora compilata o adottata.** Il builder Fedora resta operato dall'utente. Nessuna modifica a formule, archivi o dati degli atleti.

## Riscontri e scelta dei sorgenti

Il nuovo `scripts/audit_android_native.py` legge anche **tutti** i contenitori Chaquopy `.imy`, inclusa la libreria standard, oltre alle librerie APK: nel candidato Pillow sono **222 oggetti ELF**, con gli stessi sei problemi già individuati. Il precedente conteggio di 106 copriva librerie APK e requirements, non le estensioni della stdlib. Il report completo locale è `tmp/native16k-baseline-20261102-02.json`.

| Componente | Stato distribuito | Sorgente candidato | Azione |
|---|---|---|---|
| pydantic-core | 2.41.4, ARM64/x86_64 LOAD 4 KB | 2.41.4, stesso sdist PyPI | Ricompilare con max-page-size e common-page-size 16384; nessun cambio versione o algoritmo |
| chaquopy-freetype | 2.9.1, entrambe le ABI non allineate | FreeType 2.15.0, commit fissato | Compilare libreria condivisa per entrambe le ABI, preservando l'ABI richiesta da Matplotlib |
| chaquopy-libpng | 1.6.34, x86_64 non allineata | libpng 1.6.59, commit fissato | Aggiornare entrambe le ABI, controllando anche il PNG nel runtime |
| chaquopy-openblas | 0.2.20, x86_64 non allineata | OpenBLAS 0.3.34, archivio release ufficiale | Ricompilare entrambe le ABI, interfaccia LP64 e LAPACK presenti; vettori numerici obbligatori |

Gli indici Chaquopy consultati non offrono versioni nuove delle tre librerie. I metadati delle wheel NumPy 1.26.2 e Matplotlib 3.8.4 nell'APK usano vincoli **minimi** per questi provider: non è necessario rinominare librerie nuove con versioni vecchie o modificare le formule. Non aggiornare i pin dell'app fino alla ricezione/revisione dei nuovi binari. Le nuove wheel native-only hanno nomi reali `chaquopy_freetype-2.15.0`, `chaquopy_libpng-1.6.59`, `chaquopy_openblas-0.3.34`, tag py3-none/API26 e file nel layout `chaquopy/lib` già atteso dai consumatori.

La [pagina ufficiale libpng](https://libpng.org/pub/png/libpng.html) segnala **CVE-2026-46675**, corretta in **1.6.59**; non fermarsi a 1.6.58. [FreeType 2.15.0](https://freetype.org/) e [OpenBLAS 0.3.34](https://github.com/OpenMathLib/OpenBLAS/releases/tag/v0.3.34) sono release stabili osservate. Selezionare versioni nuove e correggere l'allineamento non dimostra assenza di altri problemi o completa l'audit di tutto lo stack. Zlib rimane quella del sistema Android; altre librerie Chaquopy, runtime, AndroidX e Qt/Chromium richiedono inventari e verifiche distinti.

## Integrità, ABI e numerica

`android/native-consumer-contract.json` deriva dal candidato debug Pillow identificato dal suo SHA-256. Raccoglie, per ABI, gli import effettivi dei consumatori diretti intersecati con gli export dei vecchi provider: **28 simboli FreeType e 57 OpenBLAS** richiesti in ciascuna ABI. Nessun consumatore ELF diretto di libpng osservato nell'APK: questo non autorizza a dichiararla inutilizzata da qualsiasi codice o a eliminarla senza verifica. Le nuove build controllano la copertura dei simboli richiesti, macchina ELF, DT_NEEDED, allineamento e congruenza LOAD prima di produrre una wheel.

NDK non include Fortran. La ricetta OpenBLAS abilita **C_LAPACK**, usando le routine LAPACK tradotte in C incluse nel sorgente upstream, mantiene `BUILD_WITHOUT_LAPACK=OFF` e interi LP64. **Non usare ONLY_CBLAS o una build senza LAPACK**, né sostituire il compilatore target con GCC/Fortran Fedora. Il passaggio da vecchio OpenBLAS alle nuove routine può modificare dettagli numerici: il solo elenco simboli non qualifica l'equivalenza scientifica. `scripts/check_android_native_runtime.py` prepara controlli indipendenti di prodotto matriciale, sistemi reali/complessi, autovalori, minimi quadrati, SVD e rendering font/PNG; verrà integrato nei test Android insieme alle nuove wheel. Non ricalcolare gli storici né cambiare i motori per far passare questi vettori.

FreeType conserva il profilo TTF necessario all'app, con dipendenze opzionali compresse/PNG/HarfBuzz disabilitate esplicitamente. Le librerie nuove conservano il SONAME prodotto dal linker, con nome file unversioned atteso dai consumer precedenti; il SONAME effettivo viene registrato. Nessun header ELF viene ritoccato per mascherare una build a 4 KB. Avvisi originali di FreeType, libpng, OpenBLAS e LAPACK inclusi nelle wheel; mantenere fonti/manifest e integrare gli avvisi legali nel prodotto al momento dell'adozione.

## Preparazione del kit

Dal repository aggiornato, con rete:

```bash
python scripts/prepare_android_native.py --output "$HOME/fuorigiri-android-build/native16k-kit-20261102-02"
```

In alternativa trasferire il kit ZIP già preparato su Windows, verificarne il digest consegnato ed estrarlo in una directory nuova. Tutti i sorgenti vengono ricontrollati prima dell'estrazione. Pydantic-core usa hash dello sdist PyPI; OpenBLAS il digest della release GitHub; FreeType/libpng commit fissati con hash osservati sul download, **non checksum indipendenti o firme del produttore**. La configurazione degli strumenti Fedora resta quella esistente, da registrare; non è un mirror offline degli strumenti Python/Rust.

## Esecuzione guidata nella Toolbox

Entrare nella Toolbox e ripristinare la sessione esistente:

```bash
toolbox enter --container fuorigiri-android
source "$HOME/fuorigiri-android-build/ambiente.sh"
command -v python cmake ninja rustc cargo rustup
python -c "import importlib.metadata; print(importlib.metadata.version('cibuildwheel'))"
```

Compilare **prima pydantic-core x86_64**, in una destinazione nuova:

```bash
python "$HOME/fuorigiri-android-build/native16k-kit-20261102-02/build_android_native.py" \
  --component pydantic_core --abi x86_64 \
  --output "$HOME/fuorigiri-android-build/native16k-pydantic-x86_64-20261102-01"
```

Al primo errore fermarsi, conservare tutto e inviare `build.log`; non rilanciare sullo stesso output. Solo dopo successo e revisione proseguire, **un componente e una ABI alla volta**, cambiando `--component` fra `pydantic_core`, `freetype`, `libpng`, `openblas`, `--abi` fra `x86_64` e `arm64_v8a`, e scegliendo ogni volta un output nuovo. Le compilazioni CMake e cibuildwheel scrivono i dettagli nel log, non necessariamente nel terminale; possono richiedere diversi minuti, OpenBLAS sensibilmente di più.

Ogni output conserva `build.json`, `build.log`, `elf.txt`, `wheelhouse/*.whl` e i sorgenti estratti. Non cancellare gli output precedenti o sostituire la wheelhouse già approvata. Pydantic-core mantiene 2.41.4: la nuova provenienza deve distinguere i binari ricompilati dai vecchi, conservandone gli originali prima di adottare nuovi hash.

## Dopo la ricezione dei binari

1. Confrontare digest builder/trasferimento, CRC/RECORD e ABI, dipendenze e simboli; integrare provenienza/avvisi legali e pin dei provider solo dopo revisione. I tre nuovi provider per entrambe le ABI porterebbero il gate da otto a **quattordici wheel**; pydantic-core sostituisce due file già esistenti.
2. Generare un nuovo candidato APK debug/release non firmato in directory nuova, preservando firma debug e consegne. Confrontare tutte le dipendenze risolte, i moduli incorporati e i checksum degli asset.
3. Eseguire `audit_android_native.py <apk> --output <nuovo-report.json> --require-16k` sull'intero APK, oltre a zipalign e firma. Nessuna eccezione ai sei moduli noti per promuovere la build.
4. Eseguire prove reali su emulatore 4 KB e ambiente 16 KB, vettori NumPy/LAPACK, font/PNG e test Pillow/PDF. Il rinvio concordato del grafico sul telefono resta valido: non richiedere ora un nuovo corpus QA o debug USB per quella prova.
5. Registrare esiti/limiti, mantenere firma release del titolare, Windows pulito e provider reali come gate distinti. Non pubblicare o generare chiavi implicitamente.

Fonti aggiuntive: [Android, pagine 16 KB](https://developer.android.com/guide/practices/page-sizes), [OpenBLAS, compilazione Android](https://github.com/OpenMathLib/OpenBLAS/blob/v0.3.34/docs/install.md#android), [opzione C_LAPACK](https://github.com/OpenMathLib/OpenBLAS/blob/v0.3.34/CMakeLists.txt), [indice FreeType](https://chaquo.com/pypi-13.1/chaquopy-freetype/), [indice libpng](https://chaquo.com/pypi-13.1/chaquopy-libpng/), [indice OpenBLAS](https://chaquo.com/pypi-13.1/chaquopy-openblas/).
