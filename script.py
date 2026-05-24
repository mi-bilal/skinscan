# %% [markdown]
# # 🩺 Skin Disease Detection with YOLO11
# 
# End-to-end pipeline: dataset download → training → evaluation → ONNX export.
# 
# **Runtime:** Make sure you're on a GPU runtime in Colab → `Runtime > Change runtime type > T4 GPU`
# 
# **Roboflow API key:** Store it in Colab Secrets (`🔑` icon in the left sidebar) as `ROBOFLOW_API_KEY`.

# %% [markdown]
# ## 1. Environment Setup

# %%
# Verify GPU
import subprocess
result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
print(result.stdout if result.returncode == 0 else '⚠️  No GPU detected — switch runtime to GPU!')

# %%
# Install dependencies
%pip install -q ultralytics roboflow supervision

import ultralytics
ultralytics.checks()  # Prints YOLO version, CUDA status, etc.

# %%
import os
import glob
import yaml
import time
import random
from pathlib import Path

import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

from ultralytics import YOLO

# Reproducibility
random.seed(42)
np.random.seed(42)

print('All imports OK ✅')

# %% [markdown]
# ## 2. Dataset — Download from Roboflow

# %%
import os
from getpass import getpass

# Try env var first, otherwise prompt securely
ROBOFLOW_API_KEY = os.environ.get('ROBOFLOW_API_KEY') or getpass('Enter Roboflow API key: ')

if not ROBOFLOW_API_KEY:
    raise ValueError('No API key provided.')

print('API key loaded ✅')

# %%
from roboflow import Roboflow

rf = Roboflow(api_key=ROBOFLOW_API_KEY)

# ── Dataset config ────────────────────────────────────────────────────────────
# Change these if you want a different Roboflow dataset
WORKSPACE   = 'workshop-yg2yt'
PROJECT     = 'skin-3n2jd'
VERSION     = 1
DATA_DIR    = 'data'

project = rf.workspace(WORKSPACE).project(PROJECT)
version = project.version(VERSION)
dataset = version.download('yolov8', location=DATA_DIR)  # yolov8 format works for YOLO11

print(f'Dataset downloaded to: {DATA_DIR}/')

# %%
# ── Inspect dataset ───────────────────────────────────────────────────────────
DATA_YAML = f'{DATA_DIR}/data.yaml'

with open(DATA_YAML) as f:
    data_cfg = yaml.safe_load(f)

CLASS_NAMES = data_cfg['names']
NUM_CLASSES  = len(CLASS_NAMES)

train_imgs = len(glob.glob(f'{DATA_DIR}/train/images/*.jpg'))
val_imgs   = len(glob.glob(f'{DATA_DIR}/valid/images/*.jpg'))
test_imgs  = len(glob.glob(f'{DATA_DIR}/test/images/*.jpg'))

print(f'Classes ({NUM_CLASSES}): {CLASS_NAMES}')
print(f'Train: {train_imgs} | Val: {val_imgs} | Test: {test_imgs} | Total: {train_imgs+val_imgs+test_imgs}')

