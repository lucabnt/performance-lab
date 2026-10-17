import hashlib
import pytest
from cryptography.fernet import Fernet
from cycling_test.compatibility import LEGACY_BRAND_PARTS, default_data_root, channel_directory
from cycling_test.store import Store
from cycling_test.sync import exchange


def test_default_root_preserves_absolute_registry_paths(tmp_path):
    assert default_data_root(tmp_path) == tmp_path/'Fuorigiri'
    previous=tmp_path/''.join(LEGACY_BRAND_PARTS)
    previous.mkdir()
    marker=previous/'workspaces.json';marker.write_text('[]')
    assert default_data_root(tmp_path)==previous
    assert marker.read_text()=='[]'
    (tmp_path/'Fuorigiri').mkdir()
    assert default_data_root(tmp_path)==tmp_path/'Fuorigiri'


def test_existing_encrypted_channel_is_reused_without_lost_events(tmp_path):
    folder=tmp_path/'cloud';folder.mkdir()
    key=Fernet.generate_key().decode();channel=hashlib.sha256(key.encode()).hexdigest()[:24]
    previous=folder/('-'.join(p.lower() for p in LEGACY_BRAND_PARTS)+'-'+channel)
    previous.mkdir()
    a,b=Store(tmp_path/'a'),Store(tmp_path/'b')
    saved=a.save('organization',{'name':'Club'})
    exchange(a,folder,key);exchange(b,folder,key)
    assert b.get(saved['id'])['name']=='Club'
    assert list(folder.iterdir())==[previous]
    (folder/('fuorigiri-'+channel)).mkdir()
    with pytest.raises(ValueError,match='Due cartelle'):channel_directory(folder,channel)
