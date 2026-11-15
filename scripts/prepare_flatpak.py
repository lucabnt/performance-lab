"""Run on Linux with the Freedesktop 25.08 SDK, then build without network.

Usage: python scripts/prepare_flatpak.py
The SDK supplies Python only to the builder; PyInstaller bundles it for users.
"""

import hashlib
import json
import subprocess
import shutil
from pathlib import Path

root = Path(__file__).resolve().parents[1]
wheelhouse = root / 'wheelhouse'
wheelhouse.mkdir(exist_ok=True)
command = [
    'flatpak',
    'run',
    '--share=network',
    '--filesystem=' + str(root),
    '--command=sh',
    'org.freedesktop.Sdk//25.08',
    '-ec',
    'cd "$1"; python3 -m venv wheelhouse/build-venv; wheelhouse/build-venv/bin/python -m pip install fastapi uvicorn python-multipart fitdecode numpy matplotlib reportlab cryptography PySide6 keyring==25.7.0 pytest httpx pyinstaller; wheelhouse/build-venv/bin/python -m pip freeze > wheelhouse/requirements-resolved.txt; wheelhouse/build-venv/bin/python -m pip download --only-binary=:all: --dest wheelhouse -r wheelhouse/requirements-resolved.txt',
    'prepare',
    str(root),
]
subprocess.run(command, check=True)
common = json.loads((root / 'vendor/suite-core-provenance.json').read_text(encoding='utf-8'))
wheel = root / 'vendor' / common['artifact']
if hashlib.sha256(wheel.read_bytes()).hexdigest() != common['sha256']:
    raise ValueError('Wheel common non integra.')
shutil.copyfile(wheel, wheelhouse / wheel.name)
with (wheelhouse / 'requirements-resolved.txt').open('a', encoding='utf-8') as stream:
    stream.write('\ncycling-suite-core==' + common['version'] + '\n')
manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in wheelhouse.glob('*.whl')}
(wheelhouse / 'SHA256.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
print('Wheelhouse pronta; conservare requirements-resolved.txt e SHA256.json con il rilascio.')
