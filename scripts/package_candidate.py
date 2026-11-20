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


def check_unsigned_apk(apk):
    checked_zip(apk)
    # Confirm input is an unsigned APK, not an existing debug/signed build.
    with apk.open('rb') as source:
        source.seek(max(0, apk.stat().st_size - 65557))
        tail = source.read()
        eocd = tail.rfind(b'PK\x05\x06')
        if eocd < 0:
            raise ValueError('EOCD APK mancante')
        central = struct.unpack_from('<I', tail, eocd + 16)[0]
        if central >= 16:
            source.seek(central - 16)
            if source.read(16) == b'APK Sig Block 42':
                raise ValueError('APK già firmato v2/v3: atteso input non firmato')
    with zipfile.ZipFile(apk) as archive:
        if any(re.fullmatch(r'META-INF/.*\.(RSA|DSA|EC)', n, re.I) for n in archive.namelist()):
            raise SystemExit('APK con firma JAR: fornire il release non firmato verificato con apksigner.')
        if not {'lib/arm64-v8a/libpython3.13.so', 'lib/x86_64/libpython3.13.so', 'assets/index.html'} <= set(
            archive.namelist()
        ):
            raise SystemExit('APK privo di ABI/runtime/UI richiesti.')


def write_native_wheels(destination):
    wheels = ROOT / 'android/wheels'
    hashes = json.loads((wheels / 'SHA256.json').read_text(encoding='utf-8'))
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
        for name, expected in sorted(hashes.items()):
            path = wheels / name
            if Path(name).name != name or not path.is_file() or digest(path) != expected:
                raise ValueError('Manifest wheel incoerente')
            archive.write(path, arcname='android/wheels/' + name)
        for name in ['SHA256.json', 'ABI3_REPAIR.json', 'PILLOW_BUILD.json', 'README.md']:
            archive.write(wheels / name, arcname='android/wheels/' + name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--label', required=True)
    # A candidate covers Windows (--bundle with --installer), Android (--apk) or both.
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--installer', type=Path)
    parser.add_argument('--apk', type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9.-]{0,80}', args.label):
        parser.error('Label non valida')
    windows = args.bundle is not None or args.installer is not None
    if windows and (args.bundle is None or args.installer is None):
        parser.error('--bundle e --installer vanno indicati insieme')
    if not windows and args.apk is None:
        parser.error('Indicare Windows (--bundle e --installer), Android (--apk) o entrambi')
    version = verify(ROOT)
    inputs = ([args.installer, args.bundle / 'Fuorigiri.exe'] if windows else []) + ([args.apk] if args.apk else [])
    for path in inputs:
        if not path.is_file():
            raise SystemExit(f'Input mancante: {path}')
    if args.apk:
        missing = check_wheels()
        if missing:
            raise SystemExit('Wheel native non verificate: ' + ', '.join(missing))
    output = args.output.resolve()
    if output.exists():
        raise SystemExit('Destinazione già presente: conservata senza modifiche.')
    if args.apk:
        check_unsigned_apk(args.apk)
    output.mkdir(parents=True)
    prefix = f'Fuorigiri-{version}'
    if windows:
        shutil.copy2(args.installer, output / f'{prefix}-windows-x64-setup.exe')
        portable = output / f'{prefix}-windows-x64-portable.zip'
        with zipfile.ZipFile(portable, 'w', zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
            for path in sorted(args.bundle.rglob('*')):
                if path.is_file():
                    archive.write(path, arcname='Fuorigiri/' + path.relative_to(args.bundle).as_posix())
    if args.apk:
        shutil.copy2(args.apk, output / f'{prefix}-android-release-unsigned.apk')
        write_native_wheels(output / f'{prefix}-android-native-wheels.zip')
        shutil.copy2(ROOT / 'docs' / 'FIRMA_ANDROID.md', output / 'FIRMA_ANDROID.md')
    write_source_archive(ROOT, output / f'{prefix}-sources.zip', prefix)
    shutil.copy2(ROOT / 'docs' / 'COLLAUDO_PILOT.md', output / 'COLLAUDO_PILOT.md')
    for name in ['LICENSE', 'THIRD_PARTY.md', 'CHANGELOG.md']:
        shutil.copy2(ROOT / name, output / name)
    platforms = (['windows-x64'] if windows else []) + (['android'] if args.apk else [])
    parts = [
        f'# Fuorigiri {version} — {args.label}',
        'Candidato locale, non pubblicato. Piattaforme: ' + ', '.join(platforms) + '.',
    ]
    if windows:
        parts.append(
            'Windows: installer o ZIP portabile (estrarre l’intera cartella, non il solo EXE). Dipendenze incluse; '
            'Windows pulito ancora da collaudare. I pacchetti non sono firmati Authenticode.'
        )
    if args.apk:
        parts.append(
            'Android: APK release NON FIRMATO, non installabile prima della firma. Nessuna chiave generata. Seguire '
            'FIRMA_ANDROID.md e poi COLLAUDO_PILOT.md. Native wheels: archivio separato da estrarre nella radice dei '
            'sorgenti per ricostruire Android.'
        )
    parts += [
        'Sorgenti: snapshot dei file tracciati nel working tree e lista delle risorse desktop; il commit base non '
        'include da solo tutte le modifiche. Non contiene l’intera cache delle dipendenze PyPI/Gradle: una '
        'ricostruzione completamente offline non è garantita.',
        'SHA256SUMS.txt verifica i file originali; candidate.json riporta provenienza e gate aperti. Dopo la firma '
        'conservare il nuovo APK e il suo digest come derivati, senza riscrivere i checksum originali. Nessuna '
        'qualifica automatica di telefono, cloud o correttezza biologica.',
    ]
    (output / 'LEGGIMI.md').write_text('\n\n'.join(parts) + '\n', encoding='utf-8')
    for path in output.glob('*.zip'):
        checked_zip(path)
    files = {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size} for p in sorted(output.iterdir()) if p.is_file()}
    open_gates = ['Windows clean-machine acceptance'] if windows else []
    if args.apk:
        open_gates += ['Android release signing by owner', 'Physical ARM64 Android and 16 KB qualification']
    open_gates += ['Real provider/two-account Windows-Android sync', 'Scientific external validation where applicable']
    limitations = ['Source archive plus wheels are not a full offline dependency mirror']
    if windows:
        limitations += ['Local smoke is not clean-machine acceptance', 'Windows installer is not Authenticode signed']
    limitations.append('No automatic rollback of data migrations')
    manifest = {
        'product': 'Fuorigiri Performance Lab',
        'version': version,
        'candidate': args.label,
        'platforms': platforms,
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
        'open_gates': open_gates,
        'limitations': limitations,
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
