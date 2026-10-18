"""Immutable built-in and archived analysis presets, independent of protocol loads."""
from copy import deepcopy
from hashlib import sha256
from .store import encoded

DEFAULT = {
    'id':'incremental-constant-v1', 'name':'Incrementale - step costanti', 'version':'1',
    'kind':'analysis_preset', 'schema':1, 'method_id':'incremental.constant.last-complete/1',
    'parameters':{'max_gap_s':5.,'power_coverage':.95,'hr_coverage':.8,'hr_window_s':30.,
                  'recovery_reference_s':5.,'recovery_before_s':2.,'recovery_after_s':3.,
                  'recovery_times_s':[60,90,120], 'adherence_tolerance_w':None,
                  'summary_phase':'whole_effort','vo2_window_s':30.,'gas_coverage':.95},
    'references':['https://www.thoracic.org/statements/resources/pfet/cardioexercise.pdf'],
}
RAMP = {**deepcopy(DEFAULT),'id':'incremental-descriptive-v1','name':'Rampa / discontinuo - descrittivo',
        'method_id':'incremental.ramp-discontinuous.descriptive/1'}


def catalog():
    return [deepcopy(DEFAULT),deepcopy(RAMP)]


def validate(preset):
    import math
    if preset.get('method_id') not in (DEFAULT['method_id'],RAMP['method_id']):
        raise ValueError('Metodo non supportato.')
    p=preset.get('parameters',{})
    if set(p)!=set(DEFAULT['parameters']):raise ValueError('Parametri del preset incompleti o sconosciuti.')
    for k in ('max_gap_s','hr_window_s','recovery_reference_s','recovery_after_s','vo2_window_s'):
        if isinstance(p[k],bool) or not isinstance(p[k],(float,int)) or not math.isfinite(p[k]) or not 0<p[k]<=600:
            raise ValueError('Finestra non valida: '+k)
    for k in ('power_coverage','hr_coverage','gas_coverage'):
        if isinstance(p[k],bool) or not isinstance(p[k],(float,int)) or not math.isfinite(p[k]) or not 0<p[k]<=1:raise ValueError('Copertura non valida.')
    for k in ('recovery_before_s','adherence_tolerance_w'):
        if k=='adherence_tolerance_w' and p[k] is None:continue
        if isinstance(p[k],bool) or not isinstance(p[k],(float,int)) or not math.isfinite(p[k]) or not 0<=p[k]<=600:raise ValueError('Tolleranza/finestra non valida.')
    if p['summary_phase'] not in ('whole_effort','incremental_only'):raise ValueError('Fase non valida.')
    times=p['recovery_times_s']
    if not isinstance(times,list) or not times or len(times)>100 or any(isinstance(t,bool) or not isinstance(t,(int,float)) or not math.isfinite(t) or t<p['recovery_before_s'] or t>86400 for t in times) or len(set(times))!=len(times):raise ValueError('Tempi recupero non validi.')
    return preset


def resolve(store,identifier=None):
    identifier=identifier or DEFAULT['id']
    preset=next((p for p in catalog() if p['id']==identifier),None)
    if preset is None:
        preset=store.get(identifier)
        if preset['kind']!='analysis_preset':raise ValueError('Riferimento preset non valido.')
    validate(preset)
    return preset


def identity(preset):
    body={k:v for k,v in preset.items() if k not in ('revision','hash')}
    return {**deepcopy(body),'hash':sha256(encoded(body).encode()).hexdigest()}


def comparison_key(test):
    from .anaerobic import is_anaerobic,signature
    if is_anaerobic(test):return signature(test)
    a=test.get('analysis',{})
    p=a.get('preset')
    return (p['hash']+'|engine='+a.get('engine','unknown') if p else 'legacy_unknown:'+a.get('engine','unknown'))+'|'+encoded(test.get('settings',{}).get('conditions',{}))
