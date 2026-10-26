from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.store import Store
from cycling_test.training_zones import for_test,profile
from cycling_test.zones import preset


def seed(root):
    store=Store(root)
    org=store.save('organization',{'name':'Club QA'})
    a=store.save('athlete',{'organization_id':org['id'],'name':'Ada','surname':'Esempio'})
    p=store.save('protocol',{'organization_id':org['id'],'name':'Storico QA','family':'QA','version':'1','definition':{'segments':[],'points':[]}})
    def test(date,hr=180,power=200,**extra):
        return store.save('test',{'organization_id':org['id'],'athlete_id':a['id'],'protocol_id':p['id'],'date':date,
            'historical':True,'settings':{},'analysis':{'map_w':250,'threshold_w':power,'fthr_bpm':hr,'zones':[]},**extra})
    c=TestClient(create_app(root,token='qa'));c.headers['X-Fuorigiri-Token']='qa'
    return store,a,test,c


def test_legacy_bounds_from_saved_references_without_rewrite_or_fake_time(tmp_path):
    store,a,make,c=seed(tmp_path);t=make('2026-01-01')
    before=deepcopy(t)
    r=c.get('/api/v1/tests/'+t['id']+'/zones');assert r.status_code==200
    hr,power=r.json()['zones']
    assert hr['zones'][0]['upper_value']==145.8
    assert power['zones'][0]['upper_value']==110
    assert all(z['seconds'] is None for s in (hr,power) for z in s['zones'])
    assert hr['unclassified_s'] is None
    assert store.get(t['id'])==before
    missing=make('2026-01-02',hr=None,power=None)
    assert all(z['zones']==[] for z in for_test(missing)) # MAP alone is not threshold/FTHR.


def test_preserves_saved_schemes_bounds_and_timing(tmp_path):
    _,_,make,_=seed(tmp_path);t=make('2026-01-01')
    saved=for_test(t)
    saved[0]['zones'][0]['upper_value']=123
    saved[0]['zones'][0]['seconds']=17
    t['analysis']['zones']=deepcopy(saved)
    t['analysis']['fthr_bpm']=200
    assert for_test(t)[0]['zones'][0]['upper_value']==123
    assert for_test(t)[0]['zones'][0]['seconds']==17


def test_profile_latest_per_channel_ignores_deleted_and_anaerobic(tmp_path):
    store,a,make,c=seed(tmp_path)
    older=make('2026-01-01',hr=175,power=180)
    newer=make('2026-02-01',hr=None,power=220)
    make('2026-03-01',status='deleted')
    from cycling_test.anaerobic import FAMILIES
    make('2026-04-01',test_type=next(iter(FAMILIES)))
    result=c.get('/api/v1/athletes/'+a['id']+'/training-zones').json()
    assert result['mode']=='latest'
    assert [z['test_id'] for z in result['zones']]==[older['id'],newer['id']]
    assert len(result['available_tests'])==2


def test_adopted_snapshot_custom_choice_and_name_edits_preserve_zones(tmp_path):
    store,a,make,c=seed(tmp_path);t=make('2026-01-01')
    path='/api/v1/athletes/'+a['id']+'/training-zones'
    r=c.put(path,json={'base':a['revision'],'mode':'test','test_id':t['id'],'test_revision':t['revision']})
    assert r.status_code==200
    zones=r.json()['zones'];saved_a=store.get(a['id'])
    store.save('test',{**t,'analysis':{**t['analysis'],'threshold_w':300}},t['id'],t['revision'])
    assert c.get(path).json()['zones']==zones
    # A stale source revision cannot be adopted, nor can an old athlete base.
    assert c.put(path,json={'base':saved_a['revision'],'mode':'test','test_id':t['id'],'test_revision':t['revision']}).status_code==409
    assert c.put(path,json={'base':a['revision'],'mode':'latest'}).status_code==409
    schemes=[preset('hr'),preset('power')];schemes[1]['zones'][0]['upper']=60
    r=c.put(path,json={'base':saved_a['revision'],'mode':'custom','schemes':schemes,'references':{'fthr_bpm':170,'threshold_w':250}})
    assert r.status_code==200 and r.json()['zones'][1]['zones'][0]['upper_value']==150
    latest=store.get(a['id'])
    payload={'organization_id':a['organization_id'],'name':'Nuovo nome','surname':a['surname']}
    assert c.put('/api/v1/athletes/'+a['id']+'?base='+latest['revision'],json=payload).status_code==200
    assert c.get(path).json()['mode']=='custom'
    assert store.get(t['id'])['analysis']['threshold_w']==300
    assert len(store.history(a['id']))==4


@pytest.mark.parametrize('refs',[{'fthr_bpm':0,'threshold_w':200},{'fthr_bpm':251,'threshold_w':200},{'fthr_bpm':180},{'fthr_bpm':180,'threshold_w':-2}])
def test_reject_invalid_custom_references(tmp_path,refs):
    store,a,_,c=seed(tmp_path)
    assert c.put('/api/v1/athletes/'+a['id']+'/training-zones',json={'base':a['revision'],'mode':'custom','schemes':[preset('hr'),preset('power')],'references':refs}).status_code==422
    assert store.get(a['id'])==a


def test_cross_athlete_and_custom_test_rejected(tmp_path):
    store,a,make,c=seed(tmp_path)
    other=store.save('athlete',{'organization_id':a['organization_id'],'name':'Altra','surname':'Persona'})
    t=make('2026-01-01',athlete_id=other['id'])
    path='/api/v1/athletes/'+a['id']+'/training-zones'
    assert c.put(path,json={'base':a['revision'],'mode':'test','test_id':t['id'],'test_revision':t['revision']}).status_code==422
    custom=make('2026-01-01',test_type='custom')
    assert c.get('/api/v1/tests/'+custom['id']+'/zones').status_code==422


def test_profile_selection_syncs_and_viewer_cannot_change_it(tmp_path):
    from cycling_test.workspaces import Workspaces,invitation,join
    from cycling_test.sync import exchange
    owner=Workspaces(tmp_path/'owner',Store(tmp_path/'owner'));entry=owner.create('Club','Founder')
    source=owner.get(entry['id'])
    athlete=source.save('athlete',{'organization_id':entry['organization_id'],'name':'Ada','surname':'Esempio'})
    owner_client=TestClient(create_app(owner.root,token='owner'))
    owner_client.headers.update({'X-Fuorigiri-Token':'owner','X-Fuorigiri-Workspace':entry['id']})
    response=owner_client.put('/api/v1/athletes/'+athlete['id']+'/training-zones',json={'base':athlete['revision'],'mode':'custom',
        'schemes':[preset('hr'),preset('power')],'references':{'fthr_bpm':180,'threshold_w':200}})
    assert response.status_code==200
    athlete=source.get(athlete['id'])
    viewer=Workspaces(tmp_path/'viewer',Store(tmp_path/'viewer'))
    joined=join(viewer,invitation(source,'Reader','viewer','test-password-long'),'test-password-long')
    folder=tmp_path/'cloud';folder.mkdir()
    exchange(source,folder,source.identity['sync_key'])
    target=viewer.get(joined['id']);exchange(target,folder,target.identity['sync_key'])
    c=TestClient(create_app(viewer.root,token='qa'));c.headers.update({'X-Fuorigiri-Token':'qa','X-Fuorigiri-Workspace':joined['id']})
    path='/api/v1/athletes/'+athlete['id']+'/training-zones'
    assert c.get(path).json()['selection']==athlete['training_zone_selection']
    assert c.put(path,json={'base':athlete['revision'],'mode':'latest'}).status_code==403
