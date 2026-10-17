import io
import json
import os
import secrets
import sqlite3
import zipfile
from datetime import date
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Request
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, model_validator

from .analysis import analyze
from .erg import parse_erg
from .fit import decode_fit
from .store import Store, ConflictError

Text = Annotated[str, Field(min_length=1, max_length=300)]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Organization(Model):
    name: Text


class Group(Model):
    organization_id: str
    name: str = Field(default='', max_length=300)
    season: str = ""
    parent_id: str | None = None


class Athlete(Model):
    organization_id: str
    name: Text
    surname: Text
    birth_year: int | None = Field(default=None, ge=1900, le=2100)
    birth_date: date | None = None
    status: Literal['active', 'archived', 'deleted'] = 'active'
    birth_confirmed: bool = False
    birth_source: str = ""
    sex: Literal["M", "F", ""] = ""
    notes: str = Field(default="", max_length=10000)

    @model_validator(mode='after')
    def birthday(self):
        if self.birth_date:
            if self.birth_date > date.today():
                raise ValueError('Data di nascita futura.')
            if self.birth_year and self.birth_year != self.birth_date.year:
                raise ValueError('Data e anno di nascita incoerenti.')
            self.birth_year = self.birth_date.year
        return self


class Membership(Model):
    athlete_id: str
    group_id: str
    start: date
    end: date | None = None
    category_year: int | None = Field(default=None, ge=1, le=20)

    @model_validator(mode="after")
    def dates(self):
        if self.end and self.end < self.start:
            raise ValueError("Fine appartenenza precedente all'inizio.")
        return self


class Measurement(Model):
    athlete_id: str
    date: date
    weight_kg: float | None = Field(default=None, gt=0, le=400)
    height_cm: float | None = Field(default=None, gt=0, le=260)
    source: Literal["misurato", "arrotondato", "dichiarato"] = "misurato"


class RecoveryObservation(Model):
    after_s: float = Field(ge=0, le=86400)
    hr_bpm: float = Field(gt=0, le=250)


class LactateObservation(Model):
    at_s: float = Field(ge=0)
    mmol_l: float = Field(gt=0, le=40)
    note: str = ''
    step_number: int | None = Field(default=None, ge=1, le=1000)
    power_w: float | None = Field(default=None, ge=0, le=3000)
    delay_s: float = Field(default=0,ge=0,le=600)


class Exclusion(Model):
    start_s: float = Field(ge=0)
    end_s: float = Field(gt=0)
    reason: str = Field(min_length=1,max_length=1000)


class Alignment(Model):
    number: int = Field(ge=1,le=1000)
    at_s: float = Field(ge=0)


class VentilatoryMarker(Model):
    at_s: float = Field(ge=0)
    evidence: str = Field(min_length=1,max_length=3000)


class MaximumVerification(Model):
    confirmed: bool = False
    evidence: str = Field(default='',max_length=3000)


