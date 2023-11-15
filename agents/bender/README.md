## Bender

A 2-staged LLM agent. Stage 1 finds, clones, and explores the GitHub repository of a software project and produces a build summary. Stage 2 produces the melange YAML.

__Input__: Package name and version
__Output__: Melange YAML

#### Usage
1) Write your OpenAI API key to a file called `openai_api_key.secret` in `agents/bender/`

2) Build Bender's container environment

```bash
cd agents/bender
./build.sh
```

3) Run Bender

```bash
#  run.sh [package name] [version] [output .yaml] [output dir]
./run.sh grype 0.72.0 grype.yaml /tmp/
```

If successful, a file called `grype.yaml` will appear in `/tmp/`. Please note that this is an early stage project and errors will occur often.