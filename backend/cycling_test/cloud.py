"""Cloud OAuth and immutable-object APIs. No provider SDK or central secret.

Account registration is supplied by the distributor/user. Refresh credentials
live in the OS vault, separately from the archive, invitations and data backups.
"""
import base64
import hashlib
import json
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib.error import HTTPError,URLError
from urllib.parse import urlencode,urlsplit,parse_qs,quote
from urllib.request import Request,build_opener,HTTPSHandler
import ssl
from . import credentials
from .store import encoded
from .transports import NoRedirect,MAX_PACKET,MAX_FILES,safe_name

PROVIDERS={
 'drive':{'authorize':'https://accounts.google.com/o/oauth2/v2/auth','token':'https://oauth2.googleapis.com/token',
          'scopes':'https://www.googleapis.com/auth/drive.file'},
 'dropbox':{'authorize':'https://www.dropbox.com/oauth2/authorize','token':'https://api.dropboxapi.com/oauth2/token','scopes':''},
 'onedrive':{'authorize':'https://login.microsoftonline.com/common/oauth2/v2.0/authorize','token':'https://login.microsoftonline.com/common/oauth2/v2.0/token',
             'scopes':'offline_access Files.ReadWrite.All'},
}
_sessions={};_guard=threading.RLock()


def vault_key(root,provider,client_id=''):
    return credentials.account(root)+':'+provider+':'+hashlib.sha256(client_id.encode()).hexdigest()[:16]


def load_secret(root,provider,client_id=''):
    try:raw=credentials.backend().get_password('Fuorigiri.Cloud',vault_key(root,provider,client_id))
    except Exception:raise ValueError('Portachiavi cloud non disponibile.') from None
    return json.loads(raw) if raw else {}


def save_secret(root,provider,value,client_id=''):
    try:credentials.backend().set_password('Fuorigiri.Cloud',vault_key(root,provider,client_id),encoded(value))
    except Exception:raise ValueError('Impossibile salvare le credenziali cloud nel portachiavi.') from None


class CloudHTTP:
    def __init__(self,token=lambda:'',refresh=None):
        self.token=token;self.refresh=refresh
        self.opener=build_opener(NoRedirect(),HTTPSHandler(context=ssl.create_default_context()))

    def request(self,method,url,body=None,headers=None,accepted=(200,),auth=True,limit=MAX_PACKET):
        parsed=urlsplit(url)
        if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or '\r' in url or '\n' in url:
            raise ValueError('Endpoint cloud HTTPS non valido.')
        renewed=False
        for attempt in range(4):
            try:
                h={'User-Agent':'Fuorigiri/0.7',**(headers or {})}
                if auth:h['Authorization']='Bearer '+self.token()
                with self.opener.open(Request(url,data=body,headers=h,method=method),timeout=30) as response:
                    if response.status not in accepted:raise ValueError('Risposta cloud inattesa.')
                    data=response.read(limit+1)
                    if len(data)>limit:raise ValueError('Oggetto cloud oltre il limite di dimensione.')
                    return response.status,data
            except HTTPError as exc:
                status=exc.code;exc.close()
                if status in accepted:return status,b''
                if status==401 and auth and self.refresh and not renewed:
                    self.refresh();renewed=True;continue
                if status in (408,429,500,502,503,504) and attempt<3:time.sleep(min(.4*2**attempt,2));continue
                raise ValueError({401:'Accesso cloud scaduto o revocato: ricollegare l’account.',403:'Permessi cloud insufficienti: verificare consenso e condivisione.',404:'Cartella o oggetto cloud non trovato.',409:'Conflitto di pubblicazione cloud.',413:'Quota o dimensione del caricamento non consentita.'}.get(status,f'Cloud: errore HTTP {status}.')) from None
            except (URLError,OSError,TimeoutError):
                if attempt<3:time.sleep(min(.4*2**attempt,2));continue
                raise ValueError('Cloud non raggiungibile. Dati locali conservati; riprovare.') from None

    def json(self,method,url,data=None,**kwargs):
        body=encoded(data).encode() if data is not None else None
        status,raw=self.request(method,url,body,{'Content-Type':'application/json'},**kwargs)
        return status,json.loads(raw) if raw else {}


