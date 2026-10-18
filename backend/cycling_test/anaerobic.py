"""Short all-out tests. Protocol snapshots and provenance precede comparisons."""
import hashlib
import json
import math
from datetime import date
from uuid import uuid5,NAMESPACE_URL
from pydantic import BaseModel,ConfigDict,Field,model_validator
from typing import Literal
from .store import encoded
from .custom_fields import FieldDefinition,protocol_metadata,attach

FAMILIES={'sprint':'Sprint breve','wingate30':'Wingate 30 s','wingate15':'Wingate 15 s'}
CSV_HEADER='test_id,atleta_id,data,protocollo_id,peso_kg,peso_fonte,picco_w,tempo_picco_s,media_w,indice_fatica_ws,end_power_w,rpm_max,rpm_medio,fc_max_test_bpm,lavoro_kj,segnale_fc_interrotto,referto_leggibile,note'
EXTENDED_HEADER=CSV_HEADER+',tipo_test,durata_s,coppia_nm_kg,dispositivo,partenza,posizione,finestra_picco_s,finestra_finale_s,best_1s_w,best_5s_w,fatigue_pct,decline_ws,origine_risultati,metodo_originale'
METRIC_MAP={'picco_w':'peak_w','tempo_picco_s':'time_to_peak_s','media_w':'mean_w','indice_fatica_ws':'declared_fatigue_ws','end_power_w':'end_power_w','rpm_max':'cadence_max_rpm','rpm_medio':'cadence_mean_rpm','fc_max_test_bpm':'fc_max_test_bpm','lavoro_kj':'work_kj'}
LABELS={'peak_w':'Picco dichiarato / finestra protocollo (W)','peak_wkg':'Picco / peso (W/kg)','best_1s_w':'Migliori 1 s (W)','best_5s_w':'Migliori 5 s (W)','time_to_peak_s':'Tempo al picco (s)','mean_w':'Potenza media (W)','mean_wkg':'Potenza media / peso (W/kg)','work_kj':'Lavoro meccanico osservato (kJ)','end_power_w':'Potenza finale (W)','fatigue_pct':'Calo picco-finale (%)','decline_ws':'Pendenza picco-finale (W/s)','declared_fatigue_ws':'Indice di fatica storico, formula non verificata (W/s)','cadence_max_rpm':'Cadenza massima (rpm)','cadence_mean_rpm':'Cadenza media (rpm)'}
METRICS=list(LABELS)

class Model(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)

class Protocol(Model):
    custom_fields: list[FieldDefinition]=Field(default_factory=list,max_length=50)
    custom_values: dict=Field(default_factory=dict,max_length=50)
    organization_id: str
    name: str=Field(min_length=1,max_length=300)
    family: Literal['sprint','wingate30','wingate15']
    version: str=Field(default='1',min_length=1,max_length=100)
    parent_id: str|None=None
    reason: str=Field(default='',max_length=3000)
    duration_s: float=Field(default=6,ge=3,le=30)
    torque_nm_kg: float|None=Field(default=None,gt=0,le=10)
    load_description: str=Field(default='',max_length=1000)
    start: Literal['unknown','stationary','flying']='unknown'
    position: Literal['unknown','seated','standing','mixed']='unknown'
    device: str=Field(default='',max_length=300)
    warmup: str=Field(default='',max_length=3000)
    peak_window_s: float=Field(default=1,ge=.1,le=5)
    end_window_s: float=Field(default=1,ge=.1,le=5)
    max_gap_s: float=Field(default=2,gt=0,le=5)
    coverage_min: float=Field(default=.95,ge=.95,le=1)
    @model_validator(mode='after')
    def duration(self):
        if self.family=='wingate15':self.duration_s=15
        if self.family=='wingate30':self.duration_s=30
        if self.family=='sprint' and self.duration_s>10:raise ValueError('Sprint breve: scegliere una durata tra 3 e 10 secondi.')
        if max(self.peak_window_s,self.end_window_s)>self.duration_s:raise ValueError('Finestra superiore alla durata.')
        return self

class Settings(Model):
    custom_values: dict=Field(default_factory=dict,max_length=50)
    extra_fields: list[FieldDefinition]=Field(default_factory=list,max_length=50)
    offset_s: float=Field(default=0,ge=0,le=86400)
    weight_kg: float|None=Field(default=None,gt=0,le=400)
    weight_source: Literal['misurato','arrotondato','dichiarato','derivato','stimato']='dichiarato'
    conditions: dict[str,str]=Field(default_factory=dict,max_length=30)
    excluded_intervals: list[dict]=Field(default_factory=list,max_length=100)
    @model_validator(mode='after')
    def exclusions(self):
        for e in self.excluded_intervals:
            if set(e)-{'start_s','end_s','reason'} or not e.get('reason') or not isinstance(e.get('start_s'),(int,float)) or not isinstance(e.get('end_s'),(int,float)) or not math.isfinite(e['start_s']) or not math.isfinite(e['end_s']) or not 0<=e['start_s']<e['end_s']:raise ValueError('Esclusione non valida: servono inizio, fine e motivo.')
        return self

