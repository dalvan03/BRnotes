import unittest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from notas import QApplication, Note, COLORS

app = QApplication.instance() or QApplication([])

class NotesTest(unittest.TestCase):
    def setUp(self):
        self.clipboard_text = app.clipboard().text()
        self.note = Note()
        self.note.show()
        QTest.qWait(100)

    def tearDown(self):
        self.note.close()
        app.clipboard().setText(self.clipboard_text)
        app.processEvents()

    def test_four_edges_preserve_text_and_restore(self):
        area = self.note.screen().availableGeometry()
        self.note.editor.setPlainText('Texto temporário\nsegunda linha')
        for edge in ('left', 'right', 'top', 'bottom'):
            rect = self.note.geometry()
            rect.moveCenter(area.center())
            getattr(rect, {'left':'moveLeft','right':'moveRight','top':'moveTop','bottom':'moveBottom'}[edge])(getattr(area, edge)())
            self.note.setGeometry(rect)
            self.note.snap(area)
            self.assertTrue(self.note.folded)
            self.assertTrue(area.contains(self.note.geometry()))
            self.assertEqual(min(self.note.width(), self.note.height()), 12)
            QTest.mouseClick(self.note, Qt.LeftButton, pos=QPoint(5, 5))
            self.assertFalse(self.note.folded)
            self.assertEqual(self.note.editor.toPlainText(), 'Texto temporário\nsegunda linha')
            self.assertTrue(self.note.close_button.isVisible())

    def test_edit_paste_resize_move_and_close(self):
        self.note.move(400, 300)
        app.processEvents()
        QTest.keyClicks(self.note.editor, 'Ola ')
        app.clipboard().setText('mundo\ncolado')
        QTest.keyClick(self.note.editor, Qt.Key_V, Qt.ControlModifier)
        self.assertEqual(self.note.editor.toPlainText(), 'Ola mundo\ncolado')
        start = self.note.pos()
        QTest.mousePress(self.note, Qt.LeftButton, pos=QPoint(40, 18))
        QTest.mouseMove(self.note, QPoint(90, 58))
        QTest.mouseRelease(self.note, Qt.LeftButton, pos=QPoint(40, 18))
        self.assertNotEqual(start, self.note.pos())
        old = self.note.size()
        corner = QPoint(self.note.width()-2, self.note.height()-2)
        QTest.mousePress(self.note, Qt.LeftButton, pos=corner)
        QTest.mouseMove(self.note, corner + QPoint(55, 35))
        QTest.mouseRelease(self.note, Qt.LeftButton, pos=corner + QPoint(55, 35))
        self.assertGreater(self.note.width(), old.width())
        other = Note()
        other.show()
        self.assertEqual(other.editor.toPlainText(), '')
        QTest.mouseClick(other.close_button, Qt.LeftButton)
        self.assertTrue(self.note.isVisible())

class AnimationTest(unittest.TestCase):
    def test_animation_lifecycle_preserves_content(self):
        note = Note(animated=True)
        note.show()
        note.editor.setPlainText('Não perder durante a animação')
        note.appear()
        QTest.qWait(300)
        self.assertIsNone(note._animation)
        area = note.screen().availableGeometry()
        note.move(area.left(), area.center().y())
        note.snap(area)
        QTest.qWait(320)
        self.assertTrue(note.folded)
        self.assertEqual(note.width(), 12)
        note.restore()
        QTest.qWait(320)
        self.assertFalse(note.folded)
        self.assertEqual(note.editor.toPlainText(), 'Não perder durante a animação')
        note.close()
        QTest.qWait(250)
        # WA_DeleteOnClose removes the C++ object after the exit transition.
        from shiboken6 import isValid
        self.assertFalse(isValid(note))

    def test_seven_colors_are_independent(self):
        first, second = Note(), Note()
        first.editor.setPlainText('Texto')
        for color in COLORS:
            first.color_actions[color].trigger()
            self.assertEqual(first.color_name, color)
            self.assertEqual(second.color_name, 'Amarelo')
            self.assertEqual(first.editor.toPlainText(), 'Texto')
        first.close()
        second.close()


if __name__ == '__main__':
    unittest.main()