def token_request(provider,parameters,http=None):
    client=http or CloudHTTP()
    _,body=client.request('POST',PROVIDERS[provider]['token'],urlencode(parameters).encode(),{'Content-Type':'application/x-www-form-urlencoded'},auth=False,limit=1_000_000)
    value=json.loads(body)
    if not value.get('access_token'):raise ValueError('Il provider non ha restituito un accesso utilizzabile.')
    return value


class Tokens:
    def __init__(self,root,config):self.root=root;self.config=config;self.guard=threading.RLock()
    def refresh(self):
        with self.guard:
            p=self.config['transport'];secret=load_secret(self.root,p,self.config['client_id'])
            if p=='drive' and secret.get('native') and credentials._mobile is not None:
                scope='https://www.googleapis.com/auth/drive' if self.config.get('drive_scope')=='full' else 'https://www.googleapis.com/auth/drive.file'
                try:token=credentials._mobile.refresh_google_token(scope)
                except Exception:raise ValueError('Google richiede un nuovo consenso: aprire Collega account.') from None
                if not token:raise ValueError('Google richiede un nuovo consenso: aprire Collega account.')
                secret.update(access_token=str(token),expires_at=time.time()+3300)
                save_secret(self.root,p,secret,self.config['client_id']);return
            if not secret.get('refresh_token'):raise ValueError('Ricollegare l’account cloud per rinnovare l’accesso.')
            params={'grant_type':'refresh_token','refresh_token':secret['refresh_token'],'client_id':self.config['client_id']}
            if secret.get('client_secret'):params['client_secret']=secret['client_secret']
            value=token_request(p,params)
            secret.update(value);secret['expires_at']=time.time()+float(value.get('expires_in',3600))
            save_secret(self.root,p,secret,self.config['client_id'])
    def access(self):
        with self.guard:
            secret=load_secret(self.root,self.config['transport'],self.config['client_id'])
            if secret.get('expires_at',0)<=time.time()+30:self.refresh();secret=load_secret(self.root,self.config['transport'],self.config['client_id'])
            if not secret.get('access_token'):raise ValueError('Collegare prima l’account cloud.')
            return secret['access_token']


def begin_oauth(store,config,mobile=False):
    p=config['transport'];registration=PROVIDERS[p]
    if not config.get('client_id'):raise ValueError('Configurare il client ID della registrazione OAuth.')
    state=secrets.token_urlsafe(32);verifier=secrets.token_urlsafe(64)
    if mobile and p=='drive':
        scope='https://www.googleapis.com/auth/drive' if config.get('drive_scope')=='full' else PROVIDERS[p]['scopes']
        with _guard:_sessions[state]={'root':store.root,'config':dict(config),'expires':time.time()+300,'status':'pending','native':True}
        return {'native':'google','scope':scope,'session_id':state,'expires_in':300}
    redirect='fuorigiri://oauth/callback' if mobile else 'http://127.0.0.1:53682/oauth/callback'
    listener=None
    if not mobile:
        class Callback(BaseHTTPRequestHandler):
            def log_message(self,*args):pass
            def do_GET(self):
                try:
                    if urlsplit(self.path).path!='/oauth/callback':raise ValueError('Callback non valido.')
                    finish_oauth('http://127.0.0.1:53682'+self.path,expected=state)
                    body='Account collegato. Puoi tornare a Fuorigiri.'.encode();status=200
                except (ValueError,KeyError):body='Collegamento non completato. Torna a Fuorigiri e riprova.'.encode();status=400
                self.send_response(status);self.send_header('Content-Type','text/plain; charset=utf-8');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
        try:listener=HTTPServer(('127.0.0.1',53682),Callback)
        except OSError:raise ValueError('Callback OAuth occupato: completare il collegamento già aperto o riprovare.') from None
    session={'root':store.root,'config':dict(config),'state':state,'verifier':verifier,'redirect':redirect,'expires':time.time()+300,'status':'pending','listener':listener}
    with _guard:_sessions[state]=session
    if listener:
        def serve():
            listener.timeout=1
            try:
                while session['status']=='pending' and time.time()<session['expires']:listener.handle_request()
            finally:listener.server_close()
        threading.Thread(target=serve,daemon=True).start()
    params={'client_id':config['client_id'],'response_type':'code','redirect_uri':redirect,'state':state,
            'code_challenge':base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode(),'code_challenge_method':'S256'}
    scope=registration['scopes']
    if p=='drive':
        if config.get('drive_scope')=='full':scope='https://www.googleapis.com/auth/drive'
        params.update(access_type='offline',prompt='consent')
    if p=='dropbox':params['token_access_type']='offline'
    if scope:params['scope']=scope
    return {'authorization_url':registration['authorize']+'?'+urlencode(params),'session_id':state,'expires_in':300}


