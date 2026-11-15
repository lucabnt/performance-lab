"""Synthetic disk-streaming acceptance probe. New directory only, no real data."""

import argparse
import hashlib
import json
import random
import time
import tracemalloc
from pathlib import Path
from cycling_test.store import Store
from cycling_test.workspaces import Workspaces
from cycling_test.backup_stream import write_backup, inspect_file, digest_file, CHUNK
from cycling_test.recovery import restore, summary, MAX_UPLOAD


def verify(root, large=False):
    root = Path(root).resolve()
    if root.exists():
        raise ValueError('Usare una cartella nuova: nessun dato esistente viene modificato.')
    root.mkdir(parents=True)
    manager = Workspaces(root, Store(root))
    entry = manager.create('SOLO DEMO streaming', 'Fondatore DEMO')
    store = manager.get(entry['id'])
    size = 101_000_000 if large else 3_000_000
    rng = random.Random(481516)
    sha = hashlib.sha256()
    temp = store.root / 'objects' / 'synthetic.tmp'
    with temp.open('wb') as stream:
        remaining = size
        while remaining:
            raw = rng.randbytes(min(CHUNK, remaining))
            stream.write(raw)
            sha.update(raw)
            remaining -= len(raw)
    digest = sha.hexdigest()
    temp.rename(temp.with_name(digest))
    athlete = store.save(
        'athlete',
        {'organization_id': entry['organization_id'], 'name': 'SOLO DEMO', 'surname': 'Streaming', 'objects': [digest]},
    )
    started = time.monotonic()
    tracemalloc.start()
    path = write_backup(store, root / 'backup-streaming-v3.zip')
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    with inspect_file(path) as data:
        info = summary(data)
    other_root = root / 'restored'
    other = Workspaces(other_root, Store(other_root))
    restored = restore(other, path, 'independent', operator='Fondatore copia DEMO')
    copied = other.get(restored['id'])
    assert copied.get(athlete['id']) == athlete
    assert digest_file(copied.root / 'objects' / digest) == digest
    report = {
        'synthetic': True,
        'payload_bytes': size,
        'backup_bytes': path.stat().st_size,
        'exceeds_legacy_compressed_limit': path.stat().st_size > MAX_UPLOAD,
        'python_peak_bytes_during_export': peak,
        'roundtrip_seconds': round(time.monotonic() - started, 2),
        'schema': info['schema'],
        'independent_restore_verified': True,
    }
    if large:
        assert report['exceeds_legacy_compressed_limit']
    (root / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument(
        '--large', action='store_true', help='101 MB non comprimibili; servono circa 1 GB libero per copie e temporanei'
    )
    args = parser.parse_args()
    verify(args.data, args.large)
