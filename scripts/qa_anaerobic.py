"""Synthetic UI archive and report artifacts for local inspection only."""

import json
from pathlib import Path
from cycling_test.store import Store
from cycling_test.anaerobic import Protocol, Settings, analyze, historical_plan
from cycling_test.csv_import import plan_import
from cycling_test.fit import decode_fit
from cycling_test.reports import report
from cycling_test.archive_report import build, render

root = Path(__file__).resolve().parents[1]
store = Store(root / '.local/qa-07')
if store.list('test'):
    raise SystemExit('QA già presente: usare l’archivio esistente.')
org = store.save('organization', {'name': 'Società dimostrativa - dati sintetici'})
store.save_batch(
    plan_import(store, org['id'], 'atleti', (root / 'examples/synthetic/atleti_anaerobico.csv').read_bytes())['entries']
)
store.save_batch(
    historical_plan(store, org['id'], (root / 'examples/synthetic/test_anaerobico.csv').read_bytes())['entries']
)
athlete = store.list('athlete')[0]
for family, duration in [('sprint', 6), ('wingate30', 30), ('wingate15', 15)]:
    spec = Protocol(
        organization_id=org['id'],
        name=family,
        family=family,
        duration_s=duration,
        device='Simulazione',
        start='flying',
        torque_nm_kg=0.70 if family == 'wingate15' else None,
    ).model_dump()
    protocol = store.save(
        'protocol',
        {
            'organization_id': org['id'],
            'name': family,
            'family': family,
            'test_type': family,
            'version': 'simulato-1',
            'status': 'active',
            'anaerobic_spec': spec,
            'definition': {'points': [], 'segments': [], 'duration_s': duration},
            'objects': [],
        },
    )
    raw = (root / f'examples/synthetic/SIM-ANA-{family}.fit').read_bytes()
    original_hash = store.object(raw)
    trace = decode_fit(raw, session_index=0)
    trace['original_hash'] = original_hash
    trace_hash = store.object(json.dumps(trace).encode())
    settings = Settings(offset_s=60, weight_kg=60, weight_source='misurato').model_dump()
    test = store.save(
        'test',
        {
            'organization_id': org['id'],
            'athlete_id': athlete['id'],
            'athlete_snapshot': athlete,
            'date': '2026-07-01',
            'protocol_id': protocol['id'],
            'test_type': family,
            'historical': False,
            'entry_source': 'trace',
            'trace_hash': trace_hash,
            'settings': settings,
            'samples': trace['samples'],
            'analysis': analyze(trace['samples'], spec, settings),
            'objects': [original_hash, trace_hash],
            'notes': 'SIMULAZIONE - nessun atleta reale.',
        },
    )
output = root / 'output/pdf'
output.mkdir(parents=True, exist_ok=True)
(output / 'fuorigiri-wingate15-esempio.pdf').write_bytes(report(test, athlete, protocol, 'pdf'))
(output / 'fuorigiri-archivio-anaerobico-esempio.pdf').write_bytes(render(build(store, org['id']), 'pdf'))
print('Archivio QA e due report sintetici creati.')
