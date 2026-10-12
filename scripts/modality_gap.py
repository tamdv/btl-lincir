"""[NHOM8] Modality-gap measurements on image-caption pairs (for improvement B and the "why" analysis).

1) CLIP gap (Liang et al., 2022): distance between the centroids of L2-normalised image and text embeddings,
   plus the mean paired cosine. Also saves delta = mean(image_embeds) - mean(text_embeds) (unnormalised, the
   space phi takes as input) for --gap_vector_path in train_phi.py.
2) Projection consistency, per phi checkpoint: encode "a photo of $" with $ = phi(text_embed) and with
   $ = phi(image_embed) of the same pair. Higher cosine / smaller centroid gap means phi behaves on images
   the way it was trained on texts, which is what the noise is meant to achieve.

Pairs come from a JSON-lines file ({"image": path, "caption": text}) or a HuggingFace dataset.

Usage:
  python scripts/modality_gap.py --pairs_jsonl pairs.jsonl --clip_model_name large \
      --save_delta experiments/gap_delta_large.pt \
      --phi baseline=runs/EXP-001-baseline-s12345/checkpoints/phi_best.pt --phi A=runs/.../phi_best.pt \
      --out experiments/runs/analysis/modality_gap.json
"""
import argparse
import json
import sys
from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
import compat  # noqa: E402
from encode_with_pseudo_tokens import encode_with_pseudo_tokens_HF  # noqa: E402
from models import build_text_encoder  # noqa: E402
from utils import device  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from eval_per_query import load_phi  # noqa: E402


def load_pairs(args):
    if args.coco_captions:  # COCO annotations json + image folder, one caption per image
        ann = json.load(open(args.coco_captions))
        files = {im["id"]: im["file_name"] for im in ann["images"]}
        seen, pairs = set(), []
        for a in ann["annotations"]:
            if a["image_id"] in seen:
                continue
            seen.add(a["image_id"])
            pairs.append((Image.open(Path(args.coco_images) / files[a["image_id"]]), a["caption"]))
            if len(pairs) >= args.limit:
                break
        return pairs
    if args.pairs_jsonl:
        base = Path(args.pairs_jsonl).parent
        rows = [json.loads(l) for l in open(args.pairs_jsonl) if l.strip()]
        pairs = [(Image.open(base / r["image"] if not Path(r["image"]).is_absolute() else r["image"]), r["caption"]) for r in rows]
    else:
        import datasets
        ds = datasets.load_dataset(args.hf_dataset, split=args.split)
        pairs = []
        for r in ds.select(range(min(args.limit, len(ds)))):
            cap = r[args.text_col]
            pairs.append((r[args.image_col], cap[0] if isinstance(cap, list) else cap))
    return pairs[: args.limit]


@torch.no_grad()
def embed(pairs, image_encoder, text_encoder, preprocess, bs=32):
    img, txt = [], []
    for i in range(0, len(pairs), bs):
        chunk = pairs[i:i + bs]
        pix = preprocess([p[0].convert("RGB") for p in chunk], return_tensors="pt")["pixel_values"].to(device)
        img.append(image_encoder(pixel_values=pix).image_embeds.float().cpu())
        txt.append(text_encoder(input_ids=compat.tokenize([p[1] for p in chunk]).to(device)).text_embeds.float().cpu())
    return torch.cat(img), torch.cat(txt)


def centroid_gap(a, b):
    return float((F.normalize(a, dim=-1).mean(0) - F.normalize(b, dim=-1).mean(0)).norm())


@torch.no_grad()
def projection_consistency(phi, text_encoder, img, txt, bs=64):
    prompt = compat.tokenize(["a photo of $"]).to(device)
    out_t, out_i = [], []
    for i in range(0, len(img), bs):
        ti, ii = txt[i:i + bs].to(device), img[i:i + bs].to(device)
        p = prompt.expand(ti.shape[0], -1)
        out_t.append(encode_with_pseudo_tokens_HF(text_encoder, p, phi(ti)).float().cpu())
        out_i.append(encode_with_pseudo_tokens_HF(text_encoder, p, phi(ii)).float().cpu())
    et, ei = torch.cat(out_t), torch.cat(out_i)
    return {"paired_cosine": float(F.cosine_similarity(et, ei).mean()), "centroid_gap": centroid_gap(et, ei)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs_jsonl")
    ap.add_argument("--hf_dataset")
    ap.add_argument("--coco_captions", help="COCO captions_*.json (e.g. captions_val2017.json)")
    ap.add_argument("--coco_images", help="folder with the COCO images of that split")
    ap.add_argument("--split", default="test")
    ap.add_argument("--image_col", default="image")
    ap.add_argument("--text_col", default="caption")
    ap.add_argument("--limit", type=int, default=5000)
    ap.add_argument("--clip_model_name", default="large", choices=["base", "large", "huge", "giga"])
    ap.add_argument("--cache_dir", default="./hf_models")
    ap.add_argument("--phi", action="append", default=[], help="label=path/to/phi.pt (repeatable)")
    ap.add_argument("--save_delta", help="where to save delta for --gap_vector_path")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if not (args.pairs_jsonl or args.hf_dataset or args.coco_captions):
        ap.error("give --coco_captions/--coco_images, --pairs_jsonl or --hf_dataset")
    args.mixed_precision = "no"

    image_encoder, preprocess, text_encoder, _ = build_text_encoder(args)
    image_encoder, text_encoder = image_encoder.float().to(device).eval(), text_encoder.float().to(device).eval()
    pairs = load_pairs(args)
    img, txt = embed(pairs, image_encoder, text_encoder, preprocess)

    result = {"clip_model_name": args.clip_model_name, "n_pairs": len(pairs),
              "clip_gap": {"centroid_gap": centroid_gap(img, txt),
                           "paired_cosine": float(F.cosine_similarity(img, txt).mean())},
              "projection": {}}
    if args.save_delta:
        delta = img.mean(0) - txt.mean(0)
        Path(args.save_delta).parent.mkdir(parents=True, exist_ok=True)
        torch.save(delta, args.save_delta)
        result["delta_path"], result["delta_norm"] = args.save_delta, float(delta.norm())
    for spec in args.phi:
        label, path = spec.split("=", 1)
        result["projection"][label] = projection_consistency(load_phi(path, text_encoder), text_encoder, img, txt)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
