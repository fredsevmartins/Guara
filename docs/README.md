# Guara documentation

Guara 0.1.3 records claims, sources, evidence links, and review history locally.
This is the maintained documentation on `main`; see [version guidance](support.md) for
released snapshots.
A stored claim, a supporting link, or intact file bytes do not establish scientific truth.

[Project overview](../README.md) · [Português brasileiro](pt-BR/README.md)

## Start here

1. [Install](installation.md) Python and the package in a virtual environment.
2. [Quickstart](quickstart.md): create a claim, attach evidence, inspect, and export.
3. [Tutorial](tutorial.md): run the synthetic reassessment and backup/restore walkthrough.
4. [Status interpretation](statuses.md) and [glossary](glossary.md): distinguish review, evidence, and byte integrity.
5. [Evidence model](evidence-model.md): interpret review and evidence statuses separately.

## Choose an interface

| Goal | Guide |
| --- | --- |
| Automate from Python | [Python API](python-api.md) |
| Work in a terminal or scripts | [CLI reference](cli-reference.md) |
| Connect a client that launches local stdio servers | [MCP integration](mcp-integration.md) |
| Understand system boundaries and storage | [Architecture](architecture.md), [data model and migrations](data-model.md) |

## Understand evidence

- [Introduction](introduction.md) and [scientific integrity](scientific-integrity.md)
- [Comparison rules and tolerances](conflict-detection.md)
- [Context templates](context-templates.md) and [synthetic examples](examples.md)
- [Workflow diagrams](workflows/) and [limitations](limitations.md)

## Operate and maintain

- [Operations runbook: backups, recovery drills, upgrades, and retention](operations.md)
- [Backups, restoration, and source integrity](backup-and-integrity.md)
- [Pagination, concurrency, and benchmarks](scaling-and-concurrency.md)
- [Troubleshooting](troubleshooting.md), [FAQ](faq.md), and [support/reporting](support.md)
- [Security policy](../SECURITY.md) and [security design](security.md)
- [Release downloads, checksums, and publishing](releasing.md)
- [Platforms and releases](platforms-and-releases.md), [changelog](../CHANGELOG.md), and [PyPI publication](pypi-publication.md)

## Contribute

See [contribution guidelines](../CONTRIBUTING.md), [code of conduct](../CODE_OF_CONDUCT.md),
[citation metadata](../CITATION.cff), and [Guará's mascot guide](mascot.md).
See [English social artwork](media.md) and [repository branding and rename status](repository-name.md).

Historical validation observations are in the [validation report](validation-report.md);
run the development checks in the project README to assess your current checkout.
