# Video Presentation Guidelines

Best practices for creating effective video presentations from HTML decks.

## Slide Design for Video

### Space Usage Optimization

**Target 70-100% viewport usage** on every slide. Common pitfalls:

| Problem | Impact | Solution |
|---------|--------|----------|
| Content uses only 30-45% of space | Hard to read, wastes screen real estate | Scale up typography, reduce padding |
| Overflow content | Gets cut off in video | Use `overflow-y: auto` or split into multiple slides |
| Too much whitespace | Looks unfinished | Fill with larger text or supporting visuals |

**Pre-flight check** - Before recording, verify each slide:
```javascript
// Run in browser console to check space usage
document.querySelectorAll('.slide').forEach((slide, i) => {
    const used = slide.scrollHeight / window.innerHeight * 100;
    const overflow = slide.scrollHeight > slide.clientHeight;
    console.log(`Slide ${i+1}: ${used.toFixed(0)}% used, overflow: ${overflow}`);
});
```

### Typography for Video

Video presentations are often viewed on large screens or from a distance. Use generous sizing:

```css
:root {
    /* Headlines - BIG and readable */
    --font-headline: clamp(48px, 8vw, 140px);
    
    /* Impact numbers - dominate the slide */
    --font-big-number: clamp(72px, 15vw, 220px);
    
    /* Body text - readable at distance */
    --font-body: clamp(18px, 2.5vw, 28px);
    
    /* Use gradient text for emphasis */
    background: linear-gradient(135deg, #FF2D92, #FF6B9D);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
```

### Narrative Structure

**Problem → Solution pattern** creates dramatic tension:

1. **Problem slide**: "How do you [pain point]?"
2. **Solution slide**: "And now you can [capability]"

This two-slide pattern:
- Creates anticipation
- Makes reveals memorable
- Works well with video timing (pause on reveal)

## Slide Timing Strategy

Different slides need different durations:

| Slide Type | Duration | Rationale |
|------------|----------|-----------|
| **Title slide** | 4-5 seconds | Set the scene, dramatic pause |
| **Problem slides** | 3 seconds | Quick setup for the reveal |
| **Reveal slides** ("And now you can...") | 5 seconds | Let the solution sink in |
| **Content-heavy** (grids, multi-card) | 5-6 seconds | Reading time needed |
| **Standard content** | 3 seconds | Default pacing |
| **Final slide** | 5 seconds | Let ending resonate |

**Example timing map** for a 16-slide presentation (~68 seconds total):
```python
SLIDE_TIMINGS = {
    1: 4.0,    # Title
    5: 5.0,    # First reveal
    8: 5.0,    # Second reveal
    13: 5.0,   # Content-heavy (6 cards)
    16: 5.0,   # Final takeaway
    # All others: 3.0 seconds (default)
}
```

## CSS Transitions for Video

### Slide Transitions

Add smooth transitions that look good when recorded:

```css
.slide {
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.5s ease, visibility 0.5s ease;
}

.slide.active {
    opacity: 1;
    visibility: visible;
}
```

### Element Animations

**Keep animations simple** - complex animations may not record well:

```css
/* Good: Simple fade-in */
.card {
    animation: fadeIn 0.3s ease forwards;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Avoid: Complex multi-step animations that depend on timing */
```

### Animation Persistence

**Ensure animations complete before slide change:**

1. Set animation duration shorter than minimum slide duration
2. Use `animation-fill-mode: forwards` to persist final state
3. Avoid infinite animations (they look broken when paused)

```css
/* Animation completes and holds */
.element {
    animation: slideIn 0.5s ease forwards;
    animation-fill-mode: forwards;
}
```

## Pre-Recording Checklist

Run these checks before recording:

- [ ] **Content accuracy** - Verify dates, names, numbers, spelling
- [ ] **Space usage** - Each slide uses 70%+ of viewport
- [ ] **No overflow** - No slide has scrollable content
- [ ] **WOW moments** - Key slides have impactful messaging
- [ ] **Navigation works** - Arrow keys advance correctly
- [ ] **Animations complete** - All animations finish within slide duration
- [ ] **Typography readable** - Text is large enough for video

## Recording Best Practices

### Timeout Handling

Long presentations may exceed command timeouts. For presentations over 30 seconds:

```bash
# Run in background to avoid timeout
nohup uv run --with playwright --with edge-tts python tools/html2video.py \
    input.html output.mp4 > recording.log 2>&1 &

# Monitor progress
tail -f recording.log
```

### Resolution Settings

| Use Case | Resolution | Notes |
|----------|------------|-------|
| Social media (general) | 1920x1080 | Standard HD |
| LinkedIn/Twitter | 1280x720 | Good balance of quality/size |
| Lobby display/kiosk | 1920x1080 or 3840x2160 | Higher resolution for large screens |
| Quick preview | 640x360 | Fast to generate |

### Output Format

The tool outputs WebM by default. For universal compatibility:

```bash
# Convert to MP4 for Teams/Slack/LinkedIn
ffmpeg -i presentation.webm -c:v libx264 -crf 23 -c:a aac presentation.mp4
```

**File size expectations:**
- 16 slides @ 68 seconds → ~5 MB (WebM)
- MP4 conversion: similar or smaller

## Speaker Notes for Voice-Over

### Writing Effective Notes

```html
<div class="slide">
    <h1>Feature Name</h1>
    <div class="notes">
        <!-- Keep it conversational, not bullet points -->
        This feature solves a real problem teams face every day.
        Instead of spending hours on manual work, you can now
        automate the entire process with a single command.
    </div>
</div>
```

**Guidelines:**
- Write conversationally, as if speaking to someone
- 50-80 words per slide (5-8 seconds of speech)
- Avoid technical jargon unless audience expects it
- Match tone to slide content (dramatic for reveals, calm for data)

### Voice Selection

Available voices vary by language. Common English options:

| Voice | Style |
|-------|-------|
| `en-US-AriaNeural` | Warm, professional female (default) |
| `en-US-GuyNeural` | Professional male |
| `en-GB-SoniaNeural` | British female |
| `en-AU-NatashaNeural` | Australian female |

## Common Pitfalls

### 1. Recording Stops Early
**Cause**: Process killed before video finalized
**Fix**: Wait for "Success!" message, don't interrupt

### 2. Wrong Day/Date Displayed
**Impact**: Requires full re-recording
**Fix**: Triple-check all dates before recording

### 3. Animations Look Choppy
**Cause**: Animation duration longer than frame capture rate
**Fix**: Keep animations under 0.5s, use simple easing

### 4. Text Too Small
**Cause**: Designed for desktop viewing, not video
**Fix**: Increase all typography by 1.5-2x for video

### 5. Audio/Video Desync
**Cause**: Notes too long for slide duration
**Fix**: Either shorten notes or increase min-duration

## Quick Reference

```bash
# Standard recording (with voice-over)
uv run --with playwright --with edge-tts python tools/html2video.py \
    docs/deck.html docs/deck.mp4 \
    --min-duration 3 \
    --width 1920 --height 1080

# Quick preview (silent, small)
uv run --with playwright python tools/html2video.py \
    docs/deck.html docs/preview.mp4 \
    --min-duration 2 \
    --width 640 --height 360

# High-quality with custom voice
uv run --with playwright --with edge-tts python tools/html2video.py \
    docs/deck.html docs/deck.mp4 \
    --min-duration 4 \
    --voice en-GB-SoniaNeural
```
