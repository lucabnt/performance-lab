import struct

import pytest
from fastapi.testclient import TestClient

from cycling_test import backup_crypto
from cycling_test.api import create_app
from cycling_test.backup_crypto import CHUNK, MAGIC, WrongPassword, decrypt_file, encrypt_file, is_encrypted
from cycling_test.store import Store
from cycling_test.workspaces import Workspaces

PASSWORD = 'synthetic-pass-123'
FAST = 2**14  # minimum accepted cost: keeps unit tests quick


def roundtrip(tmp_path, payload):
    source = tmp_path / 'plain.bin'
    source.write_bytes(payload)
    sealed = encrypt_file(source, tmp_path / 'sealed.fgbak', PASSWORD, n=FAST)
    assert is_encrypted(sealed)
    assert len(payload) < 64 or payload[:64] not in sealed.read_bytes()
    out = decrypt_file(sealed, tmp_path / 'out.bin', PASSWORD)
    return out.read_bytes()


@pytest.mark.parametrize('size', [0, 1, CHUNK - 1, CHUNK, CHUNK + 1, 2 * CHUNK])
def test_roundtrip_at_chunk_boundaries(tmp_path, size):
    payload = bytes(i % 251 for i in range(size))
    assert roundtrip(tmp_path, payload) == payload


def chunks(path):
    raw = path.read_bytes()
    (length,) = struct.unpack('>I', raw[8:12])
    head, rest, parts = raw[: 12 + length], raw[12 + length :], []
    while rest:
        (size,) = struct.unpack('>I', rest[:4])
        parts.append(rest[: 4 + size])
        rest = rest[4 + size :]
    return head, parts


@pytest.fixture
def sealed(tmp_path):
    source = tmp_path / 'plain.bin'
    source.write_bytes(b'x' * (2 * CHUNK + 10))
    return encrypt_file(source, tmp_path / 'sealed.fgbak', PASSWORD, n=FAST)


def test_wrong_or_missing_password_leaves_no_output(tmp_path, sealed):
    for password in ('', 'another-password-1'):
        with pytest.raises(WrongPassword):
            decrypt_file(sealed, tmp_path / 'out.bin', password)
        assert not (tmp_path / 'out.bin').exists()


@pytest.mark.parametrize('damage', ['drop-last', 'reorder', 'flip-byte', 'cut-mid-chunk', 'append-chunk'])
def test_truncated_reordered_or_altered_files_are_rejected(tmp_path, sealed, damage):
    head, parts = chunks(sealed)
    assert len(parts) == 3
    if damage == 'drop-last':
        body = parts[:-1]
    elif damage == 'reorder':
        body = [parts[1], parts[0], parts[2]]
    elif damage == 'flip-byte':
        middle = bytearray(parts[1])
        middle[100] ^= 1
        body = [parts[0], bytes(middle), parts[2]]
    elif damage == 'cut-mid-chunk':
        body = parts[:2] + [parts[2][:-5]]
    else:
        body = parts + [parts[2]]
    bad = tmp_path / 'bad.fgbak'
    bad.write_bytes(head + b''.join(body))
    with pytest.raises(ValueError):
        decrypt_file(bad, tmp_path / 'out.bin', PASSWORD)
    assert not (tmp_path / 'out.bin').exists()


def test_header_is_authenticated_and_cost_is_bounded(tmp_path, sealed):
    raw = sealed.read_bytes()
    lowered = raw.replace(b'"chunk_size":1048576', b'"chunk_size":1048577')
    (tmp_path / 'chunk.fgbak').write_bytes(lowered)
    with pytest.raises(ValueError):
        decrypt_file(tmp_path / 'chunk.fgbak', tmp_path / 'a.bin', PASSWORD)
    huge = raw.replace(b'"n":16384', b'"n":4194304')
    (tmp_path / 'huge.fgbak').write_bytes(huge)
    with pytest.raises(ValueError, match='Intestazione'):
        decrypt_file(tmp_path / 'huge.fgbak', tmp_path / 'b.bin', PASSWORD)
    assert raw.startswith(MAGIC)


def test_existing_destinations_are_never_replaced(tmp_path, sealed):
    keep = tmp_path / 'keep.bin'
    keep.write_bytes(b'precious')
    with pytest.raises(ValueError, match='esiste già'):
        decrypt_file(sealed, keep, PASSWORD)
    with pytest.raises(ValueError, match='esiste già'):
        encrypt_file(keep, keep, PASSWORD, n=FAST)
    assert keep.read_bytes() == b'precious'


