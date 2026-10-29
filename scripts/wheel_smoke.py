"""Install the built wheel in an isolated venv and exercise it outside the checkout."""

import os
import subprocess
import tempfile
import tomllib
import venv
from pathlib import Path

version = tomllib.loads(Path("pyproject.toml").read_text())["project"]["version"]
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
print("Independent wheel workflow and restore: PASS")
""",
        ],
        check=True,
        cwd=root,
    )
