import pytest
from fastapi.testclient import TestClient
from cycling_test.api import create_app


def post(c,path,data):
    r=c.post('/api/v1/'+path,json=data)
    assert r.status_code==200,r.text
    return r.json()


def setup(tmp_path):
    c=TestClient(create_app(tmp_path,token='test'));c.headers['X-Fuorigiri-Token']='test'
    org=post(c,'organizations',{'name':'Demo'})
    parent=post(c,'groups',{'organization_id':org['id'],'name':'Allievi'})
    group=post(c,'groups',{'organization_id':org['id'],'name':'Allievi','parent_id':parent['id'],'season':'2026'})
    athletes=[post(c,'athletes',{'organization_id':org['id'],'name':name,'surname':'Demo'}) for name in ['Alfa','Beta']]
    return c,org,group,athletes


def test_group_batch_is_idempotent_and_preserves_membership_period(tmp_path):
    c,org,g,athletes=setup(tmp_path)
    payload={'group_id':g['id'],'athlete_ids':[a['id'] for a in athletes]+[athletes[0]['id']],'start':'2026-01-01','end':'2026-12-31','category_year':2}
    r=post(c,'memberships/batch',payload)
    assert r['added']==2 and r['skipped']==0
    assert all(m['group_id']==g['id'] and m['category_year']==2 and m['start']=='2026-01-01' and m['end']=='2026-12-31' for m in r['memberships'])
    assert post(c,'memberships/batch',payload)['skipped']==2
    assert len(c.get('/api/v1/state').json()['membership'])==2
    assert post(c,'memberships/batch',{**payload,'start':'2026-12-31','end':'2027-01-15'})['added']==0
    assert post(c,'memberships/batch',{**payload,'start':'2027-01-01','end':None})['added']==2
    assert len(c.get('/api/v1/state').json()['membership'])==4


@pytest.mark.parametrize('invalid',['foreign','archived','dates'])
def test_membership_batch_validates_every_athlete_before_writing(tmp_path,invalid):
    c,org,g,athletes=setup(tmp_path)
    if invalid=='foreign':
        other=post(c,'organizations',{'name':'Other'})
        athletes[1]=post(c,'athletes',{'organization_id':other['id'],'name':'Other','surname':'Demo'})
    if invalid=='archived':
        post(c,'records/'+athletes[1]['id']+'/status',{'base':athletes[1]['revision'],'status':'archived'})
    payload={'group_id':g['id'],'athlete_ids':[a['id'] for a in athletes],'start':'2026-01-01','end':'2025-12-31' if invalid=='dates' else None}
    response=c.post('/api/v1/memberships/batch',json=payload)
    assert response.status_code==422,response.text
    assert c.get('/api/v1/state').json()['membership']==[]


def test_individual_assignment_skips_existing_legacy_memberships(tmp_path):
    c,org,g,athletes=setup(tmp_path)
    post(c,'memberships',{'athlete_id':athletes[0]['id'],'group_id':g['id'],'start':'2026-01-01'})
    result=post(c,'memberships/batch',{'athlete_ids':[athletes[0]['id']],'group_id':g['id'],'start':'2026-10-22'})
    assert result['added']==0 and result['skipped']==1
    assert len(c.get('/api/v1/state').json()['membership'])==1
