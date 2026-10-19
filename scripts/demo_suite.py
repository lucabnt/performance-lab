"""Seeded, entirely fictional multi-archive acceptance corpus. Never opens real data."""
import argparse
import csv
import io
import json
import math
import random
import struct
from pathlib import Path
from copy import deepcopy
from datetime import date
from cycling_test.store import Store,encoded
from cycling_test.workspaces import Workspaces,invitation,join
from cycling_test.sync import exchange
from cycling_test.sync_service import configure
from cycling_test.api import Settings
from cycling_test.erg import parse_erg
from cycling_test.fit import decode_fit
from cycling_test.csv_import import plan_import,decode_trace_csv
from cycling_test.analysis import analyze
from cycling_test.observations import enrich
from cycling_test.anaerobic import Protocol as AnaProtocol,Settings as AnaSettings,analyze as anaerobic,CSV_HEADER
from cycling_test.custom_fields import attach
from cycling_test.methods import DEFAULT,identity
from cycling_test.specialist import gas_analysis
from generate_examples import fit_bytes,recording,crc
from demo_reset import reset_notice

ROOT=Path(__file__).resolve().parents[1]
PASSWORD='SoloDemo-NonUsareInProduzione-2026'
MARKER='SIMULAZIONE: persone, misure e risultati interamente fittizi; nessuna validazione scientifica.'

def csv_bytes(header,rows):
    out=io.StringIO(newline='');w=csv.DictWriter(out,fieldnames=header.split(','));w.writeheader();w.writerows({k:r.get(k,'') for k in header.split(',')} for r in rows);return out.getvalue().encode('utf-8')

