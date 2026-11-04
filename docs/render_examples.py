"""Generate README images from the real widgets, with fictional example text."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from notas import QApplication, Note, COLORS
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter, QColor, QFont

app = QApplication([])
out = Path(__file__).parent / 'images'
out.mkdir(exist_ok=True)


def canvas(w, h):
    image = QImage(w, h, QImage.Format.Format_ARGB32)
    image.fill(QColor('#f0efeb'))
    return image


def note(color, text, w=300, h=270):
    n = Note()
    n.resize(w, h)
    n.set_color(color)
    n.editor.setPlainText(text)
    n.editor.setReadOnly(True)  # Hide caret in documentation only.
    n.show()
    app.processEvents()
    pix = n.grab()
    n.close()
    return pix


hero = canvas(1040, 440)
p = QPainter(hero)
p.setPen(QColor('#29252d'))
p.setFont(QFont('Sans Serif', 30, QFont.Weight.Bold))
p.drawText(35, 60, 'BRnotes')
p.setFont(QFont('Sans Serif', 13))
p.drawText(35, 94, 'Uma ideia. Um atalho. Uma nota.')
for x, y, color, text in [
    (24, 125, 'Amarelo', 'Ideias para hoje\n\n• Esboçar o projeto\n• Testar uma ideia\n• Compartilhar com todos'),
    (365, 120, 'Verde', 'Lembrete rápido\n\nMeta + Shift + N\nabre uma nova nota.'),
    (705, 128, 'Violeta', 'Espaço para pensar\n\nArraste até a borda\npara recolher.\n\nClique na aba para voltar.')]:
    p.drawPixmap(x, y, note(color, text))
p.end()
hero.save(str(out / 'brnotes.png'))

colors = canvas(1040, 600)
p = QPainter(colors)
for idx, color in enumerate(COLORS):
    col, row = idx % 4, idx // 4
    p.drawPixmap(10 + col * 258, 15 + row * 290, note(color, color+'\n\nSua nota, sua cor.', 250, 270))
p.end()
colors.save(str(out / 'cores.png'))

edge = canvas(940, 345)
p = QPainter(edge)
p.setPen(QColor('#29252d'));p.setFont(QFont('Sans Serif', 13))
p.drawText(30, 32, '1. Escreva');p.drawText(352, 32, '2. Recolha na borda');p.drawText(640, 32, '3. Clique para reabrir')
p.drawPixmap(15, 55, note('Azul', 'Minha ideia continua aqui.\n\nMesmo recolhida.', 280, 270))
p.fillRect(340, 65, 255, 245, QColor('#e1e0db'))
n=Note();n.set_color('Azul');n.show();app.processEvents();area=n.screen().availableGeometry();n.move(area.left(),area.center().y());n.snap(area);app.processEvents();p.drawPixmap(340,150,n.grab());n.close()
p.drawPixmap(625,55,note('Azul','Minha ideia continua aqui.\n\nMesmo recolhida.',280,270))
p.end();edge.save(str(out/'bordas.png'))
print('Generated:', ', '.join(p.name for p in out.glob('*.png')))
