#!/usr/bin/env bash

set -eux

DIST_DIR_NAME="dist"
INSTALL_DIR_PATH="/usr/bin"
DIST_DIR_PATH="./${DIST_DIR_NAME}/${INSTALL_DIR_PATH}"
PKG_NAME="elasticsearch-faker"
PKG_NAME_SNAKE="elasticsearch_faker"
PYTHON=python3

# initialize
rm -rf $DIST_DIR_NAME
mkdir -p "${DIST_DIR_NAME}/DEBIAN"

$PYTHON -m pip install --upgrade -q "pip>=21.1"
$PYTHON -m pip install --upgrade -q .[buildexe] distro

PKG_VERSION=$($PYTHON -c "import ${PKG_NAME_SNAKE}; print(${PKG_NAME_SNAKE}.__version__)")
CODENAME=$($PYTHON -m distro --json | jq --raw-output .codename)

if [ "$PKG_VERSION" = "" ]; then
    echo 'failed to get the package version' 1>&2
    exit 1
fi

echo "$CODENAME $PKG_NAME $PKG_VERSION"


# build an executable binary file
pyinstaller cli.py --clean --onefile --distpath "$DIST_DIR_PATH" --name "$PKG_NAME"

${DIST_DIR_PATH}/${PKG_NAME} --version

# build a deb package
cat <<_CONTROL_ >"${DIST_DIR_NAME}/DEBIAN/control"
Package: ${PKG_NAME}-${CODENAME}
Version: $PKG_VERSION
Maintainer: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
Architecture: amd64
Description: elasticsearch-faker is a CLI tool to generate fake data for Elasticsearch.
Homepage: https://github.com/thombashi/$PKG_NAME
Priority: extra
_CONTROL_

fakeroot dpkg-deb --build $DIST_DIR_NAME $DIST_DIR_NAME
