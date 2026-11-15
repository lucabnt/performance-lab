"""Check product metadata against pyproject.toml before creating build artifacts."""

import ast
import json
import re
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path


def verify(root):
    version = tomllib.loads((root / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version']
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('Usare una versione prodotto major.minor.patch.')
    errors = []

    def check(name, value):
        if value != version:
            errors.append(f'{name}: {value!r}, atteso {version}')

    tree = ast.parse((root / 'backend/cycling_test/__init__.py').read_text(encoding='utf-8'))
    check(
        'Python',
        next(
            ast.literal_eval(n.value)
            for n in tree.body
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '__version__' for t in n.targets)
        ),
    )
    package = json.loads((root / 'frontend/package.json').read_text(encoding='utf-8'))
    lock = json.loads((root / 'frontend/package-lock.json').read_text(encoding='utf-8'))
    check('Frontend', package['version'])
    check('Lockfile', lock['version'])
    check('Lockfile root', lock['packages']['']['version'])
    android = (root / 'android/app/build.gradle.kts').read_text(encoding='utf-8')
    check('Android', re.search(r'versionName\s*=\s*"([^"]+)"', android)[1])
    major, minor, patch = map(int, version.split('.'))
    if minor >= 100 or patch >= 100:
        errors.append('Rivedere la codifica Android prima di usare minor/patch >= 100.')
    expected_code = major * 10000 + minor * 100 + patch
    if int(re.search(r'versionCode\s*=\s*(\d+)', android)[1]) != expected_code:
        errors.append(f'Android versionCode atteso: {expected_code}')
    installer = (root / 'packaging/windows/Fuorigiri.iss').read_text(encoding='utf-8')
    check('Installer Windows', re.search(r'#define AppVersion "([^"]+)"', installer)[1])
    metadata = ET.parse(root / 'packaging/linux/org.fuorigiri.PerformanceLab.metainfo.xml')
    check('AppStream Linux', metadata.find('releases/release').get('version'))
    if errors:
        raise ValueError('\n'.join(errors))
    return version


if __name__ == '__main__':
    try:
        print('Versioni prodotto coerenti:', verify(Path(__file__).resolve().parents[1]))
    except ValueError as exc:
        raise SystemExit(str(exc)) from None
