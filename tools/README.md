# Amplifier Stories - Development Tools

Utility scripts for creating presentations, analyzing Amplifier usage, and generating data-driven insights.

## Available Tools

### html2pptx.py

Converts Amplifier Stories HTML decks to PowerPoint presentations.

**Purpose:** Generate native PowerPoint files from HTML story decks, enabling easy sharing and editing in corporate environments.

**Usage:**
```bash
# Using uv (recommended)
uv run --with python-pptx,beautifulsoup4,lxml python tools/html2pptx.py <input.html> [output.pptx]

# Examples
uv run --with python-pptx,beautifulsoup4,lxml python tools/html2pptx.py docs/my-deck.html
uv run --with python-pptx,beautifulsoup4,lxml python tools/html2pptx.py docs/my-deck.html output/presentation.pptx
```

**Supported Elements:**
- Slide structure (`.slide` divs)
- Section labels (`.section-label`)
- Headlines and subheads (`.headline`, `.subhead`, `.medium-headline`)
- Cards with titles and text (`.card`, `.card-title`, `.card-text`)
- Tenet boxes with accent colors (`.tenet`, `.tenet.green`, `.tenet.orange`)
- Feature lists with check/x marks (`.feature-list`)
- Data tables (`.data-table`)
- Highlight/callout boxes (`.highlight-box`)
- Big numbers and stats (`.stat-grid`, `.card-number`)
- Versus comparisons (`.versus`)
- Quotes (`.quote`)

**Output:**
- 16:9 widescreen format (10" × 5.625")
- Black backgrounds with Amplifier Stories color palette
- Editable text in PowerPoint
- Matching visual hierarchy and styling

---

### html2video.py

Converts HTML presentation decks to MP4 video with optional AI voice-over narration.

**Purpose:** Create shareable video content from HTML presentations for social media, lobby displays, or self-running kiosks.

**Usage:**
```bash
# Silent mode (no voice-over) - uses min-duration per slide
uv run --with playwright tools/html2video.py docs/my-deck.html docs/my-deck.mp4

# With AI voice-over from speaker notes
uv run --with playwright --with edge-tts tools/html2video.py docs/my-deck.html docs/my-deck.mp4

# Custom settings
uv run --with playwright --with edge-tts tools/html2video.py docs/my-deck.html docs/my-deck.mp4 \
    --min-duration 3 \
    --width 1920 --height 1080 \
    --voice en-GB-SoniaNeural
```

**Speaker Notes Format:**
Add notes inside slides for voice-over narration:
```html
<div class="slide">
    <h1>My Slide Title</h1>
    <div class="notes">This text will be spoken as voice-over narration.</div>
</div>
```

**Options:**
- `--min-duration` - Minimum seconds per slide (default: 5.0)
- `--width` / `--height` - Video dimensions (default: 1920x1080)
- `--voice` - Edge TTS voice ID (default: en-US-AriaNeural)

**Requirements:**
- `ffmpeg` and `ffprobe` must be installed on system path
- Playwright (loaded via `uv run --with playwright`)
- edge-tts (optional, for voice-over: `uv run --with edge-tts`)

**Output:**
- H.264 encoded MP4 video
- AAC audio (voice-over or silence)
- Slide timing synchronized with audio duration

---

### pptx2images.py

Converts PowerPoint presentations to individual slide images.

**Purpose:** Extract slide images from PPTX files for use in documentation or preview generation.

**Usage:**
```bash
python tools/pptx2images.py input.pptx output_directory/
```

---

### analyze_sessions.py

Analyzes Amplifier session data from `events.jsonl` files to extract usage patterns, agent interactions, and performance metrics.

**Purpose:** Understand how Amplifier is being used across sessions to inform storytelling and identify interesting patterns.

**Usage:**
```bash
python tools/analyze_sessions.py <path-to-events.jsonl>
```

**Output:**
- Session duration and turn count
- Agent invocations and types
- Tool usage patterns
- Provider/model statistics
- Error tracking
- Performance metrics

### create_dashboard.py

Generates Excel dashboards from analyzed session data, creating visual insights about Amplifier usage.

**Purpose:** Create data-driven stories showing Amplifier adoption, performance, and impact.

**Usage:**
```bash
# First analyze sessions to generate data
python tools/analyze_sessions.py sessions/*.jsonl > analysis.json

# Then create dashboard
python tools/create_dashboard.py analysis.json output-dashboard.xlsx
```

**Output:**
- Multi-sheet Excel workbook
- Charts showing usage trends
- Metrics tables with formulas
- Formatted with professional styling

## Data Flow

```
events.jsonl → analyze_sessions.py → analysis.json → create_dashboard.py → dashboard.xlsx
```

## Dependencies

```bash
# Python packages
pip install openpyxl pandas

# For recalculating Excel formulas (if used)
brew install libreoffice  # macOS
# or
sudo apt-get install libreoffice  # Linux
```

## Use Cases

1. **Monthly reporting** - Track Amplifier adoption and usage metrics
2. **Story research** - Find interesting patterns to showcase in presentations
3. **Performance analysis** - Identify bottlenecks or inefficiencies
4. **Feature validation** - See which features are actually being used

## Integration with Storyteller

These tools help gather data that can be turned into compelling stories:

- Excel dashboards → Metrics slides in presentations
- Usage patterns → Real-world example slides
- Performance data → Impact and velocity slides
- Agent interactions → Technical architecture slides

## Notes

- Output files (*.csv, *.json) are gitignored by default
- Scripts are version controlled in tools/ directory
- Generated dashboards can be moved to `workspace/xlsx/output/` for inclusion in presentations
