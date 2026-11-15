import json
import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.store import Store
from cycling_test.workspaces import Workspaces, invitation, join
from cycling_test.sync import exchange


def test_last_society_survives_backend_restart_and_origin_change(tmp_path):
    manager = Workspaces(tmp_path, Store(tmp_path))
    first = manager.create('First', 'Owner')
    second = manager.create('Second', 'Owner')
    choice = {'workspace': second['id'], 'organization': second['organization_id']}
    client = TestClient(create_app(tmp_path, token='first'), base_url='http://127.0.0.1:50001')
    client.headers['X-Fuorigiri-Token'] = 'first'
    assert client.get('/api/v1/workspaces/last-selection').json() == {'workspace': '', 'organization': ''}
    assert client.put('/api/v1/workspaces/last-selection', json=choice).status_code == 200
    reopened = TestClient(create_app(tmp_path, token='second'), base_url='http://127.0.0.1:50002')
    reopened.headers['X-Fuorigiri-Token'] = 'second'
    assert reopened.get('/api/v1/workspaces/last-selection').json() == choice
    assert set(json.loads((tmp_path / 'last-selection.json').read_text())) == {'workspace', 'organization'}
    assert (
        reopened.put(
            '/api/v1/workspaces/last-selection', json={**choice, 'organization': first['organization_id']}
        ).status_code
        == 422
    )
    assert reopened.get('/api/v1/workspaces/last-selection').json() == choice
    assert TestClient(create_app(tmp_path, token='private')).get('/api/v1/workspaces/last-selection').status_code == 401
    (tmp_path / 'last-selection.json').write_text('invalid', encoding='utf-8')
    assert reopened.get('/api/v1/workspaces/last-selection').json() == {'workspace': '', 'organization': ''}


def test_viewer_can_remember_society_without_writing_society_records(tmp_path):
    owner = Workspaces(tmp_path / 'owner', Store(tmp_path / 'owner'))
    entry = owner.create('Club', 'Owner')
    manager = Workspaces(tmp_path / 'viewer', Store(tmp_path / 'viewer'))
    joined = join(
        manager, invitation(owner.get(entry['id']), 'Reader', 'viewer', 'long-password-123'), 'long-password-123'
    )
    folder = tmp_path / 'cloud'
    folder.mkdir()
    exchange(owner.get(entry['id']), folder, owner.get(entry['id']).identity['sync_key'])
    exchange(manager.get(joined['id']), folder, manager.get(joined['id']).identity['sync_key'])
    client = TestClient(create_app(tmp_path / 'viewer', token='t'))
    client.headers.update({'X-Fuorigiri-Token': 't', 'X-Fuorigiri-Workspace': joined['id']})
    assert (
        client.put(
            '/api/v1/workspaces/last-selection',
            json={'workspace': joined['id'], 'organization': joined['organization_id']},
        ).status_code
        == 200
    )
    assert client.post('/api/v1/organizations', json={'name': 'Forbidden'}).status_code == 403
    assert (
        client.post(
            '/api/v1/memberships/batch', json={'group_id': 'g', 'athlete_ids': ['a'], 'start': '2026-01-01'}
        ).status_code
        == 403
    )
    assert (
        client.put('/api/v1/groups/g', json={'base': 'r', 'organization_id': 'o', 'name': 'Forbidden'}).status_code
        == 403
    )
    assert client.post('/api/v1/groups/g/lifecycle', json={'base': 'r', 'status': 'deleted'}).status_code == 403


def test_separate_archives_viewer_and_forgery(tmp_path):
    a = Workspaces(tmp_path / 'a', Store(tmp_path / 'a'))
    b = Workspaces(tmp_path / 'b', Store(tmp_path / 'b'))
    entry = a.create('Club', 'Owner')
    store = a.get(entry['id'])
    other = a.create('Other', 'Owner')
    assert not a.get(other['id']).list('athlete')
    raw = invitation(store, 'Reader', 'viewer', 'long-password-123')
    joined = join(b, raw, 'long-password-123')
    viewer = b.get(joined['id'])
    with pytest.raises(ValueError):
        viewer.save('athlete', {'name': 'Forged'})
    folder = tmp_path / 'cloud'
    folder.mkdir()
    exchange(store, folder, store.identity['sync_key'])
    exchange(viewer, folder, viewer.identity['sync_key'])
    assert viewer.list('organization')[0]['name'] == 'Club'
    c = TestClient(create_app(tmp_path / 'b', token='t'))
    c.headers.update({'X-Fuorigiri-Token': 't', 'X-Fuorigiri-Workspace': entry['id']})
    assert c.post('/api/v1/organizations', json={'name': 'Not allowed'}).status_code == 403
    assert (
        c.post(
            '/api/v1/athletes', json={'name': 'A', 'surname': 'B', 'organization_id': entry['organization_id']}
        ).status_code
        == 403
    )
    assert c.get('/api/v1/state').json()['operator']['role'] == 'viewer'
    identity = viewer.identity
    assert identity['private_key'] is None and 'authority_private' not in identity
    from cryptography.fernet import Fernet

    cipher = Fernet(store.identity['sync_key'].encode())
    shared = next(folder.iterdir())
    packet = next(shared.glob('*.ctsync'))
    forged = json.loads(cipher.decrypt(packet.read_bytes()))
    forged['change']['record']['name'] = 'Tampered with shared read key'
    (shared / 'forged.ctsync').write_bytes(cipher.encrypt(json.dumps(forged).encode()))
    result = exchange(viewer, folder, viewer.identity['sync_key'])
    assert result['errors']
    assert viewer.list('organization')[0]['name'] == 'Club'


