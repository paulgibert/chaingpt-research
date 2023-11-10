#!/bin/bash
# Usage:
#   run.sh [package name] [version] [output .yaml] [output dir]
#
# Example:
#   run.sh grype 0.72.0 grype.yaml /tmp/
#

BASEDIR=$(dirname $BASH_SOURCE)
SRC=$(pwd)/$BASEDIR/bender

docker run -it --rm -v $4:/output -v $SRC:/work/bender bender-agent python bender/main.py $1 -v $2 -o $3