import csv
import io
import zipfile
from copy import deepcopy

import pytest
from fastapi.testclient import TestClient
from cycling_test.api import Settings, create_app
from cycling_test.specialist import lactate
from cycling_test.lactate_levels import validate_levels
from cycling_test.methods import comparison_key
from synthetic import ERG, fit_bytes


def case():
    stages = [
        {
            'number': i + 1,
            'start_w': w,
            'end_w': w,
            'aligned_start_s': i * 240,
            'aligned_end_s': (i + 1) * 240,
            'actual_s': 240,
            'complete': True,
            'hr': {'mean': hr, 'coverage': 1, 'usable': True},
        }
        for i, (w, hr) in enumerate([(200, 150), (240, 160)])
    ]
    a = {'steps': stages, 'preset': {'parameters': {'hr_window_s': 30, 'hr_coverage': 0.8}}}
    observations = [
        {'at_s': 260, 'delay_s': 20, 'step_number': 1, 'mmol_l': 3},
        {'at_s': 500, 'delay_s': 20, 'step_number': 2, 'mmol_l': 5},
    ]
    return a, observations


def test_linear_oracle_and_provenance():
    a, obs = case()
    r = lactate(a, obs, [3, 3.5, 4, 5, 6], 50, 'misurato')
    v = r['results']['fixed_4']
    assert v['value'] == 220 and v['hr_bpm'] == 155 and v['wkg'] == 4.4
    assert r['results']['fixed_3p5']['value'] == 210
    assert r['results']['fixed_3']['hr_bpm'] == 150
    assert r['results']['fixed_6']['value'] is None
    assert v['supporting_points'][0]['at_s'] == 260
    assert v['supporting_points'][0]['hr_bpm'] == 150
    assert r['method_snapshot']['hr_window_s'] == 30
    assert v['status'] == 'estimated' and v['method_id'] == 'lactate.fixed-linear/2'


@pytest.mark.parametrize('problem', ['missing', 'coverage', 'partial', 'short', 'ramp'])
def test_invalid_stage_hr_does_not_remove_power(problem):
    a, obs = case()
    stage = a['steps'][1]
    if problem == 'missing':
        stage['hr']['mean'] = None
    elif problem == 'coverage':
        stage['hr'].update(mean=None, usable=False, coverage=0.5)
    elif problem == 'partial':
        stage['complete'] = False
    elif problem == 'short':
        stage['actual_s'] = 10
    else:
        stage['end_w'] = 260
        obs[1]['power_w'] = 240
    r = lactate(a, obs, [4])['results']['fixed_4']
    assert r['value'] == 220 and r['hr_bpm'] is None
    assert r['hr_reason'] == 'stage_hr_unavailable'


def test_ambiguous_nonmonotone_and_duplicate_loads():
    a, obs = case()
    obs[1]['mmol_l'] = 2
    assert lactate(a, obs, [3])['results']['fixed_3']['value'] is None
    a, obs = case()
    obs[0]['power_w'] = 240
    assert lactate(a, obs, [4])['results']['fixed_4']['value'] is None
    a, obs = case()
    obs[0]['mmol_l'] = obs[1]['mmol_l'] = 4
    assert lactate(a, obs, [4])['results']['fixed_4']['reason'] == 'ambiguous_crossing'


def test_estimated_weight_is_not_used_and_explicit_load_without_step_has_no_hr():
    a, obs = case()
    r = lactate(a, obs, [4], 50, 'stimato')['results']['fixed_4']
    assert r['wkg'] is None and r['hr_bpm'] == 155
    r = lactate(
        {'steps': []}, [{'at_s': 0, 'power_w': 200, 'mmol_l': 3}, {'at_s': 1, 'power_w': 240, 'mmol_l': 5}], [4]
    )['results']['fixed_4']
    assert r['value'] == 220 and r['hr_bpm'] is None


@pytest.mark.parametrize(
    'levels', [[], [2, 2], [0], [41], [float('nan')], [float('inf')], [2.0001], [True], list(range(1, 22))]
)
def test_invalid_levels(levels):
    with pytest.raises(ValueError):
        validate_levels(levels)


