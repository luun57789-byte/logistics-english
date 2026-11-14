import glob,re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Table,TableStyle,Spacer,PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
D='/usr/share/fonts/truetype/dejavu/'
pdfmetrics.registerFont(TTFont('DV',D+'DejaVuSans.ttf'));pdfmetrics.registerFont(TTFont('DVB',D+'DejaVuSans-Bold.ttf'));pdfmetrics.registerFont(TTFont('DVI',D+'DejaVuSans.ttf'))
from reportlab.lib.fonts import addMapping
addMapping('DV',0,0,'DV');addMapping('DV',1,0,'DVB')
src=open('src.html').read()
topics=re.findall(r'\{id:"(\w+)",code:"([^"]+)",name:"([^"]+)",en:"([^"]+)"\}',src)
rows=[l.split('|') for l in "".join(open(f).read() for f in sorted(glob.glob('vocab/*.txt'))).strip().split('\n')]
navy=colors.HexColor('#173a5e');amber=colors.HexColor('#e8a317')
H1=ParagraphStyle('h1',fontName='DVB',fontSize=20,leading=24,textColor=navy)
H2=ParagraphStyle('h2',fontName='DVB',fontSize=13,leading=16,textColor=navy,spaceBefore=4,spaceAfter=4)
P=ParagraphStyle('p',fontName='DV',fontSize=8.2,leading=10.2)
T=ParagraphStyle('t',fontName='DVB',fontSize=8.6,leading=10.4)
E=ParagraphStyle('e',fontName='DV',fontSize=7.6,leading=9.4,textColor=colors.HexColor('#55657a'))
esc=lambda s:s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
story=[Paragraph('Logistics English Dock',H1),Spacer(1,3*mm),
 Paragraph(f'Từ vựng tiếng Anh ngành logistics thông dụng trong công việc · {len(rows)} từ · {len(topics)} chủ đề · trình độ A2–B2',P),Spacer(1,3*mm),
 Paragraph('Cách dùng: che cột tiếng Việt để tự kiểm tra; đánh dấu ✓ vào ô trống khi đã thuộc.',P),Spacer(1,5*mm)]
toc=[[Paragraph('<b>Mã</b>',P),Paragraph('<b>Chủ đề</b>',P),Paragraph('<b>Số từ</b>',P)]]
for tid,code,vi,en in topics: toc.append([Paragraph(code,P),Paragraph(f'{esc(en)} – {esc(vi)}',P),Paragraph(str(sum(1 for r in rows if r[4]==tid)),P)])
t=Table(toc,colWidths=[22*mm,120*mm,20*mm]);t.setStyle(TableStyle([('LINEBELOW',(0,0),(-1,-1),0.3,colors.HexColor('#cfd7e1')),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e3e9f0'))]))
story+= [t]
n=0
for tid,code,vi,en in topics:
  ws=[r for r in rows if r[4]==tid]
  story+=[PageBreak(),Paragraph(f'{code} · {esc(en)} <font name="DV" size="10" color="#55657a">– {esc(vi)} ({len(ws)} từ)</font>',H2)]
  data=[[Paragraph('<b>#</b>',P),Paragraph('<b>Từ / cụm từ</b>',P),Paragraph('<b>Nghĩa</b>',P),Paragraph('<b>Ví dụ</b>',P),Paragraph('<b>Cấp</b>',P),Paragraph('<b>✓</b>',P)]]
  for r in ws:
    n+=1
    data.append([Paragraph(str(n),E),Paragraph(esc(r[0]),T),Paragraph(esc(r[1]),P),Paragraph('<i>'+esc(r[2])+'</i>',E),Paragraph(r[3],E),''])
  tb=Table(data,colWidths=[9*mm,40*mm,40*mm,74*mm,12*mm,7*mm],repeatRows=1)
  tb.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),0.3,colors.HexColor('#cfd7e1')),
    ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e3e9f0')),('BOX',(5,1),(5,-1),0.3,colors.HexColor('#cfd7e1')),
    ('TOPPADDING',(0,0),(-1,-1),2.5),('BOTTOMPADDING',(0,0),(-1,-1),2.5)]))
  story.append(tb)
def foot(c,d):
  c.saveState();c.setFillColor(amber);c.rect(14*mm,287*mm,182*mm,1.2*mm,fill=1,stroke=0)
  c.setFont('DV',7.5);c.setFillColor(colors.HexColor('#55657a'));c.drawString(14*mm,8*mm,'Logistics English Dock – Từ vựng logistics');c.drawRightString(196*mm,8*mm,f'Trang {d.page}');c.restoreState()
doc=SimpleDocTemplate('tu-vung-logistics.pdf',pagesize=A4,leftMargin=14*mm,rightMargin=14*mm,topMargin=14*mm,bottomMargin=14*mm,title='Từ vựng tiếng Anh logistics',author='Logistics English Dock')
doc.build(story,onFirstPage=foot,onLaterPages=foot)
print('pdf ok',len(rows))
