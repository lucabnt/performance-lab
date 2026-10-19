"""Explicit specialist methods. Estimates are not interchangeable diagnoses."""
import csv
import io
import math
from statistics import mean, stdev
import numpy as np
from numpy.polynomial import Polynomial
from .analysis import valid_number, window, intervals


def integrator(samples,field,max_gap,excluded):
    """Prefix integrals for O(log n) windows; preserve gaps and exclusions."""
    spans=list(intervals(samples,field,samples[0]['t'],samples[-1]['t'],max_gap,excluded))
    spans.sort(key=lambda r:r[2])
    starts=np.array([r[2] for r in spans]);ends=np.array([r[3] for r in spans]);values=np.array([r[0] for r in spans])
    duration=ends-starts
    areas=np.concatenate(([0.],np.cumsum(values*duration)));times=np.concatenate(([0.],np.cumsum(duration)))
    def upto(t):
        i=int(np.searchsorted(ends,t,side='right'))
        dt=max(0,t-starts[i]) if i<len(starts) else 0
        return areas[i]+(values[i]*dt if i<len(values) else 0),times[i]+dt
    def query(a,b):
        va,ta=upto(a);vb,tb=upto(b);covered=tb-ta
        return {'mean':(vb-va)/covered if covered>0 else None,'coverage':covered/(b-a) if b>a else 0}
    return query


def metric(value,method,unit='W',reason=None,**extra):
    return {'value':value,'unit':unit,'method_id':method,'status':'estimated' if value is not None else 'unavailable',
            'reason':reason,**extra}


def lactate(analysis,observations,levels=None,weight_kg=None,weight_source='dichiarato'):
    from .lactate_levels import DEFAULT_LEVELS,validate_levels,token
    levels=validate_levels(DEFAULT_LEVELS if levels is None else levels)
    params=analysis.get('preset',{}).get('parameters',{})
    hr_window=params.get('hr_window_s',30.)
    snapshot={'method_id':'lactate.fixed-linear/2','hr_method':'stage-final-window/1','hr_window_s':hr_window,
              'hr_coverage':params.get('hr_coverage',.8),'association':'explicit-step-or-delay/1','extrapolate':False}
    points=[];unmatched=[]
    for obs in observations:
        at=obs['at_s']-obs.get('delay_s',0)
        stage=next((s for s in analysis['steps'] if (obs.get('step_number')==s['number'] if obs.get('step_number') is not None else s['aligned_start_s']<at<=s['aligned_end_s'])),None)
        power=obs.get('power_w')
        if power is None and stage and stage['start_w']==stage['end_w']:power=stage['end_w']
        if power is None:unmatched.append(obs);continue
        hr=stage.get('hr',{}) if stage else {}
        hr_ok=bool(stage and stage.get('complete') and stage.get('actual_s',0)>=hr_window and stage['start_w']==stage['end_w'] and hr.get('usable') and hr.get('coverage',0)>=snapshot['hr_coverage'] and hr.get('mean') is not None)
        points.append({'origin':obs.get('origin','manual'),'hr_bpm':hr.get('mean') if hr_ok else None,'hr_coverage':hr.get('coverage'),
                       'hr_reason':None if hr_ok else 'stage_hr_unavailable','hr_window_s':hr_window,'power_w':power,'mmol_l':obs['mmol_l'],'at_s':obs['at_s'],
                       'step_number':stage['number'] if stage else None,'source':'declared_load' if obs.get('power_w') is not None else 'protocol_target'})
    points.sort(key=lambda r:r['power_w']);x=np.array([r['power_w'] for r in points]);y=np.array([r['mmol_l'] for r in points])
    results={};warning=[]
    if unmatched:warning.append('Prelievi senza carico associato: selezionare step o carico esplicito.')
    valid=len(x)>=2 and len(set(x))==len(x)
    if not valid and points:warning.append('Servono carichi distinti; ripetizioni allo stesso carico richiedono revisione.')
    for level in levels:
        candidates=[]
        if valid:
            candidates=[(float(x[i]),i,i,0.) for i,v in enumerate(y) if v==level]
            candidates += [(float(x[i]+(x[i+1]-x[i])*(level-y[i])/(y[i+1]-y[i])),i,i+1,float((level-y[i])/(y[i+1]-y[i]))) for i in range(len(x)-1) if y[i]<level<y[i+1]]
        reason='ambiguous_crossing' if len(candidates)>1 or valid and any(np.diff(y)<0) else 'no_crossing'
        value=hr_value=wkg=None;hr_reason=weight_reason=reason;support=[]
        if len(candidates)==1 and not any(np.diff(y)<0):
            value,i,j,fraction=candidates[0];reason=None
            support=[points[i]] if i==j else [points[i],points[j]]
            if all(p['hr_bpm'] is not None for p in support):
                hr_value=float(points[i]['hr_bpm']+fraction*(points[j]['hr_bpm']-points[i]['hr_bpm']));hr_reason=None
            else:hr_reason='stage_hr_unavailable'
            if weight_kg and weight_source!='stimato':wkg=value/weight_kg;weight_reason=None
            else:weight_reason='weight_missing_or_estimated'
        results['fixed_'+token(level)]=metric(value,snapshot['method_id'],reason=reason,concentration_mmol_l=level,
            candidates_w=[c[0] for c in candidates],hr_bpm=hr_value,hr_reason=hr_reason,wkg=wkg,weight_reason=weight_reason,
            supporting_points=support,hr_method=snapshot['hr_method'],hr_window_s=hr_window)
    curve=[]
    for modified in (False,True):
        name='modified_dmax' if modified else 'dmax';method='lactate.'+name+'-cubic/1'
        result=metric(None,method,reason='at_least_five_distinct_loads_required')
        if valid and len(x)>=5 and np.all(np.diff(y)>=0):
            poly=Polynomial.fit(x,y,3).convert()
            anchor=0
            if modified:
                rises=np.flatnonzero(np.diff(y)>.4)
                anchor=int(rises[0]) if len(rises) else None
            if anchor is not None and anchor<len(x)-2:
                a,b=float(x[anchor]),float(x[-1]);ya,yb=(float(y[anchor]),float(y[-1])) if modified else (float(poly(a)),float(poly(b)))
                slope=(yb-ya)/(b-a)
                candidates=[float(r.real) for r in (poly.deriv()-slope).roots() if abs(r.imag)<1e-8 and a<r.real<b]
                candidates=[r for r in candidates if (ya+slope*(r-a)-poly(r))>0]
                if candidates:
                    best=max(candidates,key=lambda r:(ya+slope*(r-a)-poly(r))/math.sqrt(1+slope*slope))
                    result=metric(best,method,anchor_w=a,end_w=b,fit_coefficients=poly.coef.tolist(),
                                  fit_rmse_mmol_l=float(np.sqrt(np.mean((poly(x)-y)**2))))
                else:result=metric(None,method,reason='no_interior_positive_maximum')
                if not curve:curve=[{'power_w':float(z),'mmol_l':float(poly(z))} for z in np.linspace(x[0],x[-1],100)]
            else:result=metric(None,method,reason='no_valid_0_4_rise_anchor')
        results[name]=result
    return {'method_snapshot':snapshot,'levels_mmol_l':levels,'points':points,'unmatched':unmatched,'results':results,'curve':curve,'warnings':warning,
            'interpretation':'Metodi distinti; nessuna equivalenza automatica con FTP, MLSS o VT.'}


