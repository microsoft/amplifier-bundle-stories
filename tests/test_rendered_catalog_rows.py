"""Guard the property the catalog is paid for: what tool-delegate RENDERS.

The delegate agent catalog is rebuilt into the head of every request. This test
asserts against the RENDERED ROW -- the exact string tool-delegate emits -- not
against the source file, because the rendered row is what is actually paid for.

Renderer contract, mirrored from amplifier_module_tool_delegate/__init__.py:

    "\\n".join(f"  - {a['name']}: {a.get('description', 'No description')}"
               for a in agents_list)

Walks agents/ AS A SET with an empty-glob tripwire, so an agent added later is
caught. Per-file tests cannot do that.
"""

from __future__ import annotations

import pathlib

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
AGENTS_DIR = REPO / "agents"
NAMESPACE = "stories"

DESCRIPTION_BUDGET = 600
TRIGGER_FIRST_PREFIX = "USE WHEN"
BOUNDARY_CLAUSE = "DO NOT USE WHEN"
FORBIDDEN_TAGS = ("<example>", "</example>", "<commentary>", "</commentary>")


def _agent_files() -> list[pathlib.Path]:
    files = sorted(AGENTS_DIR.glob("*.md"))
    # Tripwire: an empty glob must fail loudly rather than vacuously pass.
    assert files, f"no agent definitions found under {AGENTS_DIR} -- glob matched nothing"
    return files


def _frontmatter(path: pathlib.Path) -> dict:
    text = path.read_text()
    assert text.startswith("---\n"), f"{path.name}: no YAML frontmatter"
    end = text.index("\n---\n", 3)
    return yaml.safe_load(text[4:end])


def _rendered_row(path: pathlib.Path) -> tuple[str, str]:
    """Return (rendered_catalog_row, description) exactly as tool-delegate emits it."""
    meta = _frontmatter(path).get("meta") or {}
    name = meta.get("name")
    assert name, f"{path.name}: frontmatter declares no meta.name"
    description = meta.get("description", "No description")
    return f"  - {NAMESPACE}:{name}: {description}", description


@pytest.mark.parametrize("path", _agent_files(), ids=lambda p: p.stem)
def test_rendered_row_is_trigger_first(path: pathlib.Path) -> None:
    row, description = _rendered_row(path)
    assert description.startswith(TRIGGER_FIRST_PREFIX), (
        f"{path.name}: the rendered catalog row must open with a TRIGGER, not a role noun.\n"
        f"  rendered: {row[:120]}..."
    )


@pytest.mark.parametrize("path", _agent_files(), ids=lambda p: p.stem)
def test_rendered_row_states_its_boundary(path: pathlib.Path) -> None:
    _, description = _rendered_row(path)
    assert BOUNDARY_CLAUSE in description, (
        f"{path.name}: no '{BOUNDARY_CLAUSE}' clause. In a bundle of adjacent content agents, "
        f"a row that never says when NOT to use it is a mis-route waiting to happen."
    )


@pytest.mark.parametrize("path", _agent_files(), ids=lambda p: p.stem)
def test_rendered_row_is_within_budget(path: pathlib.Path) -> None:
    _, description = _rendered_row(path)
    assert len(description) <= DESCRIPTION_BUDGET, (
        f"{path.name}: description is {len(description)} chars, over the "
        f"~{DESCRIPTION_BUDGET}-char catalog budget paid on every request."
    )


@pytest.mark.parametrize("path", _agent_files(), ids=lambda p: p.stem)
def test_rendered_row_carries_no_tutorial_markup(path: pathlib.Path) -> None:
    _, description = _rendered_row(path)
    found = [tag for tag in FORBIDDEN_TAGS if tag in description]
    assert not found, (
        f"{path.name}: description contains {found}. The catalog is a routing table, "
        f"not a tutorial, and it is paid for on every turn of every session."
    )


def test_whole_rendered_slice_is_accounted_for() -> None:
    """The set-level assertion: every agent contributes exactly one compliant row."""
    rows = [_rendered_row(p)[0] for p in _agent_files()]
    assert len({r.split(":", 2)[1] for r in rows}) == len(rows), "duplicate agent names in the rendered slice"
    slice_bytes = sum(len((r + "\n").encode()) for r in rows)
    assert slice_bytes > 0
    # Documented, not asserted as an exact value: this slice is what the bundle
    # costs in the head of every request. Recorded at 4,876 B on this branch.


# ---------------------------------------------------------------------------
# Anchor on REAL rendered output, not on the format string mirrored above.
#
# The assertions above reconstruct the row from a format string copied out of
# tool-delegate. That proves SCHEMA COMPLIANCE, not that the live pipeline emits
# these rows -- if the renderer changed, they would still pass.
#
# evidence/catalog-slice-after.txt is genuine output of the real pipeline
# (`amplifier tool info delegate -b <alias> --format json`, tool mount and all).
# Anchoring on it means the expected rows come from the renderer itself rather
# than from a transcription, and any description edited without re-rendering
# fails here.
#
# HONEST LIMIT, stated rather than skipped past: this repo's test environment
# cannot import amplifier_module_tool_delegate (its native deps are absent), so
# the renderer cannot be executed IN-PROCESS at test time. The capture below is
# the closest deterministic anchor. To re-execute the real pipeline:
#     docs/lanes/kp79-catalog-stories/evidence/render-catalog.sh <out>
# ---------------------------------------------------------------------------

CAPTURE = REPO / "docs/lanes/kp79-catalog-stories/evidence/catalog-slice-after.txt"


def _captured_rows() -> dict[str, str]:
    assert CAPTURE.exists(), f"real-render capture missing at {CAPTURE}"
    rows: dict[str, str] = {}
    for line in CAPTURE.read_text().splitlines():
        if not line.startswith(f"  - {NAMESPACE}:"):
            continue
        name = line[len(f"  - {NAMESPACE}:") :].split(":", 1)[0]
        rows[name] = line
    assert rows, f"{CAPTURE.name} contained no {NAMESPACE}: rows -- capture is empty or malformed"
    return rows


def test_every_agent_appears_in_the_real_render_capture() -> None:
    captured = _captured_rows()
    live = {_frontmatter(p)["meta"]["name"] for p in _agent_files()}
    assert live == set(captured), (
        "the set of agents differs from the real-render capture.\n"
        f"  only in repo:    {sorted(live - set(captured))}\n"
        f"  only in capture: {sorted(set(captured) - live)}\n"
        "Re-run evidence/render-catalog.sh and refresh the capture."
    )


@pytest.mark.parametrize("path", _agent_files(), ids=lambda p: p.stem)
def test_rendered_row_matches_the_real_render_byte_for_byte(path: pathlib.Path) -> None:
    row, _ = _rendered_row(path)
    name = _frontmatter(path)["meta"]["name"]
    captured = _captured_rows()[name]
    assert row == captured, (
        f"{path.name}: the row this repo would render no longer matches the real pipeline capture.\n"
        f"  repo:    {row[:160]}\n"
        f"  capture: {captured[:160]}\n"
        "Either the description changed without re-rendering, or the renderer's format changed."
    )
