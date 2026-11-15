import csv
import io
import zipfile
import pytest
from cycling_test.csv_import import plan_import, read
from cycling_test.csv_safety import neutralize, restore
from cycling_test.reports import export_csv
from cycling_test.store import Store

TEXTS=['=HYPERLINK("http://x")','+39 333','-tracciato','@SUM(A1)','\tcella','\rcella',"'=gia",'normale','',"'"]


@pytest.mark.parametrize('text',TEXTS)
def test_neutralization_is_reversible(text):
    assert restore(neutralize(text))==text
    assert not neutralize(text) or neutralize(text)[0] not in '=+-@\t\r'


@pytest.mark.parametrize('value',['-12.5','-12,5','+3',-4,2.5,None])
def test_numbers_are_untouched(value):
    assert neutralize(value)==value


def test_export_neutralizes_text_and_reimport_restores_it(tmp_path):
    store=Store(tmp_path/'a');org=store.save('organization',{'name':'Club'})
    notes='=1+1 @nota'
    athlete=store.save('athlete',{'organization_id':org['id'],'name':'+Ada','surname':'-Rossi','birth_year':2011,'notes':notes,'status':'active'})
    store.save('measurement',{'athlete_id':athlete['id'],'date':'2026-01-10','weight_kg':50.5,'height_cm':160,'source':'misurato'})
    with zipfile.ZipFile(io.BytesIO(export_csv(store,org['id']))) as z:
        raw=z.read('atleti.csv');measures=z.read('antropometria.csv').decode()
    row=next(csv.DictReader(io.StringIO(raw.decode())))
    assert (row['cognome'],row['nome'],row['note'])==("'-Rossi","'+Ada","'"+notes)
    assert ',50.5,160,' in measures
    assert read(raw)[0]['note']==notes
    target=Store(tmp_path/'b');org2=target.save('organization',{'name':'Club'})
    result=plan_import(target,org2['id'],'atleti',raw)
    assert not result['errors']
    imported=next(p for kind,p in result['entries'] if kind=='athlete')
    assert (imported['surname'],imported['name'],imported['notes'])==('-Rossi','+Ada',notes)
