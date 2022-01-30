#!/bin/sh

TOPLEVEL_DIR=$(git rev-parse --show-toplevel)
VERSION_FILE=elasticsearch_faker/__version__.py

cd "$TOPLEVEL_DIR"
VERSION=$(python3 -c "info = {}; exec(open('elasticsearch_faker/__version__.py').read(), info); print(info['__version__'])")
echo "$VERSION"
