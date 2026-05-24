from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import streamlit as st
import yaml
from PIL import Image, ImageDraw, ImageFont

MODELS_DIR = Path("models")
ONNX_PATH = MODELS_DIR / "best.onnx"

def _find_yaml() -> Path:
    candidates = list(MODELS_DIR.glob("*.yaml")) + list(MODELS_DIR.glob("*.yml"))
    return candidates[0] if candidates else MODELS_DIR / "data.yaml"

YAML_PATH = _find_yaml()

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
    "C:/Windows/Fonts/consola.ttf",
    "C:/Windows/Fonts/cour.ttf",
]

_SEVERITY_BOX_COLORS = {
    "high": (239, 68, 68),
    "moderate": (245, 158, 11),
    "low": (16, 185, 129),
    None: (0, 212, 180),
}


def _load_font(size: int = 13) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


@st.cache_resource
def load_onnx_session() -> object:
    import onnxruntime as ort

    if not ONNX_PATH.exists():
        raise FileNotFoundError(
            f"ONNX model not found at {ONNX_PATH}. "
            "Ensure models/best.onnx is present."
        )
    available = ort.get_available_providers()
    providers = [p for p in ["CUDAExecutionProvider", "CPUExecutionProvider"] if p in available]
    return ort.InferenceSession(str(ONNX_PATH), providers=providers)


@st.cache_resource
def load_class_names() -> list[str]:
    if not YAML_PATH.exists():
        return []
    with open(YAML_PATH) as f:
        cfg = yaml.safe_load(f)
    names = cfg.get("names", [])
    if isinstance(names, dict):
        names = [names[k] for k in sorted(names.keys())]
    return [n.replace("-", " ").title() for n in names]


def letterbox_pil(img: Image.Image, target: int = 640) -> tuple[Image.Image, float, int, int]:
    w, h = img.size
    scale = target / max(w, h)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = img.resize((new_w, new_h), Image.BILINEAR)
    canvas = Image.new("RGB", (target, target), (0, 0, 0))
    pad_x, pad_y = (target - new_w) // 2, (target - new_h) // 2
    canvas.paste(resized, (pad_x, pad_y))
    return canvas, scale, pad_x, pad_y


def preprocess(img: Image.Image, imgsz: int = 640) -> tuple[np.ndarray, float, int, int]:
    lb, scale, pad_x, pad_y = letterbox_pil(img, imgsz)
    blob = np.array(lb, dtype=np.float32) / 255.0
    blob = np.transpose(blob, (2, 0, 1))[np.newaxis]
    return blob, scale, pad_x, pad_y


def _iou(box: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    ix1 = np.maximum(box[0], boxes[:, 0])
    iy1 = np.maximum(box[1], boxes[:, 1])
    ix2 = np.minimum(box[2], boxes[:, 2])
    iy2 = np.minimum(box[3], boxes[:, 3])
    inter = np.maximum(0, ix2 - ix1) * np.maximum(0, iy2 - iy1)
    area_box = (box[2] - box[0]) * (box[3] - box[1])
    area_boxes = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    return inter / (area_box + area_boxes - inter + 1e-9)


def _nms(boxes: np.ndarray, scores: np.ndarray, iou_thresh: float) -> list[int]:
    order = scores.argsort()[::-1]
    keep: list[int] = []
    while order.size > 0:
        i = order[0]
        keep.append(int(i))
        if order.size == 1:
            break
        ious = _iou(boxes[i], boxes[order[1:]])
        order = order[1:][ious <= iou_thresh]
    return keep


def _postprocess(
    raw_output: np.ndarray,
    scale: float,
    pad_x: int,
    pad_y: int,
    conf_thresh: float,
    iou_thresh: float,
    class_names: list[str],
) -> list[dict]:
    preds = raw_output[0].T
    boxes_xywh = preds[:, :4]
    scores = preds[:, 4:]
    class_ids = np.argmax(scores, axis=1)
    confs = scores[np.arange(len(scores)), class_ids]

    mask = confs >= conf_thresh
    if not mask.any():
        return []

    boxes_xywh = boxes_xywh[mask]
    confs = confs[mask]
    class_ids = class_ids[mask]

    x1 = (boxes_xywh[:, 0] - boxes_xywh[:, 2] / 2 - pad_x) / scale
    y1 = (boxes_xywh[:, 1] - boxes_xywh[:, 3] / 2 - pad_y) / scale
    x2 = (boxes_xywh[:, 0] + boxes_xywh[:, 2] / 2 - pad_x) / scale
    y2 = (boxes_xywh[:, 1] + boxes_xywh[:, 3] / 2 - pad_y) / scale
    boxes_xyxy = np.stack([x1, y1, x2, y2], axis=1)

    keep = _nms(boxes_xyxy, confs, iou_thresh)
    results = []
    for i in keep:
        cid = int(class_ids[i])
        results.append({
            "class_id": cid,
            "class_name": class_names[cid] if cid < len(class_names) else f"Class {cid}",
            "conf": float(confs[i]),
            "box": [float(x1[i]), float(y1[i]), float(x2[i]), float(y2[i])],
        })
    results.sort(key=lambda x: x["conf"], reverse=True)
    return results


def run_inference(
    session,
    img: Image.Image,
    conf_thresh: float,
    iou_thresh: float,
    class_names: list[str],
    severity_map: dict[str, str] | None = None,
) -> tuple[list[dict], float]:
    blob, scale, pad_x, pad_y = preprocess(img)
    t0 = time.perf_counter()
    raw = session.run(None, {session.get_inputs()[0].name: blob})
    latency_ms = (time.perf_counter() - t0) * 1000
    detections = _postprocess(raw[0], scale, pad_x, pad_y, conf_thresh, iou_thresh, class_names)
    return detections, latency_ms


def draw_detections(
    img: Image.Image,
    detections: list[dict],
    severity_map: dict[str, str] | None = None,
) -> Image.Image:
    out = img.copy()
    draw = ImageDraw.Draw(out)
    font = _load_font(13)
    font_small = _load_font(11)

    for det in detections:
        x1, y1, x2, y2 = [int(v) for v in det["box"]]
        x1, y1 = max(0, x1), max(0, y1)
        x2 = min(img.width, x2)
        y2 = min(img.height, y2)

        sev = (severity_map or {}).get(det["class_name"])
        color = _SEVERITY_BOX_COLORS.get(sev, _SEVERITY_BOX_COLORS[None])
        dim_color = tuple(max(0, c - 80) for c in color)

        draw.rectangle([x1, y1, x2, y2], outline=color, width=2)

        label = f"{det['class_name']}  {det['conf']:.2f}"
        bbox = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        tag_y0 = max(0, y1 - th - 8)
        draw.rectangle([x1, tag_y0, x1 + tw + 10, y1], fill=color)
        draw.text((x1 + 5, tag_y0 + 2), label, fill=(10, 10, 10), font=font)

    return out


def image_to_bytes(img: Image.Image) -> bytes:
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


def make_thumbnail(img: Image.Image, size: int = 80) -> Image.Image:
    thumb = img.copy()
    thumb.thumbnail((size, size), Image.LANCZOS)
    return thumb
