"""Windows launcher metadata and bootloader gate (WIN-AV-02).

Microsoft Defender's machine-learning detection (Bearfoos.A!ml) repeatedly hit
launchers built from the prebuilt PyInstaller bootloader, which is shared by
every PyInstaller application. The launcher is therefore built from a
bootloader compiled locally from the verified PyInstaller sdist
(``scripts/build_pyinstaller_bootloader.py``) and carries a version resource.
Neither measure proves the absence of detections: only a candidate installed,
started and reopened with protection enabled does (docs/WINDOWS_DEFENDER.md).
"""

from __future__ import annotations

import hashlib
import json
import tomllib
from pathlib import Path

RECORD = Path('packaging/windows/bootloader/PROVENIENZA.json')
PLATFORM = 'Windows-64bit-intel'
BOOTLOADERS = ('run.exe', 'runw.exe', 'run_d.exe', 'runw_d.exe')
PUBLISHER = 'Luca Bontempi'
DESCRIPTION = 'Fuorigiri Performance Lab'
ATTRIBUTION = 'Sviluppato da Luca Bontempi per Progetto Ciclismo - Rodengo Saiano A.S.D.'


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def product_version(root: Path) -> str:
    return tomllib.loads((root / 'pyproject.toml').read_text(encoding='utf-8'))['project']['version']


def version_tuple(version: str) -> tuple[int, int, int, int]:
    parts = [int(part) for part in version.split('.')]
    if len(parts) != 3 or any(not 0 <= part < 65536 for part in parts):
        raise SystemExit('Versione prodotto non rappresentabile nella risorsa Windows: ' + version)
    return (*parts, 0)


def version_file_text(version: str) -> str:
    numbers = version_tuple(version)
    strings = {
        'CompanyName': PUBLISHER,
        'FileDescription': DESCRIPTION,
        'FileVersion': version,
        'InternalName': 'Fuorigiri',
        'LegalCopyright': ATTRIBUTION + ' Licenza GPL-3.0-or-later.',
        'OriginalFilename': 'Fuorigiri.exe',
        'ProductName': DESCRIPTION,
        'ProductVersion': version,
    }
    table = ',\n          '.join(f'StringStruct({key!r}, {value!r})' for key, value in strings.items())
    # 0x0410 = Italian, 1200 = Unicode code page.
    return f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={numbers},
    prodvers={numbers},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '041004B0',
        [
          {table}
        ])
    ]),
    VarFileInfo([VarStruct('Translation', [0x0410, 1200])])
  ]
)
"""


def write_version_file(root: Path, target: Path) -> Path:
    target.write_text(version_file_text(product_version(root)), encoding='utf-8')
    return target


def load_record(root: Path, record: Path | None = None) -> dict:
    path = record or root / RECORD
    if not path.is_file():
        raise SystemExit(
            f'Manca {RECORD.as_posix()}: compilare il bootloader con '
            'scripts/build_pyinstaller_bootloader.py --output <cartella nuova> --install --record'
        )
    return json.loads(path.read_text(encoding='utf-8'))


def installed_bootloaders() -> tuple[str, dict[str, str]]:
    import PyInstaller
    from PyInstaller import HOMEPATH

    folder = Path(HOMEPATH) / 'PyInstaller' / 'bootloader' / PLATFORM
    found = {name: sha256(folder / name) for name in BOOTLOADERS if (folder / name).is_file()}
    return PyInstaller.__version__, found


def verify_bootloader(root: Path, record_path: Path | None = None) -> None:
    record = load_record(root, record_path)
    version, found = installed_bootloaders()
    expected = {name: record['bootloaders'][name]['sha256'] for name in BOOTLOADERS}
    problems = []
    if version != record['pyinstaller']:
        problems.append(f'PyInstaller installato {version}, registrato {record["pyinstaller"]}')
    for name, digest in expected.items():
        if found.get(name) != digest:
            problems.append(f'{name}: {found.get(name, "assente")} invece di {digest}')
    stock = set(record.get('stock_sha256', {}).values())
    if stock & set(found.values()):
        problems.append('è installato il bootloader precompilato della wheel PyInstaller')
    if problems:
        raise SystemExit(
            'Bootloader PyInstaller non corrispondente alla compilazione locale registrata (WIN-AV-02):\n- '
            + '\n- '.join(problems)
            + '\nReinstallare la wheel registrata oppure compilare e registrare un nuovo bootloader con '
            'scripts/build_pyinstaller_bootloader.py --output <cartella nuova> --install --record '
            '(vedi docs/WINDOWS_DEFENDER.md).'
        )
