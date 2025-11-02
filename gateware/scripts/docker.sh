#!/usr/bin/env bash

set -e

TAG=tiliqua_builder
TILIQUA_ROOT=$(dirname $(dirname $(dirname $(readlink -f $0))))

DOCKERFILE=$(cat <<-'EOF'
    FROM debian:trixie-slim

    # Basic stuff that the non-slim distro should already have
    RUN DEBIAN_FRONTEND="noninteractive" \
        apt-get update -qq && \
        apt-get install -qq --no-install-recommends \
        curl \
        git \
        build-essential \
        libssl-dev \
        pkg-config \
        python3 \
        python3-pip \
        python3-venv \
        && rm -rf /var/lib/apt/lists/*

    # Rust and dependencies from https://apfaudio.github.io/tiliqua/install.html
    RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
        && . /root/.cargo/env \
        && rustup component add rustfmt clippy llvm-tools \
        && rustup target add riscv32im-unknown-none-elf riscv32imafc-unknown-none-elf \
        && cargo install cargo-binutils form svd2rust --locked

    # Make sure cargo binaries are available in PATH
    ENV PATH="/root/.cargo/bin:${PATH}"

    # Install PDM
    RUN curl -sSL https://pdm-project.org/install-pdm.py | python3 -
    # This shouldn't be needed, but explicitly adding pdm to path as well.
    # Make sure cargo binaries are available in PATH
    ENV PATH="/root/.local/bin:${PATH}"

    RUN git config --global --add safe.directory /tiliqua
EOF
)

docker build -t $TAG - <<< ${DOCKERFILE}
docker run -t \
	    --volume ${TILIQUA_ROOT}:/tiliqua \
	    --workdir /tiliqua/gateware \
	    --rm $TAG \
	    "$@"
