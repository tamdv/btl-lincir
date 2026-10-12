"""[NHOM8] Word IDF over the training captions, for improvement C (--idf_path in train_phi.py).

idf(w) = log(N / (1 + df(w))), words lower-cased, letters only. Use the same corpus options as training.

Usage:
  python scripts/compute_idf.py --out experiments/idf_cc3m_sdp_mj.json            # original 3 corpora
  python scripts/compute_idf.py --train_captions_file captions.txt --out idf.json
"""
import argparse
import json
import math
import random
import re
from collections import Counter

WORD = re.compile(r"[a-z]+")

ap = argparse.ArgumentParser()
ap.add_argument("--caption_datasets", nargs="+", default=["dataset1", "dataset2", "dataset3"])
ap.add_argument("--train_captions_file")
ap.add_argument("--max_captions", type=int)
ap.add_argument("--min_df", type=int, default=2)
ap.add_argument("--out", required=True)
args = ap.parse_args()

if args.train_captions_file:
    captions = [l.strip() for l in open(args.train_captions_file) if l.strip()]
else:
    import datasets
    names = {"dataset1": "dangne/gcc_caption_only", "dataset2": "FredZhang7/stable-diffusion-prompts-2.47M",
             "dataset3": "Geonmo/midjourney-prompts-only"}
    captions = []
    for k in args.caption_datasets:
        captions += datasets.load_dataset(names[k], cache_dir=f"./datasets/{k}")["train"]["text"]
if args.max_captions and len(captions) > args.max_captions:
    captions = random.Random(0).sample(captions, args.max_captions)

df = Counter()
for c in captions:
    df.update(set(WORD.findall((c or "").lower())))
n = len(captions)
idf = {w: round(math.log(n / (1 + d)), 4) for w, d in df.items() if d >= args.min_df}
with open(args.out, "w") as f:
    json.dump(idf, f)
print(f"{len(captions)} captions, {len(idf)} words -> {args.out}")
