from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

import streamlit as st
from PIL import Image

from src.disease_info import DISEASE_INFO, get_info, severity_color
from src.model import (
    draw_detections,
    image_to_bytes,
    load_class_names,
    load_onnx_session,
    make_thumbnail,
    run_inference,
)
from src.ui import (
    detection_card,
    disclaimer,
    empty_state,
    inject_css,
    info_chip,
    metric_card,
    no_detection_state,
    render_app_header,
    render_logo,
    section_divider,
    status_badge,
)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SkinScan — AI Dermatology",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ── Session state defaults ─────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state["history"] = []
if "active_idx" not in st.session_state:
    st.session_state["active_idx"] = None

# ── Load model & class names (cached) ─────────────────────────────────────────
model_ok = True
model_error = ""
try:
    session = load_onnx_session()
except Exception as exc:
    model_ok = False
    model_error = str(exc)

class_names = load_class_names()
severity_map: dict[str, str] = {
    name: DISEASE_INFO[name].severity
    for name in class_names
    if name in DISEASE_INFO
}

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    render_logo()

    st.markdown("<h3>Input Mode</h3>", unsafe_allow_html=True)
    input_mode = st.radio(
        "input_mode",
        ["📁 File Upload", "📷 Camera"],
        label_visibility="collapsed",
    )

    section_divider()

    st.markdown("<h3>Detection Thresholds</h3>", unsafe_allow_html=True)
    conf_thresh = st.slider(
        "Confidence", 0.10, 0.95, 0.25, 0.05,
        help="Minimum confidence score for a detection to appear",
    )
    iou_thresh = st.slider(
        "IoU (NMS)", 0.10, 0.95, 0.45, 0.05,
        help="Overlap threshold for suppressing duplicate bounding boxes",
    )

    section_divider()

    # Session history
    history: list[dict] = st.session_state["history"]
    if history:
        st.markdown("<h3>Recent Analyses</h3>", unsafe_allow_html=True)
        for i, entry in enumerate(reversed(history[-5:])):
            real_idx = len(history) - 1 - i
            n = len(entry["detections"])
            label_text = entry["filename"]
            if len(label_text) > 20:
                label_text = label_text[:17] + "…"
            btn_label = f"🖼 {label_text} · {entry['timestamp']}\n{n} detection{'s' if n != 1 else ''}"
            if st.button(btn_label, key=f"hist_{real_idx}", width="stretch"):
                st.session_state["active_idx"] = real_idx

        section_divider()

    # Detectable conditions list
    if class_names:
        with st.expander("Detectable Conditions", expanded=False):
            for name in class_names:
                info = get_info(name)
                sev = info.severity if info else "low"
                dot = severity_color(sev)
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:0.5rem;'
                    f'padding:0.2rem 0;border-bottom:1px solid #0d1421;'
                    f'font-family:JetBrains Mono,monospace;font-size:0.68rem;color:#64748b;">'
                    f'<span style="width:6px;height:6px;border-radius:50%;'
                    f'background:{dot};flex-shrink:0;display:inline-block;"></span>'
                    f'{name}</div>',
                    unsafe_allow_html=True,
                )

# ── Main content ───────────────────────────────────────────────────────────────
render_app_header()

if not model_ok:
    st.error(
        f"**Model not found.** {model_error}\n\n"
        "Place `best.onnx` in the `models/` directory and restart the app."
    )
    st.stop()

# ── Input widgets ──────────────────────────────────────────────────────────────
img_pil: Image.Image | None = None
source_filename = "image.png"

if input_mode == "📁 File Upload":
    uploaded = st.file_uploader(
        "Upload a skin image for analysis",
        type=["jpg", "jpeg", "png", "bmp", "webp"],
        label_visibility="collapsed",
    )
    if uploaded is not None:
        raw = uploaded.read()
        if len(raw) > 20 * 1024 * 1024:
            st.warning("File exceeds 20 MB — please upload a smaller image.")
        else:
            img_pil = Image.open(io.BytesIO(raw)).convert("RGB")
            source_filename = uploaded.name
else:
    cam = st.camera_input("Point your camera at the affected skin area")
    if cam is not None:
        img_pil = Image.open(cam).convert("RGB")
        source_filename = f"capture_{datetime.now().strftime('%H%M%S')}.jpg"

# ── Decide what to display ─────────────────────────────────────────────────────
# Fresh image → run inference and add to history
if img_pil is not None:
    with st.spinner("Analyzing image…"):
        try:
            detections, latency_ms = run_inference(
                session, img_pil, conf_thresh, iou_thresh, class_names, severity_map
            )
        except Exception as exc:
            st.error(f"Inference error: {exc}")
            disclaimer()
            st.stop()

    annotated = draw_detections(img_pil, detections, severity_map)
    annotated_bytes = image_to_bytes(annotated)
    original_bytes = image_to_bytes(img_pil)

    entry = {
        "timestamp": datetime.now().strftime("%H:%M"),
        "filename": source_filename,
        "original_bytes": original_bytes,
        "annotated_bytes": annotated_bytes,
        "detections": detections,
        "latency_ms": latency_ms,
    }
    st.session_state["history"].append(entry)
    if len(st.session_state["history"]) > 20:
        st.session_state["history"] = st.session_state["history"][-20:]
    st.session_state["active_idx"] = len(st.session_state["history"]) - 1

    display_entry = entry

