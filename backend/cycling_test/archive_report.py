"""One archive report tree, scoped identically for company, group and athlete."""
import io
import json
import zipfile
from collections import defaultdict
from datetime import datetime,timezone
from xml.sax.saxutils import escape
from matplotlib.figure import Figure
from reportlab.platypus import Paragraph,Image,Spacer,PageBreak,CondPageBreak
from reportlab.lib.units import cm
from .history import summarize
from .methods import comparison_key
from .report_labels import metric_label
from .archive_pdf import ArchiveDocument,WIDTH,styles,table,contents
from .branding import ATTRIBUTION,logo_path

RENDERER = 'archive-5'


def build(store,org,group='',season='',athlete=''):
    organization=store.get(org)
    if organization['kind']!='organization':raise ValueError('Società non valida.')
    for identifier,kind in ((group,'group'),(athlete,'athlete')):
        if identifier:
            r=store.get(identifier)
            if r['kind']!=kind or r['organization_id']!=org:raise ValueError('Filtro esterno alla società.')
    dataset=summarize(store,org,group,season,athlete,mode='tests',dimension='all')
    ids={r['id'] for r in dataset['rows']}
    tests=sorted([t for t in store.list('test') if t['id'] in ids],key=lambda t:(t['date'],t['id']))
    athletes={a['id']:a for a in store.list('athlete') if a['organization_id']==org and a.get('status')!='deleted' and (not athlete or a['id']==athlete)}
    # A society report includes registered athletes without tests; a scoped
    # report includes dated memberships even if no test exists for that member.
    if group or season:
        groups={g['id']:g for g in store.list('group') if g['organization_id']==org}
        eligible={m['athlete_id'] for m in store.list('membership') if m.get('status')!='deleted' and m['group_id'] in groups
                  and (not group or group in (m['group_id'],groups[m['group_id']].get('parent_id')))
                  and (not season or groups[m['group_id']].get('season')==season or (not groups[m['group_id']].get('season') and m['start'][:4]<=season and (not m.get('end') or m['end'][:4]>=season)))}
        eligible|={t['athlete_id'] for t in tests}
        athletes={k:v for k,v in athletes.items() if k in eligible}
    athlete_ids=set(athletes)
    measures=sorted([m for m in store.list('measurement') if m['athlete_id'] in athlete_ids and m.get('status')!='deleted'
                     and (not season or m['date'][:4]==season)],key=lambda m:(m['date'],m['id']))
    protocols={p['id']:p for p in store.list('protocol') if any(t['protocol_id']==p['id'] for t in tests)}
    sections=[];signatures={}
    views=[('season','Per stagione'),('age_season','Per anno di età e stagione'),('age','Per anno di età'),
           ('category','Per categoria'),('category_season','Per categoria e stagione'),
           ('category_year_season','Per anno di categoria e stagione'),('cohort','Per coorte di nascita'),('cohort_season','Per coorte e stagione')]
    if not athlete:
        for dimension,title in views:
            data=summarize(store,org,group,season,athlete,mode='athlete',dimension=dimension)
            # Every view selects the latest test per athlete and method/bucket.
            # Merge only genuinely identical partitions, not equal averages.
            signature=tuple(sorted(tuple(sorted(g['revisions'])) for g in data['groups']))
            if not signature:continue
            if signature in signatures:
                signatures[signature]['equivalent_views'].append(title);continue
            section={'id':dimension,'title':title,'equivalent_views':[],'groups':data['groups']}
            signatures[signature]=section;sections.append(section)
    from .history import metric_applicable
    from .history import metrics_for,custom_labels
    available_metrics=metrics_for(store)
    coverage={m:{'valid':sum(t['analysis'].get(m) is not None if m not in ('weight_kg','height_cm') else t['settings'].get(m) is not None for t in tests if metric_applicable(t,m)),'total':sum(metric_applicable(t,m) for t in tests)} for m in available_metrics}
    entries=[]
    for a in sorted(athletes.values(),key=lambda a:(a['surname'],a['name'],a['id'])):
        from .maturation import snapshots
        entries.append({'athlete':a,'tests':[t for t in tests if t['athlete_id']==a['id']],
                        'measurements':[m for m in measures if m['athlete_id']==a['id']],
                        'maturation':snapshots(store,a['id'],season+'-12-31' if season else None)})
    group_label=store.get(group)['name'] if group else ''
    return {'schema':2,'renderer':RENDERER,'generated_at':datetime.now(timezone.utc).isoformat(),
        'scope':{'organization_id':org,'group':group,'season':season,'athlete':athlete},'organization':organization,
        'scope_label':' / '.join(filter(None,[group_label,season,(athletes[athlete]['surname']+' '+athletes[athlete]['name']) if athlete in athletes else ''])),
        'counts':{'athletes':len(athletes),'athletes_with_tests':len({t['athlete_id'] for t in tests}),'tests':len(tests),'measurements':len(measures),'protocols':len(protocols)},
        'coverage':coverage,'metric_labels':custom_labels(store),'sections':sections,'athletes':entries,'protocols':list(protocols.values()),
        'common_warnings':sorted(set.intersection(*(set(t['analysis'].get('warnings',[])) for t in tests))) if tests else [],
        'source_revisions':[r['revision'] for e in entries for r in e['maturation']]+[t['revision'] for t in tests]+[m['revision'] for m in measures]+[a['revision'] for a in athletes.values()]+[p['revision'] for p in protocols.values()]+[m['revision'] for m in store.list('membership') if m['athlete_id'] in athlete_ids]}


