"""[NHOM8] Build tiny fake CIRR / FashionIQ folders (coloured shapes) with the real file layout.

Only for smoke tests of the pipeline on a laptop: numbers on this data mean nothing.
Also writes a captions file for training and an image-caption pairs file for modality_gap.py.

Usage: python scripts/make_toy_benchmarks.py --out experiments/toy
"""
import argparse
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw

COLORS = {"red": (220, 40, 40), "green": (40, 170, 70), "blue": (40, 80, 220), "yellow": (230, 200, 30),
          "purple": (140, 60, 180), "black": (20, 20, 20)}
SHAPES = ["circle", "square", "triangle"]


def draw(color, shape, bg, path):
    im = Image.new("RGB", (224, 224), bg)
    d = ImageDraw.Draw(im)
    box = (52, 52, 172, 172)
    if shape == "circle":
        d.ellipse(box, fill=COLORS[color])
    elif shape == "square":
        d.rectangle(box, fill=COLORS[color])
    else:
        d.polygon([(112, 40), (190, 180), (34, 180)], fill=COLORS[color])
    im.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="experiments/toy")
    ap.add_argument("--n_captions", type=int, default=400, help="training captions (>= batch size x a few)")
    args = ap.parse_args()
    rng = random.Random(0)
    out = Path(args.out)
    items = [(c, s) for c in COLORS for s in SHAPES]  # 18 distinct images

    # CIRR layout: <root>/dev/*.png, <root>/cirr/{captions,image_splits}/*.rc2.val.json
    cirr = out / "CIRR"
    (cirr / "dev").mkdir(parents=True, exist_ok=True)
    (cirr / "cirr" / "captions").mkdir(parents=True, exist_ok=True)
    (cirr / "cirr" / "image_splits").mkdir(parents=True, exist_ok=True)
    names = {}
    for i, (c, s) in enumerate(items):
        n = f"dev-{i}-{c}-{s}"
        draw(c, s, (245, 245, 245), cirr / "dev" / f"{n}.png")
        names[(c, s)] = n
    json.dump({n: f"./dev/{n}.png" for n in names.values()}, open(cirr / "cirr/image_splits/split.rc2.val.json", "w"))
    triplets = []
    for pid in range(30):
        (c1, s1), (c2, s2) = rng.sample(items, 2)
        ref, tgt = names[(c1, s1)], names[(c2, s2)]
        others = [n for n in names.values() if n not in (ref, tgt)]
        members = [ref, tgt] + rng.sample(others, 4)
        rng.shuffle(members)
        triplets.append({"pairid": pid, "reference": ref, "target_hard": tgt,
                         "caption": f"is a {c2} {s2} instead", "img_set": {"id": pid, "members": members}})
    json.dump(triplets, open(cirr / "cirr/captions/cap.rc2.val.json", "w"))

    # FashionIQ layout: <root>/images/*.jpg, captions/cap.<dress>.val.json, image_splits/split.<dress>.val.json
    fiq = out / "FashionIQ"
    for sub in ("images", "captions", "image_splits"):
        (fiq / sub).mkdir(parents=True, exist_ok=True)
    for dress, bg in (("dress", (250, 235, 235)), ("shirt", (235, 245, 250)), ("toptee", (240, 250, 235))):
        dn = {}
        for c, s in items:
            n = f"{dress}_{c}_{s}"
            draw(c, s, bg, fiq / "images" / f"{n}.jpg")
            dn[(c, s)] = n
        json.dump(list(dn.values()), open(fiq / f"image_splits/split.{dress}.val.json", "w"))
        trip = []
        for _ in range(20):
            (c1, s1), (c2, s2) = rng.sample(items, 2)
            trip.append({"candidate": dn[(c1, s1)], "target": dn[(c2, s2)],
                         "captions": [f"is {c2}", f"has a {s2} shape"]})
        json.dump(trip, open(fiq / f"captions/cap.{dress}.val.json", "w"))

    # CIRCO layout: <root>/annotations/val.json, COCO2017_unlabeled/{annotations/image_info_unlabeled2017.json, unlabeled2017/}
    circo = out / "CIRCO"
    (circo / "annotations").mkdir(parents=True, exist_ok=True)
    (circo / "COCO2017_unlabeled" / "annotations").mkdir(parents=True, exist_ok=True)
    (circo / "COCO2017_unlabeled" / "unlabeled2017").mkdir(parents=True, exist_ok=True)
    images, cid = [], {}
    for i, (c, s) in enumerate(items):
        fn = f"{i:012d}.jpg"
        draw(c, s, (230, 230, 230), circo / "COCO2017_unlabeled" / "unlabeled2017" / fn)
        images.append({"id": i, "file_name": fn})
        cid[(c, s)] = i
    json.dump({"images": images}, open(circo / "COCO2017_unlabeled/annotations/image_info_unlabeled2017.json", "w"))
    ann = []
    for q in range(12):
        (c1, s1), (c2, s2) = rng.sample(items, 2)
        gts = [cid[(c2, s2)]] + [cid[(c2, x)] for x in SHAPES if x != s2][:rng.randint(0, 2)]
        ann.append({"id": q, "reference_img_id": cid[(c1, s1)], "target_img_id": gts[0], "relative_caption": f"is {c2} instead",
                    "shared_concept": "a shape", "gt_img_ids": gts})
    json.dump(ann, open(circo / "annotations/val.json", "w"))

    # training captions + image-caption pairs
    caps = [f"a {rng.choice(['small', 'large', 'bright'])} {c} {s} on a {rng.choice(['white', 'grey'])} table"
            for _ in range(args.n_captions) for c, s in [rng.choice(items)]]
    (out / "captions.txt").write_text("\n".join(caps))
    with open(out / "pairs.jsonl", "w") as f:
        for c, s in items:
            f.write(json.dumps({"image": f"CIRR/dev/{names[(c, s)]}.png", "caption": f"a {c} {s}"}) + "\n")
    print(f"toy data in {out}")


if __name__ == "__main__":
    main()
