#!/bin/bash

ARCH=x86_64
WOLFI_KEYRING=https://packages.wolfi.dev/os/wolfi-signing.rsa.pub
WOLFI_REPO=https://packages.wolfi.dev/os
KEYS_DIR=keys

cp $1 $2/
docker run --privileged -v $2:/work \
    --entrypoint=melange \
    --workdir=/work \
    ghcr.io/wolfi-dev/sdk \
    build $1 --arch $ARCH \
    --keyring-append $KEYS_DIR/melange.rsa.pub \
    --keyring-append $WOLFI_KEYRING \
    --signing-key $KEYS_DIR/melange.rsa \
    --repository-append $WOLFI_REPO \
    --repository-append /work/packages \
    --empty-workspace