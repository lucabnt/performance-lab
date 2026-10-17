"""Independent local archives and signed folder exchange identities.

Secrets stay in the local workspace, never in the synchronized folder. Invitations
are password encrypted. OS account protection is required for local secrets.
"""
import base64
import contextvars
import json
import os
import hashlib
import threading
import tempfile
from pathlib import Path
from uuid import uuid4
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from .store import Store, encoded

def b64(value): return base64.b64encode(value).decode()
def un64(value): return base64.b64decode(value,validate=True)
def private(): return Ed25519PrivateKey.generate()
def sign(key,body): return b64(Ed25519PrivateKey.from_private_bytes(un64(key)).sign(encoded(body).encode()))
def verify(key,body,signature): Ed25519PublicKey.from_public_bytes(un64(key)).verify(un64(signature),encoded(body).encode())


def seal(payload,password):
    if len(password)<12:raise ValueError('Usare una password di almeno 12 caratteri.')
    salt=os.urandom(16);key=Scrypt(salt=salt,length=32,n=2**14,r=8,p=1).derive(password.encode())
    return encoded({'salt':b64(salt),'encrypted':Fernet(base64.urlsafe_b64encode(key)).encrypt(encoded(payload).encode()).decode()}).encode()


def unseal(raw,password):
    envelope=json.loads(raw)
    salt=un64(envelope['salt'])
    if len(salt)!=16:raise ValueError('Formato cifrato non valido.')
    key=Scrypt(salt=salt,length=32,n=2**14,r=8,p=1).derive(password.encode())
    return json.loads(Fernet(base64.urlsafe_b64encode(key)).decrypt(envelope['encrypted'].encode()))


def validate_identity(identity):
    from uuid import UUID
    UUID(identity['workspace']);cert=identity['certificate'];UUID(cert['id'])
    if cert['workspace']!=identity['workspace'] or cert['role'] not in ('admin','viewer'):raise ValueError('Identità non valida.')
    verify(identity['authority_public'],cert,identity['certificate_signature'])
    Fernet(identity['sync_key'].encode())
    if cert['role']=='admin':
        if b64(Ed25519PrivateKey.from_private_bytes(un64(identity['private_key'])).public_key().public_bytes_raw())!=cert['public_key']:raise ValueError('Chiave operatore incoerente.')
    elif identity.get('private_key') or identity.get('authority_private'):raise ValueError('Identità visualizzatore incoerente.')
    if identity.get('authority_private') and b64(Ed25519PrivateKey.from_private_bytes(un64(identity['authority_private'])).public_key().public_bytes_raw())!=identity['authority_public']:raise ValueError('Chiave fondatore incoerente.')
    return identity


def fresh_identity(id,operator):
    authority=private();writer=private()
    cert={'id':str(uuid4()),'workspace':id,'name':operator,'role':'admin','public_key':b64(writer.public_key().public_bytes_raw())}
    return {'workspace':id,'authority_public':b64(authority.public_key().public_bytes_raw()),'authority_private':b64(authority.private_bytes_raw()),
        'certificate':cert,'certificate_signature':b64(authority.sign(encoded(cert).encode())), 'private_key':b64(writer.private_bytes_raw()),'sync_key':Fernet.generate_key().decode()}


def write_json(path,value):
    tmp=path.with_name(path.name+'.'+str(uuid4())+'.tmp')
    try:
        tmp.write_text(encoded(value),encoding='utf-8');os.chmod(tmp,0o600);tmp.replace(path)
    finally:tmp.unlink(missing_ok=True)


def revoke_member(store,id):
    identity=store.identity
    if not identity.get('authority_private'):raise ValueError('Solo il fondatore gestisce gli accessi.')
    if id==identity['certificate']['id']:raise ValueError('Non revocare il fondatore da questa procedura.')
    if id not in {m['id'] for m in member_directory(store)}:raise ValueError('Operatore non presente.')
    path=store.root/'revocations.json'
    old=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'version':0,'revoked':[],'accepted':{}}
    if id in old['revoked']:return
    accepted=old.get('accepted',{})
    # Freeze exact events already received. Backdating or reusing an event ID
    # cannot authorize future writes with a revoked private key.
    with store.connect() as db:
        for row in db.execute('SELECT body FROM changes'):
            change=json.loads(row[0])
            if change.get('certificate',{}).get('id')==id:
                accepted[change['id']]=hashlib.sha256(encoded(change).encode()).hexdigest()
    body={'workspace':identity['workspace'],'version':old['version']+1,'revoked':sorted(set(old['revoked']+[id])),'accepted':accepted}
    write_json(path,{**body,'signature':sign(identity['authority_private'],body)})