# %%
# ── Visualise sample training images with bounding boxes ─────────────────────
def draw_yolo_boxes(img_path, label_path, class_names):
    img = cv2.imread(img_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w = img.shape[:2]

    if Path(label_path).exists():
        with open(label_path) as f:
            for line in f:
                cls, cx, cy, bw, bh = map(float, line.strip().split())
                cls = int(cls)
                x1 = int((cx - bw/2) * w)
                y1 = int((cy - bh/2) * h)
                x2 = int((cx + bw/2) * w)
                y2 = int((cy + bh/2) * h)
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 80, 80), 2)
                label = class_names[cls] if cls < len(class_names) else str(cls)
                cv2.putText(img, label, (x1, max(y1-6, 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 80, 80), 2)
    return img

sample_imgs   = sorted(glob.glob(f'{DATA_DIR}/train/images/*.jpg'))[:6]
sample_labels = [p.replace('/images/', '/labels/').replace('.jpg', '.txt') for p in sample_imgs]

fig, axes = plt.subplots(2, 3, figsize=(16, 9))
fig.suptitle('Training Sample Images with Ground-Truth Boxes', fontsize=14, fontweight='bold')

for ax, img_p, lbl_p in zip(axes.flat, sample_imgs, sample_labels):
    vis = draw_yolo_boxes(img_p, lbl_p, CLASS_NAMES)
    ax.imshow(vis)
    ax.set_title(Path(img_p).name, fontsize=8)
    ax.axis('off')

plt.tight_layout()
plt.show()

# %% [markdown]
# ## 3. Training

# %%
# ── Hyperparameters ───────────────────────────────────────────────────────────
# YOLO11s is a good default — fast, accurate. Options: yolo11n / s / m / l / x
MODEL_WEIGHTS = 'yolo11s.pt'
EPOCHS        = 60
IMG_SIZE      = 640
BATCH_SIZE    = 16
PATIENCE      = 15       # early stopping patience
PROJECT_NAME  = 'skin_disease'
RUN_NAME      = 'yolo11s_run1'

print(f'Model : {MODEL_WEIGHTS}')
print(f'Epochs: {EPOCHS}  |  Img: {IMG_SIZE}  |  Batch: {BATCH_SIZE}  |  Patience: {PATIENCE}')

# %%
# ── Train ─────────────────────────────────────────────────────────────────────
model = YOLO(MODEL_WEIGHTS)

t0 = time.time()
train_results = model.train(
    data        = DATA_YAML,
    epochs      = EPOCHS,
    imgsz       = IMG_SIZE,
    batch       = BATCH_SIZE,
    patience    = PATIENCE,
    project     = 'runs',
    name        = RUN_NAME,
    # Augmentation (sensible defaults for medical images)
    hsv_h       = 0.015,
    hsv_s       = 0.4,
    hsv_v       = 0.3,
    flipud      = 0.3,
    fliplr      = 0.5,
    mosaic      = 1.0,
    mixup       = 0.1,
    # Optimiser
    optimizer   = 'AdamW',
    lr0         = 0.001,
    lrf         = 0.01,
    warmup_epochs = 3,
    cos_lr      = True,
    # Misc
    seed        = 42,
    verbose     = True,
    device      = 0,
)
elapsed = time.time() - t0
print(f'\n⏱️  Training finished in {elapsed/60:.1f} min')

# Locate best weights
BEST_PT = Path(f'runs/{PROJECT_NAME}/{RUN_NAME}/weights/best.pt')
print(f'Best weights → {BEST_PT}')

# %%
# ── Plot training curves ──────────────────────────────────────────────────────
results_csv = Path(train_results.save_dir) / 'results.csv'
BEST_PT     = Path(train_results.save_dir) / 'weights' / 'best.pt'  # fix this too

print(f'Save dir: {train_results.save_dir}')
print(f'CSV exists: {results_csv.exists()}')

if results_csv.exists():
    df = pd.read_csv(results_csv)
    df.columns = df.columns.str.strip()

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Training Curves — YOLO11s Skin Disease', fontsize=14, fontweight='bold')

    pairs = [
        ('train/box_loss',  'val/box_loss',  'Box Loss',       axes[0, 0]),
        ('train/cls_loss',  'val/cls_loss',  'Class Loss',     axes[0, 1]),
        ('train/dfl_loss',  'val/dfl_loss',  'DFL Loss',       axes[0, 2]),
        ('metrics/mAP50(B)', None,           'mAP@0.5',        axes[1, 0]),
        ('metrics/mAP50-95(B)', None,        'mAP@0.5-0.95',   axes[1, 1]),
        ('metrics/precision(B)', 'metrics/recall(B)', 'Precision & Recall', axes[1, 2]),
    ]

    for train_col, val_col, title, ax in pairs:
        if train_col in df.columns:
            ax.plot(df['epoch'], df[train_col], label='train' if val_col else title, color='royalblue')
        if val_col and val_col in df.columns:
            ax.plot(df['epoch'], df[val_col], label='val', color='tomato', linestyle='--')
        if val_col == 'metrics/recall(B)' and val_col in df.columns:
            ax.plot(df['epoch'], df[val_col], label='recall', color='green', linestyle=':')
        ax.set_title(title, fontsize=11)
        ax.set_xlabel('Epoch')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig('training_curves.png', dpi=150, bbox_inches='tight')
    plt.show()
    print('Saved → training_curves.png')
else:
    print('results.csv not found — plot skipped')

# %% [markdown]
# ## 4. Evaluation

# %%
# Load best model and evaluate on validation / test set
best_model = YOLO(str(BEST_PT))

val_results = best_model.val(
    data   = DATA_YAML,
    split  = 'test',    # evaluate on test split
    imgsz  = IMG_SIZE,
    batch  = BATCH_SIZE,
    device = 0,
    verbose = True,
)

# ── Aggregate metrics ─────────────────────────────────────────────────────────
mp  = float(val_results.box.mp)    # mean precision
mr  = float(val_results.box.mr)    # mean recall
map50    = float(val_results.box.map50)
map5095  = float(val_results.box.map)
f1 = 2 * mp * mr / (mp + mr + 1e-9)

print('\n' + '═'*50)
print('  EVALUATION RESULTS (test split)')
print('═'*50)
print(f'  mAP@0.5         : {map50:.4f}  ({map50*100:.1f}%)')
print(f'  mAP@0.5-0.95    : {map5095:.4f}  ({map5095*100:.1f}%)')
print(f'  Precision       : {mp:.4f}  ({mp*100:.1f}%)')
print(f'  Recall          : {mr:.4f}  ({mr*100:.1f}%)')
print(f'  F1-Score        : {f1:.4f}  ({f1*100:.1f}%)')
print('═'*50)

# %%
# ── Per-class metrics ─────────────────────────────────────────────────────────
class_names_map = val_results.names
per_class = []

for i, name in class_names_map.items():
    try:
        prec = float(val_results.box.p[i])    if i < len(val_results.box.p)    else 0.0
        rec  = float(val_results.box.r[i])    if i < len(val_results.box.r)    else 0.0
        ap50 = float(val_results.box.ap50[i]) if i < len(val_results.box.ap50) else 0.0
        f1_c = 2*prec*rec/(prec+rec+1e-9)
        per_class.append({'class': name, 'precision': prec, 'recall': rec, 'ap50': ap50, 'f1': f1_c})
    except Exception as e:
        print(f'  Class {i} error: {e}')

df_pc = pd.DataFrame(per_class).sort_values('ap50', ascending=False)
print('\nPer-class AP@0.5:')
print(df_pc[['class', 'precision', 'recall', 'ap50', 'f1']].to_string(index=False, float_format='{:.4f}'.format))

# %%
# ── Visualise per-class metrics ───────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle('Per-Class Metrics', fontsize=14, fontweight='bold')

# AP@0.5
axes[0].barh(df_pc['class'], df_pc['ap50'], color='steelblue', edgecolor='white')
axes[0].set_xlabel('AP@0.5')
axes[0].set_title('Average Precision @ IoU 0.5')
axes[0].axvline(x=df_pc['ap50'].mean(), color='tomato', linestyle='--', label=f'mean={df_pc["ap50"].mean():.3f}')
axes[0].legend()
axes[0].set_xlim(0, 1)
axes[0].grid(axis='x', alpha=0.3)

# Precision vs Recall grouped bar
x  = np.arange(len(df_pc))
w  = 0.35
axes[1].bar(x - w/2, df_pc['precision'], w, label='Precision', color='cornflowerblue')
axes[1].bar(x + w/2, df_pc['recall'],    w, label='Recall',    color='coral')
axes[1].set_xticks(x)
axes[1].set_xticklabels(df_pc['class'], rotation=40, ha='right', fontsize=9)
axes[1].set_ylabel('Score')
axes[1].set_title('Precision vs Recall per Class')
axes[1].set_ylim(0, 1)
axes[1].legend()
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('per_class_metrics.png', dpi=150, bbox_inches='tight')
plt.show()

# %% [markdown]
# ## 5. Inference on Test Images

# %%
CONF_THRESH = 0.25
IOU_THRESH  = 0.45

test_img_paths = sorted(glob.glob(f'{DATA_DIR}/test/images/*.jpg'))
sample_paths   = random.sample(test_img_paths, min(6, len(test_img_paths)))

os.makedirs('results', exist_ok=True)

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle(f'Inference Results (conf ≥ {CONF_THRESH})', fontsize=14, fontweight='bold')

for ax, img_path in zip(axes.flat, sample_paths):
    t0 = time.time()
    preds = best_model.predict(img_path, conf=CONF_THRESH, iou=IOU_THRESH, verbose=False)
    ms    = (time.time() - t0) * 1000

    result = preds[0]
    vis    = result.plot(line_width=2, font_size=10)
    vis    = cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)

    ax.imshow(vis)
    n_det = len(result.boxes)
    ax.set_title(f'{Path(img_path).name}\n{n_det} det | {ms:.0f} ms', fontsize=8)
    ax.axis('off')

