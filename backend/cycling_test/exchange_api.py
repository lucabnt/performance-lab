"""Folder exchange (legacy key and managed archives), sync key and conflicts."""

import json

from .access import viewer_allowed
from .api import SyncInput


def install(app, store):
    @app.post("/api/v1/sync")
    @viewer_allowed
    def sync(data: SyncInput):
        from .sync import exchange

        if hasattr(store, 'identity') and store.identity.get('snapshot'):
            raise ValueError('Copia di consultazione: nessun accesso al canale della società originale.')
        if hasattr(store, 'identity'):
            from .sync_service import configure, run_sync

            configure(store, {'transport': 'folder', 'folder': data.folder})
            return run_sync(store, verify_all=True)
        key = data.key
        from .workspaces import write_json
        from datetime import datetime, timezone

        try:
            from .sync_service import lock

            with lock(store.root):
                result = exchange(store, data.folder, key)
        except (ValueError, OSError) as exc:
            write_json(
                store.root / 'last-sync.json',
                {'at': datetime.now(timezone.utc).isoformat(), 'ok': False, 'error': str(exc)},
            )
            raise ValueError(str(exc)) from exc
        write_json(
            store.root / 'last-sync.json',
            {'at': datetime.now(timezone.utc).isoformat(), 'ok': not result['errors'], **result},
        )
        return result

    @app.post("/api/v1/sync/key")
    def key():
        from cryptography.fernet import Fernet

        return {"key": Fernet.generate_key().decode()}

    @app.get("/api/v1/conflicts")
    def conflicts():
        with store.connect() as db:
            return [json.loads(r[0]) for r in db.execute("SELECT body FROM conflicts")]
