"""[NHOM8] Run one experiment config for one seed: train -> per-query eval -> registry row.

  python scripts/run_experiment.py configs/EXP-002-infonce.yaml --seed 12345 \
      --cirr /kaggle/input/cirr --fiq /kaggle/input/fashioniq [--nproc 2] [--dry_run]

- Run id: <exp>-<name>-s<seed>; outputs in experiments/runs/<run id>/ (train.log, eval.log, checkpoints/,
  train_metrics.json, metrics.json, per_query_*.csv, command.txt, config.yaml).
- Paths inside `train_args` are relative to the project root. Data paths come from the command line, so the
  same config works on Kaggle and on the Mac.
- A config with `eval_only: <checkpoint>` skips training (e.g. the official checkpoint, EXP-000).
- Refuses to reuse an existing run directory: rerun with a new suffix, written as --suffix=-r2.
"""
import argparse
import csv
import datetime as dt
import json
import shlex
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "experiments" / "registry.csv"
PATH_ARGS = {"gap_vector_path", "idf_path", "train_captions_file"}


def now():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip() or "nogit"
    except FileNotFoundError:
        return "nogit"


def registry_upsert(row):
    rows, fields = [], None
    if REGISTRY.exists():
        with open(REGISTRY, newline="") as f:
            r = csv.DictReader(f)
            fields, rows = r.fieldnames, list(r)
    fields = fields or list(row)
    rows = [x for x in rows if x["run_id"] != row["run_id"]] + [{k: row.get(k, "") for k in fields}]
    with open(REGISTRY, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def run(cmd, cwd, log_path, dry):
    print("$", " ".join(shlex.quote(c) for c in cmd), f"  (cwd={cwd})")
    if dry:
        return 0
    with open(log_path, "w") as log:
        p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            sys.stdout.write(line)
            log.write(line)
        return p.wait()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--cirr", help="CIRR root (validation during training + eval)")
    ap.add_argument("--fiq", help="FashionIQ root (eval)")
    ap.add_argument("--circo", help="CIRCO root (eval)")
    ap.add_argument("--eval_only", action="store_true", help="skip training; evaluate the existing run folder again")
    ap.add_argument("--nproc", type=int, default=1, help="GPUs (torchrun). Note: InfoNCE negatives are per GPU")
    ap.add_argument("--owner", default="")
    ap.add_argument("--suffix", default="", help="appended to the run id, e.g. -r2 or -smoke")
    ap.add_argument("--set", nargs="*", default=[], help="override train args, e.g. --set max_train_steps=50")
    ap.add_argument("--python", default=sys.executable)
    ap.add_argument("--dry_run", action="store_true")
    a = ap.parse_args()

    a.cirr = a.cirr and str(Path(a.cirr).resolve())  # commands run from code/, so make data paths absolute
    a.fiq = a.fiq and str(Path(a.fiq).resolve())
    a.circo = a.circo and str(Path(a.circo).resolve())
    cfg = yaml.safe_load(open(a.config))
    run_id = f"{cfg['exp']}-{cfg['name']}-s{a.seed}{a.suffix}"
    cfg_path = Path(a.config).resolve()
    if a.eval_only and cfg_path.name == "config.yaml" and cfg_path.parent.parent.name == "runs":
        run_id = cfg_path.parent.name  # re-evaluating an existing run folder: keep its exact name
    run_dir = ROOT / "experiments" / "runs" / run_id
    if run_dir.exists() and not a.dry_run and not a.eval_only:
        sys.exit(f"{run_dir} already exists; use --suffix=-r2 for a rerun")
    if not a.dry_run:
        run_dir.mkdir(parents=True, exist_ok=a.eval_only)
    targs = dict(cfg.get("train_args") or {})
    for kv in a.set:
        k, v = kv.split("=", 1)
        targs[k] = yaml.safe_load(v)
    if not a.dry_run and not (a.eval_only and (run_dir / "config.yaml").exists()):
        (run_dir / "config.yaml").write_text(yaml.safe_dump({**cfg, "train_args": targs, "seed": a.seed}, sort_keys=False, allow_unicode=True))

    row = {"run_id": run_id, "exp": cfg["exp"], "variant": cfg["name"], "seed": a.seed,
           "backbone": targs.get("clip_model_name", cfg.get("clip_model_name", "large")),
           "train_data": (Path(targs["train_captions_file"]).name if targs.get("train_captions_file") else
                          " ".join(targs.get("caption_datasets", ["dataset1", "dataset2", "dataset3"]))) +
                         (f" max={targs['max_captions']}" if targs.get("max_captions") else ""),
           "max_steps": targs.get("max_train_steps", ""), "git_commit": git_commit(), "owner": a.owner,
           "status": "running", "started": now(), "notes": cfg.get("description", "")}
    if not a.dry_run:
        registry_upsert(row)

    phi = cfg.get("eval_only")
    if a.eval_only and not phi:
        ckpts = run_dir / "checkpoints"
        phi = str(ckpts / "phi_best.pt") if (ckpts / "phi_best.pt").exists() else str(ckpts / "phi_latest.pt")
    if not phi:
        train = [a.python, "train_phi.py"] if a.nproc == 1 else \
                [a.python, "-m", "torch.distributed.run", "--nproc_per_node", str(a.nproc), "train_phi.py"]
        args = {**targs, "seed": a.seed, "output_dir": str(run_dir)}
        if a.cirr:
            args["cirr_dataset_path"] = a.cirr
        for k, v in args.items():
            if k in PATH_ARGS and v and not Path(v).is_absolute():
                v = str(ROOT / v)
            if isinstance(v, bool):
                if v:
                    train.append(f"--{k}")
            elif isinstance(v, list):
                train += [f"--{k}", *map(str, v)]
            else:
                train += [f"--{k}", str(v)]
        if not a.dry_run:
            (run_dir / "command.txt").write_text(" ".join(shlex.quote(c) for c in train) + "\n")
        if run(train, ROOT / "code", run_dir / "train.log", a.dry_run) != 0:
            row.update(status="failed", finished=now(), notes=row["notes"] + " | training failed, see train.log")
            registry_upsert(row) if not a.dry_run else None
            sys.exit(1)
        ckpt = run_dir / "checkpoints" / ("phi_best.pt" if a.cirr else "phi_latest.pt")
        phi = str(ckpt)

    if a.cirr or a.fiq or a.circo:
        ev = [a.python, str(ROOT / "scripts" / "eval_per_query.py"), "--phi", phi, "--out_dir", str(run_dir),
              "--clip_model_name", row["backbone"], "--feature_cache", str(ROOT / "experiments" / "feature_cache")]
        ev += (["--cirr", a.cirr] if a.cirr else []) + (["--fiq", a.fiq] if a.fiq else []) + (["--circo", a.circo] if a.circo else [])
        if run(ev, ROOT / "code", run_dir / "eval.log", a.dry_run) != 0:
            row.update(status="failed", finished=now(), notes=row["notes"] + " | eval failed, see eval.log")
            registry_upsert(row) if not a.dry_run else None
            sys.exit(1)
    if a.dry_run:
        return

    m = json.load(open(run_dir / "metrics.json")) if (run_dir / "metrics.json").exists() else {}
    tm = json.load(open(run_dir / "train_metrics.json")) if (run_dir / "train_metrics.json").exists() else {}
    fmt = lambda x: "" if x is None else f"{x:.2f}"
    row.update(status="done", finished=now(),
               best_step=(tm.get("best") or {}).get("step", tm.get("steps", "")),
               cirr_dev_r1=fmt(m.get("cirr_recall_at1")), cirr_dev_r5=fmt(m.get("cirr_recall_at5")),
               cirr_dev_r10=fmt(m.get("cirr_recall_at10")), cirr_dev_r50=fmt(m.get("cirr_recall_at50")),
               fiq_avg_r10=fmt(m.get("average_fiq_recall_at10")), fiq_avg_r50=fmt(m.get("average_fiq_recall_at50")),
               circo_map5=fmt(m.get("circo_map_at5")), circo_map10=fmt(m.get("circo_map_at10")),
               train_hours=tm.get("train_hours", ""), gpu=m.get("device", tm.get("device", "")))
    registry_upsert(row)
    print(f"\n[done] {run_id} -> {run_dir}")


if __name__ == "__main__":
    main()
