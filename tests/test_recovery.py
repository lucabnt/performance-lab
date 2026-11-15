import io
import json
import zipfile
import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.store import Store
from cycling_test.workspaces import Workspaces, invitation, join, revoke_member, apply_invitation
from cycling_test.recovery import backup_bytes, inspect_backup, restore, export_recovery
from cycling_test.sync import exchange

PASSWORD = 'test-only-password-123'


def club(root):
    manager = Workspaces(root, Store(root))
    entry = manager.create('Club Demo', 'Fondatore Demo')
    store = manager.get(entry['id'])
    original = store.object(b'original fixture')
    athlete = store.save(
        'athlete',
        {'organization_id': entry['organization_id'], 'name': 'Demo', 'surname': 'Atleta', 'objects': [original]},
    )
    return manager, entry, store, athlete


def client(root, workspace=''):
    c = TestClient(create_app(root, token='test'))
    c.headers.update({'X-Fuorigiri-Token': 'test', 'X-Fuorigiri-Workspace': workspace})
    return c


def modified_zip(raw, transform):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        files = {n: z.read(n) for n in z.namelist()}
    transform(files)
    out = io.BytesIO()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for n, body in files.items():
            z.writestr(n, body)
    return out.getvalue()


def test_snapshot_independent_and_founder_recovery(tmp_path):
    a, entry, source, athlete = club(tmp_path / 'source')
    raw = backup_bytes(source)
    recovery = export_recovery(source, PASSWORD)
    b = Workspaces(tmp_path / 'b', Store(tmp_path / 'b'))
    snapshot = restore(b, raw, 'snapshot')
    read = b.get(snapshot['id'])
    assert read.get(athlete['id']) == athlete
    assert read.read_object(athlete['objects'][0]) == b'original fixture'
    c = client(tmp_path / 'b', snapshot['id'])
    assert (
        c.post(
            '/api/v1/athletes', json={'organization_id': entry['organization_id'], 'name': 'X', 'surname': 'Y'}
        ).status_code
        == 403
    )
    assert c.post('/api/v1/sync', json={'folder': str(tmp_path), 'key': ''}).status_code == 422
    independent = restore(b, raw, 'independent', operator='Nuovo fondatore')
    copy = b.get(independent['id'])
    assert copy.identity['workspace'] != source.identity['workspace']
    assert copy.identity['sync_key'] != source.identity['sync_key']
    assert copy.get(athlete['id']) == athlete and copy.history(athlete['id']) == source.history(athlete['id'])
    assert not (copy.root / 'members.json').exists()
    with copy.connect() as db:
        for row in db.execute('SELECT body FROM changes'):
            copy.verify_change(json.loads(row[0]))
    recovered = restore(b, raw, 'recover', recovery_raw=recovery, password=PASSWORD)
    restored = b.get(recovered['id'])
    assert restored.identity == source.identity
    assert restored.get(athlete['id']) == athlete
    with source.connect() as x, restored.connect() as y:
        assert (
            x.execute("SELECT value FROM config WHERE key='device'").fetchone()[0]
            != y.execute("SELECT value FROM config WHERE key='device'").fetchone()[0]
        )
    restored.save('athlete', {**athlete, 'name': 'Aggiornato'}, athlete['id'], athlete['revision'])
    with pytest.raises(ValueError):
        restore(b, raw, 'recover', recovery_raw=recovery, password=PASSWORD)
    folder = tmp_path / 'shared'
    folder.mkdir()
    assert not exchange(restored, folder, restored.identity['sync_key'])['errors']


@pytest.mark.parametrize('case', ['traversal', 'corrupt-db', 'missing-object', 'future-schema'])
def test_bad_backup_rejected_without_registry_changes(tmp_path, case):
    a, entry, source, _ = club(tmp_path / 'a')
    raw = backup_bytes(source)

    def transform(files):
        if case == 'traversal':
            files['../escape.txt'] = b'bad'
        if case == 'corrupt-db':
            files['archive.sqlite'] = b'not a database'
        if case == 'missing-object':
            files.pop(next(n for n in files if n.startswith('objects/')))
        if case == 'future-schema':
            files['manifest.json'] = b'{"schema":999}'

    raw = modified_zip(raw, transform)
    b = Workspaces(tmp_path / 'b', Store(tmp_path / 'b'))
    with pytest.raises(ValueError):
        restore(b, raw, 'snapshot')
    assert b.entries() == [] and not (tmp_path / 'escape.txt').exists()


