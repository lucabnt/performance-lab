"""Recoverable deletion keeps acquired data and immutable revisions intact."""
import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.store import Store
from cycling_test.workspaces import Workspaces, invitation, join
from cycling_test.sync import exchange


def post(client, path, body):
    response=client.post('/api/v1/'+path,json=body)
    assert response.status_code==200,response.text
    return response.json()


def test_measurement_delete_restore_updates_current_views_but_not_snapshots(tmp_path):
    with TestClient(create_app(tmp_path,'t'),headers={'X-Fuorigiri-Token':'t'}) as client:
        org=post(client,'organizations',{'name':'Lifecycle DEMO'})
        athlete=post(client,'athletes',{'organization_id':org['id'],'name':'Ada','surname':'DEMO','birth_date':'2013-01-01','sex':'F'})
        measurements=[post(client,'measurements',{'athlete_id':athlete['id'],'date':d,'weight_kg':w,'height_cm':h,'source':'misurato'}) for d,w,h in [('2025-01-01',40,150),('2026-01-01',45,155)]]
        first,last=measurements
        route=f"athletes/{athlete['id']}/maturation"
        before=client.get('/api/v1/'+route+'?on=2026-02-01').json()['preview']
        snapshot=post(client,route,{'on':'2026-02-01','input_hash':before['input_hash'],'reason':'Riferimento prima della cancellazione'})
        path=f"records/{last['id']}/status"
        deleted=post(client,path,{'base':last['revision'],'status':'deleted'})
        state=client.get('/api/v1/state').json()
        assert [m['id'] for m in state['measurement']]==[first['id']]
        assert [m['id'] for m in state['deleted_measurement']]==[last['id']]
        assert client.get(f"/api/v1/athletes/{athlete['id']}/defaults?on=2026-02-01").json()['measurement']['id']==first['id']
        current=client.get('/api/v1/'+route+'?on=2026-02-01').json()
        assert [m['measurement_id'] for m in current['preview']['series']]==[first['id']]
        assert current['history'][0]['analysis']==snapshot['analysis']
        assert client.post('/api/v1/'+path,json={'base':last['revision'],'status':'active'}).status_code==409
        assert client.post('/api/v1/'+path,json={'base':deleted['revision'],'status':'archived'}).status_code==422
        restored=post(client,path,{'base':deleted['revision'],'status':'active'})
        assert {k:v for k,v in restored.items() if k not in ('revision','status')}=={k:v for k,v in last.items() if k not in ('revision','status')}
        assert client.get('/api/v1/state').json()['deleted_measurement']==[]
        assert len(client.get('/api/v1/'+route+'?on=2026-02-01').json()['preview']['series'])==2
        assert len(client.get(f"/api/v1/records/{last['id']}/revisions").json())==3


@pytest.mark.parametrize('family',['incremental','historical','sprint','wingate15','wingate30','custom'])
def test_all_test_families_keep_samples_results_and_objects_on_deletion(tmp_path,family):
    store=Store(tmp_path)
    org=store.save('organization',{'name':'DEMO'})
    athlete=store.save('athlete',{'organization_id':org['id'],'name':'Ada','surname':'DEMO'})
    original_hash=store.object(b'original acquired file')
    record=store.save('test',{'organization_id':org['id'],'athlete_id':athlete['id'],'date':'2026-01-01','test_type':family,'historical':family=='historical','samples':[{'t':0,'power':100}],'analysis':{'map_w':100},'objects':[original_hash]})
    with TestClient(create_app(tmp_path,'t'),headers={'X-Fuorigiri-Token':'t'}) as client:
        path=f"records/{record['id']}/status"
        deleted=post(client,path,{'base':record['revision'],'status':'deleted'})
        assert client.get('/api/v1/state').json()['test'][0]['status']=='deleted'
        assert client.post('/api/v1/'+path,json={'base':record['revision'],'status':'active'}).status_code==409
        restored=post(client,path,{'base':deleted['revision'],'status':'active'})
        assert restored['samples']==record['samples'] and restored['analysis']==record['analysis']
        assert restored['objects']==record['objects']
        assert store.read_object(original_hash)==b'original acquired file'
        assert len(store.history(record['id']))==3


def test_signed_deletions_and_restores_sync_and_remain_read_only_for_viewer(tmp_path):
    owner=Workspaces(tmp_path/'owner',Store(tmp_path/'owner'))
    entry=owner.create('DEMO','Owner');source=owner.get(entry['id'])
    records=[source.save(kind,{'organization_id':entry['organization_id'],'date':'2026-01-01','weight_kg':45,'height_cm':155}) for kind in ('measurement','test')]
    viewer=Workspaces(tmp_path/'viewer',Store(tmp_path/'viewer'))
    joined=join(viewer,invitation(source,'Reader','viewer','long-password-123'),'long-password-123')
    target=viewer.get(joined['id']);folder=tmp_path/'cloud';folder.mkdir()
    def sync():
        exchange(source,folder,source.identity['sync_key'])
        exchange(target,folder,target.identity['sync_key'])
    sync()
    with TestClient(create_app(tmp_path/'owner','t'),headers={'X-Fuorigiri-Token':'t','X-Fuorigiri-Workspace':entry['id']}) as admin, TestClient(create_app(tmp_path/'viewer','t'),headers={'X-Fuorigiri-Token':'t','X-Fuorigiri-Workspace':joined['id']}) as reader:
        for record in records:
            path=f"records/{record['id']}/status"
            assert reader.post('/api/v1/'+path,json={'base':record['revision'],'status':'deleted'}).status_code==403
            deleted=post(admin,path,{'base':record['revision'],'status':'deleted'})
            sync()
            assert target.get(record['id'])['status']=='deleted'
            assert reader.post('/api/v1/'+path,json={'base':deleted['revision'],'status':'active'}).status_code==403
            post(admin,path,{'base':deleted['revision'],'status':'active'})
            sync()
            assert target.get(record['id'])['status']=='active'
