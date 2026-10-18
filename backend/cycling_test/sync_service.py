"""Per-archive connection state and sanitized, hash-linked local sync audit."""
import hashlib
import json
import threading
from datetime import datetime, timezone
from .store import encoded
from .workspaces import write_json
from . import credentials
from .transports import WebDAVTransport, validate_url

_locks={}
_guard=threading.Lock()


def lock(root):
    with _guard:return _locks.setdefault(str(root.resolve()),threading.RLock())


def require_managed(store):
    if not hasattr(store,'identity') or store.identity.get('snapshot'):
        raise ValueError('Selezionare una società con accesso personale, non una copia di consultazione.')


def configuration(store):
    path=store.root/'sync-connection.json'
    previous=store.root/'sync-folder.txt'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'transport':'folder','folder':previous.read_text(encoding='utf-8') if previous.exists() else ''}


def configure(store,data):
    require_managed(store)
    with lock(store.root):
        if data['transport']=='webdav':
            url=validate_url(data['url'])
            username=data['username'].strip()
            if not username or ':' in username:raise ValueError('Nome utente WebDAV non valido.')
            if data.get('password'):credentials.save(store.root,data['password'])
            else:credentials.read(store.root)
            value={'transport':'webdav','url':url,'username':username}
        elif data['transport'] in ('drive','dropbox','onedrive','service'):
            from .cloud import load_secret,save_secret
            import re
            kind=data['transport']
            value={k:data.get(k,'') for k in ('transport','client_id','root_id','root_path','drive_id','drive_scope','url')}
            if kind=='service':
                value['url']=validate_url(value['url'])
            elif not value['client_id'].strip():raise ValueError('Client ID OAuth obbligatorio.')
            if kind in ('drive','onedrive') and not re.fullmatch(r'[A-Za-z0-9_!.-]{1,300}',value['root_id']):raise ValueError('Indicare l’ID della cartella condivisa.')
            if kind=='dropbox' and value['root_path'] and not value['root_path'].startswith('/'):raise ValueError('Percorso Dropbox deve iniziare con /.')
            if data.get('password'):
                secret=load_secret(store.root,kind,value['client_id'])
                secret['token' if kind=='service' else 'client_secret']=data['password']
                save_secret(store.root,kind,secret,value['client_id'])
        else:value={'transport':'folder','folder':data.get('folder','')}
        write_json(store.root/'sync-connection.json',value)
    return value


def transport(store,config):
    key=store.identity['sync_key'];channel=hashlib.sha256(key.encode()).hexdigest()[:24]
    if config['transport']=='webdav':
        return WebDAVTransport(config['url'],config['username'],credentials.read(store.root),channel)
    if config['transport'] in ('drive','dropbox','onedrive','service'):
        from .cloud import DriveTransport,DropboxTransport,OneDriveTransport,DedicatedTransport
        return {'drive':DriveTransport,'dropbox':DropboxTransport,'onedrive':OneDriveTransport,'service':DedicatedTransport}[config['transport']](store.root,config,channel)
    from .transports import FolderTransport
    return FolderTransport(config['folder'],channel,store.root)


def audit(store,result):
    """Diagnostic integrity, not protection against an administrator rewriting disk."""
    with store.connect() as db:
        db.execute('CREATE TABLE IF NOT EXISTS sync_audit (seq INTEGER PRIMARY KEY, body TEXT NOT NULL, digest TEXT NOT NULL)')
        previous=db.execute('SELECT digest FROM sync_audit ORDER BY seq DESC LIMIT 1').fetchone()
        body=encoded({'at':datetime.now(timezone.utc).isoformat(),'previous':previous[0] if previous else None,**result})
        db.execute('INSERT INTO sync_audit(body,digest) VALUES(?,?)',(body,hashlib.sha256(body.encode()).hexdigest()))


def run_sync(store):
    require_managed(store)
    with lock(store.root):
        config=configuration(store)
        if (store.root/'rotation-pending.json').exists():raise ValueError('Rotazione interrotta: completare Ruota chiave prima di sincronizzare.')
        at=datetime.now(timezone.utc).isoformat()
        try:
            from .sync import exchange
            result=exchange(store,None,store.identity['sync_key'],transport(store,config))
            state={'at':at,'ok':not result['errors'] and not result['pending'],**result}
            write_json(store.root/'last-sync.json',state)
            audit(store,{'ok':state['ok'],**{k:result[k] for k in ('transport','published','received','pending','conflicts')},'invalid_packets':len(result['errors'])})
            return result
        except (ValueError,OSError):
            write_json(store.root/'last-sync.json',{'at':at,'ok':False,'error':'Scambio non completato. Controllare connessione, accessi e conflitti; dati locali conservati.'})
            audit(store,{'ok':False,'transport':config['transport']})
            raise


