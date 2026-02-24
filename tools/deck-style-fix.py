#!/usr/bin/env python3
"""Deterministic CSS accessibility and readability fixer for HTML presentation decks.

Fixes contrast, font-size, and opacity issues using ZERO LLM tokens — pure
regex/DOM transforms.  Works across 4 different CSS variable naming conventions.

Phases:
  1. CSS variable value fixes (contrast, surface brightness, border visibility)
  2. CSS rule font-size minimums (context-dependent)
  3. Inline style fixes (font-size, color, opacity)
  4. Inject missing surface hierarchy variables
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Change tracking
# ---------------------------------------------------------------------------

@dataclass
class Change:
    phase: str        # "css-var", "css-rule", "inline", "inject"
    category: str     # "contrast", "font-size", "opacity", "color", "inject"
    location: str     # variable name, selector, or line number
    old_value: str
    new_value: str
    detail: str       # human-readable explanation


# ---------------------------------------------------------------------------
# Color helpers (WCAG 2.1)
# ---------------------------------------------------------------------------

def _linearize(c: float) -> float:
    """sRGB channel (0-1) to linear."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(r: int, g: int, b: int) -> float:
    """Relative luminance for sRGB values 0-255."""
    return (0.2126 * _linearize(r / 255.0)
            + 0.7152 * _linearize(g / 255.0)
            + 0.0722 * _linearize(b / 255.0))


def contrast_ratio(l1: float, l2: float) -> float:
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def parse_hex(h: str) -> tuple[int, int, int]:
    """Parse #RGB or #RRGGBB to (r, g, b)."""
    h = h.lstrip("#")
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


_RGBA_RE = re.compile(
    r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([0-9.]+))?\s*\)"
)


def parse_rgba(val: str) -> tuple[int, int, int, float] | None:
    """Parse rgba(r,g,b,a) or rgb(r,g,b). Returns (r,g,b,a) or None."""
    m = _RGBA_RE.search(val)
    if not m:
        return None
    r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
    a = float(m.group(4)) if m.group(4) is not None else 1.0
    return r, g, b, a


def rgba_str(r: int, g: int, b: int, a: float) -> str:
    """Format an rgba() color string."""
    if a == 1.0:
        return f"rgba({r},{g},{b},1)"
    a_s = f"{a:.2f}".rstrip("0").rstrip(".")
    if not a_s or a_s == "":
        a_s = "0"
    return f"rgba({r},{g},{b},{a_s})"


def brighten_hex_to_contrast(hex_color: str, min_ratio: float = 4.5) -> str | None:
    """Brighten a hex color so its contrast against #000 meets min_ratio.

    Returns new hex string or None if already OK.
    """
    r, g, b = parse_hex(hex_color)
    lum = relative_luminance(r, g, b)
    bg_lum = 0.0  # black
    if contrast_ratio(lum, bg_lum) >= min_ratio:
        return None  # already fine

    # Target luminance: (target_lum + 0.05) / (0 + 0.05) >= min_ratio
    target_lum = min_ratio * 0.05 - 0.05
    if target_lum <= 0:
        target_lum = 0.001

    # Blend toward white until we hit target luminance
    for blend in range(1, 101):
        t = blend / 100.0
        nr = int(r + (255 - r) * t)
        ng = int(g + (255 - g) * t)
        nb = int(b + (255 - b) * t)
        if relative_luminance(nr, ng, nb) >= target_lum:
            return to_hex(nr, ng, nb)

    return to_hex(255, 255, 255)  # fallback: white


# ---------------------------------------------------------------------------
# Variable classification
# ---------------------------------------------------------------------------

# Accent / semantic colors -- never modify
_ACCENT_WORDS = {
    "accent", "green", "red", "blue", "orange", "yellow", "purple", "teal",
    "pink", "cyan", "success", "warning", "error", "danger", "info",
    "highlight", "glow",
}

