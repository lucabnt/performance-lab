"""CSV compatibility, independent observations and editable perineal height."""
import csv
import io
import zipfile

from test_features import client, post


def test_perineal_csv_roundtrip_and_revision(tmp_path):
    c=client(tmp_path)
    org=post(c,'organizations',{'name':'DEMO'})
    a=post(c,'athletes',{'organization_id':org['id'],'name':'Demo','surname':'Cavallo'})
    def preview(header, row):
        raw=(header+'\n'+a['id']+','+row+'\n').encode()
        r=c.post('/api/v1/import/preview',data={'organization_id':org['id'],'profile':'antropometria'},files={'file':('synthetic.csv',raw)})
        assert r.status_code==200,r.text
        return r.json()
    header='atleta_id,data,peso_kg,statura_cm,altezza_perineale_cm,peso_fonte,origine'
    template=c.get('/api/v1/import/template/antropometria')
    assert template.status_code==200
    assert template.content.decode('utf-8-sig').strip()==header
    for row,expected in [('2026-01-01,50,160,80,misurato,QA',80),('2026-01-03,50,160,81,misurato,QA',81),('2026-01-02,,,82,misurato,QA',82)]:
        p=preview(header,row)
        assert not p['errors'] and p['ready']==1
        assert p['preview'][0]['perineal_height_cm']==expected
        post(c,'import/commit',{'organization_id':org['id'],'profile':'antropometria','staged_hash':p['staged_hash']})
        assert preview(header,row)['skipped']==1
    old=preview('atleta_id,data,statura_cm','2026-01-04,170')
    assert not old['errors'] and old['preview'][0]['perineal_height_cm'] is None
    # Distinct dates remain independent observations.
    measurements=c.get('/api/v1/state').json()['measurement']
    assert len(measurements)==3
    m=next(m for m in measurements if m['perineal_height_cm']==80)
    from cycling_test.api import Measurement
    payload={k:v for k,v in m.items() if k in Measurement.model_fields}
    r=c.put('/api/v1/measurements/'+m['id'],json={'base':m['revision'],'reason':'Verifica QA','measurement':{**payload,'notes':'QA'}})
    assert r.status_code==200 and r.json()['perineal_height_cm']==80
    with zipfile.ZipFile(io.BytesIO(c.get('/api/v1/export/'+org['id']).content)) as z:
        rows=list(csv.DictReader(io.StringIO(z.read('antropometria.csv').decode())))
    assert sorted(float(r['altezza_perineale_cm']) for r in rows)==[80,81,82]
    for value in ('0','-1','nan','inf','160','170'):
        assert preview(header,f'2026-02-01,,160,{value},misurato,QA')['errors']


def test_perineal_does_not_change_maturity_models():
    from test_maturation import athlete, measurement
    from cycling_test.maturation import anthropometric
    base=measurement(sitting_height_cm=88)
    assert anthropometric(athlete(),base)==anthropometric(athlete(),{**base,'perineal_height_cm':80})
