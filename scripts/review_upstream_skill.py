#!/usr/bin/env python3
"""Compare selected upstream files with a pinned audited revision.

This tool is intentionally read-only. It reports upstream changes for a curator
to evaluate; it never overwrites a Monomind skill or advances the audit pin.
"""

from __future__ import annotations

import argparse
import difflib
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path
from urllib.parse import quote, urlparse


SHA_RE = re.compile(r"^[0-9a-f]{40}$")
REQUIRED_FIELDS = {
    "schema_version",
    "integration",
    "repository",
    "tracking_ref",
    "audited_revision",
    "tracked_files",
    "integration_files",
}


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    missing = sorted(REQUIRED_FIELDS - data.keys())
    if missing:
        raise ValueError(f"manifest missing fields: {', '.join(missing)}")
    if data["schema_version"] != 1:
        raise ValueError(f"unsupported schema_version: {data['schema_version']!r}")
    if not SHA_RE.fullmatch(data["audited_revision"]):
        raise ValueError("audited_revision must be a full lowercase Git SHA")
    tracked = data["tracked_files"]
    if not isinstance(tracked, list) or not tracked:
        raise ValueError("tracked_files must be a non-empty list")
    for entry in tracked:
        if not isinstance(entry, dict) or not entry.get("path") or not entry.get("reason"):
            raise ValueError("each tracked_files entry requires path and reason")
    return data


def resolve_revision(repository: str, target: str) -> str:
    if SHA_RE.fullmatch(target):
        return target
    result = subprocess.run(
        ["git", "ls-remote", repository, target],
        check=True,
        capture_output=True,
        text=True,
    )
    matches = [line.split()[0] for line in result.stdout.splitlines() if line.strip()]
    if len(matches) != 1 or not SHA_RE.fullmatch(matches[0]):
        raise ValueError(f"target {target!r} did not resolve to exactly one Git revision")
    return matches[0]


def github_raw_url(repository: str, revision: str, source_path: str) -> str:
    parsed = urlparse(repository)
    if parsed.scheme != "https" or parsed.netloc != "github.com":
        raise ValueError("only https://github.com repositories are supported")
    parts = [part for part in parsed.path.removesuffix(".git").split("/") if part]
    if len(parts) != 2:
        raise ValueError("repository URL must identify one GitHub owner and repository")
    owner, repo = parts
    return (
        f"https://raw.githubusercontent.com/{quote(owner)}/{quote(repo)}/"
        f"{revision}/{quote(source_path, safe='/')}"
    )


def fetch_text(repository: str, revision: str, source_path: str) -> str:
    request = urllib.request.Request(
        github_raw_url(repository, revision, source_path),
        headers={"User-Agent": "monomind-upstream-review/1"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def render_report(manifest: dict, target_revision: str, fetcher=fetch_text) -> str:
    repository = manifest["repository"]
    audited = manifest["audited_revision"]
    lines = [
        f"Integration: {manifest['integration']}",
        f"Repository: {repository}",
        f"Audited revision: {audited}",
        f"Target revision:  {target_revision}",
        "Mode: read-only review; no catalog files were changed.",
        "",
    ]
    changed = False
    for entry in manifest["tracked_files"]:
        source_path = entry["path"]
        before = fetcher(repository, audited, source_path)
        after = fetcher(repository, target_revision, source_path)
        diff = list(
            difflib.unified_diff(
                before.splitlines(),
                after.splitlines(),
                fromfile=f"{source_path}@{audited[:12]}",
                tofile=f"{source_path}@{target_revision[:12]}",
                lineterm="",
            )
        )
        lines.append(f"## {source_path}")
        lines.append(f"Reason: {entry['reason']}")
        if diff:
            changed = True
            lines.extend(diff)
        else:
            lines.append("No content changes.")
        lines.append("")
    lines.extend(
        [
            f"Changes detected: {'yes' if changed else 'no'}",
            "",
            "If changes are adopted, update the curated integration manually,",
            "advance the manifest only after review, refresh evals/provenance as needed,",
            "and run the repository and skill validators. Do not merge upstream text wholesale.",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="path to an upstream manifest")
    parser.add_argument(
        "--target",
        help="full Git SHA or remote ref; defaults to the manifest tracking_ref",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        manifest = load_manifest(args.manifest)
        target = args.target or manifest["tracking_ref"]
        revision = resolve_revision(manifest["repository"], target)
        print(render_report(manifest, revision))
    except (OSError, ValueError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print(f"upstream review failed: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
