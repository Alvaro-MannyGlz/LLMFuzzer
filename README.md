# Circinus

[![Build Status](https://github.com/PrVrSs/circinus/workflows/test/badge.svg)](https://github.com/PrVrSs/circinus/actions?query=workflow%3Atest)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/PrVrSs/circinus/blob/master/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue)](https://www.python.org/)

## System Requirements

### Minimum project requirements

These requirements apply to Circinus itself:

- Windows PowerShell or Command Prompt
- Python 3.10 or newer
- enough free disk space for Python dependencies and any local model assets you choose to install

Optional, only needed for the AFL++ handoff pipeline:

- AFL++ installed separately in a Linux-compatible environment such as WSL or a Linux VM
- a target program you can run with an input-file placeholder such as `@@`

If you are on Windows and want to use the AFL++ pipeline, install WSL or another Linux environment first. Circinus itself runs on Windows, but AFL++ does not ship with this project and must be available separately.

### Ollama platform notes

According to the official Ollama documentation:

- Ollama is available for Windows, macOS, and Linux
- the local Ollama service listens on `http://localhost:11434`
- Circinus uses the OpenAI-compatible local endpoint at `http://localhost:11434/v1`
- no authentication is required for local API access on `http://localhost:11434`
- on Windows, Ollama reads standard user and system environment variables

### Ollama hardware guidance

Official Ollama documentation explains that loaded models may run fully on GPU, fully in system memory, or split across CPU and GPU, and that actual memory use depends on the model you choose. The exact hardware requirement therefore depends primarily on model size.

Practical guidance for Circinus users:

- For small local coding models, 16 GB system RAM is a reasonable starting point
- For smoother local work, 32 GB RAM is strongly preferred
- A dedicated GPU helps significantly, especially for larger models and faster response times
- If you do not have a capable GPU, Ollama can still run on CPU, but generation will be slower
- Larger models require substantially more RAM or VRAM and may be impractical on entry-level hardware

Conservative model guidance:

- `qwen3.5` or similar small local models are the easiest place to start on consumer hardware
- mid-size models usually benefit from 16 GB to 24 GB of available VRAM, or enough combined GPU and system memory for mixed CPU/GPU loading
- very large models are generally not a practical default for local fuzzing workflows unless you already have a high-memory workstation

This guidance is an implementation recommendation based on Ollama's documented runtime behavior and common model sizes. It is not an official Ollama sizing table.

## Installation

From the repository root:

```powershell
python -m pip install -e .
copy .env.example .env
```

Editing `.env` is optional. Circinus can use the defaults in `.env.example` or environment variables directly when it starts.

## Quick Start

Start Circinus from the repository root:

```powershell
python -m circinus \
	--documentation notebook/blob_documentation.txt \
	--specification notebook/blob.webidl \
	--code notebook/blob.js \
	--output notebook/demo_files
```

Or run the notebook demo in `notebook/webidl.ipynb`.

When Circinus starts, it uses the configured LLM backend from `.env` or `notebook/conf.toml`.

## How To Use Ollama With Circinus

### 1. Install Ollama

Install Ollama from the official download page:

- [Ollama Downloads](https://ollama.com/download)

After installation, make sure the Ollama application or service is running.

### 2. Pull a local model

For a lightweight starting point:

```powershell
ollama pull qwen3.5
```

You can verify that the model is available with:

```powershell
ollama list
```

### 3. Start the Ollama server

If Ollama is not already running in the background, start it with:

```powershell
ollama serve
```

The default local API base URL used by Circinus is:

```text
http://localhost:11434/v1
```

### 4. Configure Circinus for Ollama

The simplest local settings are:

```powershell
$env:LLM_API_KEY="ollama"
$env:LLM_BASE_URL="http://localhost:11434/v1"
$env:LLM_MODEL="qwen3.5"
```

Or edit `.env` directly.

Circinus also supports other local or OpenAI-compatible model options through the same settings:

1. `qwen3.5`
2. `llama3.1`
3. `mistral`
4. `gemma`
5. `deepseek`-style local variants

### 5. Run Circinus with Ollama

```powershell
python -m circinus \
	--documentation notebook/blob_documentation.txt \
	--specification notebook/blob.webidl \
	--code notebook/blob.js \
	--output notebook/demo_files
```

Circinus will point the bundled client at your local Ollama-compatible endpoint.

## AFL++ Pipeline

Circinus can generate context-aware seed files and hand them directly to AFL++ as the initial corpus.

Before using this pipeline, install AFL++ separately in your Linux environment. On Ubuntu, for example:

```bash
sudo apt install afl++
```

Example:

```powershell
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

## Seed Cache

Circinus can persist crash-derived seeds to `.circinus-seed-cache.json` between runs.

When the cache file exists, Circinus loads those seeds first and writes them into the current output directory before generating new ones. If crash artifacts are available from a run, Circinus stores them back into the cache so the next run can start from known bug-triggering inputs.

## Automated Vulnerability Reporter

You can convert raw crash artifacts, such as AFL++ `crashes/` output, into plain-English findings with an Ollama model.

Example:

```powershell
python -m circinus \
	--documentation notebook/blob_documentation.txt \
	--specification notebook/blob.webidl \
	--code notebook/blob.js \
	--output notebook/demo_files/seeds \
	--crash-data notebook/demo_files/afl_findings/default/crashes \
	--vuln-report notebook/demo_files/vulnerability_report.md \
	--ollama-model qwen3.5 \
	--ollama-base-url http://localhost:11434/v1
```

By default, if `--vuln-report` is omitted, Circinus writes `vulnerability_report.md` inside `--output`.

## Examples

[notebooks](https://github.com/PrVrSs/circinus/blob/master/notebook)

## Contributing

Any help is welcome and appreciated.

## License

*circinus* is licensed under the terms of the MIT License (see the file LICENSE).