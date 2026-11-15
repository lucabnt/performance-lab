"""Hash-checked companions of the app lockfiles (delivered by cycling-suite-common).

Each lockfile `requirements*.lock` or `requirements-lock*.txt` gets a companion
with the same name and the `.hashes` extension, listing the same PyPI pins with
the SHA-256 of every published file, for `pip install --require-hashes`.
Companions keep their own extension because `sync-core.py` rewrites every
`requirements*.txt` / `requirements*.lock` to include requirements-common.txt.
The vendored common wheel is not listed: install it with
`pip install --no-deps --no-index -r requirements-common.txt`; `verify_core.py`
checks it against `vendor/suite-core-provenance.json`.

    python scripts/lock_hashes.py           # offline: every lockfile matches its companion
    python scripts/lock_hashes.py --write   # regenerate companions from PyPI (network)
"""

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ('requirements*.lock', 'requirements-lock*.txt')
COMMON = 'requirements-common.txt'
PIN = re.compile(r'^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s;\\]+)\s*(;[^\\]*)?')
INCLUDE = re.compile(r'^-r\s+(\S+)')
HEADER = (
    '# Generato da scripts/lock_hashes.py --write a partire da {lock}. Non modificare a mano.\n'
    '# Uso: pip install --require-hashes -r {name}, poi\n'
    '# pip install --no-deps --no-index -r requirements-common.txt (wheel verificata da verify_core.py).\n'
)


def normalized(name):
    return re.sub(r'[-_.]+', '-', name).lower()


def locks(root):
    return sorted({p for pattern in PATTERNS for p in root.glob(pattern) if p.name != COMMON and p.is_file()})


def companion(lock):
    return lock.with_suffix('.hashes')


def parse(path):
    """Pins as {normalized: (name, version, marker, hashes)} and included files."""
    pins, includes, current = {}, [], None
    for line in path.read_text(encoding='utf-8').splitlines():
        text = line.strip()
        if match := PIN.match(text):
            current = normalized(match.group(1))
            pins[current] = [match.group(1), match.group(2), (match.group(3) or '').strip(), 0]
        elif match := INCLUDE.match(text):
            includes.append(match.group(1))
            current = None
        elif current and text.startswith('--hash=sha256:'):
            pins[current][3] += 1
    return pins, includes


def expected_includes(lock):
    _, includes = parse(lock)
    return [companion(Path(name)).as_posix() for name in includes if name != COMMON]


def check(root=ROOT):
    problems = []
    for lock in locks(root):
        target = companion(lock)
        if not target.exists():
            problems.append(f'{target.name} assente: eseguire scripts/lock_hashes.py --write.')
            continue
        expected, _ = parse(lock)
        actual, includes = parse(target)
        if includes != expected_includes(lock):
            problems.append(f'{target.name}: file inclusi diversi da {lock.name}.')
        for key, (name, version, marker, _) in sorted(expected.items()):
            if key not in actual:
                problems.append(f'{target.name}: {name}=={version} senza hash.')
            elif actual[key][1:3] != [version, marker]:
                problems.append(f'{target.name}: {name} {version} nel lock, {actual[key][1]} negli hash.')
            elif not actual[key][3]:
                problems.append(f'{target.name}: {name}=={version} senza righe --hash.')
        problems += [f'{target.name}: {key} presente solo negli hash.' for key in sorted(set(actual) - set(expected))]
    return problems


def pypi(name, version):
    with urllib.request.urlopen(f'https://pypi.org/pypi/{name}/{version}/json', timeout=60) as response:
        return sorted({f['digests']['sha256'] for f in json.load(response)['urls']})


def write(root=ROOT, digests=pypi):
    for lock in locks(root):
        target = companion(lock)
        pins, _ = parse(lock)
        parts = [HEADER.format(lock=lock.name, name=target.name)]
        parts += [f'-r {name}\n' for name in expected_includes(lock)]
        for _, (name, version, marker, _) in sorted(pins.items()):
            hashes = digests(name, version)
            if not hashes:
                raise SystemExit(f'Nessun file pubblicato per {name}=={version}.')
            head = f'{name}=={version}' + (f' {marker}' if marker else '')
            parts.append(head + ' \\\n' + ' \\\n'.join(f'    --hash=sha256:{h}' for h in hashes) + '\n')
        target.write_text(''.join(parts), encoding='utf-8', newline='\n')
        print(f'{target.name}: hash di {len(pins)} pacchetti.')


def main(argv=None):
    parser = argparse.ArgumentParser(description='Hash dei lockfile Python.')
    parser.add_argument('--write', action='store_true', help='rigenera i file .hashes da PyPI (rete)')
    args = parser.parse_args(argv)
    if not locks(ROOT):
        print('Nessun lockfile trovato.')
        return 1
    if args.write:
        write()
    problems = check()
    for problem in problems:
        print(problem)
    if not problems:
        print('Lockfile e hash coerenti.')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
