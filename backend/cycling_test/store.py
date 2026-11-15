"""SQLite materialized records plus immutable changes; every write is transactional."""
import hashlib
import json
import sqlite3
from contextlib import contextmanager, closing
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

KINDS = {"organization", "group", "athlete", "membership", "measurement", "protocol", "test", "report", "import_batch", "zone_scheme", "default_profile", "analysis_preset"}


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False, separators=(",", ":"))


class ConflictError(ValueError):
    pass


def can_sign(store):
    """True when this device may add signed revisions: legacy archive or non-revoked admin."""
    if not hasattr(store, 'identity'):
        return True
    certificate = store.identity['certificate']
    return certificate['role'] == 'admin' and certificate['id'] not in store.revocations()


REPORT_KEY = ('organization_id', 'test_id', 'renderer_version', 'test_revision', 'query', 'source_revisions', 'format', 'language')


def save_report(store, payload, body):
    """Persist an exported report once per key; reading a report never needs write rights.

    Rendered bytes may differ between downloads (timestamps), so reuse is decided
    on the inputs that define the report, not on the file digest.
    """
    if not can_sign(store):
        return None
    key = encoded({k: payload.get(k) for k in REPORT_KEY})
    existing = next((r for r in store.list('report') if r.get('status') != 'deleted'
                     and encoded({k: r.get(k) for k in REPORT_KEY}) == key), None)
    if existing:
        return existing
    return store.save('report', {**payload, 'objects': [store.object(body)]})


