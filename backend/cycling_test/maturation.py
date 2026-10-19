"""Explicit, versioned growth observations and exploratory maturity estimates.

See docs/MATURAZIONE.md for equations, primary references and product gates.
No estimation of missing measurements or irreversible athlete classifications.
"""
from datetime import date, timedelta, datetime, timezone
import hashlib
import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Literal
from .store import encoded, ConflictError

VERSION = 'growth-maturity/1'
POLICY = {'hv_min_days':90, 'hv_max_days':400, 'hv_max_cm_year':20,
          'phv_min_measures':7, 'phv_min_span_days':730, 'phv_support_days':180,
          'phv_local_points':5, 'height_precision_default_cm':0.1,
          'moore_age_M':[10,16], 'moore_age_F':[9,14],
          'mirwald_age_M':[12,16], 'mirwald_age_F':[9,14]}
REFERENCE = 'https://doi.org/10.1007/s40279-017-0750-y'
LABELS = {'hv':'Velocità di crescita · cm/anno','phv':'PHV longitudinale esplorativo · cm/anno',
          'aphv':'APHV longitudinale esplorativa · anni','offset':'Maturity offset stimato · anni',
          'aphv_estimated':'APHV stimata · anni','pah':'Statura adulta prevista raggiunta · %',
          'residual':'Statura residua da previsione dichiarata · cm'}
WARNINGS = ['Convenzioni di qualità del prodotto, non criteri diagnostici.',
            'Le stime antropometriche possono essere inaccurate nel singolo atleta; non sono PHV osservato.',
            'La %PAH dipende da una previsione adulta esterna dichiarata. Nessun coefficiente Khamis–Roche non verificato è incorporato.']


