import unittest
from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtTest import QTest
from shiboken6 import isValid
from notas import QApplication, Note
from paper_toss import trajectory, PaperToss

app = QApplication.instance() or QApplication([])


class PaperTossTest(unittest.TestCase):
    def make_note(self, animated=True):
        note=Note(animated=animated)
        note.show()
        app.processEvents()
        return note

    def test_quick_click_keeps_original_close(self):
        note=self.make_note()
        QTest.mouseClick(note.close_button,Qt.MouseButton.LeftButton)
        self.assertFalse(hasattr(note,'_toss'))
        QTest.qWait(230)
        self.assertFalse(isValid(note))

    def test_hold_only_throws_after_release_and_cleans_up(self):
        note=self.make_note()
        note.set_color('Azul')
        note.editor.setPlainText('Teste temporário')
        QTest.mousePress(note.close_button,Qt.MouseButton.LeftButton)
        QTest.qWait(1050)
        self.assertTrue(note.isVisible())
        self.assertFalse(hasattr(note,'_toss'))
        QTest.mouseRelease(note.close_button,Qt.MouseButton.LeftButton)
        toss=note._toss
        self.assertFalse(note.isVisible())
        self.assertTrue(toss.isVisible())
        self.assertTrue(toss.windowFlags() & Qt.WindowType.WindowTransparentForInput)
        self.assertEqual(note.editor.toPlainText(),'Teste temporário')
        QTest.qWait(int(toss.duration*1000)+150)
        self.assertFalse(isValid(note))
        self.assertFalse(isValid(toss))

    def test_release_outside_cancels(self):
        note=self.make_note()
        QTest.mousePress(note.close_button,Qt.MouseButton.LeftButton)
        QTest.qWait(1050)
        QTest.mouseRelease(note.close_button,Qt.MouseButton.LeftButton,pos=QPoint(-30,50))
        self.assertTrue(note.isVisible())
        self.assertFalse(hasattr(note,'_toss'))
        note.animated=False
        note.close()

    def test_reduced_motion_does_not_throw(self):
        note=self.make_note(animated=False)
        note.close_button.held_long=True
        note.request_close()
        self.assertFalse(hasattr(note,'_toss'))
        app.processEvents()

    def test_ballistic_path_hits_bin_and_descends_on_arrival(self):
        end=QPointF(67,989)
        for start in [QPointF(800,450),QPointF(70,950),QPointF(1500,90),QPointF(50,20)]:
            duration,vx,vy=trajectory(start,end)
            self.assertAlmostEqual(start.x()+vx*duration,end.x())
            self.assertAlmostEqual(start.y()+vy*duration+.5*PaperToss.GRAVITY*duration**2,end.y())
            self.assertLess(vy,0)
            self.assertGreater(vy+PaperToss.GRAVITY*duration,0)
