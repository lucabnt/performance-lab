import json
from typing import Literal
from fastapi import UploadFile, Form
from pydantic import BaseModel,Field
from .workspaces import invitation, join, sign
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

    @app.get('/api/v1/workspaces')
    def list_workspaces():
        return manager.entries()
    @app.post('/api/v1/workspaces')
    def create(data: Create):
        return manager.create(data.name,data.operator,data.path)
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
        return download(invitation(store,data.name,data.role,data.password),'application/json','invito-ciclotest.json')
    @app.get('/api/v1/workspace/members')
    def members():
        if not hasattr(store,'identity'):return {'members':[],'folder':'','managed':False}
        path=store.root/'members.json';folder=store.root/'sync-folder.txt'
        return {'members':[store.identity['certificate']]+(json.loads(path.read_text()) if path.exists() else []),
                'revoked':store.revocations(),'folder':folder.read_text() if folder.exists() else '', 'managed':True,
                'owner':bool(store.identity.get('authority_private'))}
    @app.post('/api/v1/workspace/revoke/{id}')
    def revoke(id: str):
        if not hasattr(store,'identity') or not store.identity.get('authority_private'):raise ValueError('Solo il dispositivo fondatore revoca gli accessi.')
        if id==store.identity['certificate']['id']:raise ValueError('Non revocare il fondatore da questa procedura.')
        from uuid import UUID
        UUID(id)
        path=store.root/'revocations.json'
        old=json.loads(path.read_text()) if path.exists() else {'version':0,'revoked':[]}
        body={'workspace':store.identity['workspace'],'version':old['version']+1,'revoked':sorted(set(old['revoked']+[id]))}
        body['signature']=sign(store.identity['authority_private'],body)
        path.write_text(encoded(body),encoding='utf-8')
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
