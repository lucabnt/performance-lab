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
        a['threshold_w'] = a['map_w']*coefficient
        a['threshold_source'] = 'stimata_da_map'
    else:
        a['threshold_w'], a['threshold_source'] = None, None
    a['ftp_w'] = settings.get('ftp_w')
    a['fthr_bpm'] = settings.get('fthr_bpm')
    for metric in ('threshold', 'ftp'):
        a[metric+'_wkg'] = a[metric+'_w']/settings['weight_kg'] if a[metric+'_w'] is not None and settings.get('weight_kg') else None
    a['weight_source'] = settings.get('weight_source', 'dichiarato')
    recovery = {r['after_s']: {**r, 'source': 'sensore'} for r in a['recovery']}
    for r in settings.get('recovery_manual', []):
        previous = recovery.get(r['after_s'])
        reference=a.get('recovery_reference_hr_bpm')
        recovery[r['after_s']] = {**r, 'hrr_bpm': reference-r['hr_bpm'] if reference is not None else None, 'source': 'manuale', 'sensor': previous}
    a['recovery'] = sorted(recovery.values(), key=lambda r: r['after_s'])
    references = {**a, **{k:v for k,v in settings.items() if v is not None}}
    references['threshold_w'] = a['threshold_w']
    schemes = settings.get('zone_schemes')
    if schemes is None:
        schemes = [preset('hr'), preset('power')]
    parameters=a.get('preset',{}).get('parameters',{})
    start=settings.get('offset_s',0)
    if parameters.get('summary_phase')=='incremental_only':start=next((r['aligned_start_s'] for r in a['steps'] if r['phase']=='increment'),settings['end_s'])
    a['zones'] = [calculate(s, references.get(s['reference']), samples, start, settings['end_s'],parameters.get('max_gap_s',5),settings.get('excluded_intervals',[])) for s in schemes]
    if a.get('preset'):
        from .specialist import lactate
        from .lactate_levels import metric_key
        observations=list(settings.get('lactate',[]))
        times={r['at_s'] for r in observations}
        observations += [{'at_s':r['t'],'mmol_l':r['lactate_mmol_l'],'origin':'csv'} for r in samples if r.get('lactate_mmol_l') is not None and r['lactate_mmol_l']>0 and r['t'] not in times]
        a['lactate_analysis']=lactate(a,observations,settings.get('lactate_levels'),settings.get('weight_kg'),settings.get('weight_source'))
        a['vo2peak_l_min']=a.get('gas',{}).get('vo2peak',{}).get('value')
        a['vo2peak_ml_kg_min']=a.get('gas',{}).get('vo2peak',{}).get('ml_kg_min')
        a['metric_details']=dict(a.get('metric_details',{}))
        # Preserve stable legacy keys when a user removes 2 or 4 from the list.
        for level in (2,4):a[metric_key(level,'w')]=None
        for result in a['lactate_analysis']['results'].values():
            if 'concentration_mmol_l' not in result:continue
            level=result['concentration_mmol_l']
            for channel,value,unit,reason in [('w',result['value'],'W',result['reason']),('wkg',result['wkg'],'W/kg',result['weight_reason']),('hr_bpm',result['hr_bpm'],'bpm',result['hr_reason'])]:
                key=metric_key(level,channel);a[key]=value
                a['metric_details'][key]={**result,'value':value,'unit':unit,'reason':reason,'status':'estimated' if value is not None else 'unavailable','source':'lactate_load_curve','coverage':None}
        if a.get('gas'):
            a['metric_details']['vo2peak_l_min']={**a['gas']['vo2peak'],'source':'gas_sensor','coverage':(a['gas']['vo2peak'].get('window') or {}).get('coverage')}
        for k,unit in [('threshold_w','W'),('threshold_wkg','W/kg'),('fthr_bpm','bpm'),('ftp_w','W')]:
            value=a.get(k);source=a.get('threshold_source') if k.startswith('threshold') else 'dichiarato'
            a['metric_details'][k]={'value':value,'unit':unit,'source':source,'status':'unavailable' if value is None else 'estimated' if source=='stimata_da_map' else 'declared',
                'method_id':'threshold.map-coefficient/1' if source=='stimata_da_map' else 'declared/1','coverage':None,
                'calibration':settings.get('threshold_calibration',{})}
        if coefficient is not None and not settings.get('threshold_calibration'):
            a['warnings'].append('Coefficiente esplicito privo di calibrazione documentata: stima da verificare.')
    return a
