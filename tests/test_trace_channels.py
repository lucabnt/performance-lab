import json
import struct

import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.csv_import import decode_trace_csv
from cycling_test.fit import decode_fit
from cycling_test.store import Store
from synthetic import crc


def test_csv_optional_channels_and_missing_values():
    raw = b'tempo_s,potenza_w,fc_bpm,cadenza_rpm,lattato_mmol_l,velocita_kmh,temperatura_c,quota_m\n0,0,90,0,,0,-2,-10\n1,150,100,80,2.1,25,,100\n'
    rows = decode_trace_csv(raw)['samples']
    assert rows[0]['power'] == 0 and rows[0]['lactate_mmol_l'] is None
    assert rows[0]['temperature_c'] == -2 and rows[0]['altitude_m'] == -10
    assert rows[1]['lactate_mmol_l'] == 2.1 and rows[1]['speed_kmh'] == 25
    assert rows[1]['temperature_c'] is None


@pytest.mark.parametrize('value', ['-1', 'nan', 'inf'])
def test_invalid_lactate_rejected(value):
    with pytest.raises(ValueError):
        decode_trace_csv(f't,power,lactate_mmol_l\n0,100,{value}\n1,100,2\n'.encode())


def test_fit_additional_fields_have_explicit_units():
    fields = [253, 4, 0x86, 7, 2, 0x84, 6, 2, 0x84, 13, 1, 1, 2, 2, 0x84]
    body = bytes([0x40, 0, 0]) + struct.pack('<H', 20) + bytes([5] + fields)
    for t in range(2):
        body += bytes([0]) + struct.pack('<IHHbH', 1_100_000_000 + t, 200, 10000, -2, 3000)
    content = struct.pack('<BBHI4s', 12, 0x10, 100, len(body), b'.FIT') + body
    rows = decode_fit(content + struct.pack('<H', crc(content)))['samples']
    assert rows[0]['speed_kmh'] == 36
    assert rows[0]['temperature_c'] == -2
    assert rows[0]['altitude_m'] == 100


def test_detail_rehydrates_immutable_trace_without_changing_record(tmp_path):
    client = TestClient(create_app(tmp_path, token='test'))
    client.headers['X-Fuorigiri-Token'] = 'test'
    store = Store(tmp_path)
    rows = [{'t': 0, 'power': 0, 'hr': 90, 'cadence': 0}, {'t': 1, 'power': 120, 'hr': 100, 'cadence': 85}]
    digest = store.object(json.dumps({'samples': rows}).encode())
    record = store.save('test', {'trace_hash': digest, 'analysis': {}, 'settings': {}})
    state = client.get('/api/v1/state').json()['test'][0]
    assert state['has_trace'] is True and 'samples' not in state
    detail = client.get('/api/v1/tests/' + record['id']).json()
    assert detail['samples'] == rows and detail['revision'] == record['revision']
    assert store.get(record['id']) == record
