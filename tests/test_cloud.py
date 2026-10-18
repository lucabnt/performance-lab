import io
import json
import time
from urllib.parse import urlsplit,parse_qs
from urllib.error import HTTPError
import pytest
from cycling_test import cloud,credentials,sync_service
from cycling_test.store import Store
from cycling_test.workspaces import Workspaces

class Vault:
    def __init__(self):self.values={}
    def get_password(self,service,account):return self.values.get((service,account))
    def set_password(self,service,account,value):self.values[service,account]=value

@pytest.fixture
def vault(monkeypatch):
    value=Vault();monkeypatch.setattr(credentials,'_mobile',None);monkeypatch.setattr(credentials,'backend',lambda:value);return value

def store(tmp_path):
    w=Workspaces(tmp_path,Store(tmp_path));e=w.create('Club','Owner');return w.get(e['id'])

@pytest.mark.parametrize('provider',['drive','dropbox','onedrive','service'])
def test_configuration_secrets_are_local_and_transport_dispatch(tmp_path,vault,provider):
    s=store(tmp_path);c=sync_service.configure(s,{'transport':provider,'client_id':'registration','root_id':'folder1','root_path':'/Fuorigiri','url':'https://sync.example/','password':'SECRET'})
    assert 'SECRET' not in (s.root/'sync-connection.json').read_text()
    assert 'password' not in c
    assert sync_service.transport(s,c).kind==provider
    assert 'SECRET' not in json.dumps(s.list('organization'))
    assert len(vault.values)==1

def test_oauth_pkce_and_state_and_token_rotation(tmp_path,vault,monkeypatch):
    s=store(tmp_path);config={'transport':'dropbox','client_id':'app'}
    started=cloud.begin_oauth(s,config,mobile=True);q=parse_qs(urlsplit(started['authorization_url']).query)
    assert q['code_challenge_method']==['S256'] and q['token_access_type']==['offline']
    assert len(q['code_challenge'][0])==43
    with pytest.raises(ValueError):cloud.finish_oauth('fuorigiri://oauth/callback?state=forged&code=bad')
    calls=[]
    def token(p,data):calls.append(data);return {'access_token':'access','refresh_token':'refresh','expires_in':3600}
    monkeypatch.setattr(cloud,'token_request',token)
    cloud.finish_oauth('fuorigiri://oauth/callback?state='+q['state'][0]+'&code=ok')
    assert calls[0]['code_verifier'] and calls[0]['code']=='ok'
    assert cloud.oauth_status(s,started['session_id'])['status']=='connected'
    with pytest.raises(ValueError):cloud.finish_oauth('fuorigiri://oauth/callback?state='+q['state'][0]+'&code=ok')
    cloud.Tokens(s.root,config).refresh();assert calls[-1]['refresh_token']=='refresh'
    assert cloud.Tokens(s.root,config).access()=='access'

def test_google_native_no_embedded_browser_flow(tmp_path,vault):
    s=store(tmp_path);c={'transport':'drive','client_id':'android'}
    r=cloud.begin_oauth(s,c,True);assert r['native']=='google' and 'authorization_url' not in r
    cloud.finish_google(r['session_id'],'native-access')
    assert cloud.load_secret(s.root,'drive','android')['native']
    with pytest.raises(ValueError):cloud.finish_google(r['session_id'],'replay')

class FakeHTTP:
    def __init__(self,responses):self.responses=list(responses);self.calls=[]
    def request(self,method,url,body=None,headers=None,**kwargs):
        self.calls.append((method,url,body,headers,kwargs));expected=self.responses.pop(0)
        return expected[0],json.dumps(expected[1]).encode() if isinstance(expected[1],dict) else expected[1]
    def json(self,method,url,data=None,**kwargs):
        status,raw=self.request(method,url,data,**kwargs);return status,json.loads(raw)

def test_drive_pagination_generated_id_and_duplicate_guard(tmp_path):
    http=FakeHTTP([(200,{'files':[{'id':'1','name':'fuorigiri-ch--a.ctsync'}],'nextPageToken':'p2'}),(200,{'files':[]}),(200,{'ids':['generated']}),(200,{}),(200,b'cipher')])
    t=cloud.DriveTransport(tmp_path,{'transport':'drive','client_id':'app','root_id':'folder'},'ch',http)
    assert t.list()==['a.ctsync']
    assert 'pageToken=p2' in http.calls[1][1]
    assert t.put('b.ctsync',b'cipher')
    assert b'generated' in http.calls[-2][2]
    with pytest.raises(ValueError):t.add('fuorigiri-ch--a.ctsync','other-id')
    with pytest.raises(ValueError):t.remote_name('../bad')

