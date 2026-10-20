import io
import json
import zipfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from cycling_test.store import Store,encoded
from cycling_test.workspaces import Workspaces
from cycling_test.backup_stream import write_backup,inspect_file
from cycling_test.recovery import restore,summary,backup_bytes,export_recovery
from cycling_test.society_migration import preview,extract
from cycling_test.api import create_app


def club(root):
    manager=Workspaces(root,Store(root));entry=manager.create('Club','Owner');store=manager.get(entry['id'])
    h=store.object(b'large synthetic attachment\n'*100000)
    athlete=store.save('athlete',{'organization_id':entry['organization_id'],'name':'Demo','surname':'Athlete','objects':[h]})
    store.save('athlete',{**athlete,'notes':'revision'},athlete['id'],athlete['revision'])
    return manager,entry,store,athlete


def test_streamed_backup_restore_and_recovery_avoid_whole_object_reads(tmp_path,monkeypatch):
    manager,entry,source,athlete=club(tmp_path/'source')
    # Fail if the new paths fall back to the whole-object memory API.
    monkeypatch.setattr(Store,'read_object',lambda *a:pytest.fail('whole object read'))
    path=write_backup(source,tmp_path/'data.zip')
    with inspect_file(path) as data:
        assert summary(data)['schema']==3 and summary(data)['checksums']
        assert len(data['changes'])==3
    other=Workspaces(tmp_path/'other',Store(tmp_path/'other'))
    copy_entry=restore(other,path,'independent',operator='New owner');copy=other.get(copy_entry['id'])
    assert copy.history(athlete['id'])==source.history(athlete['id'])
    assert (copy.root/'objects'/athlete['objects'][0]).stat().st_size==len(b'large synthetic attachment\n')*100000
    recovered=restore(other,path,'recover',recovery_raw=export_recovery(source,'test-recovery-password'),password='test-recovery-password')
    assert other.get(recovered['id']).identity==source.identity
    with pytest.raises(ValueError):write_backup(source,path)


def test_v3_crosses_legacy_limits_and_still_reads_legacy(tmp_path,monkeypatch):
    from cycling_test import recovery
    _,_,store,_=club(tmp_path/'source')
    legacy=backup_bytes(store);legacy_path=tmp_path/'legacy.zip';legacy_path.write_bytes(legacy)
    with inspect_file(legacy_path) as data:assert summary(data)['schema']==2
    monkeypatch.setattr(recovery,'MAX_UPLOAD',100)
    with pytest.raises(ValueError):backup_bytes(store)
    path=write_backup(store,tmp_path/'new.zip')
    with inspect_file(path) as data:assert summary(data)['counts']['athlete']==1


@pytest.mark.parametrize('bad',['corruption','missing','traversal','duplicate','schema','inventory'])
def test_stream_backup_corruption_never_publishes_restore(tmp_path,bad):
    _,_,source,athlete=club(tmp_path/'source');path=write_backup(source,tmp_path/'good.zip')
    with zipfile.ZipFile(path) as z:files={name:z.read(name) for name in z.namelist()}
    obj=next(name for name in files if name.startswith('objects/'))
    if bad=='corruption':files[obj]=b'altered'
    if bad=='missing':files.pop(obj)
    if bad=='traversal':files['../escape']=b'bad'
    if bad=='schema':files['manifest.json']=b'{"schema":99}'
    if bad=='inventory':files['inventory.jsonl']=b'{}\n'
    broken=tmp_path/'bad.zip'
    with zipfile.ZipFile(broken,'w') as z:
        for name,raw in files.items():z.writestr(name,raw)
        if bad=='duplicate':z.writestr(obj,files[obj])
    other=Workspaces(tmp_path/'other',Store(tmp_path/'other'))
    with pytest.raises(ValueError):restore(other,broken,'independent',operator='New owner')
    assert not other.entries() and not (tmp_path/'escape').exists()


def legacy(root):
    source=Store(root);a=source.save('organization',{'name':'A'});b=source.save('organization',{'name':'B'})
    x=source.save('athlete',{'organization_id':a['id'],'name':'A','surname':'Athlete'})
    y=source.save('athlete',{'organization_id':b['id'],'name':'B','surname':'Athlete'})
    h=source.object(b'A only trace')
    measure=source.save('measurement',{'athlete_id':x['id'],'height_cm':165,'date':'2025-01-01','objects':[h]})
    source.save('measurement',{**measure,'height_cm':166},measure['id'],measure['revision'])
    source.save('test',{'organization_id':b['id'],'athlete_id':y['id'],'objects':[source.object(b'B only trace')]})
    return source,a,b,x,y,measure


