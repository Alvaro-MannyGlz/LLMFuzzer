# Circinus

[![Build Status](https://github.com/PrVrSs/circinus/workflows/test/badge.svg)](https://github.com/PrVrSs/circinus/actions?query=workflow%3Atest)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/PrVrSs/circinus/blob/master/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue)](https://www.python.org/)

## Installation

```shell script
pip install circinus
```

## LLM Setup

Circinus now uses OpenAI-compatible model calls with a local Ollama-first default.

Copy the example environment file and edit it for your setup:

```powershell
Copy-Item .env.example .env
```

Then set your preferred model backend. The defaults are tuned for Ollama, but any OpenAI-compatible endpoint should work.

Typical local Ollama values:

```powershell
$env:LLM_API_KEY="ollama"
$env:LLM_BASE_URL="http://localhost:11434/v1"
$env:LLM_MODEL="llama3.1"
```

The example `.env` file also lists other model options you can swap in, including `qwen3.5`, `mistral`, `gemma`, and `deepseek`-style local variants.

## Quick Start

1. Set the `.env` values for your local model or compatible endpoint.
2. Run the notebook demo in `notebook/webidl.ipynb`, or run the CLI:

```shell
python -m circinus \
	--documentation notebook/blob_documentation.txt \
	--specification notebook/blob.webidl \
	--code notebook/blob.js \
	--output notebook/demo_files
```

## Circinus to AFL++ Pipeline

Circinus can now generate context-aware seed files and hand them directly to AFL++ as the initial corpus.

Example:

```shell
python -m circinus \
	--documentation notebook/blob_documentation.txt \
	--specification notebook/blob.webidl \
	--code notebook/blob.js \
	--output notebook/demo_files/seeds \
	--afl \
	--afl-target-cmd "python target.py @@" \
	--afl-output-dir notebook/demo_files/afl_findings \
	--afl-extra-args=-m \
	--afl-extra-args=none
```

This flow uses Circinus for semantic seed generation and AFL++ for high-throughput mutation and crash discovery.

## Automated Vulnerability Reporter (Ollama)

You can convert raw crash artifacts (for example AFL++ `crashes/` output) into plain-English findings with an Ollama model.

Example:

```shell
python -m circinus \
	--documentation notebook/blob_documentation.txt \
	--specification notebook/blob.webidl \
	--code notebook/blob.js \
	--output notebook/demo_files/seeds \
	--crash-data notebook/demo_files/afl_findings/default/crashes \
	--vuln-report notebook/demo_files/vulnerability_report.md \
	--ollama-model llama3.1 \
	--ollama-base-url http://localhost:11434/v1
```

By default, if `--vuln-report` is omitted, Circinus writes `vulnerability_report.md` inside `--output`.

## Examples

[notebooks](https://github.com/PrVrSs/circinus/blob/master/notebook)

## Contributing

Any help is welcome and appreciated.

## License

*circinus* is licensed under the terms of the MIT License (see the file LICENSE).