"""One filtered dataset for interactive histories and exported reports."""
from collections import defaultdict
from statistics import median, mean, stdev
import numpy as np
from .methods import comparison_key

METRICS = ['map_w','map_wkg','threshold_w','threshold_wkg','ftp_w','ftp_wkg','weight_kg','height_cm','fthr_bpm','fc_max_test_bpm','lactate_2_w','lactate_4_w','vo2peak_l_min','vo2peak_ml_kg_min']

from .anaerobic import METRICS as ANAEROBIC_METRICS
METRICS=list(dict.fromkeys(METRICS+ANAEROBIC_METRICS))

def metric_applicable(record,metric):
    from .anaerobic import is_anaerobic
    return metric in ('weight_kg','height_cm','fc_max_test_bpm','work_kj') or is_anaerobic(record)==(metric in ANAEROBIC_METRICS)

def summarize(store, org, group='', season='', athlete='', mode='athlete', dimension='season', protocol=''):
    if mode not in ('athlete','tests') or dimension not in ('season','category','category_season','category_year','category_year_season','cohort','cohort_season','age','age_season','athlete','all'):
        raise ValueError('Modalità di aggregazione non valida.')
    athletes = {a['id']:a for a in store.list('athlete') if a['organization_id']==org and a.get('status')!='deleted'}
    groups = {g['id']:g for g in store.list('group') if g['organization_id']==org}
    buckets, observations = defaultdict(list), []
    for t in store.list('test'):
        if t['athlete_id'] not in athletes or t.get('status')=='deleted' or athlete and t['athlete_id']!=athlete or protocol and t['protocol_id']!=protocol:
            continue
        a = athletes[t['athlete_id']]
        members = [m for m in store.list('membership') if m.get('status')!='deleted' and m['athlete_id']==a['id'] and m['start']<=t['date'] and (not m.get('end') or m['end']>=t['date'])]
        memberships = [(groups[m['group_id']], m.get('category_year')) for m in members if m['group_id'] in groups]
        if not memberships:
            memberships = [({'id':'','name':'Senza categoria','season':t['date'][:4]}, None)]
        seen = set()
        for g, category_year in memberships:
            category = groups.get(g.get('parent_id'),g)
            year = g.get('season') or t['date'][:4]
            if group and group not in (g['id'],category['id']) or season and year!=season:
                continue
            cohort = str(a.get('birth_year') or 'Nascita ignota')
            age=str(int(t['date'][:4])-a['birth_year']) if a.get('birth_year') else 'Età ignota'
            keys = {'season':year,'category':category['name'],'category_season':category['name']+' / '+year,
                    'category_year':category['name']+' / '+str(category_year or '?'),
                    'category_year_season':category['name']+' / '+str(category_year or '?')+' / '+year,
                    'cohort':cohort,'cohort_season':cohort+' / '+year,'age':age,'age_season':age+' / '+year,'athlete':a['surname']+' '+a['name'],'all':'Totale'}
            # Never silently pool distinct protocol versions or threshold methods.
            label = keys[dimension]
            key = (label,t['protocol_id'],t['analysis'].get('threshold_source') or 'n.d.',comparison_key(t))
            if key in seen:
                continue
            seen.add(key)
            row = {'id':t['id'],'revision':t['revision'],'test_type':t.get('test_type'),'athlete_id':a['id'],'athlete':a['surname']+' '+a['name'],
                   'date':t['date'],'protocol_id':t['protocol_id'],'group':label,
                   'method_key':comparison_key(t),'method_label':t['analysis'].get('preset',{}).get('name',t['analysis'].get('source','Legacy')+' / '+t['analysis'].get('engine','ignoto')),
                   'conditions':t['settings'].get('conditions',{}),'birth_confirmed':a.get('birth_confirmed',False),
                   **{m:t['analysis'].get(m) for m in METRICS},
                   **{m:t['settings'].get(m) for m in ('weight_kg','height_cm')},
                   'threshold_source':t['analysis'].get('threshold_source'),'weight_source':t['settings'].get('weight_source','dichiarato')}
            buckets[key].append(row)
            observations.append(row)
    result = []
    for key, rows in sorted(buckets.items()):
        all_count = len(rows)
        if mode=='athlete':
            chosen = {}
            for r in sorted(rows,key=lambda r:(r['date'],r['id'])):
                chosen[r['athlete_id']] = r
            rows = list(chosen.values())
        metrics = {}
        for metric in METRICS:
            eligible=[r for r in rows if metric_applicable(r,metric)]
            values = [r[metric] for r in eligible if r.get(metric) is not None and not (metric.endswith('wkg') and r['weight_source']=='stimato')]
            metrics[metric] = {'n':len(values),'missing':len(eligible)-len(values),'median':median(values) if values else None,
                               'mean':mean(values) if values else None,'min':min(values) if values else None,'max':max(values) if values else None,
                               'q1':float(np.quantile(values,.25)) if values else None,'q3':float(np.quantile(values,.75)) if values else None,
                               'sd':stdev(values) if len(values)>1 else None}
        result.append({'label':key[0],'protocol_id':key[1],'threshold_source':key[2],'method_key':key[3],'method_label':rows[0]['method_label'], 'tests_available':all_count,
                       'tests_selected':len(rows),'athletes':len({r['athlete_id'] for r in rows}),'metrics':metrics,
                       'revisions':[r['revision'] for r in rows]})
    unique = {r['id']:r for r in observations}
    previous={}
    changes=[]
    for r in sorted(unique.values(),key=lambda r:(r['date'],r['id'])):
        key=(r['athlete_id'],r['protocol_id'],r['threshold_source'],r['method_key'])
        last=previous.get(key)
        change={'id':r['id'],'athlete':r['athlete'],'date':r['date'],'previous_date':last['date'] if last else None,'protocol_id':r['protocol_id']}
        for metric in METRICS:
            old=last.get(metric) if last else None;new=r.get(metric)
            change[metric+'_delta']=new-old if new is not None and old is not None else None
            change[metric+'_pct']=100*(new-old)/old if new is not None and old is not None and old!=0 else None
        changes.append(change);previous[key]=r
    return {'schema':1,'query':dict(organization_id=org,group=group,season=season,athlete=athlete,mode=mode,dimension=dimension,protocol=protocol),
            'groups':result,'rows':sorted(unique.values(),key=lambda r:r['date']),
            'changes':changes,
            'coverage':{m:{'valid':sum(r.get(m) is not None for r in unique.values() if metric_applicable(r,m)),'total':sum(metric_applicable(r,m) for r in unique.values())} for m in METRICS}}