# Text-purpose indicators
_TEXT_WORDS = {
    "text", "fg", "dim", "muted", "secondary", "tertiary", "subtle",
    "caption", "label", "mid", "readable", "floor",
}

# Surface-purpose indicators
_SURFACE_WORDS = {"surface", "card-bg", "bg-subtle", "bg-card", "bg-secondary"}

# Border indicators
_BORDER_WORDS = {"border"}

# Main background -- skip
_BG_EXACT = {
    "--bg", "--background", "--bg-color", "--bg-dark", "--bg-darker",
    "--bg-primary", "--bg-slide", "--color-bg",
}


def _var_name_parts(name: str) -> set[str]:
    """Split a CSS variable name into classifiable tokens.

    Strips leading ``--`` and an optional ``color-`` namespace prefix, then
    splits on hyphens.  Also returns multi-word slug fragments so that
    compound names like ``card-bg`` match against _SURFACE_WORDS.
    """
    core = name.lstrip("-")
    if core.startswith("color-"):
        core = core[6:]
    parts = set(core.split("-"))
    # Add bigram slugs: "card-bg" from ["card", "bg"]
    tokens = core.split("-")
    for i in range(len(tokens) - 1):
        parts.add(tokens[i] + "-" + tokens[i + 1])
    return parts


def classify_variable(name: str) -> str:
    """Classify a CSS variable by its name.

    Returns one of: 'text', 'surface', 'border', 'accent', 'bg', 'unknown'.
    """
    parts = _var_name_parts(name)

    # Exact main-background matches
    if name in _BG_EXACT:
        return "bg"

    # Accent / semantic -- check FIRST (accent-dim is still accent)
    if parts & _ACCENT_WORDS:
        return "accent"

    # Surface: bg for cards, subtle surfaces
    if parts & _SURFACE_WORDS:
        return "surface"
    # Also catch --bg-card, --card-bg style names not in exact bg set
    if "card" in parts and "bg" in parts:
        return "surface"

    # Border
    if parts & _BORDER_WORDS:
        return "border"

    # Text / foreground
    if parts & _TEXT_WORDS:
        if not (parts & _SURFACE_WORDS) and not (parts & _BORDER_WORDS):
            return "text"

    return "unknown"


# ---------------------------------------------------------------------------
# Phase 1: CSS Variable Value Fixes
# ---------------------------------------------------------------------------

_ROOT_BLOCK_RE = re.compile(r"(:root\s*\{)([^}]+)(\})", re.DOTALL)
_VAR_DECL_RE = re.compile(r"(--[\w-]+)\s*:\s*([^;]+);")
_HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}){1,2}$")


def phase1_css_variables(html: str) -> tuple[str, list[Change]]:
    """Fix CSS variable values in :root blocks."""
    changes: list[Change] = []

    root_match = _ROOT_BLOCK_RE.search(html)
    if not root_match:
        return html, changes

    root_open = root_match.group(1)
    root_body = root_match.group(2)
    root_close = root_match.group(3)
    new_body = root_body

    for m in _VAR_DECL_RE.finditer(root_body):
        var_name = m.group(1)
        var_value = m.group(2).strip()
        kind = classify_variable(var_name)

        if kind in ("accent", "bg", "unknown"):
            continue

        new_val: str | None = None
        detail = ""

        if kind == "text":
            new_val, detail = _fix_text_color(var_value)
        elif kind == "surface":
            new_val, detail = _fix_surface_color(var_value)
        elif kind == "border":
            new_val, detail = _fix_border_color(var_value)

        if new_val and new_val != var_value:
            old_decl = f"{var_name}: {var_value};"
            new_decl = f"{var_name}: {new_val};"
            # Preserve surrounding whitespace by replacing exact match
            idx = new_body.find(old_decl)
            if idx != -1:
                new_body = new_body[:idx] + new_decl + new_body[idx + len(old_decl):]
            changes.append(Change(
                phase="css-var",
                category="contrast" if kind == "text" else kind,
                location=var_name,
                old_value=var_value,
                new_value=new_val,
                detail=detail,
            ))

    if new_body != root_body:
        old_root = root_match.group(0)
        new_root = root_open + new_body + root_close
        html = html.replace(old_root, new_root, 1)

    return html, changes


