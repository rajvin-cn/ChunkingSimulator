from __future__ import annotations
import json
from typing import Any

# ═══════════════════════════════════════════════════════════════
# Color System — layered dark, clear depth, professional palette
# ═══════════════════════════════════════════════════════════════

COLORS = {
    "primary":        "#3B82F6",   # Blue-500 — global accent
    "primary_hover":  "#2563EB",   # Blue-600
    "primary_subtle": "#1E3A5F",   # Blue at ~15% on dark

    "success":  "#10B981",  # Emerald-500
    "warning":  "#F59E0B",  # Amber-500
    "error":    "#EF4444",  # Red-500
    "info":     "#3B82F6",

    # Surfaces — layered gray (depth through luminosity steps)
    "bg":                "#0C0E12",  # Deepest page bg
    "surface":           "#161921",  # Cards / containers
    "surface_raised":    "#1C2030",  # Hovered cards / elevated
    "surface_overlay":   "#242836",  # Details / summary panels

    # Sidebar
    "sidebar":           "#111318",
    "sidebar_hover":     "#1A1D26",

    # Borders — consistent system
    "border":            "#262A36",
    "border_light":      "#2E3340",
    "border_focus":      "#3B82F6",

    # Text — warm white scale
    "text":              "#EDF2F9",
    "text_secondary":    "#9CA3AF",
    "text_muted":        "#6B7280",
    "text_inverse":      "#0C0E12",
}

# ═══════════════════════════════════════════════════════════════
# Strategy colors — used ONLY for strategy badges / indicators
# ═══════════════════════════════════════════════════════════════

STRATEGY_COLORS = {
    "semantic":      "#3B82F6",  # Blue
    "hierarchical":  "#10B981",  # Green
    "late":          "#A855F7",  # Purple
    "compare":       "#F59E0B",  # Amber
}

STRATEGY_LABELS = {
    "semantic":      "Semantic",
    "hierarchical":  "Hierarchical",
    "late":          "Late",
    "compare":       "Compare",
}

# ═══════════════════════════════════════════════════════════════
# Typography Tokens — consistent, reusable, rem-based
# ═══════════════════════════════════════════════════════════════

TYP = {
    "h1":       "font-size:1.85rem;font-weight:700;line-height:1.25;letter-spacing:-0.02em;",
    "h2":       "font-size:1.35rem;font-weight:600;line-height:1.3;",
    "h3":       "font-size:1.05rem;font-weight:600;line-height:1.35;",
    "body":     "font-size:0.9rem;line-height:1.65;",
    "small":    "font-size:0.8rem;line-height:1.5;",
    "caption":  "font-size:0.72rem;line-height:1.4;",
    "overline": "font-size:0.64rem;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;",
    "mono":     "font-size:0.82rem;line-height:1.6;font-family:'JetBrains Mono','Fira Code',monospace;",
    "value":    "font-size:1.5rem;font-weight:700;line-height:1.2;letter-spacing:-0.01em;",
}

# ═══════════════════════════════════════════════════════════════
# Icon System — inline Lucide-style SVGs, currentColor inherited
# ═══════════════════════════════════════════════════════════════

