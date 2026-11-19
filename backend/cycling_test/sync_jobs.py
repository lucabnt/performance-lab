"""Device-local sync jobs: networking never occupies the UI request/Runtime lock."""

from .access import viewer_allowed
import json
from pathlib import Path
from cycling_suite.jobs import JobRegistry, ObservedTransport  # noqa: F401  (ObservedTransport re-exported)
from .workspaces import write_json

# Job runner shared with the suite (cycling-suite-core ``jobs``).
_registry = JobRegistry(
    product='Fuorigiri',
    failed='Sincronizzazione non completata. Controllare connessione e autorizzazioni; i dati locali sono conservati.',
    interrupted='Scambio interrotto dalla chiusura del processo. Riprovare: lo storico locale è conservato.',
)


def _root(store):
    return Path(store) if isinstance(store, (str, Path)) else store.root


def status(store):
    return _registry.status(_root(store))


def start(store, verify_all=False):
    from .sync_service import require_managed, run_sync

    require_managed(store)
    return _registry.start(
        store.root,
        lambda progress: run_sync(store, verify_all, progress=progress),
        full_verification=bool(verify_all),
    )


def wait(store, timeout=540):
    return _registry.wait(store.root, timeout)


def install(app, store):
    from pydantic import BaseModel
    from .sync_service import require_managed

    class Start(BaseModel):
        verify_all: bool = False

    class Automatic(BaseModel):
        enabled: bool

    @app.get('/api/v1/sync/automatic')
    def automatic():
        selected = store.selected.get()
        require_managed(selected)
        from .sync_service import configuration

        config = configuration(selected)
        path = selected.root / 'sync-automatic.json'
        enabled = json.loads(path.read_text(encoding='utf-8')).get('enabled', True) if path.exists() else True
        ready = (
            bool(config.get('folder'))
            if config['transport'] == 'folder'
            else bool(config.get('url'))
            if config['transport'] in ('webdav', 'service')
            else bool(config.get('client_id') and (config.get('root_id') or config.get('root_path')))
        )
        return {'enabled': enabled, 'configured': ready}

    @app.put('/api/v1/sync/automatic')
    @viewer_allowed
    def set_automatic(data: Automatic):
        selected = store.selected.get()
        require_managed(selected)
        write_json(selected.root / 'sync-automatic.json', {'enabled': data.enabled})
        return automatic()

    @app.get('/api/v1/sync/job')
    def job():
        selected = store.selected.get()
        require_managed(selected)
        return status(selected)

    @app.post('/api/v1/sync/start')
    @viewer_allowed
    def begin(data: Start):
        return start(store.selected.get(), data.verify_all)