def finish_oauth(url,expected=None):
    parsed=urlsplit(url);query=parse_qs(parsed.query);state=query.get('state',[''])[0]
    with _guard:
        session=_sessions.get(state)
        if not session or expected and not secrets.compare_digest(state,expected) or session['status']!='pending' or time.time()>session['expires']:
            raise ValueError('Sessione OAuth scaduta o non valida.')
        if parsed.scheme+'://'+parsed.netloc+parsed.path!=session['redirect']:raise ValueError('Redirect OAuth non valido.')
        session['status']='exchanging'
    try:
        if query.get('error') or not query.get('code'):raise ValueError('Autorizzazione cloud non concessa.')
        config=session['config'];provider=config['transport']
        secret=load_secret(session['root'],provider,config['client_id'])
        params={'client_id':config['client_id'],'grant_type':'authorization_code','code':query['code'][0],
                'redirect_uri':session['redirect'],'code_verifier':session['verifier']}
        if secret.get('client_secret'):params['client_secret']=secret['client_secret']
        value=token_request(provider,params)
        secret.update(value);secret['expires_at']=time.time()+float(value.get('expires_in',3600))
        with _guard:
            if session['status']!='exchanging':raise ValueError('Autorizzazione annullata.')
            save_secret(session['root'],provider,secret,config['client_id']);session['status']='connected'
    except Exception:
        session['status']='failed';raise ValueError('Collegamento cloud non completato: verificare registrazione, consenso e portachiavi.') from None
    finally:session.pop('verifier',None)
    return {'connected':True}


def oauth_status(store,state):
    session=_sessions.get(state)
    if not session or session['root'].resolve()!=store.root.resolve():raise ValueError('Sessione non disponibile per questa società.')
    return {'status':'expired' if session['status']=='pending' and time.time()>session['expires'] else session['status']}

def finish_google(state,token):
    with _guard:
        session=_sessions.get(state)
        if not session or not session.get('native') or session['status']!='pending' or time.time()>session['expires'] or not token:raise ValueError('Autorizzazione Google non valida o scaduta.')
        save_secret(session['root'],'drive',{'access_token':token,'expires_at':time.time()+3300,'native':True},session['config']['client_id'])
        session['status']='connected'
    return True


class CloudTransport:
    remote=True
    def __init__(self,root,config,channel,http=None):
        self.root=root;self.config=config;self.kind=config['transport'];self.prefix='fuorigiri-'+channel+'--'
        tokens=Tokens(root,config);self.http=http or CloudHTTP(tokens.access,tokens.refresh)
        self.index={}
    def same(self,left,right):
        if left==right:return True
        # Fernet intentionally produces different ciphertext for the same event.
        # Concurrent relays are equivalent only when authenticated plaintext is
        # identical under this archive's current channel key; never overwrite.
        try:
            from cryptography.fernet import Fernet,InvalidToken
            identity=json.loads((self.root/'identity.json').read_text(encoding='utf-8'))
            cipher=Fernet(identity['sync_key'].encode())
            return cipher.decrypt(left)==cipher.decrypt(right)
        except (OSError,ValueError,KeyError,InvalidToken):return False
    def remote_name(self,name):return self.prefix+safe_name(name)
    def add(self,name,id):
        if not name.startswith(self.prefix):return
        name=safe_name(name[len(self.prefix):])
        if name in self.index and self.index[name]!=id:raise ValueError('Nomi duplicati nella cartella cloud: riconciliare prima di proseguire.')
        self.index[name]=id
        if len(self.index)>MAX_FILES:raise ValueError('Inventario cloud troppo grande.')


