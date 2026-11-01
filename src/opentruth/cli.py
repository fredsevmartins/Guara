"""JSON-compatible CLI with optional convenience arguments and readable output."""

import argparse
import json
import sqlite3
import sys
import zipfile
from importlib.metadata import version

from .database import SCHEMA_VERSION
from .engine import OpenTruth
from .locking import WorkspaceBusy

COMMANDS = {
    ("source", "add"): "register_source",
    ("source", "verify"): "verify_sources",
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
    ("backup",): "backup",
}


def readable(result):
    if isinstance(result, list):
        return "\n\n".join(readable(item) for item in result) or "No records."
    if isinstance(result, dict) and "original_statement" in result:
        lines = [
            f"{result['id']}: {result['original_statement']}",
            f"Review: {result['review_status']}",
        ]
        if "evidence_status" in result:
            lines.append(f"Evidence: {result['evidence_status']}")
        lines.extend(f"Warning: {warning}" for warning in result.get("context_warnings", []))
        return "\n".join(lines)
    if isinstance(result, dict) and "scientific_verification" in result and "sources" in result:
        return "\n".join(
            ["Byte integrity only. Scientific verification: NOT_EVALUATED"]
            + [f"{s['source_id']}: {s['integrity_status']}" for s in result["sources"]]
        )
    return json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False)


def main():
    parser = argparse.ArgumentParser(description="Guara — Make AI Knowledge Verifiable.")
    parser.add_argument("--version", action="version", version=f"Guara {version('opentruth')}")
    parser.add_argument("--workspace", default=".", help="Allowed workspace and data root")
    parser.add_argument(
        "--lock-timeout", type=float, default=5, help="Operation lock wait, 0–60 seconds"
    )
    parser.add_argument("--format", choices=["json", "text"], default="json")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Initialize local SQLite storage")
    sub.add_parser("mcp", help="Run the MCP stdio server")
    restore = sub.add_parser("restore", help="Restore a backup into an absent data directory")
    restore.add_argument("archive_path")
    restore.add_argument("--data-dir", default=".opentruth")
    contexts = sub.add_parser("context", help="Optional scientific context checklists")
    context_sub = contexts.add_subparsers(required=True)
    templates = context_sub.add_parser("templates")
    templates.add_argument("name", nargs="?", choices=["engineering", "experiment", "study"])
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
        positional = {
            "add_claim": "original_statement",
            "register_source": "title",
            "verify_sources": "source_id",
            "inspect_claim": "claim_id",
            "get_claim_history": "claim_id",
            "check_conflicts": "claim_id",
            "backup": "archive_path",
        }.get(method)
        if positional:
            command.add_argument(positional, nargs="?")
        if method in {"search_claims", "check_conflicts", "get_claim_history"}:
            command.add_argument("--limit", type=int)
            command.add_argument("--offset", type=int)
        if method in {"search_claims", "inspect_claim"}:
            command.add_argument("--include-history", action="store_true", default=None)
        if method == "add_claim":
            for field in (
                "subject",
                "predicate",
                "value",
                "unit",
                "context",
                "provenance",
                "context_template",
            ):
                command.add_argument("--" + field.replace("_", "-"))
        if method == "register_source":
            command.add_argument("--file", dest="file_path")
            command.add_argument("--type", dest="source_type")
    args = parser.parse_args()
    try:
        if args.command == "mcp":
            from .mcp_server import run

            run(args.workspace, lock_timeout=args.lock_timeout)
            return
        if args.command == "restore":
            from .backup import restore_backup

            result = restore_backup(
                args.workspace, args.archive_path, args.data_dir, lock_timeout=args.lock_timeout
            )
        elif args.command == "context":
            from .contexts import TEMPLATES

            result = TEMPLATES[args.name] if args.name else TEMPLATES
        else:
            engine = OpenTruth(args.workspace, lock_timeout=args.lock_timeout)
            try:
                if args.command == "init":
                    result = {"schema_version": SCHEMA_VERSION, "status": "INITIALIZED"}
                else:
                    inputs = json.loads(args.json)
                    if not isinstance(inputs, dict):
                        raise ValueError("--json must be an object")
                    flags = vars(args)
                    for field in (
                        "original_statement",
                        "title",
                        "source_id",
                        "claim_id",
                        "archive_path",
                        "subject",
                        "predicate",
                        "value",
                        "unit",
                        "context",
                        "provenance",
                        "context_template",
                        "file_path",
                        "source_type",
                        "limit",
                        "offset",
                        "include_history",
                    ):
                        value = flags.get(field)
                        if value is None:
                            continue
                        if field in inputs:
                            raise ValueError("Do not supply an argument twice")
                        if field in {"context", "provenance"}:
                            value = json.loads(value)
                        if field == "value":
                            try:
                                value = json.loads(value)
                            except json.JSONDecodeError:
                                pass
                        inputs[field] = value
                    result = getattr(engine, args.method)(**inputs)
            finally:
                engine.close()
        print(
            readable(result)
            if args.format == "text"
            else json.dumps(result, ensure_ascii=False, allow_nan=False)
        )
        if isinstance(result, dict) and result.get("ok") is False:
            sys.exit(1)
    except WorkspaceBusy:
        print(
            json.dumps(
                {
                    "error": "WORKSPACE_BUSY",
                    "message": "Retry after the current operation finishes.",
                }
            ),
            file=sys.stderr,
        )
        sys.exit(1)
    except (ValueError, TypeError, OSError, sqlite3.Error, zipfile.BadZipFile, KeyError):
        # Never include raw filesystem/SQLite/ZIP errors in client-facing messages.
        print(
            json.dumps(
                {
                    "error": "INVALID_INPUT_OR_STORAGE",
                    "message": "Check arguments, identifiers, integrity, and workspace paths. "
                    "Restore requires an absent data directory.",
                }
            ),
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
