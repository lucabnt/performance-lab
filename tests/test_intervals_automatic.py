from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.store import Store
from cycling_test.workspaces import Workspaces, invitation, join
from cycling_test.sync import exchange


# Fixture locale sintetica: nessuna richiesta al sito Intervals.icu.
TEST_INTERVALS_ID = 'i' + '9' * 39


def client(root, workspace):
    c = TestClient(create_app(root, token='qa'))
    c.headers.update({'X-Fuorigiri-Token': 'qa', 'X-Fuorigiri-Workspace': workspace})
    return c


def test_intervals_shared_and_preserved_by_old_clients_and_toggle(tmp_path):
    root = tmp_path / 'owner'
    manager = Workspaces(root, Store(root))
    entry = manager.create('DEMO', 'Owner')
    owner = manager.get(entry['id'])
    c = client(root, entry['id'])
    org = owner.list('organization')[0]
    data = {'organization_id': org['id'], 'name': 'Ada', 'surname': 'DEMO', 'intervals_icu_id': TEST_INTERVALS_ID}
    a = c.post('/api/v1/athletes', json=data).json()
    assert a['intervals_icu_id'] == TEST_INTERVALS_ID
    for value in ['999999999999999999999999999999999999999', 'https://example.org', 'i42/../x', 'i42?x', 'I42', 'i']:
        assert c.post('/api/v1/athletes', json={**data, 'intervals_icu_id': value}).status_code == 422
    enabled = c.put(
        f"/api/v1/organizations/{org['id']}/integrations", json={'base': org['revision'], 'intervals_icu_enabled': True}
    )
    assert enabled.status_code == 200
    assert (
        c.put(
            f"/api/v1/organizations/{org['id']}/integrations",
            json={'base': org['revision'], 'intervals_icu_enabled': False},
        ).status_code
        == 409
    )
    old = {k: v for k, v in data.items() if k != 'intervals_icu_id'}
    changed = c.put(f"/api/v1/athletes/{a['id']}?base={a['revision']}", json={**old, 'name': 'Updated'})
    assert changed.json()['intervals_icu_id'] == TEST_INTERVALS_ID
    second = tmp_path / 'viewer'
    replicas = Workspaces(second, Store(second))
    password = 'test-password-only'
    join(replicas, invitation(owner, 'Viewer', 'viewer', password), password)
    replica = replicas.get(entry['id'])
    folder = tmp_path / 'exchange'
    folder.mkdir()
    key = owner.identity['sync_key']
    assert not exchange(owner, folder, key)['errors']
    assert not exchange(replica, folder, key)['errors']
    assert replica.get(a['id'])['intervals_icu_id'] == TEST_INTERVALS_ID
    assert replica.get(org['id'])['intervals_icu_enabled'] is True
    viewer = client(second, entry['id'])
    assert (
        viewer.put(
            f"/api/v1/organizations/{org['id']}/integrations",
            json={'base': enabled.json()['revision'], 'intervals_icu_enabled': False},
        ).status_code
        == 403
    )
    assert viewer.put('/api/v1/sync/automatic', json={'enabled': False}).status_code == 200
    assert c.get('/api/v1/sync/automatic').json()['enabled'] is True
    disabled = c.put(
        f"/api/v1/organizations/{org['id']}/integrations",
        json={'base': enabled.json()['revision'], 'intervals_icu_enabled': False},
    )
    assert disabled.status_code == 200
    assert owner.get(a['id'])['intervals_icu_id'] == TEST_INTERVALS_ID
    exchange(owner, folder, key)
    exchange(replica, folder, key)
    assert replica.get(org['id'])['intervals_icu_enabled'] is False
    assert replica.get(a['id'])['intervals_icu_id'] == TEST_INTERVALS_ID
    assert client(second, entry['id']).get('/api/v1/sync/automatic').json()['enabled'] is False


def test_automatic_preferences_persist_and_are_scoped_to_workspace(tmp_path):
    manager = Workspaces(tmp_path, Store(tmp_path))
    a = manager.create('A', 'Owner')
    b = manager.create('B', 'Owner')
    c = client(tmp_path, a['id'])
    assert c.get('/api/v1/sync/automatic').json() == {'enabled': True, 'configured': False}
    assert c.put('/api/v1/sync/automatic', json={'enabled': False}).status_code == 200
    assert client(tmp_path, a['id']).get('/api/v1/sync/automatic').json()['enabled'] is False
    assert client(tmp_path, b['id']).get('/api/v1/sync/automatic').json()['enabled'] is True
    assert (
        c.post(
            '/api/v1/sync/connection', json={'transport': 'folder', 'folder': str(tmp_path / 'exchange')}
        ).status_code
        == 200
    )
    assert c.get('/api/v1/sync/automatic').json() == {'enabled': False, 'configured': True}


def test_intervals_backup_restores_data_but_not_device_preferences(tmp_path):
    from cycling_test.backup_stream import write_backup
    from cycling_test.recovery import restore

    root = tmp_path / 'source'
    manager = Workspaces(root, Store(root))
    entry = manager.create('DEMO', 'Owner')
    store = manager.get(entry['id'])
    c = client(root, entry['id'])
    org = store.list('organization')[0]
    c.put('/api/v1/sync/automatic', json={'enabled': False})
    c.put(
        f"/api/v1/organizations/{org['id']}/integrations", json={'base': org['revision'], 'intervals_icu_enabled': True}
    )
    a = c.post(
        '/api/v1/athletes',
        json={'organization_id': org['id'], 'name': 'Ada', 'surname': 'DEMO', 'intervals_icu_id': TEST_INTERVALS_ID},
    ).json()
    path = write_backup(store, tmp_path / 'backup.zip')
    other = Workspaces(tmp_path / 'restored', Store(tmp_path / 'restored'))
    copy = other.get(restore(other, path, 'independent', operator='New owner')['id'])
    assert copy.get(a['id'])['intervals_icu_id'] == TEST_INTERVALS_ID
    assert copy.get(org['id'])['intervals_icu_enabled'] is True
    assert not (copy.root / 'sync-automatic.json').exists()


def test_last_success_survives_failure_and_is_scoped_to_destination(tmp_path, monkeypatch):
    from cycling_test import sync_service, sync

    root = tmp_path / 'source'
    manager = Workspaces(root, Store(root))
    entry = manager.create('DEMO', 'Owner')
    store = manager.get(entry['id'])
    c = client(root, entry['id'])
    (tmp_path / 'exchange').mkdir()
    connection = {'transport': 'folder', 'folder': str(tmp_path / 'exchange')}
    c.post('/api/v1/sync/connection', json=connection)
    sync_service.run_sync(store)
    success = c.get('/api/v1/sync/connection').json()['last_successful_sync']
    assert success['ok']

    def fail(*args, **kwargs):
        raise OSError('synthetic offline')

    monkeypatch.setattr(sync, 'exchange', fail)
    import pytest

    with pytest.raises(OSError):
        sync_service.run_sync(store)
    status = c.get('/api/v1/sync/connection').json()
    assert status['last_sync']['ok'] is False
    assert status['last_successful_sync'] == success
    c.post('/api/v1/sync/connection', json={**connection, 'folder': str(tmp_path / 'different')})
    assert c.get('/api/v1/sync/connection').json()['last_successful_sync'] is None
