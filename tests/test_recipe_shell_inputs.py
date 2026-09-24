"""Keep untrusted recipe data out of rendered bash source."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
RECIPES_DIR = REPO_ROOT / "recipes"
VALUE_TEMPLATE = re.compile(r"\A\{\{\s*\w+(?:\.\w+)*\s*\}\}\Z")
ENV_NAME = re.compile(r"\A[A-Z_][A-Z0-9_]*\Z")


def _recipe_files() -> list[Path]:
    return sorted(RECIPES_DIR.rglob("*.yaml")) + sorted(RECIPES_DIR.rglob("*.yml"))


def _steps(node: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(node, dict):
        if "id" in node and ("type" in node or "agent" in node):
            found.append(node)
        for value in node.values():
            found.extend(_steps(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(_steps(item))
    return found


@pytest.mark.parametrize("path", _recipe_files(), ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_bash_commands_do_not_render_context_values(path: Path) -> None:
    """Values belong in ``env:``, never in the string parsed by bash."""
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    for step in _steps(doc):
        if step.get("type") != "bash":
            continue
        command = step.get("command", "")
        assert "{{" not in command, (
            f"{path.name}:{step.get('id')} renders a context value directly into "
            "bash source. Put the template in the step's `env:` mapping and use "
            "a quoted shell expansion instead."
        )


@pytest.mark.parametrize("path", _recipe_files(), ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_bash_env_templates_are_value_only(path: Path) -> None:
    """An env entry must resolve one value, not construct shell syntax."""
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    for step in _steps(doc):
        if step.get("type") != "bash":
            continue
        env = step.get("env") or {}
        assert isinstance(env, dict), f"{path.name}:{step.get('id')} has a non-mapping `env:`"
        for name, value in env.items():
            assert isinstance(name, str) and ENV_NAME.fullmatch(name), (
                f"{path.name}:{step.get('id')} has unsafe env name {name!r}; "
                "use an uppercase shell identifier"
            )
            assert isinstance(value, str) and VALUE_TEMPLATE.fullmatch(value), (
                f"{path.name}:{step.get('id')} env {name} must be exactly one "
                "`{{value}}` or `{{value.path}}` template"
            )