# No fresh image — show selected history entry if any
elif st.session_state["active_idx"] is not None:
    idx = st.session_state["active_idx"]
    if 0 <= idx < len(st.session_state["history"]):
        display_entry = st.session_state["history"][idx]
        img_pil = Image.open(io.BytesIO(display_entry["original_bytes"])).convert("RGB")
        annotated = Image.open(io.BytesIO(display_entry["annotated_bytes"])).convert("RGB")
        annotated_bytes = display_entry["annotated_bytes"]
        source_filename = display_entry["filename"]
        detections = display_entry["detections"]
        latency_ms = display_entry["latency_ms"]
    else:
        display_entry = None

    if display_entry is None:
        empty_state("No history entry found. Drop an image to begin.")
        disclaimer()
        st.stop()

# Nothing to show
else:
    empty_state("Drop a skin image or switch to camera mode to begin")
    disclaimer()
    st.stop()

# ── Results layout ─────────────────────────────────────────────────────────────
w_orig, h_orig = img_pil.size
n_det = len(detections)
top_conf = detections[0]["conf"] if detections else 0.0
top_cls = detections[0]["class_name"] if detections else "—"

col_img, col_res = st.columns([3, 2], gap="large")

# ── Left: image viewer ─────────────────────────────────────────────────────────
with col_img:
    st.markdown("<h2>Detection Output</h2>", unsafe_allow_html=True)

    tab_ann, tab_orig = st.tabs(["Annotated", "Original"])
    with tab_ann:
        st.image(annotated, width="stretch")
    with tab_orig:
        st.image(img_pil, width="stretch")

    st.markdown(
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'margin-top:0.5rem;">'
        f'<span style="font-family:JetBrains Mono,monospace;font-size:0.62rem;'
        f'color:#334155;letter-spacing:0.04em;">'
        f'{source_filename} &nbsp;·&nbsp; {w_orig}×{h_orig}px &nbsp;·&nbsp; ONNX</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.download_button(
        label="⬇  Download Annotated Image",
        data=annotated_bytes,
        file_name=f"skinscan_{source_filename.rsplit('.', 1)[0]}.png",
        mime="image/png",
        width="stretch",
    )

# ── Right: analysis results ────────────────────────────────────────────────────
with col_res:
    st.markdown("<h2>Analysis Results</h2>", unsafe_allow_html=True)

    # Status badge
    st.markdown(status_badge(n_det, top_conf), unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Metric cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            metric_card("Detections", str(n_det), "found", accent=(n_det > 0)),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            metric_card("Latency", f"{latency_ms:.0f}", "ms"),
            unsafe_allow_html=True,
        )
    with c3:
        conf_display = f"{top_conf:.0%}" if top_conf > 0 else "—"
        cls_display = top_cls[:10] if top_cls != "—" else "—"
        st.markdown(
            metric_card("Top Conf", conf_display, cls_display),
            unsafe_allow_html=True,
        )

    section_divider()

    # Detection cards
    st.markdown("<h2>Detections</h2>", unsafe_allow_html=True)

    if n_det == 0:
        no_detection_state()
    else:
        for det in detections:
            info = get_info(det["class_name"])
            st.markdown(detection_card(det, info), unsafe_allow_html=True)

            if info:
                with st.expander(f"ℹ About {det['class_name']}", expanded=False):
                    chips = (
                        info_chip("👤", info.common_age)
                        + info_chip(
                            "🦠" if info.contagious else "🔒",
                            "Contagious" if info.contagious else "Not contagious",
                        )
                        + info_chip("⚕", info.severity.capitalize() + " severity")
                    )
                    st.markdown(
                        f'<div style="margin-bottom:0.7rem;">{chips}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div style="font-size:0.8rem;color:#94a3b8;line-height:1.65;'
                        f'margin-bottom:0.8rem;">{info.description}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div style="background:rgba(0,212,180,0.06);'
                        f'border:1px solid rgba(0,212,180,0.15);'
                        f'border-radius:6px;padding:0.6rem 0.8rem;">'
                        f'<div style="font-family:JetBrains Mono,monospace;font-size:0.6rem;'
                        f'color:#00d4b4;letter-spacing:0.1em;text-transform:uppercase;'
                        f'margin-bottom:0.35rem;">Recommendation</div>'
                        f'<div style="font-size:0.78rem;color:#94a3b8;line-height:1.5;">'
                        f'{info.recommendation}</div></div>',
                        unsafe_allow_html=True,
                    )
                    if info.symptoms:
                        st.markdown(
                            '<div style="margin-top:0.6rem;font-family:JetBrains Mono,monospace;'
                            'font-size:0.62rem;color:#334155;letter-spacing:0.04em;">'
                            'COMMON SYMPTOMS &nbsp;·&nbsp; '
                            + " &nbsp;·&nbsp; ".join(info.symptoms)
                            + "</div>",
                            unsafe_allow_html=True,
                        )

disclaimer()
