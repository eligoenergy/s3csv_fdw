#!/bin/sh
VERSION='1.4.0'
ARCHIVE="v${VERSION}.zip"
wget -N "https://github.com/Segfault-Inc/Multicorn/archive/refs/tags/${ARCHIVE}"
unzip -uoq "${ARCHIVE}"
rm -f "${ARCHIVE}"
cd "Multicorn-${VERSION}"
make && sudo make install
