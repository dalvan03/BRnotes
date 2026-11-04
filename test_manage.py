import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import manage


class InstallerTest(unittest.TestCase):
    def test_install_and_uninstall_preserve_unrelated_files(self):
        with tempfile.TemporaryDirectory(prefix='brnotes test ') as temp:
            root = Path(temp)
            with patch.object(manage, 'DATA', root), patch.object(manage, 'refresh'), patch.object(manage, 'dbus'):
                manage.install(no_shortcut=True)
                self.assertTrue((root/'brnotes/brnotes.py').exists())
                self.assertTrue((root/'kglobalaccel/brnotes.desktop').is_symlink())
                desktop = (root/'applications/brnotes.desktop').read_text()
                self.assertIn('Name=BRnotes', desktop)
                self.assertIn('"'+str(root/'brnotes/brnotes.py')+'"', desktop)
                extra = root/'brnotes/keep.txt'
                extra.write_text('unrelated')
                manage.uninstall()
                self.assertTrue(extra.exists())
                self.assertFalse((root/'applications/brnotes.desktop').exists())

    def test_shortcut_conflict_is_not_overwritten(self):
        def response(method, *args):
            return subprocess.CompletedProcess([], 0, '(@ai [],)' if method == 'shortcut' else '(false,)', '')
        with tempfile.TemporaryDirectory() as temp, patch.object(manage, 'DATA', Path(temp)), patch.object(manage, 'refresh'), patch.object(manage.shutil, 'which', return_value='/bin/gdbus'), patch.object(manage, 'dbus', side_effect=response) as bus:
            manage.install()
            self.assertNotIn('setShortcut', [call.args[0] for call in bus.call_args_list])
