"""Repopulate local demos by retaining the previous directory, never deleting it."""
import os
import time
from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4

from cycling_test.instance import InstanceLock

ROOT=Path(__file__).resolve().parents[1]


def reset_demo(destination,*,allowed_root=None):
    """Move a direct child of .local into .local/demo-backups after lock checks.

    No databases or registries are opened, and no referenced external archive or
    sync folder is followed. allowed_root is only for isolated automated tests.
    """
    base=Path(allowed_root) if allowed_root is not None else ROOT/'.local'
    if base.is_symlink() or base.is_junction():
        raise ValueError('La cartella .local non può essere un collegamento per --reset.')
    base=base.resolve();requested=Path(destination).absolute()
    if requested.is_symlink() or requested.is_junction():
        raise ValueError('La destinazione --reset non può essere un collegamento.')
    target=requested.resolve()
    if target.parent!=base or target.name in ('demo-backups','.demo-control'):
        raise ValueError('--reset ammette soltanto una cartella diretta del progetto .local, per esempio .local/ui-test; non la radice .local né cartelle operative esterne.')
    if not target.exists():return None
    if not target.is_dir():raise ValueError('La destinazione --reset deve essere una cartella.')
    # Refuse links before walking for locks: in particular Windows junctions.
    archive_roots={target}
    for current,dirs,files in os.walk(target,followlinks=False):
        current=Path(current)
        for name in dirs+files:
            path=current/name
            if path.is_symlink() or path.is_junction():
                raise ValueError('Reset rifiutato: la demo contiene collegamenti a file o cartelle.')
        if 'archive.sqlite' in files or 'fuorigiri-instance.lock' in files:
            archive_roots.add(current)
    backups=base/'demo-backups'
    if backups.is_symlink() or backups.is_junction():
        raise ValueError('La cartella demo-backups non può essere un collegamento.')
    backup=backups/(target.name+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid4().hex[:8])
    # Check final absolute source and destination before the directory move.
    if target.parent!=base or backup.resolve().parent!=base/'demo-backups':
        raise ValueError('Percorsi di reset non consentiti.')
    locks=[]
    try:
        for path in sorted(archive_roots):locks.append(InstanceLock(path))
        backups.mkdir(exist_ok=True)
        # Windows cannot rename a directory containing our open lock handles.
        # Another desktop/server handle also makes the rename fail without loss.
        if os.name=='nt':
            for lock in reversed(locks):lock.close()
        # Indexers/antivirus can briefly retain a Windows directory handle after
        # the app exits. Retry only this atomic move, never remove the original.
        for attempt in range(6):
            try:
                target.rename(backup)
                break
            except PermissionError:
                if attempt==5 or not target.exists() or backup.exists():raise
                time.sleep(.1*2**attempt)
    except OSError as exc:
        raise ValueError('Impossibile archiviare la demo: chiudere Fuorigiri, server e repliche che usano questa cartella. Nessun file viene eliminato.') from exc
    finally:
        for lock in reversed(locks):lock.close()
    return backup


def reset_notice(destination):
    backup=reset_demo(destination)
    if backup:print('Archivio precedente conservato in:',backup,flush=True)
    return backup
