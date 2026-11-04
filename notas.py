#!/usr/bin/python3
"""Ephemeral sticky notes for KDE/XWayland. Each launch creates one note."""
import os
import sys
from PIL import Image, ImageFilter

# Absolute positioning is needed for edge tabs, including on Plasma Wayland.
os.environ['QT_QPA_PLATFORM'] = 'xcb'
from PySide6.QtCore import QPoint, QRect, QSize, QRectF, Qt, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, QTimer, QElapsedTimer
from PySide6.QtGui import QCursor, QGuiApplication, QColor, QIcon, QPixmap, QActionGroup, QPainter, QPainterPath, QLinearGradient, QImage, QConicalGradient, QPen
from PySide6.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton, QMenu


def bounded(rect, area):
    w, h = min(rect.width(), area.width()), min(rect.height(), area.height())
    return QRect(max(area.left(), min(rect.x(), area.right() - w + 1)),
                 max(area.top(), min(rect.y(), area.bottom() - h + 1)), w, h)


COLORS = {
    'Vermelho': '#ffb3b3',
    'Laranja': '#ffd09b',
    'Amarelo': '#fff19b',
    'Verde': '#bce8b0',
    'Azul': '#a9d9ff',
    'Anil': '#b8b7ee',
    'Violeta': '#dfb5f1',
}


class CloseButton(QPushButton):
    """Normal clicks close; a left-button hold over one second arms the toss."""
    def __init__(self, parent):
        super().__init__('×', parent)
        self.hold_clock = QElapsedTimer()
        self.held_long = False
        self.feedback = QTimer(self)
        self.feedback.setInterval(32)
        self.feedback.timeout.connect(self.update)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.held_long = False
            self.hold_clock.start()
            self.feedback.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.held_long = self.hold_clock.isValid() and self.hold_clock.elapsed() > 1000
            self.feedback.stop()
            self.hold_clock.invalidate()
        super().mouseReleaseEvent(event)
        self.held_long = False
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.isDown() and self.hold_clock.isValid():
            progress = min(1, self.hold_clock.elapsed()/1000)
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QPen(QColor('#574934'), 1.5))
            painter.drawArc(QRectF(self.rect()).adjusted(2,2,-2,-2),
                            90*16, -int(360*16*progress))


