from copy import deepcopy
from datetime import date,timedelta
import csv,io,json,zipfile
import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.maturation import analyze,anthropometric,height_velocity,MeasurementPayload


def athlete(**extra):
    return {'id':'a','revision':'ar1','organization_id':'o','name':'Demo','surname':'Crescita','sex':'M','birth_date':'2010-01-01',**extra}


def measurement(when='2024-01-01',**extra):
    return {'id':'m'+when,'revision':'r'+when,'athlete_id':'a','date':when,'source':'misurato','height_cm':170,'weight_kg':55,**extra}


def curve():
    origin=date(2024,1,1);rows=[]
    for d in range(-720,721,180):
        t=d/365.25;rows.append(measurement((origin+timedelta(days=d)).isoformat(),height_cm=160+9*t-2*t**3/3))
    return rows


def test_independent_offset_oracles_and_optional_ratios():
    # 2010-01-01 -> 2024-01-01 is 5113 days. Hand evaluated equations.
    r=anthropometric(athlete(),measurement(sitting_height_cm=88,arm_span_cm=174,lower_limb_cm=85,adult_height_cm=180,adult_height_method='Valutazione esterna',adult_height_source='Referto demo'))
    assert r['models']['moore']['value']==pytest.approx(.596677331964407939767282684)
    age=5113/365.25
    assert r['models']['mirwald']['value']==pytest.approx(-9.236+.0002708*82*88-.001663*age*82+.007216*age*88+.02292*55/170*100)
    assert r['models']['moore']['aphv_years']==pytest.approx(age-r['models']['moore']['value'])
    assert r['optional']['pah']['value']==pytest.approx(94.44444444444444)
    assert r['optional']['residual']['value']==10
    assert r['optional']['lower_limb_pct']['value']==50


def test_female_equation_and_no_sex_inference():
    r=anthropometric(athlete(sex='F'),measurement('2022-01-01'))
    assert r['models']['moore']['value']==pytest.approx(-7.709133+.0042232*(4383/365.25)*170)
    assert anthropometric(athlete(sex=''),measurement())['models']['moore']['value'] is None
    assert anthropometric(athlete(sex=''),measurement(model_sex='M'))['models']['moore']['value'] is not None


@pytest.mark.parametrize('a,m',[({'birth_date':None},{}),({'birth_date':'2025-01-01'},{}),({'birth_date':'1990-01-01'},{}),({}, {'source':'dichiarato'}),({}, {'quality':'uncertain'}),({}, {'quality':'excluded'}),({}, {'height_cm':None})])
def test_unavailable_is_not_zero(a,m):
    r=anthropometric(athlete(**a),measurement(**m))
    assert r['models']['moore']['value'] is None
    assert r['models']['moore']['reason']


def test_missing_seated_height_does_not_invent_it():
    r=anthropometric(athlete(),measurement())
    assert r['models']['moore']['value'] is not None
    assert r['models']['mirwald']['value'] is None
    assert r['optional']['pah']['value'] is None
    excluded=anthropometric(athlete(),measurement(quality='excluded',adult_height_cm=180,arm_span_cm=170))
    assert excluded['optional']['pah']['value'] is None and excluded['optional']['arm_span_pct']['value'] is None


@pytest.mark.parametrize('days,delta,valid',[(180,3,True),(180,0,True),(0,0,False),(30,.5,False),(500,4,False),(180,-1,False),(180,15,False)])
def test_hv_guards_and_zero(days,delta,valid):
    a=measurement('2023-01-01',height_cm=160)
    b=measurement((date(2023,1,1)+timedelta(days=days)).isoformat(),id='b',height_cm=160+delta)
    r=height_velocity([a,b])[0]
    assert (r['value'] is not None)==valid
    if valid:assert r['value']==pytest.approx(delta*365.25/days)


def test_longitudinal_peak_known_cubic_and_missing_edges():
    rows=curve();r=analyze(athlete(),rows,'2026-01-01')
    assert r['phv']['value']==pytest.approx(9-(180/365.25)**2/6)
    assert r['phv']['date']=='2024-01-01'
    assert r['phv']['rmse_cm_year']<1e-10
    assert analyze(athlete(),rows[:5],'2026-01-01')['phv']['value'] is None
    rows[-1]['height_cm']=rows[-2]['height_cm']-1
    assert analyze(athlete(),rows,'2026-01-01')['phv']['value'] is None


