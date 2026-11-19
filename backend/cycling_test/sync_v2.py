"""V2 immutable encrypted chunks and small history pages.

Original signed changes are reconstructed before authentication. Chunk addresses
are HMACs scoped to the channel key, never public plaintext content hashes.
No history or v1 files are deleted. A checkpoint inventories complete pages;
it is a bootstrap aid, not authority to skip event signature verification.
"""

import hashlib
import hmac
import json
import tempfile
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidSignature
from cycling_suite.exchange import publish_immutable
from .store import encoded, KINDS

CHUNK = 1_048_576
PAGE = 32
MAX_BLOB = 16_000_000_000
MAX_JSON = 80_000_000


class Objects:
    def __init__(self, store, key, transport, names, verify_all=False):
        self.store = store
        self.key = key.encode()
        self.cipher = Fernet(self.key)
        self.transport = transport
        self.names = names
        self.verify_all = verify_all
        self.uploaded = 0
        self.downloaded = 0
        self.validated = {}
        self.published_blobs = {}

    def address(self, raw):
        return hmac.new(self.key, raw, hashlib.sha256).hexdigest()

    def immutable(self, name, raw):
        if name not in self.names:
            # Two writers may encrypt identical content with different IVs.
            created = publish_immutable(
                self.transport, name, self.cipher.encrypt(raw), lambda existing: self.cipher.decrypt(existing) == raw
            )
            self.names.add(name)
            self.uploaded += int(created)
        elif self.verify_all:
            if self.cipher.decrypt(self.transport.get(name)) != raw:
                raise ValueError('Oggetto remoto alterato.')

    def publish(self, stream):
        chunks = []
        digest = hashlib.sha256()
        size = 0
        while raw := stream.read(CHUNK):
            size += len(raw)
            if size > MAX_BLOB:
                raise ValueError('Oggetto oltre il limite v2 di 16 GB.')
            digest.update(raw)
            name = 'blob2-' + self.address(raw) + '.ctobj'
            self.immutable(name, raw)
            chunks.append(name)
        return {'sha256': digest.hexdigest(), 'size': size, 'chunks': chunks}

    def fetch(self, description):
        if (
            not isinstance(description, dict)
            or type(description.get('size')) is not int
            or not 0 <= description['size'] <= MAX_BLOB
        ):
            raise ValueError('Descrittore v2 non valido.')
        from .transports import safe_name

        chunks = description['chunks']
        digest = description['sha256']
        if not isinstance(chunks, list) or len(chunks) != (description['size'] + CHUNK - 1) // CHUNK:
            raise ValueError('Inventario blocchi non valido.')
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
            raise ValueError('Hash non valido.')
        dest = self.store.root / 'objects' / digest
        if dest.is_symlink():
            raise ValueError('Allegato simbolico non consentito.')
        signature = (description['size'], tuple(chunks))
        if self.validated.get(digest) == signature and dest.is_file() and dest.stat().st_size == description['size']:
            return dest
        if dest.exists() and not self.verify_all:
            with dest.open('rb') as src:
                if (
                    dest.stat().st_size == description['size']
                    and hashlib.file_digest(src, 'sha256').hexdigest() == digest
                ):
                    self.validated[digest] = signature
                    return dest
        with tempfile.NamedTemporaryFile(dir=self.store.root / 'objects', suffix='.tmp', delete=False) as out:
            temp = Path(out.name)
            actual = hashlib.sha256()
            size = 0
            try:
                for i, name in enumerate(chunks):
                    safe_name(name)
                    if not name.startswith('blob2-') or not name.endswith('.ctobj'):
                        raise ValueError('Nome blocco non valido.')
                    cache = self.store.root / 'parts'
                    cache.mkdir(exist_ok=True)
                    part = cache / name[6:-6]
                    if part.is_symlink():
                        raise ValueError('Cache simbolica non consentita.')
                    raw = None
                    if part.exists() and not self.verify_all:
                        try:
                            candidate = self.cipher.decrypt(part.read_bytes())
                            if name == 'blob2-' + self.address(candidate) + '.ctobj':
                                raw = candidate
                        except (InvalidToken, OSError):
                            pass
                    if raw is None:
                        token = self.transport.get(name)
                        self.downloaded += 1
                        raw = self.cipher.decrypt(token)
                        if name != 'blob2-' + self.address(raw) + '.ctobj':
                            raise ValueError('Indirizzo blocco errato.')
                        with tempfile.NamedTemporaryFile(dir=cache, suffix='.tmp', delete=False) as cached:
                            cached.write(token)
                            temporary = Path(cached.name)
                        try:
                            temporary.replace(part)
                        finally:
                            temporary.unlink(missing_ok=True)
                    expected = min(CHUNK, description['size'] - i * CHUNK)
                    if len(raw) != expected or name != 'blob2-' + self.address(raw) + '.ctobj':
                        raise ValueError('Integrità blocco v2 non valida.')
                    out.write(raw)
                    actual.update(raw)
                    size += len(raw)
                if size != description['size'] or actual.hexdigest() != digest:
                    raise ValueError('Oggetto v2 incompleto o alterato.')
            except Exception:
                out.close()
                temp.unlink(missing_ok=True)
                raise
        try:
            temp.replace(dest)
        finally:
            temp.unlink(missing_ok=True)
        self.validated[digest] = signature
        for name in chunks:
            try:
                (self.store.root / 'parts' / name[6:-6]).unlink(missing_ok=True)
            except OSError:
                pass  # Cache cleanup never invalidates a complete object.
        return dest


