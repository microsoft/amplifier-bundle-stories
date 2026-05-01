# Amplifier Bundle: Stories (storyteller)

**Autonomous storytelling engine for any project.**

Create professional presentations, documents, and content across multiple formats and audiences.

## Installation

```bash
amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-stories@main
amplifier bundle use stories
```

## What's Included

### Content Formats (5)
| Format | Best For |
|--------|----------|
| **HTML** | Quick internal shares, GitHub Pages |
| **PowerPoint** | Executive presentations, corporate settings |
| **Excel** | Data analysis, metrics dashboards |
| **Word** | Technical documentation, proposals |
| **PDF** | Final deliverables, archival |

### Specialist Agents (11)

| Agent | Purpose |
|-------|---------|
| `stories:storyteller` | Primary agent - creates presentations |
| `stories:story-researcher` | Gathers data from git, sessions, APIs |
| `stories:content-strategist` | Plans what stories to tell |
| `stories:technical-writer` | Deep technical documentation |
| `stories:marketing-writer` | Community and public communication |
| `stories:executive-briefer` | High-level summaries for decision-makers |
| `stories:release-manager` | Automated release documentation |
| `stories:case-study-writer` | Narrative case studies from sessions |
| `stories:data-analyst` | Data transformation and visualization |
| `stories:content-adapter` | Format and audience transformation |
| `stories:community-manager` | Community engagement content |

### Automated Workflows (4 Recipes)

| Recipe | Description |
|--------|-------------|
| `session-to-case-study` | Turn breakthrough sessions into shareable content |
| `git-tag-to-changelog` | Generate release notes from git tags |
| `weekly-digest` | Regular project updates with zero manual work |
| `blog-post-generator` | Feature stories from git activity |

## Quick Start

### Manual Creation

```
"Create a PowerPoint about shadow environments"
"Make an Excel dashboard showing adoption metrics"
"Write a case study about the authentication refactor"
```

### Automated (Recipes)

```
"Run the weekly digest recipe"
"Generate a case study from this session"
"Create release notes for the v2.0 tag"
```

## Directory Structure

```
amplifier-bundle-stories/
├── bundle.md                 # Thin entry point
├── behaviors/
│   └── storyteller.yaml      # Agents + recipes
├── agents/                   # 11 specialist agents
├── context/                  # Instructions & styles
│   ├── storyteller-instructions.md
│   ├── presentation-styles.md
│   ├── responsive-design.md
│   ├── powerpoint-template.md
│   └── archetypes/           # Story patterns
├── recipes/                  # Automated workflows
├── tools/                    # Python utilities
│   ├── html2pptx.py
│   ├── analyze_sessions.py
│   └── create_dashboard.py
└── workspace/                # Format templates
    ├── pptx/templates/
    ├── xlsx/templates/
    ├── docx/templates/
    └── pdf/templates/
```

## Dependencies

This bundle includes `amplifier-foundation` for core tools (filesystem, bash, web).

For document creation, you'll need the Anthropic Skills:
```bash
git clone https://github.com/anthropics/skills ~/dev/anthropic-skills
```

## Contributing

> [!NOTE]
> This project is not currently accepting external contributions, but we're actively working toward opening this up. We value community input and look forward to collaborating in the future. For now, feel free to fork and experiment!

Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
## License

MIT License - see [LICENSE](LICENSE)
