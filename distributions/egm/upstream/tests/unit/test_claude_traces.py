# Copyright 2026 Google LLC.
# SPDX-License-Identifier: Apache-2.0

"""Offline regression coverage for Claude's native transcript directory."""

from pathlib import Path
import runpy

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("config_mode", ["unset", "default", "custom"])
def test_trace_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, config_mode: str
) -> None:
  trace_directory = runpy.run_path(str(ROOT / "tests/integration/test_claude.py"))[
      "trace_directory"
  ]
  monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "home"))
  config = tmp_path / "home" / ".claude"
  if config_mode == "unset":
    monkeypatch.delenv("CLAUDE_CONFIG_DIR", raising=False)
  else:
    if config_mode == "custom":
      config = tmp_path / "custom config"
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(config))

  assert trace_directory(Path("/work/egm probe.v1")) == (
      config / "projects" / "-work-egm-probe-v1"
  )
