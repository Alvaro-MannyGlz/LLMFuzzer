# Circinus

[![Build Status](https://github.com/PrVrSs/circinus/workflows/test/badge.svg)](https://github.com/PrVrSs/circinus/actions?query=workflow%3Atest)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/PrVrSs/circinus/blob/master/LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue)](https://www.python.org/)

## Installation

```shell script
pip install circinus
```

## OpenRouter Setup

Circinus now uses live OpenRouter-backed model calls (mock mode was removed).

Set your API key before running the CLI, agent, or notebook demos.

PowerShell:

```powershell
$env:OPENROUTER_API_KEY="your_openrouter_key"
```

The tracked template is `notebook/conf.example.toml`. Create your local config from it:

```powershell
Copy-Item notebook/conf.example.toml notebook/conf.toml
```

Then edit `notebook/conf.toml` as needed. Default values are:

```toml
openrouter_api_key='${OPENROUTER_API_KEY}'
openrouter_api_model='meta-llama/llama-3.1-8b-instruct:free'
openrouter_fallback_models=['mistralai/mistral-7b-instruct:free', 'google/gemma-2-9b-it:free']
openrouter_embedding_model='nomic-ai/nomic-embed-text-v1.5'
openrouter_base_url='https://openrouter.ai/api/v1'
openrouter_site_url='https://github.com/PrVrSs/circinus'
openrouter_site_name='circinus'
max_tokens=2048
```

Recommended free chat models to try:

1. `meta-llama/llama-3.1-8b-instruct:free` (default suggestion)
2. `mistralai/mistral-7b-instruct:free` or `google/gemma-2-9b-it:free`

To switch models, change `openrouter_api_model` in `notebook/conf.toml`.

If OpenRouter returns `404 No endpoints found` for the primary model, Circinus automatically retries models listed in `openrouter_fallback_models`.

Note: OpenRouter free model availability can change over time by provider/queue status.

## Quick Start

1. Export `OPENROUTER_API_KEY`.
2. Run the notebook demo in `notebook/webidl.ipynb`, or run the CLI:

```shell
python -m circinus \
	--documentation notebook/blob_documentation.txt \
	--specification notebook/blob.webidl \
	--code notebook/blob.js \
	--output notebook/demo_files
```

## Examples

[notebooks](https://github.com/PrVrSs/circinus/blob/master/notebook)

## Contributing

Any help is welcome and appreciated.

## License

*circinus* is licensed under the terms of the MIT License (see the file LICENSE).