def _fix_text_color(value: str) -> tuple[str | None, str]:
    """Fix a text-purpose color value for contrast against black."""
    if _HEX_COLOR_RE.match(value):
        r, g, b = parse_hex(value)
        lum = relative_luminance(r, g, b)
        cr = contrast_ratio(lum, 0.0)
        if cr < 4.5:
            new_hex = brighten_hex_to_contrast(value, 4.5)
            if new_hex:
                return new_hex, f"contrast {cr:.2f}:1 -> 4.5:1"
        return None, ""

    rgba = parse_rgba(value)
    if rgba:
        r, g, b, a = rgba
        if a < 0.5:
            return rgba_str(r, g, b, 0.5), f"alpha {a} -> 0.5"
        # Approximate effective contrast: blend with black bg
        eff_r, eff_g, eff_b = int(r * a), int(g * a), int(b * a)
        lum = relative_luminance(eff_r, eff_g, eff_b)
        cr = contrast_ratio(lum, 0.0)
        if cr < 4.5 and a < 0.85:
            for test_a_int in range(int(a * 100), 101):
                test_a = test_a_int / 100.0
                er = int(r * test_a)
                eg = int(g * test_a)
                eb = int(b * test_a)
                if contrast_ratio(relative_luminance(er, eg, eb), 0.0) >= 4.5:
                    return (rgba_str(r, g, b, test_a),
                            f"contrast {cr:.2f}:1 -> 4.5:1 (alpha {a} -> {test_a})")
        return None, ""

    return None, ""


def _fix_surface_color(value: str) -> tuple[str | None, str]:
    """Fix a surface color: ensure not too close to pure black."""
    if _HEX_COLOR_RE.match(value):
        r, g, b = parse_hex(value)
        lum = relative_luminance(r, g, b)
        if lum < 0.008:
            return "#161616", f"luminance {lum:.4f} -> floor #161616"
        return None, ""

    rgba = parse_rgba(value)
    if rgba:
        r, g, b, a = rgba
        if r >= 200 and g >= 200 and b >= 200 and a < 0.05:
            return rgba_str(r, g, b, 0.06), f"alpha {a} -> 0.06"
        return None, ""

    return None, ""


def _fix_border_color(value: str) -> tuple[str | None, str]:
    """Fix a border color: ensure visible enough."""
    if _HEX_COLOR_RE.match(value):
        r, g, b = parse_hex(value)
        lum = relative_luminance(r, g, b)
        # rgba(255,255,255,0.12) on black ~ luminance of #1f1f1f ~ 0.013
        if lum < 0.013:
            return "rgba(255,255,255,0.12)", f"too dim (lum {lum:.4f}) -> rgba(255,255,255,0.12)"
        return None, ""

    rgba = parse_rgba(value)
    if rgba:
        r, g, b, a = rgba
        if r >= 200 and g >= 200 and b >= 200 and a < 0.12:
            return rgba_str(r, g, b, 0.12), f"alpha {a} -> 0.12"
        return None, ""

    return None, ""


# ---------------------------------------------------------------------------
# Phase 2: CSS Rule Font-Size Fixes
# ---------------------------------------------------------------------------