def test_failed_encryption_removes_only_the_file_it_created(tmp_path, monkeypatch):
    keep = tmp_path / 'keep.fgbak'
    keep.write_bytes(b'precious')
    with pytest.raises(FileNotFoundError):
        encrypt_file(tmp_path / 'missing.zip', keep, PASSWORD, n=FAST)
    assert keep.read_bytes() == b'precious', 'missing source must not delete an existing destination'
    source = tmp_path / 'plain.bin'
    source.write_bytes(b'x' * (CHUNK + 1))
    created = tmp_path / 'created.fgbak'

    class Broken:
        def __init__(self, key):
            pass

        def encrypt(self, *args):
            raise OSError('disk full')

    monkeypatch.setattr(backup_crypto, 'AESGCM', Broken)
    with pytest.raises(OSError):
        encrypt_file(source, created, PASSWORD, n=FAST)
    assert not created.exists(), 'a partial file created by the call is removed'


def test_short_password_is_refused(tmp_path):
    (tmp_path / 'p').write_bytes(b'data')
    with pytest.raises(ValueError, match='12 caratteri'):
        encrypt_file(tmp_path / 'p', tmp_path / 'q', 'short', n=FAST)


def club(root):
    manager = Workspaces(root, Store(root))
    entry = manager.create('Club', 'Owner')
    store = manager.get(entry['id'])
    h = store.object(b'synthetic attachment\n' * 70000)
    athlete = store.save(
        'athlete', {'organization_id': entry['organization_id'], 'name': 'Demo', 'surname': 'Athlete', 'objects': [h]}
    )
    return entry, store, athlete


def test_encrypted_backup_real_restore_and_plain_v3_still_supported(tmp_path, monkeypatch):
    monkeypatch.setattr(backup_crypto, 'SCRYPT_N', FAST)
    monkeypatch.setattr(backup_crypto.encrypt_file, '__kwdefaults__', {'n': FAST})
    entry, source, athlete = club(tmp_path / 'source')
    headers = {'X-Fuorigiri-Token': 't', 'X-Fuorigiri-Workspace': entry['id']}
    with TestClient(create_app(tmp_path / 'source', 't'), headers=headers) as client:
        assert client.post('/api/v1/backup/scalable/encrypted', json={'password': 'short'}).status_code == 422
        sealed = client.post('/api/v1/backup/scalable/encrypted', json={'password': PASSWORD})
        assert sealed.status_code == 200, sealed.text
        assert sealed.content.startswith(MAGIC) and b'Athlete' not in sealed.content
        assert 'fuorigiri-backup-v3.fgbak' in sealed.headers['content-disposition']
        wrong_suffix = client.post(
            '/api/v1/backup/scalable/save', json={'path': str(tmp_path / 'saved.zip'), 'password': PASSWORD}
        )
        assert wrong_suffix.status_code == 422 and '.fgbak' in wrong_suffix.text
        saved = client.post(
            '/api/v1/backup/scalable/save', json={'path': str(tmp_path / 'saved.fgbak'), 'password': PASSWORD}
        )
        assert saved.status_code == 200 and saved.json()['encrypted'], saved.text
        assert is_encrypted(tmp_path / 'saved.fgbak')
        assert not [p for p in tmp_path.iterdir() if p.name.startswith('.fuorigiri-backup-')]
        plain = client.get('/api/v1/backup/scalable')
        assert plain.status_code == 200 and plain.content.startswith(b'PK')
    with TestClient(create_app(tmp_path / 'target', 't'), headers={'X-Fuorigiri-Token': 't'}) as client:
        upload = {'file': ('backup.fgbak', sealed.content)}
        missing = client.post('/api/v1/workspaces/restore/preview', files=upload)
        assert missing.status_code == 422 and 'password' in missing.text
        wrong = client.post('/api/v1/workspaces/restore/preview', files=upload, data={'backup_password': 'x' * 12})
        assert wrong.status_code == 422 and 'Password errata' in wrong.text
        staging = tmp_path / 'target' / 'restore-staging'
        assert not list(staging.iterdir())
        preview = client.post('/api/v1/workspaces/restore/preview', files=upload, data={'backup_password': PASSWORD})
        assert preview.status_code == 200, preview.text
        assert preview.json()['encrypted'] and preview.json()['schema'] == 3
        assert [p.name for p in staging.iterdir()] == [preview.json()['backup_hash']]
        restored = client.post(
            '/api/v1/workspaces/restore',
            data={'backup_hash': preview.json()['backup_hash'], 'mode': 'independent', 'operator': 'New owner'},
        )
        assert restored.status_code == 200, restored.text
        copy = Workspaces(tmp_path / 'target', Store(tmp_path / 'target')).get(restored.json()['id'])
        assert copy.history(athlete['id']) == source.history(athlete['id'])
        assert copy.read_object(athlete['objects'][0]) == source.read_object(athlete['objects'][0])
        legacy = client.post('/api/v1/workspaces/restore/preview', files={'file': ('backup.zip', plain.content)})
        assert legacy.status_code == 200 and legacy.json()['encrypted'] is False
