import os
import secrets
from datetime import date
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.routing import Match, Mount
from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator

from . import __version__
from .store import Store, ConflictError
from .custom_fields import FieldDefinition

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


class GroupRevision(Group):
    base: str


class GroupLifecycle(Model):
    base: str
    status: Literal['active', 'deleted']
    scope: Literal['group', 'season'] = 'group'


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
    intervals_icu_id: str = Field(default="", max_length=40, pattern=r"^(?:i[0-9]+)?$")
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


class IntegrationSettings(Model):
    base: str
    intervals_icu_enabled: bool


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


from .maturation import MeasurementPayload as Measurement  # noqa: F401 - re-exported for scripts and tests


class RecoveryObservation(Model):
    after_s: float = Field(ge=0, le=86400)
    hr_bpm: float = Field(gt=0, le=250)


class LactateObservation(Model):
    at_s: float = Field(ge=0)
    mmol_l: float = Field(gt=0, le=40)
    note: str = ''
    step_number: int | None = Field(default=None, ge=1, le=1000)
    power_w: float | None = Field(default=None, ge=0, le=3000)
    delay_s: float = Field(default=0, ge=0, le=600)


class VO2Observation(Model):
    at_s: float = Field(ge=0)
    vo2_l_min: float = Field(gt=0)
    note: str = Field(default='', max_length=1000)


class Exclusion(Model):
    start_s: float = Field(ge=0)
    end_s: float = Field(gt=0)
    reason: str = Field(min_length=1, max_length=1000)


class Alignment(Model):
    number: int = Field(ge=1, le=1000)
    at_s: float = Field(ge=0)


class VentilatoryMarker(Model):
    at_s: float = Field(ge=0)
    evidence: str = Field(min_length=1, max_length=3000)


class MaximumVerification(Model):
    confirmed: bool = False
    evidence: str = Field(default='', max_length=3000)


class Settings(Model):
    custom_values: dict = Field(default_factory=dict, max_length=50)
    extra_fields: list[FieldDefinition] = Field(default_factory=list, max_length=50)
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
    lactate_levels: list[float] = Field(default_factory=lambda: [2.0, 3.0, 4.0], min_length=1, max_length=20)
    lactate: list[LactateObservation] = Field(default_factory=list, max_length=100)
    zone_schemes: list[dict] | None = None
    preset_id: str | None = None
    excluded_intervals: list[Exclusion] = Field(default_factory=list, max_length=100)
    alignment_markers: list[Alignment] = Field(default_factory=list, max_length=1000)
    conditions: dict[str, str] = Field(default_factory=dict, max_length=30)
    vo2: list[VO2Observation] = Field(default_factory=list, max_length=20000)
    gas_hash: str | None = None
    gas_offset_s: float = Field(default=0, ge=-86400, le=86400)
    ventilatory_markers: dict[Literal['vt1', 'vt2'], VentilatoryMarker] = Field(default_factory=dict)
    vo2max_verification: MaximumVerification = Field(default_factory=MaximumVerification)
    threshold_calibration: dict[str, str] = Field(default_factory=dict, max_length=20)

    @field_validator('lactate_levels', mode='before')
    @classmethod
    def validate_lactate_levels(cls, value):
        from .lactate_levels import validate_levels

        return validate_levels(value)

    @model_validator(mode='after')
    def validate_observations(self):
        from .zones import validate
        from .lactate_levels import validate_levels

        self.lactate_levels = validate_levels(self.lactate_levels)
        if self.zone_schemes is not None:
            if len(self.zone_schemes) > 2:
                raise ValueError('Un solo schema per ciascun canale.')
            channels = []
            for scheme in self.zone_schemes:
                validate(scheme)
                channels.append(scheme['channel'])
            if len(set(channels)) != len(channels):
                raise ValueError('Canale duplicato negli schemi zone.')
        if self.vo2:
            times = [r.at_s for r in self.vo2]
            if any(b <= a for a, b in zip(times, times[1:])):
                raise ValueError('VO2: istanti crescenti, senza duplicati.')
            if self.gas_hash:
                raise ValueError('Scegliere una sola fonte VO2: misure manuali oppure file gas.')
        times = [r.after_s for r in self.recovery_manual]
        if len(times) != len(set(times)):
            raise ValueError('Tempi di recupero duplicati.')
        if self.rpe is not None:
            if (
                self.rpe_scale == 'CR10 dichiarata'
                and self.rpe > 10
                or self.rpe_scale == 'Borg 6-20'
                and not 6 <= self.rpe <= 20
            ):
                raise ValueError('RPE incompatibile con la scala selezionata.')
        if any(len(v) > 3000 for v in self.conditions.values()):
            raise ValueError('Condizioni: testo troppo lungo.')
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


# Defence in depth for the pages served by the desktop backend (RT-18). Inline
# styles are needed by React style attributes and Plotly; no inline or eval'd
# scripts. The Android shell serves the same assets through its own loader.
CONTENT_SECURITY_POLICY = "; ".join(
    (
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self' 'unsafe-inline'",
        "img-src 'self' data: blob:",
        "font-src 'self' data:",
        "connect-src 'self'",
        "object-src 'none'",
        "base-uri 'none'",
        "form-action 'self'",
        "frame-ancestors 'none'",
    )
)


