"""Bounded ZIP validation, independent restore and encrypted founder recovery.

Uploaded SQLite is only read in a temporary directory. Restores reconstruct the
known schema in a new folder; they never execute SQL supplied by an archive.
"""

import hashlib
import io
import json
import re
import shutil
import sqlite3
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from .store import Store, KINDS, encoded
from .workspaces import ArchiveStore, fresh_identity, validate_identity, seal, unseal, write_json, verify

MAX_UPLOAD = 100_000_000
MAX_EXPANDED = 1_000_000_000
OPTIONAL_TABLES = {'sync_audit': ('seq', 'body', 'digest')}
TABLES = {
    'records': ('id', 'kind', 'revision', 'data'),
    'changes': ('id', 'body'),
    'conflicts': ('id', 'body'),
    'config': ('key', 'value'),
}


def validate_zip_members(archive):
    supported = {zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED, zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA}
    if hasattr(zipfile, 'ZIP_ZSTANDARD'):
        supported.update((20, zipfile.ZIP_ZSTANDARD))
    for member in archive.infolist():
        if member.flag_bits & (1 | 32 | 64) or member.compress_type not in supported:
            raise ValueError('Backup ZIP cifrato o con formato di compressione non supportato.')


def backup_bytes(store):
    with tempfile.TemporaryDirectory() as tmp:
        target = sqlite3.connect(Path(tmp) / 'archive.sqlite')
        try:
            with store.connect() as source:
                source.backup(target)
        finally:
            target.close()
        object_paths = [p for p in (store.root / 'objects').iterdir() if re.fullmatch('[0-9a-f]{64}', p.name)]
        if (
            len(object_paths) > 10000
            or (Path(tmp) / 'archive.sqlite').stat().st_size + sum(p.stat().st_size for p in object_paths)
            > MAX_EXPANDED
        ):
            raise ValueError(
                'Archivio oltre i limiti del backup ZIP ripristinabile. Non viene generato un backup inutilizzabile; serve una procedura di backup per archivi grandi.'
            )
        out = io.BytesIO()
        hashes = {}
        with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
            db = (Path(tmp) / 'archive.sqlite').read_bytes()
            z.writestr('archive.sqlite', db)
            hashes['archive.sqlite'] = hashlib.sha256(db).hexdigest()
            for path in sorted((store.root / 'objects').iterdir()):
                if re.fullmatch('[0-9a-f]{64}', path.name):
                    raw = store.read_object(path.name)
                    z.writestr('objects/' + path.name, raw)
                    hashes['objects/' + path.name] = path.name
            manifest = {
                'schema': 2,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'files': hashes,
                'organizations': [{'id': o['id'], 'name': o['name']} for o in store.list('organization')],
                'warning': 'Backup dati non cifrato. Non contiene credenziali né privilegi del fondatore.',
            }
            if hasattr(store, 'identity') and not store.identity.get('snapshot'):
                manifest.update(
                    workspace=store.identity['workspace'], authority_public=store.identity['authority_public']
                )
                for name in ('revocations.json', 'access.json'):
                    path = store.root / name
                    if path.exists():
                        manifest[name] = json.loads(path.read_text(encoding='utf-8'))
            z.writestr('manifest.json', encoded(manifest))
        result = out.getvalue()
    if len(result) > MAX_UPLOAD:
        raise ValueError(
            'Backup oltre il limite ripristinabile di 100 MB compressi. Non viene scaricato un file che questa versione non può ripristinare.'
        )
    return result


def inspect_backup(raw):
    try:
        return _inspect(raw)
    except (
        zipfile.BadZipFile,
        sqlite3.DatabaseError,
        UnicodeError,
        KeyError,
        TypeError,
        AttributeError,
        RecursionError,
        json.JSONDecodeError,
    ) as exc:
        raise ValueError('Backup non valido o danneggiato.') from exc