def test_validation_external_prediction_and_measurement_only_advanced():
    with pytest.raises(ValueError):MeasurementPayload(athlete_id='a',date='2024-01-01',adult_height_cm=180)
    with pytest.raises(ValueError):MeasurementPayload(athlete_id='a',date='2024-01-01',height_cm=160,sitting_height_cm=170)
    with pytest.raises(ValueError):MeasurementPayload(athlete_id='a',date='2024-01-01',height_cm=float('nan'))
    assert MeasurementPayload(athlete_id='a',date='2024-01-01',arm_span_cm=170).height_cm is None


def test_adult_stability_is_data_based_not_age_alone():
    a=athlete(birth_date='2000-01-01')
    rows=[measurement(d,height_cm=h) for d,h in [('2023-01-01',174),('2023-07-01',174.1),('2024-01-01',174.2)]]
    r=analyze(a,rows,'2024-02-01')
    assert r['stability']['value']==pytest.approx(.2)
    assert r['series'][-1]['models']['moore']['value'] is None
    assert analyze(a,rows[:1],'2024-02-01')['stability']['value'] is None
    assert r['inputs']['measurements']==rows


def test_maturation_snapshots_sync_restore_and_viewer_permissions(tmp_path):
    from cycling_test.store import Store
    from cycling_test.workspaces import Workspaces,invitation,join
    from cycling_test.sync import exchange
    from cycling_test.recovery import backup_bytes,restore
    from cycling_test.sync_service import configure,run_sync
    owner_root=tmp_path/'owner';manager=Workspaces(owner_root,Store(owner_root));entry=manager.create('Club crescita','Fondatore DEMO');owner=manager.get(entry['id'])
    with TestClient(create_app(owner_root,'test'),headers={'X-Fuorigiri-Token':'test','X-Fuorigiri-Workspace':entry['id']}) as client:
        a=client.post('/api/v1/athletes',json={'organization_id':entry['organization_id'],'name':'Demo','surname':'Replica','sex':'M','birth_date':'2010-01-01'}).json()
        for m in curve():
            data={k:v for k,v in m.items() if k not in ('id','revision')};data['athlete_id']=a['id'];assert client.post('/api/v1/measurements',json=data).status_code==200
        route='/api/v1/athletes/'+a['id']+'/maturation';preview=client.get(route+'?on=2026-01-01').json()['preview']
        r=client.post(route,json={'on':'2026-01-01','input_hash':preview['input_hash'],'reason':'Analisi da condividere'}).json()
    reader_root=tmp_path/'reader';reader_manager=Workspaces(reader_root,Store(reader_root));raw=invitation(owner,'Viewer DEMO','viewer','Password-test-1234')
    invited=join(reader_manager,raw,'Password-test-1234');reader=reader_manager.get(invited['id']);folder=tmp_path/'exchange';folder.mkdir()
    configure(owner,{'transport':'folder','folder':str(folder)});assert not run_sync(owner)['errors']
    assert not exchange(reader,folder,reader.identity['sync_key'])['errors']
    assert reader.get(r['id'])['analysis']==r['analysis']
    assert reader.read_object(r['objects'][0])==owner.read_object(r['objects'][0])
    with TestClient(create_app(reader_root,'test'),headers={'X-Fuorigiri-Token':'test','X-Fuorigiri-Workspace':invited['id']}) as client:
        assert client.get(route+'?on=2026-01-01').status_code==200
        assert client.post(route,json={'on':'2026-01-01','input_hash':preview['input_hash'],'reason':'Viewer non deve scrivere'}).status_code==403
    restore_root=tmp_path/'restored';restored_manager=Workspaces(restore_root,Store(restore_root));copy=restore(restored_manager,backup_bytes(owner),'independent',operator='Nuovo fondatore DEMO')
    assert restored_manager.get(copy['id']).get(r['id'])['analysis']==r['analysis']


def test_folder_verified_state_is_bound_to_destination(tmp_path):
    from cycling_test.store import Store
    from cycling_test.workspaces import Workspaces
    from cycling_test.sync_service import configure,run_sync
    root=tmp_path/'owner';manager=Workspaces(root,Store(root));entry=manager.create('Club','Demo');owner=manager.get(entry['id'])
    folder=tmp_path/'one';folder.mkdir();configure(owner,{'transport':'folder','folder':str(folder)})
    with TestClient(create_app(root,'test'),headers={'X-Fuorigiri-Token':'test','X-Fuorigiri-Workspace':entry['id']}) as client:
        path='/api/v1/sync/connection';assert client.get(path).json()['folder_access']=='not_verified'
        run_sync(owner);assert client.get(path).json()['folder_access']=='verified_at_last_sync'
        configure(owner,{'transport':'folder','folder':str(tmp_path/'two')})
        assert client.get(path).json()['folder_access']=='not_verified'


