"""Versioned elapsed-time analysis; missing observations never become zeros."""

import math
from copy import deepcopy
from .methods import DEFAULT, identity, validate

ENGINE_VERSION = '0.5.0'
MAX_GAP_S = 5.0


def valid_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def valid_channel(value, field):
    return valid_number(value) and (value > 0 if field in ('hr', 'vo2', 'vco2', 've') else value >= 0)


def pieces(start, end, excluded):
    spans = [(start, end)] if end > start else []
    for r in excluded:
        a, b = r['start_s'], r['end_s']
        spans = [p for x, y in spans for p in ((x, min(y, a)), (max(x, b), y)) if p[1] > p[0]]
    return spans


def intervals(samples, field, start, end, max_gap=5.0, excluded=()):
    for row, nxt in zip(samples, samples[1:]):
        dt = nxt['t'] - row['t']
        value = row.get(field)
        if not valid_channel(value, field) or not 0 < dt <= max_gap or row.get('paused'):
            continue
        a, b = max(start, row['t']), min(end, nxt['t'])
        for x, y in pieces(a, b, excluded):
            yield value, y - x, x, y


def window(samples, field, start, end, max_gap=5.0, excluded=()):
    total = covered = 0.0
    for value, width, _, _ in intervals(samples, field, start, end, max_gap, excluded):
        total += value * width
        covered += width
    return {
        'mean': total / covered if covered else None,
        'coverage': covered / (end - start) if end > start else 0.0,
        'integral': total,
        'valid_s': covered,
        'requested_s': max(0, end - start),
    }