plt.tight_layout()
plt.savefig('results/sample_predictions.png', dpi=150, bbox_inches='tight')
plt.show()
print('Saved → results/sample_predictions.png')

# %%
# ── Confidence score distribution across all test images ─────────────────────
all_confs   = []
all_classes = []

for img_path in test_img_paths:
    preds = best_model.predict(img_path, conf=0.01, verbose=False)  # low thresh for distribution
    result = preds[0]
    if len(result.boxes):
        all_confs.extend(result.boxes.conf.cpu().numpy().tolist())
        all_classes.extend([result.names[int(c)] for c in result.boxes.cls.cpu().numpy()])

if all_confs:
    df_confs = pd.DataFrame({'confidence': all_confs, 'class': all_classes})

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(df_confs['confidence'], bins=40, color='steelblue', edgecolor='white')
    axes[0].axvline(CONF_THRESH, color='tomato', linestyle='--', label=f'threshold={CONF_THRESH}')
    axes[0].set_xlabel('Confidence')
    axes[0].set_ylabel('Count')
    axes[0].set_title('Confidence Score Distribution')
    axes[0].legend()
    axes[0].grid(alpha=0.3)

    class_counts = df_confs[df_confs['confidence'] >= CONF_THRESH]['class'].value_counts()
    axes[1].bar(class_counts.index, class_counts.values, color='mediumseagreen', edgecolor='white')
    axes[1].set_xlabel('Class')
    axes[1].set_ylabel('Detections')
    axes[1].set_title(f'Detections per Class (conf ≥ {CONF_THRESH})')
    axes[1].tick_params(axis='x', rotation=35)
    axes[1].grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig('results/confidence_distribution.png', dpi=150, bbox_inches='tight')
    plt.show()

