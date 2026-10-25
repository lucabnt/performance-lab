import io
import json
import zipfile
from copy import deepcopy
from pypdf import PdfReader
from cycling_test.store import Store
from cycling_test.archive_report import build, render, RENDERER


def seed(root, athlete_count=2, test_count=8, measurement_count=4):
    store=Store(root)
    org=store.save('organization',{'name':'Società DEMO - dati interamente sintetici'})
    parents={name:store.save('group',{'organization_id':org['id'],'name':name,'season':''}) for name in ('Esordienti','Allievi')}
    seasons={}
    for year in range(2023,2027):
        name='Esordienti' if year<2025 else 'Allievi'
        seasons[year]=store.save('group',{'organization_id':org['id'],'name':name,'season':str(year),'parent_id':parents[name]['id']})
    protocols=[]
    for i in range(3):
        payload={'organization_id':org['id'],'name':['Aerobico DEMO A','Aerobico DEMO B','Wingate DEMO 15 s'][i],'family':['AER-DEMO-A','AER-DEMO-B','ANA-DEMO'][i],'version':'1','definition':{'segments':[],'points':[]},'historical':True}
        if i==2:payload.update(test_type='wingate15',anaerobic_spec={'duration_s':15})
        protocols.append(store.save('protocol',payload))
    athletes=[]
    for i in range(athlete_count):
        a=store.save('athlete',{'organization_id':org['id'],'name':f'Atleta {i+1:02d}','surname':'DEMO','external_id':f'DEMO-{i+1:03d}','birth_year':2010,'birth_confirmed':True,'sex':'M','status':'archived' if i<3 else 'active'})
        athletes.append(a)
        for year in range(2023 if i<3 else 2024,2027):
            store.save('membership',{'athlete_id':a['id'],'group_id':seasons[year]['id'],'start':f'{year}-01-01','end':f'{year}-12-31','category_year':1 if year%2 else 2})
    for i in range(test_count):
        a=athletes[i%athlete_count];p=protocols[i%3];year=2023+i%4
        analysis={'source':'Dichiarato','engine':'historical-1','threshold_source':'stimata_da_map','warnings':['Dati sintetici per verifica del layout.'],'duration_s':15 if i%3==2 else 900,'work_kj':45+i,'cadence_mean_rpm':85,'cadence_max_rpm':110,'fc_max_test_bpm':180+i%15}
        if i%3==2:analysis.update(protocol_snapshot=p['anaerobic_spec'],peak_w=900+i,peak_wkg=18+i/50,mean_w=600+i,mean_wkg=12+i/50,time_to_peak_s=3.2,declared_fatigue_ws=12)
        else:analysis.update(map_w=250+i,map_wkg=5+i/50,threshold_w=190+i,threshold_wkg=3.8+i/50,fthr_bpm=170)
        payload={'organization_id':org['id'],'athlete_id':a['id'],'date':f'{year}-06-{1+i%27:02d}','protocol_id':p['id'],'settings':{'weight_kg':50,'weight_source':'misurato','height_cm':165,'end_s':analysis['duration_s'],'rest_hr':55,'rest_after_s':120,'rpe':8},'analysis':analysis,'samples':[],'historical':True,'notes':'Esempio sintetico, non un risultato reale.'}
        if i%3==2:payload['test_type']='wingate15'
        store.save('test',payload)
    for i in range(measurement_count):
        store.save('measurement',{'athlete_id':athletes[i%athlete_count]['id'],'date':f'{2023+i%4}-03-{1+i%27:02d}','weight_kg':50+i/10,'height_cm':165+i/20,'source':'misurato'})
    return store,org,athletes,seasons


def outlines(reader):
    def walk(items):
        for item in items:
            if isinstance(item,list):yield from walk(item)
            else:yield item
    return list(walk(reader.outline))


def test_archive_pdf_has_linked_index_separate_athlete_pages_and_preserves_data(tmp_path):
    store,org,athletes,_=seed(tmp_path)
    data=build(store,org['id']);original=deepcopy(data)
    pdf=PdfReader(io.BytesIO(render(data)))
    assert data==original and data['renderer']==RENDERER
    titles=outlines(pdf)
    assert any(item.title=='1. Sintesi e copertura' for item in titles)
    assert any(item.title=='4. Protocolli e metodi' for item in titles)
    index=pdf.pages[1].extract_text()
    assert 'Indice' in index and 'DEMO Atleta 01' in index and 'DEMO Atleta 02' in index
    assert len(pdf.pages[1].get('/Annots',[]))>=4
    assert 'Placeholder' not in index
    athlete_pages=[pdf.get_destination_page_number(item) for item in titles if item.title.startswith(('3.1 ','3.2 '))]
    assert len(set(athlete_pages))==2
    for page in athlete_pages:
        assert 'Nascita:' in pdf.pages[page].extract_text()
    with zipfile.ZipFile(io.BytesIO(render(data,'md'))) as archive:
        manifest=json.loads(archive.read('manifest.json'))
        assert manifest==original
        text=archive.read('report.md').decode()
        assert 'Schede individuali degli atleti' in text and 'DEMO Atleta 02' in text


def test_single_athlete_index_has_no_missing_chapter_or_other_athletes(tmp_path):
    store,org,athletes,_=seed(tmp_path)
    data=build(store,org['id'],athlete=athletes[0]['id'])
    pdf=PdfReader(io.BytesIO(render(data)))
    titles=[item.title for item in outlines(pdf)]
    assert '2. Schede individuali degli atleti' in titles and '3. Protocolli e metodi' in titles
    assert not any('Atleta 02' in title for title in titles)


def test_archive_tables_fit_the_printable_width_with_long_labels():
    from cycling_test.archive_pdf import WIDTH,styles,table
    from reportlab.platypus import Paragraph
    ss=styles()
    rows=[[Paragraph('Intestazione lunga di una metrica',ss['TableHeader']) for _ in range(6)]]
    rows.append([Paragraph('Valore e descrizione con unità W/kg',ss['TableCell']) for _ in range(6)])
    grid=table(rows,[110]*6)
    width,height=grid.wrap(WIDTH,700)
    assert width<=WIDTH+.01 and height>0
