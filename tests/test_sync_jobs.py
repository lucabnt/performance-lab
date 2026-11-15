import threading
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.store import Store
from cycling_test.workspaces import Workspaces, write_json
from cycling_test import sync_jobs, sync_service


def setup(root):
    manager = Workspaces(root, Store(root))
    entry = manager.create('QA', 'Owner')
    c = TestClient(create_app(root, token='qa'))
    c.headers.update({'X-Fuorigiri-Token': 'qa', 'X-Fuorigiri-Workspace': entry['id']})
    return manager, entry, c


def test_sync_job_does_not_block_preferences_or_status_and_deduplicates(tmp_path, monkeypatch):
    manager, entry, c = setup(tmp_path)
    store = manager.get(entry['id'])
    entered = threading.Event()
    release = threading.Event()
    calls = []

    def slow(selected, verify_all=False, progress=None):
        calls.append(selected.root)
        entered.set()
        progress('inventory')
        assert release.wait(5)
        return {
            'errors': [],
            'pending': 0,
            'published': 0,
            'received': 0,
            'conflicts': 0,
            'downloaded_packets': 0,
            'known_packets_skipped': 42,
        }

    monkeypatch.setattr(sync_service, 'run_sync', slow)
    try:
        first = c.post('/api/v1/sync/start', json={})
        assert first.status_code == 200
        assert entered.wait(2)
        assert first.json()['status'] == 'running'
        assert c.get('/api/v1/device/preferences').status_code == 200
        assert c.get('/api/v1/sync/job').json()['phase'] == 'inventory'
        assert c.post('/api/v1/sync/start', json={}).json()['id'] == first.json()['id']
        assert len(calls) == 1 and calls[0] == store.root
        assert c.post('/api/v1/workspaces/' + entry['id'] + '/detach', json={}).status_code == 422
    finally:
        release.set()
    finished = sync_jobs.wait(store, 5)
    assert finished['status'] == 'completed' and finished['finished_at']
    assert finished['result']['known_packets_skipped'] == 42
    assert c.get('/api/v1/sync/job').json()['status'] == 'completed'


def test_interrupted_job_is_not_reported_as_success_and_failures_are_sanitized(tmp_path, monkeypatch):
    manager, entry, c = setup(tmp_path)
    store = manager.get(entry['id'])
    write_json(store.root / 'sync-job.json', {'id': 'old', 'status': 'running'})
    assert c.get('/api/v1/sync/job').json()['status'] == 'interrupted'

    def failure(*args, **kwargs):
        raise ValueError('private-password-never-expose')

    monkeypatch.setattr(sync_service, 'run_sync', failure)
    c.post('/api/v1/sync/start', json={'verify_all': True})
    result = sync_jobs.wait(store, 5)
    assert result['status'] == 'failed' and result['full_verification']
    assert 'private-password' not in str(c.get('/api/v1/sync/job').json())


def test_observed_transport_preserves_incremental_exchange_and_reports_real_io(tmp_path):
    manager, entry, c = setup(tmp_path)
    store = manager.get(entry['id'])
    folder = tmp_path / 'shared'
    folder.mkdir()
    write_json(store.root / 'sync-connection.json', {'transport': 'folder', 'folder': str(folder)})
    c.post('/api/v1/sync/start', json={})
    first = sync_jobs.wait(store, 5)
    assert first['status'] == 'completed'
    assert first['writes'] > 0
    c.post('/api/v1/sync/start', json={})
    second = sync_jobs.wait(store, 5)
    assert second['result']['published'] == 0
    assert second['result']['downloaded_packets'] == 0
    assert second['result']['known_packets_skipped'] > 0
    assert not second['full_verification']


def test_mobile_background_exchange_leaves_bridge_requests_responsive(tmp_path, monkeypatch):
    import json, base64
    from cycling_test.mobile_runtime import MobileRuntime

    manager = Workspaces(tmp_path, Store(tmp_path))
    entry = manager.create('Mobile QA', 'Owner')
    store = manager.get(entry['id'])
    write_json(
        store.root / 'sync-connection.json',
        {'transport': 'webdav', 'url': 'https://example.invalid/dav', 'username': 'qa'},
    )
    entered = threading.Event()
    release = threading.Event()
    outcome = []

    def slow(*args, **kwargs):
        entered.set()
        assert release.wait(5)
        return {'errors': [], 'pending': 0}

    monkeypatch.setattr(sync_service, 'run_sync', slow)
    runtime = MobileRuntime(tmp_path)
    worker = threading.Thread(target=lambda: outcome.append(runtime.sync_all()), daemon=True)
    worker.start()
    try:
        assert entered.wait(2)
        response = json.loads(
            runtime.request(
                json.dumps({'path': '/api/v1/device/preferences', 'method': 'GET', 'headers': {}, 'body': ''})
            )
        )
        assert response['status'] == 200
        response = json.loads(
            runtime.request(
                json.dumps(
                    {
                        'path': '/api/v1/sync/job',
                        'method': 'GET',
                        'headers': {'X-Fuorigiri-Workspace': entry['id']},
                        'body': '',
                    }
                )
            )
        )
        assert json.loads(base64.b64decode(response['body']))['status'] == 'running'
    finally:
        release.set()
        worker.join(5)
    assert outcome == [True]
