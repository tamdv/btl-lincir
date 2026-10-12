"""[NHOM8] Illustrations for the report (method and data), independent of experiment results.

  report/figures/cir_example.png     a real FashionIQ val query: reference image + relative captions -> target image
  report/figures/lincir_train.png    LinCIR training (Self-Masking Projection) with the group's changes A and B
  report/figures/lincir_infer.png    zero-shot CIR inference with the trained projection phi

Usage: python report/make_figures.py [--fiq data/FashionIQ]
"""
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from PIL import Image

OUT = Path(__file__).resolve().parent / "figures"
plt.rcParams["font.family"] = "DejaVu Sans"

FROZEN, TRAIN, DATA, NEW = "#dbe4f0", "#f6d7b0", "#e8e8e8", "#c9e8cf"


def box(ax, x, y, w, h, text, color, fs=9, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05", fc=color, ec="#333333", lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, weight="bold" if bold else "normal", wrap=True)


def arrow(ax, x1, y1, x2, y2, text=None, style="-|>", color="#333333", ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=12, color=color, lw=1.2, linestyle=ls))
    if text:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, text, ha="center", fontsize=8, color=color)


def cir_example(fiq, scale=1.0, suffix=""):
    caps = json.load(open(Path(fiq) / "captions" / "cap.dress.val.json"))
    t = next(c for c in caps if c["candidate"] == "B005X4PL1G") if any(c["candidate"] == "B005X4PL1G" for c in caps) else caps[0]
    img = lambda n: Image.open(Path(fiq) / "images" / f"{n}.jpg").convert("RGB")
    fig = plt.figure(figsize=(9 * scale, 3.2 * scale))
    ax1 = fig.add_axes([0.02, 0.08, 0.22, 0.8])
    ax1.imshow(img(t["candidate"]))
    ax1.set_title("Ảnh tham chiếu", fontsize=10)
    ax_mid = fig.add_axes([0.26, 0.08, 0.46, 0.8])
    ax_mid.axis("off")
    ax_mid.set_xlim(0, 1)
    ax_mid.set_ylim(0, 1)
    ax_mid.text(0.5, 0.85, "+ văn bản điều chỉnh", ha="center", fontsize=10, weight="bold")
    ax_mid.text(0.5, 0.64, f"\"{t['captions'][0]}\"\n\"{t['captions'][1]}\"", ha="center", va="center", fontsize=10, style="italic")
    arrow(ax_mid, 0.08, 0.25, 0.92, 0.25)
    ax_mid.text(0.5, 0.3, "hệ thống CIR tìm trong kho ảnh", ha="center", fontsize=9, color="#333333")
    ax2 = fig.add_axes([0.76, 0.08, 0.22, 0.8])
    ax2.imshow(img(t["target"]))
    ax2.set_title("Ảnh đích", fontsize=10)
    for ax in (ax1, ax2):
        ax.set_xticks([])
        ax.set_yticks([])
    fig.savefig(OUT / f"cir_example{suffix}.png", dpi=200 / scale)
    plt.close(fig)


