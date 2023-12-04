#!/bin/bash

docker run --rm -v .:/work \
    -w /work cgr.dev/chainguard/apko \
    build apko.yaml test:test test.tar \
    -k melange.rsa.pub \
    --sbom=false

docker load < ./test.tar
