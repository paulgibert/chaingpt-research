#!/bin/bash

ARCH=x86_64
WOLFI_KEYRING=https://packages.wolfi.dev/os/wolfi-signing.rsa.pub
WOLFI_REPO=https://packages.wolfi.dev/os
KEYS_DIR=.

docker run --rm --privileged -v $(pwd):/work \
    --entrypoint=melange \
    --workdir=/work \
    ghcr.io/wolfi-dev/sdk \
    build $1 --arch $ARCH \
    --keyring-append 'melange.rsa.pub https://packages.wolfi.dev/os/wolfi-signing.rsa.pub' \
    --signing-key melange.rsa \
    --repository-append $WOLFI_REPO \
    --empty-workspace