# Selector pattern -> minimum px, checked in order (first match wins)
_SELECTOR_MINIMUMS: list[tuple[re.Pattern[str], int, str]] = [
    # Card body text
    (re.compile(r"\.card\s+p|\.card\s+li|\.card\s+\.desc", re.I), 16, "card body text"),
    # Card titles
    (re.compile(r"\.card\s+h[3-6]|\.card-title", re.I), 18, "card titles"),
    # Grid cell descriptions
    (re.compile(r"\.pillar\s+p|\.pillar\s+\.desc|\.attack.*\s+p", re.I), 14, "grid cell descriptions"),
    # Grid cell titles
    (re.compile(r"\.pillar\s+h[3-6]|\.attack.*\s+h[3-6]", re.I), 16, "grid cell titles"),
    # Icons
    (re.compile(r"icon|emoji|\.attack.*icon", re.I), 28, "icons"),
    # Table headers
    (re.compile(r"\bth\b", re.I), 12, "table headers"),
    # Table cells
    (re.compile(r"\btd\b", re.I), 14, "table cells"),
    # Flow / step details
    (re.compile(r"\.flow.*detail|\.step.*detail", re.I), 14, "flow step details"),
    # Section labels
    (re.compile(r"\.slide-label|\.section-label", re.I), 12, "section labels"),
    # General body text (broad match -- checked last)
    (re.compile(r"\bp\b|\bli\b|\bspan\b", re.I), 14, "general body text"),
]

_FONT_SIZE_PROP_RE = re.compile(r"(font-size\s*:\s*)(\d+(?:\.\d+)?)\s*px\s*;")
_MEDIA_BLOCK_RE = re.compile(r"@media[^{]*\{", re.DOTALL)


def _find_media_ranges(css: str) -> list[tuple[int, int]]:
    """Find character ranges occupied by @media blocks (to skip them)."""
    ranges: list[tuple[int, int]] = []
    for m in _MEDIA_BLOCK_RE.finditer(css):
        start = m.start()
        depth = 1
        pos = m.end()
        while pos < len(css) and depth > 0:
            if css[pos] == "{":
                depth += 1
            elif css[pos] == "}":
                depth -= 1
            pos += 1
        ranges.append((start, pos))
    return ranges


def _in_media(pos: int, media_ranges: list[tuple[int, int]]) -> bool:
    for s, e in media_ranges:
        if s <= pos < e:
            return True
    return False


def _extract_style_blocks(html: str) -> list[tuple[int, int]]:
    """Return (start, end) of content inside each <style>...</style>."""
    blocks = []
    for m in re.finditer(r"<style[^>]*>(.*?)</style>", html, re.DOTALL):
        blocks.append((m.start(1), m.end(1)))
    return blocks


def phase2_css_rules(html: str) -> tuple[str, list[Change]]:
    """Fix font-size values in CSS rules (outside @media blocks)."""
    changes: list[Change] = []

    style_blocks = _extract_style_blocks(html)
    if not style_blocks:
        return html, changes

    # We work on the full HTML but only touch ranges inside <style> tags.
    # Process blocks from last to first so replacements don't shift offsets.
    for css_start, css_end in reversed(style_blocks):
        css_text = html[css_start:css_end]
        media_ranges = _find_media_ranges(css_text)
        new_css = css_text

        # Walk through CSS rule blocks: selector { body }
        # We need to be careful to handle nested @media braces, so we use a
        # simple state machine instead of a single regex.
        rule_re = re.compile(r"([^{}@]+?)\{([^}]*)\}", re.DOTALL)
        replacements: list[tuple[str, str]] = []  # (old_fragment, new_fragment)

        for rule_m in rule_re.finditer(css_text):
            if _in_media(rule_m.start(), media_ranges):
                continue

            selector = rule_m.group(1).strip()
            body = rule_m.group(2)

            for fs_m in _FONT_SIZE_PROP_RE.finditer(body):
                px_val = float(fs_m.group(2))

                min_px = 0
                reason = ""
                for pattern, threshold, desc in _SELECTOR_MINIMUMS:
                    if pattern.search(selector):
                        min_px = threshold
                        reason = desc
                        break

                if min_px > 0 and px_val < min_px:
                    old_fragment = fs_m.group(0)  # e.g. "font-size: 12px;"
                    new_fragment = f"{fs_m.group(1)}{min_px}px;"
                    replacements.append((old_fragment, new_fragment))
                    changes.append(Change(
                        phase="css-rule",
                        category="font-size",
                        location=selector,
                        old_value=f"{fs_m.group(2)}px",
                        new_value=f"{min_px}px",
                        detail=f"minimum {min_px}px for {reason}",
                    ))

        # Apply replacements (each is unique enough in context)
        for old_frag, new_frag in replacements:
            new_css = new_css.replace(old_frag, new_frag, 1)

        if new_css != css_text:
            html = html[:css_start] + new_css + html[css_end:]

    return html, changes


