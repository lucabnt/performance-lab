import csv
import io
import json
import zipfile
import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.store import Store
from cycling_test.anaerobic import Protocol,Settings,analyze,finish,signature,historical_plan,CSV_HEADER
from cycling_test.reports import export_csv
from cycling_test.history import summarize

def spec(family='wingate15',**extra):return Protocol(organization_id='org',name='Test',family=family,**extra).model_dump()
def samples(n=30):return [{'t':i,'power':1000-20*i,'hr':140+i,'cadence':120-i} for i in range(n+1)]

def test_elapsed_integrals_and_peak_windows():
    a=analyze(samples(),spec(),Settings(weight_kg=50).model_dump())
    assert a['mean_w']==860
    assert a['work_kj']==12.9
    assert a['peak_w']==a['best_1s_w']==1000
    assert a['best_5s_w']==960
    assert a['end_power_w']==720
    assert a['fatigue_pct']==28
    assert a['decline_ws']==20
    assert a['peak_wkg']==20
    assert a['time_to_peak_s']==0

def test_gap_coverage_and_no_extrapolation():
    data=samples();data[3]['power']=None
    a=analyze(data,spec(),Settings().model_dump())
    assert a['mean_w'] is None
    assert a['power_coverage']==pytest.approx(14/15)
    assert not a['complete']
    assert a['work_kj']==pytest.approx(11.96)
    a=analyze(samples(14),spec(),Settings().model_dump())
    assert a['observed_duration_s']==14 and a['end_power_w'] is None
    # Brief missing data may pass 95% gate, never produce a full mean.
    data=[{'t':i/10,'power':500} for i in range(151)];data[5]['power']=None
    a=analyze(data,spec(),Settings().model_dump())
    assert a['complete'] and a['mean_w'] is None

def test_exclusions_and_offset():
    a=analyze(samples(),spec(),Settings(offset_s=3,excluded_intervals=[{'start_s':4,'end_s':5,'reason':'Artefatto'}]).model_dump())
    assert a['peak_w']==940 and a['observed_duration_s']==14
    data=[{'t':0,'power':500},{'t':10,'power':1000},{'t':15,'power':1000}]
    assert analyze(data,spec(),Settings().model_dump())['work_kj'] is None

def test_peak_requires_contiguous_full_window():
    a=analyze([{'t':0,'power':1000},{'t':.3,'power':None},{'t':1,'power':800},{'t':2,'power':0}],spec(),Settings().model_dump())
    assert a['peak_w']==800

def test_protocols_and_provenance_never_pool():
    settings=Settings().model_dump()
    t={'settings':settings,'analysis':finish({'peak_w':800},spec(),settings,'manual')}
    keys={signature(t)}
    for family,source,window in [('wingate30','manual',1),('sprint','manual',1),('wingate15','computed',1),('wingate15','manual',5)]:
        keys.add(signature({'settings':settings,'analysis':finish({'peak_w':800},spec(family,peak_window_s=window),settings,source)}))
    assert len(keys)==5

def historical_csv(**changes):
    row=dict.fromkeys(CSV_HEADER.split(','),'');row.update(test_id='T1',atleta_id='A1',data='2026-07-01',protocollo_id='ANA-15-070',peso_kg='50',peso_fonte='derivato',picco_w='1000',media_w='800',lavoro_kj='12.2',indice_fatica_ws='18.2',**changes)
    out=io.StringIO();writer=csv.DictWriter(out,fieldnames=row);writer.writeheader();writer.writerow(row);return out.getvalue().encode()

def seeded(tmp_path):
    store=Store(tmp_path);org=store.save('organization',{'name':'Synthetic'})
    a=store.save('athlete',{'organization_id':org['id'],'external_id':'A1','surname':'Esempio','name':'Atleta','status':'active'})
    return store,org,a

def test_import_legacy_torque_missing_values_roundtrip(tmp_path):
    store,org,a=seeded(tmp_path);plan=historical_plan(store,org['id'],historical_csv())
    assert not plan['errors'];store.save_batch(plan['entries'])
    t=store.list('test')[0];p=store.get(t['protocol_id'])
    assert p['anaerobic_spec']['torque_nm_kg']==.70
    assert p['anaerobic_spec']['peak_window_s'] is None
    assert t['analysis']['declared_fatigue_ws']==18.2
    assert t['analysis']['fatigue_pct'] is None and t['analysis']['end_power_w'] is None
    assert t['settings']['weight_source']=='derivato'
    assert any('Lavoro e media' in w for w in t['analysis']['warnings'])
    assert historical_plan(store,org['id'],historical_csv())['skipped']==1
    with zipfile.ZipFile(io.BytesIO(export_csv(store,org['id']))) as z:
        raw=z.read('test_anaerobico.csv');assert raw.decode().splitlines()[0]==CSV_HEADER
        assert historical_plan(store,org['id'],raw)['skipped']==1
        assert len(list(csv.DictReader(io.StringIO(z.read('test_aerobico.csv').decode()))))==0
    data=summarize(store,org['id']);assert data['groups'][0]['metrics']['peak_w']['mean']==1000
    assert data['coverage']['map_w']['total']==0
    assert data['groups'][0]['metrics']['map_w']['missing']==0
    c=TestClient(create_app(tmp_path,token='t'));c.headers['X-Fuorigiri-Token']='t'
    payload={'athlete_id':a['id'],'protocol_id':p['id'],'date':t['date'],'revision':t['revision'],'reason':'Correzione riepilogo','manual':{'peak_w':1010,'mean_w':800,'declared_fatigue_ws':18.2},'settings':t['settings']}
    assert c.post('/api/v1/anaerobic/historical/'+t['id']+'/preview',json=payload).status_code==200
    result=c.put('/api/v1/anaerobic/historical/'+t['id'],json=payload)
    assert result.status_code==200,result.text
    assert result.json()['historical_fields']['picco_w']==1010 and result.json()['analysis']['source']=='legacy-csv'
    assert store.history(t['id'])[0]['historical_fields']['picco_w']=='1000'

