"""Build an isolated demo using actual original ERGs and reproducible synthetic FITs."""

import argparse
import json
from cycling_test.store import Store
from cycling_test.erg import parse_erg
from cycling_test.fit import decode_fit
from cycling_test.analysis import analyze
from cycling_test.observations import enrich
from cycling_test.zones import preset
from cycling_test.reports import report
from cycling_test.history import summarize
from cycling_test.history_report import render
from generate_examples import generate, ROOT
from demo_reset import reset_notice


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', default='.local/demo-fuorigiri')
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Conserva la vecchia cartella in .local/demo-backups e rigenera la demo minima (solo destinazioni dirette in .local).',
    )
    args = parser.parse_args()
    if args.reset:
        try:
            reset_notice(args.data)
        except ValueError as exc:
            raise SystemExit(str(exc)) from None
    store = Store(args.data)
    if store.list('organization'):
        raise SystemExit(
            'Archivio non vuoto: nessun dato modificato. Per rigenerarlo chiudere app/server e usare --reset (la vecchia cartella viene conservata). Per i dati completi usare scripts/demo_suite.py.'
        )
    manifest = generate()
    org = store.save('organization', {'name': 'Fuorigiri Demo - dati sintetici'})
    protocols = {}
    groups = {}
    for category, family in [('Allievi', 'AER-RULLO-ALL'), ('Esordienti', 'AER-RULLO-ESO')]:
        parent = store.save('group', {'organization_id': org['id'], 'name': category, 'season': '', 'parent_id': None})
        groups[family] = store.save(
            'group', {'organization_id': org['id'], 'name': category, 'season': '2026', 'parent_id': parent['id']}
        )
        raw = (ROOT / 'examples/protocols' / f'{family}.erg').read_bytes()
        definition = parse_erg(raw.decode('utf-8-sig'))
        for s in definition['segments']:
            s['phase'] = 'warmup' if s['end_s'] <= 600 else 'increment'
        protocols[family] = store.save(
            'protocol',
            {
                'name': family,
                'family': family,
                'version': 'originale-1',
                'definition': definition,
                'objects': [store.object(raw)],
                'parent_id': None,
                'status': 'active',
                'reason': 'ERG originale fornito dall’utente.',
            },
        )
    out = ROOT / 'tmp/qa-fuorigiri'
    out.mkdir(parents=True, exist_ok=True)
    for index, item in enumerate(manifest):
        a = store.save(
            'athlete',
            {
                'organization_id': org['id'],
                'external_id': item['athlete_code'],
                'name': item['athlete_code'],
                'surname': 'Simulazione',
                'birth_year': 2010 if 'ALL' in item['athlete_code'] else 2012,
                'birth_confirmed': False,
                'notes': 'Nessun dato reale',
                'status': 'active',
            },
        )
        group = groups[item['protocol']]
        p = protocols[item['protocol']]
        store.save(
            'membership',
            {'athlete_id': a['id'], 'group_id': group['id'], 'start': '2026-01-01', 'end': None, 'category_year': 1},
        )
        store.save(
            'measurement',
            {
                'athlete_id': a['id'],
                'date': item['date'],
                'weight_kg': item['weight_kg'],
                'height_cm': 160 + index * 2,
                'source': 'dichiarato',
            },
        )
        raw = (ROOT / 'examples/synthetic' / item['file']).read_bytes()
        decoded = decode_fit(raw)
        original = store.object(raw)
        trace = store.object(json.dumps({**decoded, 'original_hash': original}, allow_nan=False).encode())
        settings = {
            'offset_s': 0,
            'end_s': item['effort_end_s'],
            'weight_kg': item['weight_kg'],
            'height_cm': 160 + index * 2,
            'weight_source': 'dichiarato',
            'rest_hr': item['rest_hr'],
            'rest_after_s': 300,
            'rpe': 9,
            'fthr_bpm': 180,
            'threshold_coefficient': 0.8,
            'zone_schemes': [preset('hr'), preset('power')],
        }
        analysis = enrich(analyze(decoded['samples'], p['definition'], settings), decoded['samples'], settings)
        t = store.save(
            'test',
            {
                'organization_id': org['id'],
                'athlete_id': a['id'],
                'athlete_snapshot': a,
                'protocol_id': p['id'],
                'trace_hash': trace,
                'date': item['date'],
                'settings': settings,
                'samples': decoded['samples'],
                'analysis': analysis,
                'objects': [trace, original],
                'group_ids': [group['id']],
                'notes': item['notes'],
            },
        )
        if index == 0:
            (out / 'test.pdf').write_bytes(report(t, a, p, 'pdf'))
    data = summarize(store, org['id'], dimension='category', mode='athlete')
    for g in data['groups']:
        g['protocol_label'] = store.get(g['protocol_id'])['name']
    (out / 'storico.pdf').write_bytes(render(data, 'pdf', metric='map_w', statistic='mean'))
    print('Archivio dimostrativo:', store.root, '- 4 atleti / 4 test FIT simulati. PDF in', out)


if __name__ == '__main__':
    main()
