#!/usr/bin/env bash

set -e

TAG=tiliqua_builder
SCRIPT_DIR=$(dirname $(readlink -f $0))
TILIQUA_ROOT=$(dirname $(dirname $(dirname $(readlink -f $0))))

# Build mode: ./docker.sh build
if [ "$1" = "build" ]; then
    echo "Building Docker image: $TAG"
    docker build -t $TAG -f "${SCRIPT_DIR}/Dockerfile" "${SCRIPT_DIR}"
    exit 0
fi

# Run mode: ensure image exists, then run command
if ! docker image inspect $TAG >/dev/null 2>&1; then
    echo "Image $TAG not found. Building..."
    docker build -t $TAG -f "${SCRIPT_DIR}/Dockerfile" "${SCRIPT_DIR}"
fi

docker run -t \
    --volume ${TILIQUA_ROOT}:/tiliqua \
    --workdir /tiliqua/gateware \
    --rm $TAG \
    "$@"
