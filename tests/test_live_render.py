"""Execute the REAL delegate renderer and assert what it emits.

Every other guard in this repo checks the description text, or compares it to a
captured render. Both can pass while the live pipeline emits something else --
they never run the renderer. This one does.

It locates an interpreter that can import ``amplifier_module_tool_delegate``
(this one, or the ``amplifier`` CLI's own), builds a DelegateTool over THIS
repo's agents, and reads its ``description`` property -- the same property the
runtime reads to put the catalog in the head of every request. The agent-row
join under test is the shipped code, not a copy of it.

If no such interpreter exists this test FAILS. It does not skip: a skip is a
vacuous pass, which is the failure mode the rest of this suite exists to catch.
Set AMPLIFIER_SKIP_LIVE_RENDER=1 to opt out deliberately and visibly.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
NAMESPACE = "stories"

# Runs under the chosen interpreter. Exercises the real property.
_RENDER = r"""
import json, pathlib, sys, types, yaml
from amplifier_module_tool_delegate import DelegateTool
repo = pathlib.Path(sys.argv[1])
agents = {}
for p in sorted((repo / "agents").glob("*.md")):
    t = p.read_text(); end = t.index("\n---\n", 3)
    m = yaml.safe_load(t[4:end])["meta"]
    agents[f"%s:{m['name']}"] = {"description": m["description"]}
tool = object.__new__(DelegateTool)
tool.coordinator = types.SimpleNamespace(config={"agents": agents})
tool.self_delegation_enabled = True
tool.config = {}
tool._feature_registry = []          # no features; the agent-row join is what is under test
rendered = tool.description          # THE REAL PROPERTY
rows = [l for l in rendered.split("\n") if l.startswith("  - %s:")]
print(json.dumps({"rows": rows}))
""" % (NAMESPACE, NAMESPACE)


def _candidate_interpreters() -> list[str]:
    cands = [sys.executable]
    amp = shutil.which("amplifier")
    if amp:
        for name in ("python", "python3"):
            p = pathlib.Path(amp).resolve().parent / name
            if p.exists():
                cands.append(str(p))
    return cands


def _live_rows() -> list[str]:
    errors = []
    for interp in _candidate_interpreters():
        proc = subprocess.run(
            [interp, "-c", _RENDER, str(REPO)], capture_output=True, text=True, timeout=120
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return json.loads(proc.stdout.strip().splitlines()[-1])["rows"]
        errors.append(f"{interp}: {(proc.stderr or proc.stdout).strip().splitlines()[-1:]}")
    pytest.fail(
        "could not execute the real delegate renderer under any interpreter -- "
        "this test asserts LIVE rendering and will not silently skip.\n"
        + "\n".join(f"  {e}" for e in errors)
        + "\nInstall the amplifier CLI, or set AMPLIFIER_SKIP_LIVE_RENDER=1 to opt out visibly."
    )


def _expected_rows() -> list[str]:
    rows = []
    for p in sorted((REPO / "agents").glob("*.md")):
        t = p.read_text(); end = t.index("\n---\n", 3)
        m = yaml.safe_load(t[4:end])["meta"]
        rows.append(f"  - {NAMESPACE}:{m['name']}: {m['description']}")
    assert rows, "no agents found -- glob matched nothing"
    return rows


pytestmark = pytest.mark.skipif(
    os.environ.get("AMPLIFIER_SKIP_LIVE_RENDER") == "1",
    reason="AMPLIFIER_SKIP_LIVE_RENDER=1 -- live-render assertions deliberately opted out",
)


def test_live_renderer_emits_a_row_for_every_agent() -> None:
    assert len(_live_rows()) == len(_expected_rows())


def test_live_rendered_rows_are_exactly_what_this_repo_declares() -> None:
    assert _live_rows() == _expected_rows()


def test_live_rendered_rows_meet_the_standard() -> None:
    for row in _live_rows():
        desc = row.split(": ", 1)[1]
        assert desc.startswith("USE WHEN"), f"not trigger-first as RENDERED: {row[:110]}"
        assert "DO NOT USE WHEN" in desc, f"no boundary clause as RENDERED: {row[:110]}"
        assert len(desc) <= 600, f"over budget as RENDERED ({len(desc)}): {row[:110]}"
        assert "<example>" not in desc and "<commentary>" not in desc


def test_live_rendered_slice_size_is_the_published_figure() -> None:
    """The number quoted in the DONE-NOTE, re-derived from a live render."""
    assert sum(len((r + "\n").encode()) for r in _live_rows()) == 4876