def member_directory(store):
    path=store.root/'members.json'
    people=[store.identity['certificate']]+(json.loads(path.read_text(encoding='utf-8')) if path.exists() else [])
    return list({p['id']:p for p in people}.values())


class SnapshotStore(Store):
    @property
    def identity(self):
        return {'snapshot':True,'certificate':{'id':'snapshot','name':'Backup dati — sola lettura','role':'viewer'}}
    def revocations(self):return []
    def sign_change(self,change):raise ValueError('Copia di consultazione: modifiche non consentite.')


class ArchiveStore(Store):
    @property
    def identity(self):
        return json.loads((self.root/'identity.json').read_text(encoding='utf-8'))

    def sign_change(self, change):
        identity=self.identity
        if identity['certificate']['role']!='admin' or identity['certificate']['id'] in self.revocations():
            raise ValueError('Visualizzatore: modifica non autorizzata.')
        body={**change,'workspace':identity['workspace'],'certificate':identity['certificate'],'certificate_signature':identity['certificate_signature']}
        return {**body,'signature':sign(identity['private_key'],body)}

    def verify_change(self,change):
        identity=self.identity
        if change.get('workspace')!=identity['workspace']:
            raise ValueError('Workspace del pacchetto errato.')
        certificate=change['certificate']
        verify(identity['authority_public'],certificate,change['certificate_signature'])
        if certificate['workspace']!=identity['workspace'] or certificate['role']!='admin':
            raise ValueError('Autore non autorizzato alla scrittura.')
        revoked=self.revocations()
        if certificate['id'] in revoked:
            rev=json.loads((self.root/'revocations.json').read_text(encoding='utf-8'))
            if rev.get('accepted',{}).get(change['id'])!=hashlib.sha256(encoded(change).encode()).hexdigest():
                raise ValueError('Autore revocato: operazione in quarantena.')
        verify(certificate['public_key'],{k:v for k,v in change.items() if k!='signature'},change['signature'])

    def revocations(self):
        path=self.root/'revocations.json'
        return json.loads(path.read_text())['revoked'] if path.exists() else []


class StoreProxy:
    def __init__(self,default):
        self.default=default
        self.selected=contextvars.ContextVar('selected_archive',default=default)
    def __getattr__(self,name):return getattr(self.selected.get(),name)


