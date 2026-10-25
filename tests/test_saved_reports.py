from fastapi.testclient import TestClient
from cycling_test.api import create_app
from cycling_test.store import Store


def test_saved_report_context_dates_and_download_preserve_records(tmp_path):
    store=Store(tmp_path)
    org=store.save('organization',{'name':'Club demo'})
    group=store.save('group',{'organization_id':org['id'],'name':'Allievi','season':'2023'})
    athlete=store.save('athlete',{'organization_id':org['id'],'name':'Ada','surname':'Rossi','status':'archived'})
    test=store.save('test',{'organization_id':org['id'],'athlete_id':athlete['id'],'date':'2023-05-02'})
    body=b'report fixture';digest=store.object(body)
    old=store.save('report',{'organization_id':org['id'],'format':'pdf','query':{'group':group['id'],'athlete':athlete['id']},'objects':[digest]})
    newer=store.save('report',{'organization_id':org['id'],'format':'json','test_id':test['id'],'objects':[digest]})
    store.save('report',{'analysis_type':'maturation','format':'pdf'})
    client=TestClient(create_app(tmp_path,token='qa'))
    client.headers['X-Fuorigiri-Token']='qa'
    response=client.get('/api/v1/reports');assert response.status_code==200
    rows=response.json();assert [r['id'] for r in rows]==[newer['id'],old['id']]
    assert rows[0]['saved_at'] and rows[1]['saved_at']
    assert rows[0]['context']['athlete']=='Rossi Ada'
    assert rows[0]['context']['test_date']=='2023-05-02'
    assert rows[1]['context']=={'organization':'Club demo','group':'Allievi','season':'2023','athlete':'Rossi Ada','test_date':''}
    assert store.get(old['id'])==old
    assert client.get('/api/v1/reports/'+newer['id']+'/download').content==body
