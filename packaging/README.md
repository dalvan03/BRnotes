# Fedora RPM and Copr

The first package is `brnotes-0.1.0-1`, a community RPM, not an official Fedora
package. The application source is pinned to the full Git commit in
`brnotes.spec`; packaging assets are included separately in the source RPM.
Update that commit, version/release and AppStream release when shipping updates.

## Build locally

Install the build requirements:

```sh
sudo dnf install rpm-build curl python3 python3-pyside6 python3-pillow desktop-file-utils appstream
sh packaging/build-rpm.sh
```

Output: `dist/rpm/noarch/*.rpm` and `dist/rpm/*.src.rpm`.
Use `sh packaging/build-rpm.sh --srpm` for a source-only build. To rebuild an
SRPM in a clean Fedora build environment, use `mock` with the matching Fedora
configuration. The local build validates the desktop entry and AppStream data,
checks Python syntax, and runs installer tests. The full GUI suite is run
separately in a graphical session or Xvfb, as documented in the main README.

## Install and configure

```sh
sudo dnf install ./dist/rpm/noarch/brnotes-0.1.0-1.*.noarch.rpm
```

Launch BRnotes from the application menu or run `brnotes`. In KDE System
Settings → Keyboard → Shortcuts, find BRnotes (or add it from the application
picker) and assign Meta+Shift+N, or another available shortcut.

The RPM does not run the per-user installer or change user shortcuts in root
scriptlets. It installs a launcher in `/usr/bin` and application files under
`/usr/share`. If you previously installed from source, remove that per-user
installation with `python3 manage.py uninstall` before switching to the RPM:
otherwise its local desktop entry may shadow the system launcher. Open notes
are not terminated by that command. Reassign the shortcut after migration.

Update with `sudo dnf upgrade brnotes`; remove with `sudo dnf remove brnotes`.
Never run `manage.py uninstall` to uninstall the RPM itself.

## Publish in Copr

A Fedora account and an authenticated Copr session are required. Create a
project named `brnotes`, select currently supported Fedora x86_64 chroots, and
upload `dist/rpm/brnotes-0.1.0-1.*.src.rpm`. Wait for a successful build in each
selected chroot before advertising its repository.

Alternatively, use a Git source package with:

- Clone URL: `https://github.com/dalvan03/BRnotes.git`
- Committish: the packaging commit to build
- Spec: `packaging/brnotes.spec`
- Build SRPM with: `make srpm` (uses `.copr/Makefile`)

The SRPM builder needs `curl` and `rpm-build` available. Automatic rebuilds are
not enabled by these files. Choose the exact commit for reproducible packaging.

After publication, replace OWNER with the actual Copr account name:

```sh
sudo dnf copr enable OWNER/brnotes
sudo dnf install brnotes
```

These are templates, not a claim that a repository already exists. Copr signing
and repository metadata are provided by Copr after the remote build; the locally
built RPM is unsigned. AppStream metadata is included for software catalogs,
but visibility in Discover depends on repository metadata and enabled sources.

## Project description for Copr

BRnotes is an MIT-licensed disposable sticky-note application tested on Fedora
KDE Plasma. It offers seven colors, movable and resizable frameless notes,
screen-edge tabs, paper-like shading, and an optional crumple-and-toss animation.
Notes are not saved: closing a note or logging out discards its text. Requires
X11/XWayland; native Wayland positioning is not implemented. This is an
independent community project, not an official Fedora or KDE application.
