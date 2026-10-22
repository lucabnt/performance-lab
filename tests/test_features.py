import io
import zipfile
import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.zones import preset, validate, classify, calculate
from cycling_test.csv_import import decode_trace_csv
from synthetic import ERG, fit_bytes


@pytest.mark.parametrize('channel,values,expected',[
    ('hr',[80.999,81,89.999,90,99.999,100,105,105.001],[0,1,1,2,2,3,3,4]),
    ('power',[55,55.001,75,75.001,90,90.001,105,105.001],[0,1,1,2,2,3,3,4])])
def test_exact_zone_boundaries(channel,values,expected):
    assert [classify(v,100,preset(channel)) for v in values]==expected


@pytest.mark.parametrize('n',[3,5,7])
def test_dynamic_zones_gap_duration(n):
    s={'channel':'power','reference':'threshold_w','name':'Custom','version':'1','zones':[{'name':str(i),'upper':(i+1)*20 if i<n-1 else None,'inclusive':True} for i in range(n)]}
    validate(s)
    r=calculate(s,100,[{'t':0,'power':10},{'t':2,'power':40},{'t':20,'power':None},{'t':21,'power':20}],0,21)
    assert sum(z['seconds'] for z in r['zones'])==2
    assert r['unclassified_s']==19
    s['zones'][0]['upper']=999
    with pytest.raises(ValueError):validate(s)


def client(tmp_path):
    c=TestClient(create_app(tmp_path,token='test'));c.headers['X-Fuorigiri-Token']='test'
    return c


def post(c,path,data):
    r=c.post('/api/v1/'+path,json=data);assert r.status_code==200,r.text
    return r.json()


def test_revision_manual_report_and_lifecycle(tmp_path):
    c=client(tmp_path)
    org=post(c,'organizations',{'name':'Demo'})
    a=post(c,'athletes',{'organization_id':org['id'],'name':'A','surname':'B','birth_date':'2010-03-01'})
    assert a['birth_year']==2010
    p=post(c,'protocols/manual',{'name':'P','family':'P','version':'1','segments':[{'duration_s':600,'start_w':60,'end_w':60,'phase':'warmup'},{'duration_s':240,'start_w':80,'end_w':80}]})
    r=c.post('/api/v1/traces',files={'file':('x.fit',fit_bytes())});assert r.status_code==200
    body={'athlete_id':a['id'],'protocol_id':p['id'],'trace_hash':r.json()['hash'],'date':'2026-01-01','settings':{'end_s':840,'weight_kg':50,'threshold_coefficient':.8,'fthr_bpm':180,'rpe':7,'recovery_manual':[{'after_s':90,'hr_bpm':130}]}}
    t=post(c,'tests',body)
    assert t['analysis']['threshold_w']==64
    assert t['analysis']['recovery'][1]['source']=='manuale'
    first=c.get(f"/api/v1/tests/{t['id']}/report/md").content
    body['settings']['rpe']=9
    r=c.put(f"/api/v1/tests/{t['id']}",json={'base':t['revision'],'reason':'RPE corretto','test':body});assert r.status_code==200,r.text
    assert r.json()['revision']!=t['revision']
    assert len(c.get(f"/api/v1/records/{t['id']}/revisions").json())==2
    assert c.put(f"/api/v1/tests/{t['id']}",json={'base':t['revision'],'reason':'Stale','test':body}).status_code==409
    with zipfile.ZipFile(io.BytesIO(first)) as z:
        assert 'RPE (CR10 dichiarata): 7' in z.read('report.md').decode()
    post(c,f"records/{a['id']}/status",{'base':a['revision'],'status':'deleted'})
    assert not c.get(f"/api/v1/history/{org['id']}").json()['rows']


