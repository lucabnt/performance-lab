import base64
import hashlib
import json
import threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import quote,unquote
from xml.sax.saxutils import escape
import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.store import Store,encoded
from cycling_test.workspaces import Workspaces,invitation,join,write_json,sign
from cycling_test.transports import WebDAVTransport,FolderTransport,validate_url
from cycling_test.sync import exchange
from cycling_test import sync_service


@pytest.fixture
def dav():
    files={};state={'created':False,'partial':False,'timeout_after_put':False,'reads_only':False,'malicious':False,'puts':0}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def respond(self,status,body=b''):
            self.send_response(status);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        def auth(self):
            if self.headers.get('Authorization')!='Basic '+base64.b64encode(b'user:password').decode():
                self.respond(401);return False
            return True
        def do_MKCOL(self):
            if not self.auth():return
            if state['reads_only']:self.respond(403);return
            self.respond(405 if state['created'] else 201);state['created']=True
        def do_PROPFIND(self):
            if not self.auth():return
            if not state['created']:self.respond(404);return
            assert self.headers['Depth']=='1'
            hrefs=[self.path]+[self.path+quote(k) for k in files]
            if state['malicious']:hrefs.append('https://other.example/stolen.ctsync')
            xml='<d:multistatus xmlns:d="DAV:">'+''.join('<d:response><d:href>'+escape(href)+'</d:href><d:propstat><d:prop><d:resourcetype/></d:prop><d:status>HTTP/1.1 200 OK</d:status></d:propstat></d:response>' for href in hrefs)+'</d:multistatus>'
            self.respond(207,xml.encode())
        def do_GET(self):
            if not self.auth():return
            name=unquote(self.path.rsplit('/',1)[1])
            if name not in files:self.respond(404);return
            self.respond(200,files[name])
        def do_PUT(self):
            if not self.auth():return
            data=self.rfile.read(int(self.headers['Content-Length']))
            if state['reads_only']:self.respond(403);return
            assert self.headers['If-None-Match']=='*'
            name=unquote(self.path.rsplit('/',1)[1])
            if name in files:self.respond(412);return
            state['puts']+=1;files[name]=data[:5] if state['partial'] else data
            if state['timeout_after_put']:
                state['timeout_after_put']=False;self.connection.close();return
            self.respond(201)
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    def factory(key):return WebDAVTransport(f'http://127.0.0.1:{server.server_port}/dav/','user','password',hashlib.sha256(key.encode()).hexdigest()[:24],allow_loopback=True,timeout=2)
    yield factory,files,state
    server.shutdown();server.server_close();worker.join()


def pair(tmp_path,role='admin'):
    a=Workspaces(tmp_path/'a',Store(tmp_path/'a'));entry=a.create('Club','Owner');left=a.get(entry['id'])
    b=Workspaces(tmp_path/'b',Store(tmp_path/'b'));join(b,invitation(left,'Coach',role,'long-password-123'),'long-password-123')
    return left,b.get(entry['id'])


def test_webdav_encrypted_exchange_retry_conflicts_and_viewer(tmp_path,dav):
    factory,files,state=dav;left,right=pair(tmp_path);key=left.identity['sync_key'];remote=factory(key)
    state['timeout_after_put']=True
    result=exchange(left,None,key,remote)
    assert result['remote_verified'] and result['published']==1 and not result['errors']
    assert all(b'Owner' not in body and b'Club' not in body for name,body in files.items() if name.endswith('.ctsync'))
    exchange(right,None,key,factory(key));original=right.list('organization')[0]
    left.save('organization',{'name':'Left'},original['id'],original['revision'])
    right.save('organization',{'name':'Right'},original['id'],original['revision'])
    exchange(left,None,key,remote);result=exchange(right,None,key,factory(key))
    assert result['conflicts']==1
    assert exchange(right,None,key,factory(key))['published']==0
    # Read-only cloud permissions work after the channel has been created.
    b=Workspaces(tmp_path/'viewer',Store(tmp_path/'viewer'));join(b,invitation(left,'Reader','viewer','long-password-123'),'long-password-123')
    exchange(left,None,key,remote);viewer=b.get(left.identity['workspace']);state['reads_only']=True
    assert exchange(viewer,None,key,factory(key))['received']>=1


def test_webdav_rejects_partial_commit_and_external_inventory(dav):
    factory,files,state=dav;transport=factory('opaque-key');transport.list();state['partial']=True
    with pytest.raises(ValueError,match='Integrità'):transport.put('event.ctsync',b'long-encrypted-body')
    assert files['event.ctsync']==b'long-'
    state['malicious']=True
    with pytest.raises(ValueError,match='esterno'):transport.list()


def test_transport_constraints_and_malformed_auth(dav,tmp_path):
    for url in ('http://cloud.example/dav','https://u:p@example/dav','https://example/dav?token=x','https://example/%2e%2e/secret'):
        with pytest.raises(ValueError):validate_url(url)
    transport=dav[0]('key');transport.auth='Basic invalid'
    with pytest.raises(ValueError,match='Autenticazione'):transport.list()
    folder=tmp_path/'channel';folder.mkdir();local=FolderTransport(folder,'opaque',tmp_path/'archive')
    local.put('one.ctsync',b'valid')
    assert not local.put('one.ctsync',b'valid')
    with pytest.raises(ValueError):local.put('one.ctsync',b'other')
    with pytest.raises(ValueError):local.get('../identity.json')


