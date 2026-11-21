import io
import json
from .report_zip import report_zip
from xml.sax.saxutils import escape
from matplotlib.figure import Figure
from .custom_fields import display_rows


def render(test, athlete, protocol, format, language='it'):
    from .pdf_style import styles, document, table, footer
    from reportlab.platypus import Paragraph, Image, Spacer
    from reportlab.lib.units import cm
    from .branding import ATTRIBUTION, logo_path

    title = athlete['surname'] + ' ' + athlete['name']
    rows = display_rows(test)
    image = None
    samples = test.get('samples', [])
    if samples:
        fig = Figure(figsize=(9, 3.5), layout='constrained')
        ax = fig.subplots()
        ax.plot([r['t'] for r in samples], [r.get('power') for r in samples], color='#1a62b7')
        ax.set(xlabel='Tempo dal file (s)', ylabel='Potenza osservata (W)')
        ax.grid(alpha=0.2)
        out = io.BytesIO()
        fig.savefig(out, format='png', dpi=150)
        image = out.getvalue()
    if format == 'md':
        esc = lambda v: str(v).replace('|', '\\|').replace('\n', ' ')
        text = (
            f'# {esc(protocol["name"])}\n\n## {esc(title)}\n\n{test["date"]} | versione {esc(protocol["version"])}\n\n'
            + test['analysis']['method']
            + '\n\n| Campo | Valore |\n|---|---|\n'
            + ''.join('| ' + esc(k) + ' | ' + esc(v) + ' |\n' for k, v in rows)
            + '\n\n'
            + esc(test.get('notes', ''))
            + '\n'
        )
        if image:
            text += '\n![Tracciato osservato](tracciato.png)\n'
        text += '\n![Logo societario](logo.png)\n\n' + ATTRIBUTION + '\n'
        out = io.BytesIO()
        with report_zip(out) as z:
            z.writestr('report.md', text)
            z.writestr('manifest.json', json.dumps(test, ensure_ascii=False))
            z.writestr('logo.png', logo_path().read_bytes())
            if image:
                z.writestr('tracciato.png', image)
        return out.getvalue()
    out = io.BytesIO()
    s = styles()
    p = lambda v, style='BodyText': Paragraph(escape(str(v)), s[style])
    story = [
        p('FUORIGIRI PERFORMANCE LAB', 'Small'),
        p(protocol['name'], 'Heading2'),
        p(title, 'Title'),
        p(test['date'] + ' | Versione ' + protocol['version'], 'Small'),
        p(test['analysis']['method']),
    ]
    if image:
        story += [Spacer(1, 0.3 * cm), Image(io.BytesIO(image), width=17.7 * cm, height=7 * cm)]
    if rows:
        story += [
            p('Campi e osservazioni', 'Heading2'),
            table([[p(k), p(v)] for k, v in rows], [10 * cm, 7.7 * cm], False),
        ]
    if test.get('notes'):
        story += [p('Note', 'Heading2'), p(test['notes'])]
    story += [p('Provenienza', 'Heading2'), p(test['analysis']['source'] + ' | Revisione ' + test['revision'], 'Small')]
    document(out, title).build(story, onFirstPage=footer, onLaterPages=footer)
    return out.getvalue()
