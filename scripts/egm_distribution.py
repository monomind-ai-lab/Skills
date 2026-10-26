#!/usr/bin/env python3
"""Verify or export the pinned EGM distribution offline; never install or sync it."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import stat
import sys
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = Path("distributions/egm/upstream")
SHA = re.compile(r"[0-9a-f]{40}")


def git_hash(kind: str, data: bytes) -> str:
    return hashlib.sha1(f"{kind} {len(data)}\0".encode() + data).hexdigest()


def tree_hash(files: dict[str, dict]) -> str:
    """Reconstruct Git's tree identity from the full blob inventory."""
    tree: dict = {}
    for name, entry in files.items():
        parts = PurePosixPath(name).parts
        node = tree
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = (entry["mode"], entry["blob"])

    def digest(node):
        records = []
        for name, value in node.items():
            directory = isinstance(value, dict)
            mode, oid = ("40000", digest(value)) if directory else value
            key = name.encode() + (b"/" if directory else b"")
            payload = mode.encode() + b" " + name.encode() + b"\0" + bytes.fromhex(oid)
            records.append((key, payload))
        return git_hash("tree", b"".join(payload for _, payload in sorted(records)))

    return digest(tree)


def safe_name(name: str) -> bool:
    path = PurePosixPath(name)
    return (
        bool(name) and not path.is_absolute() and path.as_posix() == name
        and not any(part in {"..", ".", ".git"} for part in path.parts)
    )


def inventory(root: Path) -> dict[str, dict]:
    files = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise ValueError(f"snapshot symlink is unsupported: {relative}")
        if path.is_dir():
            continue
        if not stat.S_ISREG(path.stat().st_mode) or not safe_name(relative):
            raise ValueError(f"unsupported snapshot entry: {relative}")
        executable = bool(path.stat().st_mode & 0o111)
        files[relative] = {
            "mode": "100755" if executable else "100644",
            "blob": git_hash("blob", path.read_bytes()),
        }
    return files


def verify(repo: Path) -> dict:
    manifest_path = repo / "upstreams/egm.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (
        manifest.get("schema_version") != 2
        or manifest.get("integration") != "egm"
        or manifest.get("repository") != "https://github.com/google/elephant-goldfish-model.git"
        or manifest.get("tracking_ref") != "refs/heads/main"
        or not SHA.fullmatch(manifest.get("audited_revision", ""))
    ):
        raise ValueError("invalid EGM provenance")
    snapshot = manifest["snapshot"]
    if snapshot["path"] != SNAPSHOT.as_posix():
        raise ValueError("unexpected snapshot path")
    expected = snapshot["files"]
    if not isinstance(expected, dict) or not expected:
        raise ValueError("snapshot inventory must be non-empty")
    for name, entry in expected.items():
        if (
            not safe_name(name) or entry.get("mode") not in {"100644", "100755"}
            or not SHA.fullmatch(entry.get("blob", ""))
        ):
            raise ValueError(f"invalid snapshot inventory entry: {name}")
    source = repo / SNAPSHOT
    # Refuse redirected parents as well as redirected files.
    for path in (repo / "distributions", source.parent, source):
        if path.is_symlink():
            raise ValueError(f"symlinked distribution path: {path.name}")
    actual = inventory(source)
    missing = sorted(set(expected) - set(actual))
    extra = sorted(set(actual) - set(expected))
    changed = sorted(name for name in expected.keys() & actual.keys() if expected[name] != actual[name])
    if missing or extra or changed:
        raise ValueError(f"snapshot mismatch: missing={missing}, extra={extra}, changed={changed}")
    if tree_hash(actual) != snapshot["tree"]:
        raise ValueError("snapshot Git tree does not match provenance")
    required = ["README.md", "LICENSE", "docs/codex.md", "docs/claude.md", "plugin.json"]
    for name in required:
        if name not in actual:
            raise ValueError(f"missing runtime resource: {name}")
    for directory in ("skills/", "agents/", "resources/"):
        if not any(name.startswith(directory) for name in actual):
            raise ValueError(f"missing runtime directory: {directory}")
    for name in ("plugin.json", ".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
        plugin = json.loads((source / name).read_text(encoding="utf-8"))
        if plugin.get("name") != "egm" or plugin.get("version") != manifest["audited_package_version"]:
            raise ValueError(f"plugin identity/version mismatch: {name}")
    native = json.loads((source / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    if native.get("skills") != "./skills/":
        raise ValueError("unexpected EGM skill discovery root")
    for entry in manifest["supplemental_licenses"]:
        name = entry["path"]
        if not safe_name(name) or not name.startswith("distributions/egm/licenses/"):
            raise ValueError("invalid supplemental license path")
        path = repo / name
        if path.is_symlink() or path.parent.is_symlink():
            raise ValueError("symlinked supplemental license")
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError(f"supplemental license mismatch: {name}")
    # Export copies the enclosing bundle, so verify that boundary too. Otherwise
    # an unrelated file or redirected guide beside upstream/ could be exported.
    bundle = source.parent
    expected_bundle = {"README.md", "AGENTS.md"}
    expected_bundle.update("upstream/" + name for name in expected)
    expected_bundle.update(
        Path(entry["path"]).relative_to("distributions/egm").as_posix()
        for entry in manifest["supplemental_licenses"]
    )
    actual_bundle = set(inventory(bundle))
    if actual_bundle != expected_bundle:
        raise ValueError(
            "distribution bundle mismatch: "
            f"missing={sorted(expected_bundle - actual_bundle)}, "
            f"extra={sorted(actual_bundle - expected_bundle)}"
        )
    # The ordinary catalog plugin must not register the optional EGM runtime.
    catalog = json.loads((repo / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    if catalog.get("skills") != "./skills/":
        raise ValueError("catalog plugin must discover only the normal skills directory")
    return manifest


def export(repo: Path, destination: Path) -> dict:
    destination = destination.expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        raise ValueError("export destination already exists")
    if destination.resolve().is_relative_to(repo.resolve()):
        raise ValueError("export destination must be outside the catalog checkout")
    manifest = verify(repo)
    # copytree atomically claims the new directory and refuses an existing target.
    # On I/O failure a partial export remains visible; never delete unknown files.
    shutil.copytree(repo / "distributions/egm", destination)
    (destination / "UPSTREAM.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    # Verify the exported bytes too, rather than trusting the copy operation.
    if inventory(destination / "upstream") != manifest["snapshot"]["files"]:
        raise ValueError("export verification failed; partial export retained")
    for entry in manifest["supplemental_licenses"]:
        relative = Path(entry["path"]).relative_to("distributions/egm")
        if hashlib.sha256((destination / relative).read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError("exported supplemental license mismatch")
    return manifest


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify", help="check source, licensing, and plugin boundary offline")
    exporting = commands.add_parser("export", help="copy the verified complete distribution; no installation")
    exporting.add_argument("destination", type=Path)
    args = parser.parse_args(argv)
    try:
        result = export(args.repo, args.destination) if args.command == "export" else verify(args.repo)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"EGM distribution failed: {error}", file=sys.stderr)
        return 1
    print(f"EGM {args.command} passed: {result['audited_revision']} ({len(result['snapshot']['files'])} files).")
    if args.command == "export":
        print(f"Plugin root: {args.destination.expanduser().absolute() / 'upstream'}")
        print("Export only; no plugin installed and no upstream code executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