def test_recovery_wrong_password_other_society_and_nonempty_destination(tmp_path):
    a, entry, source, _ = club(tmp_path / 'a')
    b = Workspaces(tmp_path / 'b', Store(tmp_path / 'b'))
    raw = backup_bytes(source)
    credentials = export_recovery(source, PASSWORD)
    with pytest.raises(ValueError):
        restore(b, raw, 'recover', recovery_raw=credentials, password='wrong')
    other, _, different, _ = club(tmp_path / 'other')
    with pytest.raises(ValueError):
        restore(b, raw, 'recover', recovery_raw=export_recovery(different, PASSWORD), password=PASSWORD)
    destination = tmp_path / 'keep'
    destination.mkdir()
    (destination / 'important.txt').write_text('KEEP')
    with pytest.raises(ValueError):
        restore(b, raw, 'snapshot', path=str(destination))
    assert (destination / 'important.txt').read_text() == 'KEEP' and b.entries() == []


def test_legacy_backup_and_multiple_societies(tmp_path):
    source = Store(tmp_path / 'legacy')
    for name in ('Club A', 'Club B'):
        source.save('organization', {'name': name})
    raw = modified_zip(backup_bytes(source), lambda f: f.update({'manifest.json': b'{"schema":1}'}))
    b = Workspaces(tmp_path / 'b', Store(tmp_path / 'b'))
    snapshot = restore(b, raw, 'snapshot')
    assert len(snapshot['organizations']) == 2 and len(b.get(snapshot['id']).list('organization')) == 2
    assert inspect_backup(raw)['manifest']['schema'] == 1


def test_api_preview_commit_recovery_and_bootstrap_roles(tmp_path):
    a, entry, source, athlete = club(tmp_path / 'a')
    c = client(tmp_path / 'a', entry['id'])
    b = client(tmp_path / 'b')
    invite = c.post('/api/v1/workspace/invite', json={'name': 'Lettore PC2', 'role': 'viewer', 'password': PASSWORD})
    assert invite.status_code == 200
    joined = b.post(
        '/api/v1/workspaces/join', data={'password': PASSWORD}, files={'file': ('invite.json', invite.content)}
    )
    assert joined.status_code == 200, joined.text
    b.headers['X-Fuorigiri-Workspace'] = entry['id']
    assert not b.get('/api/v1/workspace/members').json()['ready']
    assert b.get('/api/v1/state').json()['organization'] == []
    assert b.post('/api/v1/workspace/recovery', json={'password': PASSWORD}).status_code == 403
    folder = tmp_path / 'cloud'
    folder.mkdir()
    assert c.post('/api/v1/sync', json={'folder': str(folder), 'key': ''}).status_code == 200
    sync = b.post('/api/v1/sync', json={'folder': str(folder), 'key': ''})
    assert sync.status_code == 200, sync.text
    members = b.get('/api/v1/workspace/members').json()
    assert members['ready'] and members['last_sync']['ok'] and len(members['members']) == 2
    assert members['founder_id'] == source.identity['certificate']['id']
    assert (
        b.post(
            '/api/v1/athletes', json={'organization_id': entry['organization_id'], 'name': 'No', 'surname': 'Write'}
        ).status_code
        == 403
    )
    data = c.get('/api/v1/backup').content
    preview = b.post('/api/v1/workspaces/restore/preview', files={'file': ('backup.zip', data)})
    assert preview.status_code == 200, preview.text
    result = b.post(
        '/api/v1/workspaces/restore', data={'backup_hash': preview.json()['backup_hash'], 'mode': 'snapshot'}
    )
    assert result.status_code == 200, result.text
    assert not list((tmp_path / 'b/restore-staging').iterdir())
    assert c.post('/api/v1/workspace/recovery', json={'password': PASSWORD}).status_code == 200
    # Even a reader may add a separate club; the role is scoped to the selected society.
    assert b.post('/api/v1/workspaces', json={'name': 'Another', 'operator': 'Owner'}).status_code == 200