def test_split_infers_scope_preserves_revisions_and_copies_only_own_objects(tmp_path):
    source,a,b,x,y,measure=legacy(tmp_path/'legacy');p=preview(source)
    before=(source.root/'archive.sqlite').read_bytes()
    manager=Workspaces(tmp_path/'target',Store(tmp_path/'target'))
    entry=extract(manager,source,a['id'],p['source_hash'],'New owner');copy=manager.get(entry['id'])
    assert copy.list('organization')==[a] and copy.get(x['id'])==x
    assert copy.history(measure['id'])==source.history(measure['id'])
    with pytest.raises(KeyError):copy.get(y['id'])
    assert len(list((copy.root/'objects').iterdir()))==1
    assert copy.read_object(measure['objects'][0])==b'A only trace'
    assert (source.root/'archive.sqlite').read_bytes()==before
    assert copy.identity['sync_protocol']==2 and not (copy.root/'members.json').exists()
    with copy.connect() as db:
        for row in db.execute('SELECT body FROM changes'):copy.verify_change(json.loads(row[0]))


def test_split_fails_closed_for_cross_society_unassigned_or_stale_preview(tmp_path):
    source,a,b,x,y,measure=legacy(tmp_path/'legacy');manager=Workspaces(tmp_path/'target',Store(tmp_path/'target'))
    stale=preview(source)
    source.save('test',{'organization_id':a['id'],'athlete_id':y['id']})
    with pytest.raises(ValueError,match='cambiato'):extract(manager,source,a['id'],stale['source_hash'],'Owner')
    p=preview(source);assert p['problems']
    with pytest.raises(ValueError,match='riferimenti'):extract(manager,source,a['id'],p['source_hash'],'Owner')
    assert manager.entries()==[]
    orphan=Store(tmp_path/'orphan');org=orphan.save('organization',{'name':'Orphan'})
    orphan.save('measurement',{'height_cm':170})
    p=preview(orphan);assert p['unassigned']
    with pytest.raises(ValueError):extract(manager,orphan,org['id'],p['source_hash'],'Owner')


def test_api_stream_upload_restore_and_legacy_split_preview(tmp_path):
    _,entry,source,athlete=club(tmp_path/'source')
    headers={'X-Fuorigiri-Token':'t','X-Fuorigiri-Workspace':entry['id']}
    with TestClient(create_app(tmp_path/'source','t'),headers=headers) as client:
        downloaded=client.get('/api/v1/backup/scalable');assert downloaded.status_code==200,downloaded.text
        saved=client.post('/api/v1/backup/scalable/save',json={'path':str(tmp_path/'local.zip')});assert saved.status_code==200,saved.text
    with TestClient(create_app(tmp_path/'target','t'),headers={'X-Fuorigiri-Token':'t'}) as client:
        r=client.post('/api/v1/workspaces/restore/preview',files={'file':('backup.zip',downloaded.content)})
        assert r.status_code==200,r.text
        assert r.json()['schema']==3
        restored=client.post('/api/v1/workspaces/restore',data={'backup_hash':r.json()['backup_hash'],'mode':'independent','operator':'New owner'})
        assert restored.status_code==200,restored.text
        assert client.post('/api/v1/workspaces/split/preview',json={}).status_code==200


def test_stream_backup_rejects_missing_historical_object_before_publication(tmp_path):
    _,_,source,athlete=club(tmp_path/'source')
    (source.root/'objects'/athlete['objects'][0]).unlink()
    target=tmp_path/'unusable.zip'
    with pytest.raises(ValueError,match='Allegato storico'):write_backup(source,target)
    assert not target.exists()


def test_split_registration_failure_preserves_registry_source_and_destination(tmp_path,monkeypatch):
    source,a,b,x,y,measure=legacy(tmp_path/'legacy');manager=Workspaces(tmp_path/'target',Store(tmp_path/'target'))
    p=preview(source);target=tmp_path/'empty';target.mkdir()
    def fail(entry):raise OSError('Synthetic registry failure')
    monkeypatch.setattr(manager,'register',fail)
    with pytest.raises(OSError):extract(manager,source,a['id'],p['source_hash'],'Owner',str(target))
    assert manager.entries()==[] and target.is_dir() and not list(target.iterdir())
    assert len(source.list('organization'))==2 and source.get(x['id'])==x
