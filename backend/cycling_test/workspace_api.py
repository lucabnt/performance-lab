import json
from typing import Literal
from fastapi import UploadFile, Form, File
from pydantic import BaseModel,Field
from .workspaces import invitation, join, revoke_member, member_directory, apply_invitation
from .store import encoded


def install_workspaces(app,manager,store,download):
    class Create(BaseModel):
        name: str=Field(min_length=1,max_length=300)
        operator: str=Field(min_length=1,max_length=300)
        path: str=''
    class Invite(BaseModel):
        name: str=Field(min_length=1,max_length=300)
        role: Literal['admin','viewer']
        password: str=Field(min_length=12)
        replace_id: str | None = None

    class RecoveryPassword(BaseModel):
        password: str=Field(min_length=12,max_length=1000)

    @app.get('/api/v1/workspaces')
    def list_workspaces():
        return manager.entries()

    @app.post('/api/v1/workspaces/restore/preview')
    def restore_preview(file: UploadFile):
        from .recovery import inspect_backup,summary,MAX_UPLOAD
        import hashlib,os
        raw=file.file.read(MAX_UPLOAD+1)
        data=inspect_backup(raw)
        digest=hashlib.sha256(raw).hexdigest()
        pending=manager.root/'restore-staging';pending.mkdir(exist_ok=True)
        path=pending/digest
        if not path.exists():
            from uuid import uuid4
            temp=pending/(str(uuid4())+'.tmp');temp.write_bytes(raw);os.chmod(temp,0o600);temp.replace(path)
        return {**summary(data),'backup_hash':digest}

    @app.post('/api/v1/workspaces/restore')
    def restore_archive(backup_hash: str=Form(),mode: Literal['snapshot','independent','recover']=Form(),path: str=Form(''),operator: str=Form(''),
                        password: str=Form(''),recovery_file: UploadFile | None=File(default=None)):
        from .recovery import restore
        import re,hashlib
        if not re.fullmatch('[0-9a-f]{64}',backup_hash):raise ValueError('Identificatore backup non valido.')
        pending=manager.root/'restore-staging'/backup_hash
        try:raw=pending.read_bytes()
        except FileNotFoundError as exc:raise ValueError('Ripetere l’anteprima del backup.') from exc
        if hashlib.sha256(raw).hexdigest()!=backup_hash:raise ValueError('Anteprima non integra: ricaricare il backup.')
        recovery_raw=recovery_file.file.read(1_000_001) if recovery_file else None
        if recovery_raw and len(recovery_raw)>1_000_000:raise ValueError('File di recupero troppo grande.')
        try:result=restore(manager,raw,mode,path,operator,recovery_raw,password)
        except OSError as exc:raise ValueError('Ripristino non completato: cartella non disponibile o scrittura non riuscita. Nessun archivio esistente sovrascritto.') from exc
        try:pending.unlink(missing_ok=True)
        except OSError:pass  # Cache cleanup must not turn a published restore into a reported failure.
        return result

    @app.post('/api/v1/workspaces/access')
    def replace_access(file: UploadFile,password: str=Form()):
        if not hasattr(store,'identity'):raise ValueError('Selezionare la società prima di applicare il nuovo invito.')
        raw=file.file.read(1_000_001)
        if len(raw)>1_000_000:raise ValueError('Invito troppo grande.')
        from .sync_service import lock
        try:
            with lock(store.root):return apply_invitation(store,raw,password)
        except ValueError:raise
        except Exception as exc:raise ValueError('Invito non valido o password errata.') from exc

    @app.post('/api/v1/workspace/recovery')
    def recovery(data: RecoveryPassword):
        from .recovery import export_recovery
        if not hasattr(store,'identity'):raise ValueError('Selezionare una società con fondatore.')
        return download(export_recovery(store,data.password),'application/json','fuorigiri-recupero-accessi.json')
    @app.post('/api/v1/workspaces')
    def create(data: Create):
        try:return manager.create(data.name,data.operator,data.path)
        except OSError as exc:raise ValueError('Creazione non completata: verificare cartella e permessi di scrittura.') from exc
    @app.post('/api/v1/workspaces/join')
    def join_workspace(file: UploadFile,password: str=Form(),path: str=Form('')):
        raw=file.file.read(1_000_001)
        if len(raw)>1_000_000:raise ValueError('Invito troppo grande.')
        try:return join(manager,raw,password,path)
        except Exception as exc:
            raise ValueError('Invito non valido, password errata o cartella non disponibile.') from exc
    @app.post('/api/v1/workspace/invite')
    def invite(data: Invite):
        if not hasattr(store,'identity'):raise ValueError('Creare un workspace separato prima di condividere.')
        from .sync_service import lock
        with lock(store.root):
            return download(invitation(store,data.name,data.role,data.password,data.replace_id),'application/json','fuorigiri-invito.json')
    @app.get('/api/v1/workspace/members')
    def members():
        if not hasattr(store,'identity'):return {'members':[],'folder':'','managed':False}
        if store.identity.get('snapshot'):return {'members':[],'folder':'','managed':False,'snapshot':True,'current':store.identity['certificate'],'owner':False}
        path=store.root/'members.json';folder=store.root/'sync-folder.txt'
        directory=store.root/'access.json'
        directory_data=json.loads(directory.read_text(encoding='utf-8')) if directory.exists() else {}
        members=directory_data.get('members',member_directory(store))
        members=list({m['id']:m for m in members+[store.identity['certificate']]}.values())
        last_sync=store.root/'last-sync.json'
        return {'members':members,'current':store.identity['certificate'],'path':str(store.root),
                'founder_id':directory_data.get('founder_id',store.identity['certificate']['id'] if store.identity.get('authority_private') else None),
                'last_sync':json.loads(last_sync.read_text(encoding='utf-8')) if last_sync.exists() else None,
                'ready':bool(store.list('organization')),
                'revoked':store.revocations(),'folder':folder.read_text() if folder.exists() else '', 'managed':True,
                'owner':bool(store.identity.get('authority_private'))}
    @app.post('/api/v1/workspace/revoke/{id}')
    def revoke(id: str):
        if not hasattr(store,'identity') or not store.identity.get('authority_private'):raise ValueError('Solo il dispositivo fondatore revoca gli accessi.')
        if id==store.identity['certificate']['id']:raise ValueError('Non revocare il fondatore da questa procedura.')
        from .sync_service import lock
        with lock(store.root):revoke_member(store,id)
        return {'revoked':id,'note':'Revoca delle scritture recepita dai PC al prossimo scambio. Le copie già ricevute restano disponibili.'}
    @app.get('/api/v1/reports')
    def reports():return store.list('report')
    @app.get('/api/v1/reports/{id}/download')
    def report(id: str):
        r=store.get(id)
        if r['kind']!='report':raise ValueError('Artefatto non valido.')
        return download(store.read_object(r['objects'][0]),'application/pdf' if r['format']=='pdf' else 'application/zip','report.'+('pdf' if r['format']=='pdf' else 'zip'))

    class Resolution(BaseModel):
        choice: Literal['local','remote']

    @app.post('/api/v1/conflicts/{id}/resolve')
    def resolve(id: str,data: Resolution):
        with store.connect() as db:
            row=db.execute('SELECT body FROM conflicts WHERE id=?',(id,)).fetchone()
        if not row:raise ValueError('Conflitto non trovato o già risolto.')
        incoming=json.loads(row[0]);current=store.get(incoming['record']['id'])
        payload=current if data.choice=='local' else incoming['record']
        saved=store.save(current['kind'],payload,current['id'],current['revision'],parents=[id])
        with store.connect() as db:db.execute('DELETE FROM conflicts WHERE id=?',(id,))
        return saved
