# Storyteller Agent Quickstart

Create polished presentations and documents showcasing your work.

## Invoke the Agent

Use the `@stories:storyteller` agent when you need presentations or visual documentation:

```
@stories:storyteller Create a presentation about [your topic]
```

Or ask Claude to delegate:

```
Create a deck showing our new authentication feature
```

Claude will automatically route to storyteller when it detects presentation-related requests.

## What It Produces

| Format | Best For | Output Location |
|--------|----------|-----------------|
| **HTML** (default) | Quick sharing, GitHub Pages | `docs/*.html` |
| **PowerPoint** | Executive presentations, offline use | `docs/*.pptx` |
| **Word** | Technical documentation, proposals | `docs/*.docx` |
| **Excel** | Metrics dashboards, data analysis | `docs/*.xlsx` |
| **PDF** | Final deliverables, archival | `docs/*.pdf` |
| **Video** | Social sharing, loops | `docs/*.mp4` |

## Example Prompts

**Feature showcase:**
```
@stories:storyteller Create a presentation about the caching feature we built last sprint
```

**Team demo:**
```
@stories:storyteller I need to demo Amplifier to new team members - create an overview deck
```

**Metrics report:**
```
@stories:storyteller Build an Excel dashboard showing our test coverage improvements
```

**Technical doc:**
```
@stories:storyteller Write a Word document explaining our API architecture
```

**Video presentation:**
```
@stories:storyteller Create a video presentation about our new mobile app launch
```

## Workflow

1. **Request** - Describe what you want to present
2. **Research** - Agent gathers context from repos, PRs, conversations
3. **Create** - Generates the presentation in your chosen format
4. **Review** - Auto-opens the file for your review
5. **Deploy** - Say "deploy" or "ship it" to commit and push

## Deck Structure

Every presentation follows this narrative arc:

1. **Title** - Feature name + one-line description
2. **Problem** - What pain point does this solve?
3. **Solution** - How it works (with examples)
4. **Impact** - Metrics, before/after comparisons
5. **Velocity** - Development effort and timeline
6. **CTA** - Where to learn more

## Tips

- **Be specific** about your audience (technical team vs executives)
- **Mention key points** you want emphasized
- **Reference context** - PRs, repos, or sessions the agent should research
- **Request a format** explicitly if you don't want HTML
- **Optional QA:** Add "with QA" or "run QA" to your request to get a Playwright screenshot pass (overflow, SVG overlaps, emoji rendering, scaling). (Playwright may be installed if needed.)

## Quick Reference

```bash
# Typical invocation
@stories:storyteller Create a presentation about [topic] for [audience]

# With format
@stories:storyteller Create a PowerPoint about our Q4 achievements

# With context
@stories:storyteller Build a deck about PR #123 - the new search feature
```

---

*Part of the [amplifier-bundle-stories](https://github.com/anthropics/amplifier-bundle-stories) bundle.*
