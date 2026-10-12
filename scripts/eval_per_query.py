"""[NHOM8] Evaluate a phi checkpoint on CIRR val and/or FashionIQ val, keeping the result of every query.

Same protocol and numbers as code/validate.py (reference image removed for CIRR, "a photo of $ that ..." prompt,
both caption orders averaged for FashionIQ), but it also writes per-query ranks for significance testing.

Outputs in --out_dir:
  metrics.json                       aggregate R@K (same keys as validate.py) + run info
  per_query_cirr.csv                 query_id,target_rank,group_rank,target_sim,top1_sim,reference,target
  per_query_fiq_<dress>.csv          query_id,target_rank,target_sim,top1_sim,reference,target
  per_query_circo.csv                query_id,target_rank,n_gt,ap5,ap10,ap25,ap50,reference,target
  topk_<cirr|fiq_<dress>|circo>.json  {query_id: [top-k gallery names]} with --save_topk k (qualitative figures)
Ranks are 1-based. Gallery image features are cached in --feature_cache to skip re-encoding.

Usage (from the project root):
  python scripts/eval_per_query.py --phi experiments/runs/<run>/checkpoints/phi_best.pt \
      --clip_model_name large --cirr data/CIRR --fiq data/FashionIQ --out_dir experiments/runs/<run>
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from loader import CIRCODataset, CIRRDataset, FashionIQDataset  # noqa: E402
from models import Phi, build_text_encoder  # noqa: E402
from utils import device, extract_image_features, extract_pseudo_tokens_with_phi  # noqa: E402
from validate import circo_generate_val_predictions, cirr_generate_val_predictions, fiq_generate_val_predictions  # noqa: E402

KS = (1, 5, 10, 50)


OFFICIAL = {"official-large": "lincir_large.pt"}  # released checkpoints on navervision/zeroshot-cir-models


def load_phi(path, text_encoder):
    if path in OFFICIAL:
        from huggingface_hub import hf_hub_download
        path = hf_hub_download("navervision/zeroshot-cir-models", OFFICIAL[path], cache_dir="./hf_models")
    phi = Phi(input_dim=text_encoder.config.projection_dim, hidden_dim=text_encoder.config.projection_dim * 4,
              output_dim=text_encoder.config.hidden_size, dropout=0.5)
    state = torch.load(path, map_location="cpu")
    phi.load_state_dict(state[phi.__class__.__name__] if phi.__class__.__name__ in state else state)
    return phi.to(device).eval()


def gallery_features(dataset, image_encoder, cache_file):
    if cache_file and Path(cache_file).exists():
        data = torch.load(cache_file)
        return data["features"], data["names"]
    feats, names = extract_image_features(dataset, image_encoder)
    if cache_file:
        Path(cache_file).parent.mkdir(parents=True, exist_ok=True)
        torch.save({"features": feats, "names": names}, cache_file)
    return feats, names


def ranks_from_scores(scores, gallery_names, target_names, exclude_names=None):
    """1-based rank of each target; `exclude_names` (CIRR reference) are removed from the ranking."""
    order = torch.argsort(scores, dim=-1, descending=True).cpu().numpy()
    names = np.array(gallery_names)[order]
    if exclude_names is not None:
        keep = names != np.array(exclude_names)[:, None]
        names = names[keep].reshape(names.shape[0], -1)
    hits = names == np.array(target_names)[:, None]
    assert (hits.sum(1) == 1).all(), "every target must appear exactly once in the gallery"
    return hits.argmax(1) + 1, names


def recall(ranks, k):
    return float((np.asarray(ranks) <= k).mean() * 100)


def write_topk(path, query_ids, ranked_names, k):
    if k:
        with open(path, "w") as f:
            json.dump({str(q): list(map(str, r[:k])) for q, r in zip(query_ids, ranked_names)}, f)


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


@torch.no_grad()
def eval_cirr(root, image_encoder, text_encoder, phi, preprocess, args, out_dir, cache_dir):
    rel_unique = CIRRDataset(root, "val", "relative", preprocess, no_duplicates=True)
    pseudo_tokens, ref_names = extract_pseudo_tokens_with_phi(image_encoder, phi, rel_unique, args)
    classic = CIRRDataset(root, "val", "classic", preprocess)
    gal_feats, gal_names = gallery_features(classic, image_encoder,
                                            cache_dir and f"{cache_dir}/cirr_val_{args.clip_model_name}.pt")
    relative = CIRRDataset(root, "val", "relative", preprocess)
    pred, refs, targets, groups = cirr_generate_val_predictions(text_encoder, relative, ref_names, pseudo_tokens.to(device))
    gal = F.normalize(gal_feats.to(device).float(), dim=-1)
    scores = pred.float() @ gal.T
    ranks, sorted_names = ranks_from_scores(scores, gal_names, targets, exclude_names=refs)
    write_topk(out_dir / "topk_cirr.json", range(len(targets)), sorted_names, args.save_topk)
    group_ranks = []
    for i, members in enumerate(groups):
        in_group = [n for n in sorted_names[i] if n in set(members)]
        group_ranks.append(in_group.index(targets[i]) + 1)
    name_to_idx = {n: j for j, n in enumerate(gal_names)}
    target_sim = scores[torch.arange(len(targets)), torch.tensor([name_to_idx[t] for t in targets])].cpu().numpy()
    ref_idx = torch.tensor([name_to_idx[r] for r in refs])
    scores_wo_ref = scores.clone()
    scores_wo_ref[torch.arange(len(refs)), ref_idx] = -1e4
    top1_sim = scores_wo_ref.max(1).values.cpu().numpy()
    write_csv(out_dir / "per_query_cirr.csv", ["query_id", "target_rank", "group_rank", "target_sim", "top1_sim", "reference", "target"],
              [[i, int(r), int(g), f"{ts:.5f}", f"{t1:.5f}", refs[i], targets[i]]
               for i, (r, g, ts, t1) in enumerate(zip(ranks, group_ranks, target_sim, top1_sim))])
    m = {f"cirr_recall_at{k}": recall(ranks, k) for k in KS}
    m.update({f"cirr_group_recall_at{k}": recall(group_ranks, k) for k in (1, 2, 3)})
    m["cirr_n_queries"] = len(ranks)
    return m


@torch.no_grad()
def eval_fiq(root, image_encoder, text_encoder, phi, preprocess, args, out_dir, cache_dir):
    rel_unique = FashionIQDataset(root, "val", ["dress", "toptee", "shirt"], "relative", preprocess, no_duplicates=True)
    pseudo_tokens, ref_names = extract_pseudo_tokens_with_phi(image_encoder, phi, rel_unique, args)
    pseudo_tokens = pseudo_tokens.to(device)
    m, r10, r50 = {}, [], []
    for dress in ["shirt", "dress", "toptee"]:
        classic = FashionIQDataset(root, "val", [dress], "classic", preprocess)
        gal_feats, gal_names = gallery_features(classic, image_encoder,
                                                cache_dir and f"{cache_dir}/fiq_val_{dress}_{args.clip_model_name}.pt")
        relative = FashionIQDataset(root, "val", [dress], "relative", preprocess)
        pred, targets = fiq_generate_val_predictions(text_encoder, relative, ref_names, pseudo_tokens)
        refs = [t["candidate"] for t in relative.triplets]
        scores = pred.float() @ F.normalize(gal_feats.to(device).float(), dim=-1).T
        ranks, sorted_names = ranks_from_scores(scores, gal_names, targets)
        write_topk(out_dir / f"topk_fiq_{dress}.json", [f"{dress}_{i}" for i in range(len(targets))], sorted_names, args.save_topk)
        name_to_idx = {n: j for j, n in enumerate(gal_names)}
        target_sim = scores[torch.arange(len(targets)), torch.tensor([name_to_idx[t] for t in targets])].cpu().numpy()
        top1_sim = scores.max(1).values.cpu().numpy()
        write_csv(out_dir / f"per_query_fiq_{dress}.csv", ["query_id", "target_rank", "target_sim", "top1_sim", "reference", "target"],
                  [[f"{dress}_{i}", int(r), f"{ts:.5f}", f"{t1:.5f}", refs[i], targets[i]]
                   for i, (r, ts, t1) in enumerate(zip(ranks, target_sim, top1_sim))])
        m[f"{dress}_fiq_recall_at10"], m[f"{dress}_fiq_recall_at50"] = recall(ranks, 10), recall(ranks, 50)
        r10.append(m[f"{dress}_fiq_recall_at10"])
        r50.append(m[f"{dress}_fiq_recall_at50"])
    m["average_fiq_recall_at10"], m["average_fiq_recall_at50"] = float(np.mean(r10)), float(np.mean(r50))
    return m


@torch.no_grad()
def eval_circo(root, image_encoder, text_encoder, phi, preprocess, args, out_dir, cache_dir):
    """CIRCO val, same metric as validate.circo_compute_val_metrics (reference image kept in the gallery)."""
    relative = CIRCODataset(root, "val", "relative", preprocess)
    pseudo_tokens, ref_names = extract_pseudo_tokens_with_phi(image_encoder, phi, relative, args)
    cache = cache_dir and f"{cache_dir}/circo_val_{args.clip_model_name}.pt"
    gal_feats, gal_names = gallery_features(CIRCODataset(root, "val", "classic", preprocess), image_encoder, cache)
    pred, targets, gts = circo_generate_val_predictions(text_encoder, relative, ref_names, pseudo_tokens.to(device))
    gal = F.normalize(gal_feats.to(device).float(), dim=-1)
    names = np.array(gal_names)
    rows, aps, topk = [], {k: [] for k in (5, 10, 25, 50)}, {}
    for i, (feat, target, gt) in enumerate(zip(pred, targets, gts)):
        gt = [g for g in gt if g != ""]
        order = torch.argsort(feat.float() @ gal.T, descending=True).cpu().numpy()
        ranked = names[order]
        if args.save_topk:
            topk[str(relative.annotations[i]["id"])] = [str(x) for x in ranked[:args.save_topk]]
        hits = np.isin(ranked[:50], gt).astype(float)  # top-50 (shorter only for toy galleries)
        prec = np.cumsum(hits) * hits / np.arange(1, len(hits) + 1)
        ap = {k: float(prec[:k].sum() / min(len(gt), k)) for k in aps}
        for k in aps:
            aps[k].append(ap[k])
        target_rank = int(np.where(ranked == target)[0][0]) + 1
        rows.append([relative.annotations[i]["id"], target_rank, len(gt), *(f"{ap[k]:.5f}" for k in aps),
                     relative.annotations[i]["reference_img_id"], target])
    if args.save_topk:
        with open(out_dir / "topk_circo.json", "w") as f:
            json.dump(topk, f)
    write_csv(out_dir / "per_query_circo.csv",
              ["query_id", "target_rank", "n_gt", "ap5", "ap10", "ap25", "ap50", "reference", "target"], rows)
    m = {f"circo_map_at{k}": float(np.mean(v) * 100) for k, v in aps.items()}
    ranks = [r[1] for r in rows]
    m.update({f"circo_recall_at{k}": recall(ranks, k) for k in (5, 10, 25, 50)})
    m["circo_n_queries"] = len(rows)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phi", required=True, help="phi checkpoint (.pt), or 'official-large' for the released ViT-L model")
    ap.add_argument("--clip_model_name", default="large", choices=["base", "large", "huge", "giga"])
    ap.add_argument("--cirr", help="CIRR root (with captions/, cirr/ and dev/ images)")
    ap.add_argument("--fiq", help="FashionIQ root")
    ap.add_argument("--circo", help="CIRCO root (annotations/, COCO2017_unlabeled/); gallery from --feature_cache if present")
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--feature_cache", default="experiments/feature_cache")
    ap.add_argument("--cache_dir", default="./hf_models", help="HuggingFace model cache")
    ap.add_argument("--save_topk", type=int, default=10, help="also write top-k retrieved names per query (0 = off)")
    args = ap.parse_args()
    if not (args.cirr or args.fiq or args.circo):
        ap.error("give at least one of --cirr, --fiq, --circo")
    args.mixed_precision = "fp16" if device.type == "cuda" else "no"
    args.l2_normalize = False

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    image_encoder, preprocess, text_encoder, _ = build_text_encoder(args)
    image_encoder, text_encoder = image_encoder.float().to(device).eval(), text_encoder.float().to(device).eval()
    phi = load_phi(args.phi, text_encoder)

    metrics = {"phi": args.phi, "clip_model_name": args.clip_model_name, "device": str(device)}
    if args.cirr:
        metrics.update(eval_cirr(args.cirr, image_encoder, text_encoder, phi, preprocess, args, out_dir, args.feature_cache))
    if args.circo:
        metrics.update(eval_circo(args.circo, image_encoder, text_encoder, phi, preprocess, args, out_dir, args.feature_cache))
    if args.fiq:
        metrics.update(eval_fiq(args.fiq, image_encoder, text_encoder, phi, preprocess, args, out_dir, args.feature_cache))
    metrics["eval_minutes"] = round((time.time() - t0) / 60, 2)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
