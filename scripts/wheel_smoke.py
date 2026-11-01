"""Install the built wheel in an isolated venv and exercise it outside the checkout."""

import argparse
import os
import subprocess
import tempfile
import tomllib
import venv
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--wheel", type=Path, help="Wheel to install; defaults to the current version in dist/")
args = parser.parse_args()
version = tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]
if args.wheel:
    wheel = args.wheel.resolve(strict=True)
else:
    (wheel,) = Path("dist").glob(f"opentruth-{version}-*.whl")
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    venv.EnvBuilder(with_pip=True).create(root / "venv")
    python = root / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    subprocess.run([str(python), "-m", "pip", "install", str(wheel.resolve())], check=True)
    subprocess.run([str(python), "-m", "pip", "check"], check=True)
    subprocess.run(
        [
            str(python),
            "-I",
            "-c",
            """
from pathlib import Path
from opentruth import OpenTruth
from opentruth.backup import restore_backup
Path("data").mkdir()
app = OpenTruth("data")
a = app.add_claim("SYNTHETIC wheel test", provenance={"synthetic": True})
s = app.register_source("SYNTHETIC metadata")
app.link_evidence(a["id"], s["id"], "SUPPORTS", "p1", "SYNTHETIC", "tester")
assert app.inspect_claim(a["id"])["evidence_status"] == "SUPPORTED_BY_REGISTERED_EVIDENCE"
app.backup("snapshot.zip")
app.close()
restore_backup("data", "snapshot.zip", "restored")
app = OpenTruth("data", "restored")
assert app.inspect_claim(a["id"])["original_statement"] == "SYNTHETIC wheel test"
assert app.verify_sources()["ok"]
app.close()
# Exercise the installed CLI from outside the source checkout.
import json
import subprocess
import sys
from importlib.metadata import version


def cli(*args):
    result = subprocess.run(
        [sys.executable, "-I", "-m", "opentruth.cli", "--workspace", "cli-data", *args],
        capture_output=True, text=True, check=True,
    )
    return result.stdout


assert cli("--version").strip() == f"Guara {version('opentruth')}"
assert not Path("cli-data").exists()
Path("cli-data").mkdir()
assert json.loads(cli("init"))["status"] == "INITIALIZED"
claim = json.loads(cli("claim", "add", "SYNTHETIC installed CLI"))
assert json.loads(cli("claim", "inspect", claim["id"]))["id"] == claim["id"]
source = json.loads(cli("source", "add", "SYNTHETIC installed source"))
link = json.loads(cli(
    "evidence", "link", claim["id"], source["id"], "--relationship", "SUPPORTS",
    "--location", "p1", "--excerpt", "SYNTHETIC", "--actor", "installer",
))
cli("review", claim["id"], "--decision", "INCONCLUSIVE", "--actor", "installer")
cli(
    "claim", "revise", claim["id"], "--statement", "SYNTHETIC revised installed CLI",
    "--reason", "SYNTHETIC correction", "--actor", "installer",
)
assert json.loads(cli("claim", "inspect", claim["id"]))["evidence_status"] == "INSUFFICIENT_EVIDENCE"
cli(
    "evidence", "revise", link["id"], "--relationship", "CONTRADICTS",
    "--reason", "SYNTHETIC reassessment", "--actor", "installer",
)
assert len(json.loads(cli("claim", "list", "--query", "revised installed", "--exact-phrase"))) == 1
assert len(json.loads(cli("export"))["claims"]) == 1
cli("backup", "cli-backup.zip")
cli("restore", "cli-backup.zip", "--data-dir", "restored")
with OpenTruth("cli-data", "restored") as restored:
    assert restored.inspect_claim(claim["id"])["original_statement"] == "SYNTHETIC revised installed CLI"
    assert restored.inspect_claim(claim["id"])["evidence_status"] == "CONTRADICTED_BY_REGISTERED_EVIDENCE"
print("Independent wheel API, CLI lifecycle, version, backup and restore: PASS")
""",
        ],
        check=True,
        cwd=root,
    )