def decode_gas(raw):
    text=raw.decode('utf-8-sig')
    if not text.strip():raise ValueError('Gas CSV vuoto.')
    reader=csv.DictReader(io.StringIO(text),delimiter=';' if ';' in text.splitlines()[0] else ',')
    fields={'t':'t','vo2_l_min':'vo2','vco2_l_min':'vco2','ve_l_min':'ve','peto2_mmhg':'peto2','petco2_mmhg':'petco2'}
    if not {'t','vo2_l_min'}<=set(reader.fieldnames or []):raise ValueError('Gas CSV: colonne t e vo2_l_min obbligatorie; unità L/min.')
    rows=[]
    for line,row in enumerate(reader,2):
        try:
            record={dest:float(row[src].replace(',','.')) if row.get(src,'').strip() else None for src,dest in fields.items()}
            if record['t'] is None or not all(v is None or math.isfinite(v) for v in record.values()):raise ValueError()
        except (ValueError,AttributeError):raise ValueError(f'Gas CSV, riga {line}: numero non valido.')
        rows.append(record)
    if not 2<=len(rows)<=20000 or any(b['t']<=a['t'] for a,b in zip(rows,rows[1:])):raise ValueError('Gas: 2–20000 righe ordinate, senza timestamp duplicati.')
    return rows