class DriveTransport(CloudTransport):
    API='https://www.googleapis.com/drive/v3/'
    def list(self):
        self.index={};page='';seen=set();duplicates=[]
        while True:
            params={'q':f"'{self.config['root_id']}' in parents and trashed = false",'fields':'nextPageToken,files(id,name,mimeType)','pageSize':1000,'supportsAllDrives':'true','includeItemsFromAllDrives':'true'}
            if page:params['pageToken']=page
            _,data=self.http.json('GET',self.API+'files?'+urlencode(params))
            for item in data.get('files',[]):
                if item.get('mimeType')!='application/vnd.google-apps.folder':
                    remote=item['name']
                    local=remote[len(self.prefix):] if remote.startswith(self.prefix) else ''
                    if local and local in self.index:duplicates.append((local,item['id']))
                    else:self.add(remote,item['id'])
            page=data.get('nextPageToken')
            if not page:break
            if page in seen or len(seen)>=1000:raise ValueError('Paginazione Drive non valida o eccessiva.')
            seen.add(page)
        for name,id in duplicates:
            other=self.http.request('GET',self.API+'files/'+quote(id,safe='')+'?alt=media&supportsAllDrives=true')[1]
            if not self.same(self.get(name),other):raise ValueError('Duplicati Drive con contenuto diverso: riconciliare prima di proseguire.')
        return sorted(self.index)
    def get(self,name):return self.http.request('GET',self.API+'files/'+quote(self.index[safe_name(name)],safe='')+'?alt=media&supportsAllDrives=true')[1]
    def put(self,name,body):
        if len(body)>MAX_PACKET:raise ValueError('Pacchetto troppo grande.')
        if name in self.index:
            if not self.same(self.get(name),body):raise ValueError('Oggetto cloud immutabile con contenuto diverso.')
            return False
        # Keep the generated Google ID across timeout/process restart. Retrying
        # create with the same ID cannot produce another file on this device.
        key='drive-upload:'+hashlib.sha256((self.config['root_id']+'|'+self.remote_name(name)).encode()).hexdigest()
        from .store import Store
        store=Store(self.root)
        with store.connect() as db:row=db.execute('SELECT value FROM config WHERE key=?',(key,)).fetchone()
        if row:file_id=row[0]
        else:
            _,value=self.http.json('GET',self.API+'files/generateIds?count=1&space=drive&type=files');file_id=value['ids'][0]
            with store.connect() as db:db.execute('INSERT OR IGNORE INTO config VALUES(?,?)',(key,file_id));file_id=db.execute('SELECT value FROM config WHERE key=?',(key,)).fetchone()[0]
        boundary='fuorigiri-'+secrets.token_hex(16)
        metadata={'id':file_id,'name':self.remote_name(name),'parents':[self.config['root_id']]}
        data=(f'--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n'.encode()+encoded(metadata).encode()+f'\r\n--{boundary}\r\nContent-Type: application/octet-stream\r\n\r\n'.encode()+body+f'\r\n--{boundary}--\r\n'.encode())
        status,_=self.http.request('POST','https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&supportsAllDrives=true',data,{'Content-Type':'multipart/related; boundary='+boundary},accepted=(200,201,409))
        self.index[name]=file_id
        if not self.same(self.get(name),body):raise ValueError('Pubblicazione Drive non verificata.')
        return status!=409


class DropboxTransport(CloudTransport):
    API='https://api.dropboxapi.com/2/files/'
    def path(self,name=''):return self.config['root_path'].rstrip('/')+'/'+self.remote_name(name) if name else self.config['root_path'].rstrip('/')
    def list(self):
        self.index={};seen=set();_,data=self.http.json('POST',self.API+'list_folder',{'path':self.path(),'recursive':False,'include_deleted':False,'limit':2000})
        while True:
            for item in data.get('entries',[]):
                if item.get('.tag')=='file':self.add(item['name'],item['path_lower'])
            if not data.get('has_more'):break
            if data['cursor'] in seen or len(seen)>=1000:raise ValueError('Paginazione Dropbox non valida o eccessiva.')
            seen.add(data['cursor'])
            _,data=self.http.json('POST',self.API+'list_folder/continue',{'cursor':data['cursor']})
        return sorted(self.index)
    def get(self,name):
        path=self.index.get(name,self.path(name))
        return self.http.request('POST','https://content.dropboxapi.com/2/files/download',b'',{'Dropbox-API-Arg':encoded({'path':path})})[1]
    def put(self,name,body):
        if len(body)>MAX_PACKET:raise ValueError('Pacchetto troppo grande.')
        status,_=self.http.request('POST','https://content.dropboxapi.com/2/files/upload',body,{'Content-Type':'application/octet-stream','Dropbox-API-Arg':encoded({'path':self.path(name),'mode':'add','autorename':False,'mute':True,'strict_conflict':True})},accepted=(200,409))
        if not self.same(self.get(name),body):raise ValueError('Pubblicazione Dropbox non verificata o nome già occupato.')
        self.index[name]=self.path(name);return status!=409


