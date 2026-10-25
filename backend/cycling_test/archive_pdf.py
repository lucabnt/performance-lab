"""Archive-specific PDF layout, with a generated linked table of contents."""
from pathlib import Path
from xml.sax.saxutils import escape
from matplotlib import get_data_path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Table, TableStyle
from reportlab.platypus.tableofcontents import TableOfContents
from .pdf_style import styles as base_styles, footer

WIDTH = A4[0] - 3.2 * cm


def styles():
    fonts = Path(get_data_path()) / 'fonts' / 'ttf'
    for name, filename in [('ArchiveSans', 'DejaVuSans.ttf'), ('ArchiveSans-Bold', 'DejaVuSans-Bold.ttf'), ('ArchiveSans-Italic', 'DejaVuSans-Oblique.ttf'), ('ArchiveSans-BoldItalic', 'DejaVuSans-BoldOblique.ttf')]:
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(fonts / filename)))
    pdfmetrics.registerFontFamily('ArchiveSans', normal='ArchiveSans', bold='ArchiveSans-Bold', italic='ArchiveSans-Italic', boldItalic='ArchiveSans-BoldItalic')
    result = base_styles()
    for style in result.byName.values():
        style.fontName = 'ArchiveSans'
        style.textColor = colors.HexColor('#24374e')
    for key in ('BodyText', 'Normal'):
        result[key].fontSize = 9.5
        result[key].leading = 14
        result[key].spaceAfter = 7
    result['Small'].fontSize = 8.5
    result['Small'].leading = 12
    result['Small'].spaceAfter = 6
    result['Heading2'].fontName = 'ArchiveSans-Bold'
    result['Heading2'].leading = 18
    result['Title'].fontName = 'ArchiveSans-Bold'
    result['Title'].fontSize = 23
    result['Title'].leading = 30
    result.add(ParagraphStyle('Chapter', parent=result['Heading2'], fontSize=19, leading=25, spaceBefore=0, spaceAfter=16))
    result.add(ParagraphStyle('Section', parent=result['Heading2'], fontSize=14, leading=19, spaceBefore=12, spaceAfter=12))
    result.add(ParagraphStyle('Subsection', parent=result['Heading2'], fontSize=11, leading=15, spaceBefore=12, spaceAfter=7))
    result.add(ParagraphStyle('TableHeader', parent=result['Small'], fontName='ArchiveSans-Bold', fontSize=8, leading=11, spaceAfter=0))
    result.add(ParagraphStyle('TableCell', parent=result['Small'], fontSize=8.5, leading=12, spaceAfter=0))
    result.add(ParagraphStyle('TOCMain', parent=result['BodyText'], fontName='ArchiveSans-Bold', fontSize=11, leading=16, spaceBefore=8, spaceAfter=2, rightIndent=20))
    result.add(ParagraphStyle('TOCSection', parent=result['BodyText'], fontSize=9.5, leading=12, leftIndent=16, firstLineIndent=0, spaceBefore=0, spaceAfter=0, rightIndent=20))
    return result


def table(rows, widths):
    # Old callers supplied widths whose sum could exceed the printable page.
    widths = [value * WIDTH / sum(widths) for value in widths]
    result = Table(rows, colWidths=widths, repeatRows=1, splitInRow=1, hAlign='LEFT')
    result.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e4eefb')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f6fb')]),
        ('LINEBELOW', (0, 0), (-1, 0), .7, colors.HexColor('#1a62b7')),
    ]))
    result.spaceAfter = 10
    return result


def contents(sheet_styles):
    toc = TableOfContents()
    toc.levelStyles = [sheet_styles['TOCMain'], sheet_styles['TOCSection']]
    toc.dotsMinLevel = 0
    return toc


class ArchiveDocument(BaseDocTemplate):
    def __init__(self, out, title):
        super().__init__(out, pagesize=A4, leftMargin=1.6*cm, rightMargin=1.6*cm, topMargin=1.7*cm, bottomMargin=2.5*cm, title=title, author='Fuorigiri Performance Lab')
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
        self.addPageTemplates(PageTemplate(id='archive', frames=frame, onPage=self.draw_page))

    def draw_page(self, canvas, doc):
        footer(canvas, doc)
        if doc.page > 1:
            canvas.saveState()
            canvas.setFont('ArchiveSans', 8)
            canvas.setFillColor(colors.HexColor('#61738a'))
            canvas.drawString(doc.leftMargin, A4[1]-1*cm, 'FUORIGIRI | Archivio dei test')
            canvas.restoreState()

    def afterFlowable(self, flowable):
        if hasattr(flowable, 'toc_level'):
            key = flowable.toc_key
            title = flowable.toc_title
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title, key, level=flowable.toc_level, closed=False)
            self.notify('TOCEntry', (flowable.toc_level, escape(title), self.page, key))
