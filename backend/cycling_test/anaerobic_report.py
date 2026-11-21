"""Reports for short all-out tests, with protocol and provenance visible."""

import io
from .report_zip import report_zip
from xml.sax.saxutils import escape
from matplotlib.figure import Figure
from .anaerobic import LABELS, FAMILIES


def render(test, athlete, protocol, format, language='it'):
    from .pdf_style import document, styles, table, footer
    from reportlab.platypus import Paragraph, Image, Spacer
    from reportlab.lib.units import cm

    a = test['analysis']
    spec = a['protocol_snapshot']
    title = athlete['surname'] + ' ' + athlete['name']
    metrics = [(label, a.get(key)) for key, label in LABELS.items() if a.get(key) is not None]
    if a.get('fc_max_test_bpm') is not None:
        metrics.append(('FC massima osservata (bpm)', a['fc_max_test_bpm']))
    values = [(label, f'{value:.2f}') for label, value in metrics]
    conditions = [
        ('Tipo', FAMILIES[test['test_type']]),
        ('Durata nominale (s)', spec['duration_s']),
        ('Coppia frenante (N.m/kg)', spec.get('torque_nm_kg') or 'non documentata'),
        ('Dispositivo', spec.get('device') or 'non documentato'),
        (
            'Partenza',
            {'unknown': 'non documentata', 'stationary': 'da fermo', 'flying': 'lanciata'}.get(
                spec.get('start'), 'non documentata'
            ),
        ),
        ('Finestra picco (s)', spec.get('peak_window_s') or 'non documentata'),
        ('Finestra finale (s)', spec.get('end_window_s') or 'non documentata'),
        (
            'Origine',
            {
                'computed': 'Calcolato dal tracciato',
                'manual': 'Dichiarato manualmente',
                'legacy-csv': 'Storico CSV dichiarato',
            }.get(a['source'], a['source']),
        ),
        ('Peso (kg)', test['settings'].get('weight_kg') or 'non disponibile'),
        ('Fonte peso', test['settings'].get('weight_source', 'non documentata')),
    ]
    from .custom_fields import display_rows

    conditions += display_rows(test)
    samples = test.get('samples', [])
    png = None
    if samples:
        fig = Figure(figsize=(8, 3.4), layout='constrained')
        ax = fig.subplots()
        ax.plot([r['t'] for r in samples], [r.get('power') for r in samples], color='#1a62b7', linewidth=1.7)
        start = test['settings']['offset_s']
        ax.axvspan(start, start + spec['duration_s'], alpha=0.12, color='#1a62b7')
        ax.set(xlabel='Tempo dal file (s)', ylabel='Potenza (W)')
        ax.grid(alpha=0.2)
        ax.spines[['top', 'right']].set_visible(False)
        image = io.BytesIO()
        fig.savefig(image, format='png', dpi=160)
        png = image.getvalue()
    if format == 'md':
        text = f'# Fuorigiri Performance Lab\n\n## {FAMILIES[test["test_type"]]} - {title}\n\n{test["date"]} | {protocol["name"]} | {protocol["version"]}\n\n'
        for heading, rows in [('Risultati', values), ('Metodo e riferimenti', conditions)]:
            text += (
                '### '
                + heading
                + '\n\n| Campo | Valore |\n|---|---|\n'
                + ''.join(
                    '| '
                    + str(k).replace('|', '\\|').replace('\n', ' ')
                    + ' | '
                    + str(v).replace('|', '\\|').replace('\n', ' ')
                    + ' |\n'
                    for k, v in rows
                )
                + '\n'
            )
        if png:
            text += '![Potenza nel tempo](potenza.png)\n\n'
        text += (
            '### Qualità e limiti\n\n'
            + a['method']
            + '\n\n'
            + '\n'.join('- ' + w for w in a['warnings'])
            + '\n\n'
            + test.get('notes', '')
            + '\n\nRevisioni: '
            + test['revision']
            + ' | Metodo: '
            + a['engine']
            + '\n'
        )
        from .branding import ATTRIBUTION, logo_path

        text += '\n---\n\n![Progetto Ciclismo](logo.png)\n\n' + ATTRIBUTION + '\n'
        out = io.BytesIO()
        with report_zip(out) as z:
            z.writestr('report.md', text)
            z.writestr('logo.png', logo_path().read_bytes())
            if png:
                z.writestr('potenza.png', png)
        return out.getvalue()
    out = io.BytesIO()
    s = styles()
    p = lambda text, style='BodyText': Paragraph(escape(str(text)), s[style])
    story = [
        p('FUORIGIRI PERFORMANCE LAB', 'Small'),
        p(FAMILIES[test['test_type']], 'Heading2'),
        p(title, 'Title'),
        p(test['date'] + ' | ' + protocol['name'] + ' | ' + protocol['version'], 'Small'),
        Spacer(1, 0.3 * cm),
    ]
    if png:
        story.append(Image(io.BytesIO(png), width=17.7 * cm, height=7.5 * cm))
    for heading, rows in [('Risultati', values), ('Metodo e riferimenti', conditions)]:
        compact = []
        for i in range(0, len(rows), 2):
            pair = rows[i : i + 2]
            compact.append(
                [p(pair[0][0], 'Small'), p(pair[0][1])]
                + ([p(pair[1][0], 'Small'), p(pair[1][1])] if len(pair) > 1 else ['', ''])
            )
        story += [p(heading, 'Heading2'), table(compact, [6.2 * cm, 2.65 * cm, 6.2 * cm, 2.65 * cm], False)]
    story += [p('Qualità e limiti', 'Heading2'), p(a['method'])] + [p(w) for w in a['warnings']]
    if test.get('notes'):
        story += [p('Note', 'Heading2'), p(test['notes'])]
    story += [Spacer(1, 0.3 * cm), p('Revisione ' + test['revision'] + ' | Metodo ' + a['engine'], 'Small')]
    document(out, title).build(story, onFirstPage=footer, onLaterPages=footer)
    return out.getvalue()