def _inspect(raw):
    if len(raw) > MAX_UPLOAD:
        raise ValueError('Backup oltre il limite di 100 MB compressi.')
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        validate_zip_members(z)
        infos = z.infolist()
        names = [i.filename for i in infos]
        if len(infos) > 10002 or len(set(names)) != len(names) or sum(i.file_size for i in infos) > MAX_EXPANDED:
            raise ValueError('Backup troppo grande o con voci duplicate.')
        if 'archive.sqlite' not in names or 'manifest.json' not in names:
            raise ValueError('Servono archive.sqlite e manifest.json nel backup ZIP.')
        if any(
            not (name in ('archive.sqlite', 'manifest.json') or re.fullmatch('objects/[0-9a-f]{64}', name))
            for name in names
        ):
            raise ValueError('Il backup contiene percorsi o file non consentiti.')
        manifest = json.loads(z.read('manifest.json'))
        if manifest.get('schema') not in (1, 2):
            raise ValueError('Versione del backup non supportata.')
        files = {name: z.read(name) for name in names if name != 'manifest.json'}
    hashes = {name: hashlib.sha256(body).hexdigest() for name, body in files.items()}
    if manifest['schema'] == 2 and hashes != manifest.get('files'):
        raise ValueError('Checksum del backup non valido.')
    if any(name.startswith('objects/') and hashes[name] != name.split('/')[1] for name in files):
        raise ValueError('Allegato corrotto nel backup.')
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / 'archive.sqlite'
        db_path.write_bytes(files['archive.sqlite'])
        db = sqlite3.connect(db_path.as_uri() + '?mode=ro', uri=True)
        try:
            db.execute('PRAGMA trusted_schema=OFF')
            if db.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                raise ValueError('Database danneggiato.')
            if db.execute('PRAGMA user_version').fetchone()[0] > 3:
                raise ValueError('Database di una versione più recente.')
            schema = db.execute("SELECT name,type,sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'").fetchall()
            if any(
                kind not in ('table', 'index')
                or kind == 'table'
                and (name not in TABLES and name not in OPTIONAL_TABLES or not sql.upper().startswith('CREATE TABLE'))
                for name, kind, sql in schema
            ):
                raise ValueError('Schema del database non consentito.')
            if not set(TABLES) <= {n for n, k, _ in schema if k == 'table'}:
                raise ValueError('Tabelle obbligatorie mancanti.')
            # The audit is local transport state, not archive content. Validate its
            # shape when present; restored devices start their own audit chain.
            for name, columns in OPTIONAL_TABLES.items():
                if (
                    any(n == name for n, k, _ in schema)
                    and tuple(r[1] for r in db.execute(f'PRAGMA table_info({name})')) != columns
                ):
                    raise ValueError('Schema registro locale non supportato.')
            rows = {}
            for name, columns in TABLES.items():
                if tuple(r[1] for r in db.execute(f'PRAGMA table_info({name})')) != columns:
                    raise ValueError('Schema colonne non supportato.')
                rows[name] = db.execute(f'SELECT {",".join(columns)} FROM {name}').fetchall()
        finally:
            db.close()
    changes = {}
    for id, body in rows['changes']:
        event = json.loads(body)
        record = event['record']
        if event['id'] != id or record['revision'] != id or record['kind'] not in KINDS:
            raise ValueError('Storico revisioni incoerente.')
        changes[id] = event
    records = []
    for id, kind, revision, body in rows['records']:
        record = json.loads(body)
        if kind not in KINDS or (record['id'], record['kind'], record['revision']) != (id, kind, revision):
            raise ValueError('Record incoerente.')
        if revision not in changes or encoded(changes[revision]['record']) != encoded(record):
            raise ValueError('Revisione corrente mancante o incoerente.')
        records.append(record)
    for event in changes.values():
        if any(parent and parent not in changes for parent in event.get('parents', [event['base']])):
            raise ValueError('Storico revisioni incompleto.')
        for digest in event['record'].get('objects', []):
            if 'objects/' + digest not in files:
                raise ValueError('Allegato storico mancante nel backup.')
    for id, body in rows['conflicts']:
        if id not in changes or encoded(json.loads(body)) != encoded(changes[id]):
            raise ValueError('Conflitto senza evento coerente.')
    if not any(r['kind'] == 'organization' for r in records):
        raise ValueError('Il backup non contiene società.')
    return {'manifest': manifest, 'rows': rows, 'records': records, 'changes': changes, 'files': files}


