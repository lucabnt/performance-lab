from cycling_test.history import paired_comparison, summarize
from cycling_test.store import Store


def test_non_ascii_session_token_is_rejected(tmp_path):
    from fastapi.testclient import TestClient
    from cycling_test.api import create_app

    client = TestClient(create_app(tmp_path, token='test'))
    assert client.get('/api/v1/state', headers={b'x-fuorigiri-token': b'\xff'}).status_code == 401


def test_csv_parser_errors_are_validation_errors(tmp_path):
    import csv
    from cycling_test.csv_import import read
    from fastapi.testclient import TestClient
    from cycling_test.api import create_app

    client = TestClient(create_app(tmp_path, token='test'))
    client.headers['X-Fuorigiri-Token'] = 'test'
    assert (
        read(b'name,note\r\nQA,"first line\r\nsecond ""quoted"" line"\r\n')[0]['note']
        == 'first line\r\nsecond "quoted" line'
    )
    org = client.post('/api/v1/organizations', json={'name': 'QA'}).json()
    for raw in (
        b'atleta_id,cognome,nome\nx,Demo,"unfinished',
        b'atleta_id,cognome,nome\nx,Demo,' + b'a' * (csv.field_size_limit() + 1),
    ):
        response = client.post(
            '/api/v1/import/preview',
            data={'organization_id': org['id'], 'profile': 'atleti'},
            files={'file': ('bad.csv', raw)},
        )
        assert response.status_code == 422
    assert client.get('/api/v1/state').json()['athlete'] == []


def test_csv_export_excludes_deleted_measurements(tmp_path):
    import csv
    import io
    import json
    import zipfile
    from cycling_test.reports import export_csv

    s, org, athlete, _ = records(tmp_path)
    for status, weight in [('active', 50), ('deleted', 60)]:
        s.save(
            'measurement', {'athlete_id': athlete['id'], 'date': '2026-01-01', 'weight_kg': weight, 'status': status}
        )
    with zipfile.ZipFile(io.BytesIO(export_csv(s, org['id']))) as archive:
        rows = list(csv.DictReader(io.StringIO(archive.read('antropometria.csv').decode())))
        assert [row['peso_kg'] for row in rows] == ['50']
        extended = json.loads(archive.read('extended/archive.json'))
        assert len(extended['measurement']) == 1


def records(tmp_path):
    s = Store(tmp_path)
    org = s.save('organization', {'name': 'QA'})
    athlete = s.save('athlete', {'organization_id': org['id'], 'name': 'QA', 'surname': 'Atleta'})
    protocol = s.save('protocol', {'name': 'Protocollo QA', 'version': '1'})
    return s, org, athlete, protocol


def save_test(s, org, athlete, protocol, year, source, weight_source='misurato'):
    return s.save(
        'test',
        {
            'organization_id': org['id'],
            'athlete_id': athlete['id'],
            'protocol_id': protocol['id'],
            'date': year + '-06-01',
            'settings': {'weight_source': weight_source, 'weight_kg': 50},
            'analysis': {
                'engine': 'manual-1',
                'threshold_source': source,
                'map_w': 200 if year == '2025' else 220,
                'map_wkg': 4 if year == '2025' else 4.4,
                'lactate_3p5_hr_bpm': 150 if year == '2025' else 155,
            },
        },
    )


def test_paired_sources_without_threshold_and_declared_do_not_crash(tmp_path):
    s, org, a, p = records(tmp_path)
    for year in ('2025', '2026'):
        for source in (None, 'dichiarato'):
            save_test(s, org, a, p, year, source)
    result = paired_comparison(s, org['id'], '2025', '2026')
    assert result['n_pairs'] == 2
    assert all(r['map_w_delta'] == 20 for r in result['pairs'])


def test_paired_estimated_weight_is_excluded_but_power_and_dynamic_metrics_remain(tmp_path):
    s, org, a, p = records(tmp_path)
    save_test(s, org, a, p, '2025', None, 'stimato')
    save_test(s, org, a, p, '2026', None)
    result = paired_comparison(s, org['id'], '2025', '2026')['pairs'][0]
    assert result['map_w_delta'] == 20
    assert result['map_wkg_delta'] is None and result['map_wkg_pct'] is None
    assert result['lactate_3p5_hr_bpm_delta'] == 5


def test_progression_deltas_also_exclude_estimated_weight(tmp_path):
    s, org, a, p = records(tmp_path)
    save_test(s, org, a, p, '2025', None, 'stimato')
    save_test(s, org, a, p, '2026', None)
    last = summarize(s, org['id'])['changes'][-1]
    assert last['map_w_delta'] == 20 and last['map_wkg_delta'] is None


def test_frontend_pages_carry_a_content_security_policy(tmp_path):
    from fastapi.testclient import TestClient
    from cycling_test.api import create_app

    web = tmp_path / 'web'
    web.mkdir()
    (web / 'index.html').write_text('<!doctype html><title>x</title>', encoding='utf-8')
    client = TestClient(create_app(tmp_path / 'data', token='t', frontend=web))
    policy = client.get('/').headers['content-security-policy']
    assert "script-src 'self';" in policy and 'unsafe-eval' not in policy
    assert "frame-ancestors 'none'" in policy and "object-src 'none'" in policy
    api = client.get('/api/v1/state', headers={'X-Fuorigiri-Token': 't'})
    assert 'content-security-policy' not in api.headers


def test_lock_hashes_follow_the_lockfile(tmp_path):
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / 'scripts' / 'lock_hashes.py'
    spec = importlib.util.spec_from_file_location('lock_hashes', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.check() == []
    (tmp_path / 'requirements-lock-windows.txt').write_text(
        'Foo_Bar==1.0\nbaz==2.0\n-r requirements-common.txt\n', encoding='utf-8'
    )
    (tmp_path / 'requirements-lock-windows.hashes').write_text(
        f'foo-bar==1.0 \\\n    --hash=sha256:{"a" * 64}\nbaz==2.1 \\\n    --hash=sha256:{"b" * 64}\nqux==1\n',
        encoding='utf-8',
    )
    assert module.check(tmp_path) == [
        'requirements-lock-windows.hashes: baz 2.0 nel lock, 2.1 negli hash.',
        'requirements-lock-windows.hashes: qux presente solo negli hash.',
    ]
