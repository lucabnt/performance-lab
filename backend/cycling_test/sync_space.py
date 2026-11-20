"""Read-only analysis of the space used by an exchange channel (SYNC-SPAZIO-01, phase 0).

The job lists, downloads and decrypts the channel files with the society key to
explain what occupies remote space. It never writes to the destination, never
applies events and never changes local history: it is a diagnosis, not a sync.
Page names are checked against their keyed address; signatures are not verified
because nothing is accepted from the analysed files.
"""

import json
from cryptography.fernet import InvalidToken
from cycling_suite.jobs import JobRegistry, ObservedTransport
from .access import viewer_allowed
from .store import encoded
from .sync_v2 import CHUNK, PAGE, Objects

_registry = JobRegistry(
    product='Fuorigiri-space',
    failed='Analisi dello spazio non completata. Controllare connessione e autorizzazioni; nessun dato è stato modificato.',
    interrupted='Analisi interrotta dalla chiusura del processo. Riprovare: nessun dato è stato modificato.',
    status_file='sync-space-job.json',
)


def token_size(plain):
    """Exact Fernet token length for ``plain`` plaintext bytes."""
    payload = 1 + 8 + 16 + 16 * (plain // 16 + 1) + 32
    return 4 * -(-payload // 3)


def category(name):
    if name.endswith('.ctsync'):
        return 'v1_events'
    if name.endswith('.ctsync2'):
        return 'v2_pages'
    if name.endswith('.ctindex'):
        return 'v2_catalogues'
    if name.endswith('.ctobj'):
        return 'v2_chunks'
    return 'controls'


def analyze(store, transport):
    key = store.identity['sync_key']
    objects = Objects(store, key, transport, set())
    cipher = objects.cipher
    names = transport.list()
    totals = {c: {'files': 0, 'bytes': 0} for c in ('v1_events', 'v2_pages', 'v2_catalogues', 'v2_chunks', 'controls')}
    unreadable = 0
    v1_kinds = {}
    v1_attachments = 0
    v1_ids = {}
    publishers = {}
    distinct = {}
    copies = 0
    headers = []
    referenced = {}
    catalogue_sizes = []
    chunk_names = [n for n in names if category(n) == 'v2_chunks']
    for name in names:
        kind = category(name)
        if kind == 'v2_chunks':
            continue  # Sized from the page descriptors; unreferenced ones are read below.
        try:
            raw = transport.get(name)
        except (ValueError, OSError):
            unreadable += 1
            continue
        totals[kind]['files'] += 1
        totals[kind]['bytes'] += len(raw)
        if kind == 'controls':
            continue
        try:
            plain = cipher.decrypt(raw)
            if kind == 'v1_events':
                packet = json.loads(plain)
                record = packet['change']['record']
                row = v1_kinds.setdefault(str(record.get('kind', '?')), {'files': 0, 'bytes': 0})
                row['files'] += 1
                row['bytes'] += len(raw)
                v1_attachments += sum(len(v) for v in packet.get('objects', {}).values())
                v1_ids[packet['change']['id']] = len(raw)
            elif kind == 'v2_catalogues':
                if name != 'checkpoint2-' + objects.address(plain) + '.ctindex':
                    raise ValueError('Indice alterato.')
                catalogue_sizes.append(len(raw))
            else:
                if name != 'page2-' + objects.address(plain) + '.ctsync2':
                    raise ValueError('Pagina alterata.')
                payload = json.loads(plain)
                events = payload['events']
                publisher = payload.get('publisher') or {}
                label = publisher.get('name') or publisher.get('id') or '—'
                row = publishers.setdefault(
                    publisher.get('id', '—'), {'name': label, 'pages': 0, 'events': 0, 'bytes': 0}
                )
                row['pages'] += 1
                row['events'] += len(events)
                row['bytes'] += len(raw)
                headers.append(len(encoded({k: v for k, v in payload.items() if k != 'events'})))
                for item in events:
                    copies += 1
                    distinct.setdefault(item['change']['id'], len(encoded(item)) + 1)
                    for desc in [*item.get('objects', {}).values(), *(f['blob'] for f in item.get('detached', []))]:
                        for i, chunk in enumerate(desc['chunks']):
                            referenced[chunk] = min(CHUNK, desc['size'] - i * CHUNK)
        except (ValueError, KeyError, TypeError, AttributeError, InvalidToken, RecursionError):
            unreadable += 1
    present = set(chunk_names)
    orphan_bytes = 0
    orphans = 0
    for name in chunk_names:
        if name in referenced:
            totals['v2_chunks']['files'] += 1
            totals['v2_chunks']['bytes'] += token_size(referenced[name])
            continue
        try:
            size = len(transport.get(name))
        except (ValueError, OSError):
            unreadable += 1
            continue
        totals['v2_chunks']['files'] += 1
        totals['v2_chunks']['bytes'] += size
        orphans += 1
        orphan_bytes += size
    missing_chunks = sum(1 for n in referenced if n not in present)
    # One consolidated copy of each distinct event in full pages of 32.
    pages_needed = -(-len(distinct) // PAGE)
    header = max(headers) if headers else 0
    consolidated = sum(
        token_size(sum(sizes) + header + 32)
        for sizes in (list(distinct.values())[i : i + PAGE] for i in range(0, len(distinct), PAGE))
    )
    redundant_pages = max(0, totals['v2_pages']['bytes'] - consolidated) if distinct else 0
    redundant_catalogues = sum(catalogue_sizes) - max(catalogue_sizes) if catalogue_sizes else 0
    v1_covered = [size for id, size in v1_ids.items() if id in distinct]
    total_files = sum(t['files'] for t in totals.values())
    total_bytes = sum(t['bytes'] for t in totals.values())
    return {
        'protocol': store.identity.get('sync_protocol', 1),
        'format2_notice': 'format2.json' in names,
        'files': total_files,
        'bytes': total_bytes,
        'categories': totals,
        'unreadable': unreadable,
        'v1': {
            'events': len(v1_ids),
            'by_kind': dict(sorted(v1_kinds.items(), key=lambda item: -item[1]['bytes'])),
            'attachment_base64_bytes': v1_attachments,
            'covered_by_v2': {'files': len(v1_covered), 'bytes': sum(v1_covered)},
        },
        'v2': {
            'publishers': sorted(publishers.values(), key=lambda row: -row['bytes']),
            'distinct_events': len(distinct),
            'event_copies': copies,
            'consolidated_pages': pages_needed,
            'consolidated_bytes': consolidated,
            'redundant_page_bytes': redundant_pages,
            'redundant_catalogue_bytes': redundant_catalogues,
            'unreferenced_chunks': {'files': orphans, 'bytes': orphan_bytes},
            'missing_chunks': missing_chunks,
        },
        'reclaimable_bytes': redundant_pages + redundant_catalogues + orphan_bytes,
        'note': 'Sola lettura: nessun file remoto o dato locale modificato. Le firme non sono verificate.',
    }


def run(store, progress=None):
    from .sync_service import configuration, require_managed, transport

    require_managed(store)
    connection = transport(store, configuration(store))
    if progress:
        connection = ObservedTransport(connection, progress)
    return analyze(store, connection)


def status(store):
    return _registry.status(store.root)


def start(store):
    from .sync_service import require_managed

    require_managed(store)
    return _registry.start(store.root, lambda progress: run(store, progress))


def wait(store, timeout=540):
    return _registry.wait(store.root, timeout)


def install(app, store):
    @app.get('/api/v1/sync/space/job')
    def space_job():
        selected = store.selected.get()
        from .sync_service import require_managed

        require_managed(selected)
        return status(selected)

    @app.post('/api/v1/sync/space/start')
    @viewer_allowed
    def space_start():
        return start(store.selected.get())
