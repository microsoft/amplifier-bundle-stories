# Amplifier Stories Recipes

This directory contains automated workflows (recipes) for generating content from Amplifier data.

## Available Recipes

### session-to-case-study

Convert completed Amplifier session files into compelling case studies in Word format.

**Purpose:** Automatically analyze session data and generate professional case study documents that tell the story of how problems were solved using Amplifier.

**Workflow:**
1. **Research Phase** - Analyzes events.jsonl to extract:
   - Session metadata (duration, agents, tools, iterations)
   - Key breakthrough moments
   - Quantified metrics (tool calls, files modified, complexity indicators)
   - Final outcome and deliverables

2. **Strategy Phase** - Evaluates case study worthiness:
   - Requires 10+ tool calls for substantive work
   - Must have successful outcome
   - Should have interesting problem-solving narrative
   - Determines target audience (technical/mixed/community)

3. **Writing Phase** - Generates Word document using template:
   - Creates engaging title
   - Writes Challenge/Approach/Results sections
   - Includes quantified metrics throughout
   - Adds actionable key takeaways

4. **Finalization** - Auto-opens document for review

**Usage:**

```bash
# Basic usage with session file
amplifier run "execute session-to-case-study.yaml with session_file=~/.amplifier/sessions/2026-01-15/events.jsonl"

# With custom output name
amplifier run "execute session-to-case-study.yaml with session_file=./my-session.jsonl output_name=automation-success-story"

# From recent session (relative path)
amplifier run "execute session-to-case-study.yaml with session_file=../sessions/recent/events.jsonl"
```

**Inputs:**
- `session_file` (required): Path to events.jsonl session file
- `output_name` (optional): Custom filename for output (defaults to session ID)

**Outputs:**
- Word document at `workspace/docx/output/case-study-[name].docx`
- Auto-opened in Microsoft Word for immediate review

**Requirements:**
- Agents: `story-researcher`, `content-strategist`, `case-study-writer`
- Template: `workspace/docx/templates/case-study-template.js`
- Node.js with `docx` package installed

**Success Criteria:**
- Clear narrative structure (Challenge → Approach → Results)
- Metrics quantified from actual session data
- Technical accuracy maintained
- Compelling story, not just data dump
- Actionable takeaways for readers

**Not Case-Study Worthy?**
The recipe will analyze and report if a session doesn't meet criteria:
- Too few tool calls (<10)
- Failed or abandoned session
- Routine/trivial problem
- Unclear narrative potential

In these cases, you'll get a report explaining why and what would make it case-study material.

---

### weekly-digest

Generate comprehensive weekly digests of Amplifier ecosystem activity including commits, PRs, releases, community highlights, and key metrics.

**Purpose:** Automatically generate engaging weekly digests for maintaining regular communication with the Amplifier community and keeping stakeholders informed of ecosystem progress.

**Workflow:**
1. **Git Activity Scan** - Analyzes repository activity:
   - Scans all ecosystem repos for commits over date range
   - Extracts merged PRs with descriptions
   - Identifies new releases/tags
   - Calculates velocity metrics (commits, contributors, PRs)

2. **Session Analysis** (Optional) - Examines usage patterns:
   - Analyzes session files if enabled
   - Extracts tool and agent usage patterns
   - Calculates engagement metrics
   - Identifies interesting sessions for case studies
   - Privacy-focused with aggregate data only

3. **Community Highlights** - Discovers community engagement:
   - Finds external contributions and repos
   - Identifies notable GitHub discussions/issues
   - Discovers new contributors
   - Searches for blog posts and social media mentions

4. **Content Strategy** - Plans the digest:
   - Identifies top 3-5 stories to highlight
   - Determines digest structure and sections
   - Sets audience focus and tone
   - Prioritizes content by impact

5. **Digest Writing** - Generates all content:
   - Full blog post (800-1200 words, Markdown)
   - Email version (condensed, 400-600 words)
   - Social media snippets (Twitter/X, LinkedIn, Mastodon)
   - Celebrates contributors and links to resources

6. **Distribution Prep** - Prepares for publishing:
   - Saves to workspace/blog/ and docs/blog/
   - Auto-opens for review
   - Provides distribution checklist

**Usage:**

```bash
# Standard weekly digest (last 7 days)
amplifier tool invoke recipes operation=execute recipe_path=./recipes/weekly-digest.yaml

# Custom date range
amplifier tool invoke recipes operation=execute recipe_path=./recipes/weekly-digest.yaml \
  context='{"date_range": "last 14 days"}'

# With session analysis (opt-in for privacy)
amplifier tool invoke recipes operation=execute recipe_path=./recipes/weekly-digest.yaml \
  context='{"include_sessions": true}'

# Specific repos only
amplifier tool invoke recipes operation=execute recipe_path=./recipes/weekly-digest.yaml \
  context='{"repos": "amplifier-core,amplifier-cli,amplifier-docs"}'
```

