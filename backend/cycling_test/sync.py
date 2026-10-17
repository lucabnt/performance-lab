"""Experimental encrypted folder transport. No inference of remote upload status."""
import hashlib
import json
from pathlib import Path
from uuid import uuid4
from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidSignature
from .store import encoded, KINDS


def exchange(store, folder, key):
    folder = Path(folder).resolve()
    if not folder.is_dir():
        raise ValueError("La cartella deve già esistere ed essere disponibile offline.")
    if folder == store.root.resolve() or store.root.resolve() in folder.parents or folder in store.root.resolve().parents:
        raise ValueError("La cartella di scambio deve essere separata dall'archivio locale.")
    cipher = Fernet(key.encode())
    channel = hashlib.sha256(key.encode()).hexdigest()[:24]
    shared = folder / ("ciclo-test-" + channel)
    shared.mkdir(exist_ok=True)
    managed=hasattr(store,'identity')
    if managed:
        from .workspaces import verify,write_json
        # The founder publishes the public directory; readers can inspect users
        # and roles without possessing invitation or authority private keys.
        access_local=store.root/'access.json';access_shared=shared/'access.json'
        if access_local.exists() and store.identity.get('authority_private'):
            tmp=shared/(str(uuid4())+'.tmp');tmp.write_bytes(access_local.read_bytes());tmp.replace(access_shared)
        if access_shared.exists():
            try:
                access=json.loads(access_shared.read_text(encoding='utf-8'))
                verify(store.identity['authority_public'],{k:v for k,v in access.items() if k!='signature'},access['signature'])
                if access['workspace']!=store.identity['workspace']:raise ValueError('Elenco di un’altra società.')
                previous=json.loads(access_local.read_text(encoding='utf-8')) if access_local.exists() else {'version':-1}
                if access['version']>previous['version']:write_json(access_local,access)
            except (InvalidSignature,KeyError,TypeError) as exc:raise ValueError('Elenco accessi non valido.') from exc
        revocation_file=shared/'revocations.json'
        local=store.root/'revocations.json'
        if local.exists() and store.identity.get('authority_private'):
            tmp=shared/(str(uuid4())+'.tmp');tmp.write_bytes(local.read_bytes());tmp.replace(revocation_file)
        if revocation_file.exists():
            rev=json.loads(revocation_file.read_text())
            try:verify(store.identity['authority_public'],{k:v for k,v in rev.items() if k!='signature'},rev['signature'])
            except (InvalidSignature,KeyError,TypeError) as exc:raise ValueError('Elenco revoche non valido.') from exc
            if rev['workspace']!=store.identity['workspace']:raise ValueError('Revoche di un altro workspace.')
            previous=json.loads(local.read_text()) if local.exists() else {'version':-1}
            if rev['version']>previous['version']:local.write_text(encoded(rev),encoding='utf-8')
    with store.connect() as db:
        changes = [json.loads(r[0]) for r in db.execute("SELECT body FROM changes")]
    sent = received = pending = 0
    for change in changes:
        if managed:
            # Viewers relay no writes; admins only relay already authenticated events.
            if store.identity['certificate']['role']!='admin':continue
            try:store.verify_change(change)
            except (ValueError,KeyError,InvalidSignature):continue
        dest = shared / (change["id"] + ".ctsync")
        if not dest.exists():
            # Self-contained packets: attachments travel with the change.
            import base64
            blobs = {h:base64.b64encode(store.read_object(h)).decode() for h in change["record"].get("objects", [])}
            body = cipher.encrypt(encoded({"change":change,"objects":blobs}).encode())
            tmp = shared / (str(uuid4()) + ".tmp")
            tmp.write_bytes(body)
            tmp.replace(dest)
            sent += 1
    errors = []
    candidates = []
    for path in shared.glob("*.ctsync"):
        try:
            if path.stat().st_size > 80_000_000:
                raise ValueError("Pacchetto troppo grande")
            payload = json.loads(cipher.decrypt(path.read_bytes()))
            change = payload["change"]
            if managed:store.verify_change(change)
            r = change["record"]
            if change["schema"] != 1 or r["kind"] not in KINDS or change["id"] != r["revision"]:
                raise ValueError("Schema non supportato")
            with store.connect() as db:
                existing = db.execute("SELECT body FROM changes WHERE id=?", (change["id"],)).fetchone()
            if existing:
                if encoded(change) != existing[0]:
                    raise ValueError("ID duplicato con contenuto diverso")
                continue
            import base64
            for h in r.get("objects", []):
                content = base64.b64decode(payload["objects"][h], validate=True)
                if hashlib.sha256(content).hexdigest() != h:
                    raise ValueError("Checksum allegato errato")
                store.object(content)
            candidates.append(change)
        except (ValueError, KeyError, OSError, InvalidToken, InvalidSignature, TypeError) as exc:
            errors.append(f"{path.name}: pacchetto incompleto o non valido ({type(exc).__name__})")
    while candidates:
        progress = False
        remaining = []
        for change in candidates:
            r = change["record"]
            with store.connect() as db:
                dependencies=change.get('parents',[change['base']])
                if any(parent and not db.execute("SELECT 1 FROM changes WHERE id=?",(parent,)).fetchone() for parent in dependencies):
                    remaining.append(change)
                    continue
                old = db.execute("SELECT revision FROM records WHERE id=?",(r["id"],)).fetchone()
                if (old[0] if old else None) not in dependencies:
                    db.execute("INSERT OR IGNORE INTO conflicts VALUES(?,?)",(change["id"],encoded(change)))
                else:
                    db.execute("INSERT OR REPLACE INTO records VALUES(?,?,?,?)",(r["id"],r["kind"],r["revision"],encoded(r)))
                    for parent in change.get('parents',[]):db.execute('DELETE FROM conflicts WHERE id=?',(parent,))
                db.execute("INSERT INTO changes VALUES(?,?)",(change["id"],encoded(change)))
            received += 1
            progress = True
        candidates = remaining
        if not progress:
            pending = len(candidates)
            break
    with store.connect() as db:
        conflicts = db.execute("SELECT count(*) FROM conflicts").fetchone()[0]
    return {"written_to_folder":sent,"received":received,"pending":pending,"conflicts":conflicts,"errors":errors,"status":"Scambio locale eseguito. Upload cloud non verificabile dall'app."}
