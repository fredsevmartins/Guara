"""Argparse CLI: structured arguments are JSON objects shared with the core API."""

import argparse
import json
import sqlite3
import sys

from .engine import OpenTruth

COMMANDS = {
    ("source", "add"): "register_source",
    ("claim", "add"): "add_claim",
    ("claim", "list"): "search_claims",
    ("claim", "inspect"): "inspect_claim",
    ("claim", "revise"): "revise_claim",
    ("evidence", "link"): "link_evidence",
    ("evidence", "revise"): "revise_evidence",
    ("conflicts", "check"): "check_conflicts",
    ("history",): "get_claim_history",
    ("review",): "review_claim",
    ("export",): "export_evidence",
}


def main():
    parser = argparse.ArgumentParser(description="OpenTruth — Make AI Knowledge Verifiable.")
    parser.add_argument("--workspace", default=".", help="Allowed workspace and data root")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Initialize local SQLite storage")
    sub.add_parser("mcp", help="Run the MCP stdio server")
    groups = {}
    for parts, method in COMMANDS.items():
        parent = sub
        if len(parts) == 2:
            if parts[0] not in groups:
                groups[parts[0]] = sub.add_parser(parts[0]).add_subparsers(required=True)
            parent = groups[parts[0]]
        command = parent.add_parser(parts[-1], help=method)
        command.add_argument("--json", default="{}", help="JSON object of Python API arguments")
        command.set_defaults(method=method)
    args = parser.parse_args()
    try:
        if args.command == "mcp":
            from .mcp_server import run

            run(args.workspace)
            return
        engine = OpenTruth(args.workspace)
        try:
            if args.command == "init":
                result = {"schema_version": 1, "status": "INITIALIZED"}
            else:
                inputs = json.loads(args.json)
                if not isinstance(inputs, dict):
                    raise ValueError("--json must be an object")
                result = getattr(engine, args.method)(**inputs)
            print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        finally:
            engine.close()
    except (ValueError, TypeError, OSError, sqlite3.Error):
        print(
            json.dumps(
                {
                    "error": "INVALID_INPUT_OR_STORAGE",
                    "message": "Operation failed; check input, identifiers, and workspace storage.",
                }
            ),
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
