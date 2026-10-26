import io
import json
import zipfile
from pathlib import Path
import pytest
from test_features import client, post


def test_catalog_protocol_manual_test_and_export(tmp_path):
    c=client(tmp_path);org=post(c,'organizations',{'name':'Demo'})
    parent=post(c,'groups',{'organization_id':org['id'],'name':'Allievi'})
    child=post(c,'groups',{'organization_id':org['id'],'parent_id':parent['id'],'season':'2027'})
    assert child['name']=='Allievi'
    assert c.post('/api/v1/groups',json={'organization_id':org['id']}).status_code==422
    athlete=post(c,'athletes',{'organization_id':org['id'],'name':'Demo','surname':'Manuale'})
    protocol=post(c,'protocols/manual',{'name':'Protocollo storico','family':'CATALOGO','version':'1'})
    assert protocol['definition']['segments']==[]
    assert c.get(f"/api/v1/protocols/{protocol['id']}/erg").status_code==422
    test=post(c,'manual-tests',{'athlete_id':athlete['id'],'protocol_id':protocol['id'],'date':'2026-10-17',
        'map_w':250,'fc_max_test_bpm':190,'settings':{'weight_kg':50,'threshold_coefficient':.8,'fthr_bpm':180,'recovery_manual':[{'after_s':60,'hr_bpm':130}]}})
    assert test['analysis']['map_wkg']==5 and test['analysis']['threshold_w']==200
    assert test['historical'] and test['samples']==[] and test['analysis']['power_coverage'] is None
    assert test['analysis']['zones'][0]['zones'][0]['seconds'] is None
    assert test['analysis']['recovery'][0]['hr_bpm']==130
    updated=c.put(f"/api/v1/tests/{test['id']}/historical",json={'base':test['revision'],'reason':'FC corretta','date':test['date'],
        'map_w':250,'fc_max_test_bpm':188,'settings':test['settings']})
    assert updated.status_code==200 and updated.json()['analysis']['fc_max_test_bpm']==188
    assert updated.json()['analysis']['recovery'][0]['hr_bpm']==130
    settings={**updated.json()['settings'],'threshold_coefficient':.75,'threshold_w':None}
    recalculated=c.put(f"/api/v1/tests/{test['id']}/historical",json={'base':updated.json()['revision'],'reason':'Nuovo coefficiente esplicito','date':test['date'],
        'map_w':250,'settings':settings})
    assert recalculated.status_code==200
    assert recalculated.json()['analysis']['threshold_w']==187.5
    assert recalculated.json()['analysis']['threshold_source']=='stimata_da_map'
    assert test['analysis']['threshold_w']==200
    assert c.get(f"/api/v1/tests/{test['id']}/report/pdf").content.startswith(b'%PDF')
    with zipfile.ZipFile(io.BytesIO(c.get(f"/api/v1/export/{org['id']}").content)) as z:
        assert ',187.5,0.75,stimata_da_map,' in z.read('test_aerobico.csv').decode()
    for value in (-1,3001):
        assert c.post('/api/v1/manual-tests',json={'athlete_id':athlete['id'],'protocol_id':protocol['id'],'date':'2026-10-17','map_w':value,'settings':{}}).status_code==422


def test_csv_required_optional_and_statistics(tmp_path):
    c=client(tmp_path);org=post(c,'organizations',{'name':'Demo'})
    def upload(profile,text):
        return c.post('/api/v1/import/preview',data={'organization_id':org['id'],'profile':profile},files={'file':('data.csv',text)})
    assert upload('antropometria','atleta_id,peso_kg\nx,50\n').status_code==422
    p=upload('atleti','atleta_id,cognome,nome\nx,Demo,Uno\n').json()
    post(c,'import/commit',{'organization_id':org['id'],'profile':'atleti','staged_hash':p['staged_hash']})
    assert not upload('antropometria','atleta_id;data;statura_cm\nx;2026-10-17;165\n').json()['errors']
    p=upload('test_aerobico','test_id,atleta_id,data,protocollo_id,map_w\na,x,2026-01-01,P,100\nb,x,2026-02-01,P,100\nc,x,2026-03-01,P,400\n').json()
    post(c,'import/commit',{'organization_id':org['id'],'profile':'test_aerobico','staged_hash':p['staged_hash']})
    result=c.get(f"/api/v1/history/{org['id']}?mode=tests&dimension=all").json()
    assert result['groups'][0]['metrics']['map_w']['mean']==200
    assert result['groups'][0]['metrics']['map_w']['median']==100
    report=c.get(f"/api/v1/history/{org['id']}/report/md?mode=tests&dimension=all&metric=map_w&statistic=mean")
    with zipfile.ZipFile(io.BytesIO(report.content)) as z:
        manifest=json.loads(z.read('manifest.json'))
        assert manifest['query']['statistic']=='mean'
    assert c.get(f"/api/v1/history/{org['id']}/report/pdf?metric=bad").status_code==422


def test_csv_preserves_explicit_threshold_coefficient_without_recalculating(tmp_path):
    from cycling_test.csv_import import plan_import
    from cycling_test.store import Store
    store=Store(tmp_path)
    org=store.save('organization',{'name':'Demo'})
    store.save('athlete',{'organization_id':org['id'],'external_id':'x','name':'Ada','surname':'Demo'})
    content=b'test_id;atleta_id;data;protocollo_id;map_w;soglia_w;soglia_origine;coeff_soglia\na;x;2026-01-01;P;176;141;stimata_da_map;0,8\n'
    result=plan_import(store,org['id'],'test_aerobico',content)
    assert not result['errors']
    record=next(value for kind,value in result['entries'] if kind=='test')
    assert record['settings']['threshold_coefficient']==.8
    assert record['analysis']['threshold_w']==141
    assert record['historical_fields']['coeff_soglia']=='0,8'
    invalid=plan_import(store,org['id'],'test_aerobico',content.replace(b'0,8',b'3'))
    assert invalid['errors']


@pytest.mark.parametrize('index',range(4))
def test_original_erg_realistic_simulated_fit(index):
    from cycling_test.fit import decode_fit
    from cycling_test.erg import parse_erg
    from cycling_test.analysis import analyze
    root=Path(__file__).resolve().parents[1]/'examples'
    item=json.loads((root/'synthetic/manifest.json').read_text(encoding='utf-8'))[index]
    decoded=decode_fit((root/'synthetic'/item['file']).read_bytes())
    definition=parse_erg((root/'protocols'/f"{item['protocol']}.erg").read_text(encoding='utf-8-sig'))
    for s in definition['segments']:s['phase']='warmup' if s['end_s']<=600 else 'increment'
    result=analyze(decoded['samples'],definition,{'offset_s':0,'end_s':item['effort_end_s'],'weight_kg':item['weight_kg']})
    assert result['map_w']==item['expected_map_w']
    assert result['power_coverage']>=.99
    assert result['recovery'][0]['hr_bpm'] is not None
    assert decoded['samples'][-1]['t']==item['recording_end_s']
