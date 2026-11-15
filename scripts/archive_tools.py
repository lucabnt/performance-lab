"""Streamed backups and conservative society extraction; never overwrites data."""

import argparse
import json
from pathlib import Path
from cycling_test.store import Store
from cycling_test.workspaces import Workspaces
from cycling_test.backup_stream import write_backup, inspect_file
from cycling_test.recovery import summary, restore
from cycling_test.society_migration import preview, extract


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True, help='Radice dati dell’app')
    parser.add_argument('--workspace', default='', help='ID società, vuoto per archivio legacy')
    tasks = parser.add_subparsers(dest='task', required=True)
    backup = tasks.add_parser('backup')
    backup.add_argument('--out', type=Path, required=True)
    inspect = tasks.add_parser('inspect')
    inspect.add_argument('--file', type=Path, required=True)
    tasks.add_parser('split-preview')
    split = tasks.add_parser('split')
    split.add_argument('--organization', required=True)
    split.add_argument('--source-hash', required=True)
    split.add_argument('--operator', required=True)
    recover = tasks.add_parser('restore')
    recover.add_argument('--file', type=Path, required=True)
    recover.add_argument('--operator', required=True)
    args = parser.parse_args()
    if not (args.data / 'archive.sqlite').is_file():
        parser.error('La radice dati deve già esistere.')
    manager = Workspaces(args.data, Store(args.data))
    store = manager.get(args.workspace)
    if args.task == 'backup':
        result = {'file': str(write_backup(store, args.out)), 'schema': 3}
    elif args.task == 'inspect':
        with inspect_file(args.file) as data:
            result = summary(data)
    elif args.task == 'split-preview':
        result = preview(store)
    elif args.task == 'split':
        result = extract(manager, store, args.organization, args.source_hash, args.operator)
    else:
        result = restore(manager, args.file, 'independent', operator=args.operator)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
