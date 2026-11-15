"""Signed encrypted exchange over an immutable-object transport."""
import hashlib
import json
from pathlib import Path
from uuid import uuid4
from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidSignature
from .store import encoded, KINDS


def exchange(store, folder, key, transport=None, verify_existing=True, protocol=1):
    if protocol not in (0,1,2):raise ValueError('Formato sincronizzazione non supportato.')
    if protocol==2:
        # v1 is read first, preserving controls, rotations and legacy events.
        previous=exchange(store,folder,key,transport,verify_existing,protocol=0)
        from .sync_v2 import exchange_v2
        return exchange_v2(store,folder,key,transport,verify_existing,previous)
    with store.connect() as db:
        changes=[json.loads(r[0]) for r in db.execute('SELECT body FROM changes')] if protocol else []
    from .society_scope import check_archive
    with store.connect() as db:
        organization=check_archive(store,(json.loads(r[0]) for r in db.execute('SELECT body FROM changes')))
        known={r[0] for r in db.execute('SELECT id FROM changes')}
    cipher = Fernet(key.encode())
    channel = hashlib.sha256(key.encode()).hexdigest()[:24]
    from .transports import FolderTransport
    transport=transport or FolderTransport(folder,channel,store.root)
    names=set(transport.list())
    managed=hasattr(store,'identity')
    if managed:
        from .workspaces import verify,write_json
        if 'rotation.json' in names:
            try:
                notice=json.loads(transport.get('rotation.json'))
                verify(store.identity['authority_public'],{k:v for k,v in notice.items() if k!='signature'},notice['signature'])
                if notice['workspace']!=store.identity['workspace'] or notice['from']!=hashlib.sha256(key.encode()).hexdigest():raise ValueError('Avviso di rotazione non valido.')
            except (InvalidSignature,KeyError,TypeError) as exc:raise ValueError('Firma della rotazione non valida.') from exc
            raise ValueError('Chiave del canale ruotata dal fondatore. Applicare un nuovo invito; le modifiche locali restano conservate.')
        if store.identity.get('snapshot'):raise ValueError('Copia di consultazione: scambio non consentito.')
        # Read before publish. Immutable signed versions prevent a stale owner
        # overwriting newer revocations. Same-version forks fail closed.
        updates=[]
        for stem in ('access','revocations'):
            local=store.root/(stem+'.json');versions={}
            raw_values=[local.read_bytes()] if local.exists() else []
            raw_values += [transport.get(n) for n in sorted(names) if n==stem+'.json' or n.startswith(stem+'-') and n.endswith('.json')]
            for raw in raw_values:
                try:
                    if len(raw)>4_000_000:raise ValueError('Controllo troppo grande.')
                    value=json.loads(raw)
                    if not isinstance(value,dict):raise ValueError('Controllo della società non valido.')
                    verify(store.identity['authority_public'],{k:v for k,v in value.items() if k!='signature'},value['signature'])
                    if value['workspace']!=store.identity['workspace'] or type(value['version']) is not int or value['version']<1:
                        raise ValueError('Controllo della società non valido.')
                    if stem=='access' and (not isinstance(value.get('members'),list) or not isinstance(value.get('founder_id'),str)):
                        raise ValueError('Schema dell’elenco accessi non valido.')
                    if stem=='revocations' and (not isinstance(value.get('revoked'),list) or any(not isinstance(x,str) for x in value['revoked']) or not isinstance(value.get('accepted',{}),dict)):
                        raise ValueError('Schema delle revoche non valido.')
                    previous=versions.get(value['version'])
                    if previous and encoded(previous)!=encoded(value):raise ValueError('Versioni degli accessi divergenti: usare un solo dispositivo fondatore e recuperare lo stato corretto.')
                    versions[value['version']]=value
                except (InvalidSignature,KeyError,TypeError) as exc:raise ValueError('Firma del controllo accessi non valida.') from exc
            if stem=='revocations':
                revoked_known=set()
                for version in sorted(versions):
                    current=set(versions[version]['revoked'])
                    if not revoked_known.issubset(current):raise ValueError('Le revoche non possono essere rimosse da un controllo successivo.')
                    revoked_known=current
            if versions:updates.append((stem,local,versions[max(versions)]))
        for stem,local,value in updates:
            write_json(local,value)
            if store.identity.get('authority_private'):
                raw=encoded(value).encode();digest=hashlib.sha256(raw).hexdigest()
                name=f'{stem}-{value["version"]:010d}-{digest}.json'
                transport.put(name,raw);names.add(name)
    sent = received = pending = 0
    for change in changes:
        if protocol==0:break
        if managed:
            # Viewers relay no writes; admins only relay already authenticated events.
            if store.identity['certificate']['role']!='admin' or store.identity['certificate']['id'] in store.revocations():continue
            try:store.verify_change(change)
            except (ValueError,KeyError,InvalidSignature):continue
        name=change['id']+'.ctsync'
        if name not in names:
            # Self-contained packets: attachments travel with the change.
            import base64
            blobs = {h:base64.b64encode(store.read_object(h)).decode() for h in change["record"].get("objects", [])}
            body = cipher.encrypt(encoded({"change":change,"objects":blobs}).encode())
            sent += int(transport.put(name,body));names.add(name)
    errors = [];downloaded=skipped=0
    candidates = []
    for name in sorted(names):
        if not name.endswith('.ctsync'):continue
        if not verify_existing and name[:-7] in known:
            skipped+=1;continue
        try:
            downloaded+=1
            payload = json.loads(cipher.decrypt(transport.get(name)))
            if not isinstance(payload,dict) or not isinstance(payload.get('change'),dict) or not isinstance(payload['change'].get('record'),dict):
                raise ValueError('Struttura del pacchetto non valida.')
            change = payload["change"]
            if managed:store.verify_change(change)
            r = change["record"]
            if change["schema"] != 1 or r["kind"] not in KINDS or change["id"] != r["revision"] or name!=change['id']+'.ctsync':
                raise ValueError("Schema non supportato")
            with store.connect() as db:
                existing = db.execute("SELECT body FROM changes WHERE id=?", (change["id"],)).fetchone()
            if existing:
                if encoded(change) != existing[0]:
                    raise ValueError("ID duplicato con contenuto diverso")
                continue
            from .society_scope import check_record
            check_record(r,organization)
            import base64
            for h in r.get("objects", []):
                content = base64.b64decode(payload["objects"][h], validate=True)
                if hashlib.sha256(content).hexdigest() != h:
                    raise ValueError("Checksum allegato errato")
                store.object(content)
            if not organization:organization=r['id'] if r['kind']=='organization' else r.get('organization_id')
            candidates.append(change)
        except (ValueError, KeyError, OSError, InvalidToken, InvalidSignature, TypeError) as exc:
            errors.append(f"{name}: pacchetto incompleto o non valido ({type(exc).__name__})")
    received,pending,conflicts=apply_candidates(store,candidates)
    return {"written_to_folder":sent,"published":sent,"received":received,"pending":pending,"conflicts":conflicts,"errors":errors,
            "downloaded_packets":downloaded,"known_packets_skipped":skipped,"full_verification":verify_existing,
            "transport":getattr(transport,"kind","webdav" if transport.remote else "folder"),"remote_verified":transport.remote,
            "status":"Pubblicazioni Servizio remoto rilette e verificate." if transport.remote else "Scambio locale eseguito. Upload cloud non verificabile dall'app."}


def apply_candidates(store,candidates):
    received=pending=0
    while candidates:
        progress = False
        remaining = []
        for change in candidates:
            r = change["record"]
            with store.connect(immediate=True) as db:
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
    return received,pending,conflicts
