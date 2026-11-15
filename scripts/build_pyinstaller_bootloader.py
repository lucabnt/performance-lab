"""Compile the PyInstaller Windows bootloader locally (WIN-AV-02).

Downloads the sdist of the PyInstaller version installed in this interpreter,
verifies it against the SHA-256 published by PyPI, removes the prebuilt Windows
bootloaders, compiles new ones with the local MSVC toolchain (waf) and builds a
wheel in a new output directory. ``--install`` replaces PyInstaller in the
current environment with that wheel; ``--record`` writes the digests checked by
``scripts/build.py`` to packaging/windows/bootloader/PROVENIENZA.json.

A locally compiled bootloader only removes the binary shared by all PyInstaller
apps: it does not prove that Defender will accept the launcher.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from windows_launcher import BOOTLOADERS, PLATFORM, RECORD, installed_bootloaders, sha256  # noqa: E402

root = Path(__file__).resolve().parents[1]


def pypi_sdist(version: str) -> dict:
    with urllib.request.urlopen(f'https://pypi.org/pypi/pyinstaller/{version}/json', timeout=60) as response:
        data = json.load(response)
    sdists = [item for item in data['urls'] if item['packagetype'] == 'sdist']
    if len(sdists) != 1:
        raise SystemExit('Sdist PyInstaller non univoco su PyPI.')
    return sdists[0]


def msvc_version() -> str:
    vswhere = Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')) / (
        'Microsoft Visual Studio/Installer/vswhere.exe'
    )
    if not vswhere.is_file():
        raise SystemExit('vswhere non trovato: installare Visual Studio Build Tools con il carico C++.')
    output = subprocess.check_output(
        [
            str(vswhere),
            '-products',
            '*',
            '-requires',
            'Microsoft.VisualStudio.Component.VC.Tools.x86.x64',
            '-latest',
            '-property',
            'installationVersion',
        ],
        text=True,
    ).strip()
    if not output:
        raise SystemExit('Strumenti MSVC x64 non trovati.')
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        '--output', type=Path, required=True, help='Nuova cartella di lavoro; rifiuta destinazioni esistenti'
    )
    parser.add_argument('--install', action='store_true', help='Installa la wheel nel Python corrente')
    parser.add_argument('--record', action='store_true', help=f'Aggiorna {RECORD.as_posix()}')
    args = parser.parse_args()
    if sys.platform != 'win32':
        raise SystemExit('Il bootloader Windows si compila su Windows.')

    version, _ = installed_bootloaders()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    toolchain = msvc_version()

    meta = pypi_sdist(version)
    archive = output / meta['filename']
    with urllib.request.urlopen(meta['url'], timeout=300) as response, archive.open('wb') as handle:
        shutil.copyfileobj(response, handle)
    if sha256(archive) != meta['digests']['sha256']:
        raise SystemExit('SHA-256 dello sdist diverso da quello pubblicato da PyPI.')

    source = output / 'src'
    with tarfile.open(archive) as tar:
        tar.extractall(source, filter='data')
    (tree,) = source.iterdir()
    target = tree / 'PyInstaller/bootloader' / PLATFORM
    # The prebuilt binaries shipped in the sdist are the ones of the public wheel.
    stock = {name: sha256(target / name) for name in BOOTLOADERS if (target / name).is_file()}
    for name in BOOTLOADERS:
        (target / name).unlink(missing_ok=True)
    subprocess.run(
        [sys.executable, './waf', '--target-arch=64bit', 'configure', 'all'], cwd=tree / 'bootloader', check=True
    )
    compiled = {name: sha256(target / name) for name in BOOTLOADERS}
    reused = set(compiled.values()) & set(stock.values())
    if reused:
        raise SystemExit('La compilazione ha prodotto un bootloader identico a quello precompilato.')

    env = os.environ.copy()
    env.update({'PYI_PLATFORM': PLATFORM, 'PYI_WHEEL_TAG': 'win_amd64'})
    env.pop('PYINSTALLER_COMPILE_BOOTLOADER', None)
    wheels = output / 'wheel'
    subprocess.run(
        [sys.executable, '-m', 'pip', 'wheel', '--no-deps', '--wheel-dir', str(wheels), str(tree)],
        check=True,
        env=env,
    )
    (wheel,) = wheels.glob('*.whl')
    with zipfile.ZipFile(wheel) as content:
        for name, digest in compiled.items():
            data = content.read(f'PyInstaller/bootloader/{PLATFORM}/{name}')
            if hashlib.sha256(data).hexdigest() != digest:
                raise SystemExit(f'{name} nella wheel diverso dal bootloader compilato.')

    record = {
        'requirement': 'WIN-AV-02',
        'pyinstaller': version,
        'compiled_on': date.today().isoformat(),
        'sdist': {'filename': meta['filename'], 'sha256': meta['digests']['sha256'], 'url': meta['url']},
        'toolchain': {
            'msvc_build_tools': toolchain,
            'python': platform.python_version(),
            'waf': './waf --target-arch=64bit configure all',
        },
        'wheel': {'filename': wheel.name, 'sha256': sha256(wheel)},
        'bootloaders': {
            name: {'sha256': digest, 'bytes': (target / name).stat().st_size} for name, digest in compiled.items()
        },
        'stock_sha256': stock,
        'note': (
            'Bootloader compilato localmente dallo sdist verificato; non firmato Authenticode. '
            'Non dimostra da solo l’assenza di rilevamenti Defender.'
        ),
    }
    text = json.dumps(record, indent=2, ensure_ascii=False) + '\n'
    (output / 'PROVENIENZA.json').write_text(text, encoding='utf-8')
    if args.install:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--force-reinstall', '--no-deps', str(wheel)], check=True
        )
        if installed_bootloaders()[1] != compiled:
            raise SystemExit('Il PyInstaller installato non usa il bootloader appena compilato.')
    if args.record:
        (root / RECORD).parent.mkdir(parents=True, exist_ok=True)
        (root / RECORD).write_text(text, encoding='utf-8')
    print(f'Wheel: {wheel}\nrunw.exe: {compiled["runw.exe"]}')


if __name__ == '__main__':
    main()
