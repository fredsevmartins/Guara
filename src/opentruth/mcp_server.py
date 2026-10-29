"""Official MCP SDK stdio adapter. No sockets or remote fetching."""

import sqlite3
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from pydantic import FiniteFloat, StrictFloat

from .engine import OpenTruth
from .models import Relationship, Review, SourceType


def create_server(workspace="."):
    engine = OpenTruth(workspace)
    server = FastMCP("OpenTruth", instructions="Registered evidence is not objective truth.")

    def invoke(method, **arguments):
        try:
            return getattr(engine, method)(**arguments)
        except (ValueError, TypeError, OSError, sqlite3.Error) as error:
            raise ToolError(
                "INVALID_INPUT_OR_STORAGE: check input, identifiers and workspace storage"
            ) from error

    @server.tool()
    def register_source(
        title: str,
        source_type: SourceType = "OTHER",
        authors: list[str] | None = None,
        doi: str | None = None,
        url: str | None = None,
        publication_date: str | None = None,
        file_path: str | None = None,
        actor: str | None = None,
    ) -> dict:
        """Register metadata or a workspace-relative file; never fetch or verify a URL."""
        return invoke(
            "register_source",
            title=title,
            source_type=source_type,
            authors=authors or [],
            doi=doi,
            url=url,
            publication_date=publication_date,
            file_path=file_path,
            actor=actor,
        )

    @server.tool()
    def add_claim(
        original_statement: str,
        subject: str | None = None,
        predicate: str | None = None,
        value: StrictFloat | str | None = None,
        unit: str | None = None,
        context: dict[str, Any] | None = None,
        context_template: Literal["engineering", "experiment", "study"] | None = None,
        provenance: dict[str, Any] | None = None,
        actor: str | None = None,
    ) -> dict:
        """Preserve an assertion exactly; creation does not verify it."""
        return invoke(
            "add_claim",
            original_statement=original_statement,
            subject=subject,
            predicate=predicate,
            value=value,
            unit=unit,
            context=context or {},
            context_template=context_template,
            provenance=provenance or {},
            actor=actor,
        )

    @server.tool()
    def link_evidence(
        claim_id: str,
        source_id: str,
        relationship: Relationship,
        source_location: str,
        excerpt: str,
        actor: str,
    ) -> dict:
        """Record an explicit, attributed evidence relationship that may need review."""
        return invoke(
            "link_evidence",
            claim_id=claim_id,
            source_id=source_id,
            relationship=relationship,
            source_location=source_location,
            excerpt=excerpt,
            actor=actor,
        )

    @server.tool()
    def search_claims(
        query: str = "",
        exact_phrase: bool = False,
        subject: str | None = None,
        predicate: str | None = None,
        review_status: Review | None = None,
    ) -> list[dict]:
        """Search stored assertions and return registered evidence summaries."""
        return invoke(
            "search_claims",
            query=query,
            exact_phrase=exact_phrase,
            subject=subject,
            predicate=predicate,
            review_status=review_status,
        )

    @server.tool()
    def inspect_claim(claim_id: str) -> dict:
        """Inspect assertion, registered evidence, revisions and recorded conflict checks."""
        return invoke("inspect_claim", claim_id=claim_id)

    @server.tool()
    def check_conflicts(
        claim_id: str,
        abs_tol: FiniteFloat = 0,
        rel_tol: FiniteFloat = 1e-9,
        actor: str | None = None,
    ) -> list[dict]:
        """Compare numeric values conservatively using registered context and units."""
        return invoke(
            "check_conflicts", claim_id=claim_id, abs_tol=abs_tol, rel_tol=rel_tol, actor=actor
        )

    @server.tool()
    def get_claim_history(claim_id: str) -> list[dict]:
        """Return ordered append-only lifecycle events."""
        return invoke("get_claim_history", claim_id=claim_id)

    @server.tool()
    def review_claim(
        claim_id: str, decision: Review, reason: str = "", actor: str | None = None
    ) -> dict:
        """Record an attributed review decision with reason, not a truth classification."""
        return invoke(
            "review_claim", claim_id=claim_id, decision=decision, reason=reason, actor=actor
        )

    @server.tool()
    def verify_sources(source_id: str | None = None) -> dict:
        """Check stored file hashes; byte integrity is not scientific source verification."""
        return invoke("verify_sources", source_id=source_id)

    @server.tool()
    def export_evidence(actor: str | None = None) -> dict:
        """Export schema-versioned metadata, relationships and history; excludes file bytes."""
        return invoke("export_evidence", actor=actor)

    return server


def run(workspace="."):
    create_server(workspace).run(transport="stdio")