class OneDriveTransport(CloudTransport):
    API='https://graph.microsoft.com/v1.0/'
    def base(self):
        drive=self.config.get('drive_id')
        return self.API+('drives/'+quote(drive,safe='') if drive else 'me/drive')+'/items/'+quote(self.config['root_id'],safe='')
    def list(self):
        self.index={};seen=set();url=self.base()+'/children?$select=id,name,file,remoteItem&$top=200'
        while url:
            if url in seen or len(seen)>=1000:raise ValueError('Paginazione OneDrive non valida o eccessiva.')
            seen.add(url)
            if urlsplit(url).scheme!='https' or urlsplit(url).netloc!='graph.microsoft.com':raise ValueError('Paginazione OneDrive non valida.')
            _,data=self.http.json('GET',url)
            for item in data.get('value',[]):
                if 'file' in item:self.add(item['name'],item['id'])
            url=data.get('@odata.nextLink')
        return sorted(self.index)
    def get(self,name):
        id=self.index.get(name)
        item=(self.API+('drives/'+quote(self.config['drive_id'],safe='') if self.config.get('drive_id') else 'me/drive')+'/items/'+quote(id,safe='')) if id else self.base()+':/'+quote(self.remote_name(name),safe='')
        _,value=self.http.json('GET',item)
        url=value.get('@microsoft.graph.downloadUrl','');host=urlsplit(url).hostname or ''
        if not any(host==d or host.endswith('.'+d) for d in ('sharepoint.com','sharepoint-df.com','1drv.com','onedrive.com','onedriveusercontent.com','storage.live.com','livefilestore.com')):
            raise ValueError('Destinazione download OneDrive non riconosciuta.')
        # Preauthenticated URL: never attach the Microsoft Graph access token.
        return self.http.request('GET',url,auth=False)[1]
    def put(self,name,body):
        if len(body)>MAX_PACKET:raise ValueError('Pacchetto troppo grande.')
        url=self.base()+':/'+quote(self.remote_name(name),safe='')+':/content?%40microsoft.graph.conflictBehavior=fail'
        status,data=self.http.request('PUT',url,body,{'Content-Type':'application/octet-stream','If-None-Match':'*'},accepted=(200,201,409,412))
        if status in (200,201) and data:self.index[name]=json.loads(data)['id']
        if not self.same(self.get(name),body):raise ValueError('Pubblicazione OneDrive non verificata o nome già occupato.')
        return status not in (409,412)


class DedicatedTransport(CloudTransport):
    """Client contract for a future dedicated relay. No server is deployed."""
    def __init__(self,root,config,channel,http=None):
        super().__init__(root,config,channel,http)
        from .transports import validate_url
        self.base=validate_url(config['url'])+'v1/channels/'+channel+'/objects'
        if http is None:
            def access():
                token=load_secret(root,'service',config.get('client_id','')).get('token')
                if not token:raise ValueError('Configurare il token del servizio dedicato.')
                return token
            self.http=CloudHTTP(access)
    def list(self):
        _,value=self.http.json('GET',self.base)
        if value.get('schema')!=1:raise ValueError('Versione del servizio di sincronizzazione non supportata.')
        names=value.get('objects',[])
        if not isinstance(names,list) or len(names)>MAX_FILES:raise ValueError('Inventario del servizio non valido.')
        return sorted({safe_name(n) for n in names})
    def get(self,name):return self.http.request('GET',self.base+'/'+quote(safe_name(name)))[1]
    def put(self,name,body):
        if len(body)>MAX_PACKET:raise ValueError('Pacchetto troppo grande.')
        status,_=self.http.request('PUT',self.base+'/'+quote(safe_name(name)),body,{'If-None-Match':'*','Content-Type':'application/octet-stream'},accepted=(200,201,204,412))
        if not self.same(self.get(name),body):raise ValueError('Integrità della pubblicazione al servizio non verificata.')
        return status!=412
