"""SYNC-SPAZIO-01 phase 0: read-only analysis of the exchange channel."""

import hashlib
import hmac
import json
from cycling_test.store import encoded
from cycling_test.sync import exchange
from cycling_test.sync_space import analyze, token_size
from cycling_test.transports import FolderTransport
from cryptography.fernet import Fernet
from test_sync_v2 import devices, simple_test, trace_test


def snapshot(folder):
    return {p.relative_to(folder): hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob('*') if p.is_file()}


def channel(store, folder):
    key = store.identity['sync_key']
    return FolderTransport(folder, hashlib.sha256(key.encode()).hexdigest()[:24], store.root)


def test_token_size_matches_fernet():
    cipher = Fernet(Fernet.generate_key())
    for n in (0, 1, 15, 16, 17, 1000, 1_048_576):
        assert token_size(n) == len(cipher.encrypt(b'x' * n))


def test_analysis_reports_v1_and_v2_contents_without_writing(tmp_path):
    owner, other, folder = devices(tmp_path)
    key = owner.identity['sync_key']
    trace_test(owner)
    for n in range(40):
        simple_test(owner, n)
    exchange(owner, folder, key)  # v1 packets
    exchange(owner, folder, key, protocol=2)
    exchange(other, folder, key, protocol=2)
    before = snapshot(folder)
    with owner.connect() as db:
        local = db.execute('SELECT count(*) FROM changes').fetchone()[0]
    report = analyze(owner, channel(owner, folder))
    assert snapshot(folder) == before
    on_disk = sum(p.stat().st_size for p in folder.rglob('*') if p.is_file())
    assert report['bytes'] == on_disk and report['unreadable'] == 0
    assert report['v1']['events'] == local and report['v1']['covered_by_v2']['files'] == local
    assert report['v1']['by_kind']['test']['files'] == 41
    assert report['v2']['distinct_events'] == local == report['v2']['event_copies']
    assert report['v2']['missing_chunks'] == 0 and report['v2']['unreferenced_chunks']['files'] == 0
    assert report['categories']['v2_chunks']['files'] > 0


def test_analysis_counts_duplicated_events_orphans_and_tampered_files(tmp_path):
    owner, _, folder = devices(tmp_path)
    key = owner.identity['sync_key']
    for n in range(10):
        simple_test(owner, n)
    exchange(owner, folder, key, protocol=2)
    transport = channel(owner, folder)
    cipher = Fernet(key.encode())
    with owner.connect() as db:
        local = db.execute('SELECT count(*) FROM changes').fetchone()[0]
    # A second valid page with part of the same events models whole-history republication.
    page = next(n for n in transport.list() if n.endswith('.ctsync2'))
    payload = json.loads(cipher.decrypt(transport.get(page)))
    duplicate = encoded({**payload, 'events': payload['events'][:5]}).encode()
    address = hmac.new(key.encode(), duplicate, hashlib.sha256).hexdigest()
    transport.put('page2-' + address + '.ctsync2', cipher.encrypt(duplicate))
    transport.put('page2-' + '0' * 64 + '.ctsync2', transport.get(page))
    transport.put('blob2-' + '1' * 64 + '.ctobj', cipher.encrypt(b'orphan'))
    report = analyze(owner, transport)
    assert report['unreadable'] == 1  # the renamed page fails its keyed address
    assert report['v2']['unreferenced_chunks']['files'] == 1
    assert report['v2']['distinct_events'] == local and report['v2']['event_copies'] == local + 5
    assert report['v2']['redundant_page_bytes'] > 0 and report['reclaimable_bytes'] > 0


def test_space_job_api_runs_in_background_on_the_configured_destination(tmp_path):
    from fastapi.testclient import TestClient
    from cycling_test.api import create_app
    from cycling_test.store import Store
    from cycling_test.workspaces import Workspaces
    from cycling_test import sync_space

    root = tmp_path / 'device'
    manager = Workspaces(root, Store(root))
    entry = manager.create('QA', 'Owner')
    store = manager.get(entry['id'])
    folder = tmp_path / 'exchange'
    folder.mkdir()
    c = TestClient(create_app(root, token='qa'))
    c.headers.update({'X-Fuorigiri-Token': 'qa', 'X-Fuorigiri-Workspace': entry['id']})
    assert c.post('/api/v1/sync/connection', json={'transport': 'folder', 'folder': str(folder)}).status_code == 200
    simple_test(store, 1)
    exchange(store, folder, store.identity['sync_key'], protocol=2)
    assert c.get('/api/v1/sync/space/job').json()['status'] == 'idle'
    assert c.post('/api/v1/sync/space/start').json()['status'] in ('running', 'completed')
    job = sync_space.wait(store)
    assert job['status'] == 'completed' and job['result']['v2']['distinct_events'] == 2
    assert c.get('/api/v1/sync/space/job').json()['result']['files'] == job['result']['files']