def plot(rows,kind,label,metric="map_wkg"):
    fig=Figure(figsize=(9,3.6),layout='constrained');ax=fig.subplots()
    if kind=='aggregate':
        for i,g in enumerate(rows):
            m=g['metrics'][metric];value=m['median']
            if value is not None:
                ax.scatter(i,value,color='#1a62b7',s=35)
                ax.vlines(i,m['q1'],m['q3'],color='#1a62b7',linewidth=3)
        ax.set_xticks(range(len(rows)),[g['label'] for g in rows],rotation=25,ha='right',fontsize=9)
        ax.set_ylabel(metric_label(metric)+' - mediana e IQR')
    else:
        buckets=defaultdict(list)
        for t in rows:buckets[(t['protocol_id'],comparison_key(t))].append(t)
        for (_,method),tests in buckets.items():
            valid=[t for t in tests if t['analysis'].get(metric) is not None]
            if valid:
                ax.plot([datetime.fromisoformat(t['date']) for t in valid],[t['analysis'][metric] for t in valid],marker='o',linewidth=1.5,
                        label=valid[0].get('analysis',{}).get('preset',{}).get('name','Metodo storico')+' · '+valid[0].get('protocol_label','Protocollo'))
        ax.set_ylabel(metric_label(metric));ax.tick_params(axis='x',rotation=25,labelsize=9)
        if ax.lines:ax.legend(fontsize=8,loc='best')
    ax.set_title(label,fontsize=10,loc='left');ax.grid(axis='y',alpha=.15);ax.spines[['top','right']].set_visible(False)
    out=io.BytesIO();fig.savefig(out,format='png',dpi=150);return out.getvalue()


