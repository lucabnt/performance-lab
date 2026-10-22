import csv
import json
import io
import zipfile
from xml.sax.saxutils import escape

import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from .branding import ATTRIBUTION, logo_path
from .locales import tr
from .report_labels import metric_label
from .scientific_labels import reason as scientific_reason, METHODS

from .anaerobic import CSV_HEADER as ANAEROBIC_HEADER
RENDERER_VERSION='0.8-lactate-2'
CSV_HEADERS = {
    'test_anaerobico': ANAEROBIC_HEADER,
    "atleti": "atleta_id,cognome,nome,anno_nascita,anno_nascita_confermato,origine_anno_nascita,sesso,attivo,note",
    "antropometria": "atleta_id,data,peso_kg,statura_cm,peso_fonte,origine",
    "test_aerobico": "test_id,atleta_id,data,protocollo_id,durata_s,map_w,map_alt_w,peso_kg,peso_fonte,soglia_w,coeff_soglia,soglia_origine,lattato_2mmol_w,lattato_4mmol_w,fc_max_test_bpm,fc_max_riferimento_bpm,fthr_bpm,fthr_pct_fcmax,lavoro_battito_j,lavoro_battito_max_j,cadenza_media_rpm,cadenza_max_rpm,rapporto_trasm_m,pedivella_m,segnale_fc_interrotto,referto_leggibile,tracciato_parziale,note",
}


def chart(test, protocol, language='it'):
    fig = Figure(figsize=(10, 4.8), layout="constrained")
    axes = fig.subplots(3, 1, sharex=True)
    samples = test["samples"]
    if not samples:
        axes[0].text(.5,.5,tr('Risultato storico: tracciato non disponibile',language),ha='center',transform=axes[0].transAxes)
        out=io.BytesIO();fig.savefig(out,format='png',dpi=160)
        return out.getvalue()
    for ax, field, label, color in zip(axes, ("power", "hr", "cadence"), ("Potenza (W)", "FC (bpm)", "Cadenza (rpm)"), ("#247d70", "#b85850", "#637caa")):
        ax.plot([r["t"]/60 for r in samples], [r.get(field) for r in samples], color=color, linewidth=1)
        ax.set_ylabel(tr(label,language), fontsize=8)
        ax.grid(alpha=.15)
        ax.tick_params(labelsize=8)
        ax.axvline(test["settings"]["end_s"]/60, color="#555555", linestyle="--", linewidth=.8)
    offset = test["settings"]["offset_s"]
    stop=min(samples[-1]['t'],test['settings']['end_s']);shift=offset
    markers={m['number']:m['at_s'] for m in test['settings'].get('alignment_markers',[])}
    for index,segment in enumerate(protocol['definition']['segments']):
        if index+1 in markers:shift=markers[index+1]-segment['start_s']
        a=shift+segment['start_s'];b=min(stop,shift+segment['end_s'])
        if a>=stop:break
        end_w=segment['start_w']+(segment['end_w']-segment['start_w'])*(b-a)/(segment['end_s']-segment['start_s'])
        axes[0].plot([a/60,b/60],[segment['start_w'],end_w],color='#abb2af',linewidth=1)
    for interval in test['settings'].get('excluded_intervals',[]):
        for ax in axes:ax.axvspan(interval['start_s']/60,interval['end_s']/60,color='#b85850',alpha=.12)
    axes[0].set_xlim(0, samples[-1]["t"]/60)
    axes[-1].set_xlabel(tr("Tempo trascorso (min)",language), fontsize=8)
    out = io.BytesIO()
    fig.savefig(out, format="png", dpi=160)
    return out.getvalue()


def val(value):
    return "n.d." if value is None else f'{value:.2f}'.rstrip('0').rstrip('.') if isinstance(value,float) else str(value)