_ICON_PATHS: dict[str, str] = {
    "file-text": (
        '<path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>'
        '<polyline points="14 2 14 8 20 8"/>'
        '<line x1="16" y1="13" x2="8" y2="13"/>'
        '<line x1="16" y1="17" x2="8" y2="17"/>'
    ),
    "git-branch": (
        '<line x1="6" y1="3" x2="6" y2="15"/>'
        '<circle cx="6" cy="18" r="3"/>'
        '<path d="M6 15V9a9 9 0 019-9"/>'
        '<circle cx="18" cy="3" r="3"/>'
    ),
    "brain": (
        '<path d="M12 4a2.5 2.5 0 00-2.5 2.5c0 .5.1 1 .3 1.4a3.5 3.5 0 00-2 4.8 3.5 3.5 0 00.5 5.6A3.5 3.5 0 0012 21a3.5 3.5 0 003.7-2.7 3.5 3.5 0 00.5-5.6 3.5 3.5 0 00-2-4.8c.2-.4.3-.9.3-1.4A2.5 2.5 0 0012 4z"/>'
        '<path d="M14.5 11.5a4 4 0 01-2.5 3 4 4 0 01-2.5-3"/>'
        '<path d="M12 6v2"/>'
    ),
    "layers": (
        '<polygon points="12 2 22 8.5 12 15 2 8.5 12 2"/>'
        '<polyline points="2 15.5 12 22 22 15.5"/>'
    ),
    "zap": (
        '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>'
    ),
    "wrench": (
        '<path d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 01-3-3l6.91-6.91a6 6 0 017.94-7.94l-3.76 3.76z"/>'
    ),
    "play": (
        '<polygon points="6 3 20 12 6 21 6 3"/>'
    ),
    "refresh-cw": (
        '<polyline points="23 4 23 10 17 10"/>'
        '<polyline points="1 20 1 14 7 14"/>'
        '<path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>'
    ),
    "bar-chart-3": (
        '<path d="M3 3v18h18"/>'
        '<path d="M18 7v7"/>'
        '<path d="M13 10v4"/>'
        '<path d="M8 13v1"/>'
    ),
    "settings": (
        '<path d="M12.22 2h-.44a2 2 0 00-2 2v.18a2 2 0 01-1 1.73l-.43.25a2 2 0 01-2 0l-.15-.08a2 2 0 00-2.73.73l-.22.38a2 2 0 00.73 2.73l.15.1a2 2 0 011 1.72v.51a2 2 0 01-1 1.74l-.15.09a2 2 0 00-.73 2.73l.22.38a2 2 0 002.73.73l.15-.08a2 2 0 012 0l.43.25a2 2 0 011 1.73V20a2 2 0 002 2h.44a2 2 0 002-2v-.18a2 2 0 011-1.73l.43-.25a2 2 0 012 0l.15.08a2 2 0 002.73-.73l.22-.39a2 2 0 00-.73-2.73l-.15-.08a2 2 0 01-1-1.74v-.5a2 2 0 011-1.74l.15-.09a2 2 0 00.73-2.73l-.22-.38a2 2 0 00-2.73-.73l-.15.08a2 2 0 01-2 0l-.43-.25a2 2 0 01-1-1.73V4a2 2 0 00-2-2z"/>'
        '<circle cx="12" cy="12" r="3"/>'
    ),
    "hash": (
        '<line x1="4" y1="9" x2="20" y2="9"/>'
        '<line x1="4" y1="15" x2="20" y2="15"/>'
        '<line x1="10" y1="3" x2="8" y2="21"/>'
        '<line x1="16" y1="3" x2="14" y2="21"/>'
    ),
    "info": (
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="12" y1="16" x2="12" y2="12"/>'
        '<line x1="12" y1="8" x2="12.01" y2="8"/>'
    ),
    "check-circle": (
        '<path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>'
        '<polyline points="22 4 12 14.01 9 11.01"/>'
    ),
    "alert-triangle": (
        '<path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>'
        '<line x1="12" y1="9" x2="12" y2="13"/>'
        '<line x1="12" y1="17" x2="12.01" y2="17"/>'
    ),
    "chevron-down": (
        '<polyline points="6 9 12 15 18 9"/>'
    ),
    "arrow-right": (
        '<line x1="5" y1="12" x2="19" y2="12"/>'
        '<polyline points="12 5 19 12 12 19"/>'
    ),
    "chevrons-down": (
        '<polyline points="7 13 12 18 17 13"/>'
        '<polyline points="7 6 12 11 17 6"/>'
    ),
    "split": (
        '<path d="M16 3h5v5"/>'
        '<path d="M8 3H3v5"/>'
        '<path d="M12 3v18"/>'
    ),
    "cpu": (
        '<rect x="4" y="4" width="16" height="16" rx="2"/>'
        '<rect x="9" y="9" width="6" height="6"/>'
        '<line x1="9" y1="1" x2="9" y2="4"/>'
        '<line x1="15" y1="1" x2="15" y2="4"/>'
        '<line x1="9" y1="20" x2="9" y2="23"/>'
        '<line x1="15" y1="20" x2="15" y2="23"/>'
        '<line x1="20" y1="9" x2="23" y2="9"/>'
        '<line x1="20" y1="14" x2="23" y2="14"/>'
        '<line x1="1" y1="9" x2="4" y2="9"/>'
        '<line x1="1" y1="14" x2="4" y2="14"/>'
    ),
    "search": (
        '<circle cx="11" cy="11" r="8"/>'
        '<line x1="21" y1="21" x2="16.65" y2="16.65"/>'
    ),
    "database": (
        '<ellipse cx="12" cy="5" rx="9" ry="3"/>'
        '<path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>'
        '<path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>'
    ),
    "scissors": (
        '<circle cx="6" cy="6" r="3"/>'
        '<circle cx="6" cy="18" r="3"/>'
        '<line x1="20" y1="4" x2="8.12" y2="15.88"/>'
        '<line x1="14.47" y1="14.48" x2="20" y2="20"/>'
    ),
    "target": (
        '<circle cx="12" cy="12" r="10"/>'
        '<circle cx="12" cy="12" r="6"/>'
        '<circle cx="12" cy="12" r="2"/>'
    ),
    "package": (
        '<path d="M20.91 8.84L12 3.5 3.09 8.84l8.91 5.34 8.91-5.34z"/>'
        '<path d="M21 12v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6"/>'
        '<path d="M12 14.18V21"/>'
    ),
    "globe": (
        '<circle cx="12" cy="12" r="10"/>'
        '<line x1="2" y1="12" x2="22" y2="12"/>'
        '<path d="M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/>'
    ),
    "list": (
        '<line x1="8" y1="6" x2="21" y2="6"/>'
        '<line x1="8" y1="12" x2="21" y2="12"/>'
        '<line x1="8" y1="18" x2="21" y2="18"/>'
        '<line x1="3" y1="6" x2="3.01" y2="6"/>'
        '<line x1="3" y1="12" x2="3.01" y2="12"/>'
        '<line x1="3" y1="18" x2="3.01" y2="18"/>'
    ),
    "link": (
        '<path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71"/>'
        '<path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71"/>'
    ),
    "copy": (
        '<rect x="9" y="9" width="13" height="13" rx="2"/>'
        '<path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>'
    ),
    "x": (
        '<line x1="18" y1="6" x2="6" y2="18"/>'
        '<line x1="6" y1="6" x2="18" y2="18"/>'
    ),
    "plus": (
        '<line x1="12" y1="5" x2="12" y2="19"/>'
        '<line x1="5" y1="12" x2="19" y2="12"/>'
    ),
    "folder": (
        '<path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/>'
    ),
    "user": (
        '<path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>'
        '<circle cx="12" cy="7" r="4"/>'
    ),
    "external-link": (
        '<path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/>'
        '<polyline points="15 3 21 3 21 9"/>'
        '<line x1="10" y1="14" x2="21" y2="3"/>'
    ),
}


