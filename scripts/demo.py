"""Create a separate synthetic archive; never touches the user's default archive."""
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tests'))
from synthetic import ERG, samples, fit_bytes
from cycling_test.erg import parse_erg
from cycling_test.analysis import analyze
from cycling_test.store import Store
from cycling_test.reports import report

parser=argparse.ArgumentParser()
parser.add_argument('--data',default='.local/demo')
args=parser.parse_args()
store=Store(args.data)
if store.list('organization'):
    raise SystemExit('Archivio non vuoto: nessun dato modificato.')
org=store.save('organization',{'name':'Società dimostrativa · dati sintetici'})
group=store.save('group',{'organization_id':org['id'],'name':'Allievi','season':'2026'})
p=parse_erg(ERG);p['segments'][0]['phase']='warmup'
erg_hash=store.object(ERG.encode())
protocol=store.save('protocol',{'name':'Incrementale dimostrativo','family':'DEMO-ERG','version':'1.0','parent_id':None,'reason':'Solo dati sintetici; non è un protocollo validato.','definition':p,'objects':[erg_hash]})
names=[('Andrea','Esempio'),('Marta','Demo'),('Luca','Campione'),('Giulia','Prova')]
for index,(name,surname) in enumerate(names):
    a=store.save('athlete',{'organization_id':org['id'],'name':name,'surname':surname,'birth_year':2011,'birth_confirmed':False,'birth_source':'dato sintetico','sex':'','notes':'Profilo dimostrativo'})
    store.save('membership',{'athlete_id':a['id'],'group_id':group['id'],'start':'2026-01-01','end':None})
    store.save('measurement',{'athlete_id':a['id'],'date':'2026-10-16','weight_kg':50+index*2,'height_cm':160+index*2,'source':'misurato'})
    for date,end in [('2026-03-12',1200),('2026-07-18',1320),('2026-10-16',1440)]:
        rows=samples(end)
        original=store.object(fit_bytes())
        trace=store.object(json.dumps({'samples':rows,'original_hash':original}).encode())
        settings={'offset_s':0,'end_s':end,'weight_kg':50+index*2,'height_cm':160+index*2,'rest_hr':60,'rest_after_s':300}
        t=store.save('test',{'organization_id':org['id'],'athlete_id':a['id'],'protocol_id':protocol['id'],'trace_hash':trace,'date':date,'settings':settings,'notes':'Tracciato sintetico di dimostrazione.','samples':rows,'analysis':analyze(rows,p,settings),'group_ids':[group['id']],'objects':[trace,original]})
        if index==0 and end==1440:
            out=Path('tmp/qa');out.mkdir(parents=True,exist_ok=True)
            (out/'report-demo.pdf').write_bytes(report(t,a,protocol,'pdf'))
Path('tmp/qa/demo.fit').write_bytes(fit_bytes())
Path('tmp/qa/demo.erg').write_text(ERG)
print('Archivio sintetico creato in',store.root)
