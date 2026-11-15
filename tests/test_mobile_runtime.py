import base64
import json
from cycling_test.mobile_runtime import MobileRuntime


def command(runtime,path,method='GET',data=None,workspace='',body=None,media='application/json'):
    raw=body if body is not None else json.dumps(data).encode() if data is not None else b''
    result=json.loads(runtime.request(json.dumps({'path':'/api/v1/'+path,'method':method,'headers':{'content-type':media,'x-fuorigiri-workspace':workspace,'x-fuorigiri-token':'caller-cannot-choose-token'},'body':base64.b64encode(raw).decode()})))
    return result,base64.b64decode(result['body'])


def test_mobile_offline_workspace_reports_and_restart(tmp_path):
    runtime=MobileRuntime(tmp_path)
    result,body=command(runtime,'workspaces','POST',{'name':'Mobile club','operator':'Offline owner'})
    assert result['status']==200
    entry=json.loads(body);workspace=entry['id'];org=entry['organization_id']
    result,body=command(runtime,'athletes','POST',{'organization_id':org,'name':'Synthetic','surname':'Cyclist'},workspace)
    assert result['status']==200;athlete=json.loads(body)
    result,body=command(runtime,'protocols/manual','POST',{'name':'Catalog','family':'catalog','version':'1','reason':'mobile test','segments':[]},workspace)
    assert result['status']==200;protocol=json.loads(body)
    result,body=command(runtime,'manual-tests','POST',{'athlete_id':athlete['id'],'protocol_id':protocol['id'],'date':'2026-10-18','map_w':220,'settings':{'end_s':0,'weight_kg':55,'weight_source':'misurato'}},workspace)
    assert result['status']==200;test=json.loads(body)
    assert test['analysis']['map_wkg']==4
    runtime=MobileRuntime(tmp_path)
    result,body=command(runtime,'state',workspace=workspace)
    assert result['status']==200 and len(json.loads(body)['test'])==1
    for endpoint,prefix in [(f'tests/{test["id"]}/report/pdf',b'%PDF'),(f'tests/{test["id"]}/report/md',b'PK'),(f'export/{org}',b'PK'),('backup',b'PK')]:
        result,body=command(runtime,endpoint,workspace=workspace)
        assert result['status']==200 and body.startswith(prefix)


def test_mobile_multipart_fit_and_shared_incremental_result(tmp_path):
    from pathlib import Path
    runtime=MobileRuntime(tmp_path)
    path=next(Path('examples/synthetic').glob('*.fit'));raw=path.read_bytes()
    boundary='fuorigiri-test-boundary'
    multipart=(f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="test.fit"\r\nContent-Type: application/octet-stream\r\n\r\n'.encode()+raw+f'\r\n--{boundary}--\r\n'.encode())
    result,body=command(runtime,'traces/inspect','POST',body=multipart,media='multipart/form-data; boundary='+boundary)
    assert result['status']==200
    assert json.loads(body)['sessions']


def test_mobile_rejects_arbitrary_destinations(tmp_path):
    runtime=MobileRuntime(tmp_path)
    for path in ('https://cloud.example/steal','/api/v1/../backup','file:///data/private','/health'):
        result=json.loads(runtime.request(json.dumps({'path':path,'method':'GET'})))
        assert result['status']==422
    assert runtime.sync_all()


def test_mobile_preserves_viewer_permissions(tmp_path):
    from cycling_test.workspaces import Workspaces,invitation,join
    from cycling_test.store import Store
    from cycling_test.sync import exchange
    owner=Workspaces(tmp_path/'owner',Store(tmp_path/'owner'));entry=owner.create('Club','Owner');store=owner.get(entry['id'])
    manager=Workspaces(tmp_path/'mobile',Store(tmp_path/'mobile'));join(manager,invitation(store,'Reader','viewer','long-password-123'),'long-password-123')
    cloud=tmp_path/'cloud';cloud.mkdir();exchange(store,cloud,store.identity['sync_key']);exchange(manager.get(entry['id']),cloud,store.identity['sync_key'])
    runtime=MobileRuntime(tmp_path/'mobile')
    result,_=command(runtime,'athletes','POST',{'organization_id':entry['organization_id'],'name':'Denied','surname':'Denied'},entry['id'])
    assert result['status']==403
