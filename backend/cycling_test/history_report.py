import io
import json
import zipfile
from xml.sax.saxutils import escape
from matplotlib.figure import Figure
from reportlab.platypus import Paragraph, Image, Spacer
from reportlab.lib.units import cm
from .branding import ATTRIBUTION, logo_path
from .locales import tr
from .report_labels import metric_label
from .pdf_style import document, styles, table, footer


def render(data, format, language='it', metric='map_w', statistic='median'):
    title = tr('Storico dei test', language)
    stat_name = (
        ('Mean' if statistic == 'mean' else 'Median')
        if language == 'en'
        else ('Media' if statistic == 'mean' else 'Mediana')
    )
    label = data.get('metric_labels', {}).get(metric) or metric_label(metric, language)
    groups = data['groups']
    fig = Figure(figsize=(10, 4.4), layout='constrained')
    ax = fig.subplots()
    for i, g in enumerate(groups):
        value = g['metrics'][metric][statistic]
        if value is not None:
            ax.scatter(i, value, color='#1a62b7', s=42)
    ax.set_xticks(
        range(len(groups)),
        [g['label'] + '\n' + g.get('protocol_label', g['protocol_id'][:8]) for g in groups],
        rotation=25,
        ha='right',
        fontsize=7,
    )
    ax.set_ylabel(label + ' - ' + stat_name)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', alpha=0.15)
    png = io.BytesIO()
    fig.savefig(png, format='png', dpi=160)
    rows = [['Gruppo / protocollo / soglia', 'Atleti', 'Test', 'Media', 'Mediana', 'Validi / assenti']]
    if language == 'en':
        rows = [['Group / protocol / threshold', 'Athletes', 'Tests', 'Mean', 'Median', 'Valid / missing']]
    for g in groups:
        m = g['metrics'][metric]
        fmt = lambda v: 'n.d.' if v is None else f'{v:.2f}'
        rows.append(
            [
                g['label']
                + ' / '
                + g.get('protocol_label', g['protocol_id'][:8])
                + ' / '
                + metric_label(g['threshold_source'], language),
                str(g['athletes']),
                str(g['tests_selected']),
                fmt(m['mean']),
                fmt(m['median']),
                f"{m['n']} / {m['missing']}",
            ]
        )
    mode = (
        ('Latest test per athlete in each group' if data['query']['mode'] == 'athlete' else 'All tests')
        if language == 'en'
        else ('Ultimo test per atleta in ciascun gruppo' if data['query']['mode'] == 'athlete' else 'Tutti i test')
    )
    note = (
        'Protocol versions and threshold sources are kept separate. Missing values are not zero.'
        if language == 'en'
        else 'Versioni di protocollo e origini della soglia restano separate. I valori assenti non valgono zero.'
    )
    query = json.dumps(data['query'], ensure_ascii=False)
    if format == 'md':
        text = f'# {title}\n\n{label} · {stat_name}\n\n{mode}\n\n{note}\n\n![History](assets/history.png)\n\n'
        for i, row in enumerate(rows):
            text += '| ' + ' | '.join(str(v).replace('|', '\\|').replace('\n', ' ') for v in row) + ' |\n'
            if i == 0:
                text += '|' + '---|' * len(row) + '\n'
        text += '\nFiltri: ' + query + '\n\n![Progetto Ciclismo](assets/logo.png)\n\n' + ATTRIBUTION + '\n'
        out = io.BytesIO()
        with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
            z.writestr('report.md', text)
            z.writestr('assets/history.png', png.getvalue())
            z.writestr('manifest.json', json.dumps(data, ensure_ascii=False))
            z.write(logo_path(), 'assets/logo.png')
        return out.getvalue()
    out = io.BytesIO()
    doc = document(out, title)
    ss = styles()
    p = lambda text, style='BodyText': Paragraph(escape(str(text)), ss[style])
    story = [
        p('FUORIGIRI PERFORMANCE LAB', 'Small'),
        p(title, 'Title'),
        p(label + ' | ' + stat_name, 'Heading2'),
        p(mode),
        p(note, 'Small'),
        Spacer(1, 0.3 * cm),
        Image(io.BytesIO(png.getvalue()), width=17.7 * cm, height=7.8 * cm),
        table([[p(c) for c in r] for r in rows], [7 * cm, 1.6 * cm, 1.4 * cm, 2.5 * cm, 2.5 * cm, 2.7 * cm]),
        p('Filtri e tracciabilità' if language == 'it' else 'Filters and provenance', 'Heading2'),
        p(query, 'Small'),
    ]
    # The downloadable manifest holds complete UUIDs; the PDF keeps the audit concise.
    story.append(
        p(('Risultati sorgente: ' if language == 'it' else 'Source results: ') + str(len(data['rows'])), 'Small')
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return out.getvalue()
