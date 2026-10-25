import csv
import io
import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.csv_import import template_csv
from cycling_test.membership_import import COLUMNS, sample_csv


def csv_bytes(rows):
    out=io.StringIO(newline=''); writer=csv.DictWriter(out,fieldnames=COLUMNS)
    writer.writeheader();writer.writerows(rows)
    return out.getvalue().encode('utf-8-sig')


def setup(tmp_path):
    c=TestClient(create_app(tmp_path,token='test'));c.headers['X-Fuorigiri-Token']='test'
    r=c.post('/api/v1/organizations',json={'name':'DEMO'});assert r.status_code==200
    org=r.json()['id']
    raw=b'atleta_id,nome,cognome\nDEMO-001,Giulia,Riva\nDEMO-002,Marco,Demo\n'
    r=c.post('/api/v1/import/preview',data={'organization_id':org,'profile':'atleti'},files={'file':('atleti.csv',raw)})
    assert r.status_code==200
    assert c.post('/api/v1/import/commit',json={'organization_id':org,'profile':'atleti','staged_hash':r.json()['staged_hash']}).status_code==200
    return c,org


def preview(c,org,raw):
    r=c.post('/api/v1/import/preview',data={'organization_id':org,'profile':'appartenenze'},files={'file':('appartenenze.csv',raw)})
    assert r.status_code==200,r.text
    return r.json()


def commit(c,org,p):
    return c.post('/api/v1/import/commit',json={'organization_id':org,'profile':'appartenenze','staged_hash':p['staged_hash']})


def row(**kwargs):
    return {'atleta_id':'DEMO-001','nome':'Giulia','cognome':'Riva','data_inizio':'2024-01-01','data_fine':'2024-12-31','gruppo':'Esordienti','sottogruppo':'2024',**kwargs}


def test_templates_example_preview_atomic_commit_reimport_and_undo(tmp_path):
    c,org=setup(tmp_path)
    assert c.get('/api/v1/import/template/appartenenze').content==template_csv('appartenenze')
    assert c.get('/api/v1/import/example/appartenenze').content==sample_csv()
    assert list(csv.reader(io.StringIO(template_csv('appartenenze').decode('utf-8-sig'))))==[COLUMNS]
    before=c.get('/api/v1/state').json()
    p=preview(c,org,sample_csv())
    assert not p['errors'] and p['ready_rows']==4 and len(p['new_groups'])==6
    assert p['preview'][0]['athlete_name']=='Riva Giulia'
    assert p['preview'][0]['group_name']=='Esordienti' and p['preview'][0]['subgroup']=='2024'
    assert c.get('/api/v1/state').json()==before
    result=commit(c,org,p);assert result.status_code==200,result.text
    state=c.get('/api/v1/state').json()
    assert len(state['group'])==6 and len(state['membership'])==4
    assert state['athlete']==before['athlete'] and state['test']==before['test']
    assert sorted(m['start'] for m in state['membership'])==['2024-01-01','2025-01-01','2026-01-01','2027-01-01']
    again=preview(c,org,sample_csv());assert not again['errors'] and again['skipped']==4 and again['ready']==0
    r=c.post('/api/v1/import/'+result.json()['batch_id']+'/undo',json={'reason':'Prova su dati sintetici'})
    assert r.status_code==200,r.text
    state=c.get('/api/v1/state').json()
    assert state['membership']==[] and state['athlete']==before['athlete']
    assert all(g['status']=='deleted' for g in state['group'])


@pytest.mark.parametrize('changes',[
    {'nome':'Nome errato'},{'atleta_id':'ID-NON-PRESENTE'},
    {'data_fine':'2023-12-31'},{'data_inizio':'31/01/2024'},
    {'anno_categoria':'0'},{'gruppo':''},
])
def test_any_invalid_row_blocks_the_entire_batch_without_creating_groups(tmp_path,changes):
    c,org=setup(tmp_path)
    p=preview(c,org,csv_bytes([row(),row(**changes)]))
    assert p['errors']
    assert commit(c,org,p).status_code==422
    state=c.get('/api/v1/state').json()
    assert state['group']==[] and state['membership']==[] and len(state['athlete'])==2


def test_overlaps_are_errors_exact_duplicates_skipped_open_end_preserved(tmp_path):
    c,org=setup(tmp_path)
    p=preview(c,org,csv_bytes([row(data_fine=''),row(data_fine='')]))
    assert not p['errors'] and p['ready_rows']==1 and p['skipped']==1
    assert commit(c,org,p).status_code==200
    assert c.get('/api/v1/state').json()['membership'][0]['end'] is None
    p=preview(c,org,csv_bytes([row(data_inizio='2024-12-31',data_fine='2025-01-01')]))
    assert p['errors'] and commit(c,org,p).status_code==422


def test_legacy_root_season_reused_and_deleted_season_not_recreated(tmp_path):
    c,org=setup(tmp_path)
    g=c.post('/api/v1/groups',json={'organization_id':org,'name':'Esordienti','season':'2024'}).json()
    p=preview(c,org,csv_bytes([row()]))
    assert not p['errors'] and p['new_groups']==[]
    assert commit(c,org,p).status_code==200
    assert c.get('/api/v1/state').json()['membership'][0]['group_id']==g['id']
    r=c.post(f"/api/v1/groups/{g['id']}/lifecycle",json={'base':g['revision'],'status':'deleted','scope':'season'})
    assert r.status_code==200
    assert preview(c,org,csv_bytes([row()]))['errors']


def test_undo_cannot_remove_groups_used_after_import(tmp_path):
    c,org=setup(tmp_path)
    p=preview(c,org,csv_bytes([row()]))
    batch=commit(c,org,p).json()['batch_id']
    state=c.get('/api/v1/state').json()
    g=next(g for g in state['group'] if g.get('parent_id'))
    a=next(a for a in state['athlete'] if a['external_id']=='DEMO-002')
    assert c.post('/api/v1/memberships',json={'group_id':g['id'],'athlete_id':a['id'],'start':'2024-01-01'}).status_code==200
    assert c.post('/api/v1/import/'+batch+'/undo',json={'reason':'Non deve eliminare dipendenze successive'}).status_code==422
