import io
import json
import zipfile
from xml.sax.saxutils import escape
from matplotlib.figure import Figure
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def render(data, format):
    fig=Figure(figsize=(10,4),layout='constrained');ax=fig.subplots()
    for group in data['groups']:
        v=group['metrics']['map_w']['median']
        if v is not None: ax.scatter([group['label']],[v],label=group['protocol_id'][:8])
    ax.set_ylabel('MAP W - mediana');ax.tick_params(axis='x',labelrotation=35);ax.grid(alpha=.15)
    png=io.BytesIO();fig.savefig(png,format='png',dpi=150)
    rows=[['Gruppo / protocollo','Atleti','Test','MAP W','MAP W/kg','Soglia W']]
    for g in data['groups']:
        def val(m):
            v=g['metrics'][m]['median']
            return '-' if v is None else f'{v:.2f}'
        rows.append([g['label']+' / '+g['protocol_id'][:8],str(g['athletes']),str(g['tests_selected']),val('map_w'),val('map_wkg'),val('threshold_w')])
    query=json.dumps(data['query'],ensure_ascii=False)
    if format=='md':
        text='# Storico dei test\n\nFiltri: '+query+'\n\n![Storico](assets/history.png)\n\n'
        for i,row in enumerate(rows):
            text+='| '+' | '.join(str(v).replace('|','\\|').replace('\n',' ') for v in row)+' |\n'
            if i==0:text+='|'+'---|'*len(row)+'\n'
        text+='\nRisultati separati per protocollo e fonte della soglia. Conteggi e copertura per metrica nel manifest.\n'
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('report.md',text);z.writestr('assets/history.png',png.getvalue());z.writestr('manifest.json',json.dumps(data,ensure_ascii=False))
        return out.getvalue()
    styles=getSampleStyleSheet();p=lambda s:Paragraph(escape(str(s)),styles['BodyText'])
    out=io.BytesIO();doc=SimpleDocTemplate(out)
    table=Table([[p(c) for c in row] for row in rows],repeatRows=1,colWidths=[160,45,45,65,65,65])
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8f0fa')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
    story=[Paragraph('Storico dei test',styles['Title']),p(query),Spacer(1,12),Image(io.BytesIO(png.getvalue()),width=450,height=180),table,
           p('Mediane separate per protocollo e fonte della soglia. Modalità: '+data['query']['mode'])]
    for g in data['groups']:
        story.append(p(g['label']+' | '+g['threshold_source']+' | '+', '.join(f'{m}: n={v["n"]}, mancanti={v["missing"]}' for m,v in g['metrics'].items())))
    story.append(p('Revisioni sorgente: '+', '.join(r['revision'] for r in data['rows'])))
    doc.build(story)
    return out.getvalue()
