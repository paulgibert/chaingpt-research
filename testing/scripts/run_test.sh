#!/bin/bash

ARCH=amd64

docker run --rm -it -w /work test:test-$ARCH /bin/sh