# ---------------------------------------------------------------------------
# Phase 3: Inline Style Fixes
# ---------------------------------------------------------------------------

_STYLE_ATTR_RE = re.compile(r'style="([^"]*)"')
_INLINE_FONTSIZE_RE = re.compile(r"(font-size\s*:\s*)(\d+(?:\.\d+)?)\s*px")
_INLINE_COLOR_RE = re.compile(
    r"(?<![a-z-])color\s*:\s*(#(?:[0-9a-fA-F]{3}){1,2}|rgba?\([^)]+\))"
)
_INLINE_OPACITY_RE = re.compile(r"(opacity\s*:\s*)([0-9.]+)")
_ICON_CONTEXT_RE = re.compile(r'class="[^"]*icon[^"]*"', re.I)


def phase3_inline_styles(html: str) -> tuple[str, list[Change]]:
    """Fix inline style attributes."""
    changes: list[Change] = []
    inline_count = 0

    def _fix_one(m: re.Match[str]) -> str:
        nonlocal inline_count
        inline_count += 1
        style = m.group(1)
        original_style = style

        # Check surrounding context for icon hints
        ctx_start = max(0, m.start() - 200)
        context = html[ctx_start:m.start()]
        is_icon = bool(_ICON_CONTEXT_RE.search(context)) or "icon" in style.lower()

        # --- Fix inline font-size ---
        fs_m = _INLINE_FONTSIZE_RE.search(style)
        if fs_m:
            px = float(fs_m.group(2))
            min_px = 28 if is_icon else 14
            if px < min_px:
                style = style[:fs_m.start()] + f"{fs_m.group(1)}{min_px}px" + style[fs_m.end():]
                changes.append(Change(
                    phase="inline", category="font-size",
                    location="inline",
                    old_value=f"{fs_m.group(2)}px", new_value=f"{min_px}px",
                    detail=f"inline font-size below {min_px}px minimum",
                ))

        # --- Fix inline text color ---
        color_m = _INLINE_COLOR_RE.search(style)
        if color_m:
            color_val = color_m.group(1).strip()
            new_color = _fix_inline_text_color(color_val)
            if new_color:
                style = style.replace(color_val, new_color, 1)
                changes.append(Change(
                    phase="inline", category="color",
                    location="inline",
                    old_value=color_val, new_value=new_color,
                    detail="inline color below WCAG AA contrast",
                ))

        # --- Fix inline opacity ---
        op_m = _INLINE_OPACITY_RE.search(style)
        if op_m:
            opacity = float(op_m.group(2))
            if opacity < 0.5:
                style = style[:op_m.start()] + f"{op_m.group(1)}0.5" + style[op_m.end():]
                changes.append(Change(
                    phase="inline", category="opacity",
                    location="inline",
                    old_value=str(opacity), new_value="0.5",
                    detail=f"opacity {opacity} -> 0.5",
                ))

        if style != original_style:
            return f'style="{style}"'
        return m.group(0)

    html = _STYLE_ATTR_RE.sub(_fix_one, html)

    if inline_count > 0:
        changes.append(Change(
            phase="inline", category="info",
            location="deck",
            old_value=str(inline_count), new_value=str(inline_count),
            detail=f"{inline_count} inline style attributes total",
        ))

    return html, changes