def summary(data):
    if hasattr(data['rows'], 'path'):
        from .backup_stream import connection

        with connection(data['rows'].path.as_uri() + '?mode=ro', uri=True) as db:
            counts = dict(db.execute('SELECT kind,count(*) FROM records GROUP BY kind'))
            organizations = [
                {'id': r['id'], 'name': r['name']}
                for row in db.execute("SELECT data FROM records WHERE kind='organization'")
                if (r := json.loads(row[0]))
            ]
        manifest = data['manifest']
        return {
            'organizations': organizations,
            'counts': {kind: counts.get(kind, 0) for kind in ('athlete', 'test', 'measurement', 'protocol')},
            'created_at': manifest.get('created_at'),
            'schema': manifest['schema'],
            'workspace': manifest.get('workspace'),
            'checksums': True,
            'objects': len(data['files']) - 1,
        }
    records = data['records']
    manifest = data['manifest']
    return {
        'organizations': [{'id': r['id'], 'name': r['name']} for r in records if r['kind'] == 'organization'],
        'counts': {
            kind: sum(r['kind'] == kind for r in records) for kind in ('athlete', 'test', 'measurement', 'protocol')
        },
        'created_at': manifest.get('created_at'),
        'schema': manifest['schema'],
        'workspace': manifest.get('workspace'),
        'checksums': manifest['schema'] >= 2,
        'objects': sum(n.startswith('objects/') for n in data['files']),
    }


def export_recovery(store, password):
    identity = store.identity
    if not identity.get('authority_private'):
        raise ValueError('Solo il fondatore esporta il recupero degli accessi.')
    extra = {}
    for name in ('members.json', 'revocations.json', 'access.json'):
        path = store.root / name
        if path.exists():
            extra[name] = json.loads(path.read_text(encoding='utf-8'))
    return seal(
        {
            'type': 'fuorigiri-founder-recovery',
            'schema': 1,
            'identity': identity,
            'extra': extra,
            'created_at': datetime.now(timezone.utc).isoformat(),
        },
        password,
    )


def restore(manager, raw, mode, path='', operator='', recovery_raw=None, password=''):
    if isinstance(raw, Path):
        from .backup_stream import inspect_file

        with inspect_file(raw) as data:
            return _restore_data(manager, data, mode, path, operator, recovery_raw, password)
    return _restore_data(manager, inspect_backup(raw), mode, path, operator, recovery_raw, password)


