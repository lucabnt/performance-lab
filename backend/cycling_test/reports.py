import csv
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

CSV_HEADERS = {
    "atleti": "atleta_id,cognome,nome,anno_nascita,anno_nascita_confermato,origine_anno_nascita,sesso,attivo,note",
    "antropometria": "atleta_id,data,peso_kg,statura_cm,peso_fonte,origine",
    "test_aerobico": "test_id,atleta_id,data,protocollo_id,durata_s,map_w,map_alt_w,peso_kg,peso_fonte,soglia_w,coeff_soglia,soglia_origine,lattato_2mmol_w,lattato_4mmol_w,fc_max_test_bpm,fc_max_riferimento_bpm,fthr_bpm,fthr_pct_fcmax,lavoro_battito_j,lavoro_battito_max_j,cadenza_media_rpm,cadenza_max_rpm,rapporto_trasm_m,pedivella_m,segnale_fc_interrotto,referto_leggibile,tracciato_parziale,note",
}


def chart(test, protocol):
    fig = Figure(figsize=(10, 4.8), layout="constrained")
    axes = fig.subplots(3, 1, sharex=True)
    samples = test["samples"]
    if not samples:
        axes[0].text(.5,.5,'Risultato storico: tracciato non disponibile',ha='center',transform=axes[0].transAxes)
        out=io.BytesIO();fig.savefig(out,format='png',dpi=160)
        return out.getvalue()
    for ax, field, label, color in zip(axes, ("power", "hr", "cadence"), ("Potenza (W)", "FC (bpm)", "Cadenza (rpm)"), ("#247d70", "#b85850", "#637caa")):
        ax.plot([r["t"]/60 for r in samples], [r.get(field) for r in samples], color=color, linewidth=1)
        ax.set_ylabel(label, fontsize=8)
        ax.grid(alpha=.15)
        ax.tick_params(labelsize=8)
        ax.axvline(test["settings"]["end_s"]/60, color="#555555", linestyle="--", linewidth=.8)
    offset = test["settings"]["offset_s"]
    axes[0].plot([(p[0]+offset)/60 for p in protocol["definition"]["points"]], [p[1] for p in protocol["definition"]["points"]], color="#abb2af", linewidth=1, label="Target")
    axes[0].set_xlim(0, samples[-1]["t"]/60)
    axes[-1].set_xlabel("Tempo trascorso (min)", fontsize=8)
    out = io.BytesIO()
    fig.savefig(out, format="png", dpi=160)
    return out.getvalue()


def val(value):
    return "n.d." if value is None else str(value)