def test_signed_concurrent_resolution_converges(tmp_path):
    a = Workspaces(tmp_path / 'a', Store(tmp_path / 'a'))
    entry = a.create('Club', 'Owner')
    left = a.get(entry['id'])
    b = Workspaces(tmp_path / 'b', Store(tmp_path / 'b'))
    join(b, invitation(left, 'Coach', 'admin', 'long-password-123'), 'long-password-123')
    right = b.get(entry['id'])
    folder = tmp_path / 'cloud'
    folder.mkdir()
    key = left.identity['sync_key']
    original = left.list('organization')[0]
    exchange(left, folder, key)
    exchange(right, folder, key)
    l = left.save('organization', {'name': 'Left'}, original['id'], original['revision'])
    r = right.save('organization', {'name': 'Right'}, original['id'], original['revision'])
    exchange(left, folder, key)
    exchange(right, folder, key)
    exchange(left, folder, key)
    merged = left.save('organization', {'name': 'Merged'}, original['id'], l['revision'], parents=[r['revision']])
    exchange(left, folder, key)
    exchange(right, folder, key)
    assert right.get(original['id'])['revision'] == merged['revision']
    assert right.get(original['id'])['name'] == 'Merged'


def test_store_is_reused_until_the_database_file_changes(tmp_path):
    import shutil

    manager = Workspaces(tmp_path, Store(tmp_path))
    entry = manager.create('Cached', 'Owner')
    store = manager.get(entry['id'])
    assert manager.get(entry['id']) is store
    store.save('athlete', {'name': 'Ada', 'organization_id': entry['organization_id']})
    assert manager.get(entry['id']) is store
    # A replaced file (restore, manual copy) is opened again with the usual checks.
    database = tmp_path / 'workspaces' / entry['id'] / 'archive.sqlite'
    shutil.copy(database, database.with_name('copy.sqlite'))
    database.with_name('copy.sqlite').replace(database)
    reopened = manager.get(entry['id'])
    assert reopened is not store and [a['name'] for a in reopened.list('athlete')] == ['Ada']
    manager.set_detached(entry['id'], True)
    with pytest.raises(ValueError):
        manager.get(entry['id'])


def test_verifier_checks_every_event_signature_with_cached_certificates(tmp_path):
    from cryptography.exceptions import InvalidSignature

    manager = Workspaces(tmp_path, Store(tmp_path))
    entry = manager.create('Verified', 'Owner')
    store = manager.get(entry['id'])
    store.save('athlete', {'name': 'Ada', 'organization_id': entry['organization_id']})
    with store.connect() as db:
        changes = [json.loads(r[0]) for r in db.execute('SELECT body FROM changes ORDER BY rowid')]
    check = store.verifier()
    for change in changes:
        check(change)
    altered = {**changes[-1], 'record': {**changes[-1]['record'], 'name': 'Eve'}}
    with pytest.raises(InvalidSignature):
        check(altered)
    forged = {**changes[-1], 'certificate': {**changes[-1]['certificate'], 'name': 'Eve'}}
    with pytest.raises(InvalidSignature):
        check(forged)
    with pytest.raises(ValueError):
        check({**changes[-1], 'workspace': 'other'})


def test_sealed_files_state_scrypt_parameters_and_old_files_still_open():
    import base64
    import os
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    from cycling_test.store import encoded
    from cycling_test.workspaces import seal, unseal

    password = 'invito-di-prova-12'
    envelope = json.loads(seal({'x': 1}, password))
    assert envelope['kdf'] == {'name': 'scrypt', 'n': 2**17, 'r': 8, 'p': 1}
    assert unseal(json.dumps(envelope), password) == {'x': 1}
    with pytest.raises(InvalidToken):
        unseal(json.dumps(envelope), 'password-sbagliata')
    for kdf in ({**envelope['kdf'], 'n': 2**21}, {**envelope['kdf'], 'n': 3 * 2**14}, {**envelope['kdf'], 'r': 1}):
        with pytest.raises(ValueError, match='aggiornare'):
            unseal(json.dumps({**envelope, 'kdf': kdf}), password)
    # Envelope written before RT-12: no parameters, n = 2**14.
    salt = os.urandom(16)
    key = Scrypt(salt=salt, length=32, n=2**14, r=8, p=1).derive(password.encode())
    legacy = {
        'salt': base64.b64encode(salt).decode(),
        'encrypted': Fernet(base64.urlsafe_b64encode(key)).encrypt(encoded({'x': 2}).encode()).decode(),
    }
    assert unseal(json.dumps(legacy), password) == {'x': 2}


def test_viewer_write_exceptions_are_declared_on_routes(tmp_path):
    owner = Workspaces(tmp_path / 'a', Store(tmp_path / 'a'))
    entry = owner.create('Club', 'Owner')
    reader = Workspaces(tmp_path / 'b', Store(tmp_path / 'b'))
    joined = join(
        reader, invitation(owner.get(entry['id']), 'Reader', 'viewer', 'long-password-123'), 'long-password-123'
    )
    app = create_app(tmp_path / 'b', token='t')
    client = TestClient(app)
    client.headers.update({'X-Fuorigiri-Token': 't', 'X-Fuorigiri-Workspace': joined['id']})
    org = joined['organization_id']
    refused = client.post('/api/v1/athletes', json={'organization_id': org, 'first_name': 'A', 'last_name': 'B'})
    assert refused.status_code == 403
    assert client.put('/api/v1/sync/automatic', json={'enabled': False}).status_code != 403
    # Detaching is device-local: a viewer may do it with its own society selected (RT-20).
    assert client.post(f'/api/v1/workspaces/{joined["id"]}/detach').status_code == 200
    marked = {
        r.path for r in app.routes if getattr(r, 'methods', None) and getattr(r.endpoint, 'viewer_allowed', False)
    }
    assert '/api/v1/workspaces/{id}/detach' in marked and '/api/v1/athletes' not in marked