class Settings(Model):
    offset_s: float = Field(default=0, ge=0)
    end_s: float = Field(gt=0)
    weight_kg: float | None = Field(default=None, gt=0, le=400)
    height_cm: float | None = Field(default=None, gt=0, le=260)
    rest_hr: int | None = Field(default=None, gt=0, le=250)
    rest_after_s: int | None = Field(default=None, ge=0, le=86400)
    rpe: float | None = Field(default=None, ge=0, le=20)
    rpe_scale: str = 'CR10 dichiarata'
    weight_source: Literal['misurato', 'arrotondato', 'dichiarato', 'stimato'] = 'dichiarato'
    measurement_id: str | None = None
    threshold_w: float | None = Field(default=None, gt=0, le=2500)
    threshold_coefficient: float | None = Field(default=None, gt=0, le=2)
    threshold_source: str = ''
    ftp_w: float | None = Field(default=None, gt=0, le=2500)
    fthr_bpm: float | None = Field(default=None, gt=0, le=250)
    fc_max_reference_bpm: float | None = Field(default=None, gt=0, le=250)
    recovery_manual: list[RecoveryObservation] = Field(default_factory=list, max_length=100)
    lactate: list[LactateObservation] = Field(default_factory=list, max_length=100)
    zone_schemes: list[dict] | None = None
    preset_id: str | None = None
    excluded_intervals: list[Exclusion] = Field(default_factory=list,max_length=100)
    alignment_markers: list[Alignment] = Field(default_factory=list,max_length=1000)
    conditions: dict[str,str] = Field(default_factory=dict,max_length=30)
    gas_hash: str | None = None
    gas_offset_s: float = Field(default=0,ge=-86400,le=86400)
    ventilatory_markers: dict[Literal['vt1','vt2'],VentilatoryMarker] = Field(default_factory=dict)
    vo2max_verification: MaximumVerification = Field(default_factory=MaximumVerification)
    threshold_calibration: dict[str,str] = Field(default_factory=dict,max_length=20)

    @model_validator(mode='after')
    def validate_observations(self):
        from .zones import validate
        if self.zone_schemes is not None:
            if len(self.zone_schemes) > 2:
                raise ValueError('Un solo schema per ciascun canale.')
            channels = []
            for scheme in self.zone_schemes:
                validate(scheme)
                channels.append(scheme['channel'])
            if len(set(channels)) != len(channels):
                raise ValueError('Canale duplicato negli schemi zone.')
        times = [r.after_s for r in self.recovery_manual]
        if len(times) != len(set(times)):
            raise ValueError('Tempi di recupero duplicati.')
        if self.rpe is not None:
            if self.rpe_scale=='CR10 dichiarata' and self.rpe>10 or self.rpe_scale=='Borg 6-20' and not 6<=self.rpe<=20:
                raise ValueError('RPE incompatibile con la scala selezionata.')
        if any(len(v)>3000 for v in self.conditions.values()):raise ValueError('Condizioni: testo troppo lungo.')
        return self


class TestInput(Model):
    athlete_id: str
    protocol_id: str
    trace_hash: str
    date: date
    settings: Settings
    notes: str = Field(default="", max_length=10000)


class SyncInput(Model):
    folder: str
    key: str


