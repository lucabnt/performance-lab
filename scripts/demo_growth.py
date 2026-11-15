"""Create a NEW synthetic suite plus explicit growth/maturation acceptance cases."""

from datetime import date, timedelta, datetime, timezone
from pathlib import Path
from cycling_test.store import Store, encoded
from cycling_test.workspaces import Workspaces
from cycling_test.maturation import MeasurementPayload, current


def add_growth(destination, manifest):
    destination = Path(destination)
    manager = Workspaces(destination, Store(destination))
    cases = []
    for entry in manifest['organizations']:
        store = manager.get(entry['id'])
        org = store.list('organization')[0]['id']
        for case in ('peak', 'female', 'missing', 'adult'):
            a = store.save(
                'athlete',
                {
                    'organization_id': org,
                    'name': {'peak': 'Andrea', 'female': 'Elisa', 'missing': 'Giulia', 'adult': 'Marco'}[case],
                    'surname': 'Crescita DEMO ' + case,
                    'birth_date': {
                        'peak': '2010-01-01',
                        'female': '2012-01-01',
                        'missing': None,
                        'adult': '2000-01-01',
                    }[case],
                    'birth_year': {'peak': 2010, 'female': 2012, 'missing': 2011, 'adult': 2000}[case],
                    'sex': 'F' if case in ('missing', 'female') else 'M',
                    'status': 'active',
                    'notes': 'SIMULAZIONE — dati interamente sintetici per controllare crescita e limiti.',
                },
            )
            days = range(-720, 721, 180) if case in ('peak', 'female') else (-365, 0, 180)
            for d in days:
                t = d / 365.25
                growing = case in ('peak', 'female')
                h = (
                    160 + 9 * t - 2 * t**3 / 3
                    if case == 'peak'
                    else 150 + 8 * t - 2 * t**3 / 3
                    if case == 'female'
                    else 174 + 0.1 * t
                    if case == 'adult'
                    else 150 + 5 * t
                )
                payload = MeasurementPayload(
                    athlete_id=a['id'],
                    date=date(2024, 1, 1) + timedelta(days=d),
                    height_cm=h,
                    weight_kg=round((52 if case == 'peak' else 43) + 4 * t, 1)
                    if growing
                    else 68
                    if case == 'adult'
                    else 45,
                    sitting_height_cm=h * 0.52 if growing else None,
                    source='misurato' if case != 'missing' else 'dichiarato',
                    lower_limb_cm=h * 0.49 if growing else None,
                    arm_span_cm=h * 1.01 if growing else None,
                    mother_height_cm=165 if growing else None,
                    father_height_cm=179 if growing else None,
                    adult_height_error_cm=4 if growing else None,
                    adult_height_cm=(180 if case == 'peak' else 168) if growing else None,
                    adult_height_method='Previsione esterna sintetica' if growing else '',
                    adult_height_source='SOLO DEMO — non clinico' if growing else '',
                )
                store.save('measurement', {**payload.model_dump(mode='json'), 'organization_id': org})
            result = current(store, a, '2026-01-01')
            body = {
                'organization_id': org,
                'athlete_id': a['id'],
                'analysis_type': 'maturation',
                'format': 'json',
                'analysis': result,
                'reason': 'Oracolo sintetico ' + case,
                'created_at': datetime.now(timezone.utc).isoformat(),
            }
            body['objects'] = [store.object(encoded(body).encode())]
            snapshot = store.save('report', body)
            cases.append(
                {
                    'athlete_id': a['id'],
                    'workspace_id': entry['id'],
                    'case': case,
                    'snapshot': snapshot['id'],
                    'expected': (
                        'PHV esplorativo circa '
                        + ('8.96' if case == 'peak' else '7.96')
                        + ' cm/anno, 2024-01-01; %PAH da fonte esterna'
                    )
                    if growing
                    else 'Modelli indisponibili; motivi espliciti'
                    if case == 'missing'
                    else 'Modelli adolescenti fuori dominio; HV quasi nulla',
                }
            )
        entry['athletes'] = len(store.list('athlete'))
        entry['measurements'] = len(store.list('measurement'))
    manifest['growth_cases'] = cases
    return cases