def growth(store, org, athlete=''):
    from datetime import date
    athletes={a['id']:a for a in store.list('athlete') if a['organization_id']==org and a.get('status')!='deleted' and (not athlete or a['id']==athlete)}
    rows=[]
    for id,a in athletes.items():
        previous={}
        for m in sorted([r for r in store.list('measurement') if r['athlete_id']==id and r.get('status')!='deleted'],key=lambda r:(r['date'],r['id'])):
            for metric in ('weight_kg','height_cm'):
                if m.get(metric) is None:continue
                last=previous.get(metric)
                if last:
                    days=(date.fromisoformat(m['date'])-date.fromisoformat(last['date'])).days
                    delta=m[metric]-last[metric]
                    rows.append({'id':m['id']+metric,'athlete':a['surname']+' '+a['name'],'metric':metric,'date':m['date'],'previous_date':last['date'],
                                 'days':days,'delta':delta,'annualized':delta*365.25/days if days>0 else None,'source':m.get('source','dichiarato')})
                previous[metric]=m
    return rows


def paired_comparison(store,org,first,second,group=''):
    if first==second:raise ValueError('Selezionare due stagioni diverse.')
    left=summarize(store,org,group,first,mode='athlete',dimension='all')
    right=summarize(store,org,group,second,mode='athlete',dimension='all')
    def select(data):
        rows={}
        for r in sorted(data['rows'],key=lambda r:(r['date'],r['id'])):
            rows[(r['athlete_id'],r['protocol_id'],r['threshold_source'],r['method_key'])]=r
        return rows
    a,b=select(left),select(right);rows=[]
    for key in sorted(a.keys() & b.keys()):
        before,after=a[key],b[key]
        row={'id':after['id'],'athlete':after['athlete'],'protocol_id':after['protocol_id'],'from':before['date'],'to':after['date'],'source':key[2]}
        for m in METRICS:
            x,y=before.get(m),after.get(m)
            row[m+'_delta']=y-x if x is not None and y is not None else None
            row[m+'_pct']=100*(y-x)/x if x is not None and x!=0 and y is not None else None
        rows.append(row)
    return {'first':first,'second':second,'pairs':rows,'n_pairs':len(rows),'unpaired_first':len(a.keys()-b.keys()),'unpaired_second':len(b.keys()-a.keys())}
