"""Independent local archives and signed folder exchange identities.

Secrets stay in the local workspace, never in the synchronized folder. Invitations
are password encrypted. OS account protection is required for local secrets.
"""
import base64
import contextvars
import json
import os
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
    def entries(self):
        return json.loads(self.registry.read_text(encoding='utf-8')) if self.registry.exists() else []
    def register(self,entry):
        entries=self.entries()
        if any(e['id']==entry['id'] for e in entries):raise ValueError('Workspace già presente sul dispositivo.')
        target=Path(entry['path']).resolve()
        for e in entries:
            other=Path(e['path']).resolve()
            if target==other or target in other.parents or other in target.parents:
                raise ValueError('Le cartelle dei workspace non possono sovrapporsi.')
        self.registry.write_text(encoded(entries+[entry]),encoding='utf-8')
    def get(self,id):
        if not id:return self.legacy
        entry=next((e for e in self.entries() if e['id']==id),None)
        if not entry:raise ValueError('Workspace non associato a questo dispositivo.')
        return ArchiveStore(entry['path'])
    def create(self,name,operator,path=''):
        id=str(uuid4());root=Path(path).resolve() if path else self.root/'workspaces'/id
        if root.exists() and any(root.iterdir()):raise ValueError('Usare una cartella vuota per il nuovo workspace.')
        authority=private();writer=private()
        cert={'id':str(uuid4()),'workspace':id,'name':operator,'role':'admin','public_key':b64(writer.public_key().public_bytes_raw())}
        identity={'workspace':id,'authority_public':b64(authority.public_key().public_bytes_raw()),'authority_private':b64(authority.private_bytes_raw()),
                  'certificate':cert,'certificate_signature':b64(authority.sign(encoded(cert).encode())), 'private_key':b64(writer.private_bytes_raw()),'sync_key':Fernet.generate_key().decode()}
        root.mkdir(parents=True,exist_ok=True)
        (root/'identity.json').write_text(encoded(identity),encoding='utf-8')
        os.chmod(root/'identity.json',0o600)
        store=ArchiveStore(root);org=store.save('organization',{'name':name})
        entry={'id':id,'name':name,'path':str(root),'organization_id':org['id']}
        self.register(entry)
        return entry


def invitation(store,name,role,password):
    if len(password)<12:raise ValueError('Usare una password di almeno 12 caratteri per l’invito.')
    identity=store.identity
    if not identity.get('authority_private'):raise ValueError('Solo il dispositivo fondatore gestisce gli inviti.')
    writer=private()
    cert={'id':str(uuid4()),'workspace':identity['workspace'],'name':name,'role':role,'public_key':b64(writer.public_key().public_bytes_raw())}
    invited={k:identity[k] for k in ('workspace','authority_public','sync_key')}
    invited.update(certificate=cert,certificate_signature=sign(identity['authority_private'],cert),private_key=b64(writer.private_bytes_raw()) if role=='admin' else None)
    payload={'identity':invited,'organization':store.list('organization')[0]}
    salt=os.urandom(16);key=Scrypt(salt=salt,length=32,n=2**14,r=8,p=1).derive(password.encode())
    body={'salt':b64(salt),'encrypted':Fernet(base64.urlsafe_b64encode(key)).encrypt(encoded(payload).encode()).decode()}
    # Keep only public membership information, not the recipient's private key.
    path=store.root/'members.json';members=json.loads(path.read_text()) if path.exists() else []
    path.write_text(encoded(members+[cert]),encoding='utf-8')
    return encoded(body).encode()


def join(manager,raw,password,path=''):
    envelope=json.loads(raw);key=Scrypt(salt=un64(envelope['salt']),length=32,n=2**14,r=8,p=1).derive(password.encode())
    payload=json.loads(Fernet(base64.urlsafe_b64encode(key)).decrypt(envelope['encrypted'].encode()))
    identity=payload['identity'];cert=identity['certificate']
    verify(identity['authority_public'],cert,identity['certificate_signature'])
    id=identity['workspace'];root=Path(path).resolve() if path else manager.root/'workspaces'/id
    # Validate IDs before using them as relative filesystem components.
    from uuid import UUID
    UUID(id)
    if root.exists() and any(root.iterdir()):raise ValueError('Usare una cartella vuota.')
    root.mkdir(parents=True,exist_ok=True);(root/'identity.json').write_text(encoded(identity),encoding='utf-8');os.chmod(root/'identity.json',0o600)
    ArchiveStore(root)
    entry={'id':id,'name':payload['organization']['name'],'organization_id':payload['organization']['id'],'path':str(root)}
    manager.register(entry)
    return entry
