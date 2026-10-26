"""In-process ASGI adapter: identical routes/validation, no listening socket.

    Android WebView -> origin-restricted Kotlin message -> Python -> ASGI.
    This adapter is also exercised on desktop in the shared contract tests.
"""
import base64
import json
import os
import secrets
from pathlib import Path
from urllib.parse import urlsplit

MAX_BODY=80_000_000


class MobileRuntime:
    def __init__(self,root,assets=None,secret_store=None):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True)
        os.environ.setdefault('MPLCONFIGDIR',str(self.root/'plot-cache'))
        if assets:
            from . import branding
            branding.MOBILE_ASSETS=Path(assets)
        if secret_store is not None:
            from . import credentials
            class Keystore:
                def refresh_google_token(self,scope):return secret_store.googleToken(scope)
                def set_password(self,service,account,password):secret_store.put(service+':'+account,password)
                def get_password(self,service,account):return secret_store.get(service+':'+account)
            credentials._mobile=Keystore()
        from .api import create_app
        self.token=secrets.token_urlsafe(32)
        self.app=create_app(self.root,self.token,frontend=self.root/'no-web-server')

    def request(self,raw):
        import asyncio
        try:
            message=json.loads(raw)
            path=message['path'];parsed=urlsplit(path)
            if not path.startswith('/api/v1/') or parsed.scheme or parsed.netloc or '\\' in path or '..' in path:
                raise ValueError('Comando mobile non valido.')
            if message['method'] not in ('GET','POST','PUT','DELETE','HEAD'):raise ValueError('Metodo mobile non consentito.')
            body=base64.b64decode(message.get('body',''),validate=True)
            if len(body)>MAX_BODY:raise ValueError('File troppo grande per il bridge mobile (80 MB).')
            headers={k.lower():str(v) for k,v in message.get('headers',{}).items() if k.lower() in ('content-type','x-fuorigiri-workspace')}
            headers.update({'host':'127.0.0.1','x-fuorigiri-token':self.token})
            result=asyncio.run(self.dispatch(message['method'],parsed,headers,body))
        except (ValueError,KeyError,TypeError):
            result={'status':422,'headers':{'content-type':'application/json'},'body':base64.b64encode(json.dumps({'detail':'Richiesta mobile non valida o oltre i limiti.'}).encode()).decode()}
        return json.dumps(result,separators=(',',':'))

    async def dispatch(self,method,parsed,headers,body):
        import httpx
        # ASGITransport executes the real application, including authorization,
        # workspace context, multipart parsing and native binary report routes.
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=self.app),base_url='http://127.0.0.1') as client:
            response=await client.request(method,parsed.path+('?' + parsed.query if parsed.query else ''),headers=headers,content=body)
            content=await response.aread()
            if len(content)>MAX_BODY:raise ValueError('Risposta mobile troppo grande.')
            return {'status':response.status_code,'headers':dict(response.headers),'body':base64.b64encode(content).decode()}

    def finish_cloud_oauth(self,url):
        from .cloud import finish_oauth
        return finish_oauth(url)

    def google_authorized(self,state,token):
        from .cloud import finish_google
        return finish_google(state,token)

    def sync_all(self):
        """WorkManager entry. No UI, no automatic configuration or new access."""
        from .workspaces import Workspaces
        from .store import Store
        from .sync_service import configuration
        from .sync_jobs import start,wait
        manager=Workspaces(self.root,Store(self.root));failed=0
        for entry in manager.entries():
            store=manager.get(entry['id'])
            if entry.get('mode')=='snapshot' or configuration(store)['transport'] not in ('webdav','drive','dropbox','onedrive','service'):continue
            try:
                start(store)
                job=wait(store)
                result=job.get('result',{})
                failed+=int(job['status']!='completed' or bool(result.get('errors') or result.get('pending')))
            except (ValueError,OSError):failed+=1
        return failed==0
