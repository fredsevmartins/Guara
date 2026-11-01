# Release downloads, verification, and publishing

## Install a release

Open [GitHub Releases](https://github.com/fredsevmartins/Guara/releases) and select a version.
The complete `Guara-VERSION.zip` contains source documentation, examples, mascot artwork, and
`dist/` with the wheel and source distribution. Extract it and open `COMECE-AQUI.md`.
Alternatively, download just the wheel and install it in an activated virtual environment:

```sh
python -m pip install /path/to/opentruth-0.1.3-py3-none-any.whl
opentruth --version
python -m pip check
```

The package is still named `opentruth` for compatibility. Installing dependencies initially
requires registry access; local runtime operations work offline. No PyPI publication is assumed.

## Verify downloaded bytes

Download `SHA256SUMS` alongside the artifacts. On Linux, from that directory:

```sh
sha256sum --check SHA256SUMS
```

On macOS, use `shasum -a 256 -c SHA256SUMS`. In PowerShell, calculate a file's SHA-256 with
`Get-FileHash .\Guara-0.1.3.zip -Algorithm SHA256` and compare it to the manifest entry.
Checksums detect byte changes; obtain the manifest and artifacts from the same trusted release.
They are not cryptographic signatures or scientific source validation.

## Build the complete product

From a checkout with development dependencies installed:

```sh
python -m pytest
ruff check .
python scripts/check_docs.py
python -m examples.tutorial
python -m examples.scenarios
python -m build
python scripts/wheel_smoke.py
python scripts/prepare_release.py
```

The last command creates `release-assets/` with the complete ZIP, wheel, source archive,
mascot, available social artwork, and `SHA256SUMS`. It validates matching package versions and
source archive paths before generating outputs. It reads the built source archive rather than
copying local evidence stores, virtual environments, or older committed deliveries. Given the
same input distributions, ZIP and checksum bytes are repeatable. The distributions themselves
retain their build-tool metadata; full build reproducibility is not claimed.

Use `--dist-dir PATH --output-dir PATH` to select other directories. Existing expected artifact
filenames are replaced; use a dedicated output directory. Only files generated for this release
are listed in the manifest.

## Publish on GitHub

Merge the tested change, then push a version tag matching `pyproject.toml`, for example `v0.1.3`.
The release workflow first runs the quality matrix: Linux, macOS, and Windows on Python 3.11–3.13.
It builds fresh distributions and generates the bundle and checksums before uploading them with
the workflow's GitHub token. A failed check prevents publication. Verify that the workflow
succeeded and the release assets are visible before announcing the version.

The session's external-app token may lack release-asset upload access; the Actions workflow
uses its own repository-scoped GitHub token. PyPI publishing remains a separate optional
[maintainer configuration](pypi-publication.md).