def create_app(root=None, token=None, frontend=None):
    legacy = Store(root or os.environ.get("FUORIGIRI_DATA", ".local"))
    from .workspaces import Workspaces
    workspaces=Workspaces(legacy.root,legacy)
    store=workspaces.proxy
    token = token or os.environ.get("FUORIGIRI_TOKEN") or secrets.token_urlsafe(32)
    app = FastAPI(title="Fuorigiri Performance Lab", version="0.6.0", docs_url=None, redoc_url=None)
    app.state.store = store
    app.state.token = token

    @app.middleware("http")
    async def local_only(request: Request, call_next):
        if request.url.hostname not in ("127.0.0.1", "localhost", "testserver"):
            return JSONResponse({"detail":"Host non consentito"},status_code=403)
        if request.url.path.startswith("/api/"):
            if not secrets.compare_digest(request.headers.get("X-Fuorigiri-Token", ""), token):
                return JSONResponse({"detail":"Sessione non autorizzata. Riaprire l'app."},status_code=401)
        try:
            selected=workspaces.get(request.headers.get('X-Fuorigiri-Workspace',''))
        except ValueError as exc:
            return JSONResponse({'detail':str(exc)},status_code=422)
        marker=store.selected.set(selected)
        if hasattr(selected,'identity'):
            identity=selected.identity
            read_only=identity['certificate']['role']=='viewer' or identity['certificate']['id'] in selected.revocations()
            allowed=request.method in ('GET','HEAD') or request.url.path in ('/api/v1/tests/preview','/api/v1/sync',
                '/api/v1/workspaces','/api/v1/workspaces/join','/api/v1/workspaces/access','/api/v1/workspaces/restore/preview','/api/v1/workspaces/restore',
                '/api/v1/sync/connection','/api/v1/sync/run')
            allowed=allowed or request.url.path=='/api/v1/repeatability' or request.url.path.startswith('/api/v1/repeatability/report/')
            if read_only and not allowed:
                store.selected.reset(marker)
                return JSONResponse({'detail':'Visualizzatore: operazione di modifica non consentita.'},status_code=403)
        origin = request.headers.get("origin")
        if origin and origin not in {str(request.base_url).rstrip("/"), "http://localhost:5173", "http://127.0.0.1:5173"}:
            store.selected.reset(marker)
            return JSONResponse({"detail":"Origine non consentita"},status_code=403)
        try:
            response = await call_next(request)
        finally:
            store.selected.reset(marker)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(ValueError)
    async def value_error(request, exc):
        return JSONResponse({"detail":str(exc)},status_code=409 if isinstance(exc, ConflictError) else 422)

    @app.exception_handler(KeyError)
    async def missing(request, exc):
        return JSONResponse({"detail":"Record non trovato."},status_code=404)

    def require(id, kind):
        record = store.get(id)
        if record["kind"] != kind:
            raise ValueError("Riferimento di tipo errato.")
        return record

    def download(content, media, name):
        return Response(content,media_type=media,headers={"Content-Disposition":f'attachment; filename="{name}"'})

    @app.get("/health")
    def health():
        return {"status":"ok"}

    @app.get("/api/v1/state")
    def state():
        result = {kind:store.list(kind) for kind in ("organization","group","athlete","membership","measurement","protocol")}
        for kind in ('membership','measurement'):
            result[kind]=[r for r in result[kind] if r.get('status')!='deleted']
        result["test"] = [{k:v for k,v in t.items() if k != "samples"} for t in store.list("test")]
        result['operator']={k:store.identity['certificate'][k] for k in ('name','role','id')} if hasattr(store,'identity') else {'name':'Locale','role':'admin'}
        if hasattr(store,'identity'):
            result['operator'].update(owner=bool(store.identity.get('authority_private')),snapshot=bool(store.identity.get('snapshot')),
                revoked=store.identity['certificate']['id'] in store.revocations())
        return result

    @app.post("/api/v1/organizations")
    def organization(data: Organization):
        if hasattr(store,'identity'):
            raise ValueError('Un workspace contiene una sola società. Creare un nuovo workspace.')
        return store.save("organization",data.model_dump())

    @app.post("/api/v1/groups")
    def group(data: Group):
        require(data.organization_id,"organization")
        if data.parent_id:
            parent = require(data.parent_id, 'group')
            if parent['organization_id'] != data.organization_id or parent.get('parent_id'):
                raise ValueError('Categoria padre non valida.')
            if not data.season.strip():
                raise ValueError('Indicare la stagione del gruppo figlio.')
            data.name = data.name.strip() or parent['name']
        elif not data.name.strip():
            raise ValueError('Indicare il nome della categoria principale.')
        return store.save("group",data.model_dump())

    @app.post("/api/v1/athletes")
    def athlete(data: Athlete):
        require(data.organization_id,"organization")
        return store.save("athlete",data.model_dump(mode='json'))

    @app.put("/api/v1/athletes/{id}")
    def edit_athlete(id: str, base: str, data: Athlete):
        original = require(id,"athlete")
        if original["organization_id"] != data.organization_id:
            raise ValueError("Trasferimento fra società non supportato da questa modifica.")
        return store.save("athlete",data.model_dump(mode='json'),id,base)

    @app.post("/api/v1/memberships")
    def membership(data: Membership):
        a,g = require(data.athlete_id,"athlete"),require(data.group_id,"group")
        if a["organization_id"] != g["organization_id"]:
            raise ValueError("Atleta e gruppo devono appartenere alla stessa società.")
        return store.save("membership",data.model_dump(mode="json"))

    @app.post("/api/v1/measurements")
    def measurement(data: Measurement):
        require(data.athlete_id,"athlete")
        if data.weight_kg is None and data.height_cm is None:
            raise ValueError("Inserire almeno una misura.")
        return store.save("measurement",data.model_dump(mode="json"))

    @app.post("/api/v1/protocols")
    def protocol(file: UploadFile, name: Annotated[str,Form()], family: Annotated[str,Form()], version: Annotated[str,Form()], warmup_s: Annotated[float,Form()] = 600, parent_id: Annotated[str,Form()] = "", reason: Annotated[str,Form()] = ""):
        raw = file.file.read(2_000_001)
        if len(raw)>2_000_000:
            raise ValueError("ERG troppo grande.")
        if not name.strip() or not family.strip() or not version.strip():
            raise ValueError("Nome, codice e versione sono obbligatori.")
        definition = parse_erg(raw.decode("utf-8-sig"))
        boundaries = {s["start_s"] for s in definition["segments"]} | {definition["duration_s"]}
        if warmup_s not in boundaries or warmup_s == definition["duration_s"]:
            raise ValueError("Il termine del riscaldamento deve coincidere con un confine degli step e lasciare almeno uno step incrementale.")
        for s in definition["segments"]:
            s["phase"] = "warmup" if s["end_s"] <= warmup_s else "increment"
        siblings = [p for p in store.list("protocol") if p["family"] == family.strip()]
        if any(p["version"] == version.strip() for p in siblings):
            raise ValueError("Questa versione esiste già. Scegliere un nuovo identificatore.")
        if siblings and not parent_id:
            raise ValueError("Selezionare la versione precedente per documentare l'evoluzione.")
        if parent_id and require(parent_id,"protocol")["family"] != family:
            raise ValueError("La versione precedente appartiene a un'altra famiglia.")
        digest = store.object(raw)
        return store.save("protocol",{"name":name.strip(),"family":family.strip(),"version":version.strip(),"parent_id":parent_id or None,"reason":reason,"definition":definition,"objects":[digest]})

    @app.post("/api/v1/traces")
    def trace(file: UploadFile, session_index: Annotated[int | None,Form()]=None, duplicate_policy: Annotated[str,Form()]='reject', correction_reason: Annotated[str,Form()]=''):
        raw = file.file.read(30_000_001)
        if len(raw)>30_000_000:
            raise ValueError("FIT oltre il limite di 30 MB.")
        if (file.filename or '').lower().endswith('.csv'):
            from .csv_import import decode_trace_csv
            decoded = decode_trace_csv(raw)
        else:
            decoded = decode_fit(raw,session_index=session_index,duplicate_policy=duplicate_policy,correction_reason=correction_reason)
        original = store.object(raw)
        normalized = store.object(json.dumps({**decoded,"original_hash":original},allow_nan=False).encode())
        return {**decoded,"hash":normalized}

    @app.post('/api/v1/traces/inspect')
    def inspect_trace(file: UploadFile):
        raw=file.file.read(30_000_001)
        if len(raw)>30_000_000:raise ValueError('FIT oltre 30 MB.')
        return decode_fit(raw,overview=True)

    @app.post("/api/v1/tests/preview")
    def preview(data: TestInput):
        require(data.athlete_id,"athlete")
        protocol = require(data.protocol_id,"protocol")
        if not protocol['definition']['segments']:
            raise ValueError('Protocollo senza step: usare l’inserimento manuale oppure creare una versione con carichi.')
        trace = json.loads(store.read_object(data.trace_hash))
        from .observations import enrich
        settings = data.settings.model_dump()
        from .methods import resolve
        from .store import encoded
        import hashlib
        analysis=analyze(trace['samples'],protocol['definition'],settings,resolve(store,settings.get('preset_id')))
        analysis['protocol_snapshot']={'id':protocol['id'],'version':protocol['version'],'hash':hashlib.sha256(encoded(protocol['definition']).encode()).hexdigest()}
        analysis['input_provenance']={'trace_hash':data.trace_hash,'original_hash':trace.get('original_hash'),'decoder':trace.get('decoder','legacy_unknown'),
                                     'session':trace.get('session_index',0),'exclusions':settings['excluded_intervals'],'alignment':settings['alignment_markers']}
        if settings.get('gas_hash'):
            from .specialist import gas_analysis
            gas=json.loads(store.read_object(settings['gas_hash']))
            if gas.get('kind')!='gas':raise ValueError('Allegato gas non valido.')
            analysis['gas']=gas_analysis(gas['samples'],settings,analysis)
        return enrich(analysis,trace['samples'],settings)

    @app.post("/api/v1/tests")
    def save_test(data: TestInput):
        if require(data.athlete_id, 'athlete').get('status', 'active') != 'active' or require(data.protocol_id, 'protocol').get('status', 'active') != 'active':
            raise ValueError('Ripristinare atleta e protocollo prima di creare nuovi test.')
        analysis = preview(data)
        trace = json.loads(store.read_object(data.trace_hash))
        if any(t["trace_hash"] == data.trace_hash and t["athlete_id"] == data.athlete_id for t in store.list("test")):
            raise ValueError("Tracciato già associato a questo atleta.")
        a = require(data.athlete_id,"athlete")
        objects=[data.trace_hash,trace['original_hash']]
        if data.settings.gas_hash:
            gas=json.loads(store.read_object(data.settings.gas_hash));objects += [data.settings.gas_hash,gas['original_hash']]
        memberships = [m["group_id"] for m in store.list("membership") if m["athlete_id"] == a["id"] and m["start"] <= data.date.isoformat() and (not m.get("end") or m["end"] >= data.date.isoformat())]
        return store.save("test",{**data.model_dump(mode="json"),"organization_id":a["organization_id"],"athlete_snapshot":a,"group_ids":memberships,"samples":trace["samples"],"analysis":analysis,"objects":objects})

    @app.get("/api/v1/tests/{id}")
    def test(id: str):
        return require(id,"test")

    @app.get("/api/v1/tests/{id}/report/{format}")
    def test_report(id: str, format: Literal["pdf","md"], language: Literal['it','en']='it'):
        from .reports import report
        t = require(id,"test")
        cached=next((r for r in store.list('report') if r.get('renderer_version')=='0.5' and r.get('test_revision')==t['revision'] and r.get('format')==format and r.get('language','it')==language),None)
        if cached:
            body=store.read_object(cached['objects'][0])
        else:
            body = report(t,t.get('athlete_snapshot') or require(t["athlete_id"],"athlete"),require(t["protocol_id"],"protocol"),format,language)
            if not hasattr(store,'identity') or store.identity['certificate']['role']=='admin':
                digest=store.object(body)
                store.save('report',{'organization_id':t['organization_id'],'test_id':id,'renderer_version':'0.5','test_revision':t['revision'],'format':format,'language':language,'objects':[digest]})
        return download(body,"application/pdf" if format == "pdf" else "application/zip",f"test-{id}." + ("pdf" if format == "pdf" else "zip"))

    @app.get("/api/v1/export/{organization_id}")
    def export(organization_id: str):
        from .reports import export_csv
        require(organization_id,"organization")
        return download(export_csv(store,organization_id),"application/zip","storico-csv.zip")

    @app.get("/api/v1/backup")
    def backup():
        from .recovery import backup_bytes
        return download(backup_bytes(store),'application/zip','fuorigiri-backup-dati.zip')

    @app.post("/api/v1/sync")
    def sync(data: SyncInput):
        from .sync import exchange
        if hasattr(store,'identity') and store.identity.get('snapshot'):raise ValueError('Copia di consultazione: nessun accesso al canale della società originale.')
        key=store.identity['sync_key'] if hasattr(store,'identity') else data.key
        from .workspaces import write_json
        from datetime import datetime,timezone
        try:
            from .sync_service import lock
            with lock(store.root):result=exchange(store,data.folder,key)
        except (ValueError,OSError) as exc:
            write_json(store.root/'last-sync.json',{'at':datetime.now(timezone.utc).isoformat(),'ok':False,'error':str(exc)})
            raise ValueError(str(exc)) from exc
        if hasattr(store,'identity'):(store.root/'sync-folder.txt').write_text(data.folder,encoding='utf-8')
        write_json(store.root/'last-sync.json',{'at':datetime.now(timezone.utc).isoformat(),'ok':not result['errors'],**result})
        return result

    @app.post("/api/v1/sync/key")
    def key():
        from cryptography.fernet import Fernet
        return {"key":Fernet.generate_key().decode()}

    @app.get("/api/v1/conflicts")
    def conflicts():
        with store.connect() as db:
            return [json.loads(r[0]) for r in db.execute("SELECT body FROM conflicts")]

    from .features import install_features
    from .sync_service import install_sync_api
    install_sync_api(app,store)
    install_features(app, store, require, download, preview)
    from .analysis_api import install_analysis
    install_analysis(app,store,require,download)
    from .archive_report import install_archive_reports
    install_archive_reports(app,store,require,download)
    from .workspace_api import install_workspaces
    install_workspaces(app,workspaces,store,download)
    dist = Path(frontend) if frontend else Path(__file__).resolve().parents[2]/"frontend"/"dist"
    if dist.is_dir():
        app.mount("/",StaticFiles(directory=dist,html=True),name="frontend")
    return app
