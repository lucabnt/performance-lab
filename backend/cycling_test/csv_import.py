"""Strict CSV profiles: preview before atomic commit, stable external IDs."""
import csv
import io
import hashlib
from datetime import date
from uuid import uuid5, NAMESPACE_URL

SCHEMAS = {
    'atleti': {'required':['atleta_id','cognome','nome'], 'rule':'Nome e cognome obbligatori; gli altri campi sono facoltativi.'},
    'antropometria': {'required':['atleta_id','data'], 'rule':'Almeno peso_kg oppure statura_cm; peso_fonte facoltativo (dichiarato).'},
    'test_aerobico': {'required':['test_id','atleta_id','data','protocollo_id'], 'rule':'Risultati facoltativi: i valori assenti restano vuoti, mai zero.'},
}


def read(raw):
    text = raw.decode('utf-8-sig')
    if not text.strip(): raise ValueError('CSV vuoto.')
    delimiter = ';' if text.splitlines()[0].count(';') > text.splitlines()[0].count(',') else ','
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    if not reader.fieldnames or len(reader.fieldnames)!=len(set(reader.fieldnames)):
        raise ValueError('Intestazioni CSV mancanti o duplicate.')
    rows=list(reader)
    if any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError('Numero di colonne incoerente: controllare delimitatori e virgolette.')
    return rows


def number(value):
    import math
    if value is None or str(value).strip()=='':
        return None
    v = float(str(value).replace(',','.'))
    if not math.isfinite(v):
        raise ValueError('Valore numerico non finito.')
    return v


def decode_trace_csv(raw):
    rows = read(raw)
    samples = []
    for i,r in enumerate(rows,2):
        t = number(r.get('t',r.get('tempo_s')))
        if t is None or t<0 or samples and t<=samples[-1]['t']:
            raise ValueError(f'Riga {i}: tempo in secondi mancante, duplicato o non crescente.')
        values = {k:number(r.get(k,r.get(alias))) for k,alias in [('power','potenza_w'),('hr','fc_bpm'),('cadence','cadenza_rpm')]}
        if any(v is not None and v<0 for v in values.values()):
            raise ValueError(f'Riga {i}: campione negativo.')
        samples.append({'t':t,**values,'paused':r.get('paused','').lower() in ('true','1','si')})
    if len(samples)<2:
        raise ValueError('Servono almeno due campioni.')
    return {'samples':samples,'duration_s':samples[-1]['t'],'started_at':'','warnings':[], 'source':'CSV secondi/W/bpm/rpm'}