def generate(destination,small=False):
    destination=Path(destination).resolve()
    # Refuse even an empty existing destination: no accidental merge or overwrite.
    if destination.exists():raise ValueError('La destinazione deve essere nuova. Nessun archivio viene sovrascritto.')
    destination.mkdir(parents=True);fixtures=destination/'fixtures';fixtures.mkdir();rng=random.Random(481516)
    manager=Workspaces(destination,Store(destination));entries=[manager.create(n,'Fondatore demo') for n in ('Velodromo Aurora - SIMULAZIONE','Pedale del Lago - SIMULAZIONE')]
    stores=[manager.get(e['id']) for e in entries];orgs=[s.list('organization')[0] for s in stores]
    manifest={'schema':1,'seed':481516,'synthetic':True,'description':MARKER,'primary_root':str(destination),'organizations':[], 'cases':[], 'credentials_note':'Password degli inviti SOLO DEMO: '+PASSWORD}
    def write(name,raw):
        path=fixtures/name;path.write_bytes(raw);return str(path.relative_to(destination))
    def trace(s,raw,csv_trace=False,**options):
        decoded=decode_trace_csv(raw) if csv_trace else decode_fit(raw,**options)
        original=s.object(raw);decoded['original_hash']=original;h=s.object(encoded(decoded).encode());return decoded,h,[h,original]
    all_athletes=[];comparison_pairs=[]
    names=[('Giulia','Riva','F',2010),('Matteo','Ferri','M',2010),('Elena','Moretti','F',2012),('Andrea','Villa','M',2012),('Sofia','Conti','F',2008),('Luca','Marini','M',2008),('Chiara','Galli','F',2005),('Davide','Rossi','M',2005),('Sara','Leoni','F',1995),('Paolo','Sala','M',1990),('Andrea','Villa','M',2011),('Arianna','Neri','F',None),('Nicolò','Costa','M',2013),('Alice','Fontana','F',2011),('Tommaso','Serra','M',2007),('Martina','Greco','F',2009),('Simone','Colombo','M',2006),('Beatrice','Riva','F',2014)]
    for company,(s,org) in enumerate(zip(stores,orgs)):
        count=(4 if small else 18) if company==0 else (2 if small else 6)
        groups={};parents={};protocols={}
        for category in ('Giovanissimi','Esordienti','Allievi','Juniores','Under 23','Amatori'):
            parents[category]=s.save('group',{'organization_id':org['id'],'name':category,'season':'','parent_id':None})
            for year in (2024,2025,2026):groups[category,year]=s.save('group',{'organization_id':org['id'],'name':category,'season':str(year),'parent_id':parents[category]['id']})
        extension=[{'key':'ambiente_c','label':'Temperatura ambiente','type':'number','unit':'°C','scope':'test','minimum':5,'maximum':45}, {'key':'sonno_ore','label':'Sonno precedente','type':'number','unit':'h','scope':'test','minimum':0,'maximum':16}, {'key':'modello_rullo','label':'Modello rullo','type':'text','scope':'protocol','unit':''}]
        for family in ('AER-RULLO-ALL','AER-RULLO-ESO'):
            raw=(ROOT/f'examples/protocols/{family}.erg').read_bytes();definition=parse_erg(raw.decode('utf-8-sig'))
            for stage in definition['segments']:stage['phase']='warmup' if stage['end_s']<=600 else 'increment'
            protocols[family]=s.save('protocol',{'organization_id':org['id'],'name':family+' laboratorio','family':family,'version':'1','definition':definition,'custom_fields':extension,'custom_values':{'modello_rullo':'Rullo laboratorio SIMULATO'},'objects':[s.object(raw)],'status':'active'})
        catalog=s.save('protocol',{'organization_id':org['id'],'name':'Incrementale storico senza programma','family':'AER-STORICO','version':'1','definition':{'points':[],'segments':[],'duration_s':0},'status':'active','custom_fields':[],'objects':[]})
        ana={}
        for family in ('sprint','wingate30','wingate15'):
            spec=AnaProtocol(organization_id=org['id'],name={'sprint':'Sprint lanciato 6 s','wingate30':'Wingate 30 s laboratorio','wingate15':'Wingate 15 s 0,70 N·m/kg'}[family],family=family,device='Ergometro DEMO con misuratore 1 Hz',start='flying',position='seated',warmup='10 min progressivi + 2 accelerazioni, simulazione',torque_nm_kg=.70 if family=='wingate15' else None).model_dump()
            ana[family]=s.save('protocol',{'organization_id':org['id'],'name':spec['name'],'family':family,'version':'1','test_type':family,'anaerobic_spec':spec,'definition':{'points':[],'segments':[],'duration_s':spec['duration_s']},'status':'active','objects':[],'custom_fields':[{'key':'carico_percepito','label':'Difficoltà percepita','type':'number','unit':'CR10','scope':'test','minimum':0,'maximum':10}]})
        old=ana['wingate15'];new=deepcopy(old);new.pop('id');new.pop('revision');new.update(version='2',parent_id=old['id'],reason='Finestra del picco portata a 5 s: confronto separato');new['anaerobic_spec'].update(peak_window_s=5,version='2');ana['wingate15-v2']=s.save('protocol',new)
        custom=s.save('protocol',{'organization_id':org['id'],'name':'Sprint ripetuti 5 × 6 s - osservazioni','family':'CUSTOM-RSA','version':'1','test_type':'custom','description':'Cinque sprint con recupero dichiarato. Risultati inseriti dal valutatore; nessuna stima automatica della capacità anaerobica. '+MARKER,'status':'active','definition':{'points':[],'segments':[],'duration_s':0},'objects':[], 'custom_fields':[{'key':'ripetizioni','label':'Numero di ripetizioni','type':'number','scope':'protocol','unit':'','minimum':1,'maximum':20},{'key':'picco_migliore','label':'Migliore picco dichiarato','type':'number','scope':'test','unit':'W','minimum':0,'maximum':3000},{'key':'calo_ultima','label':'Calo nell’ultima ripetizione','type':'number','scope':'test','unit':'%','minimum':0,'maximum':100},{'key':'completato','label':'Tutte le ripetizioni completate','type':'boolean','scope':'test','unit':''},{'key':'recupero','label':'Tipo di recupero','type':'choice','choices':['Attivo','Passivo'],'scope':'test','unit':''}], 'custom_values':{'ripetizioni':5}})
        previous=s.save('protocol',{**protocols['AER-RULLO-ALL'],'version':'0','status':'archived','reason':'Versione precedente conservata per testare archivio/ripristino.'})
        s.save('default_profile',{'organization_id':org['id'],'source':'Valori fittizi per collaudare la scelta esplicita di una stima','population':'SOLO DEMO, non usare su atleti reali','weight_kg':58,'height_cm':168})
        preset=deepcopy(DEFAULT);preset.pop('id');preset.update(name='Step con tolleranza 10 W - DEMO',family='incremental-demo',version='1',reason=MARKER);preset['parameters']['adherence_tolerance_w']=10;s.save('analysis_preset',preset)
        athletes=[]
        for i in range(count):
            given,surname,sex,birth=names[(i+company*5)%len(names)];external=f'SIM-{company+1}-{i+1:03}'
            status='archived' if i==count-2 else 'deleted' if i==count-1 else 'active'
            athlete=s.save('athlete',{'organization_id':org['id'],'name':given,'surname':surname,'sex':sex,'birth_year':birth,'birth_confirmed':birth is not None and i%5!=0,'birth_source':'Scenario sintetico','status':status,'external_id':external,'notes':MARKER+(' Atleta inattivo da settembre 2026.' if status=='archived' else '')});athletes.append(athlete);all_athletes.append(athlete)
            base_mass=(44+(i%7)*4+company*3) if birth and birth>=2008 else 65+(i%5)*3
            for year in (2024,2025,2026):
                age=year-birth if birth else None;category='Giovanissimi' if age and age<=12 else 'Esordienti' if age and age<=14 else 'Allievi' if age and age<=16 else 'Juniores' if age and age<=18 else 'Under 23' if age and age<=22 else 'Amatori'
                if birth:s.save('membership',{'athlete_id':athlete['id'],'group_id':groups[category,year]['id'],'start':f'{year}-01-01','end':f'{year}-12-31','category_year':1 if age in (13,15,17) else 2 if age in (14,16,18) else None})
                for month in (2,6,10):
                    s.save('measurement',{'athlete_id':athlete['id'],'date':f'{year}-{month:02}-01','weight_kg':round(base_mass+(year-2024)*1.1+(month-6)*.07,1),'height_cm':None if i%6==0 else round(155+(i%7)*3+(year-2024)*(1.7 if birth and birth>=2008 else 0),1),'source':'arrotondato' if month==2 and i%4==0 else 'misurato'})
                if i in (count-1,count-3):continue
                family='AER-RULLO-ESO' if birth and birth>=2011 else 'AER-RULLO-ALL';p=protocols[family];end=600+(4+(i%3)+(year-2024))*240+85+(i%4)*25
                weight=round(base_mass+(year-2024)*1.1,1)
                settings=Settings(offset_s=0,end_s=end,weight_kg=None if i%8==7 else weight,height_cm=None,weight_source='stimato' if i==5 else 'misurato',rest_hr=53+i%12,rest_after_s=300,rpe=8+(i%3)*.5,threshold_w=round(2.7*weight) if i%3==0 else None,fthr_bpm=172+i%10 if i%3==0 else None,conditions={'device':'Rullo DEMO','calibration':'Simulata','posture':'seduto','recovery_mode':'passivo'},custom_values={'ambiente_c':19+year%3+i%4,**({'sonno_ore':round(6.5+(i%4)*.5,1)} if i%3 else {})}).model_dump()
                if i==0 and year==2025:
                    from cycling_test.zones import preset as zone_preset
                    scheme={'name':'Potenza 7 zone DEMO','version':'1','channel':'power','reference':'threshold_w','zones':[{'name':f'Z{j+1}','upper':bound,'inclusive':True} for j,bound in enumerate([55,75,90,105,120,150])]+[{'name':'Z7','upper':None,'inclusive':False}]}
                    settings['zone_schemes']=[scheme,zone_preset('hr')]
                if i<2:
                    rows=recording(family,end,185+i%10,1000*company+100*i+year)
                    if year==2025 and i==1:
                        rows=[r for r in rows if not 1200<=r['t']<1210]
                        for r in rows:
                            if 900<=r['t']<906:r['power']=65535
                            if 1000<=r['t']<1030:r['hr']=255
                    raw=fit_bytes(rows,f'{year}-03-15T09:00:00+00:00');filename=f'{external}-{year}-incrementale.fit';write(filename,raw);decoded,h,objects=trace(s,raw)
                    settings['lactate']=[{'at_s':840+j*240,'step_number':j+2,'mmol_l':v,'delay_s':0,'note':'Prelievo simulato'} for j,v in enumerate([1.1,1.3,2.0,3.4,5.8,8.0]) if 840+j*240<=end]
                    analysis=enrich(analyze(decoded['samples'],p['definition'],settings),decoded['samples'],settings)
                    if i==0 and year==2026:
                        gas=[{'t':t,'vo2':.65+2.4*min(1,max(0,t-600)/(end-600)),'vco2':.55+2.9*min(1,max(0,t-600)/(end-600)),'ve':20+70*min(1,max(0,t-600)/(end-600)),'peto2':103+4*max(0,t-end*.7)/end,'petco2':38-3*max(0,t-end*.75)/end} for t in range(end+1)]
                        analysis['gas']=gas_analysis(gas,settings,analysis);gas_raw='t,vo2_l_min,vco2_l_min,ve_l_min,peto2_mmhg,petco2_mmhg\n'+'\n'.join(','.join(str(r[k]) for k in ('t','vo2','vco2','ve','peto2','petco2')) for r in gas)
                        write('gas-simulati.csv',gas_raw.encode());gh=s.object(gas_raw.encode());gn=s.object(encoded({'kind':'gas','samples':gas,'original_hash':gh}).encode());settings['gas_hash']=gn;objects += [gh,gn]
                    payload={'trace_hash':h,'samples':decoded['samples'],'objects':objects,'historical':False,'entry_source':'trace'}
                    manifest['cases'].append({'case':filename,'path':'fixtures/'+filename,'expected':'Lacune potenza/FC e warning' if year==2025 and i==1 else 'Incrementale con step, recupero e lattato','offset_s':0,'end_s':end,'external_athlete':external})
                else:
                    map_w=round((3.4+i%5*.25+(year-2024)*.08)*weight);analysis=enrich({'map_w':map_w,'map_alt_w':None,'map_wkg':map_w/weight,'fc_max_test_bpm':None if i%4==0 else 182+i%12,'duration_s':end,'steps':[],'recovery':[],'power_coverage':None,'engine':'manual-1','warnings':['Risultati sintetici dichiarati senza tracciato.'],'method':'Riepilogo manuale'},[],settings);payload={'trace_hash':None,'samples':[],'objects':[],'historical':True,'entry_source':'manuale'}
                if analysis.get('gas'):analysis=enrich(analysis,payload['samples'],settings)
                analysis=attach(analysis,p,settings)
                test=s.save('test',{**payload,'organization_id':org['id'],'athlete_id':athlete['id'],'athlete_snapshot':athlete,'date':f'{year}-03-15','protocol_id':p['id'],'settings':settings,'analysis':analysis,'notes':MARKER,'external_id':f'{external}-AER-{year}','group_ids':[]})
                if i==0 and year==2024:
                    test=s.save('test',{**test,'notes':MARKER+' Nota corretta: sensore FC verificato nel caso simulato.','reason':'Correzione dimostrativa con revisione conservata.'},test['id'],test['revision'])
                if i==4 and year==2024:s.save('test',{**test,'status':'deleted','reason':'Eliminazione logica dimostrativa, record originale conservato.'},test['id'],test['revision'])
                if year==2026 and i<2:
                    repeat=s.save('test',{**test,'date':'2026-03-18','external_id':f'{external}-RETEST','notes':MARKER+' Ripetizione in condizioni mantenute stabili.'});comparison_pairs.append({'first':test['id'],'second':repeat['id']})
            if status=='deleted' or i==count-3:continue
            for family in ('sprint','wingate30','wingate15','wingate15-v2'):
                p=ana[family];duration=p['anaerobic_spec']['duration_s'];weight=base_mass+2.2
                settings=AnaSettings(offset_s=60,weight_kg=weight,weight_source='dichiarato' if i%5==0 else 'misurato',custom_values={'carico_percepito':8+i%3}).model_dump()
                if i<3:
                    rows=[];peak=weight*(11.5+(i%6)*.6)
                    for t in range(60+int(duration)+91):
                        e=t-60;power=100 if e<0 else 55 if e>=duration else peak*(1-math.exp(-(e+1)/.65))*math.exp(-e/(duration*1.45))
                        rows.append({'t':t,'power':round(power+rng.uniform(-2,2)),'hr':round(103+55*(1-math.exp(-max(0,t-40)/35))),'cadence':round(80 if e<0 or e>=duration else 145-40*e/duration)})
                    if i==2 and family=='wingate15':rows=[r for r in rows if not 66<=r['t']<70]
                    raw=fit_bytes(rows,'2026-06-10T09:00:00+00:00');filename=f'{external}-{family}.fit';write(filename,raw);decoded,h,objects=trace(s,raw);a=anaerobic(decoded['samples'],p['anaerobic_spec'],settings);payload={'trace_hash':h,'samples':decoded['samples'],'objects':objects,'historical':False,'entry_source':'trace'}
                    manifest['cases'].append({'case':filename,'path':'fixtures/'+filename,'offset_s':60,'expected':'Copertura incompleta, media non disponibile' if i==2 and family=='wingate15' else 'Prova all-out; versione 2 separa finestra 5 s'})
                else:
                    from cycling_test.anaerobic import finish
                    peak=round(weight*(11+i%7*.7));mean=round(peak*(.87 if family=='sprint' else .68 if family=='wingate30' else .77));a=finish({'peak_w':peak,'mean_w':mean,'work_kj':mean*duration/1000,'end_power_w':round(mean*.85),'cadence_max_rpm':140+i%15,'fc_max_test_bpm':None if i%3==0 else 165+i%12},p['anaerobic_spec'],settings,'manual');payload={'trace_hash':None,'samples':[],'objects':[],'historical':True,'entry_source':'manuale'}
                s.save('test',{**payload,'organization_id':org['id'],'athlete_id':athlete['id'],'athlete_snapshot':athlete,'date':'2026-06-10','test_type':p['test_type'],'protocol_id':p['id'],'settings':settings,'analysis':attach(a,p,settings),'notes':MARKER,'group_ids':[]})
            for year in (2025,2026):
                settings={'offset_s':0,'end_s':None,'weight_kg':base_mass,'weight_source':'misurato','conditions':{},'custom_values':{'picco_migliore':round(base_mass*(11.8+(year-2025)*.3)),'recupero':'Passivo','completato':False if i%5==0 else True,**({'calo_ultima':14+i%10} if i%4 else {})},'extra_fields':[]}
                a=attach({'engine':'custom-1','source':'manual','protocol_snapshot':custom,'method':'Risultati custom dichiarati. '+MARKER,'steps':[],'recovery':[],'zones':[],'warnings':[],'duration_s':None},custom,settings)
                s.save('test',{'organization_id':org['id'],'athlete_id':athlete['id'],'athlete_snapshot':athlete,'date':f'{year}-09-12','protocol_id':custom['id'],'test_type':'custom','settings':settings,'analysis':a,'trace_hash':None,'samples':[],'objects':[],'historical':True,'entry_source':'manuale','notes':MARKER,'group_ids':[]})
        from cycling_test.methods import RAMP
        for shape in ('rampa','discontinuo'):
            segments=[{'start_s':0,'end_s':300,'start_w':60,'end_w':60,'phase':'warmup'}, {'start_s':300,'end_s':750,'start_w':100,'end_w':220 if shape=='rampa' else 100,'phase':'increment'}, {'start_s':750,'end_s':1200,'start_w':220 if shape=='rampa' else 180,'end_w':340 if shape=='rampa' else 180,'phase':'increment'}]
            definition={'points':[[t,w] for r in segments for t,w in ((r['start_s'],r['start_w']),(r['end_s'],r['end_w']))],'segments':segments,'duration_s':1200}
            p=s.save('protocol',{'organization_id':org['id'],'name':shape.title()+' descrittiva DEMO','family':'AER-'+shape.upper(),'version':'1','definition':definition,'status':'active','objects':[]})
            samples=[]
            for t in range(1321):
                r=next((r for r in segments if r['start_s']<=t<r['end_s']),segments[-1]);power=r['start_w']+(r['end_w']-r['start_w'])*(min(t,r['end_s'])-r['start_s'])/(r['end_s']-r['start_s']) if t<1200 else 40
                samples.append({'t':t,'power':round(power+2*math.sin(t/13)),'hr':round(95+85*min(t,1200)/1200-40*max(0,t-1200)/120),'cadence':85 if t<1200 else 60})
            raw=csv_bytes('t,power,hr,cadence',samples);write(f'{shape}-descrittiva.csv',raw);decoded,h,objects=trace(s,raw,csv_trace=True)
            settings=Settings(end_s=1200,weight_kg=58,preset_id=RAMP['id'],excluded_intervals=[{'start_s':620,'end_s':623,'reason':'Artefatto simulato'}],conditions={'device':'Rullo DEMO','stop_reason':'Fine protocollo simulata'}).model_dump()
            a=enrich(analyze(decoded['samples'],definition,settings,RAMP),decoded['samples'],settings)
            s.save('test',{'organization_id':org['id'],'athlete_id':athletes[0]['id'],'athlete_snapshot':athletes[0],'date':'2026-10-01','protocol_id':p['id'],'settings':settings,'analysis':a,'trace_hash':h,'samples':decoded['samples'],'objects':objects,'historical':False,'entry_source':'trace','notes':MARKER,'group_ids':[]})
            manifest['cases'].append({'case':shape,'path':f'fixtures/{shape}-descrittiva.csv','expected':'Risultati descrittivi terminali, MAP operativa non attribuita','end_s':1200})
        # CSV workflows: existing IDs exercise reconciliation/idempotence; one new
        # athlete and test exercise atomic import independently of the seeded set.
        write(f'societa-{company+1}-atleti.csv',csv_bytes('atleta_id,cognome,nome,anno_nascita,anno_nascita_confermato,sesso,attivo,note',[{'atleta_id':a['external_id'],'cognome':a['surname'],'nome':a['name'],'anno_nascita':a.get('birth_year'),'anno_nascita_confermato':'si' if a.get('birth_confirmed') else 'no','sesso':a['sex'],'attivo':'no' if a['status']=='archived' else 'si','note':MARKER} for a in athletes if a['status']!='deleted']))
        historical=[{'test_id':f'SIM-HIST-{company}-{i}','atleta_id':a['external_id'],'data':'2024-07-20','protocollo_id':'ANA-15-070','peso_kg':60+i*3,'peso_fonte':'derivato' if i==1 else 'misurato','picco_w':850+i*70,'media_w':660+i*40,'indice_fatica_ws':17+i,'tempo_picco_s':2.1,'end_power_w':480+i*30,'lavoro_kj':10.12+i*.6,'segnale_fc_interrotto':'si' if i==1 else 'no','note':MARKER} for i,a in enumerate([a for a in athletes if a['status']!='deleted'][:2])]
        raw=csv_bytes(CSV_HEADER,historical);write(f'societa-{company+1}-wingate-storico.csv',raw);plan=plan_import(s,org['id'],'test_anaerobico',raw)
        if plan['errors']:raise ValueError(plan['errors'])
        records=s.save_batch(plan['entries']);s.save('import_batch',{'organization_id':org['id'],'profile':'test_anaerobico','hash':s.object(raw),'objects':[s.object(raw)],'record_ids':[r['id'] for r in records]})
        manifest['organizations'].append({'id':entries[company]['id'],'organization_id':org['id'],'name':org['name'],'athletes':len(athletes),'tests':len(s.list('test')),'protocols':len(s.list('protocol'))})
        print(f"Preparata {org['name']}: {len(athletes)} atleti, {len(s.list('test'))} prove.",flush=True)
    # Invalid fixtures are separate, never silently committed to the demo.
    write('import-atleti-nuovi.csv',csv_bytes('atleta_id,cognome,nome,anno_nascita,attivo,note',[{'atleta_id':'SIM-NUOVO-01','cognome':'Esempio','nome':'Nuovo atleta','anno_nascita':2011,'attivo':'si','note':MARKER}]))
    write('import-antropometria.csv',b'atleta_id,data,peso_kg,statura_cm,peso_fonte\nSIM-NUOVO-01,2026-10-01,55.4,168.5,misurato\nSIM-NUOVO-01,2026-10-10,55.6,,dichiarato\n')
    write('import-aerobico.csv',b'test_id,atleta_id,data,protocollo_id,map_w,peso_kg,note\nSIM-IMPORT-AER-01,SIM-NUOVO-01,2026-10-10,AER-IMPORT,230,55.6,SIMULAZIONE\n')
    write('import-errori.csv',b'test_id,atleta_id,data,protocollo_id,map_w,peso_kg\nSIM-ERR-1,INESISTENTE,2026-10-10,AER-IMPORT,200,55\nSIM-ERR-2,SIM-NUOVO-01,data-errata,AER-IMPORT,abc,-4\n')
    rows=[{'t':i,'power':500+round(200*math.sin(i/12)),'hr':140+i%25,'cadence':90+i%10} for i in range(181)]
    raw=fit_bytes(rows,'2026-10-01T10:00:00+00:00');write('fit-crc-corrotto.fit',raw[:-2]+b'\x00\x00')
    duplicates=rows[:20]+[{**rows[19],'power':900}]+rows[20:];write('fit-timestamp-duplicati.fit',fit_bytes(duplicates,'2026-10-01T10:00:00+00:00'))
    # Two session messages reference the same recording in this deterministic
    # decoder fixture. Selecting a session is mandatory; not two real rides.
    body=raw[14:-2];session_definition=bytes([0x43,0,0])+struct.pack('<H',18)+bytes([6,253,4,0x86,2,4,0x86,7,4,0x86,8,4,0x86,5,1,0,6,1,0])
    from datetime import datetime,timezone
    epoch=int((datetime(2026,10,1,10,tzinfo=timezone.utc)-datetime(1989,12,31,tzinfo=timezone.utc)).total_seconds());body+=session_definition+bytes([3])+struct.pack('<IIIIBB',epoch+180,epoch+60,120000,120000,2,6);header=struct.pack('<BBHI4s',14,0x20,2180,len(body),b'.FIT');header+=struct.pack('<H',crc(header));packet=header+body;write('fit-due-sessioni.fit',packet+struct.pack('<H',crc(packet)))
    write('tracciato-pausa.csv',b't,power,hr,cadence,paused\n0,100,100,80,false\n1,105,101,81,false\n2,0,100,0,true\n3,0,99,0,true\n4,500,130,120,false\n5,700,135,130,false\n6,600,140,125,false\n')
    # Include growth snapshots before invitations, exchange and backups.
    from demo_growth import add_growth
    add_growth(destination,manifest)
    # Real per-device identities; only local encrypted folder exchange. No cloud
    # credentials, real OAuth registrations or plaintext production identity.
    main=stores[0];channel=destination/'scambio';channel.mkdir();configure(main,{'transport':'folder','folder':str(channel)})
    replicas={}
    for role in ('admin','viewer'):
        path=destination/'repliche'/role;manager_replica=Workspaces(path,Store(path));raw=invitation(main,role.title()+' DEMO',role,PASSWORD);entry=join(manager_replica,raw,PASSWORD);replica=manager_replica.get(entry['id']);replicas[role]=replica;configure(replica,{'transport':'folder','folder':str(channel)});(destination/f'invito-{role}-SOLO-DEMO.json').write_bytes(raw)
    from cycling_test.workspaces import unseal,revoke_member
    revoked=invitation(main,'Accesso revocato DEMO','viewer',PASSWORD);revoked_id=unseal(revoked,PASSWORD)['identity']['certificate']['id'];revoke_member(main,revoked_id)
    (destination/'invito-revocato-SOLO-DEMO.json').write_bytes(revoked)
    print('Preparo repliche admin/viewer e canale locale cifrato…',flush=True)
    exchange(main,channel,main.identity['sync_key'])
    for replica in replicas.values():exchange(replica,channel,replica.identity['sync_key'])
    # Offline conflicting edits are left pending in owner/admin for deliberate
    # user-controlled sync. Viewer starts from a consistent received archive.
    athlete=next(a for a in main.list('athlete') if a['status']=='active');old=replicas['admin'].get(athlete['id'])
    main.save('athlete',{**athlete,'notes':MARKER+' Modifica offline del fondatore.'},athlete['id'],athlete['revision'])
    replicas['admin'].save('athlete',{**old,'notes':MARKER+' Modifica concorrente offline dell’admin.'},old['id'],old['revision'])
    from cycling_test.recovery import backup_bytes,export_recovery
    (destination/'backup-SOLO-DEMO.zip').write_bytes(backup_bytes(main));(destination/'recupero-SOLO-DEMO.json').write_bytes(export_recovery(main,PASSWORD))
    for i,s in enumerate(stores,1):(destination/f'backup-societa-{i}-SOLO-DEMO.zip').write_bytes(backup_bytes(s))
    manifest.update(replicas={role:str(replica.root.parent.parent) for role,replica in replicas.items()},exchange_folder=str(channel),conflict_athlete=athlete['id'],repeatability_pairs=comparison_pairs,cases=manifest['cases']+[{'case':'fit-due-sessioni.fit','expected':'Ispezione: 2 sessioni; import senza selezione rifiutato'},{'case':'fit-timestamp-duplicati.fit','expected':'Rifiutato; keep_last consentito soltanto con motivo'},{'case':'fit-crc-corrotto.fit','expected':'CRC invalido, rifiuto'},{'case':'import-errori.csv','expected':'Lotto bloccato, nessuna riga salvata'},{'case':'repliche','expected':'Viewer in sola lettura; scambio owner/admin crea conflitto da risolvere'}])
    (destination/'manifest-demo.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    add_oracles(destination)
    (destination/'LEGGIMI-DEMO.md').write_text('# Corpus interamente sintetico\n\n'+MARKER+'\n\nAvvia la GUI sulla radice indicata nel manifest. Le repliche admin/viewer sono archivi separati e usano la stessa cartella locale scambio. Gli inviti hanno password pubblica SOLO DEMO `'+PASSWORD+'`. Non collegare il corpus a destinazioni operative.\n\nI casi di errore sono in fixtures e non vengono importati automaticamente. Manifest con conteggi, offset/fine sforzo, coppie di ripetibilità e risultati attesi.\n',encoding='utf-8')
    return json.loads((destination/'manifest-demo.json').read_text(encoding='utf-8'))

def add_oracles(root):
    """Independent numerical checks, deliberately simpler than realistic traces."""
    root=Path(root);path=root/'manifest-demo.json';manifest=json.loads(path.read_text(encoding='utf-8'))
    if manifest.get('synthetic') is not True:raise ValueError('Corpus non marcato come sintetico.')
    fixtures=root/'fixtures'
    (fixtures/'oracolo-wingate15-costante.csv').write_bytes(csv_bytes('t,power,hr,cadence',[{'t':i,'power':500,'hr':150,'cadence':100} for i in range(16)]))
    (fixtures/'oracolo-incrementale.csv').write_bytes(csv_bytes('t,power,hr,cadence',[{'t':i,'power':100 if i<60 else 150 if i<120 else 200,'hr':120 if i<60 else 140 if i<120 else 160,'cadence':90} for i in range(181)]))
    (fixtures/'oracolo-incrementale.erg').write_text('[COURSE HEADER]\nVERSION = 2\nMINUTES WATTS\n[END COURSE HEADER]\n[COURSE DATA]\n0 100\n1 100\n1 150\n2 150\n2 200\n3 200\n[END COURSE DATA]\n',encoding='utf-8')
    oracle={'note':'Valori attesi dedotti dalle costanti di costruzione, non dal motore analitico. File didattici semplificati separati dalle simulazioni realistiche.',
            'wingate15':{'file':'oracolo-wingate15-costante.csv','offset_s':0,'duration_s':15,'weight_kg':50,'peak_window_s':1,'end_window_s':1,'expected':{'peak_w':500,'mean_w':500,'work_kj':7.5,'peak_wkg':10,'mean_wkg':10,'fatigue_pct':0,'decline_ws':0,'time_to_peak_s':0,'power_coverage':1}},
            'incremental':{'erg':'oracolo-incrementale.erg','file':'oracolo-incrementale.csv','warmup_s':0,'end_s':150,'weight_kg':50,'expected':{'map_w':150,'map_wkg':3,'map_alt_w':175}},
            'aggregation':{'values':[700,700,1300],'mode':'tests','expected':{'mean':900,'median':700,'n':3},'note':'Inserire tre osservazioni nel medesimo campo/protocollo/metodo; scegliere Tutti i test.'}}
    (root/'oracoli-numerici.json').write_text(json.dumps(oracle,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    existing={c['case'] for c in manifest['cases']}
    for name in ('oracolo-wingate15-costante.csv','oracolo-incrementale.csv'):
        if name not in existing:manifest['cases'].append({'case':name,'path':'fixtures/'+name,'expected':'Vedere oracoli-numerici.json; controllo numerico indipendente.'})
    path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return oracle

def export_portable(root,output):
    """Backups for independent restore, without live identities or absolute registry."""
    import zipfile
    from cycling_test.recovery import backup_bytes
    root=Path(root).resolve();manifest=json.loads((root/'manifest-demo.json').read_text(encoding='utf-8'))
    if manifest.get('synthetic') is not True or manifest.get('seed')!=481516:raise ValueError('Esportazione consentita soltanto per il corpus sintetico marcato.')
    manager=Workspaces(root,Store(root));output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        for i,org in enumerate(manifest['organizations'],1):z.writestr(f'backups/societa-{i}-SOLO-DEMO.zip',backup_bytes(manager.get(org['id'])))
        for path in sorted((root/'fixtures').iterdir()):
            if path.is_file() and path.suffix.lower() in ('.fit','.csv','.erg'):z.write(path,'fixtures/'+path.name)
        if (root/'oracoli-numerici.json').exists():z.write(root/'oracoli-numerici.json','oracoli-numerici.json')
        for path in (ROOT/'examples/protocols').glob('*.erg'):z.write(path,'protocolli/'+path.name)
        z.writestr('LEGGIMI.md','# Dati interamente sintetici\n\n'+MARKER+'\n\nNell’app: Gestisci società → Apri backup → Copia indipendente. Importare separatamente i due ZIP in backups e assegnare un fondatore dimostrativo. Non usare recupero originale né collegare cloud operativi. I file in fixtures includono casi validi e casi deliberatamente errati; non sono tutti importabili. Per le repliche Admin/Viewer e il conflitto offline rigenerare il corpus da sorgenti con scripts/demo_suite.py.\n')
        safe={'synthetic':True,'seed':manifest['seed'],'organizations':[{k:v for k,v in org.items() if k not in ('id','organization_id')} for org in manifest['organizations']], 'cases':manifest['cases'],'growth_cases':[{k:v for k,v in case.items() if k not in ('athlete_id','workspace_id','snapshot')} for case in manifest.get('growth_cases',[])]}
        z.writestr('manifest.json',json.dumps(safe,ensure_ascii=False,indent=2))
    return output

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--data',default='.local/demo-suite-08');parser.add_argument('--small',action='store_true',help='Corpus ridotto per test automatici')
    parser.add_argument('--reset',action='store_true',help='Conserva la vecchia cartella in .local/demo-backups e rigenera il corpus (solo destinazioni dirette in .local).')
    parser.add_argument('--export',metavar='ZIP',help='Dopo la generazione crea uno ZIP portabile con backup e fixture.')
    args=parser.parse_args()
    try:
        if args.reset:reset_notice(args.data)
        manifest=generate(args.data,args.small)
    except ValueError as exc:
        raise SystemExit(str(exc)+' Per ripopolare una demo esistente chiudere app/server e usare --reset.') from None
    if args.export:print('Demo portabile:',export_portable(args.data,args.export))
    print(json.dumps({'root':manifest['primary_root'],'organizations':manifest['organizations'],'fixture_cases':len(manifest['cases'])},ensure_ascii=False,indent=2))
