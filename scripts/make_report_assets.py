"""[NHOM8] Build every table and figure of the report from the run folders.

Reads experiments/runs/<run>/ (metrics.json, per_query_*.csv, topk_*.json, curve/, train_metrics.json) and
experiments/gap_projection_large.json, writes:

  results/tables/main_results.{md,csv}   mean ± std over seeds, FashionIQ per category + average, CIRCO mAP@K
  results/tables/significance.md         each improvement vs baseline: Δ, 95% CI, paired bootstrap, Wilcoxon
  results/tables/ablation.md             components on/off and Δ vs baseline
  results/figures/learning_curve.png     FashionIQ avg R@10/R@50 vs step (baseline, A; seed 12345)
  results/figures/modality_gap.png       phi consistency on image vs text inputs (COCO val pairs)
  results/figures/qualitative_fiq_*.png  reference image + caption, top-5 of baseline vs best variant
  results/assets.json                    all numbers above, for the report generator

Usage: python scripts/make_report_assets.py [--root .] [--fiq data/FashionIQ] [--best A]
"""
import argparse
import csv
import json
import random
import statistics
from pathlib import Path

import stats_compare as sc

VARIANTS = [  # (label, exp prefix, InfoNCE, gap noise)
    ("Checkpoint chính thức", "EXP-000-official", None, None),
    ("Baseline (LinCIR)", "EXP-001-baseline", False, False),
    ("A: + InfoNCE", "EXP-002-infonce", True, False),
    ("B: + nhiễu có hướng", "EXP-003-gapnoise", False, True),
    ("A+B", "EXP-004-infonce-gapnoise", True, True),
]
SHORT = {"EXP-001-baseline": "baseline", "EXP-002-infonce": "A", "EXP-003-gapnoise": "B", "EXP-004-infonce-gapnoise": "A+B"}
DRESSES = ["dress", "shirt", "toptee"]
MAIN_METRICS = [
    ("dress_fiq_recall_at10", "Dress R@10"), ("dress_fiq_recall_at50", "Dress R@50"),
    ("shirt_fiq_recall_at10", "Shirt R@10"), ("shirt_fiq_recall_at50", "Shirt R@50"),
    ("toptee_fiq_recall_at10", "Toptee R@10"), ("toptee_fiq_recall_at50", "Toptee R@50"),
    ("average_fiq_recall_at10", "FIQ TB R@10"), ("average_fiq_recall_at50", "FIQ TB R@50"),
    ("circo_map_at5", "CIRCO mAP@5"), ("circo_map_at10", "CIRCO mAP@10"),
    ("circo_map_at25", "CIRCO mAP@25"), ("circo_map_at50", "CIRCO mAP@50"),
]


def run_dirs(root, prefix):
    return sorted(d for d in (root / "experiments" / "runs").glob(f"{prefix}-s*")
                  if (d / "metrics.json").exists() and not d.name.endswith(("-mac", "-kaggle-toy")))


def fmt(vals):
    vals = [v for v in vals if v is not None]
    if not vals:
        return "—"
    if len(vals) == 1:
        return f"{vals[0]:.2f}"
    return f"{statistics.mean(vals):.2f} ± {statistics.stdev(vals):.2f}"


def md_table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(map(str, r)) + " |" for r in rows]
    return "\n".join(out) + "\n"


