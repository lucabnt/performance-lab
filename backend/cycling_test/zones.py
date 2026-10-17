"""Versionable zone schemes. Boundaries classify unrounded ratios exactly once."""
from decimal import Decimal
import math


def preset(channel):
    bounds = [81, 90, 100, 105] if channel == 'hr' else [55, 75, 90, 105]
    return {'name': 'PCRS-SOGLIA-5Z', 'version': '1', 'channel': channel,
            'reference': 'fthr_bpm' if channel == 'hr' else 'threshold_w',
            'zones': [{'name': f'Z{i+1}', 'upper': b, 'inclusive': channel != 'hr' or i == 3}
                      for i, b in enumerate(bounds)] + [{'name': 'Z5', 'upper': None, 'inclusive': False}]}


def validate(scheme):
    if scheme.get('channel') not in ('hr', 'power'):
        raise ValueError('Canale zone non valido.')
    allowed = ('fthr_bpm', 'fc_max_test_bpm', 'fc_max_reference_bpm') if scheme['channel'] == 'hr' else ('threshold_w', 'map_w', 'ftp_w')
    if scheme.get('reference') not in allowed:
        raise ValueError('Riferimento non compatibile con il canale.')
    zones = scheme.get('zones', [])
    if not 2 <= len(zones) <= 100:
        raise ValueError('Definire da 2 a 100 zone.')
    last = 0
    names = set()
    for i, z in enumerate(zones):
        if not isinstance(z.get('name'), str) or not z['name'].strip() or z['name'] in names:
            raise ValueError('Nomi delle zone obbligatori e univoci.')
        names.add(z['name'])
        upper = z.get('upper')
        if i == len(zones)-1:
            if upper is not None:
                raise ValueError('L’ultima zona deve avere limite superiore aperto.')
        elif isinstance(upper,bool) or not isinstance(upper, (float, int)) or not math.isfinite(upper) or upper <= last:
            raise ValueError('Limiti percentuali positivi e strettamente crescenti richiesti.')
        else:
            last = upper
        if not isinstance(z.get('inclusive'), bool):
            raise ValueError('Inclusività del confine obbligatoria.')
    return scheme


def classify(value, reference, scheme):
    if value is None or reference is None or reference <= 0 or not math.isfinite(value) or value < 0:
        return None
    ratio = Decimal(str(value))*100/Decimal(str(reference))
    for i, z in enumerate(scheme['zones']):
        if z['upper'] is None or ratio < Decimal(str(z['upper'])) or (z['inclusive'] and ratio == Decimal(str(z['upper']))):
            return i


def calculate(scheme, reference, samples, start, end):
    validate(scheme)
    if reference is None or reference <= 0:
        return {'scheme': scheme, 'reference_value': None, 'zones': [], 'unclassified_s': end-start}
    rows = []
    lower, lower_inclusive = 0, True
    for z in scheme['zones']:
        upper = None if z['upper'] is None else reference*z['upper']/100
        rows.append({**z, 'lower_value': lower, 'lower_inclusive': lower_inclusive,
                     'upper_value': upper, 'seconds': 0.0})
        lower, lower_inclusive = upper, not z['inclusive']
    field = 'hr' if scheme['channel'] == 'hr' else 'power'
    for row, nxt in zip(samples, samples[1:]):
        width = max(0, min(end, nxt['t'])-max(start, row['t']))
        if width == 0 or row.get('paused') or not 0 < nxt['t']-row['t'] <= 5:
            continue
        i = classify(row.get(field), reference, scheme)
        if i is not None:
            rows[i]['seconds'] += width
    return {'scheme': scheme, 'reference_value': reference, 'zones': rows,
            'unclassified_s': max(0, end-start-sum(z['seconds'] for z in rows))}
