"""Record and compare the exact files of a local game, using Python 3.11+."""

import argparse
from hashlib import file_digest
import json
from pathlib import Path, PurePosixPath
import re
import sys
from zipfile import BadZipFile, ZipFile


def validate_path(path):
    parts = path.split("/")
    if any(part in {"", ".", ".."} for part in parts) or "\\" in path or "\x00" in path:
        raise ValueError(f"Invalid relative path: {path!r}")
    if PurePosixPath(path).is_absolute() or ":" in parts[0]:
        raise ValueError(f"Invalid relative path: {path!r}")
    return path


def digest(stream, size):
    return {"bytes": size, "sha256": file_digest(stream, "sha256").hexdigest()}


def directory_manifest(root):
    files = {}
    for file in sorted(root.rglob("*")):
        if file.is_symlink() or (hasattr(file, "is_junction") and file.is_junction()):
            raise ValueError(f"Linked game file or directory: {file}")
        if file.is_file():
            name = validate_path(file.relative_to(root).as_posix())
            with file.open("rb") as stream:
                files[name] = digest(stream, file.stat().st_size)
    return files


def zip_manifest(archive, prefix):
    files = {}
    with ZipFile(archive) as bundle:
        for member in bundle.infolist():
            if member.is_dir() or not member.filename.startswith(prefix):
                continue
            name = validate_path(member.filename[len(prefix):])
            if name in files:
                raise ValueError(f"Duplicate archive member under game root: {name!r}")
            with bundle.open(member) as stream:
                files[name] = digest(stream, member.file_size)
    return files


def summarize(files):
    return f"{len(files)} files, {sum(info['bytes'] for info in files.values())} bytes"


def snapshot(args):
    root = args.source.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Snapshot requires a staged game directory")
    if args.output.resolve().is_relative_to(root):
        raise ValueError("Write the manifest outside the game directory")
    files = directory_manifest(root)
    if not files:
        raise ValueError("Game directory has no files")
    args.output.write_text(json.dumps({"schema": 1, "files": files}, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(f"Recorded {summarize(files)}")
    return 0


def verify(args):
    document = json.loads(args.manifest.read_text(encoding="utf-8"))
    if not isinstance(document, dict) or document.get("schema") != 1:
        raise ValueError("Expected a version 1 mirror manifest")
    expected = document.get("files")
    if not isinstance(expected, dict) or not expected:
        raise ValueError("Manifest has no game files")
    for path, info in expected.items():
        validate_path(path)
        if (not isinstance(info, dict) or type(info.get("bytes")) is not int
                or info["bytes"] < 0 or not isinstance(info.get("sha256"), str)
                or not re.fullmatch(r"[0-9a-f]{64}", info["sha256"])):
            raise ValueError(f"Invalid manifest entry: {path!r}")

    source = args.source.resolve(strict=True)
    prefix = validate_path(args.prefix.rstrip("/")) + "/" if args.prefix else ""
    if source.is_dir() and prefix:
        raise ValueError("--prefix is for archive members")
    found = directory_manifest(source) if source.is_dir() else zip_manifest(source, prefix)
    allowed_changes = {validate_path(path) for path in args.changed}
    allowed_extras = {validate_path(path) for path in args.extra}
    if allowed_changes - expected.keys() or allowed_extras & expected.keys():
        raise ValueError("Use --changed for files in the baseline and --extra for new files")

    missing = expected.keys() - found.keys()
    extra = found.keys() - expected.keys() - allowed_extras
    changed = {path for path in expected.keys() & found.keys() if expected[path] != found[path]}
    unapproved = changed - allowed_changes
    for label, paths in (("missing", missing), ("extra", extra),
                         ("changed", unapproved), ("expected change", allowed_changes & changed),
                         ("expected extra", allowed_extras & found.keys())):
        for path in sorted(paths):
            print(f"{label}: {path}")
    result = "Mismatch" if missing or extra or unapproved else "Verified"
    print(f"{result} {summarize(found)}")
    return 1 if result == "Mismatch" else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    record = commands.add_parser("snapshot", help="Record a game directory")
    record.add_argument("source", type=Path)
    record.add_argument("-o", "--output", type=Path, required=True)
    record.set_defaults(run=snapshot)
    compare = commands.add_parser("verify", help="Compare a directory, ZIP or APK to a manifest")
    compare.add_argument("manifest", type=Path)
    compare.add_argument("source", type=Path)
    compare.add_argument("--prefix", default="", help="Game root inside ZIP/APK")
    compare.add_argument("--changed", action="append", default=[], help="Allow a listed file to change")
    compare.add_argument("--extra", action="append", default=[], help="Allow a named wrapper file")
    compare.set_defaults(run=verify)
    args = parser.parse_args()
    try:
        return args.run(args)
    except (OSError, ValueError, BadZipFile, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