def analyze(samples, protocol, settings, preset=None):
    preset = deepcopy(preset or DEFAULT)
    validate(preset)
    p = preset['parameters']
    if len(samples) < 2:
        raise ValueError('Servono almeno due campioni temporali.')
    if any(not valid_number(r.get('t')) for r in samples) or any(
        b['t'] <= a['t'] for a, b in zip(samples, samples[1:])
    ):
        raise ValueError('Timestamp duplicati, non validi o non ordinati: correggere il tracciato.')
    offset = settings.get('offset_s', 0)
    end = settings['end_s']
    if offset < samples[0]['t'] or end <= offset or end > samples[-1]['t']:
        raise ValueError('Inizio/fine sforzo fuori dal tracciato.')
    exclusions = settings.get('excluded_intervals', [])
    for r in exclusions:
        if (
            not r.get('reason', '').strip()
            or not valid_number(r.get('start_s'))
            or not valid_number(r.get('end_s'))
            or not samples[0]['t'] <= r['start_s'] < r['end_s'] <= samples[-1]['t']
        ):
            raise ValueError('Esclusione fuori dal tracciato o priva di motivo.')
    w = lambda field, a, b: window(samples, field, a, b, p['max_gap_s'], exclusions)
    markers = {int(r['number']): r['at_s'] for r in settings.get('alignment_markers', [])}
    if len(markers) != len(settings.get('alignment_markers', [])) or any(
        n < 1 or n > len(protocol['segments']) for n in markers
    ):
        raise ValueError('Marker step duplicati o non validi.')
    rows = []
    warnings = []
    shift = offset
    previous_end = offset
    for index, segment in enumerate(protocol['segments']):
        if index + 1 in markers:
            shift = markers[index + 1] - segment['start_s']
        start = shift + segment['start_s']
        planned_end = shift + segment['end_s']
        if start < previous_end:
            raise ValueError('Allineamento: fasi sovrapposte o antecedenti all’inizio.')
        previous_end = planned_end
        if start >= end:
            break
        stop = min(end, planned_end)
        power = w('power', start, stop)
        hr = w('hr', max(start, stop - p['hr_window_s']), stop)
        cadence = w('cadence', start, stop)
        hr['usable'] = hr['coverage'] >= p['hr_coverage']
        hr['observed_mean'] = hr['mean']
        if not hr['usable']:
            hr['mean'] = None
        complete = stop >= planned_end and power['coverage'] >= p['power_coverage']
        target = segment['start_w']
        constant = target == segment['end_w']
        obs = list(intervals(samples, 'power', start, stop, p['max_gap_s'], exclusions))
        if power['valid_s'] and constant:
            error = power['mean'] - target
            tolerance = p['adherence_tolerance_w']
            adherence = {
                'status': 'not_evaluated' if tolerance is None else 'descriptive',
                'mean_error_w': error,
                'mean_error_pct': 100 * error / target if target else None,
                'mae_w': sum(abs(v - target) * dt for v, dt, _, _ in obs) / power['valid_s'],
                'rmse_w': math.sqrt(sum((v - target) ** 2 * dt for v, dt, _, _ in obs) / power['valid_s']),
                'tolerance_w': tolerance,
                'within_band_fraction': sum(
                    dt for v, dt, _, _ in obs if tolerance is not None and abs(v - target) <= tolerance
                )
                / power['valid_s']
                if tolerance is not None
                else None,
            }
        else:
            adherence = {'status': 'unavailable'}
        rows.append(
            {
                **segment,
                'number': index + 1,
                'aligned_start_s': start,
                'aligned_end_s': planned_end,
                'actual_s': stop - start,
                'complete': complete,
                'power': power,
                'hr': hr,
                'cadence': cadence,
                'adherence': adherence,
            }
        )
        if power['coverage'] < p['power_coverage']:
            warnings.append(f'Step {index + 1}: copertura potenza insufficiente.')
    increments = [r for r in rows if r['phase'] == 'increment']
    constant = bool(increments) and all(r['start_w'] == r['end_w'] and r['end_w'] > 0 for r in increments)
    increasing = all(b['end_w'] > a['end_w'] for a, b in zip(increments, increments[1:]))
    first_index = next((i for i, r in enumerate(rows) if r['phase'] == 'increment'), len(rows))
    last_index = max((i for i, r in enumerate(rows) if r['phase'] == 'increment'), default=-1)
    continuous = all(r['phase'] == 'increment' for r in rows[first_index : last_index + 1])
    applicable = constant and increasing and continuous and preset['method_id'] == DEFAULT['method_id']
    completed = []
    for r in increments:
        if not r['complete']:
            break
        completed.append(r)
    map_w = completed[-1]['end_w'] if completed and applicable else None
    alt = None
    if not applicable:
        warnings.append(
            'Protocollo a rampa/discontinuo o carichi non crescenti: metodo ultimo step costante non applicabile.'
        )
    if map_w is not None and len(completed) < len(increments):
        partial = increments[len(completed)]
        duration = partial['end_s'] - partial['start_s']
        if partial['power']['coverage'] >= p['power_coverage'] and 0 < partial['actual_s'] < duration:
            alt = map_w + (partial['end_w'] - map_w) * partial['actual_s'] / duration
    if map_w is None:
        warnings.append('Nessuno step incrementale completo e valido: MAP non disponibile.')
    first_increment = increments[0]['aligned_start_s'] if increments else end
    summary_start = offset if p['summary_phase'] == 'whole_effort' else first_increment
    hrs = [
        r['hr']
        for r in samples
        if summary_start <= r['t'] < end
        and not r.get('paused')
        and valid_channel(r.get('hr'), 'hr')
        and pieces(r['t'], r['t'] + 1e-9, exclusions)
    ]
    reference = w('hr', max(offset, end - p['recovery_reference_s']), end)
    ref = reference['mean'] if reference['coverage'] >= p['hr_coverage'] else None
    recovery = []
    for t in p['recovery_times_s']:
        measured = w('hr', end + t - p['recovery_before_s'], end + t + p['recovery_after_s'])
        value = measured['mean'] if measured['coverage'] >= p['hr_coverage'] else None
        recovery.append(
            {
                'after_s': t,
                'hr_bpm': value,
                'hrr_bpm': ref - value if value is not None and ref is not None else None,
                'coverage': measured['coverage'],
                'reference_coverage': reference['coverage'],
            }
        )
    power = w('power', summary_start, end)
    weight = settings.get('weight_kg')
    if not hrs:
        warnings.append('Canale FC assente durante lo sforzo.')
    if any(r.get('paused') for r in samples if offset <= r['t'] < end):
        warnings.append('Pause timer presenti: tempo trascorso; verificare allineamento e qualità.')
    if exclusions:
        warnings.append('Intervalli esclusi con motivo: copertura calcolata sull’intera durata richiesta.')
    if map_w is not None:
        warnings.append(
            'MAP operativa = target dell’ultimo step completo; verificare separatamente la potenza realmente erogata e l’aderenza.'
        )
    ramp_mean = w('power', max(first_increment, end - 30), end)
    last = increments[-1] if increments else None
    nominal = None
    if last:
        frac = min(1.0, (end - last['aligned_start_s']) / (last['aligned_end_s'] - last['aligned_start_s']))
        nominal = last['start_w'] + (last['end_w'] - last['start_w']) * frac
    result = {
        'engine': ENGINE_VERSION,
        'preset': identity(preset),
        'steps': rows,
        'map_w': map_w,
        'map_alt_w': alt,
        'map_wkg': map_w / weight if map_w is not None and weight else None,
        'fc_max_test_bpm': max(hrs) if hrs else None,
        'duration_s': end - offset,
        'duration_incremental_s': sum(r['actual_s'] for r in increments),
        'summary_phase': p['summary_phase'],
        'power_mean_w': power['mean'],
        'work_kj': power['integral'] / 1000,
        'valid_power_s': power['valid_s'],
        'power_coverage': power['coverage'],
        'recovery': recovery,
        'recovery_reference_hr_bpm': ref,
        'recovery_reference_coverage': reference['coverage'],
        'warnings': warnings,
        'terminal_target_w': nominal if not applicable else None,
        'terminal_mean_w': ramp_mean['mean']
        if not applicable and ramp_mean['coverage'] >= p['power_coverage']
        else None,
        'method': preset['method_id'] + '; completezza per durata/copertura, aderenza separata.',
    }
    units = {
        'map_w': 'W',
        'map_alt_w': 'W',
        'map_wkg': 'W/kg',
        'fc_max_test_bpm': 'bpm',
        'work_kj': 'kJ',
        'power_mean_w': 'W',
        'terminal_target_w': 'W',
        'terminal_mean_w': 'W',
    }
    stage_coverage = completed[-1]['power']['coverage'] if map_w is not None else None
    coverage = {
        'map_w': stage_coverage,
        'map_wkg': stage_coverage,
        'map_alt_w': min(stage_coverage, increments[len(completed)]['power']['coverage']) if alt is not None else None,
        'fc_max_test_bpm': w('hr', summary_start, end)['coverage'],
        'terminal_target_w': None,
        'terminal_mean_w': ramp_mean['coverage'],
    }
    metric_methods = {
        'map_w': DEFAULT['method_id'],
        'map_alt_w': 'incremental.constant.partial-linear/1',
        'map_wkg': 'power.per-mass/1',
        'fc_max_test_bpm': 'hr.valid-sample-max/1',
        'terminal_target_w': 'protocol.terminal-target/1',
    }
    sources = {
        'map_w': 'protocol_target',
        'terminal_target_w': 'protocol_target',
        'map_alt_w': 'model_estimate',
        'map_wkg': 'protocol_target_and_mass',
    }
    result['metric_details'] = {
        k: {
            'value': result[k],
            'unit': unit,
            'source': sources.get(k, 'sensor_derived'),
            'status': 'unavailable' if result[k] is None else 'estimated' if k == 'map_alt_w' else 'computed',
            'reason': None if result[k] is not None else 'insufficient_or_inapplicable',
            'method_id': metric_methods.get(k, 'signal.time-weighted-hold/1'),
            'coverage': coverage.get(k, power['coverage']),
        }
        for k, unit in units.items()
    }
    return result
