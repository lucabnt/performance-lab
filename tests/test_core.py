import io
import zipfile

import pytest
from fastapi.testclient import TestClient
from cryptography.fernet import Fernet
from cycling_test.analysis import analyze, window
from cycling_test.api import create_app
from cycling_test.erg import parse_erg
from cycling_test.fit import decode_fit
from cycling_test.store import Store, ConflictError
from cycling_test.sync import exchange
from synthetic import ERG, samples, fit_bytes


@pytest.mark.parametrize('filename,duration,first_target', [('AER-RULLO-ALL.erg',5400,130),('AER-RULLO-ESO.erg',5880,80)])
def test_supplied_protocol_files(filename,duration,first_target):
    from pathlib import Path
    p=parse_erg((Path(__file__).resolve().parents[1]/'examples/protocols'/filename).read_text())
    assert p['duration_s']==duration
    assert p['segments'][1]['start_s']==600
    assert p['segments'][1]['start_w']==first_target


def protocol():
    p=parse_erg(ERG)
    p['segments'][0]['phase']='warmup'
    return p


def test_erg_preserves_step_boundaries():
    p=protocol()
    assert p['segments'][0]['end_s']==600
    assert p['segments'][1]['start_s']==600
    assert p['segments'][1]['start_w']==80
    assert len(p['points'])==12


@pytest.mark.parametrize('text',[ERG.replace('10 80','9 80'),ERG.replace('0 60','0 nan'),ERG.replace('MINUTES WATTS','MINUTES PERCENT')])
def test_bad_erg_rejected(text):
    with pytest.raises(ValueError):parse_erg(text)


def test_partial_stage_and_recovery():
    a=analyze(samples(),protocol(),{'offset_s':0,'end_s':1440,'weight_kg':50})
    assert a['map_w']==120
    assert a['map_alt_w']==130
    assert a['map_wkg']==2.4
    assert a['steps'][-1]['actual_s']==120
    assert 16 < a['recovery'][0]['hrr_bpm'] < 20


def test_gap_is_not_zero_or_interpolated():
    rows=[{'t':0,'power':100},{'t':1,'power':200},{'t':20,'power':300},{'t':21,'power':300}]
    w=window(rows,'power',0,21)
    assert w['mean']==200
    assert w['integral']==400
    assert w['coverage']<.1


def test_missing_early_stage_invalidates_later_map():
    rows=samples()
    for r in rows:
        if 600<=r['t']<840:r['power']=None
    a=analyze(rows,protocol(),{'end_s':1440})
    assert a['map_w'] is None


def test_no_heart_rate_no_estimate():
    rows=[{**r,'hr':None} for r in samples()]
    a=analyze(rows,protocol(),{'end_s':1440})
    assert a['fc_max_test_bpm'] is None
    assert a['recovery'][0]['hrr_bpm'] is None


def test_fit_roundtrip_and_crc():
    raw=fit_bytes()
    decoded=decode_fit(raw)
    assert len(decoded['samples'])==len(samples())
    assert decoded['samples'][600]['power']==samples()[600]['power']
    with pytest.raises(ValueError):decode_fit(raw[:-1]+bytes([raw[-1]^255]))


def test_revision_prevents_lost_update(tmp_path):
    s=Store(tmp_path)
    a=s.save('organization',{'name':'A'})
    s.save('organization',{'name':'B'},a['id'],a['revision'])
    with pytest.raises(ConflictError):s.save('organization',{'name':'C'},a['id'],a['revision'])


def test_sync_duplicate_conflict_and_partial(tmp_path):
    a,b=Store(tmp_path/'a'),Store(tmp_path/'b')
    folder=tmp_path/'shared';folder.mkdir()
    key=Fernet.generate_key().decode()
    first=a.save('organization',{'name':'A'})
    exchange(a,folder,key);exchange(b,folder,key)
    assert b.get(first['id'])['name']=='A'
    assert exchange(b,folder,key)['received']==0
    a.save('organization',{'name':'Left'},first['id'],first['revision'])
    b.save('organization',{'name':'Right'},first['id'],first['revision'])
    exchange(a,folder,key)
    result=exchange(b,folder,key)
    assert result['conflicts']==1
    assert b.get(first['id'])['name']=='Right'
    (next(folder.iterdir())/'broken.ctsync').write_bytes(b'partial')
    assert len(exchange(a,folder,key)['errors'])==1


