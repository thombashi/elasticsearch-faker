#!/usr/bin/env bash

set -eux

if [ $# != 1 ]; then
  echo "Usage: $(basename $0) <ES extras>" 1>&2
  exit 22
fi

ES_EXTRAS=$1

if ! [[ $ES_EXTRAS =~ es[0-9]+ ]]; then
  echo "[ERROR] extras must be es[0-9]+ format" 1>&2
  exit 22
fi

TOPLEVEL_DIR=$(git rev-parse --show-toplevel)
DPKG_BUILD_DIR="dpkg_build"
DIST_DIR_NAME="dist"
INSTALL_DIR_PATH="/usr/local/bin"
BUILD_DIR_PATH="${TOPLEVEL_DIR}/${DPKG_BUILD_DIR}/${INSTALL_DIR_PATH}"
PKG_NAME="elasticsearch-faker"
PKG_NAME_SNAKE="elasticsearch_faker"
PYTHON=python3
ARCH=$(dpkg --print-architecture)

cd "$TOPLEVEL_DIR"

# initialize
rm -rf "$DPKG_BUILD_DIR" build
mkdir -p "${DPKG_BUILD_DIR}/DEBIAN" "$DIST_DIR_NAME"

$PYTHON -m pip install --upgrade -q "pip>=21.1"
$PYTHON -m pip install --upgrade -q .[buildexe,${ES_EXTRAS}]

PKG_VERSION=$($PYTHON -c "import ${PKG_NAME_SNAKE}; print(${PKG_NAME_SNAKE}.__version__)")

if [ "$PKG_VERSION" = "" ]; then
    echo 'failed to get the package version' 1>&2
    exit 1
fi

echo "$PKG_NAME $PKG_VERSION"


# build an executable binary file
pyinstaller cli.py --clean --onefile --strip --distpath "$BUILD_DIR_PATH" --name "$PKG_NAME"
${BUILD_DIR_PATH}/${PKG_NAME} --version

# build a deb package
cat << _CONTROL_ > "${DPKG_BUILD_DIR}/DEBIAN/control"
Package: $PKG_NAME
Version: $PKG_VERSION
Maintainer: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
Architecture: $ARCH
Description: $PKG_NAME is a CLI tool to generate fake data for Elasticsearch.
Homepage: https://github.com/thombashi/$PKG_NAME
Priority: extra
_CONTROL_
cat "${DPKG_BUILD_DIR}/DEBIAN/control" 2>&1

VERSION_CODENAME=$(\grep -Po "(?<=VERSION_CODENAME=)[a-z]+" /etc/os-release)
FILE_SUFFIX="_${ES_EXTRAS}_${VERSION_CODENAME}_${ARCH}"

fakeroot dpkg-deb --build "$DPKG_BUILD_DIR" "$DIST_DIR_NAME"
rename -v "s/_${ARCH}.deb/${FILE_SUFFIX}.deb/" ${DIST_DIR_NAME}/*

# generate an archive file
ARCHIVE_EXTENSION=tar.gz
SYSTEM=$($PYTHON -c "import platform; print(platform.system().casefold())")
ARCHIVE_FILE="${PKG_NAME}_${PKG_VERSION}_${SYSTEM}${FILE_SUFFIX}.${ARCHIVE_EXTENSION}"

cd "$BUILD_DIR_PATH"
tar -zcvf "$ARCHIVE_FILE" "$PKG_NAME"
mv "$ARCHIVE_FILE" "${TOPLEVEL_DIR}/${DIST_DIR_NAME}/"
