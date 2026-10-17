import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.store import Store
from cycling_test.workspaces import Workspaces,invitation,join
from cycling_test.sync import exchange


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
    c=TestClient(create_app(tmp_path/'b',token='t'));c.headers.update({'X-Ciclo-Token':'t','X-Ciclo-Workspace':entry['id']})
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
