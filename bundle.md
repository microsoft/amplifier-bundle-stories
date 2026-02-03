---
bundle:
  name: stories
  version: 1.0.0
  description: Autonomous storytelling engine - create presentations, documents, and content across formats and audiences

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: stories:behaviors/stories
---

# Storyteller Bundle

**Autonomous storytelling engine for any project.**

Create professional presentations, documents, and content across multiple formats and audiences.

## What This Bundle Provides

### Content Formats (5)
- **HTML** - "Useful Apple Keynote" style presentations
- **PowerPoint** - Professional .pptx with corporate styling
- **Excel** - Data dashboards, metrics tracking, comparisons
- **Word** - Technical docs, proposals, case studies
- **PDF** - Executive one-pagers and summaries

### Specialist Agents (11)
- **storyteller** - Primary agent for creating presentations
- **story-researcher** - Automated data gathering
- **content-strategist** - Story selection and planning
- **technical-writer** - Deep technical documentation
- **marketing-writer** - Community and public communication
- **executive-briefer** - High-level summaries
- **release-manager** - Automated release documentation
- **case-study-writer** - Narrative case studies
- **data-analyst** - Data transformation and visualization
- **content-adapter** - Format and audience transformation
- **community-manager** - Community engagement content

### Automated Workflows (4 Recipes)
- **session-to-case-study** - Turn sessions into shareable content
- **git-tag-to-changelog** - Generate release notes automatically
- **weekly-digest** - Regular project updates
- **blog-post-generator** - Feature stories from git data

## Quick Start

```
"Create a PowerPoint about [feature]"
"Make an Excel dashboard showing [metrics]"
"Write a case study about [project]"
```

## Automated Workflows

Run recipes for automated content generation:

```
"Run the weekly digest recipe"
"Generate a case study from this session"
"Create release notes for the v2.0 tag"
```

---

@foundation:context/shared/common-system-base.md