def render(data,format='pdf'):
    from .report_labels import metric_label as base_label
    metric_label=lambda key:data.get('metric_labels',{}).get(key) or base_label(key)
    available_metrics=list(data['coverage'])
    ss=styles();story=[];markdown=[];assets={};title='Archivio dei test - '+data['organization']['name']
    def p(value,style='BodyText'):return Paragraph(escape(str(value).replace('—','-').replace('–','-')),ss[style])
    def text(value,style='BodyText'):
        story.append(p(value,style));markdown.append(('## ' if style=='Heading2' else '')+str(value)+'\n')
    def fmt(v):
        if v is None:return 'n.d.'
        if isinstance(v,float):return f'{v:.2f}'.rstrip('0').rstrip('.')
        return str(v)
    def grid(headers,rows,widths=None):
        if not rows:return
        story.append(table([[p(c,'TableHeader') for c in headers]]+[[p(fmt(c),'TableCell') for c in row] for row in rows],widths or [WIDTH/len(headers)]*len(headers)))
        esc=lambda v:str(v).replace('|','\\|').replace('\n',' ').replace('<','&lt;')
        markdown.extend(['| '+' | '.join(esc(c) for c in headers)+' |','|'+'---|'*len(headers)])
        markdown.extend('| '+' | '.join(esc(fmt(c)) for c in row)+' |' for row in rows);markdown.append('')
    def image(body,name):
        assets[name]=body;story.extend([Spacer(1,.25*cm),Image(io.BytesIO(body),width=WIDTH,height=7.08*cm)])
        markdown.append(f'![Grafico](assets/{name})\n')
    def heading(label,level,key,new_page=False):
        if new_page:story.append(PageBreak())
        paragraph=p(label,'Chapter' if level==0 else 'Section')
        paragraph.toc_level=level;paragraph.toc_key=key;paragraph.toc_title=label
        story.append(paragraph);markdown.append(('## ' if level==0 else '### ')+label+'\n')
    text('FUORIGIRI PERFORMANCE LAB','Small');text(title,'Title')
    if data['scope_label']:text(data['scope_label'],'Heading2')
    c=data['counts'];text(f"{c['athletes']} atleti · {c['tests']} test · {c['measurements']} misure · {c['protocols']} versioni di protocollo")
    text('Documento riservato ai destinatari autorizzati. Risultati descrittivi; nessuna diagnosi o confronto con norme pediatriche implicito.','Small')
    text('Ambito: '+(data['scope_label'] or 'Intera società'))
    text('Generato: '+data['generated_at'][:10],'Small')
    if format=='pdf':
        story.append(PageBreak());story.append(p('Indice','Chapter'))
        story.append(p('Seleziona una voce per raggiungere il capitolo o la scheda atleta.','Small'))
        story.append(contents(ss))
    heading('1. Sintesi e copertura',0,'summary',new_page=True)
    text('Aggregati: ultimo test per atleta in ogni periodo e insieme confrontabile. Media e mediana affiancate; protocolli, preset, condizioni e origini della soglia separati. Masse stimate escluse dagli aggregati W/kg. Lo storico individuale conserva tutti i test.','Small')
    text('Età = anno del test meno anno di nascita, non età esatta; nascita non confermata segnalata nella scheda. Viste equivalenti accorpate quando selezionano esattamente le stesse revisioni.','Small')
    for warning in data.get('common_warnings',[]):text('Qualità comune ai test: '+warning,'Small')
    grid(['Dato','Presenti','Assenti applicabili'],[[metric_label(m),v['valid'],v['total']-v['valid']] for m,v in data['coverage'].items() if v['total'] and (v['valid'] or m in ('map_w','weight_kg','height_cm'))],[10*cm,3.85*cm,3.85*cm])
    protocols={p['id']:p for p in data['protocols']}
    if data['sections']:heading('2. Viste aggregate',0,'aggregates',new_page=True)
    for section_index,section in enumerate(data['sections'],1):
        heading(f"2.{section_index} {section['title']}",1,'view-'+section['id'],new_page=section_index>1)
        if section['equivalent_views']:text('Stessa selezione anche per: '+', '.join(section['equivalent_views']),'Small')
        partitions=defaultdict(list)
        for g in section['groups']:partitions[(g['protocol_id'],g['method_key'],g['threshold_source'])].append(g)
        for (pid,_,source),groups in partitions.items():
            protocol=protocols[pid]
            story.append(CondPageBreak(5*cm))
            text(protocol['name']+' / '+protocol['version'],'Subsection')
            text(groups[0]['method_label']+('' if protocol.get('test_type') else ' - Soglia: '+metric_label(str(source))),'Small')
            for g in groups:
                text(g['label']+f" - {g['athletes']} atleti / {g['tests_selected']} test selezionati",'Subsection')
                compact=[]
                for metric in available_metrics:
                    value=g['metrics'][metric]
                    if value['n']:
                        compact.append([metric_label(metric),f"{value['n']} / {value['missing']}",value['mean'],value['median'],fmt(value['min'])+' - '+fmt(value['max'])])
                grid(['Metrica','n / assenti','Media','Mediana','Min - max'],compact,[7*cm,2.1*cm,2.1*cm,2.1*cm,4.4*cm])
            chart_metric='peak_wkg' if protocol.get('test_type') else 'map_wkg'
            if len(groups)>1 and any(g['metrics'][chart_metric]['n'] for g in groups):image(plot(groups,'aggregate',section['title'],chart_metric),f'aggregate-{len(assets)}.png')
    athlete_chapter=3 if data['sections'] else 2
    heading(f'{athlete_chapter}. Schede individuali degli atleti',0,'athletes',new_page=True)
    for i,entry in enumerate(data['athletes']):
        a=entry['athlete'];tests=entry['tests']
        heading(f"{athlete_chapter}.{i+1} {a['surname']} {a['name']}",1,'athlete-'+str(i),new_page=i>0)
        text('Nascita: '+str(a.get('birth_date') or a.get('birth_year') or 'n.d.')+' · '+('confermata' if a.get('birth_confirmed') else 'da confermare')+' · Sesso: '+str(a.get('sex') or 'n.d.')+' · Stato: '+str(a.get('status','active')),'Small')
        if not tests:text('Nessun test nell’ambito selezionato.')
        for chart_metric in ('map_wkg','peak_wkg','mean_wkg'):
            if sum(t['analysis'].get(chart_metric) is not None for t in tests)>=2:image(plot([{**t,'protocol_label':protocols[t['protocol_id']]['family']+' / '+protocols[t['protocol_id']]['version']} for t in tests],'athlete','Evoluzione individuale - serie separate per metodo/protocollo',chart_metric),f'athlete-{i}-{chart_metric}.png')
        if any(not t.get('test_type') for t in tests):text('Test aerobici - riepilogo','Subsection')
        grid(['Data','Protocollo','MAP W','W/kg','Soglia W','FC max'],[[t['date'],protocols[t['protocol_id']]['family']+' / '+protocols[t['protocol_id']]['version'],
            t['analysis'].get('map_w'),t['analysis'].get('map_wkg'),t['analysis'].get('threshold_w'),t['analysis'].get('fc_max_test_bpm')] for t in tests if not t.get('test_type')],
            [2.4*cm,5.3*cm,2.5*cm,2.5*cm,2.5*cm,2.5*cm])
        custom_tests=[t for t in tests if t.get('test_type')=='custom']
        for t in custom_tests:
            from .custom_fields import display_rows
            text(t['date']+' - '+protocols[t['protocol_id']]['name'],'Small')
            grid(['Campo personalizzato','Valore'],display_rows(t),[10*cm,7.7*cm])
        if any(t.get('test_type') in ('sprint','wingate15','wingate30') for t in tests):text('Test anaerobici - riepilogo','Subsection')
        grid(['Data','Protocollo','Picco W','Media W','Lavoro kJ','FC max'],[[t['date'],protocols[t['protocol_id']]['name'],t['analysis'].get('peak_w'),t['analysis'].get('mean_w'),t['analysis'].get('work_kj'),t['analysis'].get('fc_max_test_bpm')] for t in tests if t.get('test_type') in ('sprint','wingate15','wingate30')],[2.4*cm,5.3*cm,2.5*cm,2.5*cm,2.5*cm,2.5*cm])
        if tests:text('Dettagli dei test e qualità dei dati','Subsection')
        for t in tests:
            text(t['date']+' - '+protocols[t['protocol_id']]['name'],'Subsection')
            values={**t.get('historical_fields',{}),**{k:v for k,v in t['settings'].items() if k in ('weight_kg','height_cm','rest_hr','rest_after_s','rpe','rpe_scale','ftp_w','fthr_bpm','threshold_coefficient')}}
            for key in ('peak_w','peak_wkg','mean_w','mean_wkg','best_1s_w','best_5s_w','time_to_peak_s','end_power_w','fatigue_pct','decline_ws','declared_fatigue_ws','cadence_max_rpm','cadence_mean_rpm','map_alt_w','duration_s','duration_incremental_s','power_mean_w','work_kj','power_coverage','lactate_2_w','lactate_4_w','vo2peak_l_min','vo2peak_ml_kg_min','terminal_target_w','terminal_mean_w'):
                if t['analysis'].get(key) is not None:values[key]=t['analysis'][key]
            from .lactate_levels import PATTERN
            values.update({k:v for k,v in t['analysis'].items() if PATTERN.fullmatch(k) and v is not None})
            if t.get('test_type'):
                from .anaerobic import METRIC_MAP
                for k in (*METRIC_MAP,'peso_kg','peso_fonte','referto_leggibile','note','peak_w','mean_w','work_kj'):values.pop(k,None)
            for k in ('map_w','map_wkg','threshold_w','fc_max_test_bpm','test_id','atleta_id','data','protocollo_id'):values.pop(k,None)
            values={k:v for k,v in values.items() if v is not None and v!=''}
            text(t['date']+' · '+t['analysis'].get('preset',{}).get('name',t['analysis'].get('source','Legacy')+' / '+t['analysis'].get('engine','ignoto'))+('' if t.get('test_type') else ' · '+str(t['analysis'].get('threshold_source') or 'soglia assente')),'Small')
            if values:
                cells=[[metric_label(k),v] for k,v in values.items()]
                compact=[cells[i]+(cells[i+1] if i+1<len(cells) else ['','']) for i in range(0,len(cells),2)]
                grid(['Dato aggiuntivo','Valore','Dato aggiuntivo','Valore'],compact,[5.8*cm,3.05*cm,5.8*cm,3.05*cm])
            if t['analysis'].get('recovery'):grid(['Recupero dopo s','FC bpm','HRR bpm','Origine'],[[r['after_s'],r.get('hr_bpm'),r.get('hrr_bpm'),r.get('source','sensore')] for r in t['analysis']['recovery']])
            if t['settings'].get('conditions'):text('Condizioni: '+'; '.join(k.replace('_',' ')+': '+v for k,v in t['settings']['conditions'].items() if v),'Small')
            if t.get('test_type')!='custom':
                from .custom_fields import display_rows
                grid(['Campo aggiuntivo','Valore'],display_rows(t),[10*cm,7.7*cm])
            if t.get('notes'):text(t['notes'],'Small')
            warnings=[w for w in t['analysis'].get('warnings',[]) if w not in data.get('common_warnings',[])]
            if warnings:text('Qualità: '+'; '.join(warnings),'Small')
        if entry['measurements']:
            text('Antropometria datata','Subsection');grid(['Data','Massa kg','Statura cm','Fonte'],[[m['date'],m.get('weight_kg'),m.get('height_cm'),m.get('source','dichiarato')] for m in entry['measurements']])
        from .maturation import report_section
        if entry.get('maturation'):story.append(CondPageBreak(7*cm))
        report_section(entry,text,grid,image)
    heading(f'{athlete_chapter+1}. Protocolli e metodi',0,'protocols',new_page=True)
    grid(['Protocollo','Versione','Definizione'],[[p['name'],p['version'],str(len(p['definition'].get('segments',[])))+' fasi' if p['definition'].get('segments') else 'Solo catalogo'] for p in data['protocols']],[7*cm,2.7*cm,8*cm])
    for protocol in data['protocols']:
        if protocol.get('anaerobic_spec'):
            spec=protocol['anaerobic_spec']
            text(protocol['name']+' / '+protocol['version'],'Small')
            text('Durata: '+str(spec['duration_s'])+' s; coppia: '+str(spec.get('torque_nm_kg') or 'n.d.')+' N.m/kg; dispositivo: '+str(spec.get('device') or 'n.d.')+'; partenza: '+str(spec.get('start') or 'unknown')+'; finestra picco: '+str(spec.get('peak_window_s') or 'n.d.')+' s; finestra finale: '+str(spec.get('end_window_s') or 'n.d.')+' s.','Small')
    text('Il manifest allegato al Markdown contiene ambito, revisioni, provenienza e risultati completi. Le sezioni assenti non contengono dati: non vengono creati valori o analisi anaerobiche da test incrementali.','Small')
    text('Generato: '+data['generated_at'],'Small')
    if format=='md':
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
            z.writestr('report.md','\n'.join(markdown)+'\n\n'+ATTRIBUTION+'\n')
            z.writestr('manifest.json',json.dumps(data,ensure_ascii=False,allow_nan=False))
            for name,body in assets.items():z.writestr('assets/'+name,body)
            z.write(logo_path(),'assets/logo.png')
        return out.getvalue()
    out=io.BytesIO();doc=ArchiveDocument(out,title);doc.multiBuild(story)
    return out.getvalue()


def install_archive_reports(app,store,require,download):
    from typing import Literal
    @app.get('/api/v1/archive/{org}/report-data')
    def report_data(org:str,group:str='',season:str='',athlete:str=''):
        require(org,'organization');return build(store,org,group,season,athlete)

    @app.get('/api/v1/archive/{org}/report/{format}')
    def report(org:str,format:Literal['md','pdf'],group:str='',season:str='',athlete:str=''):
        data=report_data(org,group,season,athlete);body=render(data,format)
        from .store import save_report
        save_report(store,{'organization_id':org,'renderer_version':RENDERER,'query':data['scope'],'source_revisions':data['source_revisions'],
                           'format':format,'language':'it'},body)
        return download(body,'application/pdf' if format=='pdf' else 'application/zip','fuorigiri-archivio.'+('pdf' if format=='pdf' else 'zip'))
