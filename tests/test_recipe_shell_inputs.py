"""Keep untrusted recipe data out of rendered bash source."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
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
        assert "{{" not in command and "{%" not in command, (
            f"{path.name}:{step.get('id')} renders a template directly into bash "
            "source. Put values in the step's `env:` mapping and express control "
            "flow as quoted shell tests instead."
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


def _bash_step(recipe_name: str, step_id: str) -> dict[str, Any]:
    document = yaml.safe_load((RECIPES_DIR / recipe_name).read_text(encoding="utf-8"))
    matches = [step for step in _steps(document) if step.get("id") == step_id]
    assert len(matches) == 1, f"expected one {step_id!r} step in {recipe_name}"
    return matches[0]


def _render_env(env: dict[str, str], context: dict[str, Any]) -> dict[str, str]:
    """Render the runner-supported whole-value templates used by bash env maps."""
    rendered: dict[str, str] = {}
    for name, template in env.items():
        match = VALUE_TEMPLATE.fullmatch(template)
        assert match, f"{name} is not a whole-value template: {template!r}"
        value: Any = context
        for part in template[2:-2].strip().split("."):
            value = value[part]
        rendered[name] = "true" if value is True else "false" if value is False else str(value)
    return rendered


def _run_bash_step(step: dict[str, Any], context: dict[str, Any], cwd: Path) -> subprocess.CompletedProcess[str]:
    """Execute the exact bash source after the runner's env-only rendering boundary."""
    command = step["command"]
    assert "{{" not in command and "{%" not in command
    env = os.environ | {
        "AMPLIFIER_PYTHON": sys.executable,
        **_render_env(step["env"], context),
    }
    return subprocess.run(
        ["bash", "-c", command],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.mark.parametrize("include_appendix", [False, True])
def test_blog_save_and_finalize_use_shell_boolean_for_appendix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, include_appendix: bool
) -> None:
    """The two real steps run without unsupported Jinja control flow."""
    save_step = _bash_step("blog-post-generator.yaml", "save-files")
    output_dir = tmp_path / "blog" / "posts"
    appendix = tmp_path / "technical.md"
    appendix.write_text("technical details", encoding="utf-8")
    context = {
        "feature_name": "Safe recipe rendering",
        "output_dir": str(output_dir),
        "blog_post": "# Safe recipe rendering",
        "social_media": "Post about safe recipe rendering",
        "technical_appendix_path": str(appendix),
        "include_technical_appendix": include_appendix,
    }

    saved = _run_bash_step(save_step, context, tmp_path)
    assert saved.returncode == 0, saved.stderr
    file_paths = json.loads(saved.stdout.splitlines()[-1])
    assert Path(file_paths["blog_file"]).read_text(encoding="utf-8") == "# Safe recipe rendering\n"
    assert Path(file_paths["social_file"]).read_text(encoding="utf-8") == "Post about safe recipe rendering\n"
    assert ("Technical appendix:" in saved.stdout) is include_appendix

    tools = tmp_path / "tools"
    tools.mkdir()
    for name in ("open", "xdg-open", "start"):
        tool = tools / name
        tool.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        tool.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tools}{os.pathsep}{os.environ['PATH']}")
    finalize = _run_bash_step(
        _bash_step("blog-post-generator.yaml", "finalize"),
        {
            "file_paths": file_paths,
            "technical_appendix_path": str(appendix),
            "include_technical_appendix": include_appendix,
        },
        tmp_path,
    )
    assert finalize.returncode == 0, finalize.stderr
    assert ("Technical:" in finalize.stdout) is include_appendix


@pytest.mark.parametrize("optional_outputs", [False, True])
def test_changelog_save_files_uses_shell_booleans_for_optional_outputs(
    tmp_path: Path, optional_outputs: bool
) -> None:
    """The real save step writes optional outputs only when runner booleans are true."""
    output_dir = tmp_path / "release"
    result = _run_bash_step(
        _bash_step("git-tag-to-changelog.yaml", "save-files"),
        {
            "output_dir": str(output_dir),
            "tag_info": {
                "tag_name": "v1.2.3",
                "current_version": "1.2.3",
                "previous_version": "1.2.2",
                "release_type": "minor",
            },
            "changelog_entry": "Changelog entry",
            "release_notes": "Release notes",
            "migration_guide": "Migration guide",
            "blog_post": "Blog post",
            "social_media": {"twitter": "tweet", "linkedin": "post", "mastodon": "toot"},
            "commit_history": {"commit_count": 3, "contributor_count": 2},
            "commit_analysis": {
                "statistics": {"breaking_count": 1, "has_breaking_changes": optional_outputs}
            },
            "include_blog_post": optional_outputs,
            "include_social_media": optional_outputs,
        },
        tmp_path,
    )
    assert result.returncode == 0, result.stderr
    assert (output_dir / "CHANGELOG-v1.2.3.md").is_file()
    assert (output_dir / "RELEASE-NOTES-v1.2.3.md").is_file()
    optional_files = (
        output_dir / "MIGRATION-v1.2.3.md",
        output_dir / "BLOG-POST-v1.2.3.md",
        output_dir / "social" / "twitter.txt",
        output_dir / "social" / "linkedin.txt",
        output_dir / "social" / "mastodon.txt",
    )
    assert all(path.is_file() for path in optional_files) is optional_outputs
