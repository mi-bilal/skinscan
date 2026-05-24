from __future__ import annotations

import streamlit as st

# ── Design tokens ──────────────────────────────────────────────────────────────
BG_DEEP = "#080c14"
BG_CARD = "#0d1421"
BG_SIDEBAR = "#090e1a"
BORDER = "#1a2744"
BORDER_SUBTLE = "#111927"
ACCENT = "#00d4b4"
ACCENT_DIM = "#00a08a"
TEXT_PRIMARY = "#e2e8f0"
TEXT_MUTED = "#64748b"
TEXT_FAINT = "#334155"
RED = "#ef4444"
AMBER = "#f59e0b"
GREEN = "#10b981"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

*, *::before, *::after {{ box-sizing: border-box; }}

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, sans-serif;
    background-color: {BG_DEEP};
    color: {TEXT_PRIMARY};
}}

.stApp {{ background-color: {BG_DEEP}; }}
#MainMenu, footer, header {{ visibility: hidden; }}

/* Scrollbar */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: {BG_DEEP}; }}
::-webkit-scrollbar-thumb {{ background: #1e3a5f; border-radius: 4px; }}
::-webkit-scrollbar-thumb:hover {{ background: {ACCENT_DIM}; }}

/* Main content area */
.block-container {{
    padding: 1.5rem 2rem 3rem 2rem;
    max-width: 1440px;
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background: {BG_SIDEBAR};
    border-right: 1px solid {BORDER};
}}
[data-testid="stSidebar"] .block-container {{
    padding: 1.5rem 1rem 2rem 1rem;
}}

/* Typography */
h1, h2, h3 {{ font-family: 'JetBrains Mono', monospace; }}
h1 {{
    font-size: 1.6rem; font-weight: 700; color: #ffffff;
    letter-spacing: -0.03em; margin: 0;
}}
h2 {{
    font-size: 0.7rem; font-weight: 500; color: {TEXT_MUTED};
    letter-spacing: 0.12em; text-transform: uppercase; margin: 0 0 1rem 0;
}}
h3 {{
    font-size: 0.65rem; font-weight: 500; color: {TEXT_FAINT};
    letter-spacing: 0.1em; text-transform: uppercase; margin: 0;
}}

/* Inputs */
[data-testid="stFileUploader"] {{
    background: {BG_CARD};
    border: 1px dashed {BORDER};
    border-radius: 10px;
    padding: 1.5rem;
    transition: border-color 0.2s ease;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: {ACCENT_DIM};
}}

/* Camera input */
[data-testid="stCameraInput"] {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    overflow: hidden;
}}

/* Sliders */
[data-testid="stSlider"] label {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    color: {TEXT_MUTED} !important;
    letter-spacing: 0.04em;
}}
[data-testid="stSlider"] [data-testid="stMarkdownContainer"] p {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: {TEXT_MUTED};
}}

/* Checkboxes & radio */
[data-testid="stRadio"] > div {{ gap: 0.4rem; }}
[data-testid="stRadio"] label {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    color: {TEXT_MUTED} !important;
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 0.35rem 0.8rem;
    cursor: pointer;
    transition: all 0.15s ease;
}}
[data-testid="stRadio"] label:has(input:checked) {{
    background: rgba(0, 212, 180, 0.1);
    border-color: {ACCENT_DIM};
    color: {ACCENT} !important;
}}

/* Images */
[data-testid="stImage"] img {{
    border-radius: 8px;
    border: 1px solid {BORDER};
}}

/* Spinner */
[data-testid="stSpinner"] {{ color: {ACCENT}; }}

/* Tabs */
[data-testid="stTabs"] [role="tablist"] {{
    border-bottom: 1px solid {BORDER};
    gap: 0;
}}
[data-testid="stTabs"] [role="tab"] {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    color: {TEXT_MUTED};
    border: none;
    padding: 0.5rem 1rem;
    background: transparent;
}}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
}}

/* Download button */
[data-testid="stDownloadButton"] button {{
    background: rgba(0, 212, 180, 0.08) !important;
    border: 1px solid {ACCENT_DIM} !important;
    color: {ACCENT} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.05em;
    border-radius: 6px !important;
    width: 100%;
    transition: all 0.2s ease !important;
}}
[data-testid="stDownloadButton"] button:hover {{
    background: rgba(0, 212, 180, 0.15) !important;
}}

/* Expander */
[data-testid="stExpander"] {{
    background: {BG_CARD};
    border: 1px solid {BORDER_SUBTLE} !important;
    border-radius: 8px !important;
}}
[data-testid="stExpander"] summary {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: {TEXT_MUTED};
    letter-spacing: 0.04em;
}}

/* Custom classes */
.skinscan-logo {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.06em;
    padding-bottom: 1rem;
    border-bottom: 1px solid {BORDER};
    margin-bottom: 1.2rem;
}}
.skinscan-logo-accent {{
    color: {ACCENT};
}}
.skinscan-logo-sub {{
    font-size: 0.62rem;
    font-weight: 400;
    color: {TEXT_FAINT};
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 0.2rem;
}}

