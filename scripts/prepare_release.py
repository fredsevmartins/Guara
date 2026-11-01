"""Assemble a source-and-wheel ZIP and SHA-256 manifest from tested distributions."""

import argparse
import hashlib
import shutil
import tarfile
import tomllib
import zipfile
from email.parser import BytesParser
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def prepare_release(dist_dir, output_dir, version):
    dist_dir, output_dir = Path(dist_dir), Path(output_dir)
    wheel = dist_dir / f"opentruth-{version}-py3-none-any.whl"
    source = dist_dir / f"opentruth-{version}.tar.gz"
    with zipfile.ZipFile(wheel) as archive:
        metadata = BytesParser().parsebytes(
            archive.read(f"opentruth-{version}.dist-info/METADATA")
        )
        if metadata["Name"] != "opentruth" or metadata["Version"] != version:
            raise ValueError("Wheel metadata does not match the requested release")

    # Read without extracting. Never allow archive members to escape the bundle prefix.
    contents = {}
    prefix = f"opentruth-{version}"
    with tarfile.open(source, "r:gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            if (
                path.is_absolute()
                or ".." in path.parts
                or "\\" in member.name
                or not path.parts
                or path.parts[0] != prefix
            ):
                raise ValueError(f"Unsafe or unexpected source archive member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile() or len(path.parts) < 2:
                raise ValueError(f"Unsupported source archive member: {member.name}")
            relative = PurePosixPath(*path.parts[1:]).as_posix()
            if relative in contents or path.parts[1] in {"dist", "delivery", ".git", ".venv"}:
                raise ValueError(f"Duplicate or generated source member: {member.name}")
            contents[relative] = archive.extractfile(member).read()

    required = {
        "README.md", "COMECE-AQUI.md", "LICENSE", "pyproject.toml",
        "src/opentruth/__init__.py", "assets/mascot-guara.png",
    }
    if not required.issubset(contents):
        raise ValueError("Source archive is missing required product files")
    project = tomllib.loads(contents["pyproject.toml"].decode("utf-8"))["project"]
    if project["name"] != "opentruth" or project["version"] != version:
        raise ValueError("Source metadata does not match the requested release")

    # All inputs are validated before creating output files.
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle = output_dir / f"Guara-{version}.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(contents.items()):
            info = zipfile.ZipInfo(f"Guara/{name}", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
        for artifact in (wheel, source):
            info = zipfile.ZipInfo(f"Guara/dist/{artifact.name}", (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, artifact.read_bytes())

    artifacts = [bundle]
    for artifact in (wheel, source):
        destination = output_dir / artifact.name
        if artifact.resolve() != destination.resolve():
            shutil.copyfile(artifact, destination)
        artifacts.append(destination)
    for name in (
        "assets/mascot-guara.png",
        "assets/social/guara-linkedin-en.png",
        "assets/social/guara-linkedin-white-en.png",
    ):
        if name in contents:
            destination = output_dir / PurePosixPath(name).name
            destination.write_bytes(contents[name])
            artifacts.append(destination)
    checksums = output_dir / "SHA256SUMS"
    checksums.write_text(
        "".join(
            f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n"
            for path in sorted(artifacts)
        ),
        encoding="utf-8",
    )
    return [*artifacts, checksums]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dist-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "release-assets")
    args = parser.parse_args()
    version = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    for path in prepare_release(args.dist_dir, args.output_dir, version):
        print(path)