def test_csv_preview_atomic_duplicate_history(tmp_path):
    c=client(tmp_path);org=post(c,'organizations',{'name':'Demo'})
    raw=b'atleta_id,cognome,nome,anno_nascita\nx,Demo,Uno,2011\n'
    def preview(profile,raw):
        r=c.post('/api/v1/import/preview',data={'organization_id':org['id'],'profile':profile},files={'file':('data.csv',raw)})
        assert r.status_code==200,r.text
        return r.json()
    def commit(profile,p):return post(c,'import/commit',{'organization_id':org['id'],'profile':profile,'staged_hash':p['staged_hash']})
    p=preview('atleti',raw);assert p['ready']==1;commit('atleti',p)
    assert preview('atleti',raw)['skipped']==1
    p=preview('antropometria',b'atleta_id,data,peso_kg\nx,2026-01-01,50\nx,2026-02-01,-5\n')
    assert len(p['errors'])==1
    r=c.post('/api/v1/import/commit',json={'organization_id':org['id'],'profile':'antropometria','staged_hash':p['staged_hash']})
    assert r.status_code==422
    assert c.get('/api/v1/state').json()['measurement']==[]
    raw=b'test_id,atleta_id,data,protocollo_id,map_w,peso_kg,soglia_w,soglia_origine\nt1,x,2026-01-01,OLD,200,50,160,stimata_da_map\nt2,x,2026-02-01,OLD,220,50,176,stimata_da_map\n'
    commit('test_aerobico',preview('test_aerobico',raw))
    result=c.get(f"/api/v1/history/{org['id']}").json()
    assert result['groups'][0]['metrics']['map_w']['median']==220
    result=c.get(f"/api/v1/history/{org['id']}?mode=tests").json()
    assert result['groups'][0]['metrics']['map_w']['median']==210
    assert c.get(f"/api/v1/history/{org['id']}/report/pdf").content.startswith(b'%PDF')
    assert c.get(f"/api/v1/export/{org['id']}").status_code==200
    historical=c.get('/api/v1/state').json()['test'][0]
    revised=c.put(f"/api/v1/tests/{historical['id']}/historical",json={'base':historical['revision'],'reason':'Correzione del referto','date':historical['date'],
                  'map_w':230,'map_alt_w':None,'settings':{'weight_kg':50,'threshold_w':184,'fthr_bpm':180,'rpe':8},'notes':'Aggiornato'})
    assert revised.status_code==200,revised.text
    assert revised.json()['analysis']['map_wkg']==4.6
    md=c.get(f"/api/v1/tests/{historical['id']}/report/md?language=en")
    with zipfile.ZipFile(io.BytesIO(md.content)) as z:
        text=z.read('report.md').decode()
        assert 'Incremental test report' in text and 'Sviluppato da Luca Bontempi' in text
        assert 'assets/logo.png' in z.namelist()


def test_athlete_csv_preview_preserves_identity_and_birth_metadata(tmp_path):
    c=client(tmp_path);org=post(c,'organizations',{'name':'Demo'})
    raw=b'atleta_id,cognome,nome,anno_nascita,anno_nascita_confermato,origine_anno_nascita,sesso,attivo,note\na,Demo,Uno,2012,si,referto,M,si,Nota\nb,Esempio,Due,2011,no,categoria,F,no,\n'
    response=c.post('/api/v1/import/preview',data={'organization_id':org['id'],'profile':'atleti'},files={'file':('data.csv',raw)})
    assert response.status_code==200,response.text
    p=response.json()
    assert p['errors']==[] and p['ready']==2
    first,second=p['preview']
    assert (first['surname'],first['name'],first['birth_year'],first['birth_confirmed'],first['birth_source'],first['sex'],first['status'],first['notes'])==('Demo','Uno',2012,True,'referto','M','active','Nota')
    assert second['birth_confirmed'] is False and second['status']=='archived'
    assert c.get('/api/v1/state').json()['athlete']==[]
    post(c,'import/commit',{'organization_id':org['id'],'profile':'atleti','staged_hash':p['staged_hash']})
    athletes=c.get('/api/v1/state').json()['athlete']
    for row in p['preview']:
        saved=next(a for a in athletes if a['external_id']==row['external_id'])
        for key in ('surname','name','birth_year','birth_confirmed','birth_source','sex','status','notes'):
            assert saved[key]==row[key]


