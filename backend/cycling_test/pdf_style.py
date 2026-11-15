"""Shared fixed suite identity and restrained report typography."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from .branding import ATTRIBUTION, logo_path

BLUE=colors.HexColor('#1a62b7')
INK=colors.HexColor('#24374e')
def document(out,title):
    return SimpleDocTemplate(out,pagesize=A4,leftMargin=1.6*cm,rightMargin=1.6*cm,
        topMargin=1.5*cm,bottomMargin=2.5*cm,title=title,author='Fuorigiri Performance Lab')

def styles():
    s=getSampleStyleSheet()
    for key in ('BodyText','Normal'):
        s[key].fontSize=9;s[key].leading=13;s[key].textColor=INK
    s['Title'].fontName='Helvetica-Bold';s['Title'].fontSize=24;s['Title'].leading=29;s['Title'].textColor=INK;s['Title'].alignment=0
    s['Heading2'].textColor=BLUE;s['Heading2'].fontSize=13;s['Heading2'].spaceBefore=16;s['Heading2'].spaceAfter=9;s['Heading2'].keepWithNext=True
    s.add(s['BodyText'].clone('Small',fontSize=7.5,leading=10,textColor=colors.HexColor('#61738a')))
    return s

def table(rows,widths,header=True):
    t=Table(rows,colWidths=widths,repeatRows=1 if header else 0,hAlign='LEFT')
    commands=[('VALIGN',(0,0),(-1,-1),'TOP'),('FONTSIZE',(0,0),(-1,-1),9),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
        ('ROWBACKGROUNDS',(0,1 if header else 0),(-1,-1),[colors.HexColor('#f2f6fb'),colors.white]),
        ('LINEBELOW',(0,0),(-1,0),.6,BLUE)]
    if header: commands.extend([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4eefb')),('TEXTCOLOR',(0,0),(-1,0),INK),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold')])
    t.setStyle(TableStyle(commands));return t

def footer(canvas,doc):
    canvas.saveState();w,h=A4
    canvas.setStrokeColor(colors.HexColor('#dbe4ef'));canvas.line(doc.leftMargin,2.1*cm,w-doc.rightMargin,2.1*cm)
    canvas.drawImage(str(logo_path()),doc.leftMargin,.55*cm,width=2.2*cm,height=2.2*cm*707/1104,mask='auto',preserveAspectRatio=True)
    x=doc.leftMargin+2.5*cm
    canvas.setFillColor(INK);canvas.setFont('Helvetica',7)
    # Exact attribution, wrapped only for layout.
    words=ATTRIBUTION.split(' per ',1)
    canvas.drawString(x,1.45*cm,words[0]);canvas.drawString(x,1.08*cm,'per '+words[1])
    canvas.setFillColor(colors.HexColor('#61738a'));canvas.setFont('Helvetica',6.5)
    canvas.drawString(x,.65*cm,'Fuorigiri Performance Lab | Analisi descrittiva')
    canvas.drawRightString(w-doc.rightMargin,.8*cm,str(doc.page));canvas.restoreState()
