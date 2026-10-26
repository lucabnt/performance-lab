"""Training bounds from saved references; profile choices never rewrite tests."""
from copy import deepcopy
from datetime import datetime,timezone
import math
from .zones import preset,calculate,validate

CHANNELS=('hr','power')
REFERENCE_COLUMNS={'fthr_bpm':'fthr_bpm','fc_max_test_bpm':'fc_max_test_bpm',
    'fc_max_reference_bpm':'fc_max_riferimento_bpm','threshold_w':'soglia_w','map_w':'map_w','ftp_w':'ftp_w'}


def positive(value):
    if isinstance(value,bool):return None
    try:value=float(str(value).replace(',','.'))
    except (TypeError,ValueError):return None
    return value if math.isfinite(value) and value>0 else None


def aerobic(test):
    from .anaerobic import is_anaerobic
    return test.get('status')!='deleted' and test.get('test_type')!='custom' and not is_anaerobic(test)


def references(test):
    historical=test.get('historical_fields') or {}
    values={key:historical.get(column) for key,column in REFERENCE_COLUMNS.items()}
    values.update({k:v for k,v in test.get('settings',{}).items() if k in REFERENCE_COLUMNS})
    values.update({k:v for k,v in test.get('analysis',{}).items() if k in REFERENCE_COLUMNS})
    return {k:positive(v) for k,v in values.items()}


def bounds(scheme,reference):
    result=calculate(deepcopy(scheme),positive(reference),[],0,0)
    for row in result['zones']:
        if any(v is not None and not math.isfinite(v) for v in (row['lower_value'],row['upper_value'])):
            raise ValueError('Limiti delle zone fuori intervallo numerico.')
    return result


def for_test(test):
    """Prefer archived zone snapshots, fill absent channels without changing input."""
    if not aerobic(test):raise ValueError('Le zone aerobiche richiedono un test aerobico disponibile.')
    saved={z['scheme']['channel']:deepcopy(z) for z in test.get('analysis',{}).get('zones',[]) if z.get('scheme',{}).get('channel') in CHANNELS}
    configured={s['channel']:s for s in test.get('settings',{}).get('zone_schemes') or []}
    refs=references(test)
    result=[]
    for channel in CHANNELS:
        if channel in saved:
            value=saved[channel];value['definition_source']='saved_test'
        else:
            scheme=configured.get(channel) or preset(channel)
            value=bounds(scheme,refs.get(scheme['reference']))
            value['definition_source']='saved_references'
        value['test_id']=test.get('id');value['test_revision']=test.get('revision');value['test_date']=test.get('date')
        result.append(value)
    return result


def candidates(store,athlete):
    rows=[t for t in store.list('test') if t.get('athlete_id')==athlete['id'] and t.get('organization_id')==athlete['organization_id'] and aerobic(t)]
    return sorted(rows,key=lambda t:t.get('date',''),reverse=True)


def profile(store,athlete):
    selection=athlete.get('training_zone_selection') or {'mode':'latest'}
    tests=candidates(store,athlete)
    protocols={p['id']:p for p in store.list('protocol')}
    if selection['mode']=='latest':
        definitions=[for_test(t) for t in tests]
        zones=[]
        for channel in CHANNELS:
            available=[z for pair in definitions for z in pair if z['scheme']['channel']==channel]
            zones.append(deepcopy(next((z for z in available if z.get('reference_value') and z['zones']),available[0] if available else bounds(preset(channel),None))))
    else:zones=deepcopy(selection['zones'])
    return {'mode':selection['mode'],'selection':selection,'zones':zones,
        'athlete_revision':athlete['revision'],'available_tests':[{'id':t['id'],'revision':t['revision'],'date':t['date'],
            'protocol_id':t.get('protocol_id'),'protocol_name':protocols.get(t.get('protocol_id'),{}).get('name',''),
            'protocol_version':protocols.get(t.get('protocol_id'),{}).get('version',''),
            'available_channels':[z['scheme']['channel'] for z in for_test(t) if z['zones']]} for t in tests]}


def install(app,store,require):
    from typing import Literal
    from pydantic import Field
    from .api import Model
    class Choice(Model):
        base:str
        mode:Literal['latest','test','custom']
        test_id:str|None=None
        test_revision:str|None=None
        schemes:list[dict]=Field(default_factory=list,max_length=2)
        references:dict[str,float]=Field(default_factory=dict)

    @app.get('/api/v1/tests/{id}/zones')
    def test_zones(id:str):
        test=require(id,'test')
        return {'zones':for_test(test),'test_id':id,'test_revision':test['revision']}

    @app.get('/api/v1/athletes/{id}/training-zones')
    def athlete_zones(id:str):return profile(store,require(id,'athlete'))

    @app.put('/api/v1/athletes/{id}/training-zones')
    def select_zones(id:str,data:Choice):
        athlete=require(id,'athlete')
        choice={'mode':data.mode,'version':'training-zones/1','updated_at':datetime.now(timezone.utc).isoformat()}
        if data.mode=='test':
            from .store import ConflictError
            test=require(data.test_id or '','test')
            if test.get('athlete_id')!=id or test.get('organization_id')!=athlete['organization_id']:
                raise ValueError('Il test deve appartenere allo stesso atleta e alla stessa società.')
            if test['revision']!=data.test_revision:raise ConflictError('Il test è cambiato: ricaricare prima di adottarne le zone.')
            choice.update(test_id=test['id'],test_revision=test['revision'],test_date=test['date'],zones=for_test(test))
        elif data.mode=='custom':
            from uuid import uuid4
            if len(data.schemes)!=2 or {s.get('channel') for s in data.schemes}!={'hr','power'}:
                raise ValueError('Definire uno schema FC e uno schema potenza.')
            for key,value in data.references.items():
                if key not in REFERENCE_COLUMNS or positive(value) is None or value>(250 if key.startswith(('fc_','fthr')) else 3000):
                    raise ValueError('Riferimenti delle zone personalizzate non validi.')
            zones=[];schemes=[];version='custom-'+uuid4().hex[:12]
            for original in data.schemes:
                scheme={**deepcopy(original),'version':version,'source':'profile_custom'}
                if not isinstance(scheme.get('name'),str) or not scheme['name'].strip():raise ValueError('Indicare il nome di entrambi gli schemi.')
                validate(scheme)
                if scheme['reference'] not in data.references:raise ValueError('Indicare il valore del riferimento per entrambi gli schemi.')
                zones.append(bounds(scheme,data.references[scheme['reference']]))
                schemes.append(scheme)
            choice.update(zones=zones,schemes=schemes,references=data.references)
        saved=store.save('athlete',{**athlete,'training_zone_selection':choice},id,data.base)
        return profile(store,saved)
