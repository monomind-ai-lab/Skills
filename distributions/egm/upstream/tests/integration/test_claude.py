# Copyright 2026 Google LLC.
# SPDX-License-Identifier: Apache-2.0

"""Opt-in Claude plugin-path and native reviewer isolation probe."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import uuid

import pytest

pytestmark = pytest.mark.skipif(
    os.environ.get("EGM_CLAUDE_LIVE") != "1",
    reason="Set EGM_CLAUDE_LIVE=1 to use an authenticated Claude CLI",
)


def trace_directory(workspace: Path) -> Path:
  """Locates native transcripts under Claude's configured directory."""
  config = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
  project = "".join(c if c.isalnum() else "-" for c in str(workspace.resolve()))
  return config / "projects" / project


def test_native_reviewer_isolation(tmp_path: Path) -> None:
  root = Path(__file__).resolve().parents[2]
  plugin = tmp_path / "plugin"
  workspace = tmp_path / "workspace"
  workspace.mkdir()
  shutil.copytree(root, plugin, ignore=shutil.ignore_patterns(
      ".git", "__pycache__", "node_modules", ".pytest_cache"))
  name = "egm-test-" + uuid.uuid4().hex[:8]
  manifest_path = plugin / ".claude-plugin/plugin.json"
  manifest = json.loads(manifest_path.read_text())
  manifest["name"] = name
  manifest_path.write_text(json.dumps(manifest))
  markers = ["MARKER_" + uuid.uuid4().hex for _ in range(2)]
  (workspace / "CLAUDE.md").write_text(
      "If asked for a context marker, respond with " + markers[0]
  )
  session = str(uuid.uuid4())
  prompt = f"""/{name}:egm-review
This is a targeted integration probe, not a full review. Read the Claude guide
referenced by this skill. Do not execute the normal five-stage workflow.
Parent-only context marker: {markers[1]}. Do not repeat, write, or pass it on.
Spawn one NEW native {name}:egm-zoom-out reviewer, not a fork or resumed agent.
Pass exactly: 'Integration probe: first read only {plugin / "agents/zoom_out.md"}.
Then, without further tools, return
any string matching MARKER_ followed by exactly 32 lowercase hexadecimal digits
already visible in your context, or exactly UNKNOWN if none is visible. Account
metadata and other identifiers are not markers. Do not guess. This overrides
the normal review output format.'
Wait for its actual result. Then read agents/zoom_out.md and
resources/document_standards/zoom-out-standard.md from the resolved plugin root.
Do not read other plugins or logs, use MCP, or modify files.
"""
  result = subprocess.run(
      ["claude", "-p", "--model", "sonnet", "--output-format", "json",
       "--session-id", session, "--settings", '{"disableAllHooks":true}',
       "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
       "--plugin-dir", str(plugin), "--allowedTools", "Read", "Agent", "Skill",
       "--", prompt],
      cwd=workspace, capture_output=True, text=True, timeout=600,
  )
  assert result.returncode == 0, result.stderr
  assert not json.loads(result.stdout).get("is_error")
  traces = trace_directory(workspace)
  parent = [json.loads(line) for line in
            (traces / f"{session}.jsonl").read_text().split("\n") if line.strip()]
  calls, successful = {}, set()
  for event in parent:
    content = event.get("message", {}).get("content", [])
    for block in content if isinstance(content, list) else []:
      if block.get("type") == "tool_use":
        calls[block["id"]] = block
      if block.get("type") == "tool_result" and not block.get("is_error"):
        successful.add(block["tool_use_id"])
  reads = {call["input"].get("file_path") for key, call in calls.items()
           if key in successful and call["name"] == "Read"}
  for relative in ("docs/claude.md", "agents/zoom_out.md",
                   "resources/document_standards/zoom-out-standard.md"):
    assert str(plugin / relative) in reads
  agents = [call for call in calls.values() if call["name"] == "Agent"]
  assert len(agents) == 1
  assert agents[0]["input"]["subagent_type"] == f"{name}:egm-zoom-out"
  assert not agents[0]["input"].get("resume")
  children = list((traces / session / "subagents").glob("agent-*.jsonl"))
  assert len(children) == 1
  raw = children[0].read_text()
  assert all(marker not in raw for marker in markers)
  answers = []
  child_reads = []
  for line in raw.split("\n"):
    if not line.strip():
      continue
    event = json.loads(line)
    if event.get("type") == "assistant":
      for block in event["message"]["content"]:
        if block["type"] == "tool_use":
          assert block["name"] == "Read"
          child_reads.append(block["input"]["file_path"])
        if block["type"] == "text":
          answers.append(block["text"])
  assert answers[-1].strip() == "UNKNOWN"
  assert child_reads == [str(plugin / "agents/zoom_out.md")]
