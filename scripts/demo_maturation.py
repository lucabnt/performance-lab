"""Create a NEW synthetic suite plus explicit growth/maturation acceptance cases."""
import argparse
from datetime import date,timedelta,datetime,timezone
import json
from pathlib import Path
from demo_suite import generate
from cycling_test.store import Store,encoded
from cycling_test.workspaces import Workspaces
from cycling_test.maturation import MeasurementPayload,current


def generate_growth(destination):
    destination=Path(destination)
    manifest=generate(destination,small=True)  # Refuses non-empty destinations.
    manager=Workspaces(destination,Store(destination));cases=[]
    for index,entry in enumerate(manifest['organizations'],1):
        store=manager.get(entry['id']);org=store.list('organization')[0]['id']
        for case in ('peak','missing','adult'):
            a=store.save('athlete',{'organization_id':org,'name':{'peak':'Andrea','missing':'Giulia','adult':'Marco'}[case],
                'surname':'Crescita DEMO '+case,'birth_date':{'peak':'2010-01-01','missing':None,'adult':'2000-01-01'}[case],
                'birth_year':{'peak':2010,'missing':2011,'adult':2000}[case],'sex':'F' if case=='missing' else 'M','status':'active',
                'notes':'SIMULAZIONE — dati interamente sintetici per controllare crescita e limiti.'})
            days=range(-720,721,180) if case=='peak' else (-365,0,180)
            for d in days:
                t=d/365.25;h=160+9*t-2*t**3/3 if case=='peak' else 174+.1*t if case=='adult' else 150+5*t
                payload=MeasurementPayload(athlete_id=a['id'],date=date(2024,1,1)+timedelta(days=d),height_cm=h,weight_kg=55,
                    sitting_height_cm=h*.52 if case=='peak' else None,source='misurato' if case!='missing' else 'dichiarato',
                    lower_limb_cm=h*.49 if case=='peak' else None,adult_height_cm=180 if case=='peak' else None,
                    adult_height_method='Previsione esterna sintetica' if case=='peak' else '',adult_height_source='SOLO DEMO — non clinico' if case=='peak' else '')
                store.save('measurement',{**payload.model_dump(mode='json'),'organization_id':org})
            result=current(store,a,'2026-01-01');body={'organization_id':org,'athlete_id':a['id'],'analysis_type':'maturation','format':'json',
                'analysis':result,'reason':'Oracolo sintetico '+case,'created_at':datetime.now(timezone.utc).isoformat()}
            body['objects']=[store.object(encoded(body).encode())];snapshot=store.save('report',body)
            cases.append({'athlete_id':a['id'],'workspace_id':entry['id'],'case':case,'snapshot':snapshot['id'],
                          'expected':'PHV esplorativo circa 8.96 cm/anno, 2024-01-01; %PAH da fonte esterna' if case=='peak' else 'Modelli indisponibili; motivi espliciti' if case=='missing' else 'Modelli adolescenti fuori dominio; HV quasi nulla'})
        entry['athletes']=len(store.list('athlete'))
        entry['measurements']=len(store.list('measurement'))
        from cycling_test.recovery import backup_bytes
        raw=backup_bytes(store)
        (destination/f'backup-societa-{index}-SOLO-DEMO.zip').write_bytes(raw)
        if index==1:(destination/'backup-SOLO-DEMO.zip').write_bytes(raw)
    manifest['growth_cases']=cases
    (destination/'manifest-demo.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Corpus SOLO DEMO creato:',destination.resolve())
    print('Le repliche iniziali non includono i nuovi casi finché non si sincronizza; non collegare al cloud operativo.')
    return cases


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--data',type=Path,required=True)
    generate_growth(parser.parse_args().data)
