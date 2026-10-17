"""Create a separate synthetic archive; never touches the user's default archive."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from synthetic import ERG, samples, fit_bytes
from cycling_test.erg import parse_erg
from cycling_test.analysis import analyze
from cycling_test.observations import enrich
from cycling_test.zones import preset
from cycling_test.store import Store
from cycling_test.reports import report

parser=argparse.ArgumentParser()
parser.add_argument('--data',default='.local/demo')
args=parser.parse_args()
store=Store(args.data)
if store.list('organization'):
    raise SystemExit('Archivio non vuoto: nessun dato modificato.')
org=store.save('organization',{'name':'Società dimostrativa · dati sintetici'})
category=store.save('group',{'organization_id':org['id'],'name':'Allievi','season':'','parent_id':None})
group=store.save('group',{'organization_id':org['id'],'name':'Allievi','season':'2026','parent_id':category['id']})
p=parse_erg(ERG);p['segments'][0]['phase']='warmup'
erg_hash=store.object(ERG.encode())
protocol=store.save('protocol',{'name':'Incrementale dimostrativo','family':'DEMO-ERG','version':'1.0','parent_id':None,'reason':'Solo dati sintetici; non è un protocollo validato.','definition':p,'objects':[erg_hash]})
names=[('Andrea','Esempio'),('Marta','Demo'),('Luca','Campione'),('Giulia','Prova')]
for index,(name,surname) in enumerate(names):
    a=store.save('athlete',{'organization_id':org['id'],'name':name,'surname':surname,'birth_year':2011,'birth_confirmed':False,'birth_source':'dato sintetico','sex':'','notes':'Profilo dimostrativo'})
    store.save('membership',{'athlete_id':a['id'],'group_id':group['id'],'category_year':1,'start':'2026-01-01','end':None})
    store.save('measurement',{'athlete_id':a['id'],'date':'2026-03-01','weight_kg':49+index*2,'height_cm':158+index*2,'source':'misurato'})
    store.save('measurement',{'athlete_id':a['id'],'date':'2026-10-16','weight_kg':50+index*2,'height_cm':160+index*2,'source':'misurato'})
    for date,end in [('2026-03-12',1200),('2026-07-18',1320),('2026-10-16',1440)]:
        rows=samples(end)
        original=store.object(fit_bytes())
        trace=store.object(json.dumps({'samples':rows,'original_hash':original}).encode())
        settings={'offset_s':0,'end_s':end,'weight_kg':50+index*2,'height_cm':160+index*2,'weight_source':'misurato','rest_hr':60,'rest_after_s':300,
                  'threshold_coefficient':.8,'threshold_source':'stimata_da_map','fthr_bpm':180,'rpe':7,'zone_schemes':[preset('hr'),preset('power')]}
        t=store.save('test',{'organization_id':org['id'],'athlete_id':a['id'],'protocol_id':protocol['id'],'trace_hash':trace,'date':date,'settings':settings,'notes':'Tracciato sintetico di dimostrazione.','samples':rows,'analysis':enrich(analyze(rows,p,settings),rows,settings),'group_ids':[group['id']],'objects':[trace,original]})
        if index==0 and end==1440:
            out=Path('tmp/qa');out.mkdir(parents=True,exist_ok=True)
            (out/'report-demo.pdf').write_bytes(report(t,a,protocol,'pdf'))
Path('tmp/qa/demo.fit').write_bytes(fit_bytes())
Path('tmp/qa/demo.erg').write_text(ERG)
import csv
with Path('tmp/qa/demo-trace.csv').open('w',newline='',encoding='utf-8') as f:
    writer=csv.DictWriter(f,fieldnames=['t','power','hr','cadence']);writer.writeheader();writer.writerows(samples())
Path('tmp/qa/demo-atleti.csv').write_text('atleta_id,cognome,nome,anno_nascita,attivo\nCSV-DEMO,Esempio,Importato,2011,si\n',encoding='utf-8')
Path('tmp/qa/demo-antropometria.csv').write_text('atleta_id,data,peso_kg,statura_cm,peso_fonte\nCSV-DEMO,2026-10-01,50,160,misurato\n',encoding='utf-8')
Path('tmp/qa/demo-storico.csv').write_text('test_id,atleta_id,data,protocollo_id,map_w,peso_kg,soglia_w,soglia_origine\nCSV-TEST-1,CSV-DEMO,2026-10-01,DEMO-STORICO,200,50,160,stimata_da_map\n',encoding='utf-8')
print('Archivio sintetico creato in',store.root)