class TestInput(Model):
    athlete_id: str
    protocol_id: str
    date: date
    trace_hash: str|None=None
    settings: Settings=Field(default_factory=Settings)
    manual: dict[str,float|None]=Field(default_factory=dict,max_length=20)
    notes: str=Field(default='',max_length=10000)
    revision: str|None=None
    reason: str=Field(default='',max_length=3000)
    @model_validator(mode='after')
    def values(self):
        if set(self.manual)-set(METRICS)-{'fc_max_test_bpm'}:raise ValueError('Metrica manuale non riconosciuta.')
        if any(v is not None and (not math.isfinite(v) or v<0) for v in self.manual.values()):raise ValueError('Valori manuali negativi o non finiti.')
        if not self.trace_hash and not any(v is not None for v in self.manual.values()):raise ValueError('Inserire almeno un risultato oppure un tracciato.')
        if self.trace_hash and self.manual:raise ValueError('I risultati calcolati non possono essere sovrascritti da valori manuali.')
        return self

def is_anaerobic(record):return record.get('test_type') in FAMILIES

def specification(protocol):return protocol['anaerobic_spec']

def signature(test):
    # Conservative whole-method grouping; separate windows, durations, hardware,
    # declared/computed provenance, body position, load and environmental metadata.
    return 'anaerobic:'+hashlib.sha256(encoded({'spec':test['analysis']['protocol_snapshot'],'source':test['analysis']['source'],'schema':test['analysis'].get('custom_fields',[]),'engine':test['analysis']['engine'],'conditions':test.get('settings',{}).get('conditions',{})}).encode()).hexdigest()

def analyze(samples,spec,settings):
    duration=spec['duration_s'];start=settings['offset_s'];end=start+duration
    if len(samples)<2 or any(b['t']<=a['t'] for a,b in zip(samples,samples[1:])):raise ValueError('Servono campioni con tempi strettamente crescenti.')
    pieces=[]
    for a,b in zip(samples,samples[1:]):
        lo=max(start,a['t']);hi=min(end,b['t'])
        if hi<=lo or b['t']-a['t']>spec['max_gap_s'] or a.get('paused'):continue
        intervals=[(lo,hi)]
        for e in settings.get('excluded_intervals',[]):
            intervals=[p for x,y in intervals for p in ((x,min(y,e['start_s'])),(max(x,e['end_s']),y)) if p[1]>p[0]]
        for lo,hi in intervals:pieces.append((lo,hi,a))
    def integral(lo,hi,channel):
        total=coverage=0.
        for x,y,r in pieces:
            value=r.get(channel);dt=max(0,min(y,hi)-max(x,lo))
            if isinstance(value,(int,float)) and math.isfinite(value) and value>=0:total+=dt*value;coverage+=dt
        return total,coverage
    total,covered=integral(start,end,'power');coverage=covered/duration
    full=coverage>=1-1e-9
    boundaries={start,end}|{x for x,y,r in pieces}|{y for x,y,r in pieces}
    def best(window):
        if window>duration:return None,None
        candidates=boundaries|{x-window for x in boundaries}
        results=[]
        for x in candidates:
            if start<=x<=end-window:
                energy,observed=integral(x,x+window,'power')
                if observed>=window-1e-9:results.append((energy/window,x-start))
        return max(results,key=lambda p:(p[0],-p[1])) if results else (None,None)
    peak,at=best(spec['peak_window_s']);tail,tail_covered=integral(end-spec['end_window_s'],end,'power')
    tail=tail/spec['end_window_s'] if tail_covered>=spec['end_window_s']-1e-9 else None
    hr=[r.get('hr') for x,y,r in pieces if r.get('hr') is not None]
    cadence=[r.get('cadence') for x,y,r in pieces if r.get('cadence') is not None]
    cad,cad_time=integral(start,end,'cadence')
    a={'peak_w':peak,'time_to_peak_s':at,'best_1s_w':best(1)[0],'best_5s_w':best(5)[0],
       'mean_w':total/duration if full else None,'observed_mean_w':total/covered if covered else None,
       'work_kj':total/1000 if covered else None,'end_power_w':tail,'power_coverage':coverage,
       'complete':coverage>=spec['coverage_min'],'duration_s':duration,'observed_duration_s':covered,
       'cadence_max_rpm':max(cadence) if cadence else None,'cadence_mean_rpm':cad/cad_time if cad_time else None,
       'fc_max_test_bpm':max(hr) if hr else None,
       'fatigue_pct':100*(peak-tail)/peak if peak and tail is not None else None,
       'decline_ws':(peak-tail)/(duration-spec['end_window_s']-at) if peak is not None and tail is not None and duration-spec['end_window_s']-at>0 else None,
       'warnings':[]}
    if not full:a['warnings'].append('Copertura incompleta: media sull’intera prova non calcolata; lavoro limitato agli intervalli osservati. Picco e calo possono sottostimare il valore reale.')
    if any(y-x>spec['peak_window_s']+1e-9 for x,y,r in pieces):a['warnings'].append('Campionamento più lento della finestra del picco: risultato dipendente dal mantenimento del campione, non misura ad alta risoluzione.')
    return finish(a,spec,settings,'computed')

