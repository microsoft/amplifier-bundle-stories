# Finding — no agent in this repo declares `tools:` (0 of 12)

Discovered by `validate-agents` v1.7.0 during lane `kp79-catalog-stories`.
**Not fixed in that lane** — it is a functional change, not a catalog change. This file is the spec for whoever picks it up.

## Ground truth

```
grep -n "^ *tools:" agents/*.md   -> (none)
behaviors/stories.yaml            -> `agents: include:` only, no tools:
bundle.md                         -> includes foundation + behaviors, no tools:
```

Tools are declared **nowhere**. All 12 agents inherit whatever the composing bundle mounts.

| Bundle | Agents | Explicit `tools:` |
|---|---|---|
| amplifier-foundation@main | 16 | **16 / 16 (100%)** |
| amplifier-bundle-stories | 12 | **0 / 12 (0%)** |

Severity, stated honestly: `NO_TOOLS_SECTION` is **WARNING**-level. `validate-agents` reports **0 errors** on this repo, before and after the description work. The repo is not failing.

## Why it matters

`story-researcher` is the sharpest case. Its entire contract is shell — `git log`, `gh repo view`, `gh pr list`, `gh search commits`, `grep -E`, `tools/analyze_sessions.py` — and **three of the four recipes in `recipes/` delegate to it at step one**. Composed into any session that does not mount `tool-bash`, its job silently becomes impossible and those recipes fail immediately.

## Why it must NOT be bundled into a description PR

1. An explicit `tools:` list **narrows** the inherited set. An incomplete list silently disables an agent at runtime with no compile-time signal — reintroducing the exact failure the warning exists to prevent.
2. It cannot be verified at $0. A wrong `source:` URL breaks agent loading for the whole bundle; validating 12 new module mounts needs a real load.
3. It contaminates the control. The description PR's evidence is a before/after catalog render in which every other bundle moves exactly 0 bytes and the diff has exactly one hunk. Two entangled changes destroy that.

## Remediation — three profiles, not twelve bespoke lists

`tools:` is **top-level in frontmatter, a sibling of `meta:`** — not nested under it.

**P1 — filesystem only** (`content-strategist`; pure planning, zero tool evidence in its body — `tools: []` is also a legitimate owner call here)

```yaml
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
```

**P2 — filesystem + bash** (`case-study-writer`, `community-manager`, `content-adapter`, `data-analyst`, `executive-briefer`, `marketing-writer`, `release-manager`, `storyteller`, `technical-writer`)

```yaml
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
```

**P3 — filesystem + bash + search** (`story-researcher`, `evaluation-visualizer`)

```yaml
tools:
  - module: tool-filesystem
    source: git+https://github.com/microsoft/amplifier-module-tool-filesystem@main
  - module: tool-bash
    source: git+https://github.com/microsoft/amplifier-module-tool-bash@main
  - module: tool-search
    source: git+https://github.com/microsoft/amplifier-module-tool-search@main
```

Deliberately **not** prescribed: `tool-web` (no agent shows web-search evidence — `gh api` is bash, not web), `tool-lsp` (no code navigation anywhere), and any `delegate` module (foundation declares none; delegation is session-level, not a mounted tool).

## Success criteria

- Each declared list verified by **one live invocation**, not by inspection.
- `validate-agents` moves **12 warnings → 0**, errors still **0**.
- Descriptions stay **byte-identical** — `kp79`'s change must not be re-litigated.