def test_renew_role_and_revocation_keeps_exact_history(tmp_path):
    a, entry, left, athlete = club(tmp_path / 'a')
    b = Workspaces(tmp_path / 'b', Store(tmp_path / 'b'))
    join(b, invitation(left, 'Coach', 'admin', PASSWORD), PASSWORD)
    right = b.get(entry['id'])
    old = right.identity['certificate']['id']
    folder = tmp_path / 'cloud'
    folder.mkdir()
    key = left.identity['sync_key']
    exchange(left, folder, key)
    exchange(right, folder, key)
    written = right.save('athlete', {**athlete, 'name': 'Coach edit'}, athlete['id'], athlete['revision'])
    exchange(right, folder, key)
    exchange(left, folder, key)
    raw = invitation(left, 'Coach viewer', 'viewer', PASSWORD, replace_id=old)
    # A disconnected old key still signs, but its newly seen events are rejected.
    right.save('athlete', {**written, 'name': 'Unseen write'}, written['id'], written['revision'])
    exchange(right, folder, key)
    exchange(left, folder, key)
    assert left.get(athlete['id'])['name'] == 'Coach edit'
    exchange(right, folder, key)
    with pytest.raises(ValueError):
        right.save('athlete', {'name': 'Revoked'})
    apply_invitation(right, raw, PASSWORD)
    assert right.identity['certificate']['role'] == 'viewer' and right.identity['private_key'] is None
    with pytest.raises(ValueError):
        right.save('athlete', {'name': 'Reader'})
    new = Workspaces(tmp_path / 'new', Store(tmp_path / 'new'))
    join(new, invitation(left, 'New reader', 'viewer', PASSWORD), PASSWORD)
    exchange(left, folder, key)
    fresh = new.get(entry['id'])
    exchange(fresh, folder, key)
    assert fresh.get(athlete['id'])['name'] == 'Coach edit'
    with left.connect() as db:
        event = json.loads(db.execute('SELECT body FROM changes WHERE id=?', (written['revision'],)).fetchone()[0])
    left.verify_change(event)
    # Same ID re-signed with different contents is not in the revocation whitelist.
    event['record']['name'] = 'Forged'
    with pytest.raises(ValueError):
        left.verify_change(event)


def test_duplicate_join_leaves_custom_destination_untouched(tmp_path):
    a, entry, left, _ = club(tmp_path / 'a')
    b = Workspaces(tmp_path / 'b', Store(tmp_path / 'b'))
    raw = invitation(left, 'Viewer', 'viewer', PASSWORD)
    join(b, raw, PASSWORD)
    destination = tmp_path / 'empty'
    destination.mkdir()
    with pytest.raises(ValueError):
        join(b, raw, PASSWORD, str(destination))
    assert list(destination.iterdir()) == []