.app-header {{
    background: linear-gradient(135deg, {BG_CARD} 0%, #0a1628 100%);
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}}
.app-header::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, {ACCENT}, #0066ff, {ACCENT});
    background-size: 200% 100%;
    animation: shimmer 3s infinite linear;
}}
@keyframes shimmer {{
    0% {{ background-position: 200% 0; }}
    100% {{ background-position: -200% 0; }}
}}
.app-header-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.02em;
    line-height: 1;
}}
.app-header-accent {{ color: {ACCENT}; }}
.app-header-model {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: {TEXT_FAINT};
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.4rem;
}}
.app-header-desc {{
    font-size: 0.82rem;
    color: {TEXT_MUTED};
    margin-top: 0.6rem;
    line-height: 1.5;
}}

.metric-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 10px;
    padding: 1rem 1.1rem;
    text-align: center;
    transition: border-color 0.2s ease;
}}
.metric-card:hover {{ border-color: {BORDER}; }}
.metric-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem;
    color: {TEXT_FAINT};
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}}
.metric-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.8rem;
    font-weight: 600;
    color: #ffffff;
    line-height: 1;
}}
.metric-value-accent {{ color: {ACCENT}; }}
.metric-unit {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: {TEXT_FAINT};
    margin-top: 0.3rem;
    letter-spacing: 0.06em;
}}

.badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.3rem 0.7rem;
    border-radius: 20px;
    font-weight: 600;
}}
.badge-confident {{
    background: rgba(16, 185, 129, 0.12);
    color: {GREEN};
    border: 1px solid rgba(16, 185, 129, 0.3);
    box-shadow: 0 0 12px rgba(16, 185, 129, 0.1);
}}
.badge-low {{
    background: rgba(245, 158, 11, 0.12);
    color: {AMBER};
    border: 1px solid rgba(245, 158, 11, 0.3);
}}
.badge-none {{
    background: rgba(100, 116, 139, 0.1);
    color: {TEXT_MUTED};
    border: 1px solid rgba(100, 116, 139, 0.2);
}}

.sev-badge {{
    display: inline-flex;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
}}
.sev-high {{
    background: rgba(239, 68, 68, 0.15);
    color: {RED};
    border: 1px solid rgba(239, 68, 68, 0.3);
}}
.sev-moderate {{
    background: rgba(245, 158, 11, 0.15);
    color: {AMBER};
    border: 1px solid rgba(245, 158, 11, 0.3);
}}
.sev-low {{
    background: rgba(16, 185, 129, 0.15);
    color: {GREEN};
    border: 1px solid rgba(16, 185, 129, 0.3);
}}

.det-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    transition: border-color 0.2s ease, transform 0.15s ease;
}}
.det-card:hover {{
    border-color: {BORDER};
    transform: translateY(-1px);
}}
.det-card-high {{ border-left: 3px solid {RED}; }}
.det-card-moderate {{ border-left: 3px solid {AMBER}; }}
.det-card-low {{ border-left: 3px solid {GREEN}; }}
.det-card-unknown {{ border-left: 3px solid {ACCENT_DIM}; }}
.det-name {{
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: {TEXT_PRIMARY};
    margin-bottom: 0.4rem;
}}
.det-conf-row {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-top: 0.5rem;
}}
.det-bar-bg {{
    flex: 1;
    height: 4px;
    background: {BORDER_SUBTLE};
    border-radius: 2px;
    overflow: hidden;
}}
.det-bar-fg {{
    height: 100%;
    border-radius: 2px;
    transition: width 0.5s ease;
}}
.det-conf-val {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 600;
    min-width: 42px;
    text-align: right;
}}

.empty-state {{
    background: {BG_CARD};
    border: 1px dashed {BORDER};
    border-radius: 12px;
    padding: 4rem 2rem;
    text-align: center;
}}
.empty-icon {{
    font-size: 2.5rem;
    margin-bottom: 1rem;
    opacity: 0.3;
}}
.empty-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: {TEXT_FAINT};
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}}
.empty-sub {{
    font-size: 0.75rem;
    color: {TEXT_FAINT};
    opacity: 0.7;
}}

.disclaimer {{
    background: rgba(239, 68, 68, 0.05);
    border: 1px solid rgba(239, 68, 68, 0.15);
    border-left: 3px solid rgba(239, 68, 68, 0.4);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    font-size: 0.72rem;
    color: #94a3b8;
    line-height: 1.6;
    margin-top: 1.5rem;
}}

.history-thumb {{
    background: {BG_CARD};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 8px;
    padding: 0.5rem;
    margin-bottom: 0.4rem;
    cursor: pointer;
    transition: all 0.15s ease;
}}
.history-thumb:hover {{
    border-color: {BORDER};
    background: #0f1928;
}}
.history-meta {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: {TEXT_FAINT};
    margin-top: 0.3rem;
    letter-spacing: 0.04em;
}}

