#!/bin/bash
# $1: YAML file dir
# $2: YAML file name
# $3: local workspace

ARCH=x86_64
WOLFI_KEYRING=https://packages.wolfi.dev/os/wolfi-signing.rsa.pub
WOLFI_REPO=https://packages.wolfi.dev/os
KEYS_DIR=keys

cp $1/$2 $3/
docker run --privileged -v $3:/work \
    --entrypoint=melange \
    --workdir=/work \
    ghcr.io/wolfi-dev/sdk \
    build $2 --arch $ARCH \
    --keyring-append $KEYS_DIR/melange.rsa.pub \
    --keyring-append $WOLFI_KEYRING \
    --signing-key $KEYS_DIR/melange.rsa \
    --repository-append $WOLFI_REPO \
    --repository-append /work/packages \
    --empty-workspace 2> $3/build.log