"""Strict CSV profiles: preview before atomic commit, stable external IDs."""
import csv
import io
import hashlib
from datetime import date
from uuid import uuid5, NAMESPACE_URL

SCHEMAS = {
    'appartenenze': {'required':['atleta_id','nome','cognome','data_inizio','gruppo'], 'rule': 'ID, nome e cognome riconciliati. Date AAAA-MM-GG; fine vuota = in corso. Gruppo = categoria; sottogruppo = stagione (es. 2024). Anteprima dei gruppi da creare.'},
    'test_anaerobico': {'required':['test_id','atleta_id','data','protocollo_id'], 'rule':'Sprint breve, Wingate 15 s o 30 s: indicare tipo_test (sprint, wingate15, wingate30) e durata_s. Il solo codice storico ANA-15-070 conserva la compatibilità a 15 s e 0,70 N·m/kg.'},
    'atleti': {'required':['atleta_id','cognome','nome'], 'rule':'Nome e cognome obbligatori; gli altri campi sono facoltativi.'},
    'antropometria': {'required':['atleta_id','data'], 'rule':'Almeno peso_kg, statura_cm oppure altezza_perineale_cm; peso_fonte facoltativo (dichiarato).'},
    'test_aerobico': {'required':['test_id','atleta_id','data','protocollo_id'], 'rule':'Risultati facoltativi: i valori assenti restano vuoti, mai zero.'},
}



def import_columns(profile):
    if profile not in SCHEMAS:
        raise ValueError('Profilo CSV non supportato.')
    if profile=='appartenenze':
        from .membership_import import COLUMNS
        return COLUMNS
    from .reports import CSV_HEADERS
    from .anaerobic import EXTENDED_HEADER
    return (EXTENDED_HEADER if profile=='test_anaerobico' else CSV_HEADERS[profile]).split(',')


def template_csv(profile):
    stream=io.StringIO(newline='')
    csv.writer(stream).writerow(import_columns(profile))
    return stream.getvalue().encode('utf-8-sig')


def read(raw):
    text = raw.decode('utf-8-sig')
    if not text.strip(): raise ValueError('CSV vuoto.')
    delimiter = ';' if text.splitlines()[0].count(';') > text.splitlines()[0].count(',') else ','
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter, strict=True)
    try:
        if not reader.fieldnames or len(reader.fieldnames)!=len(set(reader.fieldnames)):
            raise ValueError('Intestazioni CSV mancanti o duplicate.')
        from .csv_safety import restore
        # Apostrophes added by Fuorigiri exports against spreadsheet formulas are removed.
        rows=[{k:restore(v) for k,v in row.items()} for row in reader]
    except csv.Error:
        raise ValueError('CSV non valido: controllare virgolette e dimensione dei campi.') from None
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
        # Optional channels have explicit units. Do not infer mmol/L from a
        # generic "lactate" column or convert summary values into observations.
        for key,alias in [('lactate_mmol_l','lattato_mmol_l'),('speed_kmh','velocita_kmh'),('temperature_c','temperatura_c'),('altitude_m','quota_m')]:
            if key in r or alias in r:
                values[key]=number(r.get(key,r.get(alias)))
                if key in ('lactate_mmol_l','speed_kmh') and values[key] is not None and values[key]<0:
                    raise ValueError(f'Riga {i}: {key} negativo.')
        for key in ('vo2_l_min','vco2_l_min','ve_l_min','peto2_mmhg','petco2_mmhg'):
            if key in r:
                values[key]=number(r[key])
                if values[key] is not None and (values[key]<0 or key=='vo2_l_min' and values[key]==0):
                    raise ValueError(f'Riga {i}: {key} deve essere positivo (VO2) o non negativo.')
        samples.append({'t':t,**values,'paused':r.get('paused','').lower() in ('true','1','si')})
    if len(samples)<2:
        raise ValueError('Servono almeno due campioni.')
    return {'samples':samples,'duration_s':samples[-1]['t'],'started_at':'','warnings':[], 'source':'CSV secondi/W/bpm/rpm'}


