import copy
import importlib.util
import json
from pathlib import Path
from uuid import uuid4

import pytest
from cryptography.fernet import Fernet
from cycling_test.store import Store, encoded
from cycling_test.workspaces import Workspaces, invitation, join, sign
from cycling_test.recovery import backup_bytes, restore
from cycling_test.sync import exchange
from cycling_test.sync_service import configure, configuration, run_sync
from cycling_test.transports import FolderTransport


def test_clubs_in_same_cloud_parent_have_independent_keys_data_and_connections(tmp_path):
    manager = Workspaces(tmp_path / 'owner', Store(tmp_path / 'owner'))
    a, b = manager.create('Club A', 'Owner A'), manager.create('Club B', 'Owner B')
    left, right = manager.get(a['id']), manager.get(b['id'])
    assert left.identity['sync_key'] != right.identity['sync_key']
    left.save('athlete', {'organization_id': a['organization_id'], 'name': 'Only A'})
    right.save('athlete', {'organization_id': b['organization_id'], 'name': 'Only B'})
    root = tmp_path / 'cloud'
    root.mkdir()
    configure(left, {'transport': 'folder', 'folder': str(root)})
    assert configuration(right)['folder'] == ''
    configure(right, {'transport': 'folder', 'folder': str(root)})
    recipient = Workspaces(tmp_path / 'reader', Store(tmp_path / 'reader'))
    joined = join(recipient, invitation(left, 'Coach A', 'admin', 'test-password-123'), 'test-password-123')
    reader = recipient.get(joined['id'])
    run_sync(left)
    run_sync(right)
    exchange(reader, root, reader.identity['sync_key'])
    assert [r['name'] for r in reader.list('organization')] == ['Club A']
    assert [r['name'] for r in reader.list('athlete')] == ['Only A']
    assert len([p for p in root.iterdir() if p.is_dir()]) == 2


def test_multi_society_legacy_and_restored_archives_cannot_be_shared(tmp_path):
    source = Store(tmp_path / 'legacy')
    source.save('organization', {'name': 'Club A'})
    source.save('organization', {'name': 'Club B'})

    class NoTransport:
        def list(self):
            raise AssertionError('No network operation allowed')

    with pytest.raises(ValueError, match='più società'):
        exchange(source, None, Fernet.generate_key().decode(), NoTransport())
    manager = Workspaces(tmp_path / 'restored', Store(tmp_path / 'restored'))
    entry = restore(manager, backup_bytes(source), 'independent', operator='New owner')
    restored = manager.get(entry['id'])
    assert len(restored.list('organization')) == 2  # preserved for local consultation
    with pytest.raises(ValueError, match='più società'):
        invitation(restored, 'Reader', 'viewer', 'test-password-123')
    with pytest.raises(ValueError, match='più società'):
        configure(restored, {'transport': 'folder', 'folder': str(tmp_path)})


def test_foreign_signed_society_is_rejected_by_recipient(tmp_path):
    manager = Workspaces(tmp_path / 'owner', Store(tmp_path / 'owner'))
    entry = manager.create('Club A', 'Owner')
    owner = manager.get(entry['id'])
    key = owner.identity['sync_key']
    recipient = Workspaces(tmp_path / 'recipient', Store(tmp_path / 'recipient'))
    joined = join(recipient, invitation(owner, 'Reader', 'viewer', 'test-password-123'), 'test-password-123')
    reader = recipient.get(joined['id'])
    folder = tmp_path / 'cloud'
    folder.mkdir()
    exchange(owner, folder, key)
    with owner.connect() as db:
        event = json.loads(db.execute('SELECT body FROM changes LIMIT 1').fetchone()[0])
    event = copy.deepcopy(event)
    event['id'] = str(uuid4())
    event['record'].update(id=str(uuid4()), revision=event['id'], name='Foreign club')
    event.pop('signature')
    event['signature'] = sign(owner.identity['private_key'], event)
    transport = FolderTransport(folder, __import__('hashlib').sha256(key.encode()).hexdigest()[:24], owner.root)
    transport.put(
        event['id'] + '.ctsync', Fernet(key.encode()).encrypt(encoded({'change': event, 'objects': {}}).encode())
    )
    result = exchange(reader, folder, key)
    assert result['errors']
    assert [r['name'] for r in reader.list('organization')] == ['Club A']


def test_normal_sync_skips_known_packets_and_full_verification_rereads(tmp_path):
    owner, reader = Store(tmp_path / 'a'), Store(tmp_path / 'b')
    folder = tmp_path / 'cloud'
    folder.mkdir()
    key = Fernet.generate_key().decode()
    org = owner.save('organization', {'name': 'Club'})
    exchange(owner, folder, key)
    exchange(reader, folder, key)

    class CountReads(FolderTransport):
        def __init__(self):
            super().__init__(folder, __import__('hashlib').sha256(key.encode()).hexdigest()[:24], reader.root)
            self.reads = []

        def get(self, name):
            self.reads.append(name)
            return super().get(name)

    transport = CountReads()
    result = exchange(reader, None, key, transport, verify_existing=False)
    assert result['downloaded_packets'] == 0 and result['known_packets_skipped'] == 1
    assert not transport.reads
    result = exchange(reader, None, key, transport, verify_existing=True)
    assert result['downloaded_packets'] == 1 and result['known_packets_skipped'] == 0
    packet = next(transport.root.glob('*.ctsync'))
    packet.write_bytes(b'corrupted remotely')
    assert exchange(reader, None, key, transport, verify_existing=True)['errors']
    assert reader.get(org['id'])['name'] == 'Club'


def test_size_estimate_matches_actual_packets_without_reading_keys(tmp_path):
    spec = importlib.util.spec_from_file_location(
        'measure_size', Path(__file__).resolve().parents[1] / 'scripts/measure_archive_size.py'
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    store = Store(tmp_path / 'archive')
    org = store.save('organization', {'name': 'Club'})
    obj = store.object(b'synthetic bytes' * 100)
    store.save('athlete', {'organization_id': org['id'], 'name': 'Demo', 'objects': [obj, obj]})
    folder = tmp_path / 'cloud'
    folder.mkdir()
    exchange(store, folder, Fernet.generate_key().decode())
    actual = sum(p.stat().st_size for p in folder.rglob('*.ctsync'))
    size = module.measure(store.root)
    assert size['v1_sync_estimated_bytes'] == actual
    assert size['missing_object_count'] == 0


def test_backup_never_exports_a_zip_over_its_restore_limit(tmp_path, monkeypatch):
    from cycling_test import recovery

    store = Store(tmp_path / 'archive')
    store.save('organization', {'name': 'Club'})
    monkeypatch.setattr(recovery, 'MAX_UPLOAD', 10)
    with pytest.raises(ValueError, match='ripristinabile'):
        recovery.backup_bytes(store)
    assert len(store.list('organization')) == 1
