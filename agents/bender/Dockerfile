FROM cgr.dev/chainguard/wolfi-base:latest

ARG py_version=3.11
ARG package_name
WORKDIR /work
RUN mkdir /output

RUN apk add build-base python-${py_version} py${py_version}-pip git

COPY requirements.txt openai_api_key.secret /work/

RUN pip3 install -r requirements.txt

# ENTRYPOINT [ "python", "/work/bender/main.py", ${package_name}]
