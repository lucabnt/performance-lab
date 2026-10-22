import io
import json
import zipfile
import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.custom_fields import definitions,values,metric_key

FIELDS=[{'key':'repetitions','label':'Ripetizioni','type':'number','scope':'protocol','minimum':1,'maximum':20}, {'key':'peak','label':'Picco dichiarato','type':'number','scope':'test','unit':'W','minimum':0,'maximum':3000}, {'key':'completed','label':'Completato','type':'boolean','scope':'test'}, {'key':'recovery','label':'Recupero','type':'choice','scope':'test','choices':['Attivo','Passivo']},{'key':'date_check','label':'Data verifica','type':'date','scope':'test'}]

@pytest.mark.parametrize('data',[{'peak':True},{'peak':float('inf')},{'peak':-1},{'completed':'true'},{'recovery':'Unknown'},{'date_check':'2026-99-99'},{'unknown':1},{'repetitions':3}])
def test_typed_optional_validation(data):
    with pytest.raises(ValueError):values(definitions(FIELDS),data,'test')

def test_null_false_and_schema_identifiers():
    fields=definitions(FIELDS)
    assert values(fields,{'completed':False,'peak':0,'date_check':None},'test')=={'completed':False,'peak':0}
    with pytest.raises(ValueError):definitions([FIELDS[0],FIELDS[0]])
    with pytest.raises(ValueError):definitions([{**FIELDS[0],'key':'analysis.map_w'}])
    assert metric_key('p',FIELDS[1])!=metric_key('p',{**FIELDS[1],'unit':'W/kg'})

def client(tmp_path):
    c=TestClient(create_app(tmp_path,token='t'));c.headers['X-Fuorigiri-Token']='t'
    def post(path,data):
        r=c.post('/api/v1/'+path,json=data);assert r.status_code==200,r.text;return r.json()
    org=post('organizations',{'name':'Club sintetico'});a=post('athletes',{'organization_id':org['id'],'name':'Demo','surname':'Atleta'})
    return c,post,org,a

def test_custom_full_path_revision_history_reports_and_export(tmp_path):
    c,post,org,a=client(tmp_path)
    p=post('custom/protocols',{'organization_id':org['id'],'name':'Sprint ripetuti','family':'RSA','version':'1','custom_fields':FIELDS,'custom_values':{'repetitions':5}})
    def payload(peak):return {'athlete_id':a['id'],'protocol_id':p['id'],'date':'2026-10-01','settings':{'custom_values':{'peak':peak,'completed':False}}}
    first=post('custom/tests',payload(800));second=post('custom/tests',payload(1000))
    assert first['analysis']['custom_values']['completed'] is False
    assert 'map_w' not in first['analysis']
    key=next(k for k in first['analysis'] if k.startswith('custom:'))
    data=c.get('/api/v1/history/'+org['id']+'?mode=tests').json()
    assert data['groups'][0]['metrics'][key]['mean']==900
    assert data['metric_labels'][key]=='Picco dichiarato (W)'
    for fmt in ('md','pdf'):
        r=c.get(f'/api/v1/tests/{first["id"]}/report/{fmt}');assert r.status_code==200,r.text
        assert r.content.startswith(b'PK' if fmt=='md' else b'%PDF')
        r=c.get(f'/api/v1/history/{org["id"]}/report/{fmt}?mode=tests&metric={key}');assert r.status_code==200,r.text
        r=c.get(f'/api/v1/archive/{org["id"]}/report/{fmt}');assert r.status_code==200,r.text
    r=c.get('/api/v1/export/'+org['id']);assert r.status_code==200,r.text
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        assert b'completed' in z.read('extended/campi_personalizzati.csv')
        archive=json.loads(z.read('extended/archive.json'));assert archive
    revised={**payload(850),'revision':first['revision'],'reason':'Correzione lettura'}
    r=c.put('/api/v1/custom/tests/'+first['id'],json=revised);assert r.status_code==200,r.text
    assert c.put('/api/v1/custom/tests/'+first['id'],json=revised).status_code==409
    post('custom/protocols',{'organization_id':org['id'],'name':'Sprint ripetuti','family':'RSA','version':'2','parent_id':p['id'],'reason':'Unità relativa','custom_fields':[{**FIELDS[1],'unit':'W/kg'}]})
    assert c.post('/api/v1/manual-tests',json={'athlete_id':a['id'],'protocol_id':p['id'],'date':'2026-10-01','settings':{}}).status_code==422

