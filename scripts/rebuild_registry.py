"""[NHOM8] Rebuild experiments/registry.csv rows from run folders (e.g. after copying runs back from Kaggle).

Each experiments/runs/<run_id>/ with config.yaml is (re)written as one row; rows without a run folder are kept.
Usage: python scripts/rebuild_registry.py
"""
import json
from pathlib import Path

import yaml

import csv

import run_experiment as rx

existing = {}
if rx.REGISTRY.exists():
    with open(rx.REGISTRY, newline="") as f:
        existing = {r["run_id"]: r for r in csv.DictReader(f)}


def merge(row):
    """keep values already in the registry (owner, started, git_commit, …) unless the run folder gives a new one"""
    old = existing.get(row["run_id"], {})
    return {**old, **{k: v for k, v in row.items() if v not in ("", None) or k not in old}}


for d in sorted((rx.ROOT / "experiments" / "runs").iterdir()):
    if not (d / "config.yaml").exists():
        continue
    cfg = yaml.safe_load(open(d / "config.yaml"))
    t = cfg.get("train_args") or {}
    m = json.load(open(d / "metrics.json")) if (d / "metrics.json").exists() else {}
    tm = json.load(open(d / "train_metrics.json")) if (d / "train_metrics.json").exists() else {}
    fmt = lambda x: "" if x is None else f"{x:.2f}"
    rx.registry_upsert(merge({
        "run_id": d.name, "exp": cfg["exp"], "variant": cfg["name"], "seed": cfg.get("seed", ""),
        "backbone": t.get("clip_model_name", cfg.get("clip_model_name", "large")),
        "train_data": Path(t["train_captions_file"]).name if t.get("train_captions_file") else " ".join(t.get("caption_datasets", ["dataset1", "dataset2", "dataset3"])),
        "max_steps": t.get("max_train_steps", ""),
        "status": "done" if m else ("trained" if tm.get("steps") else "failed"),  # trained = waiting for evaluation
        "best_step": (tm.get("best") or {}).get("step", tm.get("steps", "")),
        "cirr_dev_r1": fmt(m.get("cirr_recall_at1")), "cirr_dev_r5": fmt(m.get("cirr_recall_at5")),
        "cirr_dev_r10": fmt(m.get("cirr_recall_at10")), "cirr_dev_r50": fmt(m.get("cirr_recall_at50")),
        "fiq_avg_r10": fmt(m.get("average_fiq_recall_at10")), "fiq_avg_r50": fmt(m.get("average_fiq_recall_at50")),
        "circo_map5": fmt(m.get("circo_map_at5")), "circo_map10": fmt(m.get("circo_map_at10")),
        "train_hours": tm.get("train_hours", ""), "gpu": m.get("device", tm.get("device", "")),
        "notes": cfg.get("description", ""),
    }))
    print("row:", d.name)