def report(test, athlete, protocol, format):
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
                ('Watt Soglia',val(a.get('threshold_w'))),('Origine soglia',val(a.get('threshold_source'))),('Coefficiente MAP',val(test['settings'].get('threshold_coefficient'))),
                ('FTP dichiarata (W)',val(a.get('ftp_w'))),('FTHR (bpm)',val(a.get('fthr_bpm'))),('RPE (1-10)',val(test['settings'].get('rpe'))),
                ('Fonte peso',test['settings'].get('weight_source','dichiarato'))]
    for l in test['settings'].get('lactate',[]):
        metrics.append((f"Lattato a {l['at_s']} s (mmol/L)",l['mmol_l']))
    zone_rows=[]
    for scheme in a.get('zones',[]):
        label=scheme['scheme']['channel']+' / '+scheme['scheme']['reference']+' = '+val(scheme['reference_value'])
        if not scheme['zones']: zone_rows.append([label,'n.d.','Riferimento assente','-'])
        for z in scheme['zones']:
            interval=('>=' if z['lower_inclusive'] else '>')+str(round(z['lower_value'],2))
            if z['upper_value'] is not None:interval+=' / '+('<=' if z['inclusive'] else '<')+str(round(z['upper_value'],2))
            zone_rows.append([label,z['name'],interval,str(round(z['seconds'],2))])
    stage_rows = [[str(r["number"]), str(r["end_w"]), str(round(r["actual_s"],1)), val(r["power"]["mean"]), val(r["hr"]["mean"]), "Si" if r["complete"] else "No"] for r in a["steps"]]
    png = chart(test, protocol)
    note = "Convenzione provvisoria: " + a["method"] + " FC fine step: media ultimi 30 s. Recupero: finestra da t-2 a t+3 s; riferimento media ultimi 5 s di sforzo."
    trace = f"Motore {a['engine']} | Test {test['id']} | Revisione {test['revision']} | Protocollo {protocol['id']}"
    if format == "md":
        def md(s):
            return str(s).replace("|", "\\|").replace("\n", " ").replace("<", "&lt;")
        text = f"# Report test incrementale\n\n**{md(title)}**\n\n"
        text += "\n".join(f"- {label}: {md(value)}" for label,value in metrics)
        text += "\n\n![Tracciato del test](assets/test.png)\n\n| Step | Target W | Durata s | Media W | FC bpm | Completo |\n|---|---|---|---|---|---|\n"
        text += "\n".join("| " + " | ".join(row) + " |" for row in stage_rows)
        text += "\n\n## Recupero\n\n" + "\n".join(f"- {r['after_s']} s: FC {val(r['hr_bpm'])}; HRR {val(r['hrr_bpm'])} bpm" for r in a["recovery"])
        text += "\n\n## Metodo e qualità\n\n" + note + "\n\n" + "\n".join("- " + w for w in a["warnings"])
        text += "\n\n## Note\n\n" + md(test.get("notes", "")) + "\n\n" + trace
        text += '\n\n## Zone\n\n| Riferimento | Zona | Limiti assoluti | Secondi |\n|---|---|---|---|\n'
        text += '\n'.join('| '+' | '.join(md(c) for c in row)+' |' for row in zone_rows)
        out = io.BytesIO()
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("report.md", text)
            z.writestr("assets/test.png", png)
            from .store import encoded
            z.writestr('manifest.json',encoded({'test_id':test['id'],'revision':test['revision'],'settings':test['settings'],'analysis':a}))
        return out.getvalue()
    out = io.BytesIO()
    doc = SimpleDocTemplate(out, pagesize=(21*cm,29.7*cm), rightMargin=1.6*cm,leftMargin=1.6*cm,topMargin=1.5*cm,bottomMargin=1.7*cm)
    styles = getSampleStyleSheet()
    styles['Heading2'].keepWithNext = True
    def p(s, style="BodyText"):
        return Paragraph(escape(str(s)), styles[style])
    story = [p("CICLO TEST / REPORT INCREMENTALE", "Heading2"), p(title, "Title")]
    table = Table([[p(k), p(v)] for k,v in metrics], colWidths=[10*cm,7.6*cm])
    table.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,0),(-1,-1),[colors.HexColor("#f2f6f4"),colors.white]),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    story += [table, Spacer(1,.3*cm), Image(io.BytesIO(png),width=17.5*cm,height=8.4*cm),p("Step del protocollo", "Heading2")]
    table = Table([["Step","Target W","Durata s","Media W","FC bpm","Completo"]]+stage_rows, repeatRows=1, colWidths=[1.5*cm,2.7*cm,2.7*cm,3*cm,3*cm,3*cm])
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#247d70")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f2f6f4")]),("FONTSIZE",(0,0),(-1,-1),9),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
    from reportlab.platypus import KeepTogether
    story += [table,KeepTogether([p("Recupero", "Heading2")] + [p(f"{r['after_s']} s: FC {val(r['hr_bpm'])} bpm; HRR {val(r['hrr_bpm'])} bpm") for r in a["recovery"]])]
    story += [p("Metodo e qualità", "Heading2"),p(note)] + [p(w) for w in a["warnings"]]
    story += [p("Note", "Heading2"),p(test.get("notes", "") or "Nessuna nota."),Spacer(1,.3*cm),p(trace)]
    if zone_rows:
        story.append(p('Zone', 'Heading2'))
        table=Table([[p(c) for c in row] for row in [['Riferimento','Zona','Limiti assoluti','Secondi']]+zone_rows],repeatRows=1,colWidths=[6*cm,2*cm,6*cm,3.6*cm])
        table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
        story.append(table)
    def footer(canvas, doc):
        canvas.setFont("Helvetica",8)
        canvas.drawString(1.6*cm,cm,"Ciclo Test | Analisi descrittiva, non diagnosi")
        canvas.drawRightString(19.4*cm,cm,str(doc.page))
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return out.getvalue()


