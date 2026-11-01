import asyncio
import json
import os
import subprocess
import sys
from datetime import timedelta

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def cli(workspace, *args):
    return subprocess.run(
        [sys.executable, "-m", "opentruth.cli", "--workspace", str(workspace), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_cli(tmp_path):
    assert cli(tmp_path, "init").returncode == 0
    added = cli(tmp_path, "claim", "add", "--json", '{"original_statement":"synthetic"}')
    assert added.returncode == 0, added.stderr
    identifier = json.loads(added.stdout)["id"]
    assert (
        json.loads(
            cli(tmp_path, "claim", "inspect", "--json", json.dumps({"claim_id": identifier})).stdout
        )["original_statement"]
        == "synthetic"
    )
    assert len(json.loads(cli(tmp_path, "export").stdout)["claims"]) == 1
    for invalid in ("{", "[]", '{"original_statement":""}'):
        assert cli(tmp_path, "claim", "add", "--json", invalid).returncode == 1
    assert cli(tmp_path, "--help").returncode == 0


def test_real_mcp_session(tmp_path):
    async def scenario():
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "opentruth.cli", "--workspace", str(tmp_path), "mcp"],
            env=dict(os.environ),
        )
        async with (
            stdio_client(params) as (read, write),
            ClientSession(read, write, read_timeout_seconds=timedelta(seconds=15)) as session,
        ):
            await session.initialize()
            listed = await session.list_tools()
            assert len(listed.tools) == 12

            async def call(name, args):
                result = await session.call_tool(name, args)
                assert not result.isError, result
                return json.loads(result.content[0].text)

            a = await call(
                "add_claim",
                {
                    "original_statement": "SYNTHETIC: a",
                    "subject": "x",
                    "predicate": "p",
                    "value": 1,
                    "unit": "m",
                    "context": {"method": "A"},
                },
            )
            boolean_measurement = await session.call_tool(
                "add_claim", {"original_statement": "SYNTHETIC: invalid", "value": True}
            )
            assert boolean_measurement.isError
            source = await call("register_source", {"title": "SYNTHETIC source"})
            linked = await call(
                "link_evidence",
                {
                    "claim_id": a["id"],
                    "source_id": source["id"],
                    "relationship": "SUPPORTS",
                    "source_location": "p1",
                    "excerpt": "synthetic",
                    "actor": "synthetic tester",
                },
            )
            inspected = await call("inspect_claim", {"claim_id": a["id"]})
            assert inspected["evidence_status"] == "SUPPORTED_BY_REGISTERED_EVIDENCE"
            # FastMCP lists may be returned as one content block per item or wrapped structured output.
            search = await session.call_tool("search_claims", {"query": "SYNTHETIC"})
            assert not search.isError and a["id"] in str(search)
            await call(
                "review_claim",
                {
                    "claim_id": a["id"],
                    "decision": "ACCEPTED_FOR_USE",
                    "reason": "synthetic review",
                    "actor": "synthetic reviewer",
                },
            )
            unattributed = await call(
                "review_claim", {"claim_id": a["id"], "decision": "NEEDS_REVIEW"}
            )
            assert unattributed["review_status"] == "NEEDS_REVIEW"
            history = await session.call_tool("get_claim_history", {"claim_id": a["id"]})
            assert not history.isError and "HUMAN_REVIEW" in str(history)
            conflict = await session.call_tool("check_conflicts", {"claim_id": a["id"]})
            assert not conflict.isError
            await call(
                "revise_claim",
                {
                    "claim_id": a["id"],
                    "reason": "synthetic correction",
                    "changes": {"original_statement": "SYNTHETIC revised"},
                    "actor": "tester",
                },
            )
            stale = await call("inspect_claim", {"claim_id": a["id"]})
            assert stale["evidence_status"] == "INSUFFICIENT_EVIDENCE"
            await call(
                "revise_evidence",
                {
                    "link_id": linked["id"],
                    "reason": "synthetic reassessment",
                    "actor": "tester",
                    "relationship": "CONTRADICTS",
                },
            )
            revised = await call("inspect_claim", {"claim_id": a["id"]})
            assert revised["evidence_status"] == "CONTRADICTED_BY_REGISTERED_EVIDENCE"
            assert revised["history"][-1]["actor"] == "tester"
            exported = await call("export_evidence", {})
            integrity = await call("verify_sources", {})
            assert integrity["ok"] is True
            assert integrity["scientific_verification"] == "NOT_EVALUATED"
            assert len(exported["claims"]) == 1
            invalid = await session.call_tool("inspect_claim", {"claim_id": "invalid"})
            assert invalid.isError
            escaped = await session.call_tool(
                "register_source", {"title": "x", "file_path": "/etc/passwd"}
            )
            assert escaped.isError and str(tmp_path) not in str(escaped)

    asyncio.run(asyncio.wait_for(scenario(), timeout=30))
