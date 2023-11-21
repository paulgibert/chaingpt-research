## ChainGPT

A growing collection of LLM agents designed to build melange YAML files for Wolfi.

#### Open API

You will require an Open API key and credit to interact with the Chat server.

- Create an Open API Key from the [User Settings](https://beta.openai.com/account/api-keys)
- Add credit in the [Billing Settings](https://platform.openai.com/account/billing/overview)

#### Agents

`agents/ava` - Given a github repository url, produces a build script for the project.

`agents/bender` - A 2-stage LLM agent that generates melange YAMLs given a package name and version.