def main_results(root, assets):
    header = ["Biến thể", "Số seed"] + [n for _, n in MAIN_METRICS] + ["Giờ train"]
    rows, csv_rows = [], []
    for label, prefix, *_ in VARIANTS:
        dirs = run_dirs(root, prefix)
        if not dirs:
            continue
        ms = [json.load(open(d / "metrics.json")) for d in dirs]
        tms = [json.load(open(d / "train_metrics.json")) for d in dirs if (d / "train_metrics.json").exists()]
        cells = [fmt([m.get(k) for m in ms]) for k, _ in MAIN_METRICS]
        hours = fmt([t.get("train_hours") for t in tms]) if tms else "—"
        rows.append([label, len(dirs), *cells, hours])
        assets["main"][prefix] = {"label": label, "n_seeds": len(dirs), "runs": [d.name for d in dirs],
                                  **{k: [m.get(k) for m in ms] for k, _ in MAIN_METRICS},
                                  "train_hours": [t.get("train_hours") for t in tms]}
        csv_rows.append([label, len(dirs), *cells, hours])
    out = root / "results" / "tables"
    (out / "main_results.md").write_text("# Kết quả chính (trung bình ± độ lệch chuẩn qua seed)\n\n" + md_table(header, rows))
    with open(out / "main_results.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(csv_rows)
    return rows


def _fiq_side(dirs):
    """per seed: {query_id: rank} over the three FashionIQ categories"""
    per_seed = []
    for d in dirs:
        merged = {}
        for dress in DRESSES:
            p = d / f"per_query_fiq_{dress}.csv"
            if p.exists():
                merged.update(sc.load_side([str(p)])[1][0])
        per_seed.append(merged)
    return per_seed


def _circo_side(dirs):
    return [sc.load_side([str(d / "per_query_circo.csv")], ["ap5", "ap10", "ap25", "ap50"])[1][0]
            for d in dirs if (d / "per_query_circo.csv").exists()]


def _compare(base, new, keys, n_boot, rng):
    qids = sorted(set.intersection(*[set(s) for s in base + new]))
    res = []
    for k in keys:
        a, b = sc.per_query_scores(base, qids, k), sc.per_query_scores(new, qids, k)
        delta, ci, p = sc.paired_bootstrap(a, b, n_boot, rng)
        res.append({"metric": k if isinstance(k, str) else f"R@{k}", "n_queries": len(qids),
                    "base": 100 * sum(a) / len(a), "new": 100 * sum(b) / len(b), "delta": 100 * delta,
                    "ci95": [100 * ci[0], 100 * ci[1]], "p_boot": p, "p_wilcoxon": sc.wilcoxon(a, b)})
    return res


def significance(root, assets, n_boot):
    rng = random.Random(0)
    base_dirs = run_dirs(root, "EXP-001-baseline")
    if not base_dirs:
        return
    rows = []
    for label, prefix, *_ in VARIANTS[2:]:
        dirs = run_dirs(root, prefix)
        if not dirs:
            continue
        comp = []
        fb, fn = _fiq_side(base_dirs), _fiq_side(dirs)
        if fb and fb[0] and fn and fn[0]:
            comp += [{"dataset": "FashionIQ", **r} for r in _compare(fb, fn, [10, 50], n_boot, rng)]
        cb, cn = _circo_side(base_dirs), _circo_side(dirs)
        if cb and cn:
            comp += [{"dataset": "CIRCO", **r} for r in _compare(cb, cn, ["ap5", "ap10", "ap25", "ap50"], n_boot, rng)]
        assets["significance"][prefix] = comp
        for r in comp:
            pw = "—" if r["p_wilcoxon"] is None else f"{r['p_wilcoxon']:.4f}"
            verdict = "tốt hơn có ý nghĩa" if r["delta"] > 0 and r["p_boot"] < 0.05 else (
                "kém hơn" if r["delta"] < 0 and r["ci95"][1] < 0 else "chưa đủ bằng chứng")
            rows.append([label, r["dataset"], r["metric"].replace("ap", "mAP@"), f"{r['base']:.2f}", f"{r['new']:.2f}",
                         f"{r['delta']:+.2f}", f"[{r['ci95'][0]:+.2f}, {r['ci95'][1]:+.2f}]", f"{r['p_boot']:.4f}", pw, verdict])
    header = ["So với baseline", "Tập", "Chỉ số", "Baseline", "Cải tiến", "Δ", "KTC 95%", "p (bootstrap)", "p (Wilcoxon)", "Kết luận"]
    (root / "results" / "tables" / "significance.md").write_text(
        "# Kiểm định ý nghĩa (theo truy vấn, trung bình qua seed; bootstrap 1 phía 10.000 lần)\n\n" + md_table(header, rows))


def ablation(root, assets):
    base = assets["main"].get("EXP-001-baseline")
    if not base:
        return
    keys = [("average_fiq_recall_at10", "FIQ TB R@10"), ("average_fiq_recall_at50", "FIQ TB R@50"), ("circo_map_at5", "CIRCO mAP@5")]
    mean = lambda v: statistics.mean([x for x in v if x is not None]) if any(x is not None for x in v) else None
    rows = []
    for label, prefix, infonce, gap in VARIANTS[1:]:
        m = assets["main"].get(prefix)
        if not m:
            continue
        cells = []
        for k, _ in keys:
            v, b = mean(m[k]), mean(base[k])
            cells.append("—" if v is None else (f"{v:.2f}" if prefix == "EXP-001-baseline" else f"{v:.2f} ({v - b:+.2f})"))
        rows.append([label, "✓" if infonce else "", "✓" if gap else "", *cells])
    header = ["Biến thể", "InfoNCE (A)", "Nhiễu có hướng (B)"] + [n for _, n in keys]
    (root / "results" / "tables" / "ablation.md").write_text("# Ablation (trung bình qua seed; ngoặc: Δ so với baseline)\n\n" + md_table(header, rows))


def learning_curve(root, assets, plt):
    series = {}
    for prefix, label in (("EXP-001-baseline", "Baseline"), ("EXP-002-infonce", "A: + InfoNCE")):
        d = root / "experiments" / "runs" / f"{prefix}-s12345"
        pts = []
        for m in sorted((d / "curve").glob("step_*/metrics.json")):
            j = json.load(open(m))
            pts.append((int(m.parent.name.split("_")[1]), j["average_fiq_recall_at10"], j["average_fiq_recall_at50"]))
        if (d / "metrics.json").exists():
            j = json.load(open(d / "metrics.json"))
            steps = json.load(open(d / "train_metrics.json"))["steps"] if (d / "train_metrics.json").exists() else 5000
            if "average_fiq_recall_at10" in j:
                pts.append((steps, j["average_fiq_recall_at10"], j["average_fiq_recall_at50"]))
        if len(pts) >= 2:
            series[label] = sorted(pts)
    if not series:
        return
    assets["curve"] = series
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    for label, pts in series.items():
        st = [p[0] for p in pts]
        axes[0].plot(st, [p[1] for p in pts], marker="o", label=label)
        axes[1].plot(st, [p[2] for p in pts], marker="o", label=label)
    for ax, t in zip(axes, ("FashionIQ R@10 (TB)", "FashionIQ R@50 (TB)")):
        ax.set_xlabel("Số bước huấn luyện")
        ax.set_title(t)
        ax.grid(alpha=0.3)
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(root / "results" / "figures" / "learning_curve.png", dpi=200)
    plt.close(fig)
    with plt.rc_context({"font.size": 15}):  # slide version: one panel (R@10), large text
        fig, ax = plt.subplots(figsize=(6.2, 4.2))
        for label, pts in series.items():
            ax.plot([p[0] for p in pts], [p[1] for p in pts], marker="o", lw=2.5, label=label)
        ax.set_xlabel("Số bước huấn luyện")
        ax.set_ylabel("FashionIQ R@10 (TB)")
        ax.grid(alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(root / "results" / "figures" / "learning_curve_slide.png", dpi=200)
        plt.close(fig)


def modality_gap(root, assets, plt):
    p = root / "experiments" / "gap_projection_large.json"
    if not p.exists():
        return
    g = json.load(open(p))
    assets["modality_gap"] = g
    proj = g.get("projection", {})
    if not proj:
        return
    labels = list(proj)
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    axes[0].bar(labels, [proj[l]["paired_cosine"] for l in labels], color="#4C72B0")
    axes[0].set_title("Cosine (φ(ảnh) vs φ(văn bản)) ↑")
    axes[1].bar(labels, [proj[l]["centroid_gap"] for l in labels], color="#DD8452")
    axes[1].set_title("Khoảng cách tâm ↓")
    for ax in axes:
        ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(root / "results" / "figures" / "modality_gap.png", dpi=200)
    plt.close(fig)
    with plt.rc_context({"font.size": 15}):  # slide version: the consistency score only, large text
        fig, ax = plt.subplots(figsize=(6.2, 4.2))
        bars = ax.bar(labels, [proj[l]["paired_cosine"] for l in labels], color="#1E6FE8")
        ax.bar_label(bars, labels=[f"{proj[l]['paired_cosine']:.2f}".replace(".", ",") for l in labels], padding=3)
        ax.set_ylabel("cosine φ(ảnh) – φ(văn bản)")
        ax.set_ylim(0, max(proj[l]["paired_cosine"] for l in labels) * 1.15)
        ax.grid(axis="y", alpha=0.3)
        fig.tight_layout()
        fig.savefig(root / "results" / "figures" / "modality_gap_slide.png", dpi=200)
        plt.close(fig)


def qualitative(root, assets, plt, fiq_root, best_prefix, n_examples=3):
    from PIL import Image
    if not fiq_root or not Path(fiq_root).exists():
        return
    b_dir = root / "experiments" / "runs" / "EXP-001-baseline-s12345"
    n_dir = root / "experiments" / "runs" / f"{best_prefix}-s12345"
    if not (b_dir / "topk_fiq_dress.json").exists() or not (n_dir / "topk_fiq_dress.json").exists():
        return
    picks = []
    for dress in DRESSES:
        tb, tn = json.load(open(b_dir / f"topk_fiq_{dress}.json")), json.load(open(n_dir / f"topk_fiq_{dress}.json"))
        caps = json.load(open(Path(fiq_root) / "captions" / f"cap.{dress}.val.json"))
        for q, top_n in tn.items():
            i = int(q.split("_")[1])
            t = caps[i]
            if t["target"] in top_n[:1] and t["target"] not in tb[q][:5]:
                picks.append((dress, q, t, tb[q][:5], top_n[:5]))
    random.Random(0).shuffle(picks)
    assets["qualitative"] = []
    for j, (dress, q, t, top_b, top_n) in enumerate(picks[:n_examples]):
        fig, axes = plt.subplots(2, 6, figsize=(12, 4.8))
        img = lambda name: Image.open(Path(fiq_root) / "images" / f"{name}.jpg").convert("RGB")
        for r, (row_label, tops) in enumerate((("Baseline", top_b), (SHORT.get(best_prefix, best_prefix), top_n))):
            axes[r][0].imshow(img(t["candidate"]))
            axes[r][0].set_title("Ảnh truy vấn" if r == 0 else "", fontsize=9)
            axes[r][0].set_ylabel(row_label, fontsize=10)
            for c, name in enumerate(tops, start=1):
                axes[r][c].imshow(img(name))
                hit = name == t["target"]
                axes[r][c].set_title(f"#{c}" + (" ✓ đích" if hit else ""), fontsize=9, color="green" if hit else "black")
                for sp in axes[r][c].spines.values():
                    sp.set_edgecolor("green" if hit else "#cccccc")
                    sp.set_linewidth(3 if hit else 1)
            for ax in axes[r]:
                ax.set_xticks([])
                ax.set_yticks([])
        fig.suptitle(f"[{dress}] \"{t['captions'][0]}\" và \"{t['captions'][1]}\"", fontsize=10)
        fig.tight_layout()
        out = root / "results" / "figures" / f"qualitative_fiq_{j + 1}.png"
        fig.savefig(out, dpi=150)
        plt.close(fig)
        assets["qualitative"].append({"file": out.name, "dress": dress, "query": q, "captions": t["captions"]})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--fiq", default="data/FashionIQ", help="local FashionIQ (images) for qualitative figures")
    ap.add_argument("--best", default="EXP-002-infonce", help="variant shown against the baseline in qualitative figures")
    ap.add_argument("--n_boot", type=int, default=10000)
    a = ap.parse_args()
    root = Path(a.root)
    (root / "results" / "tables").mkdir(parents=True, exist_ok=True)
    (root / "results" / "figures").mkdir(parents=True, exist_ok=True)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.family"] = "DejaVu Sans"
    assets = {"main": {}, "significance": {}}
    main_results(root, assets)
    significance(root, assets, a.n_boot)
    ablation(root, assets)
    learning_curve(root, assets, plt)
    modality_gap(root, assets, plt)
    fiq = a.fiq if Path(a.fiq).is_absolute() else str(root / a.fiq)
    qualitative(root, assets, plt, fiq, a.best)
    (root / "results" / "assets.json").write_text(json.dumps(assets, indent=1, ensure_ascii=False))
    for p in sorted((root / "results").rglob("*")):
        if p.is_file():
            print(p.relative_to(root))


if __name__ == "__main__":
    main()