def test_api_full_workflow(tmp_path):
    client=TestClient(create_app(tmp_path,token='test'))
    assert client.get('/api/v1/state').status_code==401
    client.headers['X-Fuorigiri-Token']='test'
    def post(url,body):
        r=client.post('/api/v1/'+url,json=body)
        assert r.status_code==200,r.text
        return r.json()
    org=post('organizations',{'name':'Società demo'})
    a=post('athletes',{'organization_id':org['id'],'name':'Atleta','surname':'Demo'})
    group=post('groups',{'organization_id':org['id'],'name':'Allievi','season':'2026'})
    post('memberships',{'athlete_id':a['id'],'group_id':group['id'],'start':'2026-01-01'})
    post('measurements',{'athlete_id':a['id'],'date':'2026-10-16','weight_kg':50,'height_cm':160})
    r=client.post('/api/v1/protocols',data={'name':'Test','family':'DEMO','version':'1.0','warmup_s':600},files={'file':('demo.erg',ERG)})
    assert r.status_code==200,r.text
    p=r.json()
    r=client.post('/api/v1/traces',files={'file':('demo.fit',fit_bytes())})
    assert r.status_code==200,r.text
    trace=r.json()
    t=post('tests',{'athlete_id':a['id'],'protocol_id':p['id'],'trace_hash':trace['hash'],'date':'2026-10-16','settings':{'end_s':1440,'weight_kg':50}})
    assert t['analysis']['map_w']==120
    assert t['group_ids']==[group['id']]
    pdf=client.get(f"/api/v1/tests/{t['id']}/report/pdf")
    assert pdf.status_code==200 and pdf.content.startswith(b'%PDF')
    md=client.get(f"/api/v1/tests/{t['id']}/report/md")
    with zipfile.ZipFile(io.BytesIO(md.content)) as z:
        assert 'assets/test.png' in z.namelist()
        assert '120' in z.read('report.md').decode()
    exported=client.get('/api/v1/export/'+org['id'])
    with zipfile.ZipFile(io.BytesIO(exported.content)) as z:
        from cycling_test.reports import CSV_HEADERS
        assert z.read('test_aerobico.csv').decode().splitlines()[0]==CSV_HEADERS['test_aerobico']
    backup=client.get('/api/v1/backup')
    assert 'archive.sqlite' in zipfile.ZipFile(io.BytesIO(backup.content)).namelist()
    assert client.post('/api/v1/groups',json={'organization_id':a['id'],'name':'Wrong'}).status_code==422
    assert client.get('/api/v1/state',headers={'origin':'https://evil.invalid'}).status_code==403


def test_concurrent_write_with_same_base_is_a_conflict(tmp_path):
    import sqlite3,threading,time
    from cycling_test.store import encoded
    store=Store(tmp_path);record=store.save('athlete',{'name':'Ada'})
    # A sync job holds the write lock while applying a newer revision.
    other=sqlite3.connect(tmp_path/'archive.sqlite',isolation_level=None)
    other.execute('BEGIN IMMEDIATE')
    other.execute('UPDATE records SET revision=?,data=? WHERE id=?',('remote',encoded({**record,'revision':'remote'}),record['id']))
    outcome=[]
    def save():
        try:outcome.append(store.save('athlete',{'name':'Ada B.'},record['id'],record['revision']))
        except ConflictError as exc:outcome.append(exc)
    worker=threading.Thread(target=save);worker.start();time.sleep(0.3)
    other.execute('COMMIT');other.close();worker.join(10)
    assert isinstance(outcome[0],ConflictError)
    assert store.get(record['id'])['revision']=='remote'
