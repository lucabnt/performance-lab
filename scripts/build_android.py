"""Build Android on an SDK/JDK-equipped builder. No signing key is generated.

Native Android wheels are a release gate, not optional substitutes for validators.
Run --check to inspect prerequisites without Gradle or network operations.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import tomllib
from pathlib import Path

root=Path(__file__).resolve().parents[1]
NATIVE_REQUIRED={'pydantic_core':'2.41.4','cryptography':'50.0.2','cffi':'2.0.0','pillow':'13.0.0'}
ABIS=('arm64_v8a','x86_64')


def check_wheels():
    directory=root/'android/wheels';manifest=directory/'SHA256.json'
    hashes=json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else {}
    missing=[]
    for package,version in NATIVE_REQUIRED.items():
        for abi in ABIS:
            files=list(directory.glob(f'{package}-{version}-*android_*_{abi}.whl'))
            valid=[p for p in files if p.name in hashes and hashlib.sha256(p.read_bytes()).hexdigest()==hashes[p.name]]
            if not valid:missing.append(f'{package} {version} / {abi} (wheel Android + SHA256 verificato)')
    return missing


def main():
    parser=argparse.ArgumentParser(description='Compila Fuorigiri Android con il motore Python condiviso')
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--gradle',default=shutil.which('gradle') or '')
    parser.add_argument('--release',action='store_true',help='Produce APK release non firmato; firma separata con chiave del titolare')
    args=parser.parse_args()
    from verify_versions import verify
    verify(root)
    problems=check_wheels()
    if not (root/'frontend/dist/index.html').is_file():problems.append('Interfaccia compilata con npm ci && npm run build')
    sdk=Path(os.environ.get('ANDROID_HOME',os.environ.get('ANDROID_SDK_ROOT','__missing__')))
    if not (sdk/'platforms/android-35/android.jar').exists():problems.append('Android SDK platform 35 (ANDROID_HOME), build-tools e licenze SDK configurati sul builder')
    jdk=Path(os.environ.get('JAVA_HOME','__missing__'))
    if not any((jdk/'bin'/name).exists() for name in ('javac','javac.exe')):problems.append('JDK 17 o 21 completo (JAVA_HOME), non solo JRE')
    if not args.gradle:problems.append('Gradle 8.13')
    from scan_build_paths import scan
    if args.release and scan([root/'android/wheels'],strict=True):
        problems.append('Wheel native con percorsi del builder: ricostruirle da radice neutra (scan_build_paths.py --strict android/wheels)')
    if problems:raise SystemExit('Build Android non ancora disponibile:\n- '+'\n- '.join(problems))
    if args.check:
        print('Prerequisiti presenti. Non equivale a compilazione, installazione o collaudo su dispositivo.');return
    subprocess.run([args.gradle,'--no-daemon','assembleRelease' if args.release else 'assembleDebug'],cwd=root/'android',check=True)
    version=tomllib.loads((root/'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
    mode='release' if args.release else 'debug'
    candidates=list((root/f'android/app/build/outputs/apk/{mode}').glob('*.apk'))
    if not candidates:raise SystemExit('Gradle non ha prodotto un APK.')
    if args.release:
        # Distributed APKs must not carry builder homes or this checkout path.
        leaks=scan(candidates,extra=[str(root)])
        if leaks:
            raise SystemExit('APK con percorsi del builder, non copiato in dist/release:\n- '+'\n- '.join(sorted(leaks)))
    release=root/'dist/release';release.mkdir(parents=True,exist_ok=True)
    for apk in candidates:shutil.copy2(apk,release/f'Fuorigiri-{version}-android-{mode}.apk')
    print('APK copiato in dist/release. Debug non è un rilascio operativo; release richiede firma e collaudo.')


if __name__=='__main__':main()