def _restore_data(manager, data, mode, path='', operator='', recovery_raw=None, password=''):
    info = summary(data)
    extra = {}
    if mode not in ('snapshot', 'independent', 'recover'):
        raise ValueError('Modalità ripristino non valida.')
    if mode == 'recover':
        try:
            payload = unseal(recovery_raw or b'', password)
            if payload['type'] != 'fuorigiri-founder-recovery' or payload['schema'] != 1:
                raise ValueError('Formato recupero errato.')
            identity = validate_identity(payload['identity'])
            extra = payload.get('extra', {})
            if not identity.get('authority_private'):
                raise ValueError('Credenziali del fondatore mancanti.')
            if data['manifest'].get('workspace') not in (None, identity['workspace']):
                raise ValueError('Backup e recupero di società diverse.')
            for name in ('revocations.json', 'access.json'):
                newer = data['manifest'].get(name)
                if newer and newer['version'] > extra.get(name, {}).get('version', -1):
                    extra[name] = newer
                if name in extra:
                    control = extra[name]
                    verify(
                        identity['authority_public'],
                        {k: v for k, v in control.items() if k != 'signature'},
                        control['signature'],
                    )
                    if control['workspace'] != identity['workspace']:
                        raise ValueError('Metadati di altra società.')
            # Verify every signed event, including frozen history of revoked users.
            with tempfile.TemporaryDirectory() as tmp:
                check = ArchiveStore(tmp)
                write_json(check.root / 'identity.json', identity)
                if 'revocations.json' in extra:
                    write_json(check.root / 'revocations.json', extra['revocations.json'])
                verify_event = check.verifier()
                for event in data['changes'].values():
                    verify_event(event)
            if 'access.json' in extra:
                extra['members.json'] = [
                    m for m in extra['access.json']['members'] if m['id'] != identity['certificate']['id']
                ]
        except Exception as exc:
            raise ValueError(
                'Recupero non valido: controllare password, integrità e appartenenza alla stessa società. Nessun dato modificato.'
            ) from exc
        id = identity['workspace']
    else:
        id = str(uuid4())
        identity = fresh_identity(id, operator.strip()) if mode == 'independent' else None
        if mode == 'independent' and not operator.strip():
            raise ValueError('Indicare il nome del nuovo fondatore.')
    target = Path(path).resolve() if path else (manager.root / 'workspaces' / id).resolve()
    with manager.lock:
        if any(e['id'] == id for e in manager.entries(include_detached=True)):
            raise ValueError('Società già presente sul dispositivo, anche se scollegata. Nessun archivio sovrascritto.')
        if (
            target == manager.root.resolve()
            or target in manager.root.resolve().parents
            or target == manager.root.resolve() / 'objects'
            or manager.root.resolve() / 'objects' in target.parents
        ):
            raise ValueError('La destinazione deve essere separata dall’archivio principale.')
        for e in manager.entries(include_detached=True):
            other = Path(e['path']).resolve()
            if target == other or target in other.parents or other in target.parents:
                raise ValueError('Destinazione sovrapposta a una società esistente.')
        if target.exists() and (not target.is_dir() or any(target.iterdir())):
            raise ValueError('La destinazione deve essere vuota. Nessun archivio sovrascritto.')
        was_empty = target.exists()
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.fuorigiri-restore-', dir=target.parent) as tmp:
            stage = Path(tmp) / 'archive'
            store = Store(stage)
            if identity:
                write_json(stage / 'identity.json', identity)
            for name, value in extra.items():
                if name in ('members.json', 'revocations.json', 'access.json'):
                    write_json(stage / name, value)
            signer = ArchiveStore(stage) if mode == 'independent' else None
            with store.connect() as db:
                for table in ('records', 'changes', 'conflicts'):
                    rows = data['rows'][table]
                    if mode == 'independent' and table == 'changes':

                        def rebuilt():
                            for event in data['changes'].values():
                                original = hashlib.sha256(encoded(event).encode()).hexdigest()
                                body = {
                                    k: v
                                    for k, v in event.items()
                                    if k not in ('workspace', 'certificate', 'certificate_signature', 'signature')
                                }
                                signed = signer.sign_change(
                                    {
                                        **body,
                                        'import_origin': {
                                            'sha256': original,
                                            'note': 'Copia indipendente da backup; nessuna autorità originale ereditata.',
                                        },
                                    },
                                    db=db,
                                )
                                yield signed['id'], encoded(signed)

                        rows = rebuilt()
                    if mode == 'independent' and table == 'conflicts':
                        rows = (
                            (r[0], db.execute('SELECT body FROM changes WHERE id=?', (r[0],)).fetchone()[0])
                            for r in data['rows']['conflicts']
                        )
                    placeholders = ','.join('?' for _ in TABLES[table])
                    db.executemany(f'INSERT INTO {table} VALUES({placeholders})', rows)
            for name, body in data['files'].items():
                if name.startswith('objects/'):
                    if isinstance(body, Path):
                        shutil.copyfile(body, stage / name)
                    else:
                        (stage / name).write_bytes(body)
            write_json(
                stage / 'restore-info.json',
                {
                    'mode': mode,
                    'source_workspace': info['workspace'],
                    'restored_at': datetime.now(timezone.utc).isoformat(),
                },
            )
            entry = {
                'id': id,
                'path': str(target),
                'name': info['organizations'][0]['name'],
                'organization_id': info['organizations'][0]['id'],
                'organizations': info['organizations'],
                'mode': mode,
            }
            if was_empty:
                target.rmdir()  # Only removes a directory still empty.
            stage.rename(target)
            try:
                manager.register(entry)
            except Exception:
                target.rename(stage)
                if was_empty:
                    target.mkdir()
                raise
    return entry
