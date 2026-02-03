# Storyteller Instructions

Detailed guidance for creating presentation decks.

## Research Phase

Before creating a deck, gather:

1. **GitHub activity** - Use `gh` CLI to find:
   - Recent commits and PRs related to the feature
   - Timeline (when did development start/end?)
   - Number of repos touched
   - Key contributors

2. **Feature details** - Understand:
   - What problem does it solve?
   - How does it work?
   - What's the user-facing impact?
   - Any metrics or numbers?

3. **Narrative angle** - Decide the story:
   - "Built with Amplifier" (showcase projects like Cortex)
   - "Amplifier Feature" (platform capabilities)
   - "Developer Experience" (tooling improvements)
   - "Enterprise Value" (compliance, cost, scale)

## Creating the Deck

### HTML Template

**IMPORTANT**: All presentations must be responsive and work across devices. See `context/responsive-design.md` for complete guidelines.

**CRITICAL - Slide Overflow Pattern**: Do NOT use `justify-content: center` on all slides. This causes content clipping on mobile. Instead:
- Slides flow from top by default (with generous top padding)
- Use `.center` class only for title slides that need vertical centering
- Always include `overflow-y: auto` on slides

Start with this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>Deck Title</title>
    <style>
        /* Core slide CSS - CRITICAL for preventing content clipping */
        .slide {
            display: none;
            width: 100vw;
            min-height: 100vh;
            min-height: 100dvh;
            padding: clamp(60px, 10vw, 120px) clamp(20px, 5vw, 80px) clamp(80px, 12vw, 100px);
            flex-direction: column;
            overflow-y: auto;      /* Enable scrolling for tall content */
            overflow-x: hidden;    /* Prevent horizontal scroll */
            /* NO justify-content: center here! */
        }

        /* Speaker notes for voice-over generation - hidden visually */
        .notes {
            display: none;
        }

        .slide.active {
            display: flex;
        }

        /* Centering is OPT-IN for title/short slides only */
        .center {
            text-align: center;
            align-items: center;
            justify-content: center;
        }

        /* Landscape mobile: reduce vertical padding */
        @media (max-height: 500px) and (orientation: landscape) {
            .slide {
                padding: 16px clamp(20px, 5vw, 80px) 60px;
            }
            .slide.center {
                justify-content: flex-start;
            }
        }

        /* Accessibility: respect reduced motion preference */
        @media (prefers-reduced-motion: reduce) {
            .slide, .slide * {
                animation: none !important;
                transition: none !important;
            }
        }

    </style>
</head>
<body>
    <!-- Slides -->
    <div class="slide active">...</div>
    <div class="slide">...</div>
    
    <!-- Navigation -->
    <div class="nav" id="nav"></div>
    <div class="slide-counter" id="counter"></div>
    

    
    <script>
        /* Navigation JS - arrow keys, click, dots */
    </script>
</body>
</html>
```

### Navigation JavaScript

Always include this for keyboard/click/dot/**touch** navigation:

```javascript
const slides = document.querySelectorAll('.slide');
let currentSlide = 0;

function showSlide(n) {
    slides[currentSlide].classList.remove('active');
    currentSlide = (n + slides.length) % slides.length;
    slides[currentSlide].classList.add('active');
    updateNav();
}

function updateNav() {
    const nav = document.getElementById('nav');
    const counter = document.getElementById('counter');
    nav.innerHTML = '';
    slides.forEach((_, i) => {
        const dot = document.createElement('div');
        dot.className = 'nav-dot' + (i === currentSlide ? ' active' : '');
        dot.onclick = () => showSlide(i);
        nav.appendChild(dot);
    });
    counter.textContent = `${currentSlide + 1} / ${slides.length}`;
}

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ') showSlide(currentSlide + 1);
    if (e.key === 'ArrowLeft') showSlide(currentSlide - 1);
});

// Click navigation
document.addEventListener('click', (e) => {
    if (e.target.closest('.nav')) return;
    if (e.clientX > window.innerWidth / 2) showSlide(currentSlide + 1);
    else showSlide(currentSlide - 1);
});

// Touch/swipe navigation (REQUIRED for mobile)
let touchStartX = 0;
let touchEndX = 0;
const SWIPE_THRESHOLD = 50;

document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
}, { passive: true });

document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    const diff = touchStartX - touchEndX;
    if (Math.abs(diff) > SWIPE_THRESHOLD) {
        if (diff > 0) showSlide(currentSlide + 1);
        else showSlide(currentSlide - 1);
    }
}, { passive: true });

updateNav();
```

### Slide Types

**Title Slide:**
```html
<div class="slide active center">
    <div class="section-label">Category</div>
    <h1 class="headline">Feature Name</h1>
    <p class="subhead">One-line description</p>
    <div class="small-text">January 2026</div>
</div>
```

**Problem Slide:**
```html
<div class="slide">
    <div class="section-label">The Problem</div>
    <h2 class="headline">Pain point headline</h2>
    <div class="thirds">
        <div class="card">...</div>
        <div class="card">...</div>
        <div class="card">...</div>
    </div>