def test_measurement_csv_preview_commit_export_and_revision_preserve_provenance(tmp_path):
    import csv
    c=client(tmp_path);org=post(c,'organizations',{'name':'Demo'})
    a=post(c,'athletes',{'organization_id':org['id'],'surname':'Demo','name':'Uno'})
    raw=('atleta_id,data,peso_kg,statura_cm,peso_fonte,origine\n'+''.join(f"{a['id']},2026-01-{i:02d},50,160,{source},da test\n" for i,source in enumerate(['misurato','arrotondato','dichiarato','derivato','stimato',''],1))).encode()
    def preview(raw):
        r=c.post('/api/v1/import/preview',data={'organization_id':org['id'],'profile':'antropometria'},files={'file':('data.csv',raw)})
        assert r.status_code==200,r.text
        return r.json()
    p=preview(raw)
    assert p['errors']==[] and p['ready']==6
    for row,source in zip(p['preview'],['misurato','arrotondato','dichiarato','derivato','stimato','dichiarato']):
        assert (row['athlete_name'],row['athlete_external_id'],row['weight_kg'],row['height_cm'],row['source'],row['origin'])==('Demo Uno',a['id'],50,160,source,'da test')
    post(c,'import/commit',{'organization_id':org['id'],'profile':'antropometria','staged_hash':p['staged_hash']})
    assert preview(raw)['skipped']==6
    measurements=c.get('/api/v1/state').json()['measurement']
    derived=next(m for m in measurements if m['source']=='derivato')
    from cycling_test.maturation import anthropometric
    from cycling_test.api import Measurement
    assert anthropometric(a,derived)['models']['moore']['value'] is None
    payload={k:v for k,v in derived.items() if k in Measurement.model_fields}
    revised=c.put('/api/v1/measurements/'+derived['id'],json={'base':derived['revision'],'reason':'Verifica nota','measurement':{**payload,'notes':'Corretta'}})
    assert revised.status_code==200,revised.text
    assert revised.json()['source']=='derivato' and revised.json()['origin']=='da test'
    with zipfile.ZipFile(io.BytesIO(c.get('/api/v1/export/'+org['id']).content)) as z:
        rows=list(csv.DictReader(io.StringIO(z.read('antropometria.csv').decode())))
    assert next(r for r in rows if r['data']=='2026-01-04')['peso_fonte']=='derivato'
    assert all(r['origine']=='da test' for r in rows)
    bad=preview(raw.replace(b'misurato',b'sconosciuto'))
    assert len(bad['errors'])==1


def test_trace_csv_units_and_timestamps():
    assert decode_trace_csv(b't,power,hr\n0,100,120\n1,110,121\n')['samples'][1]['power']==110
    with pytest.raises(ValueError):decode_trace_csv(b't,power\n0,100\n0,120\n')


def test_growth_paired_and_fixed_branding(tmp_path):
    from cycling_test.store import Store
    from cycling_test.history import growth,paired_comparison
    from cycling_test.branding import ATTRIBUTION,logo_path
    s=Store(tmp_path);org=s.save('organization',{'name':'Generic Club'})
    a=s.save('athlete',{'organization_id':org['id'],'name':'A','surname':'Demo','birth_year':2011})
    for day,weight,height in [('2025-01-01',50,160),('2026-01-01',55,165)]:
        s.save('measurement',{'athlete_id':a['id'],'date':day,'weight_kg':weight,'height_cm':height,'source':'misurato'})
        s.save('test',{'organization_id':org['id'],'athlete_id':a['id'],'protocol_id':'same','date':day,'analysis':{'map_w':weight*4,'threshold_source':'stimata_da_map'},'settings':{'weight_kg':weight},'group_ids':[]})
    g=growth(s,org['id']);assert g[0]['days']==365;assert g[0]['delta']==5
    comparison=paired_comparison(s,org['id'],'2025','2026')
    assert comparison['n_pairs']==1 and comparison['pairs'][0]['map_w_delta']==20
    c=client(tmp_path)
    assert c.post('/api/v1/organizations',json={'name':'X','logo':'other.png'}).status_code==422
    assert logo_path().read_bytes().startswith(b'\x89PNG')
    assert ATTRIBUTION=='Sviluppato da Luca Bontempi per Progetto Ciclismo - Rodengo Saiano A.S.D.'


def test_import_templates_are_header_only_and_use_canonical_columns(tmp_path):
    import csv
    from cycling_test.csv_import import import_columns
    c=client(tmp_path);org=post(c,'organizations',{'name':'Demo'})
    for profile in ('atleti','antropometria','test_aerobico','test_anaerobico'):
        response=c.get('/api/v1/import/template/'+profile)
        assert response.status_code==200,response.text
        rows=list(csv.reader(io.StringIO(response.content.decode('utf-8-sig'))))
        assert rows==[import_columns(profile)]
        assert '.csv' in response.headers['content-disposition']
        assert len(set(rows[0]))==len(rows[0])
        empty=c.post('/api/v1/import/preview',data={'organization_id':org['id'],'profile':profile},files={'file':('empty.csv',response.content)})
        assert empty.status_code==200,empty.text
        assert empty.json()['rows']==0 and empty.json()['ready_rows']==0 and empty.json()['errors']==[]
    assert c.get('/api/v1/import/template/unknown').status_code==422