**Inputs:**
- `date_range` (optional): Time range for scan, default "last 7 days" (e.g., "last 14 days", "since 2026-01-11")
- `repos` (optional): Comma-separated list of repos to scan (defaults to all from MODULES.md)
- `include_sessions` (optional): Whether to analyze session data, default false (privacy consideration)

**Outputs:**
- Blog post at `workspace/blog/weekly-digest-YYYY-MM-DD.md`
- Contains all three formats in one file:
  - Full blog post with sections (Highlights, New Features, Community, Stats, What's Next)
  - Email version for newsletters
  - Social media snippets for Twitter/X, LinkedIn, Mastodon
- Copy in `docs/blog/` for GitHub Pages (if docs directory exists)
- Auto-opened in editor for review

**Requirements:**
- Agents: `story-researcher`, `data-analyst`, `community-manager`, `content-strategist`, `marketing-writer`
- Git access to ecosystem repositories
- Optional: GitHub CLI (`gh`) for enhanced PR/issue data
- Optional: Web search for community mentions

**Automation:**
Can be scheduled to run automatically every Monday:

**Cron (Linux/Mac):**
```bash
# Add to crontab (crontab -e):
0 9 * * 1 cd /path/to/amplifier && amplifier tool invoke recipes operation=execute recipe_path=./recipes/weekly-digest.yaml
```

**GitHub Actions:**
```yaml
name: Weekly Digest
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  digest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Generate Digest
        run: amplifier tool invoke recipes operation=execute recipe_path=./recipes/weekly-digest.yaml
```

**Success Criteria:**
- Digest covers all major ecosystem activity
- Top stories featured prominently
- Stats are accurate and sourced
- Tone is engaging and community-friendly
- Multiple formats ready for different channels
- Ready to publish with minimal editing

**Privacy Considerations:**
- Session analysis is opt-in via `include_sessions` flag
- Always review digest before publishing
- No sensitive data should be included in public digests
- Consider separate internal vs. public digests for sensitive projects

---

### git-tag-to-changelog

Generate complete release documentation from git tags including changelog, release notes, and migration guides.

**Purpose:** Automatically generate comprehensive release documentation when a git tag is created, including CHANGELOG.md entries, GitHub release notes, migration guides for breaking changes, blog post announcements, and social media content.

**Requirements:**
- Agents: `zen-architect`, `explorer`, `integration-specialist`
- Git CLI
- GitHub CLI (`gh`) for PR creation
- Repository must use semantic versioning (vX.Y.Z)
- Repository should follow conventional commits for best results

For full details, see the recipe file at `./recipes/git-tag-to-changelog.yaml`.

---

## Creating New Recipes

To create a new recipe in this collection:

1. Create a `.yaml` file in this directory
2. Follow the recipe format (see examples in `@recipes:examples/`)
3. Validate with: `amplifier recipes validate your-recipe.yaml`
4. Document it in this README
5. Test thoroughly before committing

## Recipe Format Reference

Key components:
- `name`: Unique identifier
- `description`: What the recipe does
- `context`: Input variables
- `steps`: Sequential workflow with agents or bash commands
- `condition`: Optional step execution logic
- `output`: Variable capture for next steps

### Safe data in bash steps

Treat repository paths, refs, session data, and generated content as untrusted.
Never place a `{{context_value}}` directly in `command:`: recipe substitution
happens before bash parses the command, so shell quoting or a quoted heredoc in
the template does not make arbitrary substituted bytes safe.

Use the runner's `env:` boundary instead:

```yaml
- id: save-content
  type: bash
  env:
    OUTPUT_PATH: "{{output_path}}"
    CONTENT: "{{generated_content}}"
  command: |
    set -euo pipefail
    mkdir -p -- "$(dirname -- "$OUTPUT_PATH")"
    printf '%s\n' "$CONTENT" > "$OUTPUT_PATH"
```

The runner resolves each `env:` value and passes it directly to the process
environment; it is not parsed as shell source. Inside the command:

- quote every expansion (`"$OUTPUT_PATH"`, not `$OUTPUT_PATH`);
- use `--` before path arguments where the command supports it;
- never use `eval`, `sh -c`, or `bash -c` with an environment value;
- produce JSON with `jq` or static Python via `"$AMPLIFIER_PYTHON"`, not string
  concatenation in `echo`;
- for content too large for the platform's process environment, write it in an
  earlier step and pass only the file path through `env:`.

`tests/test_recipe_shell_inputs.py` enforces this boundary for every shipped
bash step.

See the Amplifier recipes documentation for full specification.
