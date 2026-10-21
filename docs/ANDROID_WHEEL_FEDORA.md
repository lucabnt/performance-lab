# Compilare le wheel Android su Fedora Kinoite

Procedura consolidata il **20 ottobre 2026**, per Fuorigiri **0.10.0**. Questa è la ricetta operativa; i tentativi intermedi e le prove effettive restano in [VERIFICA.md](VERIFICA.md). Per la shell e i requisiti applicativi vedere [ANDROID.md](ANDROID.md).

## Risultato e limiti

Sul PC dell’utente, Fedora Kinoite 44 x86_64 con Toolbox, sono state prodotte sei wheel: pydantic-core 2.41.4, CFFI 2.0.0 e cryptography 50.0.2, ciascuna per Android API 26 **x86_64** (emulatore) e **arm64-v8a** (telefono). Cryptography x86_64 ha superato abi3audit strict. Per ARM64 abbiamo elenco file e checksum, non il log completo di audit. I digest comunicati sono in [SHA256.json](../android/wheels/SHA256.json).

Non è ancora una verifica di APK, caricamento delle librerie, pagine da 16 KB o comportamento su dispositivo. Fedora serve qui da builder delle dipendenze Android; questa procedura non produce il pacchetto desktop Linux. **Aggiornamento successivo nella stessa giornata:** sei binari trasferiti su Windows e digest verificati; build Gradle riuscita e APK debug presente (~96 MiB). Installazione e runtime restano aperti; il registro verifiche distingue questi esiti dalla ricetta di ricostruzione.

## 1. Ambiente: host Kinoite e Toolbox

Eseguire sull’**host Fedora**, una sola volta se il contenitore non esiste:

```bash
toolbox create --container fuorigiri-android
toolbox enter --container fuorigiri-android
```

Tutti i comandi Linux successivi si eseguono **nella Toolbox**, salvo indicazione diversa. La home è condivisa con l’host: non trattarla come spazio sacrificabile. Non servono modifiche con rpm-ostree all’host.

```bash
sudo dnf install git gcc gcc-c++ make cmake ninja-build perl \
  python3 python3-devel curl unzip autoconf automake libtool \
  texinfo pkgconf-pkg-config

mkdir -p "$HOME/fuorigiri-tools"
mkdir -p "$HOME/fuorigiri-android-build"
cd "$HOME/fuorigiri-android-build"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install cibuildwheel build maturin
python -m pip freeze > strumenti-build.txt
python -c "from importlib.metadata import version; print(version('cibuildwheel'))"
```

La creazione della venv è per un builder nuovo. Per riprendere quello esistente basta attivarla; non ricreare o aggiornare gli strumenti a ogni sessione. Il builder usava Python host 3.14.5; cibuildwheel prepara separatamente il Python target 3.13. La versione esatta di cibuildwheel non è stata fornita nel log: conservare `strumenti-build.txt` e riusarlo per le ricostruzioni con `python -m pip install -r strumenti-build.txt`. Non promettiamo riproducibilità binaria identica dal solo elenco qui sotto. `cibuildwheel --version` non è supportato dalla CLI incontrata.

## 2. JDK 21 senza dipendere dai pacchetti Fedora

Su Fedora 44 `java-21-openjdk-devel` non era disponibile; anche il repository Adoptium installato non esponeva `temurin-21-jdk`. La soluzione riuscita è l’archivio ufficiale Temurin, senza sostituire il Java di sistema.

Dalla [release Temurin 21.0.12.1+1](https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21.0.12.1%2B1), scaricare nella stessa cartella:

- `OpenJDK21U-jdk_x64_linux_hotspot_21.0.12.1_1.tar.gz`;
- `OpenJDK21U-jdk_x64_linux_hotspot_21.0.12.1_1.tar.gz.sha256.txt`.

Il file `.sig` è una firma, **non** il checksum SHA-256. L’API Adoptium restituiva HTTP 403 nel tentativo iniziale: il download manuale degli asset GitHub evita quella dipendenza. Dalla cartella dei due file eseguire:

