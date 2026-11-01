# CLI reference

`opentruth --workspace PATH COMMAND` uses PATH as the allowed workspace. Default: current directory.
`opentruth --help` lists commands. `opentruth --version` reports the installed package version
without creating or opening a workspace. Every operational command accepts `--json '{}'` containing a
JSON object of arguments matching the Python API. Results are JSON on stdout; failures use stderr
and exit code 1. Syntax/argparse failures use exit code 2. `init` and `mcp` do not accept `--json`.

| Command | Python method |
|---|---|
| source add / verify | register_source / verify_sources |
| claim add / list / inspect / revise | add_claim / search_claims / inspect_claim / revise_claim |
| evidence link / revise | link_evidence / revise_evidence |
| conflicts check | check_conflicts |
| history | get_claim_history |
| review | review_claim |
| export | export_evidence |
| backup | backup |
| restore | restore_backup (module function) |
| context templates | list built-in context checklists |
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


Listing/conflict/history commands accept `--limit N --offset N`; claim listing also accepts
`--include-history`. Default search/conflict limit is 100 and the maximum is 1000. Legacy `--json`
can supply the same fields. Busy stores return a structured `WORKSPACE_BUSY` error and exit 1.

## Complete terminal workflows (0.1.3+)

No JSON wrapper is needed for linking, reviewing, or revising. Replace UUID placeholders with
IDs returned by the creation commands:

```sh
opentruth claim list --query "beam length" --subject beam --predicate length --review-status NEEDS_REVIEW --limit 20 --offset 0
opentruth claim list --query "beam Q" --exact-phrase
opentruth evidence link CLAIM_UUID SOURCE_UUID --relationship SUPPORTS --location "table 1" --excerpt "SYNTHETIC measurement" --actor "synthetic assessor"
opentruth review CLAIM_UUID --decision ACCEPTED_FOR_USE --reason "SYNTHETIC use decision" --actor "synthetic reviewer"
opentruth claim revise CLAIM_UUID --statement "SYNTHETIC corrected wording" --value 2 --reason "SYNTHETIC correction" --actor "synthetic editor"
opentruth evidence revise LINK_UUID --relationship CONTRADICTS --reason "SYNTHETIC reassessment" --actor "synthetic assessor"
opentruth conflicts check CLAIM_UUID --abs-tol 0.01 --rel-tol 0.000001
```

| Operation | Additional convenience inputs |
| --- | --- |
| `claim list` | `--query`, `--exact-phrase`, `--subject`, `--predicate`, `--review-status` |
| `claim revise CLAIM_UUID` | `--statement`, claim measurement/context/provenance flags, `--reason`, `--actor` |
| `evidence link CLAIM_UUID SOURCE_UUID` | `--relationship`, `--location`, `--excerpt`, `--actor` |
| `evidence revise LINK_UUID` | `--relationship`, `--location`, `--excerpt`, `--reason`, `--actor` |
| `review CLAIM_UUID` | `--decision`, `--reason`, `--actor` |
| `conflicts check CLAIM_UUID` | `--abs-tol`, `--rel-tol`, `--actor` |
| `claim add`, `source add`, `export` | `--actor` |

Revision reasons must be nonblank; claim correction resets its review status and requires
reassessment of earlier evidence. Review acceptance/rejection also requires a nonblank reason.
Supply explicit `--actor` when reassessing evidence so audit attribution identifies the current
assessor. The Python API's existing optional-actor behavior remains compatible.

`--statement` maps to `original_statement`, `--location` to `source_location`, and hyphenated
flags map to underscore API fields. Existing `--json` shapes remain supported; JSON and flags
may be combined only for different fields. Conflicting fields fail without applying the operation.
Invalid enum flags produce argparse exit code 2; engine validation failures produce the structured
error on stderr and exit code 1. Failed operations do not add claim revisions or audit events.

Numeric comparisons still require matching explicit contexts and compatible units. Changing
comparison tolerances changes only that recorded comparison; it does not modify claims or decide
scientific truth. See [comparison rules](conflict-detection.md).
