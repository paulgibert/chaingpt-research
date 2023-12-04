#!/bin/bash
# $1: melange YAML
ARCH=x86_64
WOLFI_KEYRING=https://packages.wolfi.dev/os/wolfi-signing.rsa.pub
WOLFI_REPO=https://packages.wolfi.dev/os

docker run --privileged -v .:/work \
    --entrypoint=melange \
    --workdir=/work \
    ghcr.io/wolfi-dev/sdk \
    build $1 --arch $ARCH \
    --keyring-append melange.rsa.pub \
    --keyring-append $WOLFI_KEYRING \
    --signing-key melange.rsa \
    --repository-append $WOLFI_REPO \
    --repository-append /work/packages \
    --empty-workspace