def finish(a,spec,settings,source):
    a={**a,'engine':'anaerobic-1','source':source,'protocol_snapshot':dict(spec),'steps':[],'recovery':[],'zones':[],'method':'Finestre temporali a potenza costante sul campione sinistro; nessuna estrapolazione. Calo picco-finale distinto dall’indice storico.'}
    a.setdefault('warnings',[]);a.setdefault('duration_s',spec['duration_s']);a['offset_s']=settings.get('offset_s',0);a.setdefault('power_coverage',None)
    for k in METRICS:a.setdefault(k,None)
    for key in ('peak','mean'):
        a[key+'_wkg']=a[key+'_w']/settings['weight_kg'] if settings.get('weight_kg') and a.get(key+'_w') is not None else None
    if source!='computed':a['warnings'].append('Valori dichiarati: finestre e formule originali non ricostruibili dal solo riepilogo.')
    if not spec.get('device') or spec.get('start')=='unknown':a['warnings'].append('Comparabilità non verificata: dispositivo o tipo di partenza non documentati.')
    if a.get('peak_w') is not None and a.get('mean_w') is not None and a['mean_w']>a['peak_w']:a['warnings'].append('Potenza media superiore al picco: verificare dati e finestre.')
    if a.get('work_kj') is not None and a.get('mean_w') is not None and abs(1000*a['work_kj']-a['mean_w']*spec['duration_s'])>max(1,.001*a['mean_w']*spec['duration_s']):a['warnings'].append('Lavoro e media non coincidono con la durata nominale: valori originali conservati.')
    a['comparison_key']=signature({'analysis':a,'settings':settings})
    return a