def icon(name: str, size: int = 18) -> str:
    """Return an inline SVG icon that inherits color via currentColor."""
    paths = _ICON_PATHS.get(name, "")
    if not paths:
        return ""
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" '
        f'fill="none" stroke="currentColor" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'style="vertical-align:middle;flex-shrink:0;">{paths}</svg>'
    )


# ═══════════════════════════════════════════════════════════════
# Global CSS — injected once per page
# ═══════════════════════════════════════════════════════════════

GLOBAL_CSS = f"""
<style>
/* ── Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
body, .stApp {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {COLORS["border"]}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {COLORS["border_light"]}; }}

/* ── Expanders ── */
.stExpander {{ border-radius: 10px !important; }}
.stExpander .streamlit-expanderHeader {{
    background: {COLORS["surface"]} !important;
    border: 1px solid {COLORS["border"]} !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}}

/* ── Buttons ── */
.stButton button {{
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
}}
button[kind="primary"] {{
    background: {COLORS["primary"]} !important;
    border-color: {COLORS["primary"]} !important;
    color: #fff !important;
}}
button[kind="primary"]:hover {{
    background: {COLORS["primary_hover"]} !important;
    border-color: {COLORS["primary_hover"]} !important;
}}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: {COLORS["sidebar"]} !important;
}}
section[data-testid="stSidebar"] hr {{
    border-color: {COLORS["border"]} !important;
}}

/* ── Dividers ── */
hr {{ border-color: {COLORS["border"]} !important; }}

/* ── Progress bar base ── */
.stProgress > div > div > div > div {{
    transition: background 0.3s ease !important;
}}

/* ── Card shadows & hover (class-based) ── */
.card-hover {{
    box-shadow: 0 1px 2px rgba(0,0,0,0.25);
    transition: box-shadow 0.2s ease, transform 0.2s ease, border-color 0.2s ease;
}}
.card-hover:hover {{
    box-shadow: 0 6px 16px rgba(0,0,0,0.4);
    transform: translateY(-2px);
}}

/* ── Radio buttons ── */
div[role="radiogroup"] label {{
    padding: 6px 16px !important;
    border-radius: 8px !important;
}}

/* ── Info / success / warning / error boxes ── */
div[data-testid="stAlert"] {{
    border-radius: 8px !important;
}}

/* ── Code blocks ── */
code {{
    font-size: 0.82em !important;
}}
</style>
"""


