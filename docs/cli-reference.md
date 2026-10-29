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