def test_growth_corpus_backups_and_manifest_include_added_cases(tmp_path,monkeypatch):
    import sys
    from pathlib import Path
    from cycling_test.store import Store
    from cycling_test.workspaces import Workspaces
    from cycling_test.recovery import inspect_backup
    sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
    import demo_maturation
    def minimal_base(destination,small=True):
        destination=Path(destination);destination.mkdir()
        manager=Workspaces(destination,Store(destination));entry=manager.create('Club sintetico','Fondatore DEMO')
        return {'organizations':[entry],'synthetic':True}
    monkeypatch.setattr(demo_maturation,'generate',minimal_base)
    root=tmp_path/'new';cases=demo_maturation.generate_growth(root)
    assert {r['case'] for r in cases}=={'peak','missing','adult'}
    manifest=json.loads((root/'manifest-demo.json').read_text(encoding='utf-8'))
    assert manifest['organizations'][0]['athletes']==3
    assert manifest['organizations'][0]['measurements']==15
    backup=inspect_backup((root/'backup-SOLO-DEMO.zip').read_bytes())
    assert len([r for r in backup['records'] if r.get('analysis_type')=='maturation'])==3


def test_snapshots_revisions_exports_backup_reports(tmp_path):
    from cycling_test.store import Store
    from cycling_test.recovery import backup_bytes,inspect_backup
    from cycling_test.reports import export_csv
    from cycling_test.archive_report import build,render
    app=create_app(tmp_path,'test');headers={'X-Fuorigiri-Token':'test'}
    with TestClient(app,headers=headers) as client:
        org=client.post('/api/v1/organizations',json={'name':'Crescita sintetica'}).json()
        a=client.post('/api/v1/athletes',json={'organization_id':org['id'],'name':'Demo','surname':'Crescita','sex':'M','birth_date':'2010-01-01'}).json()
        saved=[]
        for m in curve():
            payload={k:v for k,v in m.items() if k not in ('id','revision')};payload['athlete_id']=a['id']
            r=client.post('/api/v1/measurements',json=payload);assert r.status_code==200,r.text;saved.append(r.json())
        path=f'/api/v1/athletes/{a["id"]}/maturation'
        p=client.get(path+'?on=2026-01-01').json()['preview']
        snapshot=client.post(path,json={'on':'2026-01-01','input_hash':p['input_hash'],'reason':'Riferimento iniziale'});assert snapshot.status_code==200,snapshot.text
        snapshot=snapshot.json();assert snapshot['analysis']['phv']['value'] is not None
        changed={k:v for k,v in saved[0].items() if k in MeasurementPayload.model_fields};changed['height_cm']+=.2
        edit=client.put('/api/v1/measurements/'+saved[0]['id'],json={'measurement':changed,'base':saved[0]['revision'],'reason':'Precisione riletta'});assert edit.status_code==200,edit.text
        assert client.put('/api/v1/measurements/'+saved[0]['id'],json={'measurement':changed,'base':saved[0]['revision'],'reason':'Dato obsoleto'}).status_code==409
        assert client.post(path,json={'on':'2026-01-01','input_hash':p['input_hash'],'reason':'Anteprima obsoleta'}).status_code==409
        history=client.get(path+'?on=2026-01-01').json()['history'];assert history[0]['analysis']==snapshot['analysis']
        assert client.get('/api/v1/legal').json()['license'].startswith('                    GNU GENERAL PUBLIC LICENSE')
    store=Store(tmp_path);archive=build(store,org['id'],athlete=a['id'])
    assert archive['athletes'][0]['maturation'][0]['id']==snapshot['id']
    for fmt in ('md','pdf'):
        content=render(archive,fmt);assert content
        if fmt=='md':
            with zipfile.ZipFile(io.BytesIO(content)) as z:assert b'HV' in z.read('report.md')
    with zipfile.ZipFile(io.BytesIO(export_csv(store,org['id']))) as z:
        records=list(csv.DictReader(io.StringIO(z.read('extended/maturazione.csv').decode())))
        assert any(r['metric']=='phv_cm_year' and r['value'] for r in records)
        assert json.loads(z.read('extended/maturazione_snapshot.json'))[0]['analysis']==snapshot['analysis']
        assert 'precision_cm' in z.read('extended/antropometria_completa.csv').decode()
    info=inspect_backup(backup_bytes(store));assert info
