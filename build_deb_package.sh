#!/usr/bin/env bash

set -eux

DIST_DIR_NAME="dist"
INSTALL_DIR_PATH="/usr/bin"
DIST_DIR_PATH="./${DIST_DIR_NAME}/${INSTALL_DIR_PATH}"
PKG_NAME="elasticsearch-faker"
PKG_NAME_SNAKE="elasticsearch_faker"

# initialize
rm -rf $DIST_DIR_NAME
mkdir -p "${DIST_DIR_NAME}/DEBIAN"

pip install --upgrade "pip>=19.0.2"
pip install --upgrade . pyinstaller

PKG_VERSION=$(python -c "import ${PKG_NAME_SNAKE}; print(${PKG_NAME_SNAKE}.__version__)")

if [ "$PKG_VERSION" = "" ]; then
    echo 'failed to get the package version' 1>&2
    exit 1
fi

echo $PKG_NAME $PKG_VERSION

# build an executable binary file
pyinstaller cli.py --clean --onefile --distpath $DIST_DIR_PATH --name $PKG_NAME

${DIST_DIR_PATH}/${PKG_NAME} --version

# build a deb package
cat <<_CONTROL_ >"${DIST_DIR_NAME}/DEBIAN/control"
Package: $PKG_NAME
Version: $PKG_VERSION
Maintainer: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
Architecture: amd64
Description: elasticsearch-faker is a CLI tool to generate fake data for Elasticsearch.
Homepage: https://github.com/thombashi/$PKG_NAME
Priority: extra
_CONTROL_

fakeroot dpkg-deb --build $DIST_DIR_NAME $DIST_DIR_NAME