class Store:
    def __init__(self, root):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "objects").mkdir(exist_ok=True)
        database=self.root/'archive.sqlite'
        if database.exists():
            with closing(sqlite3.connect(database)) as source:
                version=source.execute('PRAGMA user_version').fetchone()[0]
                if version>3:raise ValueError('Archivio creato con una versione più recente.')
                if version<3:
                    backup=self.root/'migrations'/'before-v3.sqlite'
                    backup.parent.mkdir(exist_ok=True)
                    if not backup.exists():
                        with closing(sqlite3.connect(backup)) as dest:source.backup(dest)
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, kind TEXT NOT NULL, revision TEXT NOT NULL, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS changes(id TEXT PRIMARY KEY, body TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS conflicts(id TEXT PRIMARY KEY, body TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS config(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            """)
            db.execute("INSERT OR IGNORE INTO config VALUES('device',?)", (str(uuid4()),))
            schema = db.execute("PRAGMA user_version").fetchone()[0]
            if schema > 3:
                raise ValueError('Archivio creato con una versione più recente.')
            # Additive migration: preserve all existing records and immutable changes.
            db.execute('CREATE INDEX IF NOT EXISTS records_kind ON records(kind)')
            db.execute("INSERT OR IGNORE INTO config VALUES('migration_v3',?)",(encoded({'from':schema,'legacy_method':'legacy_unknown','records_rewritten':False}),))
            db.execute('PRAGMA user_version=3')

    def history(self, id):
        with self.connect() as db:
            return [c['record'] for row in db.execute('SELECT body FROM changes ORDER BY rowid')
                    if (c := json.loads(row[0]))['record']['id'] == id]

    def save_batch(self, entries, bases=None):
        """Single transaction including the outbox, used after complete import validation."""
        with self.connect(immediate=True) as db:
            device = db.execute("SELECT value FROM config WHERE key='device'").fetchone()[0]
            result = []
            for kind, payload in entries:
                if kind not in KINDS:
                    raise ValueError('Tipo record non valido.')
                id, revision = payload.get('id', str(uuid4())), str(uuid4())
                base=(bases or {}).get(id)
                old=db.execute('SELECT revision,kind FROM records WHERE id=?', (id,)).fetchone()
                if (old and (old['revision']!=base or old['kind']!=kind)) or (not old and base):
                    raise ConflictError('Record importato modificato o già presente: ripetere anteprima.')
                data = {**payload, 'id': id, 'kind': kind, 'revision': revision}
                change = {'schema':1,'id':revision,'device':device,'base':base,'created_at':datetime.now(timezone.utc).isoformat(),'record':data}
                if hasattr(self, 'sign_change'):
                    change=self.sign_change(change,db=db)
                db.execute('INSERT OR REPLACE INTO records VALUES(?,?,?,?)',(id,kind,revision,encoded(data)))
                db.execute('INSERT INTO changes VALUES(?,?)',(revision,encoded(change)))
                result.append(data)
            return result

    def revise_batch(self, records, reason):
        with self.connect(immediate=True) as db:
            device=db.execute("SELECT value FROM config WHERE key='device'").fetchone()[0]
            for old in records:
                current=db.execute('SELECT revision FROM records WHERE id=?',(old['id'],)).fetchone()
                if not current or current[0]!=old['revision']:
                    raise ConflictError('Record modificato durante l’annullamento. Ricaricare.')
                revision=str(uuid4())
                record={**old,'status':'deleted','reason':reason,'revision':revision}
                change={'schema':1,'id':revision,'device':device,'base':old['revision'],'created_at':datetime.now(timezone.utc).isoformat(),'record':record}
                if hasattr(self,'sign_change'):change=self.sign_change(change,db=db)
                db.execute('UPDATE records SET revision=?,data=? WHERE id=?',(revision,encoded(record),record['id']))
                db.execute('INSERT INTO changes VALUES(?,?)',(revision,encoded(change)))

    @contextmanager
    def connect(self, immediate=False):
        """Immediate mode takes the write lock before the revision check, so a
        concurrent writer (UI or sync job) cannot slip between check and write."""
        db = sqlite3.connect(self.root / "archive.sqlite", timeout=30)
        db.row_factory = sqlite3.Row
        try:
            if immediate:
                db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def list(self, kind):
        with self.connect() as db:
            return [json.loads(r[0]) for r in db.execute("SELECT data FROM records WHERE kind=? ORDER BY rowid DESC", (kind,))]

    def get(self, id):
        with self.connect() as db:
            row = db.execute("SELECT data FROM records WHERE id=?", (id,)).fetchone()
        if row is None:
            raise KeyError(id)
        return json.loads(row[0])

    def save(self, kind, payload, id=None, base=None, parents=None):
        if kind not in KINDS:
            raise ValueError("Tipo record non valido.")
        id = id or str(uuid4())
        revision = str(uuid4())
        data = {**payload, "id": id, "kind": kind, "revision": revision}
        with self.connect(immediate=True) as db:
            old = db.execute("SELECT revision,kind FROM records WHERE id=?", (id,)).fetchone()
            if old and (old["revision"] != base or old["kind"] != kind):
                raise ConflictError("Il record è cambiato: ricaricare prima di salvare.")
            if not old and base:
                raise ConflictError("Revisione di origine non disponibile.")
            device = db.execute("SELECT value FROM config WHERE key='device'").fetchone()[0]
            change = {"schema": 1, "id": revision, "device": device, "base": base,
                      "created_at": datetime.now(timezone.utc).isoformat(), "record": data}
            if parents:
                change['parents']=list(dict.fromkeys([base]+parents))
            if hasattr(self, 'sign_change'):
                change = self.sign_change(change,db=db)
            db.execute("INSERT OR REPLACE INTO records VALUES(?,?,?,?)", (id, kind, revision, encoded(data)))
            db.execute("INSERT INTO changes VALUES(?,?)", (revision, encoded(change)))
        return data

    def object(self, content):
        digest = hashlib.sha256(content).hexdigest()
        dest = self.root / "objects" / digest
        if not dest.exists():
            tmp = dest.with_name(str(uuid4()) + ".tmp")
            tmp.write_bytes(content)
            tmp.replace(dest)
        return digest

    def read_object(self, digest):
        if len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Identificatore allegato non valido.")
        try:
            data = (self.root / "objects" / digest).read_bytes()
        except FileNotFoundError:
            raise ValueError("Allegato non presente nell'archivio locale.") from None
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError("Allegato corrotto.")
        return data
