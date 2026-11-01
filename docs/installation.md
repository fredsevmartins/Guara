# Installation

Requires Python 3.11 or newer with SQLite. The package version is 0.1.3; no PyPI release
is claimed. Install from a checkout:

```sh
git clone https://github.com/fredsevmartins/Guara.git
cd Guara
python -m venv .venv
```

Activate the virtual environment with the command for your shell:

| Shell | Activation |
| --- | --- |
| Linux/macOS POSIX shell | `. .venv/bin/activate` |
| Windows PowerShell | `.\.venv\Scripts\Activate.ps1` |
| Windows Command Prompt | `.venv\Scripts\activate.bat` |

Then install runtime dependencies:

```sh
python -m pip install -e .
opentruth --help
```

For development, use `python -m pip install -e ".[dev]"` instead. See
[contributing](../CONTRIBUTING.md) for validation commands.

## Choose a data workspace

By default, Guara uses the current directory as its authorized workspace and stores its
SQLite database and copied source files under `.opentruth/`. Choose the directory deliberately:

```sh
opentruth --workspace /absolute/allowed/workspace init
```

The workspace must already exist. Use the same `--workspace` for subsequent operations;
otherwise you may inspect a different evidence store. Run the [quickstart](quickstart.md)
for a persistent store, or `python -m examples.tutorial` from the checkout root for a synthetic
walkthrough that uses a temporary directory.

## Offline use and platform limits

Initial dependency installation requires package registry access; installed runtime operations
are offline. No API keys, LLM, or external database are required. SQLite FTS5 is optional;
without it, search falls back to Python substring/token matching over SQLite records.

Windows supports metadata workflows. Secure local source-file ingestion is POSIX-only.
See [platform support](platforms-and-releases.md), [MCP setup](mcp-integration.md), and
[troubleshooting](troubleshooting.md).
