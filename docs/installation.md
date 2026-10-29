# Installation

Use Python 3.11 or newer with SQLite. From the checkout root:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
opentruth init
python -m pytest
ruff check .
python -m build
```

Omit `[dev]` for runtime-only installation. Initial dependency installation requires package
registry access; installed runtime operations are offline. SQLite FTS5 is optional. Without it,
search uses Python substring/token matching over SQLite records. No API keys are required.
