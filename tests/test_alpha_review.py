import io
import struct
import zipfile

import pytest
from fastapi.testclient import TestClient

from cycling_test.api import create_app
from cycling_test.backup_stream import inspect_file
from cycling_test.recovery import inspect_backup


@pytest.mark.parametrize('encrypted', [False, True])
@pytest.mark.parametrize('member', [0, 1])
def test_unreadable_zip_is_validation_error_without_staging(tmp_path, encrypted, member):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w') as archive:
        archive.writestr('manifest.json', '{"schema":3}')
        archive.writestr('archive.sqlite', b'not reached')
    raw = bytearray(stream.getvalue())
    # Valid ZIP directory, but an encrypted member or unsupported codec.
    local = raw.index(b'PK\x03\x04')
    central = raw.index(b'PK\x01\x02')
    if member:
        local = raw.index(b'PK\x03\x04', local + 4)
        central = raw.index(b'PK\x01\x02', central + 4)
    for offset in (local + (6 if encrypted else 8), central + (8 if encrypted else 10)):
        struct.pack_into('<H', raw, offset, 1 if encrypted else 99)
    with pytest.raises(ValueError, match='Backup'):
        inspect_backup(bytes(raw))
    path = tmp_path / 'bad.zip'
    path.write_bytes(raw)
    with pytest.raises(ValueError, match='Backup'):
        with inspect_file(path):
            pytest.fail('Invalid archive accepted')
    root = tmp_path / 'app'
    client = TestClient(create_app(root, token='test'))
    response = client.post(
        '/api/v1/workspaces/restore/preview',
        headers={'X-Fuorigiri-Token': 'test'},
        files={'file': ('bad.zip', bytes(raw))},
    )
    assert response.status_code == 422
    assert list((root / 'restore-staging').iterdir()) == []
    assert client.get('/api/v1/workspaces', headers={'X-Fuorigiri-Token': 'test'}).json() == []
