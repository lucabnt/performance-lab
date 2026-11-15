"""Isolated synthetic QA archive and five report examples. Never imports private data."""
import json
from pathlib import Path
import argparse
from cycling_test.store import Store
from cycling_test.erg import parse_erg
from cycling_test.fit import decode_fit
from cycling_test.analysis import analyze
from cycling_test.observations import enrich
from cycling_test.specialist import gas_analysis
from cycling_test.archive_report import build,render
from cycling_test.reports import report


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data',default='.local/qa-incrementale-05');args=parser.parse_args()
    root=Path(__file__).resolve().parents[1];s=Store(args.data)
    if s.list('organization'):raise SystemExit('Archivio non vuoto: nessun dato modificato.')
    org=s.save('organization',{'name':'Fuorigiri - società dimostrativa, dati sintetici'})
    manifest=json.loads((root/'examples/synthetic/manifest.json').read_text(encoding='utf-8'))
    parents={};groups={};protocols={};athletes=[];last=None
    for index,item in enumerate(manifest):
        family=item['protocol']
        if family not in protocols:
            raw=(root/'examples/protocols'/f'{family}.erg').read_bytes();definition=parse_erg(raw.decode('utf-8-sig'))
            for stage in definition['segments']:stage['phase']='warmup' if stage['end_s']<=600 else 'increment'
            protocols[family]=s.save('protocol',{'name':family,'family':family,'version':'originale-1','definition':definition,'objects':[s.object(raw)]})
            parents[family]=s.save('group',{'organization_id':org['id'],'name':'Allievi' if 'ALL' in family else 'Esordienti','season':''})
            for year in (2025,2026):groups[family,year]=s.save('group',{'organization_id':org['id'],'name':parents[family]['name'],'season':str(year),'parent_id':parents[family]['id']})
        athlete=s.save('athlete',{'organization_id':org['id'],'name':f'Atleta {index+1}','surname':'Simulazione','birth_year':2010 if 'ALL' in family else 2012,'birth_confirmed':True,'sex':'','status':'active'})
        athletes.append(athlete);p=protocols[family]
        raw=(root/'examples/synthetic'/item['file']).read_bytes();trace=decode_fit(raw);original=s.object(raw)
        trace_hash=s.object(json.dumps({**trace,'original_hash':original}).encode())
        for year in (2025,2026):
            group=groups[family,year]
            s.save('membership',{'athlete_id':athlete['id'],'group_id':group['id'],'start':f'{year}-01-01','end':f'{year}-12-31','category_year':1 if year==2025 else 2})
            end=item['effort_end_s']-(240 if year==2025 else 0)
            settings={'offset_s':0,'end_s':end,'weight_kg':item['weight_kg']-(2 if year==2025 else 0),'height_cm':160+index*2-(3 if year==2025 else 0),
                'weight_source':'misurato','rest_hr':60-index,'rest_after_s':300,'rpe':9,'fthr_bpm':180,'threshold_w':None,
                'conditions':{'device':'Rullo sintetico','calibration':'Simulata','recovery_mode':'passivo','posture':'seduto','stop_reason':'esaurimento simulato'},
                'lactate':[{'at_s':840+i*240,'mmol_l':level,'step_number':i+2} for i,level in enumerate([1.,1.2,1.8,3.,5.]) if 840+i*240<=end]}
            s.save('measurement',{'athlete_id':athlete['id'],'date':f'{year}-06-01','weight_kg':settings['weight_kg'],'height_cm':settings['height_cm'],'source':'misurato'})
            analysis=analyze(trace['samples'],p['definition'],settings)
            objects=[trace_hash,original]
            if index==0 and year==2026:
                gas=[]
                for t in range(int(trace['duration_s'])+1):
                    vo2=.7+2.3*min(1,max(0,t-600)/(end-600));vco2=.85*vo2+max(0,vo2-1.8)*.6
                    gas.append({'t':t,'vo2':vo2,'vco2':vco2,'ve':vco2*27+max(0,vo2-2.4)*25,'peto2':100+vo2,'petco2':38-max(0,vo2-2.4)*3})
                csv='t,vo2_l_min,vco2_l_min,ve_l_min,peto2_mmhg,petco2_mmhg\n'+'\n'.join(','.join(str(row[k]) for k in ('t','vo2','vco2','ve','peto2','petco2')) for row in gas)
                gas_original=s.object(csv.encode());gas_hash=s.object(json.dumps({'kind':'gas','samples':gas,'original_hash':gas_original}).encode())
                settings['gas_hash']=gas_hash;objects += [gas_hash,gas_original]
                analysis['gas']=gas_analysis(gas,settings,analysis)
            analysis=enrich(analysis,trace['samples'],settings)
            test=s.save('test',{'organization_id':org['id'],'athlete_id':athlete['id'],'athlete_snapshot':athlete,'protocol_id':p['id'],'trace_hash':trace_hash,'date':f'{year}-06-01',
                'settings':settings,'analysis':analysis,'samples':trace['samples'],'objects':objects,'notes':'ESEMPIO SINTETICO - nessun risultato reale o calibrazione clinica.'})
            if index==0 and year==2026:last=(test,athlete,p)
    output=root/'output/pdf';output.mkdir(parents=True,exist_ok=True)
    scopes=[('fuorigiri-societa-sintetica',{}),('fuorigiri-gruppo-sintetico',{'group':parents[manifest[0]['protocol']]['id']}),
            ('fuorigiri-gruppo-2026-sintetico',{'group':parents[manifest[0]['protocol']]['id'],'season':'2026'}),
            ('fuorigiri-atleta-sintetico',{'athlete':athletes[0]['id']})]
    for name,filters in scopes:
        data=build(s,org['id'],**filters)
        (output/(name+'.pdf')).write_bytes(render(data,'pdf'))
        (output/(name+'.zip')).write_bytes(render(data,'md'))
    (output/'fuorigiri-test-specialistico-sintetico.pdf').write_bytes(report(*last,'pdf'))
    print('QA sintetica:',s.root,'- 4 atleti / 8 test / 2 stagioni; 5 PDF in',output)


if __name__=='__main__':main()
