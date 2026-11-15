import io
import json
import sqlite3
import struct
import zipfile
from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from cycling_test.analysis import analyze, window
from cycling_test.methods import DEFAULT, comparison_key
from cycling_test.specialist import lactate, decode_gas, gas_analysis, repeatability
from cycling_test.store import Store
from cycling_test.api import create_app
from cycling_test.fit import decode_fit
from synthetic import crc


def protocol():
    return {
        'segments': [
            {'start_s': 0, 'end_s': 240, 'start_w': 200, 'end_w': 200, 'phase': 'increment'},
            {'start_s': 240, 'end_s': 480, 'start_w': 230, 'end_w': 230, 'phase': 'increment'},
        ]
    }


def samples():
    return [{'t': i, 'power': 100, 'hr': 150, 'cadence': 90} for i in range(661)]


def test_no_rounding_before_completion_and_no_adherence_gate():
    rows = samples()
    for r in rows:
        if 228 <= r['t'] < 240:
            r['power'] = None
    a = analyze(rows, protocol(), {'end_s': 240})
    assert a['map_w'] == 200
    assert a['steps'][0]['adherence']['mean_error_w'] == -100
    assert a['steps'][0]['adherence']['status'] == 'not_evaluated'
    b = analyze(
        rows, protocol(), {'end_s': 240, 'excluded_intervals': [{'start_s': 0, 'end_s': 0.01, 'reason': 'Artefatto'}]}
    )
    assert b['map_w'] is None and b['steps'][0]['power']['coverage'] < 0.95


def test_partial_primary_and_overlap_exclusions():
    a = analyze(samples(), protocol(), {'end_s': 340, 'weight_kg': 50})
    assert a['map_w'] == 200 and a['map_alt_w'] == 212.5
    assert a['map_wkg'] == 4
    assert a['metric_details']['map_alt_w']['status'] == 'estimated'
    assert a['metric_details']['map_alt_w']['method_id'] == 'incremental.constant.partial-linear/1'
    w = window(samples(), 'power', 0, 10, excluded=[{'start_s': 1, 'end_s': 5}, {'start_s': 3, 'end_s': 7}])
    assert w['valid_s'] == 4 and w['mean'] == 100


def test_marker_calibration_gap_and_hr_endpoint():
    rows = samples()
    rows[340]['hr'] = 250
    a = analyze(rows, protocol(), {'end_s': 340, 'alignment_markers': [{'number': 2, 'at_s': 260}]})
    assert a['steps'][1]['actual_s'] == 80 and a['fc_max_test_bpm'] == 150
    assert a['map_alt_w'] == 210
    with pytest.raises(ValueError):
        analyze(rows, protocol(), {'end_s': 340, 'alignment_markers': [{'number': 2, 'at_s': 230}]})


def test_hr_coverage_and_ramp_are_explicit():
    rows = samples()
    for r in rows:
        if 210 <= r['t'] < 217:
            r['hr'] = None
    a = analyze(rows, protocol(), {'end_s': 240})
    assert a['steps'][0]['hr']['mean'] is None
    ramp = protocol()
    ramp['segments'][0]['start_w'] = 100
    a = analyze(samples(), ramp, {'end_s': 240})
    assert a['map_w'] is None and a['terminal_target_w'] == 200 and a['terminal_mean_w'] == 100


def test_negative_channels_not_valid_zeros_retained():
    assert window([{'t': 0, 'power': -1}, {'t': 1, 'power': 0}, {'t': 2, 'power': 1}], 'power', 0, 2)['coverage'] == 0.5
    assert window([{'t': 0, 'hr': 0}, {'t': 1, 'hr': 100}], 'hr', 0, 1)['mean'] is None


def test_presets_new_version_and_legacy_migration(tmp_path):
    root = tmp_path / 'archive'
    s = Store(root)
    t = s.save('test', {'analysis': {'engine': '0.2.0', 'map_w': 100}})
    with s.connect() as db:
        db.execute('PRAGMA user_version=2')
    reopened = Store(root)
    assert reopened.get(t['id']) == t and comparison_key(t).startswith('legacy_unknown')
    backup = root / 'migrations/before-v3.sqlite'
    with sqlite3.connect(backup) as db:
        assert db.execute('PRAGMA user_version').fetchone()[0] == 2
    # No frontend: otherwise the static mount answers 405 to any PUT and hides a missing route.
    c = TestClient(create_app(tmp_path / 'api', token='t', frontend=tmp_path / 'no-frontend'))
    c.headers['X-Fuorigiri-Token'] = 't'
    p = {k: v for k, v in DEFAULT.items() if k in ('name', 'version', 'method_id', 'parameters')}
    p.update(family='custom', version='2', reason='Finestra FC')
    p['parameters'] = deepcopy(p['parameters'])
    p['parameters']['hr_window_s'] = 20
    saved = c.post('/api/v1/analysis-presets', json=p)
    assert saved.status_code == 200
    assert c.post('/api/v1/analysis-presets', json=p).status_code == 422
    assert (
        c.put('/api/v1/analysis-presets/' + saved.json()['id'], json=p).status_code == 404
    )  # presets are immutable: no update route


