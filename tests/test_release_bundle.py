"""Validate release contents, checksums, metadata and source archive boundaries."""

import hashlib
import io
import tarfile
import zipfile

import pytest

from scripts.prepare_release import prepare_release

VERSION = "0.1.3"


def distributions(root, *, extra=None, source_version=VERSION, wheel_version=VERSION):
    dist = root / "dist"
    dist.mkdir()
    with zipfile.ZipFile(dist / f"opentruth-{VERSION}-py3-none-any.whl", "w") as archive:
        archive.writestr(
            f"opentruth-{VERSION}.dist-info/METADATA",
            f"Name: opentruth\nVersion: {wheel_version}\n",
        )
    files = dict.fromkeys(
        ["README.md", "COMECE-AQUI.md", "LICENSE", "src/opentruth/__init__.py"], b"SYNTHETIC"
    )
    files["assets/mascot-guara.png"] = b"synthetic mascot bytes"
    files["pyproject.toml"] = (
        f'[project]\nname = "opentruth"\nversion = "{source_version}"\n'.encode()
    )
    with tarfile.open(dist / f"opentruth-{VERSION}.tar.gz", "w:gz") as archive:
        for name, data in files.items():
            info = tarfile.TarInfo(f"opentruth-{VERSION}/{name}")
            info.size = len(data)
            archive.addfile(info, io.BytesIO(data))
        if extra:
            name, kind = extra
            info = tarfile.TarInfo(name)
            info.type = kind
            if kind == tarfile.SYMTYPE:
                info.linkname = "../../outside"
            archive.addfile(info, io.BytesIO())
    return dist


def test_bundle_contains_installable_files_and_verifiable_checksums(tmp_path):
    dist = distributions(tmp_path)
    out = tmp_path / "release"
    artifacts = prepare_release(dist, out, VERSION)
    with zipfile.ZipFile(out / f"Guara-{VERSION}.zip") as archive:
        assert archive.testzip() is None
        assert archive.read("Guara/README.md") == b"SYNTHETIC"
        assert archive.read(f"Guara/dist/opentruth-{VERSION}-py3-none-any.whl") == (
            dist / f"opentruth-{VERSION}-py3-none-any.whl"
        ).read_bytes()
    for row in (out / "SHA256SUMS").read_text().splitlines():
        digest, name = row.split("  ", 1)
        assert hashlib.sha256((out / name).read_bytes()).hexdigest() == digest
    before = {path.name: path.read_bytes() for path in artifacts}
    prepare_release(dist, out, VERSION)
    assert {path.name: path.read_bytes() for path in artifacts} == before


@pytest.mark.parametrize(
    "extra",
    [
        ("../outside", tarfile.REGTYPE),
        (f"opentruth-{VERSION}/../outside", tarfile.REGTYPE),
        (f"opentruth-{VERSION}/link", tarfile.SYMTYPE),
        (f"opentruth-{VERSION}/README.md", tarfile.REGTYPE),
        (f"opentruth-{VERSION}/delivery/old.zip", tarfile.REGTYPE),
    ],
)
def test_invalid_source_archive_cannot_create_delivery(tmp_path, extra):
    dist = distributions(tmp_path, extra=extra)
    with pytest.raises(ValueError):
        prepare_release(dist, tmp_path / "release", VERSION)
    assert not (tmp_path / "release").exists()
    assert not (tmp_path / "outside").exists()


@pytest.mark.parametrize("field", ["source_version", "wheel_version"])
def test_mismatched_versions_cannot_create_delivery(tmp_path, field):
    dist = distributions(tmp_path, **{field: "0.0.0"})
    with pytest.raises(ValueError, match="metadata"):
        prepare_release(dist, tmp_path / "release", VERSION)
    assert not (tmp_path / "release").exists()
