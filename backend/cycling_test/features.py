"""Archive editing, protocols, CSV staging and common historical queries."""
import json
from datetime import date
from typing import Literal
from fastapi import UploadFile, Form
from .store import encoded


def install_features(app, store, require, download, preview):
    from .api import Model, TestInput, Settings
    from pydantic import Field

    class Status(Model):
        base: str
        status: Literal['active','archived','deleted']

    class Revision(Model):
        base: str
        reason: str = Field(min_length=1, max_length=1000)
        test: TestInput

    class HistoricalSettings(Settings):
        end_s: float = Field(default=0,ge=0)

    class HistoricalRevision(Model):
        base: str
        reason: str = Field(min_length=1,max_length=1000)
        date: date
        map_w: float | None = Field(default=None,ge=0,le=3000)
        map_alt_w: float | None = Field(default=None,ge=0,le=3000)
        settings: HistoricalSettings
        notes: str = Field(default='',max_length=10000)

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
        athlete=require(id,'athlete')
        values=sorted([m for m in store.list('measurement') if m['athlete_id']==id and m.get('status')!='deleted' and m['date']<=on.isoformat()],key=lambda m:(m['date'],m['id']))
        profiles=[p for p in store.list('default_profile') if p['organization_id']==athlete['organization_id']]
        return {'measurement':values[-1] if values else None,'suggestion':profiles[0] if profiles and not values else None}

    @app.put('/api/v1/tests/{id}/historical')
    def revise_historical(id: str,data: HistoricalRevision):
        from .observations import enrich
        old=require(id,'test')
        if not old.get('historical'):raise ValueError('Usare la revisione del test con tracciato.')
        settings=data.settings.model_dump()
        analysis={**old['analysis'],'map_w':data.map_w,'map_alt_w':data.map_alt_w,'duration_s':settings['end_s'] or None}
        analysis['map_wkg']=round(data.map_w/settings['weight_kg'],3) if data.map_w is not None and settings.get('weight_kg') else None
        analysis=enrich(analysis,[],settings)
        historic={**old.get('historical_fields',{}),'data':data.date.isoformat(),'map_w':data.map_w,'map_alt_w':data.map_alt_w,'peso_kg':settings.get('weight_kg'),
                  'soglia_w':analysis.get('threshold_w'),'soglia_origine':analysis.get('threshold_source'),'fthr_bpm':settings.get('fthr_bpm'),'note':data.notes}
        return store.save('test',{**old,'settings':settings,'analysis':analysis,'historical_fields':historic,'date':data.date.isoformat(),'notes':data.notes,'reason':data.reason},id,data.base)

    class DefaultProfile(Model):
        organization_id: str
        source: str = Field(min_length=1,max_length=1000)
        population: str = Field(min_length=1,max_length=1000)
        weight_kg: float | None = Field(default=None,gt=0,le=400)
        height_cm: float | None = Field(default=None,gt=0,le=260)

    @app.post('/api/v1/default-profiles')
    def default_profile(data: DefaultProfile):
        require(data.organization_id,'organization')
        if data.weight_kg is None and data.height_cm is None:raise ValueError('Inserire almeno un valore suggerito.')
        return store.save('default_profile',data.model_dump())

    class UndoImport(Model):
        reason: str = Field(min_length=1,max_length=1000)

    @app.post('/api/v1/import/{id}/undo')
    def undo_import(id: str,data: UndoImport):
        batch=require(id,'import_batch')
        records=[store.get(record_id) for record_id in batch['record_ids']]
        if any(len(store.history(r['id']))!=1 for r in records):raise ValueError('Il lotto contiene record modificati successivamente: riconciliare manualmente prima dell’annullamento.')
        removed_ids={r['id'] for r in records}
        if any(t['athlete_id'] in removed_ids and t['id'] not in removed_ids for t in store.list('test')):
            raise ValueError('Atleti del lotto hanno test successivi: annullare prima i lotti dipendenti.')
        store.revise_batch(records,data.reason)
        return {'undone':len(records)}

    @app.get('/api/v1/import/batches')
    def import_batches():
        return store.list('import_batch')

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
    def history_report(org: str, format: Literal['pdf','md'], group: str='', season: str='', athlete: str='', mode: str='athlete', dimension: str='season', protocol: str='', language: Literal['it','en']='it'):
        from .history_report import render
        data=history(org,group,season,athlete,mode,dimension,protocol)
        body=render(data,format,language)
        if not hasattr(store,'identity') or store.identity['certificate']['role']=='admin':
            digest=store.object(body)
            store.save('report',{'organization_id':org,'query':data['query'],'source_revisions':[r['revision'] for r in data['rows']], 'format':format,'language':language,'objects':[digest]})
        return download(body,'application/pdf' if format=='pdf' else 'application/zip','storico.'+('pdf' if format=='pdf' else 'zip'))

    @app.get('/api/v1/history/{org}/growth')
    def growth(org: str, athlete: str=''):
        from .history import growth
        require(org,'organization')
        return growth(store,org,athlete)

    @app.get('/api/v1/history/{org}/compare')
    def compare(org: str,first: str,second: str,group: str=''):
        from .history import paired_comparison
        require(org,'organization')
        return paired_comparison(store,org,first,second,group)
