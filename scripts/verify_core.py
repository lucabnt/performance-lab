"""Standalone verification: no sibling clone required."""

import hashlib
import importlib.metadata
import json
import zipfile
from pathlib import Path


def verify(root):
    meta = json.loads((root / 'vendor/suite-core-provenance.json').read_text(encoding='utf-8'))
    name = meta['artifact']
    if Path(name).name != name or not name.endswith('.whl'):
        raise ValueError('Nome wheel non valido.')
    wheel = root / 'vendor' / name
    if hashlib.sha256(wheel.read_bytes()).hexdigest() != meta['sha256']:
        raise ValueError('Checksum common Python non valido.')
    with zipfile.ZipFile(wheel) as archive:
        for file in (
            'cycling_suite/credentials.py',
            'cycling_suite/transports.py',
            'cycling_suite/instance.py',
            'cycling_suite/desktop.py',
            f'cycling_suite_core-{meta["version"]}.dist-info/LICENSE',
        ):
            if file not in archive.namelist():
                raise ValueError('Wheel common incompleta.')
    if importlib.metadata.version('cycling-suite-core') != meta['version']:
        raise ValueError('Reinstallare la wheel common registrata.')
    if '"cycling-suite-core==' + meta['version'] + '"' not in (root / 'pyproject.toml').read_text(encoding='utf-8'):
        raise ValueError('Versione common dichiarata nel progetto non coerente.')
    import cycling_suite

    for module in ('__init__.py', 'credentials.py', 'transports.py', 'instance.py', 'desktop.py'):
        actual = Path(cycling_suite.__file__).parent / module
        with zipfile.ZipFile(wheel) as archive:
            if actual.read_bytes() != archive.read('cycling_suite/' + module):
                raise ValueError('Sorgenti installate diverse dalla wheel.')
    requirement = 'vendor/' + name
    if requirement not in (root / 'requirements-common.txt').read_text(encoding='utf-8'):
        raise ValueError('Dipendenza common non coerente.')
    return meta


if __name__ == '__main__':
    result = verify(Path(__file__).resolve().parents[1])
    print('Common Python ' + result['version'] + ': integrità e installazione verificate.')