def historical_plan(store,org,raw):
    from .csv_import import read,number
    rows=read(raw);required={'test_id','atleta_id','data','protocollo_id'}
    if rows and required-set(rows[0]):raise ValueError('Colonne obbligatorie: '+', '.join(sorted(required)))
    if len(rows)>100000:raise ValueError('Troppe righe nel lotto.')
    athletes={a.get('external_id',a['id']):a for a in store.list('athlete') if a['organization_id']==org and a.get('status')!='deleted'}
    athletes.update({a['id']:a for a in athletes.copy().values()})
    existing={t['id'] for t in store.list('test')};tests=store.list('test');protocols={p.get('historical_code'):p for p in store.list('protocol') if p.get('organization_id')==org and p.get('historical_code')}
    entries=[];errors=[];skipped=0;digest=hashlib.sha256(raw).hexdigest()
    for i,r in enumerate(rows,2):
        try:
            if not r['test_id'].strip() or not r['protocollo_id'].strip():raise ValueError('ID test e protocollo obbligatori.')
            athlete=athletes[r['atleta_id']];date.fromisoformat(r['data']);code=r['protocollo_id']
            if code!='ANA-15-070' and (r.get('tipo_test') not in FAMILIES or not r.get('durata_s')):raise ValueError('Protocollo non riconosciuto: usare CSV esteso con tipo_test e durata_s espliciti.')
            identity=str(uuid5(NAMESPACE_URL,org+'|anaerobic-test|'+r['test_id']))
            if identity in existing or any(t['athlete_id']==athlete['id'] and r['test_id'] in (t['id'],t.get('external_id')) for t in tests):skipped+=1;continue
            legacy=code=='ANA-15-070'
            family='wingate15' if legacy else r['tipo_test']
            duration=15 if legacy else number(r['durata_s'])
            if family in ('wingate15','wingate30') and duration!=(15 if family=='wingate15' else 30):raise ValueError('Durata e tipo Wingate incoerenti.')
            spec=Protocol(organization_id=org,name='Wingate 15 s · 0,70 N·m/kg' if legacy else code,family=family,duration_s=duration,torque_nm_kg=.70 if legacy else number(r.get('coppia_nm_kg')),device=r.get('dispositivo',''),start=r.get('partenza') or 'unknown',position=r.get('posizione') or 'unknown',load_description='Coppia frenante dichiarata dall’operatore: 0,70 N·m/kg' if legacy else '').model_dump()
            spec['peak_window_s']=number(r.get('finestra_picco_s'));spec['end_window_s']=number(r.get('finestra_finale_s'));spec['fatigue_formula']='unknown'
            if any(v is not None and not 0<v<=duration for v in (spec['peak_window_s'],spec['end_window_s'])):raise ValueError('Finestra temporale non valida.')
            if code not in protocols:
                p={'id':str(uuid5(NAMESPACE_URL,org+'|anaerobic-protocol|'+code)),'organization_id':org,'name':spec['name'],'family':code,'test_type':family,'version':'storico-1','historical':True,'historical_code':code,'status':'archived','anaerobic_spec':spec,'definition':{'points':[],'segments':[],'duration_s':duration},'objects':[]}
                protocols[code]=p;entries.append(('protocol',p))
            elif protocols[code]['anaerobic_spec']!=spec:raise ValueError('Stesso codice protocollo con metadati diversi: distinguere le versioni.')
            weight=number(r.get('peso_kg'))
            if weight is not None and not 0<weight<=400:raise ValueError('Peso fuori intervallo.')
            settings=Settings(weight_kg=weight,weight_source=r.get('peso_fonte') or 'dichiarato').model_dump()
            values={k:number(r.get(c)) for c,k in METRIC_MAP.items()}
            values.update({k:number(r.get(k)) for k in ('best_1s_w','best_5s_w','fatigue_pct','decline_ws')})
            if any(v is not None and v<0 for v in values.values()):raise ValueError('Valore negativo.')
            if values['time_to_peak_s'] is not None and values['time_to_peak_s']>duration:raise ValueError('Tempo al picco oltre la durata.')
            if values.get('fc_max_test_bpm') is not None and not 0<values['fc_max_test_bpm']<=250:raise ValueError('FC fuori intervallo.')
            payload={'id':identity,'external_id':r['test_id'],'import_hash':digest,'organization_id':org,'athlete_id':athlete['id'],'athlete_snapshot':athlete,'protocol_id':protocols[code]['id'],'test_type':family,'date':r['data'],'historical':True,'entry_source':'csv','historical_fields':r,'samples':[],'trace_hash':None,'settings':settings,'analysis':finish(values,protocols[code]['anaerobic_spec'],settings,'legacy-csv'),'notes':r.get('note',''),'objects':[],'group_ids':[]}
            entries.append(('test',payload));existing.add(identity)
        except (ValueError,KeyError,TypeError) as exc:errors.append({'row':i,'error':str(exc)})
    return {'entries':entries,'errors':errors,'skipped':skipped,'rows':len(rows),'hash':digest}

def csv_row(test,protocol):
    row={c:test['analysis'].get(k) for c,k in METRIC_MAP.items()}
    row.update(test.get('historical_fields',{}))
    row.update(test_id=test['id'],atleta_id=test['athlete_id'],data=test['date'],protocollo_id=protocol['family'],peso_kg=test['settings'].get('weight_kg'),peso_fonte=test['settings'].get('weight_source'),note=test.get('notes',''))
    return row

def extended_row(test,protocol):
    row=csv_row(test,protocol);s=test['analysis']['protocol_snapshot']
    row.update(protocollo_id=protocol['id'],tipo_test=test['test_type'],durata_s=s['duration_s'],coppia_nm_kg=s.get('torque_nm_kg'),dispositivo=s.get('device'),partenza=s.get('start'),posizione=s.get('position'),finestra_picco_s=s.get('peak_window_s'),finestra_finale_s=s.get('end_window_s'),origine_risultati=test['analysis']['source'],metodo_originale=test['analysis']['engine'])
    for k in ('best_1s_w','best_5s_w','fatigue_pct','decline_ws'):row[k]=test['analysis'].get(k)
    return row

