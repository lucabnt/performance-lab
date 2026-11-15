"""Archive editing, protocols, CSV staging and common historical queries."""
import json
from datetime import date
from typing import Literal
from fastapi import UploadFile, Form
from .store import encoded
from .custom_fields import FieldDefinition,protocol_metadata,attach


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
        fc_max_test_bpm: float | None = Field(default=None,gt=0,le=250)
        settings: HistoricalSettings
        notes: str = Field(default='',max_length=10000)

    class ManualTest(Model):
        athlete_id: str
        protocol_id: str
        date: date
        map_w: float | None = Field(default=None,ge=0,le=3000)
        map_alt_w: float | None = Field(default=None,ge=0,le=3000)
        fc_max_test_bpm: float | None = Field(default=None,gt=0,le=250)
        settings: HistoricalSettings
        notes: str = Field(default='',max_length=10000)

    @app.post('/api/v1/manual-tests')
    def manual_test(data: ManualTest):
        from .observations import enrich
        athlete=require(data.athlete_id,'athlete'); protocol=require(data.protocol_id,'protocol')
        if protocol.get('organization_id') and protocol['organization_id']!=athlete['organization_id']:raise ValueError('Protocollo esterno alla società.')
        from .anaerobic import is_anaerobic
        if is_anaerobic(protocol) or protocol.get('test_type')=='custom':raise ValueError('Usare la registrazione test anaerobici.')
        if any(r.get('status','active')!='active' for r in (athlete,protocol)):
            raise ValueError('Ripristinare atleta e protocollo prima di creare nuovi test.')
        settings=data.settings.model_dump()
        analysis={'map_w':data.map_w,'map_alt_w':data.map_alt_w,
                  'map_wkg':round(data.map_w/settings['weight_kg'],3) if data.map_w is not None and settings.get('weight_kg') else None,
                  'fc_max_test_bpm':data.fc_max_test_bpm,'duration_s':settings['end_s'] or None,
                  'steps':[],'recovery':[],'power_coverage':None,'engine':'manual-1',
                  'method':'Risultati dichiarati manualmente, senza verifica del tracciato.',
                  'warnings':['Campioni assenti: MAP, FC e durata sono dichiarati; nessuna verifica automatica degli step.']}
        analysis=attach(enrich(analysis,[],settings),protocol,settings)
        memberships=[m['group_id'] for m in store.list('membership') if m['athlete_id']==athlete['id'] and m['start']<=data.date.isoformat() and (not m.get('end') or m['end']>=data.date.isoformat())]
        return store.save('test',{**data.model_dump(mode='json'),'organization_id':athlete['organization_id'],
            'athlete_snapshot':athlete,'historical':True,'entry_source':'manuale','trace_hash':None,'samples':[],
            'objects':[],'group_ids':memberships,'analysis':analysis})

    class Segment(Model):
        duration_s: float = Field(gt=0, le=86400)
        start_w: float = Field(ge=0, le=3000)
        end_w: float = Field(ge=0, le=3000)
        phase: Literal['warmup','increment','recovery','cooldown'] = 'increment'

    class Protocol(Model):
        organization_id: str | None = None
        custom_fields: list[FieldDefinition] = Field(default_factory=list,max_length=50)
        custom_values: dict = Field(default_factory=dict,max_length=50)
        name: str = Field(min_length=1,max_length=300)
        family: str = Field(min_length=1,max_length=100)
        version: str = Field(min_length=1,max_length=100)
        parent_id: str | None = None
        reason: str = ''
        segments: list[Segment] = Field(default_factory=list,max_length=1000)

    @app.post('/api/v1/records/{id}/status')
    def status(id: str, data: Status):
        r=store.get(id)
        if r['kind'] not in ('athlete','protocol','test','measurement'):
            raise ValueError('Ciclo di vita non disponibile per questo record.')
        if r['kind']=='measurement' and data.status=='archived':
            raise ValueError('Una rilevazione può essere attiva o eliminata, non archiviata.')
        return store.save(r['kind'],{**r,'status':data.status},id,data.base)

    @app.get('/api/v1/records/{id}/revisions')
    def revisions(id: str):
        store.get(id)
        return [{k:v for k,v in r.items() if k!='samples'} for r in store.history(id)]

    @app.put('/api/v1/tests/{id}')
    def revise(id: str, data: Revision):
        old=require(id,'test')
        from .anaerobic import is_anaerobic
        if is_anaerobic(old) or old.get('test_type')=='custom':raise ValueError('Usare la revisione specifica per test anaerobici.')
        if old.get('historical'):
            raise ValueError('Test storico senza campioni: correggere tramite il profilo storico.')
        if old['athlete_id']!=data.test.athlete_id or old['trace_hash']!=data.test.trace_hash:
            raise ValueError('La revisione non cambia atleta o file originale.')
        a=preview(data.test)
        objects=[data.test.trace_hash]
        trace=json.loads(store.read_object(data.test.trace_hash));objects.append(trace['original_hash'])
        if data.test.settings.gas_hash:
            gas=json.loads(store.read_object(data.test.settings.gas_hash));objects += [data.test.settings.gas_hash,gas['original_hash']]
        return store.save('test',{**old,**data.test.model_dump(mode='json'),'analysis':a,'objects':objects,'reason':data.reason},id,data.base)

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
        from .anaerobic import is_anaerobic
        if is_anaerobic(old) or old.get('test_type')=='custom':raise ValueError('Usare la revisione specifica per test anaerobici.')
        if not old.get('historical'):raise ValueError('Usare la revisione del test con tracciato.')
        settings=data.settings.model_dump()
        analysis={**old['analysis'],'map_w':data.map_w,'map_alt_w':data.map_alt_w,'duration_s':settings['end_s'] or None}
        if 'fc_max_test_bpm' in data.model_fields_set:analysis['fc_max_test_bpm']=data.fc_max_test_bpm
        analysis['map_wkg']=round(data.map_w/settings['weight_kg'],3) if data.map_w is not None and settings.get('weight_kg') else None
        analysis=attach(enrich(analysis,[],settings),store.get(old['protocol_id']),settings)
        historic={**old.get('historical_fields',{}),'data':data.date.isoformat(),'map_w':data.map_w,'map_alt_w':data.map_alt_w,'peso_kg':settings.get('weight_kg'),
                  'soglia_w':analysis.get('threshold_w'),'soglia_origine':analysis.get('threshold_source'),'fthr_bpm':settings.get('fthr_bpm'),
                  'fc_max_test_bpm':analysis.get('fc_max_test_bpm'),'durata_s':analysis.get('duration_s'),'note':data.notes}
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
        if any(m['id'] not in removed_ids and m.get('status')!='deleted' and (m['group_id'] in removed_ids or m['athlete_id'] in removed_ids) for m in store.list('membership')) or any(g['id'] not in removed_ids and g.get('status')!='deleted' and g.get('parent_id') in removed_ids for g in store.list('group')):
            raise ValueError('Gruppi o atleti del lotto hanno appartenenze o stagioni successive: riconciliare prima le dipendenze.')
        store.revise_batch(records,data.reason)
        return {'undone':len(records)}

    @app.get('/api/v1/import/batches')
    def import_batches():
        return store.list('import_batch')

    @app.get('/api/v1/import/schemas')
    def import_schemas():
        from .csv_import import SCHEMAS,import_columns
        return {k:{**v,'optional':[h for h in import_columns(k) if h not in v['required']]} for k,v in SCHEMAS.items()}

    @app.get('/api/v1/import/template/{profile}')
    def import_template(profile:str):
        from .csv_import import template_csv
        return download(template_csv(profile),'text/csv; charset=utf-8',profile+'-modello.csv')

    @app.get('/api/v1/import/example/appartenenze')
    def membership_example():
        from .membership_import import sample_csv
        return download(sample_csv(),'text/csv; charset=utf-8','appartenenze-esempio.csv')

    @app.get('/api/v1/zones/presets')
    def presets():
        from .zones import preset
        return [preset('hr'),preset('power')]

    @app.post('/api/v1/protocols/manual')
    def manual(data: Protocol):
        if data.organization_id:require(data.organization_id,'organization')
        metadata=protocol_metadata(data.model_dump())
        siblings=[p for p in store.list('protocol') if p['family']==data.family and p.get('organization_id')==data.organization_id]
        if any(p['version']==data.version for p in siblings):
            raise ValueError('Versione già esistente.')
        if siblings and not data.parent_id:
            raise ValueError('Selezionare la versione precedente.')
        if data.parent_id:
            parent=require(data.parent_id,'protocol')
            if parent['family']!=data.family or parent.get('organization_id')!=data.organization_id or parent.get('test_type') not in (None,'incremental') or not data.reason.strip():
                raise ValueError('Famiglia precedente incoerente o motivo mancante.')
        time=0;points=[];segments=[]
        for s in data.segments:
            points.extend([[time,s.start_w],[time+s.duration_s,s.end_w]])
            segments.append({'start_s':time,'end_s':time+s.duration_s,'start_w':s.start_w,'end_w':s.end_w,'phase':s.phase})
            time+=s.duration_s
        if data.segments and not any(s.phase=='increment' for s in data.segments):
            raise ValueError('Il protocollo deve contenere una fase incrementale.')
        definition={'points':points,'segments':segments,'duration_s':time,'description':data.name}
        return store.save('protocol',{**data.model_dump(exclude={'segments'}),**metadata,'definition':definition,'objects':[],'status':'active'})

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
        from .csv_import import plan_import, plan_digest
        require(organization_id,'organization')
        raw=file.file.read(30_000_001)
        if len(raw)>30_000_000: raise ValueError('CSV troppo grande.')
        result=plan_import(store,organization_id,profile,raw)
        digest=store.object(raw)
        athletes={a['id']:a for a in store.list('athlete') if a['organization_id']==organization_id}
        protocols={p['id']:p for p in store.list('protocol')}
        protocols.update({p['id']:p for kind,p in result['entries'] if kind=='protocol'})
        groups={g['id']:g for g in store.list('group')}
        groups.update({p['id']:p for kind,p in result['entries'] if kind=='group'})
        records=[(kind,p) for kind,p in result['entries'] if kind not in ('protocol','group')]
        created=[p for kind,p in result['entries'] if kind=='protocol']
        preview=[]
        for kind,payload in records[:20]:
            athlete=athletes.get(payload.get('athlete_id'),{})
            protocol=protocols.get(payload.get('protocol_id'),{})
            preview.append({'kind':kind,**payload,**({'athlete_name':(athlete.get('surname','')+' '+athlete.get('name','')).strip(),
                'athlete_external_id':athlete.get('external_id',athlete.get('id',''))} if athlete else {}),
                **({'protocol_code':protocol['family'],'protocol_name':protocol['name']} if protocol else {})})
            if kind=='membership':
                g=groups[payload['group_id']]
                preview[-1].update(group_name=groups.get(g.get('parent_id'),g)['name'],subgroup=g.get('season',''))
            if kind=='measurement':
                preview[-1].update(import_action='integrate' if payload['id'] in result.get('bases',{}) else 'create',
                                   added_fields=result.get('integrated_fields',{}).get(payload['id'],[]))
        return {k:v for k,v in result.items() if k not in ('entries','bases','integrated_fields')} | {'staged_hash':digest,'plan_hash':plan_digest(result),'ready':len(result['entries']),
                'ready_rows':len(records),'new_protocols':[{'code':p['family'],'name':p['name']} for p in created],
                'new_groups':[{'name':p['name'],'season':p.get('season','')} for kind,p in result['entries'] if kind=='group'],'preview':preview}

    class Commit(Model):
        organization_id: str
        profile: str
        staged_hash: str
        plan_hash: str | None = None

    @app.post('/api/v1/import/commit')
    def commit(data: Commit):
        from .csv_import import plan_import, plan_digest
        from .store import ConflictError
        require(data.organization_id,'organization')
        result=plan_import(store,data.organization_id,data.profile,store.read_object(data.staged_hash))
        if result['errors']: raise ValueError('Correggere tutte le righe segnalate prima del commit.')
        if (data.plan_hash is not None and data.plan_hash!=plan_digest(result)) or (result.get('bases') and data.plan_hash is None):
            raise ConflictError('I dati o le integrazioni sono cambiati: ripetere anteprima prima di confermare.')
        batch={'organization_id':data.organization_id,'hash':result['hash'],'profile':data.profile,'objects':[data.staged_hash],
               'record_ids':[p['id'] for _,p in result['entries']]}
        records=store.save_batch(result['entries']+[('import_batch',batch)],bases=result.get('bases')) if result['entries'] else []
        return {'imported':len(result['entries']),'integrated':len(result.get('bases',{})),'skipped':result['skipped'],'batch_id':records[-1]['id'] if records else None}

    @app.get('/api/v1/history/{org}')
    def history(org: str, group: str='', season: str='', athlete: str='', mode: str='athlete', dimension: str='season', protocol: str=''):
        from .history import summarize
        require(org,'organization')
        return summarize(store,org,group,season,athlete,mode,dimension,protocol)

    @app.get('/api/v1/history/{org}/report/{format}')
    def history_report(org: str, format: Literal['pdf','md'], group: str='', season: str='', athlete: str='', mode: str='athlete', dimension: str='season', protocol: str='', language: Literal['it','en']='it', metric: str='map_w', statistic: Literal['mean','median']='median'):
        from .history_report import render
        data=history(org,group,season,athlete,mode,dimension,protocol)
        from .history import metrics_for
        if metric not in metrics_for(store): raise ValueError('Metrica non supportata.')
        data['query'].update(metric=metric,statistic=statistic)
        labels={p['id']:p['name']+' · '+p['version'] for p in store.list('protocol')}
        for g in data['groups']: g['protocol_label']=labels.get(g['protocol_id'],g['protocol_id'][:8])
        body=render(data,format,language,metric,statistic)
        from .store import save_report
        save_report(store,{'organization_id':org,'query':data['query'],'source_revisions':[r['revision'] for r in data['rows']],'format':format,'language':language},body)
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
