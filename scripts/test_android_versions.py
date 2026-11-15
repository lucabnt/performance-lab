"""Run the Python tests with the library versions shipped on Android (RT-16).

Android pins numpy, matplotlib, pydantic, reportlab and cffi to older releases
than the desktop lock (`android/requirements.txt`). PyPI has no Windows or
Linux wheels of numpy 1.26.2 and matplotlib 3.8.4 for Python 3.13, the Android
interpreter, so this check uses Python 3.12: it covers library differences,
not the Chaquopy interpreter itself. Desktop-only tests skip without PySide6.

    py -3.12 scripts/test_android_versions.py --venv .local/android-versions-312

The virtual environment must be a new folder, or one created by this script.
"""

import argparse
import re
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKER = 'fuorigiri-android-versions'
# Test tools and desktop-side modules imported by the tests, pinned as in the desktop lock.
EXTRA = ('pytest', 'pluggy', 'iniconfig', 'packaging', 'Pygments', 'pypdf', 'uvicorn', 'click', 'h11', 'colorama')
REPORT = ('numpy', 'matplotlib', 'pydantic', 'pydantic-core', 'reportlab', 'cffi', 'fastapi', 'starlette')


def pins(path):
    result = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        match = re.match(r'^([A-Za-z0-9][A-Za-z0-9._-]*)==(\S+)', line.strip())
        if match:
            result[match.group(1).lower()] = f'{match.group(1)}=={match.group(2)}'
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description='Test Python con le versioni delle librerie Android.')
    parser.add_argument('--venv', type=Path, default=ROOT / '.local' / 'android-versions-venv')
    parser.add_argument('pytest_args', nargs='*', help='argomenti aggiuntivi per pytest')
    args = parser.parse_args(argv)
    if sys.version_info[:2] != (3, 12):
        raise SystemExit('Usare Python 3.12: le wheel delle versioni Android non esistono per altre versioni.')
    target = args.venv.resolve()
    if target.exists() and not (target / MARKER).exists():
        raise SystemExit(f'{target} esiste e non è stato creato da questo script: indicare una cartella nuova.')
    if not target.exists():
        venv.create(target, with_pip=True)
        (target / MARKER).write_text('Ambiente di prova RT-16, rigenerabile.\n', encoding='utf-8')
    python = target / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
    desktop = pins(ROOT / 'requirements-lock-windows.txt')
    requirements = [line for line in pins(ROOT / 'android' / 'requirements.txt').values()]
    requirements += [desktop[name.lower()] for name in EXTRA if name.lower() in desktop]
    common = (ROOT / 'requirements-common.txt').read_text(encoding='utf-8').split()[0]
    subprocess.run([python, '-m', 'pip', 'install', '--quiet', *requirements], check=True)
    subprocess.run([python, '-m', 'pip', 'install', '--quiet', '--no-deps', '--no-index', ROOT / common], check=True)
    versions = subprocess.run(
        [python, '-c', f'import importlib.metadata as m;print(", ".join(n+" "+m.version(n) for n in {REPORT!r}))'],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    print('Versioni in prova:', versions, flush=True)
    return subprocess.run(
        [python, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', *args.pytest_args], cwd=ROOT
    ).returncode


if __name__ == '__main__':
    sys.exit(main())
