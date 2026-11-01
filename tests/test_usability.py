"""Resource lifetime and installation diagnostics regressions."""

import sqlite3
from importlib.metadata import version

import pytest
from test_interfaces import cli

from opentruth import OpenTruth, __version__


def test_context_manager_persists_and_closes(tmp_path):
    with OpenTruth(tmp_path) as app:
        claim = app.add_claim("SYNTHETIC context-manager record")
    with pytest.raises(sqlite3.ProgrammingError):
        app.db.execute("SELECT 1")
    with OpenTruth(tmp_path) as reopened:
        assert reopened.inspect_claim(claim["id"])["original_statement"] == claim["original_statement"]


def test_context_manager_closes_on_error_without_rolling_back_prior_operations(tmp_path):
    with pytest.raises(RuntimeError, match="synthetic failure"), OpenTruth(tmp_path) as app:
        claim = app.add_claim("SYNTHETIC committed operation")
        raise RuntimeError("synthetic failure")
    with pytest.raises(sqlite3.ProgrammingError):
        app.db.execute("SELECT 1")
    with OpenTruth(tmp_path) as reopened:
        assert reopened.inspect_claim(claim["id"])["id"] == claim["id"]


def test_version_does_not_create_store_or_require_workspace(tmp_path):
    result = cli(tmp_path / "does-not-exist", "--version")
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == f"Guara {version('opentruth')}"
    assert version("opentruth") == __version__
    assert list(tmp_path.iterdir()) == []
