#!/usr/bin/env python3
"""Install/uninstall BRnotes for the current user; never requires root."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

APP_ID = 'brnotes.desktop'
ACTION = "['brnotes.desktop', '_launch', 'BRnotes', 'Nova nota']"
KEY = 301989966  # Qt: Meta + Shift + N


def dbus(method, *args):
    return subprocess.run(['gdbus', 'call', '--session', '--dest', 'org.kde.kglobalaccel',
                           '--object-path', '/kglobalaccel', '--method',
                           'org.kde.KGlobalAccel.' + method, *args],
                          text=True, capture_output=True, timeout=15)


def desktop_quote(value):
    # Desktop Entry Exec quoting, followed by the general string escape layer.
    value = str(value).replace('%', '%%')
    for char in ('\\', '"', '`', '$'):
        value = value.replace(char, '\\' + char)
    return '"' + value.replace('\\', '\\\\') + '"'


def refresh():
    for program, args in [('kbuildsycoca6', []), ('update-desktop-database', [str(DATA / 'applications')])]:
        if shutil.which(program):
            subprocess.run([program, *args], capture_output=True, timeout=30)


def install(no_shortcut=False):
    try:
        import PySide6  # noqa: F401
        import PIL  # noqa: F401
    except ImportError:
        raise SystemExit('Dependências ausentes. No Fedora: sudo dnf install python3-pyside6 python3-pillow')
    if not os.environ.get('DISPLAY'):
        print('Aviso: sessão X11/XWayland não detectada; execute em uma sessão gráfica para usar o app.')
    target = DATA / 'brnotes'
    target.mkdir(parents=True, exist_ok=True)
    for source, name in [('notas.py', 'brnotes.py'), ('LICENSE', 'LICENSE'), ('manage.py', 'manage.py')]:
        src = Path(__file__).resolve().parent / source
        # The installed copy is intended for uninstall only.
        shutil.copy2(src, target / name)
    desktop = DATA / 'applications' / APP_ID
    desktop.parent.mkdir(parents=True, exist_ok=True)
    desktop.write_text('[Desktop Entry]\nType=Application\nName=BRnotes\n'
                       'Comment=Notas temporárias com abas nas bordas da tela\n'
                       f'Exec={desktop_quote(sys.executable)} {desktop_quote(target / "brnotes.py")}\n'
                       'Icon=accessories-text-editor\nTerminal=false\nCategories=Utility;TextEditor;\n'
                       'X-KDE-GlobalAccel-CommandShortcut=true\nStartupNotify=false\n', encoding='utf-8')
    link = DATA / 'kglobalaccel' / APP_ID
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(desktop)
    refresh()
    print(f'BRnotes instalado em {target}')
    if no_shortcut:
        print('Atalho não alterado (--no-shortcut).')
        return
    if not shutil.which('gdbus'):
        print('Configure o atalho manualmente nas Configurações do KDE → Teclado → Atalhos → BRnotes.')
        return
    try:
        # Preserve a shortcut previously customized by the user.
        existing = dbus('shortcut', ACTION)
        if existing.returncode == 0 and existing.stdout.strip() not in ('(@ai [],)', '([],)', '([0],)'):
            print('Atalho existente preservado. Configure em Teclado → Atalhos → BRnotes.')
            return
        available = dbus('isGlobalShortcutAvailable', str(KEY), APP_ID)
        if available.returncode or 'true' not in available.stdout:
            print('Meta+Shift+N indisponível ou KDE inacessível; nenhum atalho foi substituído.')
            print('Configure em Configurações do Sistema → Teclado → Atalhos → BRnotes.')
            return
        registered = dbus('doRegister', ACTION)
        assigned = dbus('setShortcut', ACTION, f'[{KEY}]', '6') if registered.returncode == 0 else registered
        if assigned.returncode or str(KEY) not in assigned.stdout:
            print('Não foi possível ativar o atalho. Configure BRnotes nos atalhos do KDE.')
        else:
            print('Atalho ativado: Meta + Shift + N.')
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f'Aplicativo instalado; configure o atalho manualmente ({exc}).')


def uninstall():
    if shutil.which('gdbus'):
        try:
            dbus('unregister', APP_ID, '_launch')
        except (OSError, subprocess.TimeoutExpired):
            pass
    for path in [DATA / 'kglobalaccel' / APP_ID, DATA / 'applications' / APP_ID,
                 DATA / 'brnotes' / 'brnotes.py', DATA / 'brnotes' / 'LICENSE',
                 DATA / 'brnotes' / 'manage.py']:
        path.unlink(missing_ok=True)
    try:
        (DATA / 'brnotes').rmdir()
    except (OSError, FileNotFoundError):
        pass  # Do not remove unrelated files.
    refresh()
    print('BRnotes desinstalado. Notas abertas não foram encerradas.')


DATA = Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')).expanduser().resolve()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['install', 'uninstall'])
    parser.add_argument('--no-shortcut', action='store_true', help='Não configurar atalho na instalação')
    args = parser.parse_args()
    if os.geteuid() == 0:
        parser.error('Execute como usuário normal, sem sudo.')
    if args.action == 'install':
        install(args.no_shortcut)
    else:
        uninstall()
