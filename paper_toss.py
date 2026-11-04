"""A transient, input-transparent paper crumple and ballistic throw overlay."""
import math
from PySide6.QtCore import QPointF, QRectF, Qt, QElapsedTimer, QTimer
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPolygonF, QTransform, QLinearGradient
from PySide6.QtWidgets import QWidget


def smooth(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def trajectory(start, end, ceiling=45.0, gravity=1900.0):
    """Constant gravity, continuous velocity and exact arrival at the bin mouth."""
    apex = max(ceiling, min(start.y(), end.y()) - max(100, abs(end.x()-start.x())*.22))
    apex = min(apex, start.y()-1, end.y()-1)
    up = math.sqrt(2 * (start.y()-apex) / gravity)
    down = math.sqrt(2 * (end.y()-apex) / gravity)
    duration = up + down
    return duration, (end.x()-start.x()) / duration, -gravity * up


def affine(source, target):
    """Map one texture triangle onto a folded-paper triangle."""
    a, b, c = source
    u, v, w = target
    dx, dy = b.x()-a.x(), b.y()-a.y()
    ex, ey = c.x()-a.x(), c.y()-a.y()
    det = dx*ey-ex*dy
    m11 = ((v.x()-u.x())*ey-(w.x()-u.x())*dy)/det
    m21 = ((w.x()-u.x())*dx-(v.x()-u.x())*ex)/det
    m12 = ((v.y()-u.y())*ey-(w.y()-u.y())*dy)/det
    m22 = ((w.y()-u.y())*dx-(v.y()-u.y())*ex)/det
    return QTransform(m11, m12, m21, m22,
                      u.x()-m11*a.x()-m21*a.y(), u.y()-m12*a.x()-m22*a.y())


class PaperToss(QWidget):
    CRUMPLE_START = .18
    LAUNCH = 1.0
    GRAVITY = 1900.0

    def __init__(self, texture, origin, screen_area, finished):
        flags = (Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
                 Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.WindowTransparentForInput |
                 Qt.WindowType.WindowDoesNotAcceptFocus)
        super().__init__(None, flags)
        self.setWindowTitle('BRnotes · papel na lixeira')
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setGeometry(screen_area)
        self.texture = texture
        self.origin = QRectF(origin.translated(-screen_area.topLeft()))
        self.start = self.origin.center()
        self.end = QPointF(67, self.height()-91)
        self.flight, self.vx, self.vy = trajectory(self.start, self.end)
        self.impact = self.LAUNCH + self.flight
        self.duration = self.impact + .70
        self.finished_callback = finished
        self.elapsed = 0.0
        self.clock = QElapsedTimer()
        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.tick)
        self.build_mesh()

    def build_mesh(self):
        # The same mesh carries the real note texture all the way into the ball.
        self.vertices = []
        n = 7
        for j in range(n+1):
            for i in range(n+1):
                u, v = i/n*2-1, j/n*2-1
                ripple = 1 + .10*math.sin(i*7.3+j*4.9)
                ball = QPointF(24*u*math.sqrt(1-v*v/2)*ripple,
                               24*v*math.sqrt(1-u*u/2)*ripple)
                self.vertices.append((QPointF(i/n*self.texture.width(), j/n*self.texture.height()),
                                      QPointF(self.origin.left()+i/n*self.origin.width(),
                                              self.origin.top()+j/n*self.origin.height()), ball))
        self.triangles = []
        for j in range(n):
            for i in range(n):
                a=j*(n+1)+i
                for ids in ((a,a+1,a+n+1),(a+1,a+n+2,a+n+1)):
                    self.triangles.append(ids)

    def start_animation(self):
        self.show()
        self.raise_()
        self.clock.start()
        self.timer.start()

    def tick(self):
        self.elapsed = self.clock.elapsed()/1000
        if self.elapsed >= self.duration:
            self.timer.stop()
            self.finished_callback()
            self.close()
        else:
            self.update()

    def ball_position(self, t):
        t = max(0, min(t, self.flight))
        return QPointF(self.start.x()+self.vx*t,
                       self.start.y()+self.vy*t+.5*self.GRAVITY*t*t)

    def draw_bin(self, p, t, front=False):
        rise = smooth(t/.32)
        leave = smooth((t-self.impact-.25)/.45)
        y = self.height()+12 - 103*rise + 112*leave
        # A tiny damped impact response, after the paper crosses the rim.
        since = max(0, t-self.impact)
        bounce = math.sin(since*27)*math.exp(-since*11)*3 if since else 0
        y += bounce
        x = self.end.x()
        if not front:
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor(0,0,0,25))
            p.drawEllipse(QRectF(x-37,y+65,74,9))
            p.setBrush(QColor('#242e38'))
            p.drawEllipse(QRectF(x-32,y-9,64,18))
            return
        body = QPainterPath()
        body.moveTo(x-31,y+1)
        body.lineTo(x-23,y+61)
        body.quadTo(x,y+72,x+23,y+61)
        body.lineTo(x+31,y+1)
        body.quadTo(x,y+13,x-31,y+1)
        gradient = QLinearGradient(x-32,y,x+32,y)
        gradient.setColorAt(0,QColor('#667987'))
        gradient.setColorAt(.4,QColor('#b2c2cb'))
        gradient.setColorAt(1,QColor('#526675'))
        p.fillPath(body,gradient)
        p.save()
        p.setClipPath(body)
        p.setPen(QPen(QColor(35,52,65,65),1.2))
        for offset in range(-24,25,8):
            p.drawLine(QPointF(x+offset,y+10),QPointF(x+offset*.73,y+63))
        for offset in range(18,62,9):
            p.drawLine(QPointF(x-28,y+offset),QPointF(x+28,y+offset))
        p.restore()
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(QColor('#cad5dc'),2.4))
        p.drawArc(QRectF(x-32,y-9,64,18),180*16,180*16)

    def draw_paper(self, p, t):
        if t > self.impact+.18:
            return
        fold = smooth((t-self.CRUMPLE_START)/(self.LAUNCH-self.CRUMPLE_START))
        center = self.ball_position(t-self.LAUNCH) if t >= self.LAUNCH else self.start
        if t > self.impact:
            progress = (t-self.impact)/.18
            center += QPointF(0, progress*40)
        angle = (t-self.LAUNCH)*6 if t >= self.LAUNCH else -.2*fold
        scale = 1-.65*smooth((t-self.impact)/.18)
        cos, sin = math.cos(angle), math.sin(angle)
        targets = []
        for idx, (_, flat, ball) in enumerate(self.vertices):
            # Alternate folding ridges develop before the sheet fully contracts.
            wrinkle = math.sin(math.pi*fold)*math.sin(idx*4.3)*9
            x = (flat.x()-self.start.x())*(1-fold)+(ball.x()+wrinkle)*fold
            y = (flat.y()-self.start.y())*(1-fold)+ball.y()*fold
            targets.append(QPointF(center.x()+(x*cos-y*sin)*scale,
                                   center.y()+(x*sin+y*cos)*scale))
        for index, ids in enumerate(self.triangles):
            src = [self.vertices[i][0] for i in ids]
            dst = [targets[i] for i in ids]
            polygon = QPolygonF(dst)
            p.save()
            clip = QPainterPath();clip.addPolygon(polygon);clip.closeSubpath()
            p.setClipPath(clip)
            p.setTransform(affine(src,dst),True)
            p.drawPixmap(0,0,self.texture)
            p.restore()
            shade = math.sin(index*2.4)
            p.setPen(QPen(QColor(77,53,18,int(45*fold)),.65))
            p.setBrush(QColor(255,255,255,int(shade*65*fold)) if shade>0 else
                       QColor(58,39,15,int(-shade*95*fold)))
            p.drawPolygon(polygon)

    def paintEvent(self, event):
        p=QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.draw_bin(p,self.elapsed)
        self.draw_paper(p,self.elapsed)
        self.draw_bin(p,self.elapsed,front=True)