def install_api(app,store):
    def require(id,kind):
        record=store.get(id)
        if record['kind']!=kind or record.get('status')=='deleted':raise ValueError('Riferimento non valido.')
        return record
    @app.post('/api/v1/anaerobic/protocols')
    def protocol(data:Protocol):
        require(data.organization_id,'organization')
        if data.parent_id:
            p=require(data.parent_id,'protocol')
            if p.get('organization_id')!=data.organization_id or not is_anaerobic(p):raise ValueError('Protocollo padre non valido.')
            if not data.reason.strip():raise ValueError('Motivare la nuova versione.')
        if any(p.get('organization_id')==data.organization_id and p.get('test_type')==data.family and p.get('name')==data.name and p.get('version')==data.version for p in store.list('protocol')):raise ValueError('Nome e versione del protocollo già presenti.')
        metadata=protocol_metadata(data.model_dump())
        return store.save('protocol',{**metadata,'organization_id':data.organization_id,'name':data.name,'family':data.family,'test_type':data.family,'version':data.version,'parent_id':data.parent_id,'reason':data.reason,'status':'active','anaerobic_spec':data.model_dump(),'definition':{'points':[],'segments':[],'duration_s':data.duration_s},'objects':[]})
    def prepare(data,editing=False):
        athlete=require(data.athlete_id,'athlete');p=require(data.protocol_id,'protocol')
        if not is_anaerobic(p) or p.get('historical'):raise ValueError('Selezionare un protocollo anaerobico attivo con metodo esplicito.')
        if p.get('organization_id')!=athlete['organization_id']:raise ValueError('Atleta e protocollo appartengono a società diverse.')
        if not editing and (p.get('status')!='active' or athlete.get('status','active')!='active'):raise ValueError('Atleta o protocollo archiviato.')
        settings=data.settings.model_dump();trace={'samples':[]};objects=[]
        if data.trace_hash:
            trace=json.loads(store.read_object(data.trace_hash));objects=[data.trace_hash]
            if trace.get('original_hash'):objects.append(trace['original_hash'])
            analysis=analyze(trace['samples'],specification(p),settings)
        else:analysis=finish(data.manual,specification(p),settings,'manual')
        analysis=attach(analysis,p,settings)
        return {'organization_id':athlete['organization_id'],'athlete_id':athlete['id'],'athlete_snapshot':athlete,'protocol_id':p['id'],'test_type':p['test_type'],'date':data.date.isoformat(),'historical':not bool(data.trace_hash),'entry_source':'trace' if data.trace_hash else 'manuale','trace_hash':data.trace_hash,'samples':trace['samples'],'settings':settings,'analysis':analysis,'notes':data.notes,'reason':data.reason,'objects':objects,'group_ids':[]}
    @app.post('/api/v1/anaerobic/preview')
    def preview(data:TestInput):return prepare(data,editing=bool(data.revision))['analysis']
    @app.post('/api/v1/anaerobic/tests')
    def save(data:TestInput):return store.save('test',prepare(data))
    @app.put('/api/v1/anaerobic/tests/{id}')
    def revise(id:str,data:TestInput):
        old=require(id,'test')
        if not is_anaerobic(old) or old.get('entry_source')=='csv':raise ValueError('Revisione non disponibile per questo tipo di record.')
        if not data.reason.strip():raise ValueError('Motivare la correzione.')
        if data.athlete_id!=old['athlete_id'] or data.protocol_id!=old['protocol_id']:raise ValueError('Non cambiare atleta o protocollo durante una revisione.')
        return store.save('test',prepare(data,True),id=id,base=data.revision)
    def historical_data(id,data):
        old=require(id,'test')
        if not is_anaerobic(old) or old.get('entry_source')!='csv' or data.trace_hash:raise ValueError('Questa correzione richiede un riepilogo CSV senza tracciato.')
        if data.athlete_id!=old['athlete_id'] or data.protocol_id!=old['protocol_id']:raise ValueError('Non cambiare atleta o protocollo durante la correzione storica.')
        if not data.reason.strip():raise ValueError('Motivare la correzione.')
        settings=data.settings.model_dump();a=finish(data.manual,old['analysis']['protocol_snapshot'],settings,'legacy-csv')
        a=attach(a,require(old['protocol_id'],'protocol'),settings)
        fields={**old['historical_fields'],**{column:a.get(key) for column,key in METRIC_MAP.items()},'data':data.date.isoformat(),'peso_kg':settings.get('weight_kg'),'peso_fonte':settings['weight_source'],'note':data.notes}
        return {**old,'settings':settings,'analysis':a,'date':data.date.isoformat(),'notes':data.notes,'historical_fields':fields,'reason':data.reason}
    @app.post('/api/v1/anaerobic/historical/{id}/preview')
    def preview_historical(id:str,data:TestInput):return historical_data(id,data)['analysis']
    @app.put('/api/v1/anaerobic/historical/{id}')
    def revise_historical(id:str,data:TestInput):return store.save('test',historical_data(id,data),id=id,base=data.revision)