def test_lactate_fixed_and_dmax_and_ambiguity():
    observations = [
        {'at_s': i, 'power_w': power, 'mmol_l': level}
        for i, (power, level) in enumerate([(100, 1), (150, 1.2), (200, 1.8), (250, 3), (300, 5)])
    ]
    r = lactate({'steps': []}, observations)
    assert r['results']['fixed_4']['value'] == 275
    assert r['results']['fixed_2']['value'] == pytest.approx(208.333333)
    assert 100 < r['results']['dmax']['value'] < 300
    assert r['results']['modified_dmax']['anchor_w'] == 150
    observations[2]['mmol_l'] = 0.9
    assert lactate({'steps': []}, observations)['results']['fixed_4']['value'] is None
    assert lactate({'steps': []}, [{'at_s': 0, 'mmol_l': 2}])['unmatched']


def test_gas_units_peak_and_review_markers():
    rows = decode_gas(('t,vo2_l_min,vco2_l_min,ve_l_min\n' + '\n'.join(f'{t},3,3.2,90' for t in range(661))).encode())
    a = analyze(samples(), protocol(), {'end_s': 480})
    g = gas_analysis(rows, {'end_s': 480, 'weight_kg': 50}, a)
    assert g['vo2peak']['value'] == 3 and g['vo2peak']['ml_kg_min'] == 60
    assert g['vo2max']['value'] is None
    assert g['vo2max']['reason'] == 'maximum_not_verified'
    with pytest.raises(ValueError):
        decode_gas(b't,vo2\n0,3\n1,4')
    with pytest.raises(ValueError):
        gas_analysis(
            rows,
            {
                'end_s': 480,
                'ventilatory_markers': {
                    'vt1': {'at_s': 300, 'evidence': 'Reviewed'},
                    'vt2': {'at_s': 200, 'evidence': 'Reviewed'},
                },
            },
            a,
        )


def test_repeatability_reference_formula():
    r = repeatability([(100, 105), (100, 98), (100, 106), (100, 100), (100, 97)])
    assert r['typical_error'] == pytest.approx((16.7 / 2) ** 0.5)
    assert r['mdc95'] == pytest.approx(1.96 * 16.7**0.5)
    assert repeatability([(100, 101)])['typical_error'] is None
    ci = repeatability([(100, 100 + i) for i in range(6)])['ci95']
    assert ci['replicates'] == 2000 and ci['typical_error'][0] < ci['typical_error'][1]


def test_multisession_selection_and_duplicate_correction():
    body = bytes([0x40, 0, 0]) + struct.pack('<H', 20) + bytes([2, 253, 4, 0x86, 7, 2, 0x84])
    epoch = 1_100_000_000
    for t in (0, 1, 1, 2, 10, 11, 12):
        body += bytes([0]) + struct.pack('<IH', epoch + t, 100 + t)
    body += bytes([0x41, 0, 0]) + struct.pack('<H', 18) + bytes([2, 2, 4, 0x86, 253, 4, 0x86])
    for a, b in ((0, 2), (10, 12)):
        body += bytes([1]) + struct.pack('<II', epoch + a, epoch + b)
    raw = struct.pack('<BBHI4s', 12, 0x10, 100, len(body), b'.FIT') + body
    raw += struct.pack('<H', crc(raw))
    assert len(decode_fit(raw, overview=True)['sessions']) == 2
    with pytest.raises(ValueError):
        decode_fit(raw)
    assert decode_fit(raw, session_index=1)['samples'][0]['power'] == 110
    with pytest.raises(ValueError):
        decode_fit(raw, session_index=0)
    assert (
        len(
            decode_fit(
                raw, session_index=0, duplicate_policy='keep_last', correction_reason='Doppio record confermato'
            )['samples']
        )
        == 3
    )


