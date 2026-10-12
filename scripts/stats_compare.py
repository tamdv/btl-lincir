"""Paired comparison of two CIR systems from per-query rank files.

Each input CSV has columns `query_id,target_rank` (rank is 1-based).
Several files per side (one per seed) are averaged per query before testing.

Usage:
  python scripts/stats_compare.py --base runs/A-s*/per_query_cirr.csv \
      --new runs/B-s*/per_query_cirr.csv --k 1 5 10 50
"""
import argparse
import csv
import glob
import json
import random
import statistics


def load_side(patterns, value_cols=()):
    files = sorted({f for p in patterns for f in glob.glob(p)})
    if not files:
        raise SystemExit(f"No files match: {patterns}")
    per_seed = []
    for f in files:
        with open(f, newline="") as fh:
            rows = list(csv.DictReader(fh))
            if value_cols:  # dict of per-query metric values, e.g. CIRCO ap5
                per_seed.append({r["query_id"]: {c: float(r[c]) for c in value_cols} for r in rows})
            else:
                per_seed.append({r["query_id"]: int(r["target_rank"]) for r in rows})
    return files, per_seed


def _value(rank_or_row, k):
    if isinstance(k, str):            # named per-query column (e.g. "ap5")
        return rank_or_row[k]
    return (1.0 / rank_or_row) if k == 0 else float(rank_or_row <= k)


def per_query_scores(per_seed, qids, k):
    """Mean over seeds of a per-query metric: recall@k (k>0), reciprocal rank (k=0) or a named column."""
    out = []
    for q in qids:
        vals = [_value(s[q], k) for s in per_seed]
        out.append(sum(vals) / len(vals))
    return out


def seed_summary(per_seed, qids, k):
    vals = [100 * sum(_value(s[q], k) for q in qids) / len(qids) for s in per_seed]
    return statistics.mean(vals), (statistics.stdev(vals) if len(vals) > 1 else 0.0)


def paired_bootstrap(a, b, n_boot, rng):
    n = len(a)
    diffs = [y - x for x, y in zip(a, b)]
    obs = sum(diffs) / n
    worse = 0
    samples = []
    for _ in range(n_boot):
        s = sum(diffs[rng.randrange(n)] for _ in range(n)) / n
        samples.append(s)
        if s <= 0:
            worse += 1
    samples.sort()
    ci = (samples[int(0.025 * n_boot)], samples[int(0.975 * n_boot) - 1])
    return obs, ci, worse / n_boot


def wilcoxon(a, b):
    try:
        from scipy.stats import wilcoxon as w
    except ImportError:
        return None
    diffs = [y - x for x, y in zip(a, b)]
    if all(d == 0 for d in diffs):
        return 1.0
    return float(w(a, b, zero_method="wilcox", alternative="two-sided").pvalue)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", nargs="+", required=True)
    ap.add_argument("--new", nargs="+", required=True)
    ap.add_argument("--k", nargs="+", type=int, default=[1, 5, 10, 50])
    ap.add_argument("--value_cols", nargs="+", default=[], help="test these per-query columns instead (e.g. ap5 ap10 for CIRCO)")
    ap.add_argument("--n-boot", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--json", help="Optional path to write results as JSON")
    args = ap.parse_args()

    base_files, base = load_side(args.base, args.value_cols)
    new_files, new = load_side(args.new, args.value_cols)
    qids = sorted(set.intersection(*[set(s) for s in base + new]))
    if not qids:
        raise SystemExit("No common query_id across files")
    rng = random.Random(args.seed)

    rows = []
    for k in (args.value_cols or args.k + [0]):
        name = k if isinstance(k, str) else ("MRR" if k == 0 else f"R@{k}")
        a, b = per_query_scores(base, qids, k), per_query_scores(new, qids, k)
        bm, bs = seed_summary(base, qids, k)
        nm, ns = seed_summary(new, qids, k)
        delta, ci, p_boot = paired_bootstrap(a, b, args.n_boot, rng)
        rows.append({"metric": name, "base_mean": bm, "base_std": bs, "new_mean": nm, "new_std": ns,
                     "delta": 100 * delta, "ci95": [100 * ci[0], 100 * ci[1]],
                     "p_bootstrap_one_sided": p_boot, "p_wilcoxon": wilcoxon(a, b)})

    print(f"base: {len(base_files)} file(s), new: {len(new_files)} file(s), queries: {len(qids)}")
    print(f"{'metric':<7}{'base':>16}{'new':>16}{'Δ':>8}{'95% CI':>18}{'p_boot':>9}{'p_wilc':>9}")
    for r in rows:
        pw = "n/a" if r["p_wilcoxon"] is None else f"{r['p_wilcoxon']:.4f}"
        print(f"{r['metric']:<7}{r['base_mean']:>9.2f}±{r['base_std']:<5.2f}{r['new_mean']:>10.2f}±{r['new_std']:<5.2f}"
              f"{r['delta']:>+8.2f}  [{r['ci95'][0]:+.2f}, {r['ci95'][1]:+.2f}]{r['p_bootstrap_one_sided']:>9.4f}{pw:>9}")
    if args.json:
        with open(args.json, "w") as fh:
            json.dump({"base_files": base_files, "new_files": new_files, "n_queries": len(qids), "results": rows}, fh, indent=2)


if __name__ == "__main__":
    main()