```bash
python3 - <<'PY'
import hashlib
import pathlib
import tarfile
import tempfile

archive = pathlib.Path('OpenJDK21U-jdk_x64_linux_hotspot_21.0.12.1_1.tar.gz')
expected = pathlib.Path(str(archive) + '.sha256.txt').read_text().split()[0]
with archive.open('rb') as stream:
    actual = hashlib.file_digest(stream, 'sha256').hexdigest()
if actual != expected.lower():
    raise SystemExit('Checksum JDK non valido')
base = pathlib.Path.home() / 'fuorigiri-tools'
base.mkdir(exist_ok=True)
target = base / 'jdk-21'
if target.exists():
    raise SystemExit(f'Destinazione già presente: {target}; non sovrascritta')
with tempfile.TemporaryDirectory(dir=base) as temporary:
    extracted = pathlib.Path(temporary)
    with tarfile.open(archive) as source:
        source.extractall(extracted, filter='data')
    roots = list(extracted.iterdir())
    if len(roots) != 1 or not (roots[0] / 'bin/javac').is_file():
        raise SystemExit('Struttura JDK inattesa')
    roots[0].rename(target)
print(f'JDK verificato: {target}')
PY
```

## 3. SDK, NDK e Rust separato

Installare i Command-line Tools Linux dal [sito Android ufficiale](https://developer.android.com/studio#command-tools), mantenendo la struttura:

```text
~/fuorigiri-tools/android-sdk/cmdline-tools/latest/bin/sdkmanager
```

Nella sessione riuscita: `commandlinetools-linux-15859902_latest.zip`, SDK Manager 22.0, SHA-256 ZIP `4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583`. Se si usa un’altra versione, verificare il suo checksum ufficiale, non quello di questo ZIP.

Per quel file esatto, dalla cartella dove è stato scaricato, installare una sola volta:

```bash
python3 - <<'PY'
import hashlib
import pathlib
import tempfile
import zipfile

archive = pathlib.Path('commandlinetools-linux-15859902_latest.zip')
expected = '4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583'
with archive.open('rb') as stream:
    actual = hashlib.file_digest(stream, 'sha256').hexdigest()
if actual != expected:
    raise SystemExit('Checksum Command-line Tools non valido')
parent = pathlib.Path.home() / 'fuorigiri-tools/android-sdk/cmdline-tools'
parent.mkdir(parents=True, exist_ok=True)
target = parent / 'latest'
if target.exists():
    raise SystemExit(f'Destinazione già presente: {target}; non sovrascritta')
with tempfile.TemporaryDirectory(dir=parent) as temporary:
    extracted = pathlib.Path(temporary)
    with zipfile.ZipFile(archive) as source:
        source.extractall(extracted)
    tools = extracted / 'cmdline-tools'
    if not (tools / 'bin/sdkmanager').is_file():
        raise SystemExit('Struttura Command-line Tools inattesa')
    for executable in (tools / 'bin').iterdir():
        if executable.is_file():
            executable.chmod(executable.stat().st_mode | 0o111)
    tools.rename(target)
print(f'Command-line Tools verificati: {target}')
PY
```

Poi preparare piattaforma e NDK:

```bash
export JAVA_HOME="$HOME/fuorigiri-tools/jdk-21"
export ANDROID_HOME="$HOME/fuorigiri-tools/android-sdk"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"

sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-35" "build-tools;35.0.0" "ndk;27.3.13750724"
```

Leggere e accettare interattivamente le licenze. L’avviso di deprecazione di sdkmanager 22.0 non aveva impedito l’uso. NDK effettivo del builder: **27.3.13750724**. API 26 è il minimo delle wheel, API 35 la piattaforma di compilazione dell’app: non sono in conflitto.

Installare rustup separatamente, anche se esiste `/usr/bin/rustc`:

```bash
export CARGO_HOME="$HOME/fuorigiri-tools/rust/cargo"
export RUSTUP_HOME="$HOME/fuorigiri-tools/rust/rustup"
curl --fail --location https://sh.rustup.rs -o "$HOME/fuorigiri-tools/rustup-init.sh"
sh "$HOME/fuorigiri-tools/rustup-init.sh" -y --no-modify-path --profile minimal --default-toolchain 1.99.1
export PATH="$CARGO_HOME/bin:$PATH"
export RUSTUP_TOOLCHAIN=1.99.1
rustup target add x86_64-linux-android aarch64-linux-android
```

Rust realmente usato: **1.99.1**, rustup **1.29.1**. In origine fu installato `stable`, che allora risolveva a 1.99.1; per ricostruire usare la versione esplicita. Il download futuro di rustup può cambiare versione: registrarla. Non installare wheel Android nella venv host: maturin, setuptools e il CFFI che genera codice devono poter funzionare su Linux.

## 4. Riprendere una sessione: passaggio obbligatorio

Salvare il seguente blocco come `~/fuorigiri-android-build/ambiente.sh` e caricarlo con `source "$HOME/fuorigiri-android-build/ambiente.sh"` a ogni ingresso nella Toolbox:

```bash
cd "$HOME/fuorigiri-android-build"
source .venv/bin/activate
export JAVA_HOME="$HOME/fuorigiri-tools/jdk-21"
export ANDROID_HOME="$HOME/fuorigiri-tools/android-sdk"
export ANDROID_NDK_ROOT="$ANDROID_HOME/ndk/27.3.13750724"
export CARGO_HOME="$HOME/fuorigiri-tools/rust/cargo"
export RUSTUP_HOME="$HOME/fuorigiri-tools/rust/rustup"
export RUSTUP_TOOLCHAIN=1.99.1
export ANDROID_API_LEVEL=26
export PATH="$CARGO_HOME/bin:$JAVA_HOME/bin:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$ANDROID_NDK_ROOT/toolchains/llvm/prebuilt/linux-x86_64/bin:$PATH"
hash -r
set -o pipefail
```

Verificare prima di compilare:

```bash
command -v rustc cargo rustup
rustc --version
rustup target list --installed
java -version
javac -version
sdkmanager --version
```

Rust e Cargo devono provenire da `fuorigiri-tools/rust/cargo/bin`, non da `/usr/bin`. Questo controllo evita l’errore **E0463: can't find crate for core** incontrato quando una nuova sessione aveva perso il PATH corretto.

## 5. Sorgenti e configurazione cibuildwheel

Dal builder nuovo, senza sovrascrivere directory già lavorate:

```bash
cd "$HOME/fuorigiri-android-build"
git clone --depth 1 --branch v2.41.4 https://github.com/pydantic/pydantic-core.git pydantic-core-2.41.4
git clone --depth 1 --branch v2.0.0 https://github.com/python-cffi/cffi.git cffi-2.0.0
git clone --depth 1 --branch 50.0.2 https://github.com/pyca/cryptography.git cryptography-50.0.2
git clone --depth 1 --branch v3.8.0 https://github.com/libffi/libffi.git libffi-3.8.0

mkdir -p downloads wheelhouse
cd downloads
curl --fail --location --remote-name https://github.com/openssl/openssl/releases/download/openssl-3.5.9/openssl-3.5.9.tar.gz
curl --fail --location --remote-name https://github.com/openssl/openssl/releases/download/openssl-3.5.9/openssl-3.5.9.tar.gz.sha256
python - <<'PY'
import hashlib
from pathlib import Path
p = Path('openssl-3.5.9.tar.gz')
expected = Path(str(p) + '.sha256').read_text().split()[0]
with p.open('rb') as stream:
    actual = hashlib.file_digest(stream, 'sha256').hexdigest()
if actual != expected.lower():
    raise SystemExit('Checksum OpenSSL non valido')
print('Checksum OpenSSL valido')
PY
```

Solo dopo esito positivo estrarre il sorgente in una destinazione nuova:

```bash
cd "$HOME/fuorigiri-android-build"
test ! -e openssl-3.5.9 && tar -xzf downloads/openssl-3.5.9.tar.gz
cat > build-android.toml <<'TOML'
[tool.cibuildwheel]
build-frontend = "build"
test-command = ""
TOML
```

`test-command` vuoto produce i binari ma non esegue test runtime Android. Annotare i commit effettivi con `git -C <directory-sorgente> rev-parse HEAD`; conservare anche digest di archivi/toolchain e log. I tag da soli non sostituiscono una distinta dei sorgenti.

## 6. pydantic-core, entrambe le ABI

```bash
python -m cibuildwheel pydantic-core-2.41.4 --only cp313-android_x86_64 --config-file build-android.toml --output-dir wheelhouse 2>&1 | tee pydantic-core-x86_64.log
```

Attendere il successo prima del secondo comando:

```bash
python -m cibuildwheel pydantic-core-2.41.4 --only cp313-android_arm64_v8a --config-file build-android.toml --output-dir wheelhouse 2>&1 | tee pydantic-core-arm64.log
```

## 7. OpenSSL statico per ciascuna ABI

Eseguire dalla radice del builder. Il blocco interrompe il lavoro al primo errore; non usa OpenSSL Fedora come libreria target.

```bash
(
set -eu
root="$PWD"
for abi in x86_64 arm64; do
  build="$root/openssl-build-$abi"
  prefix="$root/openssl-android-$abi"
  mkdir -p "$build"
  cd "$build"
  perl "$root/openssl-3.5.9/Configure" "android-$abi" \
    -D__ANDROID_API__=26 no-shared no-module no-tests -fPIC \
    --prefix="$prefix" --libdir=lib
  make -j4
  make install_dev
done
) 2>&1 | tee openssl-android.log
```

Controllare `include/openssl/ssl.h`, `lib/libcrypto.a` e `lib/libssl.a` nei due prefissi. L’esistenza di `libcrypto.a` di circa 12 MB era stata verificata dall’utente. Sono archivi Android, non eseguibili host.

## 8. libffi statica per ciascuna ABI

```bash
(
set -eu
root="$PWD"
ndk_bin="$ANDROID_NDK_ROOT/toolchains/llvm/prebuilt/linux-x86_64/bin"
cd "$root/libffi-3.8.0"
./autogen.sh
for abi in x86_64 arm64; do
  if [ "$abi" = x86_64 ]; then
    triplet=x86_64-linux-android
  else
    triplet=aarch64-linux-android
  fi
  prefix="$root/libffi-android-$abi"
  mkdir -p "$root/libffi-build-$abi"
  cd "$root/libffi-build-$abi"
  CC="$ndk_bin/${triplet}26-clang" \
  AR="$ndk_bin/llvm-ar" RANLIB="$ndk_bin/llvm-ranlib" \
  CFLAGS="-O2 -fPIC" \
  "$root/libffi-3.8.0/configure" \
    --host="$triplet" --build="$(gcc -dumpmachine)" \
    --prefix="$prefix" --libdir="$prefix/lib" \
    --disable-shared --enable-static
  make -j4
  make install
done
) 2>&1 | tee libffi-android.log
```

Controllare `include/ffi.h`, `include/ffitarget.h` e `lib/libffi.a` nei due prefissi. I file statici osservati erano circa 93 KB x86_64 e 118 KB ARM64.

## 9. CFFI: preparazione del prefisso target

I tentativi basati soltanto su CFLAGS/LDFLAGS/PKG_CONFIG fallivano: cibuildwheel riassegna queste variabili quando prepara Android. La procedura riuscita copia header e libreria **Android dell’ABI corretta** nel prefisso temporaneo già usato dal compilatore e dal linker. Non modifica CFFI né la libffi del sistema.

Creare `prepare-cffi-android.py` nella radice del builder:

```python
import pathlib
import shutil
import sysconfig

root = pathlib.Path.cwd()
platform = sysconfig.get_platform()
if not platform.startswith('android-'):
    raise SystemExit(f'Ambiente non Android: {platform}')
if 'x86_64' in platform:
    abi = 'x86_64'
elif 'arm64' in platform or 'aarch64' in platform:
    abi = 'arm64'
else:
    raise SystemExit(f'Architettura inattesa: {platform}')
prefix = pathlib.Path(sysconfig.get_config_var('prefix')).resolve()
if 'cibw-run-' not in str(prefix):
    raise SystemExit(f'Prefisso temporaneo inatteso: {prefix}')
source = root / f'libffi-android-{abi}'
files = ['include/ffi.h', 'include/ffitarget.h', 'lib/libffi.a']
for name in files:
    if not (source / name).is_file():
        raise SystemExit(f'File mancante: {source / name}')
for name in files:
    target = prefix / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / name, target)
print(f'Libffi Android {abi} preparata in {prefix}', flush=True)
```

Il programma deve girare dalla radice del builder; non dalla cartella del sorgente CFFI. Creare configurazione e compilare una ABI alla volta:

```bash
cat > build-cffi-android.toml <<'TOML'
[tool.cibuildwheel]
build-frontend = "build"
test-command = ""
before-build = "python {project}/prepare-cffi-android.py"
TOML

CIBW_ENVIRONMENT="" python -m cibuildwheel cffi-2.0.0 --only cp313-android_x86_64 --config-file build-cffi-android.toml --output-dir wheelhouse 2>&1 | tee cffi-android-x86_64.log
```

Dopo il successo:

```bash
CIBW_ENVIRONMENT="" python -m cibuildwheel cffi-2.0.0 --only cp313-android_arm64_v8a --config-file build-cffi-android.toml --output-dir wheelhouse 2>&1 | tee cffi-android-arm64.log
```

## 10. Cryptography: header Python target e OpenSSL

È stato necessario un secondo adattamento di layout: il build di cryptography deduceva `python/include/lib`, dove non trovava Python.h. Si rendono gli header target disponibili anche nel `prefix/include` già presente nei flag. Non si usano gli header di Python Fedora e non si modificano i sorgenti cryptography.

Creare `prepare-crypto-headers.py` nella radice del builder:

```python
import pathlib
import shutil
import sysconfig

platform = sysconfig.get_platform()
if not platform.startswith('android-'):
    raise SystemExit(f'Ambiente inatteso: {platform}')
prefix = pathlib.Path(sysconfig.get_config_var('prefix')).resolve()
source = pathlib.Path(sysconfig.get_path('include')).resolve()
destination = prefix / 'include'
if 'cibw-run-' not in str(prefix):
    raise SystemExit(f'Prefisso temporaneo inatteso: {prefix}')
if not source.is_relative_to(prefix):
    raise SystemExit(f'Header esterni al Python Android: {source}')
if not (source / 'Python.h').is_file():
    raise SystemExit(f'Python.h non trovato in {source}')
if source != destination:
    shutil.copytree(source, destination, dirs_exist_ok=True)
print(f'Header Android: {source} -> {destination}', flush=True)
```

Configurazione e vincolo della dipendenza di build host:

```bash
printf 'cffi==2.0.0\n' > cryptography-build-constraints.txt
cat > build-cryptography-android.toml <<'TOML'
[tool.cibuildwheel]
build-frontend = "build"
test-command = ""
before-build = "python {project}/prepare-crypto-headers.py"
TOML
```

Cryptography richiede CFFI anche durante la generazione del codice: il pip del builder installerà CFFI **host**. Le wheel Android nella wheelhouse servono invece all’app. Eseguire prima x86_64:

```bash
(
set -eu
openssl_prefix="$PWD/openssl-android-x86_64"
test -f "$openssl_prefix/include/openssl/ssl.h"
test -f "$openssl_prefix/lib/libcrypto.a"
test -f "$openssl_prefix/lib/libssl.a"
CIBW_ENVIRONMENT="OPENSSL_DIR='$openssl_prefix' OPENSSL_STATIC=1 OPENSSL_NO_VENDOR=1 PIP_CONSTRAINT='$PWD/cryptography-build-constraints.txt' PIP_FIND_LINKS='$PWD/wheelhouse' RUSTFLAGS='-C link-arg=-Wl,-z,max-page-size=16384'" \
python -m cibuildwheel cryptography-50.0.2 \
  --only cp313-android_x86_64 \
  --config-file build-cryptography-android.toml --output-dir wheelhouse
) 2>&1 | tee cryptography-android-x86_64.log
```

Poi ARM64, cambiando sia ABI sia prefisso OpenSSL:

```bash
(
set -eu
openssl_prefix="$PWD/openssl-android-arm64"
test -f "$openssl_prefix/include/openssl/ssl.h"
test -f "$openssl_prefix/lib/libcrypto.a"
test -f "$openssl_prefix/lib/libssl.a"
CIBW_ENVIRONMENT="OPENSSL_DIR='$openssl_prefix' OPENSSL_STATIC=1 OPENSSL_NO_VENDOR=1 PIP_CONSTRAINT='$PWD/cryptography-build-constraints.txt' PIP_FIND_LINKS='$PWD/wheelhouse' RUSTFLAGS='-C link-arg=-Wl,-z,max-page-size=16384'" \
python -m cibuildwheel cryptography-50.0.2 \
  --only cp313-android_arm64_v8a \
  --config-file build-cryptography-android.toml --output-dir wheelhouse
) 2>&1 | tee cryptography-android-arm64.log
```

Il flag di allineamento non dimostra da solo compatibilità 16 KB dell’intero APK. Preservare log di repair/audit; per x86_64 il report ricevuto conferma baseline ABI3 3.13 senza simboli estranei. Non rinominare le wheel `cp313-abi3` in `cp313-cp313`.

## 10 bis. Riparazione ABI3 necessaria prima dell’uso con Chaquopy

**Blocco runtime scoperto dopo la prima build APK:** le due wheel cryptography prodotte sopra superavano il packaging, e x86_64 anche abi3audit, ma `_rust.abi3.so` dichiarava soltanto libdl.so/libc.so come dipendenze ELF. Mancava il collegamento esplicito a libpython. Su emulatore l’import falliva con `cannot locate symbol PyType_GetFlags`. Il simbolo è esportato da libpython3.13.so dell’APK; il problema non è una versione Python priva di quel simbolo.

Chaquopy 17.1 include libpython3.so per i moduli ABI3. Aggiungere il relativo DT_NEEDED è un passaggio di riparazione del collegamento, non una modifica degli algoritmi o un downgrade. Questa fase è necessaria per gli artefatti ricevuti; non va applicata a future wheel già correttamente collegate. [Contesto ufficiale](https://github.com/chaquo/chaquopy/issues/1380).

La repository include `scripts/repair_android_abi3.py`, eseguibile anche su Windows. Richiede **LIEF 1.0.0** soltanto come strumento di build; non aggiungerlo alle dipendenze dell’app. Esempio dalla radice della repository in PowerShell, dopo aver trasferito le wheel originali:

```powershell
.venv/Scripts/python.exe -m pip install --only-binary=:all: --target tmp/android-elf-tools lief==1.0.0
$env:PYTHONPATH = "$PWD/tmp/android-elf-tools"
.venv/Scripts/python.exe scripts/repair_android_abi3.py android/wheels/cryptography-50.0.2-cp313-abi3-android_26_x86_64.whl tmp/repair-x86_64-nuovo
.venv/Scripts/python.exe scripts/repair_android_abi3.py android/wheels/cryptography-50.0.2-cp313-abi3-android_26_arm64_v8a.whl tmp/repair-arm64-nuovo
```

Le directory di destinazione devono essere nuove. Non applicare ai file già riparati presenti oggi: lo script rifiuta moduli con dipendenza Python già dichiarata. Funziona analogamente su Fedora usando python e percorsi Linux, dal clone della repository.

Lo script conserva l’input, aggiunge libpython3.so al modulo ELF, verifica che `.text` e architettura non cambino e che i segmenti LOAD restino allineati a 16 KB, rigenera RECORD della wheel (senza righe per le directory) e scrive `repair.json` con hash originali/corretti, tool e dipendenze prima/dopo. I controlli strutturali non sostituiscono abi3audit o il test Android.

Prima di sostituire una wheel in android/wheels, conservare l’originale in una cartella distinta e verificare il report e RECORD. Registrare i report in `android/wheels/ABI3_REPAIR.json` e i digest approvati in SHA256.json, quindi eseguire nuovamente il gate. I report presenti registrano questa riparazione dei due originali Fedora; una futura ricostruzione deve mantenere la propria provenienza. Non aggiornare silenziosamente gli hash per aggirare un errore.

Le task Gradle install*PythonRequirements dichiarano ora wheel e manifest come input: modificare una wheel locale deve reinstallare i requisiti, evitando di riutilizzare una copia precedente nell’APK. La prima prova aveva mostrato UP-TO-DATE anche dopo la sostituzione; il solo Run non bastava prima di questa correzione.

## 11. Conservazione e trasferimento su Windows

```bash
ls -lh wheelhouse/*.whl
sha256sum wheelhouse/*.whl
(cd wheelhouse && sha256sum *.whl > SHA256SUMS.txt)
```

Attesi sei file, circa 15 MB complessivi. Copiare i sei `.whl`, senza rinominarli, in `android/wheels/` della repository Windows. Se provengono dalla prima ricetta Fedora originale, applicare poi la riparazione cryptography del punto 10 bis prima del gate; non sovrascrivere nuovamente le wheel riparate con gli originali. Conservare altrove sorgenti/commit, archivi originali con checksum, i due hook, configurazioni TOML, `ambiente.sh`, freeze e log. Non occorre trasferire al progetto le directory temporanee o l’intero SDK. I binari wheel sono ignorati da Git; il manifest JSON è versionato.

Gli hash correnti in repository rappresentano le wheel approvate, comprese quelle riparate; gli originali cryptography sono tracciati in ABI3_REPAIR.json: una ricompilazione può produrre digest diversi. In quel caso non sostituirli automaticamente con quelli del download; registrare provenienza e verifiche della nuova build prima di approvare il nuovo manifest. Un checksum confrontato con il manifest del builder rileva alterazioni nel trasferimento, non certifica la sicurezza o il corretto comportamento della libreria.

Dal terminale **PowerShell di Android Studio, cartella android**, controllare i file:

```powershell
..\.venv\Scripts\python.exe -c "import runpy; m=runpy.run_path('../scripts/build_android.py'); p=m['check_wheels'](); print('\n'.join(p) if p else 'Tutte le sei wheel verificate'); raise SystemExit(bool(p))"
```

Poi compilare solo se il controllo termina con successo, frontend già compilato e IDE configurato con **JDK 21**, **Gradle wrapper 8.13**, SDK 35 e Python host 3.13:

```powershell
.\gradlew.bat :app:assembleDebug --stacktrace
```

Questa chiamata Gradle diretta non esegue il gate Python automaticamente: non saltare il controllo precedente. In alternativa `scripts/build_android.py --check --gradle <wrapper>` dalla radice controlla anche versioni, frontend e variabili SDK/JDK, se configurate nella sessione. Il successo delle sei wheel non assicura la risoluzione di tutte le altre dipendenze Chaquopy.

## 12. Diagnosi e verifiche residue

| Errore | Causa osservata / azione corretta |
|---|---|
| `java: comando non trovato` | Ripristinare JAVA_HOME/PATH; JDK 21 nell’archivio locale, non insistere sui pacchetti Fedora assenti. |
| `rustup: comando non trovato` o E0463 `core` | Caricare ambiente.sh, controllare command -v e target della toolchain effettiva. Non basta che il target sia installato in un altro Rust. |
| `ffi.h` assente / `unable to find library -lffi` | Usare l’hook CFFI e i file Android nel prefisso temporaneo; installare libffi Fedora non risolve il target. |
| `Python.h` assente in cryptography | Usare l’hook header Python target; niente include host o percorsi temporanei fissati a mano. |
| `NameError: name 'file' is not defined` | Copia dello script alterata: usare il codice qui riportato con Path.cwd(), evitando conversioni da testo formattato. |
| Il log termina solo con exit status 1 | Cercare il primo errore del compilatore, non soltanto il riepilogo maturin. |

Esempio senza ripetere la build:

```bash
grep -n -B 8 -A 15 -m 4 -E 'fatal error:|error:|error occurred|error\[E0463\]' cryptography-android-x86_64.log
```

Non incollare nel terminale il prompt o i delimitatori Markdown. Ogni file Python/TOML va salvato come testo semplice. Dopo un errore fermarsi prima della fase successiva; non cancellare output o sorgenti per tentare di risolverlo. Per aggiornare versioni usare un builder/output separato e ripetere i controlli.

Esito successivo: installazione/avvio e test nativo import, Fernet, Ed25519, API e Keystore verificati sull’emulatore API 35 x86_64. Accettazione ancora aperta: telefono ARM64, equivalenza con desktop e flussi completi offline/import FIT/grafici/PDF, memoria/pagine 16 KB e provider cloud reali. Nessuna release firmata o pubblicazione è inclusa nella produzione di queste wheel.

## Fonti tecniche

- [cibuildwheel: piattaforma Android](https://cibuildwheel.pypa.io/en/stable/platforms/#android).
- [Ambiente Android di cibuildwheel](https://github.com/pypa/cibuildwheel/blob/main/cibuildwheel/platforms/android.py): ordine di preparazione delle variabili.
- [Rustup: variabili dell’ambiente](https://rust-lang.github.io/rustup/environment-variables.html) e [E0463](https://doc.rust-lang.org/error_codes/E0463.html).
- [OpenSSL: note Android](https://github.com/openssl/openssl/blob/master/NOTES-ANDROID.md).
- [CFFI 2.0.0: setup](https://github.com/python-cffi/cffi/blob/v2.0.0/setup.py).
- [Cryptography 50.0.2: requisiti](https://github.com/pyca/cryptography/blob/50.0.2/pyproject.toml) e [build CFFI](https://github.com/pyca/cryptography/blob/50.0.2/src/rust/cryptography-cffi/build.rs).
