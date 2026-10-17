"""Methods, gas imports and explicitly paired repeatability, shared by all UIs."""
import json
from collections import defaultdict
from fastapi import UploadFile
from pydantic import Field


def install_analysis(app,store,require,download):
    from .api import Model
    from .methods import catalog,validate,comparison_key

    @app.get('/api/v1/analysis-presets')
    def presets():return catalog()+store.list('analysis_preset')

    class Preset(Model):
        name: str=Field(min_length=1,max_length=300)
        family: str=Field(min_length=1,max_length=100)
        version: str=Field(min_length=1,max_length=100)
        method_id: str
        parameters: dict
        reason: str=Field(min_length=1,max_length=1000)

    @app.post('/api/v1/analysis-presets')
    def publish(data: Preset):
        payload=data.model_dump();validate(payload)
        if any(p.get('family')==data.family and p['version']==data.version for p in store.list('analysis_preset')):raise ValueError('Versione del preset già presente.')
        return store.save('analysis_preset',{**payload,'schema':1,'references':catalog()[0]['references']})

    @app.post('/api/v1/gas-traces')
    def gas(file: UploadFile):
        from .specialist import decode_gas
        raw=file.file.read(10_000_001)
        if len(raw)>10_000_000:raise ValueError('Gas CSV oltre 10 MB.')
        rows=decode_gas(raw);original=store.object(raw)
        digest=store.object(json.dumps({'kind':'gas','samples':rows,'original_hash':original},allow_nan=False).encode())
        return {'hash':digest,'samples':rows,'rows':len(rows),'units':'L/min; t in secondi'}

    class Pair(Model):
        first: str
        second: str

    class Repeatability(Model):
        pairs: list[Pair]=Field(min_length=1,max_length=500)
        metric: str='map_w'
        stable_conditions_confirmed: bool=False
        reason: str=Field(min_length=1,max_length=1000)

    @app.post('/api/v1/repeatability')
    def repeat(data: Repeatability):
        from .specialist import repeatability
        from .history import METRICS
        from .analysis import valid_number
        if not data.stable_conditions_confirmed:raise ValueError('Confermare esplicitamente che si tratta di prove ripetute in condizioni stabili.')
        if data.metric not in METRICS:raise ValueError('Metrica non supportata.')
        buckets=defaultdict(list);seen=set();sources=[]
        for pair in data.pairs:
            a,b=require(pair.first,'test'),require(pair.second,'test')
            if a['id']==b['id'] or a['athlete_id']!=b['athlete_id'] or a['protocol_id']!=b['protocol_id'] or comparison_key(a)!=comparison_key(b) or a['analysis'].get('threshold_source')!=b['analysis'].get('threshold_source'):
                raise ValueError('Coppia non confrontabile: stesso atleta, protocollo, metodo, condizioni e fonte soglia richiesti.')
            key=(a['organization_id'],a['protocol_id'],comparison_key(a),a['analysis'].get('threshold_source'))
            if (key,a['athlete_id']) in seen:raise ValueError('Una sola coppia per atleta nello stesso insieme: evitare pseudo-replicazioni.')
            seen.add((key,a['athlete_id']))
            x,y=a['analysis'].get(data.metric),b['analysis'].get(data.metric)
            if not valid_number(x) or not valid_number(y):raise ValueError('Metrica mancante nella coppia.')
            if data.metric.endswith('wkg') and any(t['settings'].get('weight_source')=='stimato' for t in (a,b)):raise ValueError('Massa stimata non ammessa nella ripetibilità standard.')
            buckets[key].append((x,y));sources.append({'first':a['revision'],'second':b['revision']})
        return {'metric':data.metric,'reason':data.reason,'source_revisions':sources,
                'groups':[{'protocol_id':k[1],'protocol_label':store.get(k[1])['name']+' / '+store.get(k[1])['version'],'method_key':k[2],**repeatability(v)} for k,v in buckets.items()]}

    @app.post('/api/v1/repeatability/report/{format}')
    def repeat_report(format:str,data:Repeatability):
        import io,csv,zipfile
        from xml.sax.saxutils import escape
        from reportlab.platypus import Paragraph,Spacer
        from reportlab.lib.units import cm
        from .pdf_style import document,styles,table,footer
        from .branding import ATTRIBUTION
        if format not in ('pdf','md'):raise ValueError('Formato non valido.')
        result=repeat(data);ss=styles();out=io.BytesIO()
        p=lambda v:Paragraph(escape(str(v)),ss['BodyText'])
        note='Differenze di prove ripetute in condizioni stabili, non cambiamenti stagionali. Errore tipico e MDC95 sono descrittivi; incertezza elevata con pochi soggetti.'
        rows=[['Protocollo','Coppie','Bias','Errore tipico','MDC95','IC95 TE (bootstrap)']]
        for g in result['groups']:
            fmt=lambda x:'n.d.' if x is None else f'{x:.2f}'
            ci=g['ci95'];interval=' - '.join(fmt(v) for v in ci['typical_error']) if ci else 'n.d. (<6 coppie)'
            rows.append([g['protocol_label'],str(g['n_pairs']),fmt(g['bias']),fmt(g['typical_error']),fmt(g['mdc95']),interval])
        if format=='md':
            text='# Ripetibilità - '+data.metric+'\n\n'+data.reason+'\n\n'+note+'\n\n'
            for i,row in enumerate(rows):
                text+='| '+' | '.join(v.replace('|','\\|') for v in row)+' |\n'
                if i==0:text+='|'+'---|'*len(row)+'\n'
            with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
                z.writestr('report.md',text+'\n'+ATTRIBUTION)
                z.writestr('manifest.json',json.dumps(result,ensure_ascii=False,allow_nan=False))
                buffer=io.StringIO();writer=csv.writer(buffer);writer.writerows(rows);z.writestr('ripetibilita.csv',buffer.getvalue())
        else:
            doc=document(out,'Ripetibilità');story=[Paragraph('Ripetibilità - '+escape(data.metric),ss['Title']),p(data.reason),p(note),Spacer(1,.5*cm),table([[p(c) for c in row] for row in rows],[4.2*cm,1.4*cm,2.2*cm,2.7*cm,2.2*cm,5*cm])]
            doc.build(story,onFirstPage=footer,onLaterPages=footer)
        return download(out.getvalue(),'application/pdf' if format=='pdf' else 'application/zip','fuorigiri-ripetibilita.'+('pdf' if format=='pdf' else 'zip'))