def create_app(root=None, token=None, frontend=None):
    legacy = Store(root or os.environ.get("FUORIGIRI_DATA", ".local"))
    from .workspaces import Workspaces

    workspaces = Workspaces(legacy.root, legacy)
    store = workspaces.proxy
    token = token or os.environ.get("FUORIGIRI_TOKEN") or secrets.token_urlsafe(32)
    app = FastAPI(title="Fuorigiri Performance Lab", version=__version__, docs_url=None, redoc_url=None)
    app.state.store = store
    app.state.token = token

    def viewer_route(scope):
        for route in app.router.routes:
            if isinstance(route, Mount):
                continue
            match, child = route.matches(scope)
            if match == Match.FULL:
                return getattr(child.get('endpoint'), 'viewer_allowed', False)
        return False

    @app.middleware("http")
    async def local_only(request: Request, call_next):
        if request.url.hostname not in ("127.0.0.1", "localhost", "testserver"):
            return JSONResponse({"detail": "Host non consentito"}, status_code=403)
        if request.url.path.startswith("/api/"):
            supplied = request.headers.get("X-Fuorigiri-Token", "")
            if not supplied.isascii() or not secrets.compare_digest(supplied, token):
                return JSONResponse({"detail": "Sessione non autorizzata. Riaprire l'app."}, status_code=401)
        try:
            selected = workspaces.get(request.headers.get('X-Fuorigiri-Workspace', ''))
        except ValueError as exc:
            return JSONResponse({'detail': str(exc)}, status_code=422)
        marker = store.selected.set(selected)
        if hasattr(selected, 'identity'):
            identity = selected.identity
            read_only = (
                identity['certificate']['role'] == 'viewer' or identity['certificate']['id'] in selected.revocations()
            )
            # Exceptions are declared on the routes with @viewer_allowed (RT-20).
            allowed = request.method in ('GET', 'HEAD') or viewer_route(request.scope)
            if read_only and not allowed:
                store.selected.reset(marker)
                return JSONResponse(
                    {'detail': 'Visualizzatore: operazione di modifica non consentita.'}, status_code=403
                )
        origin = request.headers.get("origin")
        if origin and origin not in {
            str(request.base_url).rstrip("/"),
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        }:
            store.selected.reset(marker)
            return JSONResponse({"detail": "Origine non consentita"}, status_code=403)
        try:
            response = await call_next(request)
        finally:
            store.selected.reset(marker)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        if not request.url.path.startswith("/api/"):
            response.headers["Content-Security-Policy"] = CONTENT_SECURITY_POLICY
        return response

    @app.exception_handler(ValueError)
    async def value_error(request, exc):
        return JSONResponse({"detail": str(exc)}, status_code=409 if isinstance(exc, ConflictError) else 422)

    @app.exception_handler(KeyError)
    async def missing(request, exc):
        return JSONResponse({"detail": "Record non trovato."}, status_code=404)

    def require(id, kind):
        record = store.get(id)
        if record["kind"] != kind:
            raise ValueError("Riferimento di tipo errato.")
        return record

    def download(content, media, name):
        return Response(content, media_type=media, headers={"Content-Disposition": f'attachment; filename="{name}"'})

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/api/v1/state")
    def state():
        result = {
            kind: store.list(kind)
            for kind in ("organization", "group", "athlete", "membership", "measurement", "protocol")
        }
        result['deleted_measurement'] = [r for r in result['measurement'] if r.get('status') == 'deleted']
        for kind in ('membership', 'measurement'):
            result[kind] = [r for r in result[kind] if r.get('status') != 'deleted']
        # Samples are dropped in SQL: the list never needs them (RT-01).
        result["test"] = [
            {**t, 'has_trace': bool(present or t.get('trace_hash'))}
            for t, present in store.list_without_samples("test")
        ]
        result['operator'] = (
            {k: store.identity['certificate'][k] for k in ('name', 'role', 'id')}
            if hasattr(store, 'identity')
            else {'name': 'Locale', 'role': 'admin'}
        )
        if hasattr(store, 'identity'):
            result['operator'].update(
                owner=bool(store.identity.get('authority_private')),
                snapshot=bool(store.identity.get('snapshot')),
                revoked=store.identity['certificate']['id'] in store.revocations(),
            )
        return result

    from .registry_api import install as install_registry

    install_registry(app, store, require)

    from .incremental_api import install as install_incremental

    preview = install_incremental(app, store, require, download)

    from .backup_api import install as install_backup

    install_backup(app, store, require, download)

    from .exchange_api import install as install_exchange

    install_exchange(app, store)

    from .features import install_features
    from .custom_tests import install_api as install_custom_api

    install_custom_api(app, store)
    from .anaerobic import install_api as install_anaerobic_api

    install_anaerobic_api(app, store)
    from .sync_service import install_sync_api

    install_sync_api(app, store)
    install_features(app, store, require, download, preview)
    from .analysis_api import install_analysis

    install_analysis(app, store, require, download)
    from .archive_report import install_archive_reports

    install_archive_reports(app, store, require, download)
    from .workspace_api import install_workspaces

    install_workspaces(app, workspaces, store, download)
    from .training_zones import install as install_training_zones

    install_training_zones(app, store, require)
    from .sync_jobs import install as install_sync_jobs

    install_sync_jobs(app, store)
    from .sync_space import install as install_sync_space

    install_sync_space(app, store)
    from .maturation import install_api as install_maturation

    install_maturation(app, store, require, download)

    @app.get('/api/v1/legal')
    def legal():
        import sys
        from . import branding

        roots = [Path(__file__).resolve().parents[2], Path(sys.executable).parent]
        if branding.MOBILE_ASSETS is not None:
            roots.insert(0, branding.MOBILE_ASSETS / 'legal')

        def read(name):
            for root in roots:
                if (root / name).is_file():
                    return (root / name).read_text(encoding='utf-8')
            raise ValueError('Documento legale non incluso nel pacchetto: ' + name)

        from . import __version__ as v

        return {'version': v, 'license': read('LICENSE'), 'third_party': read('THIRD_PARTY.md')}

    dist = Path(frontend) if frontend else Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if dist.is_dir():
        app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
    return app