def progress_bar_css(color: str) -> str:
    """Return a <style> block that sets the progress bar to *color*."""
    return f"<style>.stProgress > div > div > div > div {{ background: {color} !important; }}</style>"


# ═══════════════════════════════════════════════════════════════
# HTML Escape Helpers
# ═══════════════════════════════════════════════════════════════

def _safe(text: str) -> str:
    return (text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))


def _escape_pre(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ═══════════════════════════════════════════════════════════════
# JSON Syntax Highlighting
# ═══════════════════════════════════════════════════════════════

def _render_json_value(v: Any, indent: int = 0) -> str:
    pad = "   " * indent
    if isinstance(v, dict):
        if not v:
            return "{}"
        items = [f"{pad}{{"]
        for i, (k, val) in enumerate(v.items()):
            key_colored = f'{pad}   <span style="color:#7DD3FC;">"{_escape_pre(str(k))}"</span><span style="color:#64748B;">:</span>'
            val_colored = _render_json_value(val, indent + 1)
            comma = '<span style="color:#64748B;">,</span>' if i < len(v) - 1 else ""
            items.append(f"{key_colored}{val_colored}{comma}")
        items.append(f"{pad}}}")
        return "<br>".join(items)
    elif isinstance(v, list):
        if not v:
            return "[]"
        items = [f"{pad}["]
        for i, item in enumerate(v):
            val_colored = _render_json_value(item, indent + 1)
            comma = '<span style="color:#64748B;">,</span>' if i < len(v) - 1 else ""
            items.append(f"{pad}   {val_colored}{comma}")
        items.append(f"{pad}]")
        return "<br>".join(items)
    elif isinstance(v, str):
        safe = _escape_pre(v)
        return f'<span style="color:#A5D6A7;">"{safe}"</span>'
    elif isinstance(v, bool):
        return f'<span style="color:#C4B5FD;font-weight:500;">{"true" if v else "false"}</span>'
    elif isinstance(v, (int, float)):
        return f'<span style="color:#FECDD3;">{v}</span>'
    elif v is None:
        return f'<span style="color:#C4B5FD;font-weight:500;">null</span>'
    return _escape_pre(str(v))


def syntax_highlight_json(json_str: str) -> str:
    try:
        data = json.loads(json_str)
        return _render_json_value(data)
    except json.JSONDecodeError:
        return _escape_pre(json_str)


# ═══════════════════════════════════════════════════════════════
# Component: Badge
# ═══════════════════════════════════════════════════════════════

def badge_html(text: str, color: str, *, icon_name: str = "", variant: str = "filled") -> str:
    """Unified badge/chip component.
    variant: 'filled' (solid bg at 15% opacity) or 'outline' (transparent w/ border).
    """
    if variant == "outline":
        style = (
            f"display:inline-flex;align-items:center;gap:5px;"
            f"padding:2px 10px;border-radius:12px;font-size:0.7rem;font-weight:600;"
            f"color:{color};border:1px solid {color}40;"
        )
    else:
        style = (
            f"display:inline-flex;align-items:center;gap:5px;"
            f"padding:2px 10px;border-radius:12px;font-size:0.7rem;font-weight:600;"
            f"background:{color}18;color:{color};"
        )
    icon_svg = icon(icon_name, 14) if icon_name else ""
    return f'<span style="{style}">{icon_svg}{text}</span>'


# ═══════════════════════════════════════════════════════════════
# Component: Page Header
# ═══════════════════════════════════════════════════════════════

def page_header_html(title: str, subtitle: str = "", *, icon_name: str = "", accent: str = "") -> str:
    """Consistent page hero used on every page."""
    c = accent or COLORS["primary"]
    icon_svg = icon(icon_name, 28) if icon_name else ""
    icon_block = ""
    if icon_svg:
        icon_block = (
            f'<div style="width:48px;height:48px;border-radius:12px;'
            f'background:{c}18;display:flex;align-items:center;justify-content:center;'
            f'flex-shrink:0;color:{c};">{icon_svg}</div>'
        )
    parts = [f'<div style="display:flex;align-items:center;gap:16px;margin-bottom:4px;">']
    if icon_block:
        parts.append(icon_block)
    parts.append(
        f'<div>'
        f'<h1 style="{TYP["h1"]}color:{COLORS["text"]};margin:0;">{title}</h1>'
    )
    if subtitle:
        parts.append(
            f'<p style="{TYP["small"]}color:{COLORS["text_secondary"]};margin:4px 0 0 0;">{subtitle}</p>'
        )
    parts.append('</div></div>')
    return "".join(parts)


# ═══════════════════════════════════════════════════════════════
# Component: Metric Card
# ═══════════════════════════════════════════════════════════════

def metric_card_html(value: str, label: str, *, icon_name: str = "", color: str = "") -> str:
    """Individual metric card with icon, large value, and label."""
    c = color or COLORS["primary"]
    icon_svg = icon(icon_name, 22) if icon_name else ""
    icon_block = ""
    if icon_svg:
        icon_block = (
            f'<div style="margin-bottom:6px;color:{c};">{icon_svg}</div>'
        )
    return (
        f'<div class="card-hover" style="background:{COLORS["surface"]};'
        f'border:1px solid {COLORS["border"]};border-radius:10px;'
        f'padding:16px 18px;text-align:center;flex:1;min-width:110px;">'
        f'{icon_block}'
        f'<div style="{TYP["value"]}color:{c};">{value}</div>'
        f'<div style="{TYP["caption"]}color:{COLORS["text_muted"]};margin-top:4px;">{label}</div>'
        f'</div>'
    )


# ═══════════════════════════════════════════════════════════════
# Component: Metric Summary (row of metric cards)
# ═══════════════════════════════════════════════════════════════

_METRIC_ICONS = {
    "Total Chunks": "layers",
    "Total Tokens": "hash",
    "Topic Shifts": "git-branch",
    "Token Cap Hits": "alert-triangle",
    "Parents": "folder",
    "Children": "file-text",
    "Avg Tokens": "bar-chart-3",
}

def metric_summary_html(metrics: list[tuple[str, str, str]], strategy: str = "semantic") -> str:
    """Render a row of metric cards. Each metric = (value, label, tooltip)."""
    color = STRATEGY_COLORS.get(strategy, COLORS["primary"])
    cards = []
    for value, label, _tooltip in metrics:
        ico = _METRIC_ICONS.get(label, "")
        cards.append(metric_card_html(value, label, icon_name=ico, color=color))
    return (
        f'<div style="display:flex;gap:10px;flex-wrap:wrap;margin:16px 0;">'
        f'{"".join(cards)}</div>'
    )


# ═══════════════════════════════════════════════════════════════
# Component: Step Header
# ═══════════════════════════════════════════════════════════════

def step_header_html(
    number: int,
    title: str,
    status: str,
    accent: str = "",
    icon_name: str = "",
) -> str:
    """
    Three states:
      'completed' — green dot + checkmark, green left border, full text
      'active'    — accent dot + number, accent left border, full text
      'upcoming'  — muted dot + number, muted border, dim text (min opacity 0.65)
    """
    accent = accent or COLORS["primary"]

    if status == "completed":
        dot_bg = COLORS["success"]
        dot_text = "&#10003;"  # ✓
        border = COLORS["success"]
        label_color = COLORS["text"]
        opacity = "1"
    elif status == "active":
        dot_bg = accent
        dot_text = str(number)
        border = accent
        label_color = COLORS["text"]
        opacity = "1"
    else:
        dot_bg = COLORS["text_muted"]
        dot_text = str(number)
        border = COLORS["border"]
        label_color = COLORS["text_secondary"]
        opacity = "0.65"  # still readable (was 0.5)

    icon_svg = icon(icon_name, 18) if icon_name else ""

    return (
        f'<div style="display:flex;align-items:center;gap:14px;'
        f'border-left:3px solid {border};padding:12px 0 12px 18px;'
        f'margin:24px 0 14px 0;opacity:{opacity};'
        f'background:{COLORS["surface"]};border-radius:0 10px 10px 0;'
        f'transition:opacity 0.2s ease,border-color 0.2s ease;">'
        f'<span style="width:36px;height:36px;border-radius:50%;background:{dot_bg};'
        f'color:#fff;display:inline-flex;align-items:center;justify-content:center;'
        f'font-size:15px;font-weight:700;flex-shrink:0;">{dot_text}</span>'
        f'<span style="{TYP["h3"]}color:{label_color};display:inline-flex;align-items:center;gap:8px;">'
        f'{icon_svg}{title}'
        f'</span>'
        f'</div>'
    )


# ═══════════════════════════════════════════════════════════════
# Component: Stepper (replaces ASCII breadcrumb)
# ═══════════════════════════════════════════════════════════════

def stepper_html(steps: list[str], done_mask: list[bool], accent: str = "") -> str:
    """Modern step indicator with SVG dots and connector lines."""
    accent = accent or COLORS["primary"]
    items: list[str] = []

    for i, (label, done) in enumerate(zip(steps, done_mask)):
        if done:
            # Completed: green circle with checkmark
            dot = (
                f'<span style="width:28px;height:28px;border-radius:50%;'
                f'background:{COLORS["success"]};color:#fff;display:inline-flex;'
                f'align-items:center;justify-content:center;font-size:13px;'
                f'font-weight:700;flex-shrink:0;">&#10003;</span>'
            )
            text_color = COLORS["text"]
            weight = "600"
        elif i == 0 or (i > 0 and done_mask[i - 1]):
            # Active: accent circle with number
            dot = (
                f'<span style="width:28px;height:28px;border-radius:50%;'
                f'background:{accent};color:#fff;display:inline-flex;'
                f'align-items:center;justify-content:center;font-size:13px;'
                f'font-weight:700;flex-shrink:0;">{i + 1}</span>'
            )
            text_color = COLORS["text"]
            weight = "600"
        else:
            # Upcoming: muted circle
            dot = (
                f'<span style="width:28px;height:28px;border-radius:50%;'
                f'background:{COLORS["border"]};color:{COLORS["text_muted"]};'
                f'display:inline-flex;align-items:center;justify-content:center;'
                f'font-size:13px;font-weight:600;flex-shrink:0;">{i + 1}</span>'
            )
            text_color = COLORS["text_muted"]
            weight = "400"

        items.append(
            f'<span style="display:inline-flex;align-items:center;gap:8px;">'
            f'{dot}'
            f'<span style="font-size:0.8rem;font-weight:{weight};color:{text_color};'
            f'white-space:nowrap;">{label}</span>'
            f'</span>'
        )

        if i < len(steps) - 1:
            line_color = COLORS["success"] if done else COLORS["border"]
            items.append(
                f'<span style="display:inline-flex;align-items:center;padding:0 6px;">'
                f'{icon("arrow-right", 14) if done else ""}'
                f'<span style="display:inline-block;width:20px;height:2px;'
                f'background:{line_color};border-radius:1px;'
                f'{"margin-left:4px;" if done else ""}"></span>'
                f'</span>'
            )

    return (
        f'<div style="display:flex;align-items:center;flex-wrap:wrap;gap:4px;'
        f'margin:8px 0 16px 0;padding:10px 18px;background:{COLORS["surface"]};'
        f'border-radius:10px;border:1px solid {COLORS["border"]};">'
        f'{"".join(items)}</div>'
    )


# Legacy alias
def breadcrumb_html(steps: list[str], done_mask: list[bool], strategy: str = "semantic") -> str:
    return stepper_html(steps, done_mask, STRATEGY_COLORS.get(strategy, COLORS["primary"]))


# ═══════════════════════════════════════════════════════════════
# Component: Scroll Container
# ═══════════════════════════════════════════════════════════════

def scroll_div(content: str, max_height: str = "500px") -> str:
    return (
        f'<div style="max-height:{max_height};overflow-y:auto;padding:16px;'
        f'border:1px solid {COLORS["border"]};border-radius:10px;'
        f'background:{COLORS["surface"]};">{content}</div>'
    )


# ═══════════════════════════════════════════════════════════════
# Component: Chunk Card (the hero component)
# ═══════════════════════════════════════════════════════════════

def _split_badge_html(badge: str | None, strategy_color: str = "") -> str:
    if not badge:
        return ""
    color_map = {
        "Topic Shift": strategy_color or COLORS["primary"],
        "Token Cap": COLORS["warning"],
        "End of Text": COLORS["text_muted"],
        "Parent": COLORS["success"],
        "Child": "#6366F1",
    }
    bg_color = color_map.get(badge, COLORS["text_muted"])
    ico = {
        "Topic Shift": "git-branch",
        "Token Cap": "alert-triangle",
        "Parent": "folder",
        "Child": "file-text",
    }.get(badge, "")
    return badge_html(badge, bg_color, icon_name=ico)


def chunk_card_html(
    idx: int,
    chunk_text: str,
    token_count: int,
    strategy: str = "semantic",
    extra_fields: dict[str, Any] | None = None,
    badge: str | None = None,
    tree: str | None = None,
) -> str:
    color = STRATEGY_COLORS.get(strategy, COLORS["primary"])
    label = STRATEGY_LABELS.get(strategy, strategy.capitalize())
    escaped = _safe(chunk_text)
    preview = escaped[:320] + ("..." if len(escaped) > 320 else "")

    if extra_fields is None:
        extra_fields = {}
    meta = {k: v for k, v in extra_fields.items() if k != "chunk_text"}
    meta["chunk_text"] = chunk_text
    extra_json = json.dumps(meta, indent=2)

    # Alternating background — subtle rhythm between cards
    _alt_surface = "#1A1E2A" if idx % 2 == 0 else COLORS["surface"]

    # Split badge block
    split_badge_markup = _split_badge_html(badge, strategy_color=color)

    # Card body
    card_body = (
        f'<div class="card-hover" style="background:{_alt_surface};'
        f'border-left:3px solid {color};'
        f'border-radius:8px;padding:10px 14px;margin-bottom:10px;'
        f'border-top:1px solid {COLORS["border"]};'
        f'border-right:1px solid {COLORS["border"]};'
        f'border-bottom:1px solid {COLORS["border"]};">'

        # Header row
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'
        f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">'
        f'{badge_html(f"Chunk {idx}", color, icon_name="layers" if strategy == "hierarchical" else "file-text")}'
        f'<span style="font-size:0.68rem;color:{COLORS["text_muted"]};">{token_count} tokens</span>'
        f'{split_badge_markup}'
        f'</div>'
        f'{badge_html(label, color, variant="outline")}'
        f'</div>'

        # Text preview
        f'<div style="color:{COLORS["text"]};font-size:0.78rem;line-height:1.55;'
        f'max-height:110px;overflow-y:auto;padding:4px 0;'
        f'word-wrap:break-word;word-break:break-word;">'
        f'{preview}</div>'

        # Expandable JSON details
        f'<details style="margin-top:6px;">'
        f'<summary style="color:{color};font-size:0.72rem;cursor:pointer;'
        f'padding:4px 0;font-weight:600;">'
        f'{icon("search", 14)} Inspect ChunkResult</summary>'
        f'<div style="background:{COLORS["surface_overlay"]};padding:12px;'
        f'border-radius:6px;font-size:0.72rem;color:{COLORS["text"]};'
        f'line-height:1.6;overflow-x:auto;font-family:monospace;'
        f'white-space:pre-wrap;max-height:300px;overflow-y:auto;'
        f'margin:6px 0 0 0;border:1px solid {COLORS["border"]};">'
        f'{syntax_highlight_json(extra_json)}</div>'
        f'</details>'

        f'</div>'
    )

    # Tree connectors (for hierarchical)
    if tree:
        is_last = tree == "end"
        vline_bottom = "22px" if is_last else "0"
        card_body = (
            f'<div style="display:flex;gap:6px;margin:14px 0 0 0;">'
            f'<div style="display:flex;flex-direction:column;align-items:center;'
            f'min-width:18px;flex-shrink:0;position:relative;">'
            f'<div style="position:absolute;top:0;bottom:{vline_bottom};left:50%;'
            f'width:2px;background:{color}30;transform:translateX(-50%);"></div>'
            f'<div style="position:absolute;top:22px;left:50%;width:12px;'
            f'height:2px;background:{color}60;"></div>'
            f'</div>'
            f'<div style="flex:1;min-width:0;">{card_body}</div>'
            f'</div>'
        )

    return card_body


# ═══════════════════════════════════════════════════════════════
# Component: Colored Log
# ═══════════════════════════════════════════════════════════════

def colored_log_html(log_entries: list[str]) -> str:
    lines = []
    for entry in log_entries:
        if "FLUSHED" in entry or "\u274c" in entry:
            color = COLORS["error"]
        elif "ADDED" in entry or "\u2705" in entry:
            color = COLORS["success"]
        elif "FINAL" in entry or "\U0001f4e6" in entry:
            color = COLORS["warning"]
        else:
            color = COLORS["text_muted"]
        lines.append(
            f'<div style="color:{color};font-size:0.76rem;padding:3px 0;'
            f'border-bottom:1px solid {COLORS["border"]};line-height:1.5;'
            f'font-family:monospace;">{entry}</div>'
        )
    return (
        f'<div style="max-height:260px;overflow-y:auto;padding-right:4px;">'
        f'{"".join(lines)}</div>'
    )


# ═══════════════════════════════════════════════════════════════
# Component: How It Works
# ═══════════════════════════════════════════════════════════════

def how_it_works_html(sections: list[dict], strategy: str = "semantic") -> str:
    color = STRATEGY_COLORS.get(strategy, COLORS["primary"])
    parts = [
        f'<div style="line-height:1.7;{TYP["small"]};border-left:3px solid {color};'
        f'padding-left:16px;">'
    ]
    for i, sec in enumerate(sections):
        parts.append(
            f'<div style="display:flex;align-items:baseline;gap:8px;'
            f'margin:10px 0 4px 0;">'
            f'<span style="width:22px;height:22px;border-radius:6px;background:{color}18;'
            f'color:{color};display:inline-flex;align-items:center;justify-content:center;'
            f'font-size:12px;font-weight:700;flex-shrink:0;">{i + 1}</span>'
            f'<span style="color:{color};font-weight:600;{TYP["small"]};">{sec["title"]}</span>'
            f'</div>'
        )
        parts.append(
            f'<div style="color:{COLORS["text_secondary"]};margin-left:30px;'
            f'margin-bottom:8px;">{sec["content"]}</div>'
        )
    parts.append("</div>")
    return "".join(parts)


# ═══════════════════════════════════════════════════════════════
# Component: Completion Arrow (divider between completed steps)
# ═══════════════════════════════════════════════════════════════

def completion_arrow_html() -> str:
    return (
        f'<div style="text-align:center;padding:4px 0;color:{COLORS["success"]};">'
        f'{icon("chevrons-down", 22)}</div>'
    )


# ═══════════════════════════════════════════════════════════════
# Component: Processing Overlay
# ═══════════════════════════════════════════════════════════════

def processing_overlay_html(message: str, color: str = "") -> str:
    """Stylized processing indicator — pulsing dot + message in strategy color."""
    c = color or COLORS["primary"]
    return (
        f'<div style="display:flex;align-items:center;gap:10px;'
        f'padding:10px 16px;background:{COLORS["surface"]};'
        f'border:1px solid {COLORS["border"]};border-radius:8px;'
        f'margin:4px 0;">'
        f'<span style="width:10px;height:10px;border-radius:50%;background:{c};'
        f'display:inline-block;animation:pulse 1.2s ease-in-out infinite;"></span>'
        f'<span style="color:{COLORS["text"]};font-size:0.85rem;font-weight:500;">{message}</span>'
        f'</div>'
        f'<style>@keyframes pulse {{ 0%,100%{{opacity:1;transform:scale(1);}} '
        f'50%{{opacity:0.4;transform:scale(0.85);}} }}</style>'
    )


# ═══════════════════════════════════════════════════════════════
# Component: Loading Placeholder
# ═══════════════════════════════════════════════════════════════

def loading_placeholder_html(message: str, color: str = "", submessage: str = "") -> str:
    """Centered loading card with ring spinner, step title, and progress bar.
    Use inside st.empty() placeholder to show/hide during loading."""
    c = color or COLORS["primary"]
    sub = ""
    if submessage:
        sub = (
            f'<div style="color:{COLORS["text_muted"]};font-size:0.72rem;'
            f'margin-top:6px;">{submessage}</div>'
        )
    return (
        f'<div style="max-width:480px;margin:24px auto;text-align:center;'
        f'padding:28px 24px;background:{COLORS["surface"]};'
        f'border:1px solid {COLORS["border"]};border-radius:12px;">'
        f'<div style="width:40px;height:40px;margin:0 auto 16px auto;'
        f'border:3px solid {COLORS["border"]};border-top-color:{c};'
        f'border-radius:50%;animation:spin 0.8s linear infinite;"></div>'
        f'<div style="color:{COLORS["text"]};font-size:0.95rem;font-weight:600;">{message}</div>'
        f'{sub}'
        f'<div style="margin-top:16px;height:3px;background:{COLORS["border"]};'
        f'border-radius:2px;overflow:hidden;">'
        f'<div style="height:100%;width:30%;background:{c};border-radius:2px;'
        f'animation:indeterminate 1.4s ease-in-out infinite;"></div>'
        f'</div>'
        f'</div>'
        f'<style>@keyframes spin {{ to{{transform:rotate(360deg);}} }}'
        f'@keyframes indeterminate {{ '
        f'0%{{margin-left:-30%;width:30%;}} 50%{{margin-left:50%;width:40%;}} '
        f'100%{{margin-left:100%;width:30%;}} }}</style>'
    )