def gas_analysis(samples,settings,analysis):
    p=analysis['preset']['parameters'];offset=settings.get('gas_offset_s',0)
    rows=[{**r,'t':r['t']+offset} for r in samples]
    increments=[s for s in analysis['steps'] if s['phase']=='increment']
    start=increments[0]['aligned_start_s'] if increments else settings['end_s'];end=settings['end_s'];width=p['vo2_window_s']
    exclusions=settings.get('excluded_intervals',[])
    channels={f:integrator(rows,f,p['max_gap_s'],exclusions) for f in ('vo2','vco2','ve','peto2','petco2')}
    candidates=sorted({r['t']+d for r in rows for d in (0,width) if start+width<=r['t']+d<=end})
    best=None
    for stop in candidates:
        value=channels['vo2'](stop-width,stop)
        if value['coverage']>=p['gas_coverage'] and (best is None or value['mean']>best['value']):
            best={'value':value['mean'],'start_s':stop-width,'end_s':stop,'coverage':value['coverage']}
    peak=metric(best['value'] if best else None,'gas.vo2peak-time-mean/1','L/min',reason=None if best else 'insufficient_window',window_s=width,window=best)
    weight=settings.get('weight_kg');peak['ml_kg_min']=peak['value']*1000/weight if peak['value'] is not None and weight else None
    # Fixed 30 s bins reduce breath noise for review and segmented regression.
    bins=[];a=start
    while a+30<=end:
        values={f:query(a,a+30) for f,query in channels.items()}
        means={f:v['mean'] if v['coverage']>=p['gas_coverage'] else None for f,v in values.items()}
        if means['vo2']:
            means.update(t=a+15,ve_vo2=means['ve']/means['vo2'] if means['ve'] is not None else None,
                         ve_vco2=means['ve']/means['vco2'] if means['ve'] is not None and means['vco2'] else None,
                         rer=means['vco2']/means['vo2'] if means['vco2'] else None)
            bins.append(means)
        a+=30
    def breakpoint(xfield,yfield):
        usable=[r for r in bins if r.get(xfield) is not None and r.get(yfield) is not None]
        if len(usable)<10:return metric(None,'gas.segmented-hinge-review/1','s',reason='at_least_ten_valid_30s_bins_required')
        x=np.array([r[xfield] for r in usable]);y=np.array([r[yfield] for r in usable]);bestfit=None
        for i in range(4,len(x)-4):
            pivot=x[i];design=np.column_stack([np.ones(len(x)),x,np.maximum(0,x-pivot)])
            coeff,_,rank,_=np.linalg.lstsq(design,y,rcond=None)
            if rank<3 or coeff[1]<=0 or coeff[2]<=0:continue
            sse=float(np.sum((y-design@coeff)**2))
            if bestfit is None or sse<bestfit[0]:bestfit=(sse,i,coeff)
        if bestfit is None:return metric(None,'gas.segmented-hinge-review/1','s',reason='no_positive_slope_change')
        sse,i,coeff=bestfit
        return {**metric(usable[i]['t'],'gas.segmented-hinge-review/1','s',slopes=[float(coeff[1]),float(coeff[1]+coeff[2])],sse=sse),'status':'needs_review','reason':'confirm_with_equivalents_and_end_tidal'}
    suggestions={'vt1':breakpoint('vo2','vco2'),'vt2':breakpoint('vco2','ve')}
    markers={}
    for key in ('vt1','vt2'):
        mark=settings.get('ventilatory_markers',{}).get(key)
        if mark:
            if not start<=mark['at_s']<end:raise ValueError('Marker ventilatorio fuori dalla fase incrementale.')
            markers[key]={**mark,'status':'declared_reviewed','method_id':'gas.reviewer-marker/1'}
    if 'vt1' in markers and 'vt2' in markers and markers['vt2']['at_s']<=markers['vt1']['at_s']:raise ValueError('VT2 deve seguire VT1.')
    verification=settings.get('vo2max_verification',{})
    confirmed=bool(verification.get('evidence','').strip() and verification.get('confirmed') and peak['value'] is not None)
    return {'vo2peak':peak,'vo2max':{**metric(peak['value'] if confirmed else None,'gas.reviewer-verified-maximum/1','L/min',reason=None if confirmed else 'maximum_not_verified'),
        'status':'declared_verified' if confirmed else 'unavailable','evidence':verification.get('evidence','')},
        'bins':bins,'suggestions':suggestions,'markers':markers,
        'warnings':['Breakpoint automatici esplorativi: confermare con equivalenti ventilatori, gas end-tidal e valutazione esperta; non equivalgono a VT validate.']}


def repeatability(pairs):
    differences=[b-a for a,b in pairs]
    n=len(differences);sd=stdev(differences) if n>=2 else None
    ci=None
    if n>=6:
        rng=np.random.default_rng(17052026)
        draws=rng.choice(np.array(differences),size=(2000,n),replace=True)
        errors=np.std(draws,axis=1,ddof=1)/math.sqrt(2)
        ci={'typical_error':[float(v) for v in np.quantile(errors,[.025,.975])],
            'method':'percentile-bootstrap','replicates':2000,'seed':17052026,'confidence':.95}
    return {'n_pairs':n,'bias':mean(differences) if n else None,'sd_difference':sd,'ci95':ci,
        'typical_error':sd/math.sqrt(2) if sd is not None else None,'mdc95':1.96*sd if sd is not None else None,
        'method':'repeatability.paired/1','status':'descriptive' if n>=2 else 'unavailable',
        'warning':'Coppie esplicitamente ripetute in condizioni stabili; stima incerta con pochi soggetti, nessuna diagnosi.'}