def specialist_charts(analysis):
    images=[];lactate=analysis.get('lactate_analysis',{})
    if lactate.get('points'):
        fig=Figure(figsize=(9,4),layout='constrained');ax=fig.subplots();points=lactate['points'];curve=lactate['curve']
        ax.plot([p['power_w'] for p in points],[p['mmol_l'] for p in points],'o',label='Prelievi associati al carico',color='#1a62b7')
        if len(points)>1 and all(b['power_w']>a['power_w'] and b['mmol_l']>=a['mmol_l'] for a,b in zip(points,points[1:])):
            ax.plot([p['power_w'] for p in points],[p['mmol_l'] for p in points],'--',label='Interpolazione lineare',color='#1a62b7')
        if curve:ax.plot([p['power_w'] for p in curve],[p['mmol_l'] for p in curve],':',label='Fit cubico',color='#61738a')
        for result in lactate.get('results',{}).values():
            if result.get('concentration_mmol_l') is not None and result['value'] is not None:
                ax.scatter([result['value']],[result['concentration_mmol_l']],marker='D',s=30,color='#b44d78')
                ax.axhline(result['concentration_mmol_l'],color='#b44d78',alpha=.2,linestyle=':')
        ax.set_xlabel('Carico (W)');ax.set_ylabel('Lattato (mmol/L)');ax.grid(alpha=.15);ax.legend(fontsize=8)
        out=io.BytesIO();fig.savefig(out,format='png',dpi=150);images.append(('lactate.png','Lattato - curva e misure',out.getvalue(),7.87))
    gas=analysis.get('gas')
    if gas:
        fig=Figure(figsize=(9,6.3),layout='constrained');axes=fig.subplots(2,2);bins=gas['bins'];times=[r['t']/60 for r in bins]
        axes[0,0].plot(times,[r['vo2'] for r in bins],label='VO2');axes[0,0].plot(times,[r['vco2'] for r in bins],label='VCO2');axes[0,0].set(xlabel='Tempo FIT (min)',ylabel='L/min')
        axes[0,1].scatter([r['vo2'] for r in bins],[r['vco2'] for r in bins],s=10);axes[0,1].set(xlabel='VO2 (L/min)',ylabel='VCO2 (L/min) - V-slope')
        for k in ('ve_vo2','ve_vco2'):axes[1,0].plot(times,[r.get(k) for r in bins],label=k.replace('_','/').upper())
        axes[1,0].set(xlabel='Tempo FIT (min)',ylabel='Equivalenti ventilatori')
        for k in ('peto2','petco2'):axes[1,1].plot(times,[r.get(k) for r in bins],label=k.upper())
        axes[1,1].set(xlabel='Tempo FIT (min)',ylabel='Gas end-tidal (mmHg)')
        for ax in axes.flat:
            ax.grid(alpha=.15)
            if ax.get_legend_handles_labels()[0]:ax.legend(fontsize=7)
        out=io.BytesIO();fig.savefig(out,format='png',dpi=150);images.append(('gas.png','Gas - segnali e supporto alla revisione',out.getvalue(),12.39))
    return images


