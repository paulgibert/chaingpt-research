#!/bin/bash

docker run -it --rm -v ./bender:/work/bender bender-agent python bender/main.py $1