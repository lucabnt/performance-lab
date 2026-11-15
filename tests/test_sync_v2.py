import json
from pathlib import Path
import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from cycling_test.store import Store,encoded
from cycling_test.workspaces import Workspaces,invitation,join,revoke_member,write_json
from cycling_test.sync import exchange
from cycling_test.sync_service import configure,run_sync
from cycling_test.transports import FolderTransport
from cycling_test.api import create_app

PASSWORD='test-only-password-123'


def devices(tmp_path,role='admin'):
    root=tmp_path/'owner';manager=Workspaces(root,Store(root));entry=manager.create('Club','Founder');owner=manager.get(entry['id'])
    other_root=tmp_path/'other';other=Workspaces(other_root,Store(other_root))
    join(other,invitation(owner,'Reader',role,PASSWORD),PASSWORD);replica=other.get(entry['id'])
    folder=tmp_path/'exchange';folder.mkdir()
    return owner,replica,folder


def trace_test(owner):
    org=owner.list('organization')[0]['id']
    samples=[{'t':i,'power':200+i%10,'hr':120,'cadence':90} for i in range(2000)]
    h=owner.object(encoded({'samples':samples}).encode())
    return owner.save('test',{'organization_id':org,'samples':samples,'objects':[h],'notes':'first'})


def test_v2_deduplicates_and_preserves_original_signatures_and_history(tmp_path):
    owner,replica,folder=devices(tmp_path,'viewer');test=trace_test(owner);key=owner.identity['sync_key']
    first=exchange(owner,folder,key,protocol=2,verify_existing=False)
    channel=next(folder.iterdir());chunks={p.name:p.read_bytes() for p in channel.glob('*.ctobj')}
    assert chunks and first['errors']==[]
    corrected=owner.save('test',{**test,'notes':'corrected'},test['id'],test['revision'])
    next_sync=exchange(owner,folder,key,protocol=2,verify_existing=False)
    assert {p.name:p.read_bytes() for p in channel.glob('*.ctobj')}==chunks
    # Published history pages contain no inlined sample array or base64 object.
    for path in channel.glob('*.ctsync2'):
        raw=Fernet(key.encode()).decrypt(path.read_bytes())
        assert b'"t":1999' not in raw and len(raw)<20_000
    received=exchange(replica,folder,key,protocol=2,verify_existing=False)
    assert not received['errors'] and not received['pending']
    assert replica.get(test['id'])==corrected and replica.history(test['id'])==owner.history(test['id'])
    with owner.connect() as a,replica.connect() as b:
        assert a.execute('SELECT body FROM changes ORDER BY id').fetchall()==b.execute('SELECT body FROM changes ORDER BY id').fetchall()
    again=exchange(replica,folder,key,protocol=2,verify_existing=False)
    assert again['received']==0 and again['downloaded_packets']==0


def test_v2_missing_chunk_retries_and_full_verification_detects_corruption(tmp_path):
    owner,viewer,folder=devices(tmp_path,'viewer');test=trace_test(owner);key=owner.identity['sync_key']
    exchange(owner,folder,key,protocol=2,verify_existing=False)
    channel=next(folder.iterdir());chunk=next(channel.glob('*.ctobj'));original=chunk.read_bytes();chunk.unlink()
    result=exchange(viewer,folder,key,protocol=2,verify_existing=False)
    assert result['errors']
    with pytest.raises(KeyError):viewer.get(test['id'])
    chunk.write_bytes(original)
    assert not exchange(viewer,folder,key,protocol=2,verify_existing=False)['errors']
    chunk.write_bytes(b'corrupt')
    assert exchange(viewer,folder,key,protocol=2,verify_existing=True)['errors']
    assert viewer.get(test['id'])==test


def test_v1_history_migrates_without_rewriting_or_removal(tmp_path):
    owner,viewer,folder=devices(tmp_path,'viewer');test=trace_test(owner);key=owner.identity['sync_key']
    exchange(owner,folder,key)
    legacy={p.name:p.read_bytes() for p in next(folder.iterdir()).glob('*.ctsync')}
    configure(owner,{'transport':'folder','folder':str(folder)})
    write_json(owner.root/'identity.json',{**owner.identity,'sync_protocol':2})
    assert run_sync(owner)['protocol']==2
    configure(viewer,{'transport':'folder','folder':str(folder)})
    assert run_sync(viewer)['protocol']==2
    assert viewer.get(test['id'])==test
    assert {p.name:p.read_bytes() for p in next(folder.iterdir()).glob('*.ctsync')}==legacy


def test_concurrent_v2_edits_resolve_and_revoked_events_stay_frozen(tmp_path):
    owner,other,folder=devices(tmp_path);test=trace_test(owner);key=owner.identity['sync_key']
    exchange(owner,folder,key,protocol=2);exchange(other,folder,key,protocol=2)
    left=owner.save('test',{**test,'notes':'left'},test['id'],test['revision'])
    right=other.save('test',{**test,'notes':'right'},test['id'],test['revision'])
    exchange(owner,folder,key,protocol=2);exchange(other,folder,key,protocol=2)
    assert exchange(owner,folder,key,protocol=2)['conflicts']==1
    resolved=owner.save('test',{**left,'notes':'resolved'},test['id'],left['revision'],parents=[right['revision']])
    exchange(owner,folder,key,protocol=2);exchange(other,folder,key,protocol=2)
    assert other.get(test['id'])==resolved
    revoke_member(owner,other.identity['certificate']['id'])
    # A writer unaware of revocation creates an event. Owner will reject it.
    other.save('test',{**resolved,'notes':'unauthorized'},test['id'],resolved['revision'])
    # Publish before receiving the new control to model an offline attacker.
    from cycling_test.sync_v2 import exchange_v2
    baseline={'published':0,'written_to_folder':0,'received':0,'pending':0,'errors':[],'downloaded_packets':0,'known_packets_skipped':0}
    exchange_v2(other,folder,key,None,False,baseline)
    result=exchange(owner,folder,key,protocol=2)
    assert result['errors'] and owner.get(test['id'])==resolved