def report(test, athlete, protocol, format, language='it'):
    if test.get('test_type')=='custom':
        from .custom_report import render
        return render(test,athlete,protocol,format,language)
    from .anaerobic import is_anaerobic
    if is_anaerobic(test):
        from .anaerobic_report import render
        return render(test,athlete,protocol,format,language)
    a = test["analysis"]
    title = f"{athlete['surname']} {athlete['name']}"
    metrics = [("Data", test["date"]), ("Protocollo", f"{protocol['name']} - {protocol['version']}"),
               ("Peso (kg)", val(test["settings"].get("weight_kg"))),
               ("Statura (cm)", val(test["settings"].get("height_cm"))),
               ("Ultimo step completo / MAP operativa (W)", val(a["map_w"])),
               ("Interpolazione separata (W)", val(a["map_alt_w"])), ("MAP / peso (W/kg)", val(a["map_wkg"])),
               ("FC massima osservata (bpm)", val(a["fc_max_test_bpm"])),
               ("FC a riposo (bpm)", val(test["settings"].get("rest_hr"))),
               ("Durata riposo prima della misura (s)", val(test["settings"].get("rest_after_s"))),
               ("Durata sforzo (s)", val(a["duration_s"])), ("Copertura potenza", f"{a['power_coverage']*100:.1f}%" if a.get('power_coverage') is not None else 'n.d.')]
    metrics += [('Nascita',athlete.get('birth_date') or val(athlete.get('birth_year'))),('Stato nascita','confermato' if athlete.get('birth_confirmed') else 'da confermare'),
                ('Watt Soglia',val(a.get('threshold_w'))),('Origine soglia',metric_label(a.get('threshold_source') or 'n.d.',language)),('Coefficiente MAP',val(test['settings'].get('threshold_coefficient'))),
                ('FTP dichiarata (W)',val(a.get('ftp_w'))),('FTHR (bpm)',val(a.get('fthr_bpm'))),('RPE ('+test['settings'].get('rpe_scale','CR10 dichiarata')+')',val(test['settings'].get('rpe'))),
                ('Fonte peso',test['settings'].get('weight_source','dichiarato'))]
    for l in test['settings'].get('lactate',[]):
        metrics.append((f"Lattato a {l['at_s']} s (mmol/L)",l['mmol_l']))
    if a.get('preset'):
        metrics += [('Preset analisi',a['preset']['name']+' / '+a['preset']['version']),('Identità preset',a['preset']['hash'][:16])]
        metrics += [('Durata fase incrementale (s)',val(a.get('duration_incremental_s'))),('Potenza media osservata (W)',val(a.get('power_mean_w'))),('Lavoro osservato (kJ)',val(a.get('work_kj'))),('Secondi validi potenza',val(a.get('valid_power_s')))]
        if a.get('terminal_target_w') is not None:metrics += [('Carico terminale nominale (W)',val(a['terminal_target_w'])),('Media ultimi 30 s (W)',val(a.get('terminal_mean_w')))]
        for key,result in a.get('lactate_analysis',{}).get('results',{}).items():
            level=result.get('concentration_mmol_l')
            method_title=('Potenza a '+val(level)+' mmol/L') if level is not None else METHODS.get(key,key)
            metrics.append(('Lattato - '+method_title+' (W)',val(result['value'])+(' / '+scientific_reason(result['reason']) if result.get('reason') else '')))
            if level is not None and 'hr_bpm' in result:
                metrics += [('Lattato - '+val(level)+' mmol/L (W/kg)',val(result['wkg'])+(' / '+scientific_reason(result['weight_reason']) if result.get('weight_reason') else '')),
                            ('Lattato - '+val(level)+' mmol/L (bpm)',val(result['hr_bpm'])+(' / '+scientific_reason(result['hr_reason']) if result.get('hr_reason') else ''))]
        if a.get('gas'):
            g=a['gas'];metrics += [('VO2peak (L/min)',val(g['vo2peak']['value'])),('VO2peak (mL/kg/min)',val(g['vo2peak']['ml_kg_min'])),('VO2peak - finestra (s)',g['vo2peak']['window_s']),('VO2max verificato (L/min)',val(g['vo2max']['value']))]
            for key in ('vt1','vt2'):
                metrics.append((key.upper()+' - marker confermato (s)',val(g['markers'].get(key,{}).get('at_s'))))
                metrics.append((key.upper()+' - suggerimento da rivedere (s)',val(g['suggestions'][key]['value'])))
    for key,value in test['settings'].get('conditions',{}).items():
        if value:metrics.append(('Condizioni - '+key.replace('_',' '),value))
    zone_rows=[]
    for scheme in a.get('zones',[]):
        label=('FC' if scheme['scheme']['channel']=='hr' else tr('Potenza',language))+' / '+metric_label(scheme['scheme']['reference'],language)+' = '+val(scheme['reference_value'])
        if not scheme['zones']: zone_rows.append([label,'n.d.','Riferimento assente','-'])
        for z in scheme['zones']:
            interval=('>=' if z['lower_inclusive'] else '>')+str(round(z['lower_value'],2))
            if z['upper_value'] is not None:interval+=' / '+('<=' if z['inclusive'] else '<')+str(round(z['upper_value'],2))
            zone_rows.append([label,z['name'],interval,'n.d.' if z['seconds'] is None else str(round(z['seconds'],2))])
    from .custom_fields import display_rows
    metrics += display_rows(test)
    stage_rows = [[str(r["number"]), str(r["end_w"]), str(round(r["actual_s"],1)), val(r["power"]["mean"]), val(r["hr"]["mean"]), "Si" if r["complete"] else "No"] for r in a["steps"]]
    metrics=[(tr(k,language),tr(v,language) if isinstance(v,str) and k=='Stato nascita' else v) for k,v in metrics]
    png = chart(test, protocol,language)
    specialist_images=specialist_charts(a)
    note = "Convenzione provvisoria: " + a["method"] + " FC fine step: media ultimi 30 s. Recupero: finestra da t-2 a t+3 s; riferimento media ultimi 5 s di sforzo."
    if test.get('historical'):note=a['method']+' I valori sono dichiarati; nessuna verifica sui campioni.'
    if language=='en':
        note='Provisional convention: last completed constant incremental stage; power coverage at least 95%, without target-adherence validation. Stage HR: last 30 seconds. Recovery: window t-2 to t+3 seconds, reference: last 5 seconds of effort.' if not test.get('historical') else 'Imported declared historical results; original samples unavailable.'
    if a.get('preset'):
        note=a['method']+' Parametri risolti: '+str(a['preset']['parameters'])
    lm=a.get('lactate_analysis',{}).get('method_snapshot')
    if lm and a.get('lactate_analysis',{}).get('points'):
        note += ' Metodo lattato '+lm['method_id']+'; FC media ultimi '+val(lm['hr_window_s'])+' s dello step completo, copertura minima '+val(lm['hr_coverage']*100)+'%. Valori stimati, nessuna estrapolazione o equivalenza automatica con LT/FTP/MLSS.'
    trace = f"Motore {a['engine']} | Test {test['id']} | Revisione {test['revision']} | Protocollo {protocol['id']}"
    if format == "md":
        def md(s):
            return str(s).replace("|", "\\|").replace("\n", " ").replace("<", "&lt;")
        text = f"# {tr('Report test incrementale',language)}\n\n**{md(title)}**\n\n"
        text += "\n".join(f"- {label}: {md(value)}" for label,value in metrics)
        text += '\n\n!['+tr('Tracciato del test',language)+'](assets/test.png)\n\n| '+' | '.join(tr(h,language) for h in ['Step','Target W','Durata s','Media W','FC bpm','Completo'])+' |\n|---|---|---|---|---|---|\n'
        text += "\n".join("| " + " | ".join(row) + " |" for row in stage_rows)
        text += '\n\n## '+tr('Recupero',language)+'\n\n' + "\n".join(f"- {r['after_s']} s: HR {val(r['hr_bpm'])}; HRR {val(r['hrr_bpm'])} bpm" for r in a["recovery"])
        text += '\n\n## '+tr('Metodo e qualità',language)+'\n\n' + note + "\n\n" + "\n".join("- " + w for w in a["warnings"])
        text += '\n\n## '+tr('Note',language)+'\n\n' + md(test.get("notes", "")) + "\n\n" + trace
        text += '\n\n## '+tr('Zone',language)+'\n\n| '+' | '.join(tr(h,language) for h in ['Riferimento','Zona','Limiti assoluti','Secondi'])+' |\n|---|---|---|---|\n'
        text += '\n'.join('| '+' | '.join(md(c) for c in row)+' |' for row in zone_rows)
        text += '\n\n![Progetto Ciclismo - Rodengo Saiano A.S.D.](assets/logo.png)\n\n'+ATTRIBUTION+'\n'
        for filename,label,_,_ in specialist_images:text+='\n\n## '+label+'\n\n!['+label+'](assets/'+filename+')\n'
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("report.md", text)
            z.writestr("assets/test.png", png)
            for filename,_,body,_ in specialist_images:z.writestr('assets/'+filename,body)
            z.write(logo_path(),'assets/logo.png')
            from .store import encoded
            z.writestr('manifest.json',encoded({'test_id':test['id'],'revision':test['revision'],'settings':test['settings'],'analysis':a}))
        return out.getvalue()
    from .pdf_style import document, styles as report_styles, table as styled_table, footer
    from reportlab.platypus import PageBreak, KeepTogether
    out=io.BytesIO();doc=document(out,title);styles=report_styles()
    def p(text,style='BodyText'):
        return Paragraph(escape(str(tr(text,language) if isinstance(text,str) else text)),styles[style])
    story=[p('FUORIGIRI PERFORMANCE LAB','Small'),p(tr('Report test incrementale',language),'Heading2'),p(title,'Title'),
           p(test['date']+'  |  '+protocol['name']+' - '+protocol['version'],'Small'),Spacer(1,.4*cm)]
    summary=[['MAP operativa (W)','MAP / peso (W/kg)','FC massima (bpm)'],[val(a['map_w']),val(a['map_wkg']),val(a['fc_max_test_bpm'])]]
    story.append(styled_table([[p(c) for c in row] for row in summary],[5.9*cm]*3))
    if test.get('historical'):story.append(p('Risultati dichiarati: tracciato non disponibile.','Small'))
    if test['samples']:story += [Spacer(1,.4*cm),Image(io.BytesIO(png),width=17.7*cm,height=8.5*cm)]
    compact=[]
    for index in range(0,len(metrics),2):
        pair=metrics[index:index+2]
        compact.append([p(pair[0][0],'Small'),p(pair[0][1])]+([p(pair[1][0],'Small'),p(pair[1][1])] if len(pair)>1 else ['','']))
    details=styled_table(compact,[5*cm,3.8*cm,5*cm,3.9*cm],False)
    details.setStyle(TableStyle([('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story += [p('Dati e riferimenti','Heading2'),details]
    if a.get('preset') and stage_rows:
        quality=[['Step','Copertura W','Errore W','MAE W','RMSE W','Banda']]
        for step in a['steps']:
            adherence=step.get('adherence',{})
            quality.append([str(step['number']),val(step['power']['coverage']*100)+'%',val(adherence.get('mean_error_w')),val(adherence.get('mae_w')),val(adherence.get('rmse_w')),'Non valutata' if adherence.get('within_band_fraction') is None else val(adherence['within_band_fraction']*100)+'%'])
        story += [p('Aderenza separata dalla completezza','Heading2'),styled_table([[p(c) for c in row] for row in quality],[2.95*cm]*6)]
    if stage_rows:
        story += [p('Step del protocollo','Heading2'),styled_table([[p(tr(c,language)) for c in row] for row in [['Step','Target W','Durata s','Media W','FC bpm','Completo']]+stage_rows],[1.5*cm,3*cm,3*cm,3.4*cm,3.4*cm,3.4*cm])]
    if a['recovery']:
        story += [p('Recupero','Heading2'),styled_table([[p(c) for c in row] for row in [['Dopo (s)','FC (bpm)','HRR (bpm)']]+[[str(r['after_s']),val(r['hr_bpm']),val(r['hrr_bpm'])] for r in a['recovery']]],[5.9*cm]*3)]
    if zone_rows:
        story += [p('Zone','Heading2'),styled_table([[p(c) for c in row] for row in [['Riferimento','Zona','Limiti assoluti','Secondi']]+zone_rows],[7*cm,2*cm,5.7*cm,3*cm])]
    story += [p('Metodo e qualità','Heading2'),p(note)]+[p(w) for w in a['warnings']]
    for _,label,body,height in specialist_images:story += [p(label,'Heading2'),Image(io.BytesIO(body),width=17.7*cm,height=height*cm)]
    story += [p('Note','Heading2'),p(test.get('notes') or 'Nessuna nota.'),Spacer(1,.4*cm),p(trace,'Small')]
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()



def export_csv(store, organization_id):
    athletes = [a for a in store.list("athlete") if a["organization_id"] == organization_id and a.get('status')!='deleted']
    ids = {a["id"] for a in athletes}
    rows = {name:[] for name in CSV_HEADERS}
    for a in athletes:
        rows["atleti"].append({"atleta_id":a["id"],"cognome":a["surname"],"nome":a["name"],"anno_nascita":a.get("birth_year"),"anno_nascita_confermato":"si" if a.get("birth_confirmed") else "no","origine_anno_nascita":a.get("birth_source", ""),"sesso":a.get("sex", ""),"attivo":"si" if a.get("status","active")=="active" else "no","note":a.get("notes", "")})
    for m in store.list("measurement"):
        if m["athlete_id"] in ids and m.get('status') != 'deleted':
            rows["antropometria"].append({"atleta_id":m["athlete_id"],"data":m["date"],"peso_kg":m.get("weight_kg"),"statura_cm":m.get("height_cm"),"peso_fonte":m.get("source", ""),"origine":m.get("origin","inserimento manuale")})
    versions = [];anaerobic_rows=[];lactate_rows=[]
    for t in store.list("test"):
        if t["athlete_id"] not in ids or t.get('status')=='deleted':
            continue
        a,s = t["analysis"],t["settings"]
        protocol = store.get(t["protocol_id"])
        for result in a.get('lactate_analysis',{}).get('results',{}).values():
            if result.get('concentration_mmol_l') is None:continue
            lactate_rows.append({'test_id':t['id'],'test_revision':t['revision'],'atleta_id':t['athlete_id'],'data':t['date'],'protocol_id':t['protocol_id'],
                'mmol_l':result['concentration_mmol_l'],'power_w':result['value'],'power_wkg':result.get('wkg'),'hr_bpm':result.get('hr_bpm'),
                'method_id':result['method_id'],'hr_window_s':result.get('hr_window_s'),'status':result['status'],'power_reason':result.get('reason'),'hr_reason':result.get('hr_reason'),'weight_reason':result.get('weight_reason')})
        if t.get('test_type')=='custom':
            versions.append({'test_id':t['id'],'protocol_version_id':protocol['id'],'version':protocol['version']})
            continue
        from .anaerobic import is_anaerobic,csv_row
        if is_anaerobic(t):
            rows['test_anaerobico'].append(csv_row(t,protocol))
            from .anaerobic import extended_row
            anaerobic_rows.append(extended_row(t,protocol))
            versions.append({'test_id':t['id'],'protocol_version_id':protocol['id'],'version':protocol['version']})
            continue
        rows["test_aerobico"].append({"test_id":t["id"],"atleta_id":t["athlete_id"],"data":t["date"],"protocollo_id":protocol["family"],"durata_s":a["duration_s"],"map_w":a["map_w"],"map_alt_w":a["map_alt_w"],"peso_kg":s.get("weight_kg"),"peso_fonte":"manuale","fc_max_test_bpm":a["fc_max_test_bpm"],"tracciato_parziale":"si" if a.get("power_coverage") is not None and a["power_coverage"] < .95 else "no","note":t.get("notes", "")})
        versions.append({"test_id":t["id"],"protocol_version_id":protocol["id"],"version":protocol["version"]})
        row=rows['test_aerobico'][-1]
        row.update(lattato_2mmol_w=a.get('lactate_2_w'),lattato_4mmol_w=a.get('lactate_4_w'))
        row.update(t.get('historical_fields',{}))
        row.update(test_id=t['id'],atleta_id=t['athlete_id'])
        if not t.get('historical') or t.get('entry_source')=='manuale':
            row.update(soglia_w=a.get('threshold_w'),soglia_origine=a.get('threshold_source'),coeff_soglia=s.get('threshold_coefficient'),fthr_bpm=s.get('fthr_bpm'),peso_fonte=s.get('weight_source'),fc_max_riferimento_bpm=s.get('fc_max_reference_bpm'))
    out = io.BytesIO()
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
        for name, header in CSV_HEADERS.items():
            text = io.StringIO(newline="")
            writer = csv.DictWriter(text,fieldnames=header.split(","))
            writer.writeheader()
            writer.writerows({k:v for k,v in row.items() if k in header.split(',')} for row in rows[name])
            z.writestr(name+".csv",text.getvalue())
        lactate_csv=io.StringIO(newline='')
        lw=csv.DictWriter(lactate_csv,fieldnames=['test_id','test_revision','atleta_id','data','protocol_id','mmol_l','power_w','power_wkg','hr_bpm','method_id','hr_window_s','status','power_reason','hr_reason','weight_reason']);lw.writeheader();lw.writerows(lactate_rows)
        z.writestr('extended/lattato_livelli.csv',lactate_csv.getvalue())
        from .custom_fields import display_rows
        custom_csv=io.StringIO(newline='');cw=csv.writer(custom_csv);cw.writerow(['test_id','protocol_id','scope','field_key','label','type','unit','value_json'])
        for t in store.list('test'):
            if t['athlete_id'] not in ids or t.get('status')=='deleted':continue
            for f in t['analysis'].get('custom_fields',[]):
                data=t['analysis'].get('protocol_custom_values',{}) if f['scope']=='protocol' else t['analysis'].get('custom_values',{})
                cw.writerow([t['id'],t['protocol_id'],f['scope'],f['key'],f['label'],f['type'],f.get('unit',''),json.dumps(data.get(f['key']),ensure_ascii=False)])
        z.writestr('extended/campi_personalizzati.csv',custom_csv.getvalue())
        from .anaerobic import EXTENDED_HEADER
        extended_ana=io.StringIO(newline='');ana_writer=csv.DictWriter(extended_ana,fieldnames=EXTENDED_HEADER.split(','));ana_writer.writeheader();ana_writer.writerows({k:row.get(k) for k in EXTENDED_HEADER.split(',')} for row in anaerobic_rows)
        z.writestr('extended/test_anaerobico.csv',extended_ana.getvalue())
        from .store import encoded
        z.writestr("manifest.json",encoded({"schema":1,"protocol_versions":versions,"note":"CSV dati grezzi: i campi testuali non sono neutralizzati per fogli di calcolo. Campi non misurati vuoti; map_alt_w è interpolazione fra step, non equivalente a metodi storici non documentati."}))
        extended=io.StringIO(newline='')
        writer=csv.DictWriter(extended,fieldnames=['test_id','test_revision','channel','schema_name','schema_version','reference','reference_value','zone','lower_value','lower_inclusive','upper_value','upper_inclusive','seconds'])
        writer.writeheader()
        for t in store.list('test'):
            if t['athlete_id'] not in ids or t.get('status')=='deleted':continue
            for scheme in t['analysis'].get('zones',[]):
                for zone in scheme['zones']:
                    writer.writerow({'test_id':t['id'],'test_revision':t['revision'],'channel':scheme['scheme']['channel'],'schema_name':scheme['scheme']['name'],
                                     'schema_version':scheme['scheme'].get('version',''),'reference':scheme['scheme']['reference'],'reference_value':scheme['reference_value'],
                                     'zone':zone['name'],'lower_value':zone['lower_value'],'lower_inclusive':zone['lower_inclusive'],'upper_value':zone['upper_value'],
                                     'upper_inclusive':zone['inclusive'],'seconds':zone['seconds']})
        z.writestr('extended/zones.csv',extended.getvalue())
        from .maturation import export_files as export_maturation
        export_maturation(z,store,ids)
        referenced_protocols={t['protocol_id'] for t in store.list('test') if t['athlete_id'] in ids and t.get('status')!='deleted'}
        extended_records={kind:[r for r in store.list(kind) if r.get('athlete_id') in ids and r.get('status')!='deleted'] for kind in ('membership','measurement','test')}
        extended_records['group']=[g for g in store.list('group') if g['organization_id']==organization_id]
        extended_records['protocol']=[p for p in store.list('protocol') if p['id'] in referenced_protocols or p.get('organization_id')==organization_id and p.get('status')!='deleted']
        z.writestr('extended/archive.json',encoded(extended_records))
    return out.getvalue()
