"""Freeze a local candidate without signing, publishing or overwriting old deliveries."""

import argparse
import hashlib
import json
import platform
import re
import shutil
import subprocess
import struct
import zipfile
from importlib.metadata import distributions
from pathlib import Path
from verify_versions import verify
from build_android import check_wheels

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def checked_zip(path):
    with zipfile.ZipFile(path) as archive:
        error = archive.testzip()
        if error:
            raise ValueError(f'ZIP corrotto: {path.name}: {error}')


def write_source_archive(root, destination, prefix):
    names = subprocess.check_output(['git', 'ls-files', '--cached', '-z'], cwd=root).decode('utf-8').split('\0')
    resources = []
    with zipfile.ZipFile(destination, 'x', zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
        for name in sorted(filter(None, names)):
            path = root / name
            if name == 'bundle-resources.json' or not path.is_file():
                continue
            if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
                raise ValueError('Collegamento non ammesso nello snapshot: ' + name)
            if path.name in {'identity.json', '.env', 'keystore.properties'} or path.suffix.lower() in {
                '.jks',
                '.keystore',
                '.p12',
                '.pfx',
            }:
                raise ValueError('Materiale riservato tra i sorgenti: ' + name)
            archive.write(path, arcname=f'{prefix}/{name}')
            if name.startswith(('docs/', 'examples/')):
                resources.append(name)
        # Permit a desktop build from the extracted source archive without .git.
        archive.writestr(f'{prefix}/bundle-resources.json', json.dumps(resources, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--label', required=True)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--installer', type=Path, required=True)
    parser.add_argument('--apk', type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9.-]{0,80}', args.label):
        parser.error('Label non valida')
    version = verify(ROOT)
    for path in [args.installer, args.apk, args.bundle / 'Fuorigiri.exe']:
        if not path.is_file():
            raise SystemExit(f'Input mancante: {path}')
    missing = check_wheels()
    if missing:
        raise SystemExit('Wheel native non verificate: ' + ', '.join(missing))
    output = args.output.resolve()
    if output.exists():
        raise SystemExit('Destinazione già presente: conservata senza modifiche.')
    checked_zip(args.apk)
    # Confirm input is an unsigned APK, not an existing debug/signed build.
    with args.apk.open('rb') as source:
        source.seek(max(0, args.apk.stat().st_size - 65557))
        tail = source.read()
        eocd = tail.rfind(b'PK\x05\x06')
        if eocd < 0:
            raise ValueError('EOCD APK mancante')
        central = struct.unpack_from('<I', tail, eocd + 16)[0]
        if central >= 16:
            source.seek(central - 16)
            if source.read(16) == b'APK Sig Block 42':
                raise ValueError('APK già firmato v2/v3: atteso input non firmato')
    with zipfile.ZipFile(args.apk) as apk:
        if any(re.fullmatch(r'META-INF/.*\.(RSA|DSA|EC)', n, re.I) for n in apk.namelist()):
            raise SystemExit('APK con firma JAR: fornire il release non firmato verificato con apksigner.')
        if not {'lib/arm64-v8a/libpython3.13.so', 'lib/x86_64/libpython3.13.so', 'assets/index.html'} <= set(
            apk.namelist()
        ):
            raise SystemExit('APK privo di ABI/runtime/UI richiesti.')
    output.mkdir(parents=True)
    prefix = f'Fuorigiri-{version}'
    shutil.copy2(args.installer, output / f'{prefix}-windows-x64-setup.exe')
    shutil.copy2(args.apk, output / f'{prefix}-android-release-unsigned.apk')
    portable = output / f'{prefix}-windows-x64-portable.zip'
    with zipfile.ZipFile(portable, 'w', zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
        for path in sorted(args.bundle.rglob('*')):
            if path.is_file():
                archive.write(path, arcname='Fuorigiri/' + path.relative_to(args.bundle).as_posix())
    sources = output / f'{prefix}-sources.zip'
    write_source_archive(ROOT, sources, prefix)
    wheels = ROOT / 'android/wheels'
    native = output / f'{prefix}-android-native-wheels.zip'
    hashes = json.loads((wheels / 'SHA256.json').read_text(encoding='utf-8'))
    with zipfile.ZipFile(native, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
        for name, expected in sorted(hashes.items()):
            path = wheels / name
            if Path(name).name != name or not path.is_file() or digest(path) != expected:
                raise ValueError('Manifest wheel incoerente')
            archive.write(path, arcname='android/wheels/' + name)
        for name in ['SHA256.json', 'ABI3_REPAIR.json', 'PILLOW_BUILD.json', 'README.md']:
            archive.write(wheels / name, arcname='android/wheels/' + name)
    for name in ['COLLAUDO_PILOT.md', 'FIRMA_ANDROID.md']:
        shutil.copy2(ROOT / 'docs' / name, output / name)
    for name in ['LICENSE', 'THIRD_PARTY.md', 'CHANGELOG.md']:
        shutil.copy2(ROOT / name, output / name)
    (output / 'LEGGIMI.md').write_text(
        f'''# Fuorigiri {version} — {args.label}

Candidato locale, non pubblicato. Windows: installer o ZIP portabile (estrarre l’intera cartella, non il solo EXE). Dipendenze incluse; Windows pulito ancora da collaudare.

Android: APK release NON FIRMATO, non installabile prima della firma. Nessuna chiave generata. Seguire FIRMA_ANDROID.md e poi COLLAUDO_PILOT.md. I pacchetti non sono firmati Authenticode.

Sorgenti: snapshot dei file tracciati nel working tree e lista delle risorse desktop; il commit base non include da solo tutte le modifiche. Native wheels: archivio separato da estrarre nella radice dei sorgenti per ricostruire Android. Non contiene l’intera cache delle dipendenze PyPI/Gradle: una ricostruzione completamente offline non è garantita.

SHA256SUMS.txt verifica i file originali; candidate.json riporta provenienza e gate aperti. Dopo la firma conservare il nuovo APK e il suo digest come derivati, senza riscrivere i checksum originali. Nessuna qualifica automatica di telefono, cloud o correttezza biologica.
''',
        encoding='utf-8',
    )
    for path in output.glob('*.zip'):
        checked_zip(path)
    files = {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size} for p in sorted(output.iterdir()) if p.is_file()}
    manifest = {
        'product': 'Fuorigiri Performance Lab',
        'version': version,
        'candidate': args.label,
        'status': 'local-candidate-pending-acceptance',
        'published': False,
        'signed': False,
        'android_installable': False,
        'git_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'working_tree_dirty': bool(
            subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip()
        ),
        'source_snapshot': 'working-tree-zip',
        'builder_python': platform.python_version(),
        'builder_platform': platform.platform(),
        'python_distributions': {d.metadata['Name']: d.version for d in distributions() if d.metadata['Name']},
        'files': files,
        'open_gates': [
            'Android release signing by owner',
            'Windows clean-machine acceptance',
            'Physical ARM64 Android and 16 KB qualification',
            'Real provider/two-account Windows-Android sync',
            'Scientific external validation where applicable',
        ],
        'limitations': [
            'Local smoke is not clean-machine acceptance',
            'Source archive plus wheels are not a full offline dependency mirror',
            'Windows installer is not Authenticode signed',
            'No automatic rollback of data migrations',
        ],
    }
    (output / 'candidate.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    hashes = {p.name: digest(p) for p in sorted(output.iterdir()) if p.is_file()}
    (output / 'SHA256SUMS.txt').write_text(
        ''.join(f'{sha}  {name}\n' for name, sha in hashes.items()), encoding='utf-8'
    )
    print('Candidato congelato:', output)
    for name, entry in files.items():
        if name.endswith(('.exe', '.zip', '.apk')):
            print(name, entry['bytes'], 'byte')


if __name__ == '__main__':
    main()
