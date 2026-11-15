"""Repair an explicit Android abi3 wheel's missing libpython dependency.

Build tool only: requires lief==1.0.0. Never overwrites the input wheel.
The output directory must be new. A provenance JSON accompanies the wheel.
"""

import argparse
import base64
import csv
import hashlib
import io
import json
import tempfile
import zipfile
from pathlib import Path


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def repair(source: Path, destination: Path):
    import lief

    if not source.name.endswith('.whl') or '-abi3-android_' not in source.name:
        raise ValueError('Serve una wheel abi3 Android esplicita.')
    if destination.exists():
        raise ValueError('La destinazione deve essere nuova; nessun file sovrascritto.')
    with zipfile.ZipFile(source) as archive:
        entries = {item.filename: (item, archive.read(item)) for item in archive.infolist()}
    if any(name.endswith(('/RECORD.jws', '/RECORD.p7s')) for name in entries):
        raise ValueError('Wheel firmata: richiede una nuova firma, non modificata.')
    modules = [name for name in entries if name.endswith('.abi3.so')]
    records = [name for name in entries if name.endswith('.dist-info/RECORD')]
    if not modules or len(records) != 1:
        raise ValueError('Contenuto wheel inatteso.')
    changes = []
    for name in modules:
        info, original = entries[name]
        binary = lief.ELF.parse(original)
        if binary is None:
            raise ValueError('Modulo ELF non valido.')
        before = list(binary.libraries)
        if any(lib.startswith('libpython') for lib in before):
            raise ValueError('Dipendenza Python già presente: non applicare questa riparazione.')
        if not any(symbol.shndx == 0 and symbol.name.startswith(('Py', '_Py')) for symbol in binary.dynamic_symbols):
            raise ValueError('Nessun simbolo Python da risolvere.')
        text = bytes(binary.get_section('.text').content)
        binary.add_library('libpython3.so')
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / 'module.so'
            binary.write(str(target))
            patched = target.read_bytes()
        checked = lief.ELF.parse(patched)
        if 'libpython3.so' not in checked.libraries:
            raise ValueError('DT_NEEDED non scritto.')
        if bytes(checked.get_section('.text').content) != text:
            raise ValueError('La riparazione ha modificato il codice eseguibile.')
        if checked.header.machine_type != binary.header.machine_type:
            raise ValueError('Architettura modificata.')
        for segment in checked.segments:
            if segment.type == lief.ELF.Segment.TYPE.LOAD:
                if segment.alignment < 16384 or (segment.virtual_address - segment.file_offset) % 16384:
                    raise ValueError('Segmento non allineato a 16 KB.')
        entries[name] = (info, patched)
        changes.append(
            {
                'module': name,
                'before': before,
                'after': list(checked.libraries),
                'original_sha256': sha256(original),
                'repaired_sha256': sha256(patched),
            }
        )
    record = records[0]
    out = io.StringIO(newline='')
    writer = csv.writer(out, lineterminator='\n')
    for name, (info, content) in entries.items():
        if name != record and not info.is_dir():
            digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b'=').decode()
            writer.writerow([name, 'sha256=' + digest, len(content)])
    writer.writerow([record, '', ''])
    entries[record] = (entries[record][0], out.getvalue().encode())
    destination.mkdir(parents=True)
    wheel = destination / source.name
    with zipfile.ZipFile(wheel, 'w') as archive:
        for info, content in entries.values():
            archive.writestr(info, content)
    report = {
        'tool': 'repair_android_abi3/1',
        'lief': lief.__version__,
        'wheel': source.name,
        'original_sha256': sha256(source.read_bytes()),
        'repaired_sha256': sha256(wheel.read_bytes()),
        'changes': changes,
        'runtime_verified': False,
    }
    (destination / 'repair.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    print(json.dumps(repair(args.source, args.destination), indent=2))