def test_extensions_on_supported_manual_tests(tmp_path):
    c,post,org,a=client(tmp_path)
    p=post('protocols/manual',{'organization_id':org['id'],'name':'Incrementale scheda','family':'AER','version':'1','segments':[],'custom_fields':FIELDS,'custom_values':{'repetitions':1}})
    data={'athlete_id':a['id'],'protocol_id':p['id'],'date':'2026-10-01','map_w':200,'settings':{'weight_kg':50,'custom_values':{'peak':900},'extra_fields':[{'key':'sleep','label':'Sonno','type':'number','scope':'test','unit':'h'}]}}
    t=post('manual-tests',data);assert t['analysis']['custom_values']['peak']==900
    assert t['analysis']['map_wkg']==4
    data['settings']['custom_values']['sleep']=7.5;t=post('manual-tests',data)
    assert t['analysis']['custom_values']['sleep']==7.5
    p=post('anaerobic/protocols',{'organization_id':org['id'],'name':'Wingate','family':'wingate15','custom_fields':FIELDS,'custom_values':{'repetitions':1}})
    t=post('anaerobic/tests',{'athlete_id':a['id'],'protocol_id':p['id'],'date':'2026-10-01','manual':{'peak_w':800},'settings':{'custom_values':{'completed':False}}})
    assert t['analysis']['custom_values']['completed'] is False

def test_custom_file_observation_and_cross_society_guard(tmp_path):
    c,post,org,a=client(tmp_path)
    p=post('custom/protocols',{'organization_id':org['id'],'name':'Osservazioni','family':'OBS','version':'1','custom_fields':FIELDS})
    r=c.post('/api/v1/traces',files={'file':('trace.csv','t,power,hr\n0,100,90\n1,200,91\n2,300,93\n','text/csv')});assert r.status_code==200,r.text
    t=post('custom/tests',{'athlete_id':a['id'],'protocol_id':p['id'],'date':'2026-10-01','trace_hash':r.json()['hash']})
    assert t['samples'] and t['analysis']['source']=='trace-observations'
    assert t['analysis']['custom_values']=={}
    other=post('organizations',{'name':'Altro club'});b=post('athletes',{'organization_id':other['id'],'name':'B','surname':'Demo'})
    assert c.post('/api/v1/custom/tests',json={'athlete_id':b['id'],'protocol_id':p['id'],'date':'2026-10-01','notes':'Osservazione'}).status_code==422


def test_revision_preview_keeps_archived_references(tmp_path):
    c,post,org,a=client(tmp_path)
    p=post('custom/protocols',{'organization_id':org['id'],'name':'Custom','family':'CUSTOM','version':'1','custom_fields':FIELDS})
    payload={'athlete_id':a['id'],'protocol_id':p['id'],'date':'2026-10-01','notes':'Osservazione'}
    t=post('custom/tests',payload)
    r=c.post('/api/v1/records/'+p['id']+'/status',json={'status':'archived','base':p['revision']})
    assert r.status_code==200,r.text
    correction={**payload,'revision':t['revision'],'reason':'Correzione note'}
    assert c.post('/api/v1/custom/preview',json=correction).status_code==200
    assert c.post('/api/v1/custom/tests',json=payload).status_code==422
    assert c.put('/api/v1/custom/tests/'+t['id'],json=correction).status_code==200


@pytest.mark.parametrize('kind', ['sprint', 'wingate15', 'wingate30'])
def test_anaerobic_editable_code_preserves_method_and_revisions(tmp_path, kind):
    c,post,org,a=client(tmp_path)
    base={'organization_id':org['id'],'name':'Protocollo sintetico','family':kind,'version':'1'}
    legacy=post('anaerobic/protocols',base)
    assert legacy['family']==legacy['test_type']==kind
    data={**base,'code':' ANA-DEMO '}
    p=post('anaerobic/protocols',data)
    assert p['family']=='ANA-DEMO'
    assert p['test_type']==p['anaerobic_spec']['family']==kind
    assert p['anaerobic_spec']==legacy['anaerobic_spec']
    revised=post('anaerobic/protocols',{**data,'version':'2','parent_id':p['id'],'reason':'Revisione'})
    assert revised['family']=='ANA-DEMO' and revised['parent_id']==p['id']
    assert c.post('/api/v1/anaerobic/protocols',json={**data,'name':'Altro nome'}).status_code==422
    for code in ('', '   '):
        assert c.post('/api/v1/anaerobic/protocols',json={**data,'code':code}).status_code==422
    t=post('anaerobic/tests',{'athlete_id':a['id'],'protocol_id':p['id'],'date':'2026-10-22','manual':{'peak_w':800},'settings':{}})
    assert t['test_type']==kind and t['analysis']['peak_w']==800