def plan_import(store, org, profile, raw):
    from .api import Athlete, Measurement
    if profile not in ('atleti','antropometria','test_aerobico'):
        raise ValueError('Profilo CSV non supportato.')
    rows = read(raw)
    text=raw.decode('utf-8-sig')
    headers=next(csv.reader(io.StringIO(text),delimiter=';' if text.splitlines()[0].count(';')>text.splitlines()[0].count(',') else ','))
    missing=set(SCHEMAS[profile]['required'])-set(headers)
    if missing: raise ValueError('Colonne obbligatorie mancanti: '+', '.join(sorted(missing)))
    if len(rows)>100000:
        raise ValueError('Troppe righe nel lotto.')
    entries, errors, skipped = [], [], 0
    existing = {r['id']:r for k in ('athlete','measurement','test','protocol') for r in store.list(k)}
    athletes = {a.get('external_id',a['id']):a for a in store.list('athlete') if a['organization_id']==org}
    athletes.update({a['id']:a for a in store.list('athlete') if a['organization_id']==org})
    protocols = {p['family']:p for p in store.list('protocol') if p.get('historical') and p.get('organization_id')==org}
    batch = hashlib.sha256(raw).hexdigest()
    for i,r in enumerate(rows,2):
        try:
            external = r.get('atleta_id','').strip()
            if not external:
                raise ValueError('atleta_id obbligatorio.')
            if profile=='atleti':
                if external in athletes:
                    skipped += 1
                    continue
                payload = Athlete(organization_id=org,name=r['nome'],surname=r['cognome'],birth_year=int(r['anno_nascita']) if r.get('anno_nascita') else None,
                                  birth_confirmed=r.get('anno_nascita_confermato')=='si',birth_source=r.get('origine_anno_nascita',''),sex=r.get('sesso',''),
                                  status='active' if r.get('attivo','si')=='si' else 'archived',notes=r.get('note','')).model_dump(mode='json')
                kind='athlete'; identity=external
            else:
                if external not in athletes:
                    raise ValueError('Atleta non riconciliato: importare prima le anagrafiche.')
                athlete_id=athletes[external]['id']
                date.fromisoformat(r['data'])
                if profile=='antropometria':
                    payload=Measurement(athlete_id=athlete_id,date=r['data'],weight_kg=number(r.get('peso_kg')),height_cm=number(r.get('statura_cm')),
                                        source=r.get('peso_fonte') if r.get('peso_fonte') in ('misurato','arrotondato','dichiarato') else 'dichiarato').model_dump(mode='json')
                    if payload['weight_kg'] is None and payload['height_cm'] is None:
                        raise ValueError('Rilevazione priva di misure.')
                    if any(m['athlete_id']==athlete_id and m['date']==payload['date'] and m.get('weight_kg')==payload['weight_kg'] and m.get('height_cm')==payload['height_cm'] and m.get('source')==payload['source'] for m in store.list('measurement')):
                        skipped+=1;continue
                    kind='measurement';identity=external+'|'+r['data']+'|'+str(r)
                else:
                    source_id=r.get('test_id','')
                    if any(t['athlete_id']==athlete_id and (t['id']==source_id or t.get('external_id')==source_id) for t in store.list('test')):
                        skipped+=1;continue
                    family=r.get('protocollo_id','').strip()
                    if not family: raise ValueError('Codice protocollo obbligatorio.')
                    if family not in protocols:
                        p={'id':str(uuid5(NAMESPACE_URL,org+'|historic-protocol|'+family)), 'organization_id':org,'name':family,'family':family,'version':'storico-non-specificato',
                           'historical':True,'status':'archived','reason':'Import storico: carico e versione non documentati','parent_id':None,
                           'definition':{'points':[],'segments':[],'duration_s':0},'objects':[]}
                        protocols[family]=p
                        if p['id'] not in existing: entries.append(('protocol',p))
                    weight=number(r.get('peso_kg'))
                    if weight is not None and weight<=0: raise ValueError('Peso deve essere positivo.')
                    a={k:number(r.get(k)) for k in ('map_w','map_alt_w','fc_max_test_bpm','fthr_bpm')}
                    if any(v is not None and v<0 for v in a.values()):raise ValueError('Valori prestativi negativi non validi.')
                    if any(a.get(k) is not None and not 0<a[k]<=250 for k in ('fc_max_test_bpm','fthr_bpm')):raise ValueError('FC fuori intervallo.')
                    a.update(threshold_w=number(r.get('soglia_w')),threshold_source=r.get('soglia_origine') or 'dichiarato',duration_s=number(r.get('durata_s')),
                             steps=[],recovery=[],zones=[],warnings=['Risultati storici dichiarati: campioni non disponibili.'],method='Import CSV storico',engine='historical-1',power_coverage=None)
                    for m in ('map','threshold'): a[m+'_wkg']=round(a[m+'_w']/weight,3) if weight and a.get(m+'_w') is not None else None
                    payload={'organization_id':org,'athlete_id':athlete_id,'date':r['data'],'protocol_id':protocols[family]['id'],'historical':True,
                             'trace_hash':None,'samples':[],'objects':[],'group_ids':[],'settings':{'weight_kg':weight,'weight_source':r.get('peso_fonte','dichiarato'),'offset_s':0,'end_s':a['duration_s'] or 0},
                             'analysis':a,'notes':r.get('note',''),'historical_fields':r}
                    kind='test';identity=r.get('test_id')
                    if not identity: raise ValueError('test_id obbligatorio.')
            id=str(uuid5(NAMESPACE_URL,org+'|'+kind+'|'+identity))
            if id in existing:
                skipped+=1;continue
            payload.update(id=id,external_id=external if kind=='athlete' else identity,import_hash=batch)
            entries.append((kind,payload));existing[id]=payload
            if kind=='athlete': athletes[external]=payload
        except (ValueError,KeyError,TypeError) as exc:
            errors.append({'row':i,'error':str(exc)})
    return {'entries':entries,'errors':errors,'skipped':skipped,'rows':len(rows),'hash':batch}