def test_api_recover_and_apply_promotion_invitation(tmp_path):
    a, entry, source, athlete = club(tmp_path / 'a')
    owner = client(tmp_path / 'a', entry['id'])
    reader = client(tmp_path / 'b')
    raw = owner.post(
        '/api/v1/workspace/invite', json={'name': 'PC reader', 'role': 'viewer', 'password': PASSWORD}
    ).content
    reader.post('/api/v1/workspaces/join', data={'password': PASSWORD}, files={'file': ('invite.json', raw)})
    reader.headers['X-Fuorigiri-Workspace'] = entry['id']
    current = reader.get('/api/v1/workspace/members').json()['current']['id']
    renewed = owner.post(
        '/api/v1/workspace/invite',
        json={'name': 'PC admin', 'role': 'admin', 'password': PASSWORD, 'replace_id': current},
    )
    assert renewed.status_code == 200
    applied = reader.post(
        '/api/v1/workspaces/access', data={'password': PASSWORD}, files={'file': ('invite.json', renewed.content)}
    )
    assert applied.status_code == 200, applied.text
    folder = tmp_path / 'share'
    folder.mkdir()
    owner.post('/api/v1/sync', json={'folder': str(folder), 'key': ''})
    reader.post('/api/v1/sync', json={'folder': str(folder), 'key': ''})
    assert (
        reader.post(
            '/api/v1/athletes',
            json={'organization_id': entry['organization_id'], 'name': 'Admin', 'surname': 'Allowed'},
        ).status_code
        == 200
    )
    data = owner.get('/api/v1/backup').content
    keys = owner.post('/api/v1/workspace/recovery', json={'password': PASSWORD}).content
    new = client(tmp_path / 'recovered')
    p = new.post('/api/v1/workspaces/restore/preview', files={'file': ('backup.zip', data)}).json()
    result = new.post(
        '/api/v1/workspaces/restore',
        data={'backup_hash': p['backup_hash'], 'mode': 'recover', 'password': PASSWORD},
        files={'recovery_file': ('keys.json', keys)},
    )
    assert result.status_code == 200, result.text
    new.headers['X-Fuorigiri-Workspace'] = entry['id']
    assert new.get('/api/v1/state').json()['operator']['owner']
    assert (
        new.post(
            '/api/v1/workspace/invite', json={'name': 'New PC', 'role': 'viewer', 'password': PASSWORD}
        ).status_code
        == 200
    )


def test_failed_registration_rolls_back_empty_destination(tmp_path, monkeypatch):
    a, entry, source, _ = club(tmp_path / 'a')
    b = Workspaces(tmp_path / 'b', Store(tmp_path / 'b'))
    dest = tmp_path / 'dest'
    dest.mkdir()

    def fail(entry):
        raise OSError('simulated registry failure')

    monkeypatch.setattr(b, 'register', fail)
    with pytest.raises(OSError):
        restore(b, backup_bytes(source), 'snapshot', path=str(dest))
    assert list(dest.iterdir()) == [] and b.entries() == []


def test_older_recovery_uses_newer_signed_access_directory(tmp_path):
    a, entry, source, _ = club(tmp_path / 'a')
    old_keys = export_recovery(source, PASSWORD)
    invitation(source, 'Invitato dopo il recupero', 'viewer', PASSWORD)
    member = json.loads((source.root / 'members.json').read_text(encoding='utf-8'))[0]
    revoke_member(source, member['id'])
    b = Workspaces(tmp_path / 'b', Store(tmp_path / 'b'))
    result = restore(b, backup_bytes(source), 'recover', recovery_raw=old_keys, password=PASSWORD)
    recovered = b.get(result['id'])
    assert member['id'] in recovered.revocations()
    directory = json.loads((recovered.root / 'members.json').read_text(encoding='utf-8'))
    assert any(m['id'] == member['id'] for m in directory)


def test_optional_local_audit_shape_remains_bounded(tmp_path):
    _, _, store, _ = club(tmp_path / 'source')
    with store.connect() as db:
        db.execute('CREATE TABLE sync_audit (seq INTEGER PRIMARY KEY, body TEXT NOT NULL, digest TEXT NOT NULL)')
    assert inspect_backup(backup_bytes(store))
    with store.connect() as db:
        db.execute('DROP TABLE sync_audit')
        db.execute('CREATE TABLE sync_audit (body TEXT)')
    with pytest.raises(ValueError, match='Schema registro locale'):
        inspect_backup(backup_bytes(store))


def test_abandoned_restore_previews_are_pruned_at_startup(tmp_path):
    import os, time
    from cycling_test.api import create_app

    staging = tmp_path / 'restore-staging'
    staging.mkdir()
    old = staging / ('a' * 64)
    old.write_bytes(b'old preview')
    recent = staging / ('b' * 64)
    recent.write_bytes(b'recent preview')
    stale = time.time() - 2 * 24 * 3600
    os.utime(old, (stale, stale))
    create_app(tmp_path, token='qa')
    assert not old.exists() and recent.read_bytes() == b'recent preview'