def plan_import(store, org, profile, raw):
    if profile=='appartenenze':
        from .membership_import import plan_memberships
        return plan_memberships(store,org,raw)
    if profile=='test_anaerobico':
        from .anaerobic import historical_plan
        return historical_plan(store,org,raw)
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
    warnings = []
    bases = {}
    integrated_fields = {}
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
                    payload=Measurement(athlete_id=athlete_id,date=r['data'],weight_kg=number(r.get('peso_kg')),height_cm=number(r.get('statura_cm')),perineal_height_cm=number(r.get('altezza_perineale_cm')),
                                        source='dichiarato',origin='').model_dump(mode='json')
                    payload.update(source=r.get('peso_fonte','').strip() or 'dichiarato',origin=r.get('origine',''))
                    if all(payload[k] is None for k in ('weight_kg','height_cm','perineal_height_cm')):
                        raise ValueError('Rilevazione priva di misure.')
                    measures=('weight_kg','height_cm','perineal_height_cm')
                    same_day=[m for m in existing.values() if m.get('kind')=='measurement' and m['athlete_id']==athlete_id and m['date']==payload['date']]
                    active=[m for m in same_day if m.get('status','active')=='active']
                    compatible=[m for m in active if all(payload[k] is None or m.get(k) is None or payload[k]==m[k] for k in measures)]
                    if same_day:
                        if not compatible:
                            raise ValueError('Misure discordanti o rilevazione eliminata per atleta e data: correggere o ripristinare dal profilo.')
                        metadata=[(key,payload[key]) for key,column in (('source','peso_fonte'),('origin','origine')) if r.get(column,'').strip()]
                        # Already acquired measurements need no target to be updated, even
                        # when multiple historical observations contain those same values.
                        covered=[m for m in compatible if all(payload[k] is None or m.get(k)==payload[k] for k in measures)]
                        candidates=covered or compatible
                        matching=[m for m in candidates if all(str(m.get(k) or '').strip()==str(v).strip() for k,v in metadata)]
                        if matching:
                            candidates=matching
                        else:
                            for key,value in metadata:
                                matches=[m for m in candidates if str(m.get(key) or '').strip()==str(value).strip()]
                                if matches:
                                    candidates=matches
                        if not covered and len(candidates)>1:
                            raise ValueError('Più rilevazioni compatibili per atleta e data: integrazione ambigua. Correggere la rilevazione dal profilo.')
                        old=candidates[0]
                        athlete=athletes[external]
                        context={'row':i,'athlete_external_id':external,'athlete_name':(athlete.get('surname','')+' '+athlete.get('name','')).strip(),'date':payload['date']}
                        row_warnings=[]
                        for key,column in (('source','peso_fonte'),('origin','origine')):
                            if r.get(column,'').strip() and str(payload[key]).strip()!=str(old.get(key) or '').strip():
                                row_warnings.append({**context,'column':column,'previous':old.get(key,'') or '', 'incoming':payload[key]})
                        added=[k for k in measures if payload[k] is not None and old.get(k) is None]
                        if not added:
                            warnings.extend(row_warnings)
                            skipped+=1;continue
                        merged={**old,**{k:payload[k] for k in added}}
                        # Revalidate the combined observation, preserving advanced data and provenance.
                        Measurement(**{k:v for k,v in merged.items() if k in Measurement.model_fields})
                        warnings.extend(row_warnings)
                        if old.get('revision'):
                            bases[old['id']]=old['revision']
                            merged['reason']='Integrazione CSV di misure mancanti'
                        merged['import_hash']=batch
                        integrated_fields.setdefault(old['id'],[]).extend(k for k in added if k not in integrated_fields.get(old['id'],[]))
                        for index,(_,entry) in enumerate(entries):
                            if entry['id']==old['id']:
                                entries[index]=('measurement',merged)
                                break
                        else:
                            entries.append(('measurement',merged))
                        existing[old['id']]=merged
                        continue
                    # New observations still require a valid source; only existing
                    # observations can retain a previous value instead of an invalid one.
                    payload=Measurement(**payload).model_dump(mode='json')
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
                    coefficient=number(r.get('coeff_soglia'))
                    if coefficient is not None and not 0<coefficient<=2:raise ValueError('Coefficiente soglia fuori intervallo: deve essere maggiore di 0 e non oltre 2.')
                    a={k:number(r.get(k)) for k in ('map_w','map_alt_w','fc_max_test_bpm','fthr_bpm')}
                    if any(v is not None and v<0 for v in a.values()):raise ValueError('Valori prestativi negativi non validi.')
                    if any(a.get(k) is not None and not 0<a[k]<=250 for k in ('fc_max_test_bpm','fthr_bpm')):raise ValueError('FC fuori intervallo.')
                    a.update(threshold_w=number(r.get('soglia_w')),threshold_source=r.get('soglia_origine') or 'dichiarato',duration_s=number(r.get('durata_s')),
                             steps=[],recovery=[],zones=[],warnings=['Risultati storici dichiarati: campioni non disponibili.'],method='Import CSV storico',engine='historical-1',power_coverage=None)
                    for m in ('map','threshold'): a[m+'_wkg']=round(a[m+'_w']/weight,3) if weight and a.get(m+'_w') is not None else None
                    payload={'organization_id':org,'athlete_id':athlete_id,'date':r['data'],'protocol_id':protocols[family]['id'],'historical':True,
                             'trace_hash':None,'samples':[],'objects':[],'group_ids':[],'settings':{'weight_kg':weight,'weight_source':r.get('peso_fonte','dichiarato'),'threshold_coefficient':coefficient,'offset_s':0,'end_s':a['duration_s'] or 0},
                             'analysis':a,'notes':r.get('note',''),'historical_fields':r}
                    from .training_zones import for_test
                    payload['analysis']['zones']=[{k:v for k,v in z.items() if k not in ('test_id','test_revision','test_date','definition_source')} for z in for_test(payload)]
                    kind='test';identity=r.get('test_id')
                    if not identity: raise ValueError('test_id obbligatorio.')
            id=str(uuid5(NAMESPACE_URL,org+'|'+kind+'|'+identity))
            if id in existing:
                skipped+=1;continue
            payload.update(id=id,kind=kind,external_id=external if kind=='athlete' else identity,import_hash=batch)
            entries.append((kind,payload));existing[id]=payload
            if kind=='athlete': athletes[external]=payload
        except (ValueError,KeyError,TypeError) as exc:
            errors.append({'row':i,'error':str(exc)})
    return {'entries':entries,'bases':bases,'integrated_fields':integrated_fields,'warnings':warnings,'errors':errors,'skipped':skipped,'rows':len(rows),'hash':batch}


def plan_digest(result):
    """Bind confirmation to the proposed records and their exact source revisions."""
    from .store import encoded
    return hashlib.sha256(encoded({'entries':result['entries'],'bases':result.get('bases',{})}).encode()).hexdigest()
