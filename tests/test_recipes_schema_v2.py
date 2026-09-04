"""Lint: every shipped recipe that references an agent must declare schema_version 2.

Why this exists
---------------
A recipe without ``schema_version: 2`` resolves its ``agent:`` references from
the *calling session's* agent map. That makes it silently caller-bound: it works
when run from a session that already carries ``stories:``/``foundation:``
agents, and fails with "not found in configuration" from any other bundle.

``schema_version: 2`` plus a ``dependencies:`` block flips that to a closed
world -- agents resolve only from the recipe's own declared closure, so the
recipe runs from ANY session bundle.

This test fails loud if a new (or edited) recipe reintroduces the caller-bound
shape. It is a structural lint only: it never clones a source or contacts the
network. Full dependency resolution is the runner's job::

    python -m amplifier_recipe_runner validate recipes/<file>.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
RECIPES_DIR = REPO_ROOT / "recipes"

# Recipes deliberately left on the legacy (schema_version 1) shape, each with a
# reason. Keep this EMPTY unless a recipe genuinely cannot be made v2-safe.
#
# The known legitimate case is a recipe using ``agent: self``: a self-reference
# names the calling session's own agent, which by definition has no declaring
# bundle, so it cannot be expressed in a closed-world dependency manifest.
EXEMPT: dict[str, str] = {
    # "recipes/example.yaml": "uses `agent: self`, which cannot be declared in a
    #                          dependency closure -- see bundle-recipes recipes-80q",
}


def _recipe_files() -> list[Path]:
    return sorted(RECIPES_DIR.rglob("*.yaml")) + sorted(RECIPES_DIR.rglob("*.yml"))


def _agent_refs(node: Any, found: list[str]) -> None:
    """Collect every ``agent:`` value anywhere in the document.

    Walks the whole tree rather than just ``steps``: staged recipes nest their
    steps under ``stages``, and a check that only knew about flat ``steps``
    would pass a staged recipe with zero coverage.
    """
    if isinstance(node, dict):
        agent = node.get("agent")
        if isinstance(agent, str) and agent.strip():
            found.append(agent.strip())
        for value in node.values():
            _agent_refs(value, found)
    elif isinstance(node, list):
        for item in node:
            _agent_refs(item, found)


def _declared_agents(doc: dict[str, Any]) -> list[str]:
    declared: list[str] = []
    for dep in doc.get("dependencies") or []:
        if isinstance(dep, dict):
            declared.extend(str(a) for a in (dep.get("required_agents") or []))
    return declared


@pytest.mark.parametrize("path", _recipe_files(), ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_agent_referencing_recipe_declares_schema_v2(path: Path) -> None:
    rel = str(path.relative_to(REPO_ROOT))
    doc = yaml.safe_load(path.read_text()) or {}
    if not isinstance(doc, dict):
        pytest.skip(f"{rel} is not a mapping document")

    refs: list[str] = []
    _agent_refs(doc, refs)
    if not refs:
        pytest.skip(f"{rel} references no agents")

    if rel in EXEMPT:
        pytest.skip(f"{rel} exempt: {EXEMPT[rel]}")

    assert doc.get("schema_version") == 2, (
        f"{rel} references agents {sorted(set(refs))} but does not declare "
        f"`schema_version: 2`. Without it the recipe resolves agents from the "
        f"CALLING session and cannot run from a bundle that lacks them. Add a "
        f"`schema_version: 2` + `dependencies:` manifest, or add {rel} to "
        f"EXEMPT in this file with a reason."
    )

    deps = doc.get("dependencies")
    assert isinstance(deps, list) and deps, (
        f"{rel} declares `schema_version: 2` but has no `dependencies:` list. "
        f"A closed-world recipe with an empty closure can never resolve "
        f"{sorted(set(refs))}."
    )
    for dep in deps:
        assert isinstance(dep, dict) and dep.get("source"), f"{rel} has a dependency entry with no `source`"


@pytest.mark.parametrize("path", _recipe_files(), ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_every_agent_reference_is_declared(path: Path) -> None:
    """Each referenced agent appears in some dependency's ``required_agents``.

    Catches the drift case: a step added later that references an agent nobody
    remembered to declare. Bare references (``story-researcher``) are matched
    against the bare tail of each declared name (``stories:story-researcher``),
    which is how the runner's planner resolves them.
    """
    rel = str(path.relative_to(REPO_ROOT))
    doc = yaml.safe_load(path.read_text()) or {}
    if not isinstance(doc, dict) or doc.get("schema_version") != 2:
        pytest.skip(f"{rel} is not a schema_version 2 recipe")

    refs: list[str] = []
    _agent_refs(doc, refs)
    declared = _declared_agents(doc)
    declared_bare = {d.split(":", 1)[-1] for d in declared}

    for ref in sorted(set(refs)):
        covered = ref in declared or (":" not in ref and ref in declared_bare)
        assert covered, (
            f"{rel} references agent {ref!r}, which no declared dependency lists "
            f"under `required_agents` (declared: {sorted(set(declared))}). "
            f"Add it, or add the dependency that supplies it."
        )
