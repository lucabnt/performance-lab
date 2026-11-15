"""Device-local sync jobs: networking never occupies the UI request/Runtime lock."""

from .access import viewer_allowed
import json
import threading
import time
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4
from .workspaces import write_json

_guard = threading.RLock()
_jobs = {}


def now():
    return datetime.now(timezone.utc).isoformat()


def status(store):
    root = Path(store) if isinstance(store, (str, Path)) else store.root
    key = str(root.resolve())
    with _guard:
        job = _jobs.get(key)
        if job:
            result = {k: v for k, v in job.items() if not k.startswith('_')}
            if result['status'] == 'running':
                result['elapsed_s'] = round(time.monotonic() - job['_start'], 1)
            return result
        try:
            result = json.loads((root / 'sync-job.json').read_text(encoding='utf-8'))
        except (ValueError, OSError):
            return {'status': 'idle'}
        if result.get('status') == 'running':
            result.update(
                status='interrupted',
                phase='interrupted',
                error='Scambio interrotto dalla chiusura del processo. Riprovare: lo storico locale è conservato.',
            )
        return result


class ObservedTransport:
    def __init__(self, base, progress):
        self.base = base
        self.progress = progress

    def __getattr__(self, key):
        return getattr(self.base, key)

    def list(self):
        self.progress('inventory')
        return self.base.list()

    def get(self, name):
        self.progress('receiving')
        result = self.base.get(name)
        self.progress('receiving', reads=1)
        return result

    def put(self, name, body):
        self.progress('publishing')
        result = self.base.put(name, body)
        self.progress('publishing', writes=int(bool(result)))
        return result


def start(store, verify_all=False):
    from .sync_service import require_managed, run_sync

    require_managed(store)
    key = str(store.root.resolve())
    with _guard:
        previous = _jobs.get(key)
        if previous and previous['status'] == 'running':
            return status(store)
        job = {
            'id': str(uuid4()),
            'status': 'running',
            'phase': 'preparing',
            'started_at': now(),
            'full_verification': bool(verify_all),
            'reads': 0,
            'writes': 0,
            'elapsed_s': 0,
            '_start': time.monotonic(),
            '_persist': 0,
            '_done': threading.Event(),
        }
        _jobs[key] = job

        def persist():
            write_json(store.root / 'sync-job.json', {k: v for k, v in job.items() if not k.startswith('_')})

        persist()

        def progress(phase, reads=0, writes=0):
            with _guard:
                job.update(phase=phase, reads=job['reads'] + reads, writes=job['writes'] + writes)
                if time.monotonic() - job['_persist'] >= 0.5:
                    job['elapsed_s'] = round(time.monotonic() - job['_start'], 1)
                    persist()
                    job['_persist'] = time.monotonic()

        def work():
            try:
                result = run_sync(store, verify_all, progress=progress)
                with _guard:
                    job.update(status='completed', phase='completed', result=result)
            except Exception:
                # No provider URLs, credentials or exception text in the public status.
                with _guard:
                    job.update(
                        status='failed',
                        phase='failed',
                        error='Sincronizzazione non completata. Controllare connessione e autorizzazioni; i dati locali sono conservati.',
                    )
            finally:
                with _guard:
                    job.update(finished_at=now(), elapsed_s=round(time.monotonic() - job['_start'], 1))
                    try:
                        persist()
                    finally:
                        job['_done'].set()

        threading.Thread(target=work, name='Fuorigiri-sync-' + job['id'][:8], daemon=True).start()
        return status(store)


def wait(store, timeout=540):
    key = str(store.root.resolve())
    with _guard:
        event = _jobs[key]['_done']
    event.wait(timeout)
    return status(store)


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
