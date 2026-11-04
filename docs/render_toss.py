"""Render the actual paper-toss painter for documentation and visual QA."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from notas import QApplication, Note
from paper_toss import PaperToss
from PySide6.QtCore import QRect
from PySide6.QtGui import QImage, QPainter, QColor, QFont
from PIL import Image

app=QApplication([])
note=Note();note.resize(310,270);note.show();app.processEvents()
note.editor.setPlainText('Uma ideia no papel.\n\nMissão cumprida!');note.editor.setReadOnly(True)
note.close_button.hide();note.color_button.hide()
rect=note.paper_rect().toAlignedRect();texture=note.grab(rect)
toss=PaperToss(texture,QRect(470,120,rect.width(),rect.height()),QRect(0,0,860,600),lambda:None)
frames=[]
for i in range(int(toss.duration*40)+1):
    toss.elapsed=i/40
    img=QImage(860,600,QImage.Format.Format_RGBA8888);img.fill(QColor('#f0efeb'))
    p=QPainter(img);p.setPen(QColor('#29252d'));p.setFont(QFont('Sans Serif',18));p.drawText(24,38,'BRnotes · segure × e solte')
    p.drawPixmap(0,0,toss.grab());p.end()
    frames.append(Image.frombytes('RGBA',(860,600),bytes(img.constBits())).convert('RGB'))
output=Path(__file__).parent/'images/lixeira.gif'
frames[0].save(output,save_all=True,append_images=frames[1:],duration=25,loop=0)
contact=Image.new('RGB',(1290,600),'#f0efeb')
for i,t in enumerate([0,.55,.98,1.25,toss.impact-.06,toss.impact+.1]):
    contact.paste(frames[min(len(frames)-1,round(t*40))].resize((430,300)),((i%3)*430,(i//3)*300))
contact.save('/tmp/brnotes-toss-contact.png')
note.close();toss.close()
print('duration',round(toss.duration,2),'seconds;',len(frames),'frames')