def seed_api(root):
    client = TestClient(create_app(root, token='test'))
    client.headers['X-Fuorigiri-Token'] = 'test'

    def post(path, body):
        r = client.post('/api/v1/' + path, json=body)
        assert r.status_code == 200, r.text
        return r.json()

    org = post('organizations', {'name': 'Lattato QA - SIMULAZIONE'})
    athlete = post('athletes', {'organization_id': org['id'], 'name': 'Giulia', 'surname': 'Sintetica'})
    r = client.post(
        '/api/v1/protocols',
        data={'name': 'Incrementale lattato QA', 'family': 'QA-LAT', 'version': '1', 'warmup_s': 600},
        files={'file': ('demo.erg', ERG)},
    )
    assert r.status_code == 200, r.text
    protocol = r.json()
    r = client.post('/api/v1/traces', files={'file': ('demo.fit', fit_bytes())})
    assert r.status_code == 200, r.text
    payload = {
        'athlete_id': athlete['id'],
        'protocol_id': protocol['id'],
        'date': '2026-10-18',
        'trace_hash': r.json()['hash'],
        'settings': {
            'end_s': 1440,
            'weight_kg': 50,
            'weight_source': 'misurato',
            'lactate_levels': [2, 3, 3.5, 4, 6],
            'lactate': [
                {'step_number': i, 'at_s': t, 'mmol_l': level}
                for i, t, level in [(2, 840, 1), (3, 1080, 3), (4, 1320, 5)]
            ],
        },
    }
    saved = post('tests', payload)
    return client, org, saved, payload


def test_api_revision_histories_exports_and_reports(tmp_path):
    c, org, t, payload = seed_api(tmp_path)
    a = t['analysis']
    assert a['lactate_3p5_w'] == 105
    assert a['lactate_3p5_wkg'] == 2.1 and a['lactate_3p5_hr_bpm'] is not None
    detail = a['metric_details']['lactate_3p5_hr_bpm']
    assert detail['unit'] == 'bpm' and detail['status'] == 'estimated'
    h = c.get('/api/v1/history/' + org['id']).json()
    assert 'lactate_3p5_hr_bpm' in h['coverage']
    assert '3.5 mmol/L' in h['metric_labels']['lactate_3p5_hr_bpm']
    from cycling_test.store import Store

    old_store = Store(tmp_path)
    digest = old_store.object(b'old renderer cache')
    old_store.save(
        'report',
        {
            'test_revision': t['revision'],
            'renderer_version': '0.8',
            'format': 'md',
            'language': 'it',
            'objects': [digest],
        },
    )
    report = c.get('/api/v1/tests/' + t['id'] + '/report/md')
    with zipfile.ZipFile(io.BytesIO(report.content)) as z:
        md = z.read('report.md').decode()
        assert '**Sintetica Giulia**' in md
        assert '3.5 mmol/L (bpm)' in md and 'lactate.fixed-linear/2' in md
    from cycling_test.store import Store
    from cycling_test.reports import export_csv

    with zipfile.ZipFile(io.BytesIO(export_csv(Store(tmp_path), org['id']))) as z:
        rows = list(csv.DictReader(io.StringIO(z.read('extended/lattato_livelli.csv').decode())))
        row = next(r for r in rows if float(r['mmol_l']) == 3.5)
        assert float(row['power_w']) == 105 and row['hr_bpm']
    history_report = c.get('/api/v1/history/' + org['id'] + '/report/md?metric=lactate_3p5_hr_bpm')
    assert history_report.status_code == 200, history_report.text
    with zipfile.ZipFile(io.BytesIO(history_report.content)) as z:
        assert '3.5 mmol/L' in z.read('report.md').decode()
    from cycling_test.archive_report import build

    archive = build(Store(tmp_path), org['id'])
    assert archive['coverage']['lactate_3p5_hr_bpm']['valid'] == 1
    # Existing immutable revision remains unchanged; method identities distinguish v1/v2.
    old = deepcopy(t)
    old['analysis']['lactate_analysis'].pop('method_snapshot')
    assert comparison_key(old) != comparison_key(t)
    payload['settings']['lactate_levels'] = [2, 4]
    assert c.get('/api/v1/tests/' + t['id']).json()['settings']['lactate_levels'] == [2, 3, 3.5, 4, 6]


def test_csv_preloads_are_associated_and_manual_observation_takes_precedence():
    from cycling_test.analysis import analyze
    from cycling_test.erg import parse_erg
    from cycling_test.observations import enrich
    from synthetic import samples

    rows = samples()
    rows[840]['lactate_mmol_l'] = 1
    rows[1080]['lactate_mmol_l'] = 3
    rows[1320]['lactate_mmol_l'] = 5
    settings = Settings(
        end_s=1440, weight_kg=50, lactate_levels=[4], lactate=[{'at_s': 1080, 'mmol_l': 3.5}]
    ).model_dump()
    a = enrich(analyze(rows, parse_erg(ERG), settings), rows, settings)
    points = a['lactate_analysis']['points']
    assert len(points) == 3
    assert next(p for p in points if p['at_s'] == 1080)['mmol_l'] == 3.5
    assert a['lactate_4_hr_bpm'] is not None
