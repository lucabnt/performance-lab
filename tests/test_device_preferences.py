import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.store import Store
from cycling_test.workspaces import Workspaces


def client(root, port=50001):
    c = TestClient(create_app(root, token='qa'), base_url=f'http://127.0.0.1:{port}')
    c.headers['X-Fuorigiri-Token'] = 'qa'
    return c


def test_preferences_survive_new_origin_and_merge_without_society_writes(tmp_path):
    c = client(tmp_path)
    assert c.get('/api/v1/device/preferences').json() == {'language': None, 'time_zone': 'local'}
    assert c.put('/api/v1/device/preferences', json={'language': 'en'}).status_code == 200
    assert c.put('/api/v1/device/preferences', json={'time_zone': 'Europe/Rome'}).json() == {
        'language': 'en',
        'time_zone': 'Europe/Rome',
    }
    assert client(tmp_path, 50002).get('/api/v1/device/preferences').json() == {
        'language': 'en',
        'time_zone': 'Europe/Rome',
    }
    assert Store(tmp_path).list('organization') == []
    assert c.put('/api/v1/device/preferences', json={'language': 'xx'}).status_code == 422
    assert c.put('/api/v1/device/preferences', json={'time_zone': 'bad'}).status_code == 422
    assert TestClient(create_app(tmp_path, token='qa')).get('/api/v1/device/preferences').status_code == 401


def test_detach_and_restore_preserve_archive_identity_and_other_club(tmp_path):
    manager = Workspaces(tmp_path, Store(tmp_path))
    first = manager.create('First', 'Founder')
    second = manager.create('Second', 'Founder')
    store = manager.get(first['id'])
    identity = store.identity
    records = store.list('organization')
    c = client(tmp_path)
    assert (
        c.put(
            '/api/v1/workspaces/last-selection',
            json={'workspace': first['id'], 'organization': first['organization_id']},
        ).status_code
        == 200
    )
    assert c.post('/api/v1/workspaces/' + first['id'] + '/detach', json={}).status_code == 200
    assert [e['id'] for e in c.get('/api/v1/workspaces').json()] == [second['id']]
    assert c.get('/api/v1/workspaces/last-selection').json() == {'workspace': '', 'organization': ''}
    assert c.get('/api/v1/workspaces/detached').json()[0]['id'] == first['id']
    assert store.identity == identity and store.list('organization') == records
    with pytest.raises(ValueError):
        manager.get(first['id'])
    with pytest.raises(ValueError):
        manager.register(first)
    assert c.post('/api/v1/workspaces/' + first['id'] + '/reattach', json={}).status_code == 200
    assert manager.get(first['id']).identity == identity
    assert len(manager.entries()) == 2
    assert c.get('/api/v1/workspaces/detached').json() == []
    assert c.post('/api/v1/workspaces/missing/detach', json={}).status_code == 422
