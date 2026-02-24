# Stories Bundle Backport Design

## Goal
Backport improvements from ramparte/amplifier-stories (v2.0.0) into microsoft/amplifier-bundle-stories (v1.0.0) to incorporate substantial improvements made since the original Microsoft clean-up.

## Background
The microsoft/amplifier-bundle-stories was originally based on the ramparte/amplifier-stories version but was cleaned up into a proper Microsoft-ready bundle. Since then, ramparte has made substantial improvements worth incorporating, including enhanced agent descriptions with parameter specs, accessibility/WCAG compliance, source verification safeguards, quality gates, and production tooling improvements.

## Approach
**Approach A: Surgical copy-and-adapt** - For each improved file, take the ramparte version, adapt namespace references (`@amplifier-module-stories:` → `@stories:`), and replace the microsoft version. Preserve emojis as-is (intentional by author). Skip ramparte's project management artifacts to maintain Microsoft's clean bundle structure.

## Architecture

### Source and Target Repositories
- **Source**: ramparte/amplifier-stories (v2.0.0) at `/home/bkrabach/dev/update-stories-bundle/amplifier-stories`
- **Target**: microsoft/amplifier-bundle-stories (v1.0.0) at `/home/bkrabach/dev/update-stories-bundle/amplifier-bundle-stories`

### File Categories
1. **Agents** (11 files) - Core bundle functionality with enhanced descriptions
2. **Context files** (2 files) - Supporting instruction and style configurations
3. **Tools** (3 files) - Python utilities for presentation generation and verification
4. **Preserved files** - Bundle metadata, behaviors, recipes, templates, governance

## Components

### Agents (11 files — all updated)
Take each agent from ramparte, adapt namespace references:
- `agents/case-study-writer.md`
- `agents/community-manager.md`
- `agents/content-adapter.md`
- `agents/content-strategist.md`
- `agents/data-analyst.md`
- `agents/executive-briefer.md`
- `agents/marketing-writer.md`
- `agents/release-manager.md`
- `agents/story-researcher.md`
- `agents/storyteller.md`
- `agents/technical-writer.md`

**Key changes**: Enhanced descriptions with `PASS IN:` parameter specs, `<example>` blocks with usage commentary, corrected namespace references (`@stories:` not `@amplifier-module-stories:`).

### Context Files (2 files updated)
- `context/storyteller-instructions.md` — add source verification safeguards, quality gates, antagonistic review checklist
- `context/presentation-styles.md` — add WCAG AA compliance, CSS custom properties, projector-readable sizing

### Tools (1 replaced, 2 added)
- `tools/html2pptx.py` — **REPLACED** with ramparte's `html2pptx_v2.py` (renamed to `html2pptx.py`)
- `tools/pptx_verify.py` — **NEW**, quality verification tool
- `tools/deck-style-fix.py` — **NEW**, CSS cleanup tool

### Preserved Components
- `bundle.md` — keep Microsoft's thin bundle pattern
- `behaviors/stories.yaml` — keep Microsoft's behavior config
- `recipes/*.yaml` — no changes needed
- `workspace/` templates — no changes
- Governance files (LICENSE, SECURITY.md, SUPPORT.md, CODE_OF_CONDUCT.md) — untouched

### Skipped Components (ramparte project management artifacts)
- ACTIVATION.md, SCRATCH.md, FUTURE_TOPICS.md, IMPLEMENTATION_LOG.md
- staging/ directory
- deploy.sh (SharePoint deployment)
- .env.local.example
- AGENTS.md
- docs/ directory with 80+ generated decks
- .github/workflows/

## Data Flow

### Adaptation Process
1. **Context files first** → Update `storyteller-instructions.md` and `presentation-styles.md` (referenced by agents, must be correct first)
2. **All 11 agents** → Take ramparte versions, fix namespace, replace microsoft versions
3. **Tools** → Replace `html2pptx.py` with v2, add `pptx_verify.py` and `deck-style-fix.py`, fix namespace references in Python code
4. **Validation** → Run bundle validation and agent validation recipes against the updated repo
5. **Fix** → Address any validation issues
6. **Commit** → Single commit describing the backport

### Adaptation Rules
1. **Namespace references**: `@amplifier-module-stories:` → `@stories:` (all context/agent cross-references)
2. **Emojis**: Preserve as-is from ramparte's files (intentional usage by author)
3. **Bundle metadata**: Agent frontmatter `meta:` blocks keep same name values (match `behaviors/stories.yaml`), update description content
4. **Tool files**: `html2pptx_v2.py` renamed to `html2pptx.py` (replacing existing), new tools added with namespace fixes, any internal references to `amplifier-module-stories` in Python code updated

## Error Handling

### Validation Strategy
After all changes applied:
1. **Bundle validation recipe** — verify bundle loads, agent references resolve, context file paths valid
2. **Agent validation recipe** — verify descriptions parse, example blocks well-formed, cross-references resolve
3. **Fix any issues found** — namespace typos, broken references, etc.

### Risk Mitigation
- Update context files before agents to avoid broken references
- Preserve Microsoft's bundle structure and governance files
- Skip ramparte project artifacts that don't fit Microsoft bundle pattern
- Run comprehensive validation before completion

## Testing Strategy

### Key Improvements Being Backported

#### Tier 1: Critical
1. **Enhanced agent descriptions** — `PASS IN` parameter specs, example blocks making agents usable by end users
2. **Accessibility/WCAG compliance** — CSS custom properties, contrast ratios, projector-readable sizing
3. **Source verification safeguards** — anti-hallucination rules preventing confusion between microsoft/amplifier* and anthropics/amplifier*
4. **Quality gates** — antagonistic review checklists requiring evidence for every metric
5. **Production tooling** — html2pptx_v2 with multi-row grids, per-character width estimation, 15+ CSS class handlers, code syntax highlighting; pptx_verify for quality verification; deck-style-fix for CSS cleanup

### Validation Tests
- Bundle loads correctly without errors
- All agent references resolve to valid context files
- Cross-references between agents work properly
- Tool namespace references updated correctly
- Python tools function with new paths

## Open Questions

None — design is complete and validated. All implementation details have been specified and approved.