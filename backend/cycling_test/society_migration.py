"""Conservative extraction of one society with all revisions and dependencies."""

import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from uuid import uuid4
from .store import Store, encoded
from .workspaces import ArchiveStore, fresh_identity, write_json
from .backup_stream import digest_file, HASH, connection


def plan(store):
    records = {}
    owners = {}
    references = {}
    revision_ids = {}
    broken = []
    hasher = hashlib.sha256()
    organizations = {}
    # Collect all historical references, not only the current materialized view.
    with store.connect() as db:
        for id, body in db.execute('SELECT id,body FROM changes ORDER BY id'):
            hasher.update(body.encode())
            event = json.loads(body)
            r = event['record']
            rid = r['id']
            revision_ids[id] = rid
            records[rid] = {'kind': r['kind']}
            references.setdefault(rid, set())
            owners.setdefault(rid, set())
            if r['kind'] == 'organization':
                owners[rid].add(rid)
                organizations[rid] = r.get('name', rid)
            if r.get('organization_id'):
                owners[rid].add(r['organization_id'])
        ids = set(records) | set(revision_ids)

        def refs(value):
            if isinstance(value, str):
                if value in ids:
                    yield revision_ids.get(value, value)
            elif isinstance(value, list):
                for item in value:
                    yield from refs(item)
            elif isinstance(value, dict):
                for key, item in value.items():
                    if key not in ('id', 'revision', 'objects', 'samples', 'notes', 'import_origin'):
                        yield from refs(item)

        for (body,) in db.execute('SELECT body FROM changes'):
            event = json.loads(body)
            rid = event['record']['id']
            references[rid].update(refs(event['record']))
            for key in ('athlete_id', 'protocol_id', 'group_id', 'parent_id'):
                reference = event['record'].get(key)
                if reference and reference not in records:
                    broken.append(
                        {'record_id': rid, 'kind': event['record']['kind'], 'reason': f'Riferimento {key} mancante.'}
                    )
            for parent in event.get('parents', [event['base']]):
                if parent and revision_ids.get(parent) != rid:
                    raise ValueError('Storico con dipendenze fra record incoerenti.')
    # Propagate only from dependencies to dependents; never attribute a parent
    # athlete to the society of an incorrectly linked test.
    while True:
        changed = False
        for rid, deps in references.items():
            before = len(owners[rid])
            for dep in deps:
                owners[rid].update(owners[dep])
            changed |= before != len(owners[rid])
        if not changed:
            break
    problems = [
        {'record_id': rid, 'kind': records[rid]['kind'], 'reason': 'Riferimenti a più società o società inesistente.'}
        for rid, scope in owners.items()
        if len(scope) > 1 or scope - set(organizations)
    ]
    problems.extend(broken)
    unassigned = [
        {
            'record_id': rid,
            'kind': records[rid]['kind'],
            'reason': 'Società non ricavabile dai dati e dalle dipendenze.',
        }
        for rid, scope in owners.items()
        if not scope
    ]
    return {
        'source_hash': hasher.hexdigest(),
        'organizations': [
            {'id': org, 'name': name, 'records': sum(scope == {org} for scope in owners.values())}
            for org, name in organizations.items()
        ],
        'problems': problems,
        'unassigned': unassigned,
        'owners': owners,
    }


def preview(store):
    result = plan(store)
    result.pop('owners')
    return result


def extract(manager, source, organization, source_hash, operator, path=''):
    if (
        hasattr(source, 'identity')
        and not source.identity.get('snapshot')
        and not source.identity.get('authority_private')
    ):
        raise ValueError('Solo il fondatore separa un archivio gestito.')
    if not operator.strip():
        raise ValueError('Indicare il nuovo fondatore.')
    # SQLite backup produces a consistent source view and leaves the original intact.
    with tempfile.TemporaryDirectory(prefix='fuorigiri-split-') as tmp:
        snapshot = Path(tmp) / 'source'
        snapshot.mkdir()
        with connection(snapshot / 'archive.sqlite') as dest:
            with source.connect() as src:
                src.backup(dest)
        frozen = Store(snapshot)
        result = plan(frozen)
        if result['source_hash'] != source_hash:
            raise ValueError('Archivio cambiato: ripetere l’anteprima.')
        if result['problems'] or result['unassigned']:
            raise ValueError(
                'Risolvere prima i riferimenti incoerenti o privi di società mostrati nell’anteprima. Nessun dato escluso silenziosamente.'
            )
        selected = {rid for rid, scope in result['owners'].items() if scope == {organization}}
        info = next((o for o in result['organizations'] if o['id'] == organization), None)
        if not info:
            raise ValueError('Società non presente.')
        id = str(uuid4())
        identity = {**fresh_identity(id, operator.strip()), 'organization_id': organization, 'sync_protocol': 2}

        def build(stage):
            stage.mkdir()
            write_json(stage / 'identity.json', identity)
            target = ArchiveStore(stage)
            with frozen.connect() as src, target.connect() as db:
                for (body,) in src.execute('SELECT body FROM changes ORDER BY rowid'):
                    old = json.loads(body)
                    if old['record']['id'] not in selected:
                        continue
                    event = {
                        k: v
                        for k, v in old.items()
                        if k not in ('workspace', 'certificate', 'certificate_signature', 'signature')
                    }
                    event = target.sign_change(
                        {
                            **event,
                            'import_origin': {
                                'sha256': hashlib.sha256(encoded(old).encode()).hexdigest(),
                                'source_archive_sha256': source_hash,
                                'note': 'Separazione società: nuova autorità, cronologia conservata.',
                            },
                        },
                        db=db,
                    )
                    for digest in event['record'].get('objects', []):
                        if not isinstance(digest, str) or not HASH.fullmatch(digest):
                            raise ValueError('Allegato non valido.')
                        dest = stage / 'objects' / digest
                        if not dest.exists():
                            origin = source.root / 'objects' / digest
                            if origin.is_symlink() or digest_file(origin) != digest:
                                raise ValueError('Allegato originale mancante o corrotto.')
                            shutil.copyfile(origin, dest)
                    db.execute('INSERT INTO changes VALUES(?,?)', (event['id'], encoded(event)))
                for row in src.execute('SELECT id,kind,revision,data FROM records'):
                    if row['id'] in selected:
                        db.execute('INSERT INTO records VALUES(?,?,?,?)', tuple(row))
                for change_id, body in src.execute('SELECT id,body FROM conflicts'):
                    if json.loads(body)['record']['id'] in selected:
                        db.execute(
                            'INSERT INTO conflicts VALUES(?,?)',
                            (change_id, db.execute('SELECT body FROM changes WHERE id=?', (change_id,)).fetchone()[0]),
                        )
            from .society_scope import check_archive

            with target.connect() as db:
                check_archive(target, (json.loads(r[0]) for r in db.execute('SELECT body FROM changes')))
            write_json(
                stage / 'migration-info.json',
                {
                    'source_archive_sha256': source_hash,
                    'organization_id': organization,
                    'records': len(selected),
                    'original_preserved': True,
                },
            )
            return organization

        return manager.install_new(id, info['name'], path, build)
