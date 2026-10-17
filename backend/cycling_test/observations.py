"""Explicit inputs and derived values, shared by preview and immutable revisions."""
from .zones import preset, calculate


def enrich(analysis, samples, settings):
    a = dict(analysis)
    coefficient = settings.get('threshold_coefficient')
    supplied = settings.get('threshold_w')
    if supplied is not None:
        a['threshold_w'] = supplied
        a['threshold_source'] = settings.get('threshold_source') or 'dichiarato'
    elif coefficient is not None and a.get('map_w') is not None:
        a['threshold_w'] = round(a['map_w']*coefficient, 2)
        a['threshold_source'] = 'stimata_da_map'
    else:
        a['threshold_w'], a['threshold_source'] = None, None
    a['ftp_w'] = settings.get('ftp_w')
    a['fthr_bpm'] = settings.get('fthr_bpm')
    for metric in ('threshold', 'ftp'):
        a[metric+'_wkg'] = round(a[metric+'_w']/settings['weight_kg'], 3) if a[metric+'_w'] is not None and settings.get('weight_kg') else None
    a['weight_source'] = settings.get('weight_source', 'dichiarato')
    recovery = {r['after_s']: {**r, 'source': 'sensore'} for r in a['recovery']}
    for r in settings.get('recovery_manual', []):
        previous = recovery.get(r['after_s'])
        recovery[r['after_s']] = {**r, 'hrr_bpm': None, 'source': 'manuale', 'sensor': previous}
    a['recovery'] = sorted(recovery.values(), key=lambda r: r['after_s'])
    references = {**a, **{k:v for k,v in settings.items() if v is not None}}
    references['threshold_w'] = a['threshold_w']
    schemes = settings.get('zone_schemes')
    if schemes is None:
        schemes = [preset('hr'), preset('power')]
    a['zones'] = [calculate(s, references.get(s['reference']), samples, settings.get('offset_s', 0), settings['end_s']) for s in schemes]
    return a
