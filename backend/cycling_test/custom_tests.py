"""Custom protocols record observations without borrowing physiological methods."""
import json
from datetime import date
from pydantic import BaseModel,ConfigDict,Field
from .custom_fields import FieldDefinition,protocol_metadata,attach

class Model(BaseModel):model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
class Protocol(Model):
    organization_id: str
    name: str=Field(min_length=1,max_length=300)
    family: str=Field(min_length=1,max_length=100)
    version: str=Field(min_length=1,max_length=100)
    parent_id: str|None=None
    reason: str=Field(default='',max_length=3000)
    description: str=Field(default='',max_length=10000)
    custom_fields: list[FieldDefinition]=Field(default_factory=list,max_length=50)
    custom_values: dict=Field(default_factory=dict,max_length=50)
class Settings(Model):
    offset_s: float=Field(default=0,ge=0)
    end_s: float|None=Field(default=None,gt=0)
    weight_kg: float|None=Field(default=None,gt=0,le=400)
    weight_source: str='dichiarato'
    conditions: dict[str,str]=Field(default_factory=dict,max_length=30)
    custom_values: dict=Field(default_factory=dict,max_length=50)
    extra_fields: list[FieldDefinition]=Field(default_factory=list,max_length=50)
class Test(Model):
    athlete_id: str
    protocol_id: str
    date: date
    trace_hash: str|None=None
    settings: Settings=Field(default_factory=Settings)
    notes: str=Field(default='',max_length=10000)
    revision: str|None=None
    reason: str=Field(default='',max_length=3000)

def install_api(app,store):
    def require(id,kind):
        r=store.get(id)
        if r['kind']!=kind or r.get('status')=='deleted':raise ValueError('Riferimento non disponibile.')
        return r
    @app.post('/api/v1/custom/protocols')
    def protocol(data:Protocol):
        require(data.organization_id,'organization');d=data.model_dump()
        siblings=[p for p in store.list('protocol') if p.get('organization_id')==data.organization_id and p['family']==data.family]
        if any(p['version']==data.version for p in siblings):raise ValueError('Versione già presente.')
        if siblings and not data.parent_id:raise ValueError('Selezionare la versione precedente.')
        if data.parent_id:
            p=require(data.parent_id,'protocol')
            if p.get('organization_id')!=data.organization_id or p['family']!=data.family or p.get('test_type')!='custom' or not data.reason.strip():raise ValueError('Versione precedente incoerente o motivo mancante.')
        return store.save('protocol',{**d,**protocol_metadata(d),'test_type':'custom','status':'active','definition':{'points':[],'segments':[],'duration_s':0},'objects':[]})
    def prepare(data,editing=False):
        p=require(data.protocol_id,'protocol');a=require(data.athlete_id,'athlete')
        if p.get('test_type')!='custom' or p.get('organization_id')!=a['organization_id']:raise ValueError('Protocollo custom e atleta devono appartenere alla stessa società.')
        if not editing and (p.get('status','active')!='active' or a.get('status','active')!='active'):raise ValueError('Ripristinare atleta e protocollo.')
        s=data.settings.model_dump();trace={'samples':[]};objects=[]
        if data.trace_hash:
            trace=json.loads(store.read_object(data.trace_hash));objects=[data.trace_hash]+([trace['original_hash']] if trace.get('original_hash') else [])
            if s['end_s'] is None:s['end_s']=trace['duration_s']
            if not s['offset_s']<s['end_s']<=trace['duration_s']:raise ValueError('Intervallo fuori dal tracciato.')
        elif s['end_s'] is not None and s['end_s']<=s['offset_s']:raise ValueError('Fine precedente all’inizio.')
        analysis=attach({'engine':'custom-1','source':'trace-observations' if data.trace_hash else 'manual','method':'Protocollo custom: risultati dichiarati, nessuna formula fisiologica automatica. Il tracciato è conservato come osservazione.','steps':[],'recovery':[],'zones':[],'duration_s':s['end_s']-s['offset_s'] if s['end_s'] is not None else None,'warnings':['Protocollo custom: la validità e l’interpretazione dei campi sono responsabilità del metodo dichiarato.'],'protocol_snapshot':p},p,s)
        if not data.trace_hash and not analysis['custom_values'] and not data.notes.strip():raise ValueError('Inserire almeno un risultato, un’osservazione o un tracciato.')
        return {'organization_id':a['organization_id'],'athlete_id':a['id'],'athlete_snapshot':a,'protocol_id':p['id'],'test_type':'custom','date':data.date.isoformat(),'settings':s,'analysis':analysis,'historical':not bool(data.trace_hash),'trace_hash':data.trace_hash,'samples':trace['samples'],'objects':objects,'notes':data.notes,'group_ids':[]}
    @app.post('/api/v1/custom/preview')
    def preview(data:Test):return prepare(data,editing=bool(data.revision))['analysis']
    @app.post('/api/v1/custom/tests')
    def save(data:Test):return store.save('test',prepare(data))
    @app.put('/api/v1/custom/tests/{id}')
    def revise(id:str,data:Test):
        old=require(id,'test')
        if old.get('test_type')!='custom' or data.athlete_id!=old['athlete_id'] or data.protocol_id!=old['protocol_id'] or not data.reason.strip():raise ValueError('Revisione custom non valida: stesso atleta e motivo obbligatorio.')
        return store.save('test',{**prepare(data,True),'reason':data.reason},id=id,base=data.revision)
