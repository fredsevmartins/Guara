# Platform support and releases

Python 3.11–3.13 is configured in CI on Linux, macOS, and Windows. The full test suite runs on
Linux/macOS. Windows runs metadata/revision/persistence, portable backup/restore, CLI, and real
MCP stdio tests. Every matrix entry builds a wheel/sdist and installs the wheel into a fresh virtual
environment outside the checkout, exercising a complete metadata evidence/backup/restore workflow.
Configured jobs are not proof of passing runs; consult the current Actions results.

Secure local source ingestion uses POSIX directory descriptors and O_NOFOLLOW. Linux/macOS can
register source files; platforms lacking those primitives, including Windows, reject that operation
instead of silently falling back to a weaker copying guarantee. Metadata, claims, comparisons,
reviews, and exports remain available there. Backups can restore already registered source bytes
on Windows; subsequent integrity reading requires trusted paths without symlinks/junctions and no
concurrent filesystem changes. This is not protection against a malicious local OS user.

## Version publication

`.github/workflows/release.yml` runs on version-tag pushes. It reuses the full CI matrix and only
creates a GitHub Release after all jobs pass. It checks the tag against `pyproject.toml`, requires
`docs/releases/TAG.md`, builds packages, and attaches the wheel/sdist to the release. Build/test jobs
have read-only repository permissions; only the final release job gets `contents: write`. It uses
the repository-provided Actions token and never publishes to PyPI.

Before tagging, update the package version, `__version__`, citation, changelog, release notes, and
validation report. Never move an already published tag to conceal a failed release. Fix failures
in a subsequent commit/version. If Actions is disabled or write permissions are disallowed by the
repository/organization, an owner must enable the workflow; a pushed tag alone is not a completed
GitHub Release.
