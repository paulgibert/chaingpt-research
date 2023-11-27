#!/bin/bash

ARCH=amd64

docker run --rm -it -v $1:/work \
    -w /work test:test-$ARCH $2