.info-chip {{
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    font-size: 0.7rem;
    color: {TEXT_MUTED};
    background: rgba(100, 116, 139, 0.08);
    border: 1px solid rgba(100, 116, 139, 0.15);
    border-radius: 4px;
    padding: 0.2rem 0.5rem;
    margin-right: 0.3rem;
    margin-bottom: 0.3rem;
}}

.section-divider {{
    height: 1px;
    background: linear-gradient(90deg, transparent, {BORDER}, transparent);
    margin: 1.2rem 0;
}}

.pulse-dot {{
    display: inline-block;
    width: 6px; height: 6px;
    background: {ACCENT};
    border-radius: 50%;
    animation: pulse 2s infinite ease-in-out;
    margin-right: 0.4rem;
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.4; transform: scale(0.8); }}
}}

.no-det-state {{
    background: {BG_CARD};
    border: 1px solid {BORDER_SUBTLE};
    border-radius: 10px;
    padding: 1.5rem;
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: {TEXT_FAINT};
    letter-spacing: 0.06em;
    line-height: 1.8;
}}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def render_app_header() -> None:
    st.markdown("""
    <div class="app-header">
        <div class="app-header-title">SKIN<span class="app-header-accent">SCAN</span></div>
        <div class="app-header-model">
            <span class="pulse-dot"></span>
            ONNX Runtime &nbsp;·&nbsp; 11 Disease Classes &nbsp;·&nbsp; YOLOv11s
        </div>
        <div class="app-header-desc">
            AI-powered dermatological analysis. Upload or capture a skin image for instant disease detection.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_logo() -> None:
    st.markdown("""
    <div class="skinscan-logo">
        SKIN<span class="skinscan-logo-accent">SCAN</span>
        <div class="skinscan-logo-sub">Dermatology AI · v2.0</div>
    </div>
    """, unsafe_allow_html=True)


def metric_card(label: str, value: str, unit: str = "", accent: bool = False) -> str:
    val_class = "metric-value-accent" if accent else "metric-value"
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="{val_class}">{value}</div>
        <div class="metric-unit">{unit}</div>
    </div>"""


def severity_badge(level: str) -> str:
    cls = f"sev-{level.lower()}"
    symbols = {"high": "⚠", "moderate": "◆", "low": "●"}
    sym = symbols.get(level.lower(), "○")
    return f'<span class="sev-badge {cls}">{sym} {level.upper()}</span>'


def detection_card(det: dict, info=None) -> str:
    name = det["class_name"]
    conf = det["conf"]
    conf_pct = int(conf * 100)

    if info:
        sev = info.severity
        from src.disease_info import severity_color, severity_bg
        bar_color = severity_color(sev)
        card_border = f"det-card-{sev}"
        sev_html = severity_badge(sev)
    else:
        bar_color = "#00d4b4"
        card_border = "det-card-unknown"
        sev_html = ""

    if conf >= 0.70:
        conf_color = "#10b981"
    elif conf >= 0.45:
        conf_color = "#f59e0b"
    else:
        conf_color = "#ef4444"

    return f"""
    <div class="det-card {card_border}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;">
            <div class="det-name">{name}</div>
            {sev_html}
        </div>
        <div class="det-conf-row">
            <div class="det-bar-bg">
                <div class="det-bar-fg" style="width:{conf_pct}%;background:{bar_color};"></div>
            </div>
            <span class="det-conf-val" style="color:{conf_color};">{conf:.1%}</span>
        </div>
    </div>"""


def status_badge(n_det: int, top_conf: float) -> str:
    if n_det == 0:
        return '<span class="badge badge-none">● No Detections</span>'
    if top_conf >= 0.60:
        return '<span class="badge badge-confident">✓ Confident Detection</span>'
    return '<span class="badge badge-low">◆ Low Confidence</span>'


def empty_state(msg: str = "Drop an image to begin analysis") -> None:
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-icon">◎</div>
        <div class="empty-title">Awaiting Input</div>
        <div class="empty-sub">{msg}</div>
    </div>
    """, unsafe_allow_html=True)


def no_detection_state() -> None:
    st.markdown("""
    <div class="no-det-state">
        No detections above threshold<br>
        <span style="opacity:0.6;font-size:0.65rem;">
            Try lowering the confidence slider or check image quality
        </span>
    </div>
    """, unsafe_allow_html=True)


def section_divider() -> None:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


def info_chip(icon: str, text: str) -> str:
    return f'<span class="info-chip">{icon} {text}</span>'


def disclaimer() -> None:
    st.markdown("""
    <div class="disclaimer">
        <strong>Medical Disclaimer</strong><br>
        SkinScan is an AI-powered screening tool for informational and educational purposes only.
        Results are not a substitute for professional medical diagnosis.
        Always consult a qualified dermatologist or healthcare provider for medical advice.
    </div>
    """, unsafe_allow_html=True)
