"""Record real BRnotes transitions on a neutral canvas for the README."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from notas import QApplication, Note
from PySide6.QtTest import QTest
from PySide6.QtGui import QImage, QPainter, QColor, QFont
from PIL import Image
from shiboken6 import isValid

app=QApplication([])
n=Note(animated=True)
n.setGeometry(180,110,310,270)
n.editor.setPlainText('Uma ideia no papel.\n\nRecolha na borda.\nClique para trazer de volta.')
n.editor.setReadOnly(True)
n.show()
app.processEvents()
frames=[]

def record(label, count):
    for _ in range(count):
        app.processEvents()
        img=QImage(680,430,QImage.Format.Format_RGBA8888)
        img.fill(QColor('#f0efeb'))
        p=QPainter(img);p.setPen(QColor('#29252d'));p.setFont(QFont('Sans Serif',16));p.drawText(24,38,label)
        if isValid(n):
            p.setOpacity(n.windowOpacity());p.drawPixmap(n.x()+12,n.y()-30,n.grab())
        p.end()
        frames.append(Image.frombytes('RGBA',(680,430),bytes(img.constBits())).convert('RGB'))
        QTest.qWait(30)

n.appear();record('BRnotes · abrir',28)
n.move(n.screen().availableGeometry().left(),110)
n.snap(n.screen().availableGeometry());record('BRnotes · recolher na borda',28)
n.restore();record('BRnotes · reabrir',28)
n.close();record('BRnotes · fechar',24)
frames[0].save(Path(__file__).parent/'images/animacoes.gif',save_all=True,append_images=frames[1:],duration=30,loop=0)