class Workspaces:
    def __init__(self,root,legacy):
        self.root=Path(root)
        self.registry=self.root/'workspaces.json'
        self.legacy=legacy
        self.proxy=StoreProxy(legacy)
        self.lock=threading.RLock()
    def entries(self):
        return json.loads(self.registry.read_text(encoding='utf-8')) if self.registry.exists() else []
    def register(self,entry):
        with self.lock:self._register(entry)
    def _register(self,entry):
        entries=self.entries()
        if any(e['id']==entry['id'] for e in entries):raise ValueError('Workspace già presente sul dispositivo.')
        target=Path(entry['path']).resolve()
        for e in entries:
            other=Path(e['path']).resolve()
            if target==other or target in other.parents or other in target.parents:
                raise ValueError('Le cartelle dei workspace non possono sovrapporsi.')
        write_json(self.registry,entries+[entry])
    def get(self,id):
        if not id:return self.legacy
        entry=next((e for e in self.entries() if e['id']==id),None)
        if not entry:raise ValueError('Workspace non associato a questo dispositivo.')
        return (SnapshotStore if entry.get('mode')=='snapshot' else ArchiveStore)(entry['path'])
    def create(self,name,operator,path=''):
        name=name.strip();operator=operator.strip()
        if not name or not operator:raise ValueError('Indicare società e nome del fondatore.')
        id=str(uuid4())
        identity=fresh_identity(id,operator)
        def build(stage):
            stage.mkdir();write_json(stage/'identity.json',identity)
            return ArchiveStore(stage).save('organization',{'name':name})['id']
        return self.install_new(id,name,path,build)

    def install_new(self,id,name,path,build):
        """Publish only a complete new archive; never overwrite an existing one."""
        with self.lock:
            root=Path(path).resolve() if path else (self.root/'workspaces'/id).resolve()
            if any(e['id']==id for e in self.entries()):raise ValueError('Società già collegata: per rinnovare usa Applica nuovo invito.')
            if root==self.root.resolve() or root in self.root.resolve().parents or root==self.root.resolve()/'objects' or self.root.resolve()/'objects' in root.parents:
                raise ValueError('La cartella deve essere separata dall’archivio principale.')
            for e in self.entries():
                other=Path(e['path']).resolve()
                if root==other or root in other.parents or other in root.parents:raise ValueError('Cartella sovrapposta a una società esistente.')
            if root.exists() and (not root.is_dir() or any(root.iterdir())):raise ValueError('Usare una cartella vuota.')
            was_empty=root.exists();root.parent.mkdir(parents=True,exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='.fuorigiri-create-',dir=root.parent) as tmp:
                stage=Path(tmp)/'archive';org_id=build(stage)
                entry={'id':id,'name':name,'path':str(root),'organization_id':org_id}
                if was_empty:root.rmdir()
                stage.rename(root)
                try:self.register(entry)
                except Exception:
                    root.rename(stage)
                    if was_empty:root.mkdir()
                    raise
            return entry


def invitation(store,name,role,password,replace_id=None):
    if len(password)<12:raise ValueError('Usare una password di almeno 12 caratteri per l’invito.')
    identity=store.identity
    if not identity.get('authority_private'):raise ValueError('Solo il dispositivo fondatore gestisce gli inviti.')
    writer=private()
    cert={'id':str(uuid4()),'workspace':identity['workspace'],'name':name,'role':role,'public_key':b64(writer.public_key().public_bytes_raw())}
    invited={k:identity[k] for k in ('workspace','authority_public','sync_key')}
    invited.update(certificate=cert,certificate_signature=sign(identity['authority_private'],cert),private_key=b64(writer.private_bytes_raw()) if role=='admin' else None)
    payload={'identity':invited,'organization':store.list('organization')[0]}
    result=seal(payload,password)
    if replace_id:revoke_member(store,replace_id)
    # Keep only public membership information, not the recipient's private key.
    path=store.root/'members.json';members=json.loads(path.read_text()) if path.exists() else []
    write_json(path,members+[cert])
    access_path=store.root/'access.json'
    version=json.loads(access_path.read_text(encoding='utf-8'))['version']+1 if access_path.exists() else 1
    access={'workspace':identity['workspace'],'version':version,'founder_id':identity['certificate']['id'],'members':member_directory(store)}
    write_json(access_path,{**access,'signature':sign(identity['authority_private'],access)})
    return result


def join(manager,raw,password,path=''):
    payload=unseal(raw,password)
    identity=validate_identity(payload['identity'])
    if identity.get('authority_private'):raise ValueError('Usare il percorso di recupero per il fondatore.')
    id=identity['workspace']
    # Validate IDs before using them as relative filesystem components.
    from uuid import UUID
    UUID(id)
    def build(stage):
        stage.mkdir();write_json(stage/'identity.json',identity);ArchiveStore(stage)
        return payload['organization']['id']
    return manager.install_new(id,payload['organization']['name'],path,build)


def apply_invitation(store,raw,password):
    payload=unseal(raw,password);identity=validate_identity(payload['identity'])
    if identity.get('authority_private') or store.identity.get('snapshot'):raise ValueError('Invito non applicabile a questo archivio.')
    if identity['workspace']!=store.identity['workspace'] or identity['authority_public']!=store.identity['authority_public']:raise ValueError('Invito di un’altra società.')
    if store.identity.get('authority_private'):raise ValueError('Non sostituire il fondatore con un invito collaboratore.')
    if identity['certificate']['id'] in store.revocations():raise ValueError('Invito già revocato.')
    write_json(store.root/'identity.json',identity)
    return {'updated':True,'role':identity['certificate']['role']}