def _fix_inline_text_color(value: str) -> str | None:
    """Fix an inline text color for contrast. Returns new value or None."""
    if _HEX_COLOR_RE.match(value):
        r, g, b = parse_hex(value)
        lum = relative_luminance(r, g, b)
        cr = contrast_ratio(lum, 0.0)
        if cr < 4.5:
            return brighten_hex_to_contrast(value, 4.5)
        return None

    rgba = parse_rgba(value)
    if rgba:
        r, g, b, a = rgba
        if a < 0.5:
            return rgba_str(r, g, b, 0.5)
        eff_r, eff_g, eff_b = int(r * a), int(g * a), int(b * a)
        lum = relative_luminance(eff_r, eff_g, eff_b)
        cr = contrast_ratio(lum, 0.0)
        if cr < 4.5 and a < 0.85:
            for test_a_int in range(int(a * 100), 101):
                test_a = test_a_int / 100.0
                er, eg, eb = int(r * test_a), int(g * test_a), int(b * test_a)
                if contrast_ratio(relative_luminance(er, eg, eb), 0.0) >= 4.5:
                    return rgba_str(r, g, b, test_a)
        return None

    return None


# ---------------------------------------------------------------------------
# Phase 4: Inject Missing CSS Variables
# ---------------------------------------------------------------------------

_SURFACE_VARS = [
    "--surface-1",
    "--surface-2",
    "--surface-3",
    "--border-subtle",
    "--text-primary",
    "--text-readable",
    "--text-muted-floor",
]

_INJECT_BLOCK = """
    /* Surface hierarchy (injected by deck-style-fix) */
    --surface-1: rgba(255,255,255,0.06);
    --surface-2: rgba(255,255,255,0.10);
    --surface-3: rgba(255,255,255,0.15);
    --border-subtle: rgba(255,255,255,0.12);
    --text-primary: #ffffff;
    --text-readable: rgba(255,255,255,0.7);
    --text-muted-floor: rgba(255,255,255,0.5);
"""


def phase4_inject_missing(html: str) -> tuple[str, list[Change]]:
    """Inject surface hierarchy variables if ALL are missing from :root."""
    changes: list[Change] = []

    root_match = _ROOT_BLOCK_RE.search(html)
    if not root_match:
        return html, changes  # No :root -- don't create one

    root_body = root_match.group(2)

    # If ANY of the surface vars already exist, don't inject
    for var in _SURFACE_VARS:
        # Match "  --surface-1:" or "--surface-1 :" etc.
        if re.search(re.escape(var) + r"\s*:", root_body):
            return html, changes

    # Inject before the closing brace
    new_body = root_body.rstrip() + "\n" + _INJECT_BLOCK
    old_root = root_match.group(0)
    new_root = root_match.group(1) + new_body + root_match.group(3)
    html = html.replace(old_root, new_root, 1)

    changes.append(Change(
        phase="inject", category="inject",
        location=":root",
        old_value="(none)", new_value="surface hierarchy",
        detail=f"injected {len(_SURFACE_VARS)} surface hierarchy variables",
    ))

    return html, changes


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def fix_deck(html: str) -> tuple[str, list[Change]]:
    """Run all 4 fix phases on an HTML deck string."""
    changes: list[Change] = []
    html, c = phase1_css_variables(html);  changes.extend(c)
    html, c = phase2_css_rules(html);      changes.extend(c)
    html, c = phase3_inline_styles(html);  changes.extend(c)
    html, c = phase4_inject_missing(html); changes.extend(c)
    return html, changes


# ---------------------------------------------------------------------------
# Reporting / output formatting
# ---------------------------------------------------------------------------

def _is_fixable(c: Change) -> bool:
    return c.category != "info"