def rotate(store):
    """Publish a signed stop notice to the old channel before changing the key.

    The durable local journal makes retry safe across interruption at either step.
    Existing downloaded data is not revoked. New invitations are required.
    """
    require_managed(store)
    if not store.identity.get('authority_private'):raise ValueError('Solo il fondatore ruota la chiave del canale.')
    from cryptography.fernet import Fernet
    from .workspaces import sign
    with lock(store.root):
        journal=store.root/'rotation-pending.json'
        if journal.exists():pending=json.loads(journal.read_text(encoding='utf-8'))
        else:
            result=run_sync(store)
            if result['errors'] or result['pending'] or result['conflicts']:raise ValueError('Risolvere prima pacchetti in attesa, errori e conflitti.')
            old=store.identity;new={**old,'sync_key':Fernet.generate_key().decode()}
            body={'workspace':old['workspace'],'from':hashlib.sha256(old['sync_key'].encode()).hexdigest(),
                  'to':hashlib.sha256(new['sync_key'].encode()).hexdigest(),'at':datetime.now(timezone.utc).isoformat()}
            pending={'identity':new,'notice':{**body,'signature':sign(old['authority_private'],body)}}
            write_json(journal,pending)
        # With an unfinished journal the identity still contains the old key.
        if store.identity['sync_key']!=pending['identity']['sync_key']:
            transport(store,configuration(store)).put('rotation.json',encoded(pending['notice']).encode())
            write_json(store.root/'identity.json',pending['identity'])
        audit(store,{'action':'channel_key_rotated','ok':True})
        journal.unlink()
        return {'rotated':True,'note':'Nuovo canale: eseguire uno scambio, rinnovare gli inviti dei dispositivi autorizzati e scaricare un nuovo recupero accessi. Le copie già scaricate restano leggibili.'}


def install_sync_api(app,store):
    from pydantic import BaseModel,ConfigDict,Field
    from typing import Literal
    class Connection(BaseModel):
        model_config=ConfigDict(extra='forbid')
        transport: Literal['folder','webdav','drive','dropbox','onedrive','service']
        client_id: str=Field(default='',max_length=500)
        root_id: str=Field(default='',max_length=300)
        root_path: str=Field(default='',max_length=2000)
        drive_id: str=Field(default='',max_length=300)
        drive_scope: Literal['','file','full']='file'
        folder: str=Field(default='',max_length=2000)
        url: str=Field(default='',max_length=2000)
        username: str=Field(default='',max_length=300)
        password: str=Field(default='',max_length=2000)

    @app.get('/api/v1/sync/connection')
    def connection():
        require_managed(store)
        last=store.root/'last-sync.json'
        config=configuration(store);account_status=None
        if config['transport'] in ('drive','dropbox','onedrive','service'):
            from .cloud import load_secret
            try:
                value=load_secret(store.root,config['transport'],config.get('client_id',''))
                account_status='connected' if value.get('access_token') or value.get('token') else 'disconnected'
            except ValueError:account_status='vault_unavailable'
        return {'connection':config,'account_status':account_status,'last_sync':json.loads(last.read_text(encoding='utf-8')) if last.exists() else None}

    @app.post('/api/v1/sync/connection')
    def save_connection(data:Connection):return configure(store,data.model_dump())

    class OAuthRequest(BaseModel):
        mobile: bool=False
    @app.post('/api/v1/sync/oauth/start')
    def oauth_start(data:OAuthRequest):
        require_managed(store)
        from .cloud import begin_oauth
        return begin_oauth(store,configuration(store),data.mobile)

    @app.get('/api/v1/sync/oauth/status/{session}')
    def oauth_state(session:str):
        from .cloud import oauth_status
        return oauth_status(store,session)

    class OAuthCallback(BaseModel):
        url: str=Field(max_length=8000)
    @app.post('/api/v1/sync/oauth/callback')
    def oauth_callback(data:OAuthCallback):
        from .cloud import oauth_status,finish_oauth
        from urllib.parse import urlsplit,parse_qs
        state=parse_qs(urlsplit(data.url).query).get('state',[''])[0]
        oauth_status(store,state)
        return finish_oauth(data.url)

    @app.post('/api/v1/sync/oauth/disconnect')
    def oauth_disconnect():
        from .cloud import save_secret
        config=configuration(store)
        if config['transport'] not in ('drive','dropbox','onedrive','service'):raise ValueError('Nessun account OAuth selezionato.')
        from .cloud import _guard,_sessions
        with lock(store.root),_guard:
            for session in _sessions.values():
                if session['root'].resolve()==store.root.resolve() and session['config']['transport']==config['transport'] and session['status'] in ('pending','exchanging'):session['status']='cancelled'
            save_secret(store.root,config['transport'],{},config.get('client_id',''))
        return {'disconnected':True}

    @app.post('/api/v1/sync/run')
    def sync():return run_sync(store)

    @app.post('/api/v1/sync/rotate')
    def rotate_key():return rotate(store)

    @app.get('/api/v1/sync/audit')
    def read_audit():
        require_managed(store)
        with store.connect() as db:
            if not db.execute("SELECT 1 FROM sqlite_master WHERE name='sync_audit'").fetchone():return []
            return [{'seq':r[0],**json.loads(r[1]),'digest':r[2]} for r in db.execute('SELECT seq,body,digest FROM sync_audit ORDER BY seq DESC LIMIT 100')]
