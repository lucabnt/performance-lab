"""Deterministic SIMULATED recordings from the two original ERGs; no real people."""
import json
import math
import random
import struct
from datetime import datetime, timezone
from pathlib import Path
from cycling_test.erg import parse_erg

ROOT=Path(__file__).resolve().parents[1]
CASES=[
    ('SIM-ALL-01','AER-RULLO-ALL',600+6*240+105,57.5,188,'2026-03-14T09:00:00+00:00'),
    ('SIM-ALL-02','AER-RULLO-ALL',600+7*240+155,62.0,193,'2026-09-19T09:00:00+00:00'),
    ('SIM-ESO-01','AER-RULLO-ESO',600+6*240+80,43.5,192,'2026-03-15T10:00:00+00:00'),
    ('SIM-ESO-02','AER-RULLO-ESO',600+7*240+125,48.0,196,'2026-09-20T10:00:00+00:00'),
]

def crc(data):
    value=0
    for byte in data:
        value^=byte
        for _ in range(8):value=(value>>1)^(0xA001 if value&1 else 0)
    return value

def recording(family,end,maximum,seed):
    definition=parse_erg((ROOT/'examples/protocols'/f'{family}.erg').read_text(encoding='utf-8-sig'))
    randomizer=random.Random(seed);hr=88.;power=0.;rows=[]
    for t in range(end+181):
        segment=next((s for s in definition['segments'] if s['start_s']<=t<s['end_s']),definition['segments'][-1])
        target=segment['start_w'] if t<end else 40
        power+=(target-power)*.45
        # Delayed cardiovascular response, drift, breathing oscillation and cadence decline.
        target_hr=107+(maximum-107)*max(0,t-600)/max(1,end-600) if t>=600 else 100+18*(1-math.exp(-t/180))
        if t>=end:target_hr=maximum-65
        hr+=(min(maximum,target_hr)-hr)/(33 if t<end else 55)
        cadence=87+3*math.sin(t/41)-max(0,t-end+90)*.055 if t<end else 65+2*math.sin(t/20)
        rows.append({'t':t,'power':max(0,round(power+randomizer.gauss(0,2.5)+2*math.sin(t/7))),
            'hr':round(hr+1.2*math.sin(t/9)),'cadence':max(0,round(cadence+randomizer.gauss(0,1)))})
    return rows

def fit_bytes(rows,started):
    timestamp=int((datetime.fromisoformat(started)-datetime(1989,12,31,tzinfo=timezone.utc)).total_seconds())
    body=bytearray()
    # FIT file_id: activity, development manufacturer. No fabricated exporter claim.
    body.extend(bytes([0x40,0,0])+struct.pack('<H',0)+bytes([4,0,1,0,1,2,0x84,3,4,0x8c,4,4,0x86]))
    body.extend(bytes([0])+struct.pack('<B H I I',4,255,10001,timestamp))
    body.extend(bytes([0x41,0,0])+struct.pack('<H',20)+bytes([4,253,4,0x86,7,2,0x84,3,1,2,4,1,2]))
    for r in rows:body.extend(bytes([1])+struct.pack('<IHBB',timestamp+r['t'],r['power'],r['hr'],r['cadence']))
    # session start/end/elapsed/timer/sport/cycling-sub-sport.
    body.extend(bytes([0x42,0,0])+struct.pack('<H',18)+bytes([6,253,4,0x86,2,4,0x86,7,4,0x86,8,4,0x86,5,1,0,6,1,0]))
    duration=rows[-1]['t'];body.extend(bytes([2])+struct.pack('<IIIIBB',timestamp+duration,timestamp,duration*1000,duration*1000,2,6))
    header=struct.pack('<BBHI4s',14,0x20,2180,len(body),b'.FIT');header+=struct.pack('<H',crc(header))
    content=header+body
    return content+struct.pack('<H',crc(content))

def generate():
    out=ROOT/'examples/synthetic';out.mkdir(parents=True,exist_ok=True);manifest=[]
    for seed,(name,family,end,weight,maximum,date) in enumerate(CASES,1):
        rows=recording(family,end,maximum,seed);(out/f'{name}.fit').write_bytes(fit_bytes(rows,date))
        manifest.append({'file':name+'.fit','athlete_code':name,'synthetic':True,'protocol':family,'version':'originale-1',
            'date':date[:10],'effort_end_s':end,'recording_end_s':rows[-1]['t'],'weight_kg':weight,'rest_hr':58+seed,
            'rest_after_s':300,'rpe':9,'expected_map_w':130+30*((end-600)//240-1) if 'ALL' in family else 80+20*((end-600)//240-1),
            'notes':'SIMULAZIONE: non è un test reale e non valida compatibilità GoldenCheetah, MyWhoosh o Zwift.'})
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'atleti.csv').write_text('atleta_id,cognome,nome,anno_nascita,attivo,note\n'+''.join(f'{r["athlete_code"]},Simulazione,{r["athlete_code"]},{2010 if "ALL" in r["athlete_code"] else 2012},si,Dati sintetici\n' for r in manifest),encoding='utf-8')
    (out/'antropometria.csv').write_text('atleta_id,data,peso_kg,statura_cm,peso_fonte\n'+''.join(f'{r["athlete_code"]},{r["date"]},{r["weight_kg"]},,dichiarato\n' for r in manifest),encoding='utf-8')
    (out/'test_aerobico.csv').write_text('test_id,atleta_id,data,protocollo_id,map_w,peso_kg,note\n'+''.join(f'CSV-{r["athlete_code"]},{r["athlete_code"]},{r["date"]},{r["protocol"]},{r["expected_map_w"]},{r["weight_kg"]},SIMULAZIONE senza campioni\n' for r in manifest),encoding='utf-8')
    return manifest

if __name__=='__main__':
    for item in generate():print(item['file'],item['expected_map_w'],'W',item['effort_end_s'],'s')
