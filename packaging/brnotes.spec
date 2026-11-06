%global commit d6f151ed4c0ee85d904e8e2cd57cdf7dde909810
Name:           brnotes
Version:        0.1.0
Release:        1%{?dist}
Summary:        Disposable sticky notes with screen-edge tabs
License:        MIT
URL:            https://github.com/dalvan03/BRnotes
Source0:        %{url}/archive/%{commit}/BRnotes-%{commit}.tar.gz
Source1:        brnotes.desktop
Source2:        io.github.dalvan03.BRnotes.svg
Source3:        io.github.dalvan03.BRnotes.metainfo.xml
BuildArch:      noarch
BuildRequires:  python3
BuildRequires:  python3-pyside6
BuildRequires:  python3-pillow
BuildRequires:  desktop-file-utils
BuildRequires:  appstream
Requires:       python3 >= 3.10
Requires:       python3-pyside6
Requires:       python3-pillow
Requires:       xorg-x11-server-Xwayland

%description
Temporary sticky notes for KDE Plasma, with seven colors, paper-like shading,
screen-edge tabs and a paper-toss animation. Notes are discarded when closed.
Uses X11/XWayland. Configure a global shortcut in KDE System Settings.

%prep
%autosetup -n BRnotes-%{commit}

%build
# Pure Python application; no compilation required.

%install
install -Dpm0644 notas.py %{buildroot}%{_datadir}/brnotes/notas.py
install -Dpm0644 paper_toss.py %{buildroot}%{_datadir}/brnotes/paper_toss.py
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/brnotes <<'LAUNCHER'
#!/bin/sh
exec /usr/bin/python3 /usr/share/brnotes/notas.py "$@"
LAUNCHER
chmod 0755 %{buildroot}%{_bindir}/brnotes
install -Dpm0644 %{SOURCE1} %{buildroot}%{_datadir}/applications/brnotes.desktop
install -Dpm0644 %{SOURCE2} %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/io.github.dalvan03.BRnotes.svg
install -Dpm0644 %{SOURCE3} %{buildroot}%{_datadir}/metainfo/io.github.dalvan03.BRnotes.metainfo.xml
mkdir -p %{buildroot}%{_datadir}/kglobalaccel
ln -s ../applications/brnotes.desktop %{buildroot}%{_datadir}/kglobalaccel/brnotes.desktop

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/brnotes.desktop
appstreamcli validate --no-net %{buildroot}%{_datadir}/metainfo/io.github.dalvan03.BRnotes.metainfo.xml
/usr/bin/python3 -m unittest test_manage -v
/usr/bin/python3 -c "import ast, pathlib; [ast.parse(p.read_text()) for p in pathlib.Path('%{buildroot}%{_datadir}/brnotes').glob('*.py')]"

%files
%license LICENSE
%doc README.md CONTRIBUTING.md
%{_bindir}/brnotes
%{_datadir}/brnotes/
%{_datadir}/applications/brnotes.desktop
%{_datadir}/kglobalaccel/brnotes.desktop
%{_datadir}/icons/hicolor/scalable/apps/io.github.dalvan03.BRnotes.svg
%{_datadir}/metainfo/io.github.dalvan03.BRnotes.metainfo.xml

%changelog
* Thu Nov 05 2026 Dalvan (dalvan03) - 0.1.0-1
- Initial community RPM packaging.