def test_report_scope_and_method_separation(tmp_path):
    from cycling_test.archive_report import build, render
    from cycling_test.observations import enrich

    s = Store(tmp_path)
    org = s.save('organization', {'name': 'Società sintetica'})
    group = s.save('group', {'organization_id': org['id'], 'name': 'Allievi', 'season': ''})
    child = s.save(
        'group', {'organization_id': org['id'], 'name': 'Allievi', 'parent_id': group['id'], 'season': '2026'}
    )
    p = s.save('protocol', {'name': 'P', 'family': 'P', 'version': '1', 'definition': protocol()})
    athletes = []
    for name in ('Uno', 'Due'):
        a = s.save('athlete', {'organization_id': org['id'], 'name': name, 'surname': 'Esempio', 'birth_year': 2010})
        athletes.append(a)
        s.save('membership', {'athlete_id': a['id'], 'group_id': child['id'], 'start': '2026-01-01', 'end': None})
        for day in ('2026-02-01', '2026-06-01'):
            settings = {'end_s': 340, 'weight_kg': 50, 'weight_source': 'misurato'}
            analysis = enrich(analyze(samples(), protocol(), settings), samples(), settings)
            s.save(
                'test',
                {
                    'organization_id': org['id'],
                    'athlete_id': a['id'],
                    'date': day,
                    'protocol_id': p['id'],
                    'samples': samples(),
                    'settings': settings,
                    'analysis': analysis,
                },
            )
    full = build(s, org['id'])
    sub = build(s, org['id'], athlete=athletes[0]['id'])
    gr = build(s, org['id'], group=group['id'], season='2026')
    assert full['counts']['tests'] == 4 and sub['counts']['tests'] == 2 and gr['counts']['tests'] == 4
    assert {t['revision'] for e in sub['athletes'] for t in e['tests']} <= {
        t['revision'] for e in full['athletes'] for t in e['tests']
    }
    with zipfile.ZipFile(io.BytesIO(render(sub, 'md'))) as z:
        assert json.loads(z.read('manifest.json'))['scope']['athlete'] == athletes[0]['id']
        assert 'Esempio Due' not in z.read('report.md').decode()
    assert render(sub, 'pdf').startswith(b'%PDF')


def test_specialist_api_preserves_input_and_revisions(tmp_path):
    from synthetic import ERG, fit_bytes

    c = TestClient(create_app(tmp_path, token='t'))
    c.headers['X-Fuorigiri-Token'] = 't'

    def post(path, data):
        r = c.post('/api/v1/' + path, json=data)
        assert r.status_code == 200, r.text
        return r.json()

    org = post('organizations', {'name': 'Demo'})
    athlete = post('athletes', {'organization_id': org['id'], 'name': 'Uno', 'surname': 'Simulazione'})
    protocol = c.post(
        '/api/v1/protocols', data={'name': 'P', 'family': 'P', 'version': '1'}, files={'file': ('p.erg', ERG)}
    ).json()
    trace = c.post('/api/v1/traces', files={'file': ('t.fit', fit_bytes())}).json()
    gas = c.post(
        '/api/v1/gas-traces',
        files={'file': ('gas.csv', ('t,vo2_l_min\n' + '\n'.join(f'{i},3' for i in range(1600))).encode())},
    ).json()
    payload = {
        'athlete_id': athlete['id'],
        'protocol_id': protocol['id'],
        'trace_hash': trace['hash'],
        'date': '2026-01-01',
        'settings': {'end_s': 1440, 'gas_hash': gas['hash'], 'weight_kg': 50},
    }
    original = post('tests', payload)
    assert original['analysis']['gas']['vo2peak']['value'] == 3
    assert gas['hash'] in original['objects']
    changed = deepcopy(payload)
    changed['settings']['end_s'] = 1400
    r = c.put(
        '/api/v1/tests/' + original['id'],
        json={'base': original['revision'], 'reason': 'Fine corretta', 'test': changed},
    )
    assert r.status_code == 200 and gas['hash'] in r.json()['objects']
    revisions = c.get('/api/v1/records/' + original['id'] + '/revisions').json()
    assert len(revisions) == 2 and revisions[0]['analysis']['duration_s'] == 1440
    archive = c.get('/api/v1/archive/' + org['id'] + '/report/pdf')
    assert archive.status_code == 200 and archive.content.startswith(b'%PDF')
    bad = post('organizations', {'name': 'Altra'})
    assert c.get('/api/v1/archive/' + bad['id'] + '/report-data?athlete=' + athlete['id']).status_code == 422