def export_csv(store, organization_id):
    athletes = [a for a in store.list("athlete") if a["organization_id"] == organization_id and a.get('status')!='deleted']
    ids = {a["id"] for a in athletes}
    rows = {"atleti": [], "antropometria": [], "test_aerobico": []}
    for a in athletes:
        rows["atleti"].append({"atleta_id":a["id"],"cognome":a["surname"],"nome":a["name"],"anno_nascita":a.get("birth_year"),"anno_nascita_confermato":"si" if a.get("birth_confirmed") else "no","origine_anno_nascita":a.get("birth_source", ""),"sesso":a.get("sex", ""),"attivo":"si" if a.get("status","active")=="active" else "no","note":a.get("notes", "")})
    for m in store.list("measurement"):
        if m["athlete_id"] in ids:
            rows["antropometria"].append({"atleta_id":m["athlete_id"],"data":m["date"],"peso_kg":m.get("weight_kg"),"statura_cm":m.get("height_cm"),"peso_fonte":m.get("source", ""),"origine":"inserimento manuale"})
    versions = []
    for t in store.list("test"):
        if t["athlete_id"] not in ids or t.get('status')=='deleted':
            continue
        a,s = t["analysis"],t["settings"]
        protocol = store.get(t["protocol_id"])
        rows["test_aerobico"].append({"test_id":t["id"],"atleta_id":t["athlete_id"],"data":t["date"],"protocollo_id":protocol["family"],"durata_s":a["duration_s"],"map_w":a["map_w"],"map_alt_w":a["map_alt_w"],"peso_kg":s.get("weight_kg"),"peso_fonte":"manuale","fc_max_test_bpm":a["fc_max_test_bpm"],"tracciato_parziale":"si" if a.get("power_coverage") is not None and a["power_coverage"] < .95 else "no","note":t.get("notes", "")})
        versions.append({"test_id":t["id"],"protocol_version_id":protocol["id"],"version":protocol["version"]})
        row=rows['test_aerobico'][-1]
        row.update(t.get('historical_fields',{}))
        row.update(test_id=t['id'],atleta_id=t['athlete_id'])
        if not t.get('historical'):
            row.update(soglia_w=a.get('threshold_w'),soglia_origine=a.get('threshold_source'),coeff_soglia=s.get('threshold_coefficient'),fthr_bpm=s.get('fthr_bpm'),peso_fonte=s.get('weight_source'),fc_max_riferimento_bpm=s.get('fc_max_reference_bpm'))
    out = io.BytesIO()
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
        for name, header in CSV_HEADERS.items():
            text = io.StringIO(newline="")
            writer = csv.DictWriter(text,fieldnames=header.split(","))
            writer.writeheader()
            writer.writerows(rows[name])
            z.writestr(name+".csv",text.getvalue())
        from .store import encoded
        z.writestr("manifest.json",encoded({"schema":1,"protocol_versions":versions,"note":"CSV dati grezzi: i campi testuali non sono neutralizzati per fogli di calcolo. Campi non misurati vuoti; map_alt_w è interpolazione fra step, non equivalente a metodi storici non documentati."}))
    return out.getvalue()