def _format_change(c: Change) -> str:
    if c.category == "info":
        return f"  [INLINE] {c.detail}"
    if c.category == "inject":
        return f"  [INJECT] {c.detail}"
    cat = c.category.upper()
    return f"  [{cat}] {c.location}: {c.old_value} -> {c.new_value} ({c.detail})"


def report_issues(filepath: str, changes: list[Change]) -> str:
    """Format --report output."""
    fixable = [c for c in changes if _is_fixable(c)]
    infos = [c for c in changes if c.category == "info"]
    total = len(fixable) + len(infos)
    lines = [f"{filepath}:"]
    lines.append(f"  ISSUES: {total}")
    for c in fixable:
        lines.append(f"    - {_format_change(c).strip()}")
    for c in infos:
        lines.append(f"    - {_format_change(c).strip()}")
    return "\n".join(lines)


def report_dryrun(filepath: str, changes: list[Change]) -> str:
    """Format --dry-run output."""
    fixable = [c for c in changes if _is_fixable(c)]
    infos = [c for c in changes if c.category == "info"]
    lines = [f"{filepath}:"]
    lines.append(f"  WOULD FIX: {len(fixable)} issues")
    for c in fixable:
        lines.append(f"    {_format_change(c).strip()}")
    if infos:
        lines.append(f"  REMAINING: {len(infos)} issues (manual review needed)")
        for c in infos:
            lines.append(f"    {_format_change(c).strip()}")
    return "\n".join(lines)


def report_verbose(filepath: str, changes: list[Change]) -> str:
    """Format --verbose output."""
    fixable = [c for c in changes if _is_fixable(c)]
    infos = [c for c in changes if c.category == "info"]
    lines = [f"{filepath}: FIXED {len(fixable)} issues ({len(infos)} remaining)"]
    for c in changes:
        lines.append(_format_change(c))
    return "\n".join(lines)


def report_normal(filepath: str, changes: list[Change]) -> str:
    """Format default output."""
    fixable = [c for c in changes if _is_fixable(c)]
    infos = [c for c in changes if c.category == "info"]
    return f"{filepath}: FIXED {len(fixable)} issues ({len(infos)} remaining)"


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic CSS accessibility fixer for HTML presentation decks.",
        usage="python deck-style-fix.py FILE [FILE...] [OPTIONS]",
    )
    parser.add_argument(
        "files", nargs="+", metavar="FILE",
        help="HTML file(s) to process",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without modifying files",
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Only report issues, don't fix anything",
    )
    parser.add_argument(
        "--backup", action="store_true",
        help="Create .bak files before modifying (default: no backup)",
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Show detailed change log",
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Only show summary counts",
    )

    args = parser.parse_args()

    total_fixed = 0
    total_remaining = 0
    files_processed = 0

    for filepath in args.files:
        if not os.path.isfile(filepath):
            print(f"ERROR: {filepath}: not found", file=sys.stderr)
            continue

        html = Path(filepath).read_text(encoding="utf-8")
        new_html, changes = fix_deck(html)

        fixable = [c for c in changes if _is_fixable(c)]
        infos = [c for c in changes if c.category == "info"]
        total_fixed += len(fixable)
        total_remaining += len(infos)
        files_processed += 1

        if args.report:
            if not args.quiet:
                print(report_issues(filepath, changes))
                print()
        elif args.dry_run:
            if not args.quiet:
                print(report_dryrun(filepath, changes))
                print()
        else:
            # Actually write the file
            if new_html != html:
                if args.backup:
                    shutil.copy2(filepath, filepath + ".bak")
                Path(filepath).write_text(new_html, encoding="utf-8")

            if not args.quiet:
                if args.verbose:
                    print(report_verbose(filepath, changes))
                else:
                    print(report_normal(filepath, changes))

    if args.quiet or files_processed > 1:
        mode = "reported" if (args.report or args.dry_run) else "fixed"
        print(f"\nProcessed {files_processed} files: "
              f"{total_fixed} issues {mode}, {total_remaining} remaining")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