def pack(change, objects):
    detached = []

    def walk(value, path):
        if isinstance(value, list):
            # Streaming encoder keeps large sample arrays out of the envelope.
            if len(value) > 32 and path and path[0] == 'record':
                with tempfile.SpooledTemporaryFile(max_size=CHUNK) as stream:
                    for text in json.JSONEncoder(
                        ensure_ascii=False, sort_keys=True, allow_nan=False, separators=(',', ':')
                    ).iterencode(value):
                        stream.write(text.encode())
                    if stream.tell() > MAX_JSON:
                        raise ValueError('Campo JSON oltre 80 MB.')
                    stream.seek(0)
                    description = objects.publish(stream)
                detached.append({'path': path, 'blob': description})
                return None
            return [walk(v, path + [i]) for i, v in enumerate(value)]
        if isinstance(value, dict):
            return {k: walk(v, path + [k]) for k, v in value.items()}
        return value

    template = walk(change, [])
    blobs = {}
    for digest in change['record'].get('objects', []):
        path = objects.store.root / 'objects' / digest
        # Validate the local hash, including on deduplication/retry.
        if len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest) or path.is_symlink():
            raise ValueError('Allegato non valido.')
        if digest in objects.published_blobs:
            blobs[digest] = objects.published_blobs[digest]
            continue
        with path.open('rb') as stream:
            if hashlib.file_digest(stream, 'sha256').hexdigest() != digest:
                raise ValueError('Allegato locale corrotto.')
            stream.seek(0)
            blobs[digest] = objects.publish(stream)
            objects.published_blobs[digest] = blobs[digest]
    return {'change': template, 'detached': detached, 'objects': blobs}


def unpack(item, objects):
    event = item['change']
    for field in item['detached']:
        desc = field['blob']
        if desc['size'] > MAX_JSON:
            raise ValueError('Campo JSON troppo grande.')
        value = json.loads(objects.fetch(desc).read_bytes())
        node = event
        path = field['path']
        if not path or path[0] != 'record':
            raise ValueError('Campo separato non consentito.')
        for key in path[:-1]:
            node = node[key]
        if node[path[-1]] is not None:
            raise ValueError('Campo separato duplicato.')
        node[path[-1]] = value
    return event


def fetch_attachments(item, event, objects):
    for digest in event['record'].get('objects', []):
        desc = item['objects'][digest]
        if desc['sha256'] != digest:
            raise ValueError('Riferimento allegato errato.')
        objects.fetch(desc)


