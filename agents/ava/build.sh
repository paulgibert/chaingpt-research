#!/bin/bash

# Clone the repository
git clone https://github.com/numpy/numpy.git

# Navigate to the repository
cd numpy

# Initialize the git submodules
git submodule update --init

# Install NumPy
pip install .

# If the above command fails, try an editable install
pip install -e . --no-build-isolation