class Note(QWidget):
    def __init__(self, animated=False):
        self.animated = animated
        self._animation = None
        self._closing = False
        super().__init__(None, Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
                         Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle('BRnotes')
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        self.editor = QTextEdit(self)
        self.editor.setAcceptRichText(False)
        self.editor.setPlaceholderText('Escreva aqui…')
        self.editor.setFrameStyle(0)
        self.close_button = CloseButton(self)
        self.close_button.setToolTip('Clique para fechar. Segure por mais de 1 segundo e solte para jogar na lixeira.')
        self.close_button.setAccessibleName('Fechar e descartar nota')
        self.close_button.clicked.connect(self.request_close)
        self.color_button = QPushButton(self)
        wheel = QPixmap(64, 64)
        wheel.fill(Qt.GlobalColor.transparent)
        painter = QPainter(wheel)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        spectrum = QConicalGradient(32, 32, 90)
        for position, color in enumerate(('#ef4444', '#fb923c', '#facc15',
                                          '#4ade80', '#38bdf8', '#6366f1',
                                          '#c45bf0', '#ef4444')):
            spectrum.setColorAt(position / 7, QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(spectrum)
        painter.drawEllipse(QRectF(3, 3, 58, 58))
        painter.end()
        self.color_button.setIcon(QIcon(wheel))
        self.color_button.setIconSize(QSize(18, 18))
        self.color_button.setAccessibleName('Mudar cor da nota')
        self.color_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.color_menu = QMenu(self)
        self.color_menu.setStyleSheet('''
            QMenu { background: #fffdf5; color: #29252d; border: 1px solid #d5cfc0;
                    padding: 5px; font-size: 14px; }
            QMenu::item { padding: 7px 18px 7px 10px; }
            QMenu::item:selected { background: #e8e3d7; }
        ''')
        self.color_group = QActionGroup(self)
        self.color_group.setExclusive(True)
        self.color_actions = {}
        for name, color in COLORS.items():
            swatch = QPixmap(18, 18)
            swatch.fill(QColor(color))
            action = self.color_menu.addAction(QIcon(swatch), name)
            action.setCheckable(True)
            self.color_group.addAction(action)
            action.triggered.connect(lambda checked=False, name=name: self.set_color(name))
            self.color_actions[name] = action
        self.color_button.clicked.connect(self.show_colors)
        self.set_color('Amarelo')
        self.editor.setAccessibleName('Texto da nota')
        self.folded = False
        self.gesture = None
        self.saved = QRect()
        self.setMinimumSize(160, 120)
        screen = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        area = screen.availableGeometry()
        self.setGeometry(bounded(QRect(QCursor.pos() + QPoint(20, 20),
                                       QSize(310, 270)), area))
        self.setToolTip('Arraste a área vazia acima do texto para mover.\nArraste os cantos para redimensionar.\nSolte junto a uma borda para recolher.')
        self.editor.setFocus()

    def set_color(self, name):
        self.color_name = name
        background = COLORS[name]
        hover = QColor(background).darker(110).name()
        self.setStyleSheet(f"""
            Note {{ background: transparent; }}
            QTextEdit {{ background: transparent; color: #29252d; border: 0;
                         font-size: 17px; selection-background-color: #51476b;
                         selection-color: white; }}
            QPushButton {{ border: 0; background: transparent; color: #49404b;
                           font-size: 22px; }}
            QPushButton:hover {{ background: {hover}; color: #29252d; }}
        """)
        self.color_actions[name].setChecked(True)
        self.color_button.setToolTip(f'Mudar cor · {name}')
        self.update()

    def show_colors(self):
        self.color_menu.popup(self.color_button.mapToGlobal(QPoint(0, self.color_button.height())))

    def transition(self, target, opacity, finished, duration=190):
        if not self.animated:
            self.setGeometry(target)
            self.setWindowOpacity(opacity)
            finished()
            return
        if self._animation is not None:
            self._animation.stop()
            self._animation.deleteLater()
        group = QParallelAnimationGroup(self)
        for prop, start, end in ((b'geometry', self.geometry(), target),
                                 (b'windowOpacity', self.windowOpacity(), opacity)):
            animation = QPropertyAnimation(self, prop, group)
            animation.setDuration(duration)
            animation.setStartValue(start)
            animation.setEndValue(end)
            animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
            group.addAnimation(animation)
        self._animation = group

        def complete():
            self._animation = None
            group.deleteLater()
            finished()

        group.finished.connect(complete)
        group.start()

    def appear(self):
        target = self.geometry()
        start = target.adjusted(8, 0, -8, -18)
        self.setGeometry(start)
        self.setWindowOpacity(0)
        self.transition(target, 1, self.editor.setFocus, 220)

    def request_close(self):
        if self._animation is not None or self._closing:
            return
        if self.close_button.held_long and self.animated:
            from paper_toss import PaperToss
            self.color_menu.hide()
            self.close_button.hide()
            self.color_button.hide()
            paper = self.paper_rect().toAlignedRect()
            texture = self.grab(paper)
            # Normalize texture coordinates on high-DPI screens.
            texture = texture.scaled(paper.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                                     Qt.TransformationMode.SmoothTransformation)
            texture.setDevicePixelRatio(1)
            origin = paper.translated(self.pos())
            self._closing = True
            self._toss = PaperToss(texture, origin, self.screen().availableGeometry(), self.close)
            self._toss.start_animation()
            self.hide()
        else:
            self.close()

    def closeEvent(self, event):
        if self.animated and not self._closing:
            event.ignore()
            if self._animation is not None:
                return
            self._closing = True
            self.color_menu.hide()
            rect = self.geometry()
            target = rect.adjusted(10, 8, -10, -8)
            self.transition(target, 0, self.close, 160)
        else:
            super().closeEvent(event)

    def paper_rect(self):
        return QRectF(self.rect()).adjusted(12, 4, -12, -23)

    @staticmethod
    def paper_path(rect):
        path = QPainterPath()
        path.moveTo(rect.left(), rect.top())
        path.lineTo(rect.right(), rect.top())
        path.lineTo(rect.right(), rect.bottom() - 2)
        path.cubicTo(rect.right() - rect.width() * .3, rect.bottom() + 2,
                     rect.left() + rect.width() * .3, rect.bottom() + 2,
                     rect.left(), rect.bottom() - 2)
        path.closeSubpath()
        return path

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        base = QColor(COLORS[self.color_name])
        if self.folded or self.width() < 60 or self.height() < 60:
            painter.fillRect(self.rect(), base)
            return
        rect = self.paper_rect()
        # Cache a blurred alpha shadow per size; typing and color changes reuse it.
        if getattr(self, '_shadow_size', None) != self.size():
            shadow_image = QImage(self.size(), QImage.Format.Format_RGBA8888)
            shadow_image.fill(Qt.GlobalColor.transparent)
            shadow_painter = QPainter(shadow_image)
            shadow_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            for spread in range(12, 0, -1):
                shadow = QPainterPath()
                shadow.moveTo(rect.left() - spread * .08, rect.top() + 1)
                shadow.lineTo(rect.right() + spread * .08, rect.top() + 1)
                shadow.lineTo(rect.right() + spread * .65, rect.bottom() + 5 + spread)
                shadow.quadTo(rect.center().x(), rect.bottom() + 9 + spread,
                              rect.left() - spread * .65, rect.bottom() + 5 + spread)
                shadow.closeSubpath()
                shade = QLinearGradient(0, rect.top(), 0, rect.bottom() + 18)
                shade.setColorAt(0, QColor(30, 23, 14, 0))
                shade.setColorAt(.25, QColor(30, 23, 14, 1))
                shade.setColorAt(.7, QColor(30, 23, 14, 4))
                shade.setColorAt(1, QColor(30, 23, 14, 9))
                shadow_painter.fillPath(shadow, shade)
            shadow_painter.end()
            rgba = Image.frombytes('RGBA', (self.width(), self.height()),
                                   bytes(shadow_image.constBits()))
            blurred = rgba.filter(ImageFilter.GaussianBlur(3.5))
            self._shadow_image = QImage(blurred.tobytes(), self.width(), self.height(),
                                        QImage.Format.Format_RGBA8888).copy()
            self._shadow_size = self.size()
        painter.drawImage(0, 0, self._shadow_image)
        paper = self.paper_path(rect)
        gradient = QLinearGradient(0, rect.top(), 0, rect.bottom())
        gradient.setColorAt(0, base.darker(104))
        gradient.setColorAt(.145, base)
        gradient.setColorAt(.16, base.darker(106))
        gradient.setColorAt(.38, base.darker(102))
        gradient.setColorAt(.80, base)
        gradient.setColorAt(.96, base.lighter(109))
        gradient.setColorAt(1, base.lighter(103))
        painter.fillPath(paper, gradient)
        painter.setClipPath(paper)
        painter.setPen(QColor(255, 255, 255, 65))
        painter.drawLine(rect.topLeft(), rect.topRight())
        painter.setPen(QColor(100, 70, 20, 28))
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

    def resizeEvent(self, event):
        rect = self.paper_rect().toRect()
        self.editor.setGeometry(rect.left() + 12, rect.top() + 32,
                                max(1, rect.width() - 24), max(1, rect.height() - 46))
        self.close_button.setGeometry(rect.right() - 30, rect.top() + 5, 25, 24)
        self.color_button.setGeometry(rect.right() - 58, rect.top() + 5, 25, 24)
        super().resizeEvent(event)

    def edges(self, point):
        rect = self.paper_rect()
        return (point.x() < rect.left() + 6, point.x() >= rect.right() - 6,
                point.y() < rect.top() + 6, point.y() >= rect.bottom() - 6)

    def mousePressEvent(self, event):
        if self._animation is not None or event.button() != Qt.MouseButton.LeftButton:
            return
        if self.folded:
            self.restore()
            return
        edges = self.edges(event.position().toPoint())
        self.gesture = ('resize' if any(edges) else 'move',
                        event.globalPosition().toPoint(), self.geometry(), edges)
        self.grabMouse()

    def mouseMoveEvent(self, event):
        if self.folded:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            return
        if not self.gesture:
            l, r, t, b = self.edges(event.position().toPoint())
            cursor = (Qt.CursorShape.SizeFDiagCursor if (l and t) or (r and b) else
                      Qt.CursorShape.SizeBDiagCursor if (r and t) or (l and b) else
                      Qt.CursorShape.SizeHorCursor if l or r else
                      Qt.CursorShape.SizeVerCursor if t or b else Qt.CursorShape.SizeAllCursor)
            self.setCursor(cursor)
            return
        mode, origin, rect, edges = self.gesture
        delta = event.globalPosition().toPoint() - origin
        if mode == 'move':
            self.move(rect.topLeft() + delta)
        else:
            result = QRect(rect)
            l, r, t, b = edges
            if l:
                result.setLeft(min(rect.left() + delta.x(), rect.right() - 159))
            if r:
                result.setRight(max(rect.right() + delta.x(), rect.left() + 159))
            if t:
                result.setTop(min(rect.top() + delta.y(), rect.bottom() - 119))
            if b:
                result.setBottom(max(rect.bottom() + delta.y(), rect.top() + 119))
            self.setGeometry(result)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.gesture:
            mode = self.gesture[0]
            self.gesture = None
            self.releaseMouse()
            if mode == 'move':
                screen = QGuiApplication.screenAt(event.globalPosition().toPoint()) or self.screen()
                self.snap(screen.availableGeometry())

    def snap(self, area):
        rect = self.geometry()
        distances = {'left': abs(rect.left() - area.left()),
                     'right': abs(rect.right() - area.right()),
                     'top': abs(rect.top() - area.top()),
                     'bottom': abs(rect.bottom() - area.bottom())}
        # Also accept overshooting the boundary during a drag.
        if rect.left() < area.left(): distances['left'] = 0
        if rect.right() > area.right(): distances['right'] = 0
        if rect.top() < area.top(): distances['top'] = 0
        if rect.bottom() > area.bottom(): distances['bottom'] = 0
        edge = min(distances, key=distances.get)
        if distances[edge] > 22:
            return
        self.saved = bounded(rect, area.adjusted(24, 24, -24, -24))
        self.editor.hide()
        self.close_button.hide()
        self.color_button.hide()
        self.color_menu.hide()
        self.setMinimumSize(1, 1)
        tab = bounded(QRect(rect.x(), rect.y(), 58 if edge in ('top', 'bottom') else 12,
                            12 if edge in ('top', 'bottom') else 58), area)
        if edge == 'left': tab.moveLeft(area.left())
        elif edge == 'right': tab.moveRight(area.right())
        elif edge == 'top': tab.moveTop(area.top())
        else: tab.moveBottom(area.bottom())
        def finish_fold():
            self.folded = True
            self.update()
        self.transition(tab, 1, finish_fold, 240)
        self.setToolTip('Clique para abrir a nota')
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def restore(self):
        target = bounded(self.saved, self.screen().availableGeometry())
        self.folded = False

        def finish_restore():
            self.setMinimumSize(160, 120)
            self.editor.show()
            self.close_button.show()
            self.color_button.show()
            self.editor.setFocus()

        self.transition(target, 1, finish_restore, 240)
        self.setToolTip('Arraste a área vazia acima do texto para mover.\nArraste os cantos para redimensionar.')
        self.raise_()
        self.activateWindow()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName('BRnotes')
    app.setDesktopFileName('brnotes')
    note = Note(animated=os.environ.get('BRNOTES_REDUCED_MOTION') != '1')
    note.show()
    note.raise_()
    note.activateWindow()
    if note.animated:
        QTimer.singleShot(0, note.appear)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
