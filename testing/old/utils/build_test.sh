#!/bin/bash

docker run --rm -v $1:/work \
    -w /work cgr.dev/chainguard/apko \
    build apko.yaml test:test test.tar \
    -k keys/melange.rsa.pub

docker load < $1/test.tar