def test_format_upgrade_requires_founder_and_explicit_device_acknowledgement(tmp_path):
    owner,other,folder=devices(tmp_path)
    root=owner.root.parent.parent
    with TestClient(create_app(root,'t'),headers={'X-Fuorigiri-Token':'t','X-Fuorigiri-Workspace':owner.identity['workspace']}) as c:
        assert c.post('/api/v1/sync/format-v2',json={'all_devices_updated':False}).status_code==422
        assert c.post('/api/v1/sync/format-v2',json={'all_devices_updated':True}).status_code==200
    with TestClient(create_app(other.root.parent.parent,'t'),headers={'X-Fuorigiri-Token':'t','X-Fuorigiri-Workspace':other.identity['workspace']}) as c:
        assert c.post('/api/v1/sync/format-v2',json={'all_devices_updated':True}).status_code==422


def test_interrupted_chunk_publication_resumes_without_republishing_prior_chunks(tmp_path):
    owner,viewer,folder=devices(tmp_path,'viewer');key=owner.identity['sync_key']
    import hashlib,random
    raw=random.Random(42).randbytes(2_500_000);h=owner.object(raw)
    owner.save('athlete',{'organization_id':owner.list('organization')[0]['id'],'name':'Demo','surname':'Chunk','objects':[h]})
    channel=hashlib.sha256(key.encode()).hexdigest()[:24]
    transport=FolderTransport(folder,channel,owner.root)
    original=transport.put;count=0
    def fail_second(name,data):
        nonlocal count
        if name.endswith('.ctobj'):
            count+=1
            if count==2:raise OSError('Synthetic interruption')
        return original(name,data)
    transport.put=fail_second
    with pytest.raises(OSError):exchange(owner,folder,key,transport,False,protocol=2)
    prior={p.name:p.read_bytes() for p in transport.root.glob('*.ctobj')};assert len(prior)==1
    transport.put=original
    assert not exchange(owner,folder,key,transport,False,protocol=2)['errors']
    assert all((transport.root/name).read_bytes()==body for name,body in prior.items())
    assert not exchange(viewer,folder,key,protocol=2)['errors']
    assert viewer.read_object(h)==raw


def test_reader_cannot_forge_a_page_even_with_channel_encryption_key(tmp_path):
    owner,viewer,folder=devices(tmp_path,'viewer');trace_test(owner);key=owner.identity['sync_key']
    exchange(owner,folder,key,protocol=2)
    channel=next(folder.iterdir());original=next(channel.glob('*.ctsync2'))
    cipher=Fernet(key.encode());payload=json.loads(cipher.decrypt(original.read_bytes()))
    # A reader knows the shared encryption key, but cannot sign as an admin.
    payload['events'][0]['change']['record']['notes']='forged'
    raw=encoded(payload).encode()
    import hashlib,hmac
    name='page2-'+hmac.new(key.encode(),raw,hashlib.sha256).hexdigest()+'.ctsync2'
    (channel/name).write_bytes(cipher.encrypt(raw))
    result=exchange(viewer,folder,key,protocol=2)
    assert any(name in error for error in result['errors'])
    assert all(r.get('notes')!='forged' for r in viewer.list('test'))


def test_receiver_reuses_validated_chunks_after_missing_final_chunk(tmp_path):
    owner,viewer,folder=devices(tmp_path,'viewer');key=owner.identity['sync_key']
    import hashlib,random
    raw=random.Random(99).randbytes(2_500_000);digest=owner.object(raw)
    owner.save('athlete',{'organization_id':owner.list('organization')[0]['id'],'name':'Demo','surname':'Resume','objects':[digest]})
    exchange(owner,folder,key,protocol=2)
    channel=next(folder.iterdir());page=next(channel.glob('*.ctsync2'))
    payload=json.loads(Fernet(key.encode()).decrypt(page.read_bytes()))
    chunks=next(e['objects'][digest]['chunks'] for e in payload['events'] if digest in e['objects'])
    missing=channel/chunks[-1];token=missing.read_bytes();missing.unlink()
    assert exchange(viewer,folder,key,protocol=2)['errors']
    assert len(list((viewer.root/'parts').iterdir()))==2
    missing.write_bytes(token)
    transport=FolderTransport(folder,hashlib.sha256(key.encode()).hexdigest()[:24],viewer.root)
    original=transport.get;downloaded=[]
    def counted(name):downloaded.append(name);return original(name)
    transport.get=counted
    assert not exchange(viewer,folder,key,transport,False,protocol=2)['errors']
    assert not set(chunks[:-1])&set(downloaded)
    assert viewer.read_object(digest)==raw
    assert not list((viewer.root/'parts').iterdir())


def test_unreadable_v2_index_falls_back_to_full_inventory(tmp_path):
    owner,viewer,folder=devices(tmp_path,'viewer');test=trace_test(owner);key=owner.identity['sync_key']
    exchange(owner,folder,key,protocol=2,verify_existing=False)
    channel=next(folder.iterdir())
    (channel/('checkpoint2-'+'0'*64+'.ctindex')).write_bytes(b'partial upload')
    result=exchange(viewer,folder,key,protocol=2,verify_existing=False)
    assert not result['pending'] and viewer.get(test['id'])['id']==test['id']
    assert len(result['errors'])==1 and 'indice v2 ignorato' in result['errors'][0]
