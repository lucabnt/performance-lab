"""VO2 source selection, coverage, provenance and immutable API revisions."""

from copy import deepcopy
import io
import zipfile
import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app, Settings
from cycling_test.csv_import import decode_trace_csv
from cycling_test.specialist import attach_gas, decode_gas
from cycling_test.analysis import analyze
from cycling_test.observations import enrich
from cycling_test.methods import comparison_key
from test_incremental_v1 import protocol, samples
from synthetic import ERG, fit_bytes


def evaluate(rows, settings):
    a = analyze(rows, protocol(), settings)
    attach_gas(a, rows, settings)
    return enrich(a, rows, settings)


def test_combined_csv_vo2_and_lactate():
    raw = (
        't,power,hr,vo2_l_min,lactate_mmol_l\n'
        + '\n'.join(f'{i},200,150,3,{2 if i == 100 else ""}' for i in range(481))
    ).encode()
    rows = decode_trace_csv(raw)['samples']
    a = evaluate(rows, {'end_s': 480, 'weight_kg': 50})
    assert a['vo2peak_l_min'] == 3
    assert a['vo2peak_ml_kg_min'] == 60
    assert a['gas']['source'] == 'trace_csv'
    assert a['gas']['vo2max']['value'] is None
    assert a['lactate_analysis']['points']
    assert a['metric_details']['vo2peak_ml_kg_min']['unit'] == 'mL/kg/min'
    assert a['metric_details']['vo2peak_ml_kg_min']['value'] == 60


@pytest.mark.parametrize('value', ['-1', '0', 'nan', 'inf'])
def test_invalid_vo2_csv(value):
    raw = f't,vo2_l_min\n0,{value}\n1,3'.encode()
    with pytest.raises(ValueError):
        decode_trace_csv(raw)
    with pytest.raises(ValueError):
        decode_gas(raw)


def test_manual_coverage_and_source_separation():
    settings = {'end_s': 480, 'vo2': [{'at_s': i, 'vo2_l_min': 3} for i in range(481)]}
    a = evaluate(samples(), settings)
    assert a['vo2peak_l_min'] == 3 and a['vo2peak_ml_kg_min'] is None
    assert a['gas']['source'] == 'manual_observations'
    sparse = {**settings, 'vo2': [{'at_s': 0, 'vo2_l_min': 3}, {'at_s': 60, 'vo2_l_min': 5}]}
    assert evaluate(samples(), sparse)['vo2peak_l_min'] is None
    excluded = {**settings, 'excluded_intervals': [{'start_s': 0, 'end_s': 479, 'reason': 'Artefatti'}]}
    assert evaluate(samples(), excluded)['vo2peak_l_min'] is None
    with pytest.raises(ValueError):
        evaluate([{**r, 'vo2_l_min': 4} for r in samples()], settings)
    with pytest.raises(ValueError):
        Settings(**{**settings, 'gas_hash': 'a'})
    with pytest.raises(ValueError):
        Settings(**{**settings, 'vo2': list(reversed(settings['vo2']))})
    sensor = evaluate([{**r, 'vo2_l_min': 3} for r in samples()], {'end_s': 480})
    assert comparison_key({'analysis': a}) != comparison_key({'analysis': sensor})


def test_manual_vo2_api_revision_and_reports(tmp_path):
    c = TestClient(create_app(tmp_path, token='qa'))
    c.headers['X-Fuorigiri-Token'] = 'qa'

    def post(path, body):
        r = c.post('/api/v1/' + path, json=body)
        assert r.status_code == 200, r.text
        return r.json()

    org = post('organizations', {'name': 'VO2 QA sintetica'})
    athlete = post('athletes', {'organization_id': org['id'], 'name': 'Atleta', 'surname': 'Sintetico'})
    p = c.post(
        '/api/v1/protocols', data={'name': 'VO2 QA', 'family': 'QA', 'version': '1'}, files={'file': ('p.erg', ERG)}
    ).json()
    trace = c.post('/api/v1/traces', files={'file': ('t.fit', fit_bytes())}).json()
    payload = {
        'athlete_id': athlete['id'],
        'protocol_id': p['id'],
        'trace_hash': trace['hash'],
        'date': '2026-10-31',
        'settings': {
            'end_s': 1440,
            'weight_kg': 50,
            'vo2': [{'at_s': i, 'vo2_l_min': 3, 'note': 'Analizzatore QA'} for i in range(1441)],
        },
    }
    original = post('tests', payload)
    assert original['analysis']['vo2peak_ml_kg_min'] == 60
    changed = deepcopy(payload)
    changed['settings']['vo2'][0]['note'] = 'Nota corretta'
    r = c.put(
        '/api/v1/tests/' + original['id'], json={'base': original['revision'], 'reason': 'Nota fonte', 'test': changed}
    )
    assert r.status_code == 200, r.text
    revisions = c.get('/api/v1/records/' + original['id'] + '/revisions').json()
    assert any(t['settings']['vo2'][0]['note'] == 'Analizzatore QA' for t in revisions)
    report = c.get('/api/v1/tests/' + original['id'] + '/report/md')
    assert report.status_code == 200
    with zipfile.ZipFile(io.BytesIO(report.content)) as z:
        text = z.read('report.md').decode()
        assert 'VO2peak' in text and 'Misure manuali temporizzate' in text
    history = c.get('/api/v1/history/' + org['id'] + '?metric=vo2peak_ml_kg_min').json()
    assert history['coverage']['vo2peak_ml_kg_min']['valid'] == 1

    export = c.get('/api/v1/export/' + org['id'])
    with zipfile.ZipFile(io.BytesIO(export.content)) as z:
        csv_text = z.read('extended/vo2.csv').decode()
        assert 'manual_observations' in csv_text and 'gas.vo2peak-time-mean/1' in csv_text
        assert 'Analizzatore QA' in z.read('extended/vo2_osservazioni.csv').decode()