def test_import_errors_never_invent_unknown_protocol(tmp_path):
    store,org,a=seeded(tmp_path)
    raw=historical_csv().replace(b'ANA-15-070',b'UNKNOWN')
    plan=historical_plan(store,org['id'],raw)
    assert plan['errors'] and not plan['entries'] and not store.list('protocol')

def test_api_manual_trace_revision_and_reports(tmp_path):
    c=TestClient(create_app(tmp_path,token='test'));c.headers['X-Fuorigiri-Token']='test'
    def post(path,data):
        r=c.post('/api/v1/'+path,json=data);assert r.status_code==200,r.text;return r.json()
    org=post('organizations',{'name':'Synthetic'})
    a=post('athletes',{'organization_id':org['id'],'name':'Atleta','surname':'Esempio'})
    p=post('anaerobic/protocols',{'organization_id':org['id'],'name':'Wingate','family':'wingate15','torque_nm_kg':.70})
    payload={'athlete_id':a['id'],'protocol_id':p['id'],'date':'2026-07-01','manual':{'peak_w':1000,'mean_w':800},'settings':{'weight_kg':50}}
    t=post('anaerobic/tests',payload)
    assert t['analysis']['peak_wkg']==20
    for fmt in ('pdf','md'):
        r=c.get(f'/api/v1/tests/{t["id"]}/report/{fmt}');assert r.status_code==200,r.text
        assert r.content.startswith(b'%PDF' if fmt=='pdf' else b'PK')
    payload.update(revision=t['revision'],reason='Correzione peso',settings={'weight_kg':55})
    r=c.put('/api/v1/anaerobic/tests/'+t['id'],json=payload);assert r.status_code==200,r.text
    assert r.json()['analysis']['peak_wkg']==pytest.approx(1000/55)
    assert c.put('/api/v1/anaerobic/tests/'+t['id'],json=payload).status_code==409
    raw='t,power,hr,cadence\n'+'\n'.join(f'{r["t"]},{r["power"]},{r["hr"]},{r["cadence"]}' for r in samples())
    tr=c.post('/api/v1/traces',files={'file':('test.csv',raw,'text/csv')});assert tr.status_code==200,tr.text
    payload.update(trace_hash=tr.json()['hash'],manual={},revision=None,reason='')
    t=post('anaerobic/tests',payload);assert t['analysis']['mean_w']==860
    from cycling_test.archive_report import build,render
    store=Store(tmp_path);data=build(store,org['id']);assert render(data,'md').startswith(b'PK')

@pytest.mark.parametrize('kwargs',[{'duration_s':11,'family':'sprint'},{'peak_window_s':0},{'coverage_min':.5}])
def test_invalid_protocol(kwargs):
    family=kwargs.pop('family','wingate15')
    with pytest.raises(ValueError):spec(family,**kwargs)

@pytest.mark.parametrize('family,duration',[('sprint',6),('wingate15',15),('wingate30',30)])
def test_synthetic_fit_end_to_end(family,duration):
    from pathlib import Path
    from cycling_test.fit import decode_fit
    trace=decode_fit((Path(__file__).parents[1]/'examples/synthetic'/f'SIM-ANA-{family}.fit').read_bytes(),session_index=0)
    a=analyze(trace['samples'],spec(family),Settings(offset_s=60,weight_kg=60).model_dump())
    assert a['duration_s']==a['observed_duration_s']==duration
    assert a['complete'] and 500<a['peak_w']<1200
    assert a['mean_w']*duration/1000==pytest.approx(a['work_kj'])

def test_extended_csv_preserves_duration_and_provenance(tmp_path):
    from cycling_test.anaerobic import EXTENDED_HEADER,extended_row
    store,org,athlete=seeded(tmp_path);s=Settings(weight_kg=60).model_dump()
    p=store.save('protocol',{'family':'wingate30','name':'Wingate 30 s','version':'1','test_type':'wingate30','organization_id':org['id']})
    a=analyze(samples(),spec('wingate30'),s)
    t=store.save('test',{'test_type':'wingate30','athlete_id':athlete['id'],'protocol_id':p['id'],'date':'2026-07-01','settings':s,'analysis':a})
    out=io.StringIO();w=csv.DictWriter(out,fieldnames=EXTENDED_HEADER.split(','));w.writeheader();w.writerow(extended_row(t,p))
    # A fresh archive with the same athlete ID, like an exported CSV import.
    other=Store(tmp_path/'other');other.save('organization',{'name':'Other'},id=org['id']);other.save('athlete',{**athlete,'organization_id':org['id']},id=athlete['id'])
    plan=historical_plan(other,org['id'],out.getvalue().encode());assert not plan['errors'],plan['errors']
    test=next(v for k,v in plan['entries'] if k=='test')
    assert test['test_type']=='wingate30' and test['analysis']['duration_s']==30
    assert test['analysis']['best_5s_w']==a['best_5s_w'] and test['analysis']['source']=='legacy-csv'
    assert test['historical_fields']['origine_risultati']=='computed'