# %% [markdown]
# ## 6. Speed Benchmark

# %%
bench_img = test_img_paths[0]
WARMUP    = 20
RUNS      = 200

# Warm-up
for _ in range(WARMUP):
    best_model.predict(bench_img, verbose=False)

# Benchmark
t0 = time.time()
for _ in range(RUNS):
    best_model.predict(bench_img, verbose=False)
total = time.time() - t0

avg_ms = total / RUNS * 1000
fps    = 1000 / avg_ms

print(f'Benchmark  ({RUNS} runs, warmup {WARMUP})')
print(f'  Avg latency : {avg_ms:.2f} ms/image')
print(f'  Throughput  : {fps:.1f} FPS')

# %% [markdown]
# ## 7. Export Models

# %%
# ── Export to ONNX ────────────────────────────────────────────────────────────
# opset=12 for broadest compatibility; dynamic=True allows variable batch sizes
best_model.export(
    format   = 'onnx',
    imgsz    = IMG_SIZE,
    opset    = 12,
    dynamic  = True,
    simplify = True,
)

BEST_ONNX = BEST_PT.with_suffix('.onnx')
print(f'ONNX model  → {BEST_ONNX}')
print(f'PyTorch model → {BEST_PT}')

# %%
# ── Quick ONNX smoke-test ─────────────────────────────────────────────────────
import onnxruntime as ort

sess = ort.InferenceSession(str(BEST_ONNX), providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
inp  = sess.get_inputs()[0]
print(f'ONNX input  : name={inp.name}  shape={inp.shape}  type={inp.type}')
print(f'ONNX providers in use: {sess.get_providers()}')
print('ONNX model verified ✅')

# %% [markdown]
# ## 8. Download Artefacts

# %%
from google.colab import drive
drive.mount('/content/drive')

SAVE_DIR = '/content/drive/MyDrive/skin_disease_model'
os.makedirs(SAVE_DIR, exist_ok=True)

# %%
import shutil

# Copy weights
shutil.copy(BEST_PT,   f'{SAVE_DIR}/best.pt')
shutil.copy(BEST_ONNX, f'{SAVE_DIR}/best.onnx')

# Copy data.yaml (you'll need it for the app)
shutil.copy(DATA_YAML, f'{SAVE_DIR}/data.yaml')

print(f'Model saved to Google Drive → {SAVE_DIR}')

# %% [markdown]
# ## 9. Summary

# %%
print('=' * 55)
print('  SKIN DISEASE DETECTION — YOLO11s — SUMMARY')
print('=' * 55)
print(f'  Model          : {MODEL_WEIGHTS}')
print(f'  Dataset        : {train_imgs + val_imgs + test_imgs} images | {NUM_CLASSES} classes')
print(f'  Classes        : {", ".join(CLASS_NAMES)}')
print(f'  Training time  : {elapsed/60:.1f} min')
print()
print('  Metrics (test split):')
print(f'    mAP@0.5      : {map50*100:.1f}%')
print(f'    mAP@0.5-0.95 : {map5095*100:.1f}%')
print(f'    Precision    : {mp*100:.1f}%')
print(f'    Recall       : {mr*100:.1f}%')
print(f'    F1-Score     : {f1*100:.1f}%')
print()
print(f'  Inference speed: {avg_ms:.1f} ms/image  ({fps:.0f} FPS)')
print()
print('  Saved artefacts:')
print(f'    best.pt   → {BEST_PT}')
print(f'    best.onnx → {BEST_ONNX}')
print('=' * 55)

# %%



