#!/bin/bash

docker run --rm -v $(pwd):/work \
    -w /work cgr.dev/chainguard/apko \
    build apko-grype.yaml test:test test.tar \
    -k melange.rsa.pub --sbom=false

docker load < test.tar