def exchange_v2(store, folder, key, transport, verify_all, result):
    from .transports import FolderTransport
    from .sync import apply_candidates
    from .society_scope import check_archive, check_record
    from .workspaces import write_json, sign, verify

    channel = hashlib.sha256(key.encode()).hexdigest()[:24]
    transport = transport or FolderTransport(folder, channel, store.root)
    names = set(transport.list())
    objects = Objects(store, key, transport, names, verify_all)
    managed = hasattr(store, 'identity')
    org = check_archive(store)
    identity = store.identity if managed else None
    can_write = (
        not managed
        or identity['certificate']['role'] == 'admin'
        and identity['certificate']['id'] not in store.revocations()
    )
    pages = []
    published = 0
    # Controls were settled by the v1 step: read identity and revocations once (RT-09).
    check = store.verifier() if managed else None
    if can_write:
        # Stable rowid pages include complete signed history, not just live heads.
        with store.connect() as db:
            cursor = db.execute('SELECT body FROM changes ORDER BY rowid')
            while rows := cursor.fetchmany(PAGE):
                events = []
                for row in rows:
                    change = json.loads(row[0])
                    if managed:
                        try:
                            check(change)
                        except (ValueError, KeyError, InvalidSignature):
                            continue
                    events.append(change)
                if not events:
                    continue
                # Cache the descriptor locally, preserving exact signed events.
                cache = store.root / 'sync-v2'
                cache.mkdir(exist_ok=True)
                source = hmac.new(objects.key, digestmod=hashlib.sha256)
                for fragment in json.JSONEncoder(
                    ensure_ascii=False, sort_keys=True, allow_nan=False, separators=(',', ':')
                ).iterencode(events):
                    source.update(fragment.encode())
                cache_id = source.hexdigest()
                cached = cache / (cache_id + '.json')
                if cached.exists():
                    payload = json.loads(cached.read_text(encoding='utf-8'))
                    # Ensure absent remote chunks are republished after switching destination.
                    required = {
                        n
                        for e in payload['events']
                        for d in [*e['objects'].values(), *(f['blob'] for f in e['detached'])]
                        for n in d['chunks']
                    }
                    if not required.issubset(names) or verify_all:
                        payload = None
                else:
                    payload = None
                if payload is None:
                    payload = {'schema': 2, 'events': [pack(e, objects) for e in events]}
                    write_json(cached, payload)
                if managed:
                    payload = {
                        **payload,
                        'workspace': identity['workspace'],
                        'publisher': identity['certificate'],
                        'publisher_certificate_signature': identity['certificate_signature'],
                    }
                    payload = {**payload, 'signature': sign(identity['private_key'], payload)}
                raw = encoded(payload).encode()
                name = 'page2-' + objects.address(raw) + '.ctsync2'
                before = objects.uploaded
                objects.immutable(name, raw)
                published += objects.uploaded - before
                pages.append(name)
        # Complete bootstrap catalogue. No authority is inferred from a catalogue:
        # receivers authenticate every original event in every selected page.
        checkpoint = encoded({'schema': 2, 'pages': pages, 'complete_history': True}).encode()
        objects.immutable('checkpoint2-' + objects.address(checkpoint) + '.ctindex', checkpoint)
    receipts_path = store.root / 'sync-v2-receipts.json'
    receipts = json.loads(receipts_path.read_text(encoding='utf-8')) if receipts_path.exists() else {}
    known = set(receipts.get(channel, []))
    received = downloaded = skipped = 0
    errors = []
    pending = sorted(n for n in names if n.endswith('.ctsync2'))
    deferred = []
    if not known:
        # Bootstrap catalogues prioritize complete histories in original page
        # order. The full inventory remains a fallback for missing/stale indices.
        priority = []
        # An index is only an ordering hint: an unreadable one is reported and the
        # complete inventory below still delivers every page.
        for index in sorted(n for n in names if n.endswith('.ctindex')):
            try:
                raw = objects.cipher.decrypt(transport.get(index))
                if index != 'checkpoint2-' + objects.address(raw) + '.ctindex':
                    raise ValueError('Indice v2 alterato.')
                catalogue = json.loads(raw)
                if (
                    not isinstance(catalogue, dict)
                    or catalogue.get('schema') != 2
                    or not isinstance(catalogue.get('pages'), list)
                ):
                    raise ValueError('Indice v2 non valido.')
                priority.extend(
                    n for n in catalogue['pages'] if isinstance(n, str) and n in names and n.endswith('.ctsync2')
                )
            except (ValueError, TypeError, OSError, InvalidToken, RecursionError) as exc:
                errors.append(f'{index}: indice v2 ignorato, usato l’inventario completo ({type(exc).__name__})')
        pending = list(dict.fromkeys(priority + pending))
    while pending:
        progress = False
        deferred = []
        for name in pending:
            if name in known and not verify_all:
                skipped += 1
                continue
            try:
                raw = objects.cipher.decrypt(transport.get(name))
                downloaded += 1
                if name != 'page2-' + objects.address(raw) + '.ctsync2':
                    raise ValueError('Pagina v2 alterata.')
                payload = json.loads(raw)
                if payload['schema'] != 2 or not 1 <= len(payload['events']) <= PAGE:
                    raise ValueError('Pagina v2 non valida.')
                if managed:
                    publisher = payload['publisher']
                    verify(identity['authority_public'], publisher, payload['publisher_certificate_signature'])
                    if (
                        publisher['workspace'] != identity['workspace']
                        or payload['workspace'] != identity['workspace']
                        or publisher['role'] != 'admin'
                    ):
                        raise ValueError('Editore v2 non autorizzato.')
                    verify(
                        publisher['public_key'],
                        {k: v for k, v in payload.items() if k != 'signature'},
                        payload['signature'],
                    )
                candidates = []
                page_ids = set()
                for item in payload['events']:
                    event = unpack(item, objects)
                    r = event['record']
                    if event['schema'] != 1 or r['kind'] not in KINDS or event['id'] != r['revision']:
                        raise ValueError('Revisione v2 incoerente.')
                    if event['id'] in page_ids:
                        raise ValueError('Revisione duplicata nella pagina.')
                    page_ids.add(event['id'])
                    check_record(r, org)
                    if managed:
                        check(event)
                    fetch_attachments(item, event, objects)
                    with store.connect() as db:
                        old = db.execute('SELECT body FROM changes WHERE id=?', (event['id'],)).fetchone()
                    if old:
                        if old[0] != encoded(event):
                            raise ValueError('Revisione duplicata divergente.')
                    else:
                        candidates.append(event)
                    if not org:
                        org = r['id'] if r['kind'] == 'organization' else r.get('organization_id')
                count, waiting, _ = apply_candidates(store, candidates)
                received += count
                progress |= bool(count)
                if waiting:
                    deferred.append(name)
                else:
                    known.add(name)
            except (
                ValueError,
                KeyError,
                TypeError,
                IndexError,
                OSError,
                InvalidToken,
                InvalidSignature,
                RecursionError,
            ) as exc:
                known.discard(name)
                errors.append(f'{name}: pagina v2 incompleta o non valida ({type(exc).__name__})')
        if not deferred or not progress:
            break
        pending = deferred
    receipts[channel] = sorted(known)
    write_json(receipts_path, receipts)
    with store.connect() as db:
        conflicts = db.execute('SELECT count(*) FROM conflicts').fetchone()[0]
    result.update(
        protocol=2,
        published=result['published'] + published,
        written_to_folder=result['written_to_folder'] + published,
        received=result['received'] + received,
        pending=result['pending'] + len(deferred),
        conflicts=conflicts,
        errors=result['errors'] + errors,
        downloaded_packets=result['downloaded_packets'] + downloaded,
        known_packets_skipped=result['known_packets_skipped'] + skipped,
        uploaded_objects=objects.uploaded - published,
        downloaded_chunks=objects.downloaded,
        bootstrap_pages=len(pages),
        status='Scambio v2: blocchi cifrati riutilizzabili e revisioni originali verificate. Nessun dato v1 eliminato.',
    )
    return result