def test_test_import_preview_separates_protocols_and_shows_athletes_and_results(tmp_path):
    c=client(tmp_path);org=post(c,'organizations',{'name':'Demo'})
    a=post(c,'athletes',{'organization_id':org['id'],'surname':'Demo','name':'Uno'})
    raw=('test_id,atleta_id,data,protocollo_id,map_w,soglia_w,fc_max_test_bpm\n'+''.join(f"A{i},{a['id']},2026-01-01,DEMO-AER,200,160,190\n" for i in range(21))).encode()
    response=c.post('/api/v1/import/preview',data={'organization_id':org['id'],'profile':'test_aerobico'},files={'file':('a.csv',raw)})
    assert response.status_code==200,response.text
    p=response.json()
    assert not p['errors'] and p['ready_rows']==21 and p['ready']==22
    assert p['new_protocols']==[{'code':'DEMO-AER','name':'DEMO-AER'}]
    assert len(p['preview'])==20 and all(r['kind']=='test' for r in p['preview'])
    assert all((r['athlete_name'],r['athlete_external_id'],r['protocol_code'],r['analysis']['map_w'])==('Demo Uno',a['id'],'DEMO-AER',200) for r in p['preview'])
    post(c,'import/commit',{'organization_id':org['id'],'profile':'test_aerobico','staged_hash':p['staged_hash']})
    state=c.get('/api/v1/state').json()
    assert len(state['test'])==21 and len(state['protocol'])==1


def test_general_anaerobic_csv_templates_support_all_families_and_legacy(tmp_path):
    import csv
    from cycling_test.csv_import import template_csv
    c=client(tmp_path);org=post(c,'organizations',{'name':'Demo'})
    a=post(c,'athletes',{'organization_id':org['id'],'surname':'Demo','name':'Uno'})
    fields=next(csv.reader(io.StringIO(template_csv('test_anaerobico').decode('utf-8-sig'))))
    out=io.StringIO();writer=csv.DictWriter(out,fieldnames=fields);writer.writeheader()
    for i,(kind,duration) in enumerate([('sprint',6),('wingate15',15),('wingate30',30)]):
        writer.writerow({'test_id':f'T{i}','atleta_id':a['id'],'data':'2026-01-01','protocollo_id':f'DEMO-{kind}','tipo_test':kind,'durata_s':duration,'picco_w':800,'media_w':600})
    writer.writerow({'test_id':'LEGACY','atleta_id':a['id'],'data':'2026-01-01','protocollo_id':'ANA-15-070','picco_w':750})
    def preview(raw):
        response=c.post('/api/v1/import/preview',data={'organization_id':org['id'],'profile':'test_anaerobico'},files={'file':('a.csv',raw)})
        assert response.status_code==200,response.text
        return response.json()
    raw=out.getvalue().encode();p=preview(raw)
    assert not p['errors'] and p['ready_rows']==4 and len(p['new_protocols'])==4
    assert [r['test_type'] for r in p['preview']]==['sprint','wingate15','wingate30','wingate15']
    assert [r['analysis']['duration_s'] for r in p['preview']]==[6,15,30,15]
    assert all(r['athlete_name']=='Demo Uno' and r['analysis']['peak_w'] for r in p['preview'])
    post(c,'import/commit',{'organization_id':org['id'],'profile':'test_anaerobico','staged_hash':p['staged_hash']})
    assert preview(raw)['skipped']==4
    assert len(c.get('/api/v1/state').json()['test'])==4
    # Conflicting explicit legacy metadata must not be silently overridden.
    out=io.StringIO();writer=csv.DictWriter(out,fieldnames=fields);writer.writeheader()
    writer.writerow({'test_id':'CONFLICT','atleta_id':a['id'],'data':'2026-01-01','protocollo_id':'ANA-15-070','tipo_test':'wingate30','durata_s':30})
    assert len(preview(out.getvalue().encode())['errors'])==1
    response=c.post('/api/v1/import/preview',data={'organization_id':org['id'],'profile':'test_anaerobico'},files={'file':('a.csv',b'test_id,atleta_id\n')})
    assert response.status_code==422