</div>
```

**Code Example Slide:**
```html
<div class="slide">
    <div class="section-label">Usage</div>
    <h2 class="medium-headline">How to use it</h2>
    <div class="code-block">
        <pre><code><span class="comment"># Comment</span>
<span class="command">command</span> --flag value

<span class="comment"># Another section</span>
<span class="command">another-command</span> <span class="string">"argument"</span></code></pre>
    </div>
</div>
```

**CRITICAL: Code blocks MUST use `<pre><code>` wrapper** to preserve line breaks. Without `<pre>`, all lines will run together as a single line. The `<pre>` tag preserves whitespace and newlines.

**Velocity Slide:**
```html
<div class="slide center">
    <h2 class="medium-headline">Development velocity</h2>
    <div class="velocity-grid">
        <div class="velocity-stat">
            <div class="velocity-number">3</div>
            <div class="velocity-label">Repositories</div>
        </div>
        <!-- More stats -->
    </div>
</div>
```

## Quality Checklist

Before presenting to user:

- [ ] Navigation works (arrows, click, dots, **swipe on mobile**)
- [ ] Slide counter updates correctly
- [ ] No horizontal scrolling on any slide
- [ ] **No content clipping on mobile (test at 320px viewport)**
- [ ] **Slides use `overflow-y: auto` (not clipping tall content)**
- [ ] **`justify-content: center` only on `.slide.center` classes**
- [ ] Code blocks use `<pre><code>` wrapper (NOT just `<code>` - lines will run together!)
- [ ] Code blocks don't overflow (use `pre-wrap` if needed)
- [ ] Consistent color scheme throughout
- [ ] Velocity slide has accurate numbers
- [ ] All links are correct

- [ ] **Responsive: Text readable on mobile without zooming**
- [ ] **Responsive: Grids collapse to single column on narrow screens**
- [ ] **Responsive: Touch targets ≥44px for tappable elements**

### Optional QA Enhancement (Opt-in Only)

- Run a Playwright screenshot pass on the HTML deck only when explicitly requested.
- If Playwright isn't available, ask permission to install it; if installation isn't possible, provide a manual QA checklist and note the limitation.
- Check for overflow/clipping, space usage, SVG connector overlaps, emoji rendering in headless mode, and large-screen scaling.
- Provide a brief QA report with slide numbers and proposed fixes.
- Do not modify the deck unless the user asks to apply fixes.

## Deployment Workflow

1. Create deck, save to `docs/`
2. Present to user for review
3. Iterate based on feedback
4. When approved: `./deploy.sh filename.html`
5. Commit changes to git

## Video Generation (Optional)

You can convert the HTML deck to an MP4 video using the `tools/html2video.py` tool. This supports optional AI voice-over.

**For detailed best practices, see `context/video-presentation-guidelines.md`.**

### Video-Optimized Slide Design

When creating decks intended for video:

1. **Use 70%+ of viewport space** - Video is often viewed on large screens or from a distance
2. **Scale up typography** - Headlines 48-140px, body text 18-28px minimum
3. **Use Problem → Solution pattern** - "How do you...?" followed by "And now you can..."
4. **Keep animations simple** - Under 0.5s duration, use `animation-fill-mode: forwards`

### Speaker Notes for Voice-Over

```html
<div class="slide">
    <h1>Slide Title</h1>
    <div class="notes">
        Write conversationally, as if speaking to someone.
        Aim for 50-80 words per slide (5-8 seconds of speech).
        Match tone to content - dramatic for reveals, calm for data.
    </div>
</div>
```

### Slide Timing Strategy

Different slides need different durations:

| Slide Type | Duration | 
|------------|----------|
| Title slide | 4-5 seconds |
| Reveal slides ("And now you can...") | 5 seconds |
| Content-heavy (grids, multi-card) | 5-6 seconds |
| Standard content | 3 seconds |
| Final slide | 5 seconds |

### Recording Workflow

```bash
# Quick preview (silent, small)
uv run --with playwright tools/html2video.py docs/deck.html docs/preview.mp4 \
    --min-duration 2 --width 640 --height 360

# Standard recording with voice-over
uv run --with playwright --with edge-tts tools/html2video.py docs/deck.html docs/deck.mp4 \
    --min-duration 3 --voice en-US-AriaNeural

# High-quality with British voice
uv run --with playwright --with edge-tts tools/html2video.py docs/deck.html docs/deck.mp4 \
    --min-duration 4 --width 1920 --height 1080 --voice en-GB-SoniaNeural
```

### Pre-Recording Checklist

Before running the video tool:
- [ ] Content accuracy verified (dates, names, numbers)
- [ ] Each slide uses 70%+ of viewport
- [ ] No overflow on any slide
- [ ] Animations complete within slide duration
- [ ] Speaker notes are conversational (if using voice-over)

### Post-Recording

For universal compatibility (Teams, Slack, LinkedIn), convert WebM to MP4:
```bash
ffmpeg -i presentation.webm -c:v libx264 -crf 23 -c:a aac presentation.mp4
```

4. **Deploy**: Commit .mp4 to `docs/`.
