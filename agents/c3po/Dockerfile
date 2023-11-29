FROM cgr.dev/chainguard/wolfi-base:latest

ARG py_version=3.11
ARG package_name
WORKDIR /work
RUN mkdir /output

RUN apk add build-base python-${py_version} py${py_version}-pip git

COPY requirements.txt /work/
COPY pyproject.toml /work/
COPY . /work/c3po

RUN pip3 install -r requirements.txt
RUN pip3 install /work/c3po