def test_controls_no_rollback_and_same_version_fork(tmp_path):
    left,right=pair(tmp_path);folder=tmp_path/'cloud';folder.mkdir();key=left.identity['sync_key']
    old=(left.root/'access.json').read_bytes()
    exchange(left,folder,key)
    invitation(left,'Reader','viewer','long-password-123');new=(left.root/'access.json').read_bytes()
    exchange(left,folder,key);(left.root/'access.json').write_bytes(old)
    exchange(left,folder,key)
    assert json.loads((left.root/'access.json').read_bytes())==json.loads(new)
    latest=json.loads(new);latest['founder_id']='divergent';body={k:v for k,v in latest.items() if k!='signature'};latest['signature']=sign(left.identity['authority_private'],body)
    write_json(left.root/'access.json',latest)
    with pytest.raises(ValueError,match='divergenti'):exchange(left,folder,key)


def test_previous_folder_configuration_remains_available(tmp_path):
    left,_=pair(tmp_path)
    (left.root/'sync-folder.txt').write_text('F:/synthetic-cloud',encoding='utf-8')
    assert sync_service.configuration(left)=={'transport':'folder','folder':'F:/synthetic-cloud'}


def test_signed_access_cannot_be_replayed_as_revocations(tmp_path):
    left,right=pair(tmp_path);folder=tmp_path/'cloud';folder.mkdir();key=left.identity['sync_key']
    exchange(left,folder,key)
    shared=next(folder.iterdir())
    (shared/'revocations.json').write_bytes((left.root/'access.json').read_bytes())
    with pytest.raises(ValueError,match='Schema delle revoche'):exchange(right,folder,key)
    assert not (right.root/'revocations.json').exists()
    assert not (right.root/'access.json').exists()


def test_reader_key_cannot_break_exchange_with_wrong_json_shape(tmp_path):
    from cryptography.fernet import Fernet
    left,right=pair(tmp_path,'viewer');folder=tmp_path/'cloud';folder.mkdir();key=left.identity['sync_key']
    exchange(left,folder,key)
    (next(folder.iterdir())/'malformed.ctsync').write_bytes(Fernet(key.encode()).encrypt(b'[]'))
    result=exchange(right,folder,key)
    assert result['errors'] and right.list('organization')[0]['name']=='Club'


def test_rotation_and_invitation_preserve_unsent_changes(tmp_path):
    left,right=pair(tmp_path);folder=tmp_path/'cloud';folder.mkdir()
    sync_service.configure(left,{'transport':'folder','folder':str(folder)})
    oldkey=left.identity['sync_key'];sync_service.run_sync(left);exchange(right,folder,oldkey)
    saved=right.save('athlete',{'name':'Offline','surname':'Athlete'})
    assert sync_service.rotate(left)['rotated']
    assert left.identity['sync_key']!=oldkey and not (left.root/'rotation-pending.json').exists()
    with pytest.raises(ValueError,match='ruotata'):exchange(right,folder,oldkey)
    assert right.get(saved['id'])['name']=='Offline'
    from cycling_test.workspaces import apply_invitation
    apply_invitation(right,invitation(left,'Coach renewed','admin','long-password-123',right.identity['certificate']['id']),'long-password-123')
    sync_service.run_sync(left)
    # Old author events created before revocation remain local and require recovery;
    # rotation never silently discards or re-signs them.
    result=exchange(right,folder,right.identity['sync_key'])
    assert right.get(saved['id'])['revision']==saved['revision']
    assert result['transport']=='folder'


def test_connection_password_never_serialized_and_viewer_config(tmp_path,monkeypatch):
    secrets={}
    monkeypatch.setattr(sync_service.credentials,'save',lambda root,value:secrets.update(password=value))
    monkeypatch.setattr(sync_service.credentials,'read',lambda root:secrets['password'])
    left,right=pair(tmp_path,'viewer')
    value=sync_service.configure(right,{'transport':'webdav','url':'https://cloud.example/dav','username':'reader','password':'not-in-json'})
    assert 'password' not in value and 'not-in-json' not in (right.root/'sync-connection.json').read_text()
    c=TestClient(create_app(tmp_path/'b',token='t'));c.headers.update({'X-Fuorigiri-Token':'t','X-Fuorigiri-Workspace':right.identity['workspace']})
    assert c.post('/api/v1/sync/connection',json={'transport':'folder','folder':str(tmp_path/'cloud')}).status_code==200
    assert c.post('/api/v1/sync/rotate',json={}).status_code==403


def test_rotation_recovers_after_remote_notice_commit(tmp_path,monkeypatch):
    left,_=pair(tmp_path);folder=tmp_path/'cloud';folder.mkdir()
    sync_service.configure(left,{'transport':'folder','folder':str(folder)})
    original=sync_service.write_json
    def interrupted(path,value):
        if path.name=='identity.json':raise OSError('power loss')
        return original(path,value)
    monkeypatch.setattr(sync_service,'write_json',interrupted)
    with pytest.raises(OSError):sync_service.rotate(left)
    assert (left.root/'rotation-pending.json').exists()
    with pytest.raises(ValueError,match='interrotta'):sync_service.run_sync(left)
    monkeypatch.setattr(sync_service,'write_json',original)
    assert sync_service.rotate(left)['rotated']
    assert sync_service.run_sync(left)['published']>=1