class MeasurementPayload(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    athlete_id:str
    date:date
    weight_kg:float|None=Field(default=None,gt=0,le=400)
    height_cm:float|None=Field(default=None,gt=0,le=260)
    source:Literal['misurato','arrotondato','dichiarato']='misurato'
    quality:Literal['valid','uncertain','excluded']='valid'
    precision_cm:float=Field(default=.1,gt=0,le=5)
    model_sex:Literal['','M','F']=''
    sitting_height_cm:float|None=Field(default=None,gt=0,le=160)
    arm_span_cm:float|None=Field(default=None,gt=0,le=300)
    lower_limb_cm:float|None=Field(default=None,gt=0,le=180)
    mother_height_cm:float|None=Field(default=None,gt=0,le=260)
    father_height_cm:float|None=Field(default=None,gt=0,le=260)
    adult_height_cm:float|None=Field(default=None,gt=0,le=260)
    adult_height_method:str=Field(default='',max_length=300)
    adult_height_source:str=Field(default='',max_length=500)
    adult_height_error_cm:float|None=Field(default=None,gt=0,le=30)
    notes:str=Field(default='',max_length=4000)

    @model_validator(mode='after')
    def consistent(self):
        if not any(getattr(self,k) is not None for k in ('height_cm','weight_kg','sitting_height_cm','arm_span_cm','lower_limb_cm','mother_height_cm','father_height_cm','adult_height_cm')):
            raise ValueError('Inserire almeno una misura.')
        if self.sitting_height_cm and self.height_cm and self.sitting_height_cm>=self.height_cm:
            raise ValueError('La statura seduta deve essere inferiore alla statura.')
        if self.lower_limb_cm and self.height_cm and self.lower_limb_cm>=self.height_cm:
            raise ValueError('La lunghezza degli arti deve essere inferiore alla statura.')
        if self.adult_height_cm and (not self.adult_height_method.strip() or not self.adult_height_source.strip()):
            raise ValueError('La previsione di statura adulta richiede metodo e fonte esterni espliciti.')
        return self


def age_at(birth,on):
    if not birth:return None
    days=(date.fromisoformat(on)-date.fromisoformat(birth)).days
    return days/365.25 if days>=0 else None


def unavailable(reason,method):return {'value':None,'reason':reason,'method_id':method}


def anthropometric(athlete,m):
    age=age_at(athlete.get('birth_date'),m['date']);sex=m.get('model_sex') or athlete.get('sex','')
    h=m.get('height_cm');sh=m.get('sitting_height_cm');w=m.get('weight_kg')
    result={'date':m['date'],'measurement_id':m['id'],'revision':m['revision'],'age_years':age,'model_sex':sex,
            'height_cm':h,'source':m.get('source'), 'models':{},'optional':{}}
    good=m.get('source')=='misurato' and m.get('quality','valid')=='valid'
    for model in ('moore','mirwald'):
        method=model+('-standing/2015-1' if model=='moore' else '/2002-1')
        reason=None
        if not good:reason='Misura non misurata o qualità non confermata.'
        elif age is None:reason='Serve la data di nascita completa e non futura rispetto alla misura.'
        elif sex not in ('M','F'):reason='Parametro M/F per l’equazione non disponibile; non viene inferito.'
        elif not POLICY[model+'_age_'+sex][0]<=age<=POLICY[model+'_age_'+sex][1]:reason='Età fuori dal dominio prudenziale del preset.'
        elif h is None:reason='Statura mancante.'
        elif model=='mirwald' and (sh is None or w is None):reason='Servono statura seduta e massa nella stessa rilevazione.'
        if reason:result['models'][model]=unavailable(reason,method);continue
        if model=='moore':
            offset=(-7.999994+.0036124*age*h) if sex=='M' else (-7.709133+.0042232*age*h)
            see=.542 if sex=='M' else .528
        else:
            leg=h-sh
            if leg<=0:result['models'][model]=unavailable('Statura seduta incoerente.',method);continue
            offset=(-9.236+.0002708*leg*sh-.001663*age*leg+.007216*age*sh+.02292*w/h*100) if sex=='M' else (-9.376+.0001882*leg*sh+.0022*age*leg+.005841*age*sh-.002658*age*w+.07693*w/h*100)
            see=.592 if sex=='M' else .569
        result['models'][model]={'value':offset,'aphv_years':age-offset,'method_id':method,'reason':None,
                                 'reference':REFERENCE,'development_see_years':see,
                                 'uncertainty':'SEE della popolazione di sviluppo; non intervallo di confidenza individuale.'}
    adult=m.get('adult_height_cm')
    if good and adult and h and adult>=h:
        result['optional'].update(pah={'value':100*h/adult,'method_id':'pah-external/1','source':m.get('adult_height_source'),'prediction_method':m.get('adult_height_method'),'adult_height_cm':adult,'prediction_error_cm':m.get('adult_height_error_cm')},
                                  residual={'value':adult-h,'method_id':'residual-external/1'})
    else:
        reason='Misura non misurata o qualità non confermata.' if not good else 'Serve una previsione adulta esterna con metodo e fonte.' if not adult else 'Previsione adulta inferiore alla statura rilevata o statura mancante.'
        result['optional'].update(pah=unavailable(reason,'pah-external/1'),residual=unavailable(reason,'residual-external/1'))
    for key,num in (('sitting_height_pct',sh),('arm_span_pct',m.get('arm_span_cm')),('lower_limb_pct',m.get('lower_limb_cm'))):
        result['optional'][key]={'value':100*num/h if good and num and h else None,'method_id':'body-ratios/1','reason':None if good and num and h else 'Misura non misurata o qualità non confermata.' if not good else 'Misure specifiche mancanti.'}
    return result


def height_velocity(measures):
    heights=sorted((m for m in measures if m.get('height_cm') is not None),key=lambda m:(m['date'],m['id']))
    rows=[]
    for a,b in zip(heights,heights[1:]):
        days=(date.fromisoformat(b['date'])-date.fromisoformat(a['date'])).days
        delta=b['height_cm']-a['height_cm'];reason=None
        if any(m.get('source')!='misurato' or m.get('quality','valid')!='valid' for m in (a,b)):reason='Usare due misure confermate come misurate e valide.'
        elif days<POLICY['hv_min_days']:reason='Intervallo inferiore a 90 giorni o stessa data; annualizzazione non utilizzabile.'
        elif days>POLICY['hv_max_days']:reason='Intervallo superiore a 400 giorni; serie troppo rada.'
        elif delta<0:reason='Statura diminuita: verificare le misure.'
        elif delta*365.25/days>POLICY['hv_max_cm_year']:reason='Velocità oltre il controllo prudenziale del preset: verificare le misure.'
        precision=sum(m.get('precision_cm',.1) for m in (a,b))
        rows.append({'method_id':'hv-interval/1','from':a['date'],'to':b['date'],'days':days,'delta_cm':delta,
                     'value':delta*365.25/days if not reason else None,'reason':reason,
                     'precision_bound_cm_year':precision*365.25/days if days>0 else None,
                     'measurement_ids':[a['id'],b['id']],'revisions':[a['revision'],b['revision']],
                     'mid_date':(date.fromisoformat(a['date'])+timedelta(days=days/2)).isoformat()})
    return rows


def longitudinal_phv(athlete,measures,hv):
    method='phv-local-quadratic/1'
    if len(hv)<POLICY['phv_min_measures']-1 or any(r['value'] is None for r in hv):return unavailable('Servono almeno 7 stature con intervalli validi e senza discontinuità.',method)
    span=(date.fromisoformat(hv[-1]['to'])-date.fromisoformat(hv[0]['from'])).days
    if span<POLICY['phv_min_span_days']:return unavailable('Servono almeno due anni di osservazioni attorno al picco.',method)
    peak=int(np.argmax([r['value'] for r in hv]))
    if peak<2 or peak>len(hv)-3:return unavailable('Picco al bordo o senza due intervalli di supporto per lato.',method)
    rows=hv[peak-2:peak+3];origin=date.fromisoformat(rows[2]['mid_date'])
    x=np.array([(date.fromisoformat(r['mid_date'])-origin).days/365.25 for r in rows]);y=np.array([r['value'] for r in rows])
    a,b,c=np.polyfit(x,y,2)
    if a>=-1e-6:return unavailable('Nessun massimo interno della curva locale.',method)
    t=-b/(2*a);predicted=a*t*t+b*t+c
    if not x[0]<t<x[-1] or predicted<=0:return unavailable('Massimo locale fuori dalla finestra o non valido.',method)
    when=origin+timedelta(days=float(t)*365.25)
    if min((when-date.fromisoformat(rows[0]['mid_date'])).days,(date.fromisoformat(rows[-1]['mid_date'])-when).days)<POLICY['phv_support_days']:
        return unavailable('Copertura insufficiente prima/dopo il massimo locale (180 giorni per lato).',method)
    return {'value':float(predicted),'method_id':method,'reason':None,'date':when.isoformat(),
            'aphv_years':age_at(athlete.get('birth_date'),when.isoformat()),'origin':'Ricostruzione longitudinale esplorativa, non misura istantanea del PHV.',
            'rmse_cm_year':float(np.sqrt(np.mean((np.polyval([a,b,c],x)-y)**2))),
            'support':[r['revisions'] for r in rows],'uncertainty':'Nessun intervallo individuale validato; sensibilità a frequenza e precisione delle misure.'}


def analyze(athlete,measures,on):
    date.fromisoformat(on)
    measures=sorted([m for m in measures if m['date']<=on and m.get('status')!='deleted'],key=lambda m:(m['date'],m['id']))
    source={'athlete':athlete,'measurements':measures,'on':on,'engine':VERSION,'policy':POLICY}
    series=[anthropometric(athlete,m) for m in measures];hv=height_velocity(measures);phv=longitudinal_phv(athlete,measures,hv)
    previous=None
    for m,s in zip(measures,series):
        limb=m.get('lower_limb_cm')
        value=None;reason='Servono due misure specifiche valide distanziate di 90–400 giorni.'
        if limb is not None:
            if previous:
                days=(date.fromisoformat(m['date'])-date.fromisoformat(previous['date'])).days
                delta=limb-previous['lower_limb_cm']
                if 90<=days<=400 and delta>=0 and all(r.get('source')=='misurato' and r.get('quality','valid')=='valid' for r in (m,previous)):
                    candidate=delta*365.25/days
                    if candidate<=20:value=candidate;reason=None
            previous=m
        s['optional']['limb_velocity']={'value':value,'reason':reason,'method_id':'limb-hv-interval/1'}
    age=age_at(athlete.get('birth_date'),on)
    stature=[m for m in measures if m.get('height_cm') is not None]
    stability=unavailable('Valutabile da 18 anni con almeno tre stature misurate valide su un anno; non prova la fine della crescita.','height-stability/1')
    if age is not None and age>=18 and len(stature)>=3:
        last=stature[-1];window=[m for m in stature if 0<=(date.fromisoformat(last['date'])-date.fromisoformat(m['date'])).days<=730]
        if len(window)>=3 and (date.fromisoformat(last['date'])-date.fromisoformat(window[0]['date'])).days>=365 and all(m.get('source')=='misurato' and m.get('quality','valid')=='valid' for m in window):
            delta=max(m['height_cm'] for m in window)-min(m['height_cm'] for m in window)
            stability={'value':delta,'method_id':'height-stability/1','reason':None,'from':window[0]['date'],'to':last['date'],
                       'interpretation':'Variazione contenuta (≤0,5 cm nel periodo osservato), senza garanzia di crescita conclusa.' if delta<=.5 else 'Variazione superiore a 0,5 cm nel periodo: documentare l’andamento.'}
    band='Età non disponibile' if age is None else '<13' if age<13 else '13–<14' if age<14 else '14–<15' if age<15 else '15–<16' if age<16 else '16–<18' if age<18 else '≥18'
    return {'engine':VERSION,'policy':POLICY.copy(),'on':on,'age_years':age,'age_band':band,
            'series':series,'hv':hv,'phv':phv,'stability':stability,'warnings':WARNINGS,
            'inputs':{'athlete':athlete,'measurements':measures},
            'source_revisions':[athlete['revision']]+[m['revision'] for m in measures],
            'input_hash':hashlib.sha256(encoded(source).encode()).hexdigest()}


def current(store,athlete,on):
    return analyze(athlete,[m for m in store.list('measurement') if m['athlete_id']==athlete['id']],on)


def snapshots(store,athlete_id,on=None):
    return sorted([r for r in store.list('report') if r.get('analysis_type')=='maturation' and r.get('athlete_id')==athlete_id and (not on or r['analysis']['on']<=on)],key=lambda r:(r['created_at'],r['id']),reverse=True)


def export_files(z,store,athlete_ids):
    import csv,io
    measures=[m for m in store.list('measurement') if m['athlete_id'] in athlete_ids and m.get('status')!='deleted']
    fields=['id','revision',*MeasurementPayload.model_fields]
    raw=io.StringIO(newline='');w=csv.DictWriter(raw,fieldnames=fields);w.writeheader();w.writerows({k:m.get(k) for k in fields} for m in measures)
    z.writestr('extended/antropometria_completa.csv',raw.getvalue())
    saved=[r for r in store.list('report') if r.get('analysis_type')=='maturation' and r.get('athlete_id') in athlete_ids]
    raw=io.StringIO(newline='');w=csv.writer(raw);w.writerow(['snapshot_id','snapshot_revision','athlete_id','on','date','metric','value','method_id','reason','provenance_json'])
    for r in saved:
        a=r['analysis']
        def row(when,metric,value):w.writerow([r['id'],r['revision'],r['athlete_id'],a['on'],when,metric,value.get('value'),value['method_id'],value.get('reason'),encoded(value)])
        for h in a['hv']:row(h['to'],'hv_cm_year',h)
        row(a['phv'].get('date',''),'phv_cm_year',a['phv'])
        if a.get('stability'):row(a['on'],'height_stability_range_cm',a['stability'])
        for s in a['series']:
            for name,v in s['models'].items():
                row(s['date'],name+'_offset_years',v)
                row(s['date'],name+'_aphv_years',{**v,'value':v.get('aphv_years')})
            for name,v in s['optional'].items():row(s['date'],name,v)
    z.writestr('extended/maturazione.csv',raw.getvalue())
    z.writestr('extended/maturazione_snapshot.json',encoded(saved))


def report_section(entry,text,grid,image):
    from reportlab.lib.units import cm
    saved=entry.get('maturation',[])
    if not saved:return
    a=saved[0]['analysis'];text('Crescita e maturazione — analisi conservata','Heading2')
    text('Riferimento: '+a['on']+'; metodo '+a['engine']+'. '+saved[0]['reason'],'Small')
    text('Lo snapshot conserva i dati disponibili al momento del calcolo; non viene ricalcolato nel report. Misure successive o corrette richiedono una nuova analisi.','Small')
    grid(['Intervallo','Giorni','HV cm/anno','Qualità'],[[h['from']+' / '+h['to'],h['days'],h['value'],h['reason'] or 'Valida'] for h in a['hv']],[5.2*cm,1.4*cm,2.4*cm,8.7*cm])
    if a['hv']:
        from matplotlib.figure import Figure
        import io
        fig=Figure(figsize=(9,3.6),layout='constrained');ax=fig.subplots();ax.plot([h['mid_date'] for h in a['hv']],[h['value'] if h['value'] is not None else float('nan') for h in a['hv']],marker='o',color='#1a62b7');ax.set_ylabel('HV - cm/anno');ax.tick_params(axis='x',rotation=30,labelsize=8);ax.grid(alpha=.2)
        out=io.BytesIO();fig.savefig(out,format='png',dpi=140);image(out.getvalue(),'growth-'+saved[0]['id']+'.png')
    grid(['Data','Moore offset anni','Moore APHV anni','Mirwald offset anni','Mirwald APHV anni'],[[s['date'],s['models']['moore']['value'],s['models']['moore'].get('aphv_years'),s['models']['mirwald']['value'],s['models']['mirwald'].get('aphv_years')] for s in a['series']])
    missing=sorted({name+': '+v['reason'] for s in a['series'] for name,v in s['models'].items() if v.get('reason')})
    for reason in missing:text('Indisponibilità — '+reason,'Small')
    phv=a['phv'];text('PHV longitudinale esplorativo: '+(str(round(phv['value'],2))+' cm/anno, '+phv['date']+', APHV '+(str(round(phv['aphv_years'],2)) if phv.get('aphv_years') is not None else 'n.d.')+' anni' if phv['value'] is not None else phv['reason']),'Small')
    if a.get('stability',{}).get('value') is not None:text('Statura: '+a['stability']['interpretation'],'Small')
    optional=[s for s in a['series'] if s['optional']['pah']['value'] is not None]
    if optional:
        text('Indici facoltativi da previsione adulta esterna','Small')
        grid(['Data','%PAH','Residuo cm','Fonte / metodo'],[[s['date'],s['optional']['pah']['value'],s['optional']['residual']['value'],str(s['optional']['pah'].get('source'))+' / '+str(s['optional']['pah'].get('prediction_method'))] for s in optional])
    text('HV: velocità media di crescita nell’intervallo; PHV/APHV: picco ed età al picco. Le equazioni di Moore/Mirwald stimano offset/APHV, non misurano il picco. %PAH: percentuale della statura adulta prevista.','Small')
    for warning in a['warnings']:text(warning,'Small')
    if len(saved)>1:text('Ulteriori analisi conservate (risultati completi nel CSV/manifest): '+'; '.join(r['analysis']['on']+' / '+r['analysis']['engine'] for r in saved[1:]),'Small')


def install_api(app,store,require,download):
    class SaveAnalysis(BaseModel):
        model_config=ConfigDict(extra='forbid')
        on:date
        input_hash:str=Field(min_length=64,max_length=64)
        reason:str=Field(min_length=3,max_length=1000)
    @app.get('/api/v1/athletes/{id}/maturation')
    def preview(id:str,on:date):
        a=require(id,'athlete');return {'preview':current(store,a,on.isoformat()),'history':snapshots(store,id)}
    @app.post('/api/v1/athletes/{id}/maturation')
    def save(id:str,data:SaveAnalysis):
        a=require(id,'athlete');result=current(store,a,data.on.isoformat())
        if result['input_hash']!=data.input_hash:raise ConflictError('Misure o profilo modificati: ricalcolare l’anteprima prima di salvare.')
        payload={'analysis':result,'athlete_id':id,'organization_id':a['organization_id'],'reason':data.reason,
                 'created_at':datetime.now(timezone.utc).isoformat(),'analysis_type':'maturation','format':'json','objects':[]}
        payload['objects']=[store.object(encoded(payload).encode())]
        return store.save('report',payload)
    @app.get('/api/v1/athletes/{id}/maturation/{snapshot_id}')
    def get_snapshot(id:str,snapshot_id:str):
        require(id,'athlete');r=require(snapshot_id,'report')
        if r.get('analysis_type')!='maturation' or r.get('athlete_id')!=id:raise ValueError('Analisi non appartenente all’atleta.')
        return r
