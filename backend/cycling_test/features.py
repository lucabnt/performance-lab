"""Archive editing, protocols, CSV staging and common historical queries."""
import json
from datetime import date
from typing import Literal
from fastapi import UploadFile, Form
from .store import encoded


def install_features(app, store, require, download, preview):
    from .api import Model, TestInput
    from pydantic import Field

    class Status(Model):
        base: str
        status: Literal['active','archived','deleted']

    class Revision(Model):
        base: str
        reason: str = Field(min_length=1, max_length=1000)
        test: TestInput

    class Segment(Model):
        duration_s: float = Field(gt=0, le=86400)
        start_w: float = Field(ge=0, le=3000)
        end_w: float = Field(ge=0, le=3000)
        phase: Literal['warmup','increment','recovery','cooldown'] = 'increment'

    class Protocol(Model):
        name: str = Field(min_length=1,max_length=300)
        family: str = Field(min_length=1,max_length=100)
        version: str = Field(min_length=1,max_length=100)
        parent_id: str | None = None
        reason: str = ''
        segments: list[Segment] = Field(min_length=1,max_length=1000)

    @app.post('/api/v1/records/{id}/status')
    def status(id: str, data: Status):
        r=store.get(id)
        if r['kind'] not in ('athlete','protocol','test'):
            raise ValueError('Ciclo di vita non disponibile per questo record.')
        return store.save(r['kind'],{**r,'status':data.status},id,data.base)

    @app.get('/api/v1/records/{id}/revisions')
    def revisions(id: str):
        store.get(id)
        return [{k:v for k,v in r.items() if k!='samples'} for r in store.history(id)]

    @app.put('/api/v1/tests/{id}')
    def revise(id: str, data: Revision):
        old=require(id,'test')
        if old.get('historical'):
            raise ValueError('Test storico senza campioni: correggere tramite il profilo storico.')
        if old['athlete_id']!=data.test.athlete_id or old['trace_hash']!=data.test.trace_hash:
            raise ValueError('La revisione non cambia atleta o file originale.')
        a=preview(data.test)
        return store.save('test',{**old,**data.test.model_dump(mode='json'),'analysis':a,'reason':data.reason},id,data.base)

    @app.get('/api/v1/athletes/{id}/defaults')
    def defaults(id: str, on: date):
        require(id,'athlete')
        values=sorted([m for m in store.list('measurement') if m['athlete_id']==id and m['date']<=on.isoformat()],key=lambda m:(m['date'],m['id']))
        return {'measurement':values[-1] if values else None}

    @app.get('/api/v1/zones/presets')
    def presets():
        from .zones import preset
        return [preset('hr'),preset('power')]

    @app.post('/api/v1/protocols/manual')
    def manual(data: Protocol):
        siblings=[p for p in store.list('protocol') if p['family']==data.family]
        if any(p['version']==data.version for p in siblings):
            raise ValueError('Versione già esistente.')
        if siblings and not data.parent_id:
            raise ValueError('Selezionare la versione precedente.')
        if data.parent_id:
            parent=require(data.parent_id,'protocol')
            if parent['family']!=data.family or not data.reason.strip():
                raise ValueError('Famiglia precedente incoerente o motivo mancante.')
        time=0;points=[];segments=[]
        for s in data.segments:
            points.extend([[time,s.start_w],[time+s.duration_s,s.end_w]])
            segments.append({'start_s':time,'end_s':time+s.duration_s,'start_w':s.start_w,'end_w':s.end_w,'phase':s.phase})
            time+=s.duration_s
        if not any(s.phase=='increment' for s in data.segments):
            raise ValueError('Il protocollo deve contenere una fase incrementale.')
        definition={'points':points,'segments':segments,'duration_s':time,'description':data.name}
        return store.save('protocol',{**data.model_dump(exclude={'segments'}),'definition':definition,'objects':[],'status':'active'})

    @app.get('/api/v1/protocols/{id}/erg')
    def erg(id: str):
        p=require(id,'protocol')
        if not p['definition']['points']:
            raise ValueError('Lo storico non contiene una definizione di carico esportabile.')
        text='[COURSE HEADER]\nVERSION = 2\nMINUTES WATTS\n[END COURSE HEADER]\n[COURSE DATA]\n'
        text+='\n'.join(f'{t/60:.12g} {w:.12g}' for t,w in p['definition']['points'])+'\n[END COURSE DATA]\n'
        return download(text.encode(),'text/plain',f'protocol-{id}.erg')

    @app.get('/api/v1/protocols/{id}/definition')
    def definition(id: str):
        p=require(id,'protocol')
        return download(encoded(p).encode(),'application/json',f'protocol-{id}.json')

    @app.post('/api/v1/import/preview')
    def import_preview(file: UploadFile, organization_id: str=Form(), profile: str=Form()):
        from .csv_import import plan_import
        require(organization_id,'organization')
        raw=file.file.read(30_000_001)
        if len(raw)>30_000_000: raise ValueError('CSV troppo grande.')
        result=plan_import(store,organization_id,profile,raw)
        digest=store.object(raw)
        return {k:v for k,v in result.items() if k!='entries'} | {'staged_hash':digest,'ready':len(result['entries']),
                'preview':[{'kind':k,**v} for k,v in result['entries'][:20]]}

    class Commit(Model):
        organization_id: str
        profile: str
        staged_hash: str

    @app.post('/api/v1/import/commit')
    def commit(data: Commit):
        from .csv_import import plan_import
        require(data.organization_id,'organization')
        result=plan_import(store,data.organization_id,data.profile,store.read_object(data.staged_hash))
        if result['errors']: raise ValueError('Correggere tutte le righe segnalate prima del commit.')
        batch={'organization_id':data.organization_id,'hash':result['hash'],'profile':data.profile,'objects':[data.staged_hash],
               'record_ids':[p['id'] for _,p in result['entries']]}
        records=store.save_batch(result['entries']+[('import_batch',batch)]) if result['entries'] else []
        return {'imported':len(result['entries']),'skipped':result['skipped'],'batch_id':records[-1]['id'] if records else None}

    @app.get('/api/v1/history/{org}')
    def history(org: str, group: str='', season: str='', athlete: str='', mode: str='athlete', dimension: str='season', protocol: str=''):
        from .history import summarize
        require(org,'organization')
        return summarize(store,org,group,season,athlete,mode,dimension,protocol)

    @app.get('/api/v1/history/{org}/report/{format}')
    def history_report(org: str, format: Literal['pdf','md'], group: str='', season: str='', athlete: str='', mode: str='athlete', dimension: str='season', protocol: str=''):
        from .history_report import render
        data=history(org,group,season,athlete,mode,dimension,protocol)
        body=render(data,format)
        if not hasattr(store,'identity') or store.identity['certificate']['role']=='admin':
            digest=store.object(body)
            store.save('report',{'organization_id':org,'query':data['query'],'source_revisions':[r['revision'] for r in data['rows']], 'format':format,'objects':[digest]})
        return download(body,'application/pdf' if format=='pdf' else 'application/zip','storico.'+('pdf' if format=='pdf' else 'zip'))
