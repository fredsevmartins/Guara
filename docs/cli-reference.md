# CLI reference

`opentruth --workspace PATH COMMAND` uses PATH as the allowed workspace. Default: current directory.
`opentruth --help` lists commands. Every operational command accepts `--json '{}'` containing a
JSON object of arguments matching the Python API. Results are JSON on stdout; failures use stderr
and exit code 1. Syntax/argparse failures use exit code 2. `init` and `mcp` do not accept `--json`.

| Command | Python method |
|---|---|
| source add | register_source |
| claim add / list / inspect / revise | add_claim / search_claims / inspect_claim / revise_claim |
| evidence link / revise | link_evidence / revise_evidence |
| conflicts check | check_conflicts |
| history | get_claim_history |
| review | review_claim |
| export | export_evidence |
| init | initialize database |
| mcp | run stdio server |

See [quickstart](quickstart.md) for executable argument shapes. Shell redirect `export` output to
an appropriate private destination; export contains sensitive evidence text and attribution.


## Convenience arguments and readable output

JSON remains the default output, preserving automation compatibility. Put `--format text` before
the command for human-readable claims and integrity reports. Other structured reports use indented
JSON in text mode. `--json` remains available; supplying the same field via JSON and a convenience
argument is an error rather than an implicit override.

```sh
opentruth claim add "SYNTHETIC statement" --subject beam --predicate length --value 1 --unit m
opentruth --format text claim inspect CLAIM_UUID
opentruth source add "SYNTHETIC report" --file report.txt --type TECHNICAL_DOCUMENT
opentruth source verify
opentruth source verify SOURCE_UUID
opentruth conflicts check CLAIM_UUID
opentruth history CLAIM_UUID
opentruth backup snapshot.zip
opentruth restore snapshot.zip --data-dir restored-evidence
opentruth context templates study
```

Claim flags also include `--context`, `--provenance` (JSON objects), and `--context-template`.
`--value` parses JSON numbers/quoted strings; other text is kept as a qualitative value. Booleans
are rejected as measurements. Restore and context commands have their own positional syntax and
do not accept `--json`. Backup accepts either an archive positional argument or JSON.
`source verify` exits 1 with its report if any stored file is missing, altered, or unsafe.
