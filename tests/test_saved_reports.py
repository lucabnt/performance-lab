import json
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.store import Store


def test_saved_report_context_dates_and_download_preserve_records(tmp_path):
    store = Store(tmp_path)
    org = store.save('organization', {'name': 'Club demo'})
    group = store.save('group', {'organization_id': org['id'], 'name': 'Allievi', 'season': '2023'})
    athlete = store.save(
        'athlete', {'organization_id': org['id'], 'name': 'Ada', 'surname': 'Rossi', 'status': 'archived'}
    )
    test = store.save('test', {'organization_id': org['id'], 'athlete_id': athlete['id'], 'date': '2023-05-02'})
    body = b'report fixture'
    digest = store.object(body)
    old = store.save(
        'report',
        {
            'organization_id': org['id'],
            'format': 'pdf',
            'query': {'group': group['id'], 'athlete': athlete['id']},
            'objects': [digest],
        },
    )
    newer = store.save(
        'report', {'organization_id': org['id'], 'format': 'json', 'test_id': test['id'], 'objects': [digest]}
    )
    store.save('report', {'analysis_type': 'maturation', 'format': 'pdf'})
    client = TestClient(create_app(tmp_path, token='qa'))
    client.headers['X-Fuorigiri-Token'] = 'qa'
    response = client.get('/api/v1/reports')
    assert response.status_code == 200
    rows = response.json()
    assert [r['id'] for r in rows] == [newer['id'], old['id']]
    assert rows[0]['saved_at'] and rows[1]['saved_at']
    assert rows[0]['context']['athlete'] == 'Rossi Ada'
    assert rows[0]['context']['test_date'] == '2023-05-02'
    assert rows[1]['context'] == {
        'organization': 'Club demo',
        'group': 'Allievi',
        'season': '2023',
        'athlete': 'Rossi Ada',
        'test_date': '',
    }
    assert store.get(old['id']) == old
    assert client.get('/api/v1/reports/' + newer['id'] + '/download').content == body


def test_repeated_report_downloads_reuse_one_record(tmp_path):
    store = Store(tmp_path)
    org = store.save('organization', {'name': 'Club demo'})
    client = TestClient(create_app(tmp_path, token='qa'))
    client.headers['X-Fuorigiri-Token'] = 'qa'
    for _ in range(3):
        assert client.get(f"/api/v1/history/{org['id']}/report/md").status_code == 200
    assert len(store.list('report')) == 1
    assert client.get(f"/api/v1/history/{org['id']}/report/md", params={'language': 'en'}).status_code == 200
    assert len(store.list('report')) == 2


def test_revoked_admin_downloads_report_without_writing(tmp_path):
    from cycling_test.workspaces import Workspaces, invitation, join
    from cycling_test.sync import exchange

    owner = Workspaces(tmp_path / 'owner', Store(tmp_path / 'owner'))
    entry = owner.create('Club', 'Owner')
    manager = Workspaces(tmp_path / 'coach', Store(tmp_path / 'coach'))
    join(manager, invitation(owner.get(entry['id']), 'Coach', 'admin', 'long-password-123'), 'long-password-123')
    folder = tmp_path / 'cloud'
    folder.mkdir()
    key = owner.get(entry['id']).identity['sync_key']
    exchange(owner.get(entry['id']), folder, key)
    exchange(manager.get(entry['id']), folder, key)
    coach = manager.get(entry['id'])
    (coach.root / 'revocations.json').write_text(
        json.dumps({'revoked': [coach.identity['certificate']['id']]}), encoding='utf-8'
    )
    client = TestClient(create_app(tmp_path / 'coach', token='t'))
    client.headers.update({'X-Fuorigiri-Token': 't', 'X-Fuorigiri-Workspace': entry['id']})
    assert client.get(f"/api/v1/history/{entry['organization_id']}/report/md").status_code == 200
    assert coach.list('report') == []


def test_missing_attachment_is_a_clear_client_error(tmp_path):
    store = Store(tmp_path)
    org = store.save('organization', {'name': 'Club demo'})
    saved = store.save('report', {'organization_id': org['id'], 'format': 'pdf', 'objects': ['0' * 64]})
    client = TestClient(create_app(tmp_path, token='qa'))
    client.headers['X-Fuorigiri-Token'] = 'qa'
    response = client.get('/api/v1/reports/' + saved['id'] + '/download')
    assert response.status_code == 422 and 'Allegato non presente' in response.text


def test_new_reports_keep_the_file_on_the_creating_device_only(tmp_path):
    """REPORT-LOCALE-01: metadata and fingerprint are exchanged, the file is not."""
    from cycling_test.store import save_report
    from cycling_test.sync import exchange
    from cycling_test.workspaces import Workspaces, invitation, join

    owner_ws = Workspaces(tmp_path / 'owner', Store(tmp_path / 'owner'))
    entry = owner_ws.create('Club', 'Owner')
    owner = owner_ws.get(entry['id'])
    other_ws = Workspaces(tmp_path / 'coach', Store(tmp_path / 'coach'))
    join(other_ws, invitation(owner, 'Coach', 'admin', 'long-password-123'), 'long-password-123')
    coach = other_ws.get(entry['id'])
    body = b'%PDF-1.4 report fixture'
    saved = save_report(owner, {'organization_id': entry['organization_id'], 'format': 'pdf', 'query': {}}, body)
    assert 'objects' not in saved and saved['file_bytes'] == len(body)
    for protocol in (1, 2):
        folder = tmp_path / f'cloud-v{protocol}'
        folder.mkdir()
        key = owner.identity['sync_key']
        exchange(owner, folder, key, protocol=protocol)
        exchange(coach, folder, key, protocol=protocol)
        assert all(body not in p.read_bytes() for p in folder.rglob('*') if p.is_file())
        assert sum(p.stat().st_size for p in folder.rglob('*') if p.is_file()) < 200_000
    assert coach.get(saved['id']) == saved
    assert not (coach.root / 'objects' / saved['file_sha256']).exists()

    def client(root):
        c = TestClient(create_app(root, token='qa'))
        c.headers.update({'X-Fuorigiri-Token': 'qa', 'X-Fuorigiri-Workspace': entry['id']})
        return c

    mine = next(r for r in client(tmp_path / 'owner').get('/api/v1/reports').json() if r['id'] == saved['id'])
    theirs = next(r for r in client(tmp_path / 'coach').get('/api/v1/reports').json() if r['id'] == saved['id'])
    assert mine['file_available'] and not theirs['file_available'] and theirs['saved_by'] == 'Owner'
    assert client(tmp_path / 'owner').get(f"/api/v1/reports/{saved['id']}/download").content == body
    response = client(tmp_path / 'coach').get(f"/api/v1/reports/{saved['id']}/download")
    assert response.status_code == 422 and 'solo sul dispositivo' in response.text
