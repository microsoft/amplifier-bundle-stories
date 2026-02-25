# Presentation Styles

Two remembered styles for different use cases.

## Useful Apple Keynote (Preferred)

Higher information density while maintaining polish. Use for most decks.

**Characteristics:**
- Black backgrounds (#000)
- Clean sans-serif typography (SF Pro Display, Segoe UI, system fonts)
- Section labels: 14px uppercase, accent color, letter-spacing: 2px
- Headlines: 48-72px, font-weight 600-700, letter-spacing: -1px to -2px
- Cards with titles and descriptions for feature grids
- Code blocks with syntax highlighting (green for code, gray for comments)
- Comparison tables and before/after layouts
- Flow diagrams with colored step boxes
- Velocity/stats grids near the end
- Navigation dots at bottom center
- Slide counter at bottom right

**CSS Essentials (Responsive):**

See `context/responsive-design.md` for complete responsive guidelines.

```css
:root {
    /* Fluid typography - scales with viewport */
    --font-headline: clamp(36px, 8vw, 72px);
    --font-medium-headline: clamp(24px, 5vw, 48px);
    --font-subhead: clamp(16px, 3vw, 32px);
    --font-big-number: clamp(60px, 20vw, 180px);
    
    /* Fluid spacing */
    --padding-slide: clamp(20px, 5vw, 80px);
    --gap-grid: clamp(16px, 3vw, 40px);
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
    background: #000;
    color: #fff;
    overflow: hidden;
    overscroll-behavior: none;
}

.slide {
    min-height: 100vh;
    min-height: 100dvh; /* Dynamic viewport for mobile */
    padding: var(--padding-slide);
    overflow-y: auto;
    overflow-x: hidden;
}

.section-label {
    font-size: clamp(12px, 1.5vw, 14px);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--accent-color, #0A84FF);
}

.headline {
    font-size: var(--font-headline);
    font-weight: 700;
    letter-spacing: clamp(-1px, -0.03em, -2px);
    line-height: 1.1;
}

.big-number {
    font-size: var(--font-big-number);
}

/* Responsive grids - collapse on mobile */
.thirds, .split {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(280px, 100%), 1fr));
    gap: var(--gap-grid);
}

.card {
    background: var(--surface-1, rgba(255,255,255,0.06));
    border: 1px solid var(--border-subtle, rgba(255,255,255,0.12));
    border-radius: clamp(12px, 2vw, 16px);
    padding: clamp(16px, 4vw, 28px);
}

.code-block {
    background: var(--surface-1, rgba(255,255,255,0.06));
    border: 1px solid var(--border-subtle, rgba(255,255,255,0.12));
    border-radius: 12px;
    padding: clamp(12px, 3vw, 20px) clamp(16px, 4vw, 28px);
    font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
    font-size: clamp(12px, 2vw, 15px);
    line-height: 1.6;
    white-space: pre-wrap;  /* WRAP long lines on mobile */
    word-wrap: break-word;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}
```

## Color Accessibility (Required)

ALL text must meet WCAG AA contrast ratios against its immediate background:
- Normal text (< 24px): minimum **4.5:1** contrast ratio
- Large text (>= 24px or >= 19px bold): minimum **3:1**

### Surface Color Hierarchy

Use these CSS custom properties for layered surfaces on dark backgrounds:

```css
:root {
    /* Surface hierarchy - visible layers on #000 */
    --surface-1: rgba(255,255,255,0.06);   /* default cards */
    --surface-2: rgba(255,255,255,0.10);   /* elevated cards, active states, matrix cells */
    --surface-3: rgba(255,255,255,0.15);   /* modals, overlays, highlighted regions */
    --border-subtle: rgba(255,255,255,0.12);
    --border-visible: rgba(255,255,255,0.20);

    /* Text hierarchy - minimum opacities on #000 */
    --text-primary: #ffffff;
    --text-secondary: rgba(255,255,255,0.7);   /* descriptions, body text */
    --text-tertiary: rgba(255,255,255,0.5);    /* captions, labels - MINIMUM for readable text */
}
```

### Text Opacity Rules

- **Primary** (`#fff`): Headlines, key numbers, emphasized content
- **Secondary** (`rgba(255,255,255,0.7)`): Card descriptions, body paragraphs, list items
- **Tertiary** (`rgba(255,255,255,0.5)`): Section labels, captions, footnotes
- **FORBIDDEN**: Never use `rgba(255,255,255,0.3)` or lower for any text that must be read

### Card Styling (Updated)

```css
.card {
    background: var(--surface-1);
    border: 1px solid var(--border-subtle);
    border-radius: clamp(12px, 2vw, 16px);
    padding: clamp(16px, 4vw, 28px);
}
.card h3, .card h4 { color: var(--text-primary); }
.card p, .card li  { color: var(--text-secondary); }  /* 0.7, never 0.5 for body text */
```

Cards must be visually distinct from the body background. On a dim projector, if you can't see the card boundary, increase `--surface-1`.

## Icons and Emoji Sizing

Icons follow the same fluid sizing rules as typography. NEVER use fixed pixel values for icons.

```css
.icon-inline  { font-size: inherit; }                        /* matches surrounding text */
.icon-card    { font-size: clamp(28px, 5vw, 48px); }        /* card header icons */
.icon-feature { font-size: clamp(32px, 6vw, 56px); }        /* standalone feature icons */
.icon-hero    { font-size: clamp(48px, 10vw, 80px); }       /* hero/title icons */
```

**Rules:**
- Minimum card icon size: **28px** (anything smaller is unreadable on projectors)
- Minimum standalone icon size: **32px**
- Always use `clamp()` — never hardcode `font-size: 24px` or `font-size: 20px` on icons
- Emoji icons in grids should be at least `clamp(28px, 5vw, 48px)`

## Tables and Matrix Grids

### Data Tables

```css
.data-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
}
.data-table th {
    color: var(--accent-color, #0A84FF);
    font-size: var(--fs-small, clamp(12px, 1.8vw, 14px));
    font-weight: 600;
    text-align: left;
    padding: clamp(8px, 1.5vw, 12px);
    border-bottom: 1px solid var(--border-visible);
}
.data-table td {
    color: var(--text-secondary);
    font-size: var(--fs-body, clamp(14px, 2vw, 16px));
    padding: clamp(8px, 1.5vw, 12px);
    border-bottom: 1px solid rgba(255,255,255,0.06);
}
```

### Quadrant / Matrix Grids

```css
.quadrant {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2px;
}
.quadrant-cell {
    background: var(--surface-2);   /* elevated surface for visibility */
    padding: var(--space-lg, clamp(24px, 4vw, 40px));
    border-radius: var(--radius-sm, clamp(8px, 1vw, 12px));
}
.quadrant-cell h4 { color: var(--text-primary); }
.quadrant-cell p  { color: var(--text-secondary); }
```

**Rules:**
- Matrix cells use `--surface-2` (0.10 opacity), NOT `--surface-1` — each cell must be clearly visible
- NEVER use `opacity` below 0.5 on matrix cells — dim cells become invisible on projectors
- Table header text uses accent color, not white, for visual hierarchy

## Apple Keynote (Pure)

Maximum visual impact, minimal information density. Use for executive summaries or high-level vision decks.

**Characteristics:**
- Pure black backgrounds
- San Francisco typography (or similar sans-serif)
- One major concept per slide
- Full-bleed imagery where applicable
- Bold, centered headlines
- Avoid bullet points entirely
- Use icons or 3-word phrases instead of lists
- Premium, quiet, powerful aesthetic

**When to use:**
- Executive presentations
- Vision/strategy decks
- When visual impact matters more than information density

## Choosing a Style

| Audience | Recommended Style |
|----------|-------------------|
| Engineers, developers | Useful Apple Keynote |
| Executives, leadership | Apple Keynote (Pure) |
| Mixed audience | Useful Apple Keynote |
| Feature deep-dive | Useful Apple Keynote |
| Vision/roadmap | Apple Keynote (Pure) |

Default to **Useful Apple Keynote** unless specifically asked for the pure style.
