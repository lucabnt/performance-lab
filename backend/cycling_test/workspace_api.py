import json
from typing import Literal
from fastapi import UploadFile, Form, File
from pydantic import BaseModel, Field
from .workspaces import invitation, join, revoke_member, member_directory, apply_invitation


RESTORE_STAGING_MAX_AGE_S = 24 * 3600


def prune_restore_staging(root, max_age_s=RESTORE_STAGING_MAX_AGE_S):
    """Remove restore previews abandoned by the operator (up to 64 GB each).

    Only regular files older than the threshold are touched; a recent preview
    awaiting confirmation stays available. Errors never block startup.
    """
    import time
    from pathlib import Path

    folder = Path(root) / 'restore-staging'
    removed = 0
    if not folder.is_dir():
        return 0
    limit = time.time() - max_age_s
    for path in folder.iterdir():
        try:
            if path.is_file() and not path.is_symlink() and path.stat().st_mtime < limit:
                path.unlink()
                removed += 1
        except OSError:
            continue
    return removed


def install_workspaces(app, manager, store, download):
    prune_restore_staging(manager.root)

    class Create(BaseModel):
        name: str = Field(min_length=1, max_length=300)
        operator: str = Field(min_length=1, max_length=300)
        path: str = ''

    class Invite(BaseModel):
        name: str = Field(min_length=1, max_length=300)
        role: Literal['admin', 'viewer']
        password: str = Field(min_length=12)
        replace_id: str | None = None

    class RecoveryPassword(BaseModel):
        password: str = Field(min_length=12, max_length=1000)

    @app.get('/api/v1/workspaces')
    def list_workspaces():
        return manager.entries()

    class DevicePreferences(BaseModel):
        language: Literal['it', 'en'] | None = None
        time_zone: Literal['local', 'Europe/Rome', 'UTC'] | None = None

    def preferences():
        try:
            value = DevicePreferences.model_validate_json(
                (manager.root / 'device-preferences.json').read_text(encoding='utf-8')
            )
            return {'language': value.language, 'time_zone': value.time_zone or 'local'}
        except (OSError, ValueError):
            return {'language': None, 'time_zone': 'local'}

    @app.get('/api/v1/device/preferences')
    def device_preferences():
        return preferences()

    @app.put('/api/v1/device/preferences')
    def save_device_preferences(data: DevicePreferences):
        from .workspaces import write_json

        with manager.lock:
            value = {**preferences(), **data.model_dump(exclude_none=True)}
            write_json(manager.root / 'device-preferences.json', value)
        return value

    @app.get('/api/v1/workspaces/detached')
    def detached_workspaces():
        return [e for e in manager.entries(include_detached=True) if e.get('detached')]

    @app.post('/api/v1/workspaces/{id}/detach')
    def detach_workspace(id: str):
        return manager.set_detached(id, True)

    @app.post('/api/v1/workspaces/{id}/reattach')
    def reattach_workspace(id: str):
        return manager.set_detached(id, False)

    class LastSelection(BaseModel):
        workspace: str = Field(max_length=100)
        organization: str = Field(max_length=100)

    @app.get('/api/v1/workspaces/last-selection')
    def last_selection():
        # Device preference, outside society databases and synchronized records.
        path = manager.root / 'last-selection.json'
        try:
            return LastSelection.model_validate_json(path.read_text(encoding='utf-8')).model_dump()
        except (OSError, ValueError):
            return {'workspace': '', 'organization': ''}

    @app.put('/api/v1/workspaces/last-selection')
    def remember_selection(data: LastSelection):
        from .workspaces import write_json

        selected = manager.get(data.workspace)
        if data.organization and not any(o['id'] == data.organization for o in selected.list('organization')):
            raise ValueError('Società non presente nell’archivio selezionato.')
        with manager.lock:
            write_json(manager.root / 'last-selection.json', data.model_dump())
        return data.model_dump()

    @app.post('/api/v1/workspaces/restore/preview')
    def restore_preview(file: UploadFile, backup_password: str = Form('', max_length=1000)):
        from .recovery import summary
        from .backup_stream import inspect_file, digest_file, MAX_COMPRESSED, CHUNK
        from .backup_crypto import is_encrypted, decrypt_file
        import hashlib, os
        from uuid import uuid4

        prune_restore_staging(manager.root)
        pending = manager.root / 'restore-staging'
        pending.mkdir(exist_ok=True)
        temp = pending / (str(uuid4()) + '.tmp')
        digest = hashlib.sha256()
        size = 0
        try:
            with temp.open('xb') as out:
                os.chmod(temp, 0o600)
                while chunk := file.file.read(CHUNK):
                    size += len(chunk)
                    if size > MAX_COMPRESSED:
                        raise ValueError('Backup oltre 64 GB.')
                    digest.update(chunk)
                    out.write(chunk)
            encrypted = is_encrypted(temp)
            if encrypted:
                # Staged as the decrypted v3 ZIP: restore and its checks stay unchanged.
                plain = pending / (str(uuid4()) + '.plain.tmp')
                try:
                    decrypt_file(temp, plain, backup_password)
                    os.chmod(plain, 0o600)
                    temp.unlink()
                    plain.rename(temp)
                finally:
                    plain.unlink(missing_ok=True)
            with inspect_file(temp) as data:
                info = summary(data)
            value = digest_file(temp) if encrypted else digest.hexdigest()
            path = pending / value
            temp.replace(path)
            return {**info, 'backup_hash': value, 'encrypted': encrypted}
        finally:
            temp.unlink(missing_ok=True)

    @app.post('/api/v1/workspaces/restore')
    def restore_archive(
        backup_hash: str = Form(),
        mode: Literal['snapshot', 'independent', 'recover'] = Form(),
        path: str = Form(''),
        operator: str = Form(''),
        password: str = Form(''),
        recovery_file: UploadFile | None = File(default=None),
    ):
        from .recovery import restore
        import re

        if not re.fullmatch('[0-9a-f]{64}', backup_hash):
            raise ValueError('Identificatore backup non valido.')
        pending = manager.root / 'restore-staging' / backup_hash
        from .backup_stream import digest_file

        try:
            digest = digest_file(pending)
        except FileNotFoundError as exc:
            raise ValueError('Ripetere l’anteprima del backup.') from exc
        if digest != backup_hash:
            raise ValueError('Anteprima non integra: ricaricare il backup.')
        recovery_raw = recovery_file.file.read(1_000_001) if recovery_file else None
        if recovery_raw and len(recovery_raw) > 1_000_000:
            raise ValueError('File di recupero troppo grande.')
        try:
            result = restore(manager, pending, mode, path, operator, recovery_raw, password)
        except OSError as exc:
            raise ValueError(
                'Ripristino non completato: cartella non disponibile o scrittura non riuscita. Nessun archivio esistente sovrascritto.'
            ) from exc
        try:
            pending.unlink(missing_ok=True)
        except OSError:
            pass  # Cache cleanup must not turn a published restore into a reported failure.
        return result

    class SaveBackup(BaseModel):
        path: str = Field(min_length=1, max_length=2000)
        # Optional: empty keeps the unencrypted v3 ZIP.
        password: str = Field('', max_length=1000)

    @app.post('/api/v1/backup/scalable/save')
    def save_scalable_backup(data: SaveBackup):
        from pathlib import Path
        from .backup_stream import write_backup
        from .backup_crypto import write_encrypted_backup, SUFFIX

        target = Path(data.path).expanduser()
        suffix = SUFFIX if data.password else '.zip'
        if not target.is_absolute() or target.suffix.lower() != suffix:
            raise ValueError(f'Indicare un percorso assoluto di file {suffix}.')
        root = store.root.resolve()
        resolved = target.resolve()
        if root == resolved or root in resolved.parents:
            raise ValueError('Salvare il backup fuori dalla cartella dati della società.')
        if data.password:
            write_encrypted_backup(store, target, data.password)
            return {
                'path': str(target),
                'schema': 3,
                'encrypted': True,
                'note': 'Backup protetto da password scritto e completato. Senza la password non è recuperabile. Conservare separatamente il recupero degli accessi.',
            }
        write_backup(store, target)
        return {
            'path': str(target),
            'schema': 3,
            'note': 'Backup scritto e completato. Conservare separatamente il recupero degli accessi.',
        }

    @app.post('/api/v1/workspaces/split/preview')
    def split_preview():
        from .society_migration import preview

        return preview(store)

    class SplitSociety(BaseModel):
        organization_id: str
        source_hash: str = Field(pattern='^[0-9a-f]{64}$')
        operator: str = Field(min_length=1, max_length=300)
        path: str = ''

    @app.post('/api/v1/workspaces/split')
    def split_society(data: SplitSociety):
        from .society_migration import extract
        from .sync_service import lock

        with lock(store.root):
            return extract(manager, store, data.organization_id, data.source_hash, data.operator, data.path)

    @app.post('/api/v1/workspaces/access')
    def replace_access(file: UploadFile, password: str = Form()):
        if not hasattr(store, 'identity'):
            raise ValueError('Selezionare la società prima di applicare il nuovo invito.')
        raw = file.file.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ValueError('Invito troppo grande.')
        from .sync_service import lock

        try:
            with lock(store.root):
                return apply_invitation(store, raw, password)
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError('Invito non valido o password errata.') from exc

    @app.post('/api/v1/workspace/recovery')
    def recovery(data: RecoveryPassword):
        from .recovery import export_recovery

        if not hasattr(store, 'identity'):
            raise ValueError('Selezionare una società con fondatore.')
        return download(export_recovery(store, data.password), 'application/json', 'fuorigiri-recupero-accessi.json')

    @app.post('/api/v1/workspaces')
    def create(data: Create):
        try:
            return manager.create(data.name, data.operator, data.path)
        except OSError as exc:
            raise ValueError('Creazione non completata: verificare cartella e permessi di scrittura.') from exc

    @app.post('/api/v1/workspaces/join')
    def join_workspace(file: UploadFile, password: str = Form(), path: str = Form('')):
        raw = file.file.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ValueError('Invito troppo grande.')
        try:
            return join(manager, raw, password, path)
        except Exception as exc:
            raise ValueError('Invito non valido, password errata o cartella non disponibile.') from exc

    @app.post('/api/v1/workspace/invite')
    def invite(data: Invite):
        if not hasattr(store, 'identity'):
            raise ValueError('Creare un workspace separato prima di condividere.')
        from .sync_service import lock

        with lock(store.root):
            return download(
                invitation(store, data.name, data.role, data.password, data.replace_id),
                'application/json',
                'fuorigiri-invito.json',
            )

    @app.get('/api/v1/workspace/members')
    def members():
        if not hasattr(store, 'identity'):
            return {'members': [], 'folder': '', 'managed': False}
        if store.identity.get('snapshot'):
            return {
                'members': [],
                'folder': '',
                'managed': False,
                'snapshot': True,
                'current': store.identity['certificate'],
                'owner': False,
            }
        folder = store.root / 'sync-folder.txt'
        directory = store.root / 'access.json'
        directory_data = json.loads(directory.read_text(encoding='utf-8')) if directory.exists() else {}
        members = directory_data.get('members', member_directory(store))
        members = list({m['id']: m for m in members + [store.identity['certificate']]}.values())
        last_sync = store.root / 'last-sync.json'
        from .society_scope import check_archive

        scope_error = None
        try:
            check_archive(store)
        except ValueError as exc:
            scope_error = str(exc)
        return {
            'scope_error': scope_error,
            'members': members,
            'current': store.identity['certificate'],
            'path': str(store.root),
            'founder_id': directory_data.get(
                'founder_id', store.identity['certificate']['id'] if store.identity.get('authority_private') else None
            ),
            'last_sync': json.loads(last_sync.read_text(encoding='utf-8')) if last_sync.exists() else None,
            'ready': bool(store.list('organization')),
            'revoked': store.revocations(),
            'folder': folder.read_text() if folder.exists() else '',
            'managed': True,
            'owner': bool(store.identity.get('authority_private')),
        }

    @app.post('/api/v1/workspace/revoke/{id}')
    def revoke(id: str):
        if not hasattr(store, 'identity') or not store.identity.get('authority_private'):
            raise ValueError('Solo il dispositivo fondatore revoca gli accessi.')
        if id == store.identity['certificate']['id']:
            raise ValueError('Non revocare il fondatore da questa procedura.')
        from .sync_service import lock

        with lock(store.root):
            revoke_member(store, id)
        return {
            'revoked': id,
            'note': 'Revoca delle scritture recepita dai PC al prossimo scambio. Le copie già ricevute restano disponibili.',
        }

    @app.get('/api/v1/reports')
    def reports():
        # Display metadata only: never rewrite the signed report records.
        with store.connect() as db:
            records = {
                r['id']: r
                for row in db.execute(
                    "SELECT data FROM records WHERE kind IN ('report','organization','group','athlete','test')"
                )
                if (r := json.loads(row[0]))
            }
            dates = {
                row[0]: json.loads(row[1]).get('created_at', '')
                for row in db.execute(
                    "SELECT r.revision,c.body FROM records r LEFT JOIN changes c ON c.id=r.revision WHERE r.kind='report'"
                )
                if row[1]
            }
        result = []
        for r in records.values():
            if r['kind'] != 'report' or r.get('analysis_type') == 'maturation':
                continue
            scope = r.get('query') or {}
            test = records.get(r.get('test_id'), {})
            athlete = records.get(scope.get('athlete') or test.get('athlete_id'), {})
            group = records.get(scope.get('group'), {})
            organization = records.get(r.get('organization_id'), {})
            result.append(
                {
                    **r,
                    'saved_at': dates.get(r['revision'], ''),
                    'context': {
                        'organization': organization.get('name', ''),
                        'group': group.get('name', ''),
                        'season': scope.get('season') or group.get('season', ''),
                        'athlete': ' '.join(filter(None, [athlete.get('surname'), athlete.get('name')])),
                        'test_date': test.get('date', ''),
                    },
                }
            )
        return sorted(result, key=lambda r: (r['saved_at'], r['id']), reverse=True)

    @app.get('/api/v1/reports/{id}/download')
    def report(id: str):
        r = store.get(id)
        if r['kind'] != 'report':
            raise ValueError('Artefatto non valido.')
        return download(
            store.read_object(r['objects'][0]),
            'application/json'
            if r['format'] == 'json'
            else 'application/pdf'
            if r['format'] == 'pdf'
            else 'application/zip',
            'report.' + ('json' if r['format'] == 'json' else 'pdf' if r['format'] == 'pdf' else 'zip'),
        )

    class Resolution(BaseModel):
        choice: Literal['local', 'remote']

    @app.post('/api/v1/conflicts/{id}/resolve')
    def resolve(id: str, data: Resolution):
        with store.connect() as db:
            row = db.execute('SELECT body FROM conflicts WHERE id=?', (id,)).fetchone()
        if not row:
            raise ValueError('Conflitto non trovato o già risolto.')
        incoming = json.loads(row[0])
        current = store.get(incoming['record']['id'])
        payload = current if data.choice == 'local' else incoming['record']
        saved = store.save(current['kind'], payload, current['id'], current['revision'], parents=[id])
        with store.connect() as db:
            db.execute('DELETE FROM conflicts WHERE id=?', (id,))
        return saved
