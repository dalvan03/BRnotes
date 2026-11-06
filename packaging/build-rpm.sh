#!/bin/sh
# Run from any directory. Pass --srpm for a source-only build.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
out=${BRNOTES_RPM_OUTDIR:-"$root/dist/rpm"}
mkdir -p "$out"
out=$(CDPATH= cd -- "$out" && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT HUP INT TERM
mkdir -p "$work/SOURCES"
cp "$root"/packaging/*.desktop "$root"/packaging/*.svg "$root"/packaging/*.xml "$work/SOURCES/"
commit=$(sed -n 's/^%global commit //p' "$root/packaging/brnotes.spec")
curl --fail --location --retry 3 "https://codeload.github.com/dalvan03/BRnotes/tar.gz/$commit" -o "$work/SOURCES/BRnotes-$commit.tar.gz"
mode=-ba
if [ "${1:-}" = --srpm ]; then mode=-bs; fi
rpmbuild "$mode" --define "_topdir $work" --define "_rpmdir $out" --define "_srcrpmdir $out" "$root/packaging/brnotes.spec"