def test_dropbox_shared_path_no_autorename_and_readback(tmp_path):
    http=FakeHTTP([(200,{'entries':[],'has_more':True,'cursor':'next'}),(200,{'entries':[], 'has_more':False}),(200,{}),(200,b'cipher')])
    t=cloud.DropboxTransport(tmp_path,{'transport':'dropbox','client_id':'app','root_path':'/Shared'},'ch',http)
    assert t.list()==[] and t.put('a.ctsync',b'cipher')
    metadata=json.loads(http.calls[2][3]['Dropbox-API-Arg'])
    assert metadata['mode']=='add' and not metadata['autorename'] and metadata['strict_conflict']
    assert metadata['path']=='/Shared/fuorigiri-ch--a.ctsync'

def test_onedrive_download_never_receives_graph_bearer(tmp_path):
    http=FakeHTTP([(200,{'value':[{'id':'file','name':'fuorigiri-ch--a.ctsync','file':{}}]}),(200,{'@microsoft.graph.downloadUrl':'https://public.dm.files.1drv.com/file?secret=private'}),(200,b'cipher')])
    t=cloud.OneDriveTransport(tmp_path,{'transport':'onedrive','client_id':'app','root_id':'folder','drive_id':'shared'},'ch',http)
    assert t.list()==['a.ctsync'];assert t.get('a.ctsync')==b'cipher'
    assert http.calls[-1][4]['auth'] is False
    http=FakeHTTP([(200,{'value':[],'@odata.nextLink':'https://attacker.example/page'})]);t.http=http
    with pytest.raises(ValueError):t.list()

def test_dedicated_client_contract(tmp_path):
    http=FakeHTTP([(200,{'schema':1,'objects':['a.ctsync']}),(201,b''),(200,b'cipher')])
    t=cloud.DedicatedTransport(tmp_path,{'transport':'service','client_id':'','url':'https://sync.example/'},'ch',http)
    assert t.list()==['a.ctsync'] and t.put('a.ctsync',b'cipher')
    assert http.calls[-2][3]['If-None-Match']=='*'
    assert http.calls[0][1]=='https://sync.example/v1/channels/ch/objects'

def test_http_refresh_sanitized_errors_and_https(monkeypatch):
    h=cloud.CloudHTTP(lambda:'secret',lambda:None)
    class Response:
        status=200
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self,*args):return b'ok'
    class Opener:
        count=0
        def open(self,request,timeout):
            self.count+=1
            if self.count==1:raise HTTPError(request.full_url,401,'secret-token',{},io.BytesIO())
            return Response()
    h.opener=Opener();assert h.request('GET','https://example.org/')[1]==b'ok' and h.opener.count==2
    with pytest.raises(ValueError):h.request('GET','http://example.org/')
    with pytest.raises(ValueError):h.request('GET','https://user:password@example.org/')

def test_concurrent_ciphertext_semantics_and_tampering(tmp_path):
    s=store(tmp_path)
    from cryptography.fernet import Fernet
    f=Fernet(s.identity['sync_key'].encode());a=f.encrypt(b'{"same":"event"}');b=f.encrypt(b'{"same":"event"}')
    t=cloud.CloudTransport(s.root,{'transport':'drive','client_id':'app'},'ch',FakeHTTP([]))
    assert a!=b and t.same(a,b)
    assert not t.same(a,f.encrypt(b'{"different":"event"}'))
    assert not t.same(a,b'corrupted')

def test_oauth_api_and_viewer_permissions(tmp_path,vault):
    from fastapi.testclient import TestClient
    from cycling_test.api import create_app
    from cycling_test.workspaces import invitation,join
    w=Workspaces(tmp_path/'owner',Store(tmp_path/'owner'));entry=w.create('Club','Owner');s=w.get(entry['id'])
    target=Workspaces(tmp_path/'viewer',Store(tmp_path/'viewer'));join(target,invitation(s,'Viewer','viewer','long-password-123'),'long-password-123')
    c=TestClient(create_app(tmp_path/'viewer',token='t'));c.headers.update({'X-Fuorigiri-Token':'t','X-Fuorigiri-Workspace':entry['id']})
    config={'transport':'dropbox','client_id':'app','root_path':'/Shared'}
    assert c.post('/api/v1/sync/connection',json=config).status_code==200
    r=c.post('/api/v1/sync/oauth/start',json={'mobile':True});assert r.status_code==200,r.text
    assert 'authorization_url' in r.json()
    assert c.post('/api/v1/anaerobic/protocols',json={}).status_code==403
    assert c.post('/api/v1/sync/oauth/disconnect',json={}).status_code==200
    assert cloud.oauth_status(target.get(entry['id']),r.json()['session_id'])['status']=='cancelled'