def lincir_train(scale=1.0, suffix=""):
    fig, ax = plt.subplots(figsize=(10 * scale, 4.6 * scale))
    ax.set_xlim(0, 10.15)
    ax.set_ylim(0, 4.7)
    ax.axis("off")
    box(ax, 0.1, 3.4, 2.2, 0.8, "Câu mô tả x_c\n\"gray cat sleeps\non a pillow\"", DATA)
    box(ax, 2.7, 3.4, 2.35, 0.8, "Bộ mã hóa văn bản C\n(đóng băng)", FROZEN)
    arrow(ax, 2.3, 3.8, 2.7, 3.8)
    box(ax, 5.4, 3.4, 1.2, 0.8, "z_c", DATA, fs=11, bold=True)
    arrow(ax, 5.05, 3.8, 5.4, 3.8)
    box(ax, 5.15, 2.05, 1.7, 0.8, "+ nhiễu n\nU(0,1)·N(0,I)\n(+ α·Δ — B)", NEW, fs=8)
    arrow(ax, 6.0, 3.4, 6.0, 2.85)
    box(ax, 7.3, 2.05, 1.5, 0.8, "φ (MLP 3 lớp)\nhuấn luyện", TRAIN, bold=True)
    arrow(ax, 6.85, 2.45, 7.3, 2.45)
    box(ax, 7.3, 0.6, 1.5, 0.8, "token giả ê_c\n[$]", TRAIN)
    arrow(ax, 8.05, 2.05, 8.05, 1.4)
    box(ax, 0.1, 1.95, 2.2, 1.0, "Che từ khóa (spaCy):\n\"[\\$] sleeps on [\\$]\"", DATA)
    arrow(ax, 1.2, 3.4, 1.2, 2.95)
    ax.text(1.3, 3.15, "tính từ + danh từ", fontsize=8, color="#333333")
    box(ax, 2.7, 0.6, 2.35, 0.8, "Bộ mã hóa văn bản C\n(đóng băng)", FROZEN)
    arrow(ax, 1.2, 1.95, 2.7, 1.0)
    arrow(ax, 7.3, 1.0, 5.05, 1.0, "thay [$] bằng ê_c")
    box(ax, 5.4, 0.05, 1.2, 0.55, "ẑ_c", DATA, fs=11, bold=True)
    arrow(ax, 3.9, 0.6, 5.4, 0.33)
    box(ax, 8.7, 3.4, 1.4, 0.8, "MSE(z_c, ẑ_c)\n+ λ·InfoNCE (A)", NEW, fs=8)
    arrow(ax, 6.6, 3.8, 8.7, 3.8, color="#888888", ls="--")
    ax.plot([6.6, 9.4], [0.33, 0.33], color="#888888", lw=1.2, ls="--")
    arrow(ax, 9.4, 0.33, 9.4, 3.4, color="#888888", ls="--")
    ax.text(0.1, 4.45, "Xanh dương: đóng băng · Cam: được huấn luyện · Xanh lá: phần nhóm bổ sung", fontsize=8, color="#555555")
    fig.savefig(OUT / f"lincir_train{suffix}.png", dpi=200 / scale, bbox_inches="tight")
    plt.close(fig)


def lincir_infer(scale=1.0, suffix=""):
    fig, ax = plt.subplots(figsize=(10 * scale, 3.0 * scale))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    box(ax, 0.1, 1.8, 1.6, 0.8, "Ảnh tham chiếu", DATA)
    box(ax, 2.1, 1.8, 1.7, 0.8, "Bộ mã hóa ảnh\nI (đóng băng)", FROZEN)
    arrow(ax, 1.7, 2.2, 2.1, 2.2)
    box(ax, 4.2, 1.8, 1.5, 0.8, "φ đã\nhuấn luyện", TRAIN)
    arrow(ax, 3.8, 2.2, 4.2, 2.2)
    box(ax, 0.1, 0.4, 3.7, 0.8, "\"a photo of [$] that\n{văn bản điều chỉnh}\"", DATA)
    box(ax, 4.2, 0.4, 1.9, 0.8, "Bộ mã hóa\nvăn bản C", FROZEN)
    arrow(ax, 3.8, 0.8, 4.2, 0.8)
    arrow(ax, 4.95, 1.8, 4.95, 1.2)
    ax.text(5.05, 1.45, "[$]", fontsize=8, color="#333333")
    box(ax, 6.5, 0.4, 1.4, 0.8, "vector\ntruy vấn q", DATA)
    arrow(ax, 6.1, 0.8, 6.5, 0.8)
    box(ax, 6.5, 1.8, 1.4, 0.8, "Kho ảnh\n(đã mã hóa I)", FROZEN)
    box(ax, 8.3, 1.1, 1.6, 0.8, "Xếp hạng theo\ncosine(q, ảnh)", NEW)
    arrow(ax, 7.9, 0.8, 8.3, 1.3)
    arrow(ax, 7.9, 2.2, 8.3, 1.7)
    fig.savefig(OUT / f"lincir_infer{suffix}.png", dpi=200 / scale, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fiq", default=str(Path(__file__).resolve().parents[1] / "data" / "FashionIQ"))
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    cir_example(a.fiq)
    lincir_train()
    lincir_infer()
    # slide versions: smaller canvas -> text ~1.6x larger once stretched to slide width
    cir_example(a.fiq, 0.8, "_slide")
    lincir_train(0.88, "_slide")
    lincir_infer(0.9, "_slide")
    print(sorted(p.name for p in OUT.glob("*.png")))
