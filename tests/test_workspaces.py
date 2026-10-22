import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.store import Store
from cycling_test.workspaces import Workspaces,invitation,join
from cycling_test.sync import exchange


def test_last_society_survives_backend_restart_and_origin_change(tmp_path):
    manager=Workspaces(tmp_path,Store(tmp_path))
    first=manager.create('First','Owner');second=manager.create('Second','Owner')
    choice={'workspace':second['id'],'organization':second['organization_id']}
    client=TestClient(create_app(tmp_path,token='first'),base_url='http://127.0.0.1:50001')
    client.headers['X-Fuorigiri-Token']='first'
    assert client.get('/api/v1/workspaces/last-selection').json()=={'workspace':'','organization':''}
    assert client.put('/api/v1/workspaces/last-selection',json=choice).status_code==200
    reopened=TestClient(create_app(tmp_path,token='second'),base_url='http://127.0.0.1:50002')
    reopened.headers['X-Fuorigiri-Token']='second'
    assert reopened.get('/api/v1/workspaces/last-selection').json()==choice
    assert set(json.loads((tmp_path/'last-selection.json').read_text()))=={'workspace','organization'}
    assert reopened.put('/api/v1/workspaces/last-selection',json={**choice,'organization':first['organization_id']}).status_code==422
    assert reopened.get('/api/v1/workspaces/last-selection').json()==choice
    assert TestClient(create_app(tmp_path,token='private')).get('/api/v1/workspaces/last-selection').status_code==401
    (tmp_path/'last-selection.json').write_text('invalid',encoding='utf-8')
    assert reopened.get('/api/v1/workspaces/last-selection').json()=={'workspace':'','organization':''}


def test_viewer_can_remember_society_without_writing_society_records(tmp_path):
    owner=Workspaces(tmp_path/'owner',Store(tmp_path/'owner'));entry=owner.create('Club','Owner')
    manager=Workspaces(tmp_path/'viewer',Store(tmp_path/'viewer'))
    joined=join(manager,invitation(owner.get(entry['id']),'Reader','viewer','long-password-123'),'long-password-123')
    folder=tmp_path/'cloud';folder.mkdir()
    exchange(owner.get(entry['id']),folder,owner.get(entry['id']).identity['sync_key'])
    exchange(manager.get(joined['id']),folder,manager.get(joined['id']).identity['sync_key'])
    client=TestClient(create_app(tmp_path/'viewer',token='t'))
    client.headers.update({'X-Fuorigiri-Token':'t','X-Fuorigiri-Workspace':joined['id']})
    assert client.put('/api/v1/workspaces/last-selection',json={'workspace':joined['id'],'organization':joined['organization_id']}).status_code==200
    assert client.post('/api/v1/organizations',json={'name':'Forbidden'}).status_code==403
    assert client.post('/api/v1/memberships/batch',json={'group_id':'g','athlete_ids':['a'],'start':'2026-01-01'}).status_code==403


def test_separate_archives_viewer_and_forgery(tmp_path):
    a=Workspaces(tmp_path/'a',Store(tmp_path/'a'))
    b=Workspaces(tmp_path/'b',Store(tmp_path/'b'))
    entry=a.create('Club','Owner')
    store=a.get(entry['id'])
    other=a.create('Other','Owner')
    assert not a.get(other['id']).list('athlete')
    raw=invitation(store,'Reader','viewer','long-password-123')
    joined=join(b,raw,'long-password-123');viewer=b.get(joined['id'])
    with pytest.raises(ValueError):viewer.save('athlete',{'name':'Forged'})
    folder=tmp_path/'cloud';folder.mkdir()
    exchange(store,folder,store.identity['sync_key'])
    exchange(viewer,folder,viewer.identity['sync_key'])
    assert viewer.list('organization')[0]['name']=='Club'
    c=TestClient(create_app(tmp_path/'b',token='t'));c.headers.update({'X-Fuorigiri-Token':'t','X-Fuorigiri-Workspace':entry['id']})
    assert c.post('/api/v1/organizations',json={'name':'Not allowed'}).status_code==403
    assert c.post('/api/v1/athletes',json={'name':'A','surname':'B','organization_id':entry['organization_id']}).status_code==403
    assert c.get('/api/v1/state').json()['operator']['role']=='viewer'
    identity=viewer.identity
    assert identity['private_key'] is None and 'authority_private' not in identity
    from cryptography.fernet import Fernet
    cipher=Fernet(store.identity['sync_key'].encode())
    shared=next(folder.iterdir());packet=next(shared.glob('*.ctsync'))
    forged=json.loads(cipher.decrypt(packet.read_bytes()))
    forged['change']['record']['name']='Tampered with shared read key'
    (shared/'forged.ctsync').write_bytes(cipher.encrypt(json.dumps(forged).encode()))
    result=exchange(viewer,folder,viewer.identity['sync_key'])
    assert result['errors']
    assert viewer.list('organization')[0]['name']=='Club'


def test_signed_concurrent_resolution_converges(tmp_path):
    a=Workspaces(tmp_path/'a',Store(tmp_path/'a'));entry=a.create('Club','Owner');left=a.get(entry['id'])
    b=Workspaces(tmp_path/'b',Store(tmp_path/'b'));join(b,invitation(left,'Coach','admin','long-password-123'),'long-password-123');right=b.get(entry['id'])
    folder=tmp_path/'cloud';folder.mkdir();key=left.identity['sync_key']
    original=left.list('organization')[0]
    exchange(left,folder,key);exchange(right,folder,key)
    l=left.save('organization',{'name':'Left'},original['id'],original['revision'])
    r=right.save('organization',{'name':'Right'},original['id'],original['revision'])
    exchange(left,folder,key);exchange(right,folder,key);exchange(left,folder,key)
    merged=left.save('organization',{'name':'Merged'},original['id'],l['revision'],parents=[r['revision']])
    exchange(left,folder,key);exchange(right,folder,key)
    assert right.get(original['id'])['revision']==merged['revision']
    assert right.get(original['id'])['name']=='Merged'
