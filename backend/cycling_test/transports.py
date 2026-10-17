"""Small, immutable-object transport contract shared by desktop and Android."""
import base64
import os
import re
import socket
import ssl
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, build_opener, HTTPSHandler, HTTPRedirectHandler
from uuid import uuid4
from xml.etree import ElementTree as ET

MAX_PACKET = 80_000_000
MAX_INVENTORY = 16_000_000
MAX_FILES = 100_000


def safe_name(name):
    if not isinstance(name,str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,199}',name) or '..' in name:
        raise ValueError('Nome remoto non valido.')
    return name


class FolderTransport:
    remote = False

    def __init__(self, folder, channel, store_root):
        folder=Path(folder).resolve();root=Path(store_root).resolve()
        if not folder.is_dir():raise ValueError('La cartella deve già esistere ed essere disponibile offline.')
        if folder==root or root in folder.parents or folder in root.parents:
            raise ValueError('La cartella di scambio deve essere separata dall’archivio locale.')
        from .compatibility import channel_directory
        self.root=channel_directory(folder,channel);self.root.mkdir(exist_ok=True)

    def list(self):
        names=sorted(p.name for p in self.root.iterdir() if p.is_file() and not p.is_symlink() and not p.name.endswith('.tmp'))
        if len(names)>MAX_FILES:raise ValueError('Inventario troppo grande.')
        return names

    def get(self,name):
        path=self.root/safe_name(name)
        if path.is_symlink():raise ValueError('Collegamento simbolico non ammesso nel canale.')
        if path.stat().st_size>MAX_PACKET:raise ValueError('Pacchetto troppo grande.')
        return path.read_bytes()

    def put(self,name,data):
        path=self.root/safe_name(name)
        if len(data)>MAX_PACKET:raise ValueError('Pacchetto troppo grande.')
        if path.exists():
            if self.get(name)!=data:raise ValueError('Oggetto immutabile già presente con contenuto diverso.')
            return False
        temp=self.root/(str(uuid4())+'.tmp')
        try:
            with temp.open('xb') as stream:
                stream.write(data);stream.flush();os.fsync(stream.fileno())
            # Hard-link publication is atomic and cannot replace another writer.
            try:
                if os.name=='nt':os.rename(temp,path)  # Windows rename never replaces an existing destination.
                else:os.link(temp,path)
            except FileExistsError:
                if self.get(name)!=data:raise ValueError('Pubblicazione concorrente incompatibile.')
                return False
        finally:temp.unlink(missing_ok=True)
        return True


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None


def validate_url(url, allow_loopback=False):
    parsed=urlsplit(url)
    local=allow_loopback and parsed.scheme=='http' and parsed.hostname in ('127.0.0.1','localhost','::1')
    if not (parsed.scheme=='https' or local) or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('Usare un URL WebDAV HTTPS senza password, query o frammenti.')
    if any(c in url for c in ('\r','\n','\\')) or any(x in ('.','..') for x in unquote(parsed.path).split('/')):
        raise ValueError('Percorso WebDAV non valido.')
    return url.rstrip('/')+'/'


class WebDAVTransport:
    """RFC 4918. No redirects, unverified TLS, deletes or mutable overwrites.

    Retry restarts the individual immutable object, never the whole database.
    A timeout after a committed PUT is resolved by GET and byte verification.
    """
    remote=True

    def __init__(self,url,username,password,channel,*,allow_loopback=False,timeout=25):
        self.base=validate_url(url,allow_loopback)+quote(safe_name('fuorigiri-'+channel))+'/'
        self.auth='Basic '+base64.b64encode((username+':'+password).encode()).decode()
        self.timeout=timeout
        self.opener=build_opener(NoRedirect(),HTTPSHandler(context=ssl.create_default_context()))

    def request(self,method,name='',data=None,headers=None,accepted=(200,)):
        target=self.base+quote(safe_name(name)) if name else self.base
        for attempt in range(3):
            try:
                req=Request(target,data=data,method=method,headers={'Authorization':self.auth,'User-Agent':'Fuorigiri/0.6',**(headers or {})})
                with self.opener.open(req,timeout=self.timeout) as response:
                    if response.status not in accepted:raise ValueError('Risposta WebDAV non supportata.')
                    limit=MAX_INVENTORY if method=='PROPFIND' else MAX_PACKET
                    body=response.read(limit+1)
                    if len(body)>limit:raise ValueError('Risposta WebDAV troppo grande.')
                    return response.status,body
            except HTTPError as exc:
                code=exc.code;exc.close()
                if code in accepted:return code,b''
                if code in (408,429,500,502,503,504) and attempt<2:
                    time.sleep(0.4*(2**attempt));continue
                messages={401:'Autenticazione WebDAV rifiutata.',403:'Permessi WebDAV insufficienti.',404:'Cartella WebDAV non trovata.',409:'Creare prima la cartella WebDAV indicata.',412:'Oggetto remoto già presente.',301:'Redirect WebDAV non consentito: usare l’URL finale.',302:'Redirect WebDAV non consentito: usare l’URL finale.'}
                raise ValueError(messages.get(code,f'WebDAV: errore HTTP {code}.')) from None
            except (URLError,TimeoutError,socket.timeout,OSError):
                if attempt<2:time.sleep(0.4*(2**attempt));continue
                raise ValueError('WebDAV non raggiungibile o certificato TLS non valido. Dati locali conservati; riprovare.') from None

    def list(self):
        body=b'<?xml version="1.0"?><d:propfind xmlns:d="DAV:"><d:prop><d:resourcetype/></d:prop></d:propfind>'
        status,raw=self.request('PROPFIND',data=body,headers={'Depth':'1','Content-Type':'application/xml'},accepted=(207,404))
        if status==404:
            self.request('MKCOL',accepted=(201,405))
            _,raw=self.request('PROPFIND',data=body,headers={'Depth':'1','Content-Type':'application/xml'},accepted=(207,))
        if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():raise ValueError('XML WebDAV non valido.')
        try:tree=ET.fromstring(raw)
        except ET.ParseError:raise ValueError('Inventario WebDAV non valido.') from None
        base=urlsplit(self.base);basepath=unquote(base.path)
        names=[]
        for item in tree.findall('{DAV:}response'):
            href=item.findtext('{DAV:}href','');parsed=urlsplit(href)
            if parsed.netloc and (parsed.scheme,parsed.netloc)!=(base.scheme,base.netloc):raise ValueError('Inventario WebDAV esterno alla destinazione.')
            path=unquote(parsed.path)
            if path.rstrip('/')==basepath.rstrip('/'):continue
            if not path.startswith(basepath):raise ValueError('Inventario WebDAV fuori dal canale.')
            name=path[len(basepath):]
            if item.find('.//{DAV:}collection') is not None:continue
            names.append(safe_name(name))
        if len(names)>MAX_FILES:raise ValueError('Inventario WebDAV troppo grande.')
        return sorted(set(names))

    def get(self,name):return self.request('GET',name)[1]

    def put(self,name,data):
        if len(data)>MAX_PACKET:raise ValueError('Pacchetto troppo grande.')
        status,_=self.request('PUT',name,data,{'If-None-Match':'*','Content-Type':'application/octet-stream'},accepted=(200,201,204,412))
        if self.get(name)!=data:raise ValueError('Integrità della pubblicazione WebDAV non confermata; riprovare senza eliminare file.')
        return status!=412
