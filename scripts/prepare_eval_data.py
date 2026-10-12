"""[NHOM8] Download and lay out the evaluation data that needs no registration.

  fiq    FashionIQ val: annotations from the official GitHub repo, images from the HuggingFace mirror
         `royokong/fashioniq_val_imgs` (the official image URLs are mostly dead). ~210 MB.
         -> <out>/FashionIQ/{captions,image_splits,images}
  circo  CIRCO val: annotations from github.com/miccunifi/CIRCO, images from COCO unlabeled2017 (20 GB zip,
         read in place, never extracted). Encodes the full 123k-image gallery once into the feature cache used by
         scripts/eval_per_query.py, then keeps a "lite" copy with only the query images (reference + target).
         -> <out>/CIRCO/{annotations,COCO2017_unlabeled/annotations,COCO2017_unlabeled/unlabeled2017}
            <feature_cache>/circo_val_<clip>.pt
  coco   COCO val2017 images + captions (for the modality-gap direction of improvement B). ~1 GB.
         -> <out>/COCO/{val2017,annotations/captions_val2017.json}

Usage (Kaggle):
  python scripts/prepare_eval_data.py --what fiq circo coco --out /kaggle/working/eval_data \
      --download_dir /tmp/dl --feature_cache experiments/feature_cache --clip_model_name large
"""
import argparse
import io
import json
import shutil
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

import torch
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

FIQ_GH = "https://raw.githubusercontent.com/XiaoxiaoGuo/fashion-iq/master"
CIRCO_GH = "https://raw.githubusercontent.com/miccunifi/CIRCO/main/annotations"
COCO = "http://images.cocodataset.org"
DRESSES = ["dress", "shirt", "toptee"]


def fetch(url, dest):
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    t = time.time()
    print(f"download {url}", flush=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, length=16 << 20)
    tmp.rename(dest)
    print(f"  -> {dest} ({dest.stat().st_size / 2**20:.0f} MB, {time.time() - t:.0f}s)", flush=True)
    return dest


def prep_fiq(out):
    root = out / "FashionIQ"
    names = set()
    for d in DRESSES:
        fetch(f"{FIQ_GH}/captions/cap.{d}.val.json", root / "captions" / f"cap.{d}.val.json")
        split = fetch(f"{FIQ_GH}/image_splits/split.{d}.val.json", root / "image_splits" / f"split.{d}.val.json")
        names |= set(json.load(open(split)))
        for t in json.load(open(root / "captions" / f"cap.{d}.val.json")):
            names |= {t["candidate"], t["target"]}
    img_dir = root / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    have = {p.stem for p in img_dir.glob("*.jpg")}
    if not names <= have:
        import datasets
        ds = datasets.load_dataset("royokong/fashioniq_val_imgs", split="val")
        for r in ds:
            if r["id"] in names and r["id"] not in have:
                r["img"].convert("RGB").save(img_dir / f"{r['id']}.jpg", quality=95)
                have.add(r["id"])
    missing = sorted(names - have)
    print(f"FashionIQ: {len(have & names)}/{len(names)} images ({len(missing)} missing)")
    if missing:
        (root / "missing_images.txt").write_text("\n".join(missing))
        raise SystemExit(f"FashionIQ incomplete, see {root / 'missing_images.txt'}")


class _ZipImages(torch.utils.data.Dataset):
    """Reads COCO images straight from the zip; each worker opens its own handle."""

    def __init__(self, zip_path, members, ids, preprocess):
        self.zip_path, self.members, self.ids, self.preprocess, self.zf = zip_path, members, ids, preprocess, None

    def __len__(self):
        return len(self.members)

    def __getitem__(self, i):
        if self.zf is None:
            self.zf = zipfile.ZipFile(self.zip_path)
        img = Image.open(io.BytesIO(self.zf.read(self.members[i]))).convert("RGB")
        return self.preprocess(img, return_tensors="pt")["pixel_values"][0], self.ids[i]


def prep_circo(out, dl, cache_dir, clip_model_name, batch_size, workers):
    root = out / "CIRCO"
    for split in ("val", "test"):
        fetch(f"{CIRCO_GH}/{split}.json", root / "annotations" / f"{split}.json")
    info_zip = fetch(f"{COCO}/annotations/image_info_unlabeled2017.zip", dl / "image_info_unlabeled2017.zip")
    ann_dir = root / "COCO2017_unlabeled" / "annotations"
    ann_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(info_zip) as z:
        (ann_dir / "image_info_unlabeled2017.json").write_bytes(z.read("annotations/image_info_unlabeled2017.json"))
    info = json.load(open(ann_dir / "image_info_unlabeled2017.json"))["images"]
    ids = [str(im["id"]) for im in info]                       # same order and names as CIRCODataset classic mode
    files = [im["file_name"] for im in info]

    img_zip = fetch(f"{COCO}/zips/unlabeled2017.zip", dl / "unlabeled2017.zip")
    with zipfile.ZipFile(img_zip) as z:
        available = set(z.namelist())
    members = [f"unlabeled2017/{f}" for f in files]
    assert all(m in available for m in members), "unlabeled2017.zip does not match image_info_unlabeled2017.json"

    # lite copy: only the images CIRCO val/test queries open (reference + target)
    lite = root / "COCO2017_unlabeled" / "unlabeled2017"
    lite.mkdir(parents=True, exist_ok=True)
    needed = set()
    for split in ("val", "test"):
        for a in json.load(open(root / "annotations" / f"{split}.json")):
            needed.add(str(a["reference_img_id"]))
            if "target_img_id" in a:
                needed.add(str(a["target_img_id"]))
    id_to_file = dict(zip(ids, files))
    with zipfile.ZipFile(img_zip) as z:
        for i in needed:
            p = lite / id_to_file[i]
            if not p.exists():
                p.write_bytes(z.read(f"unlabeled2017/{id_to_file[i]}"))
    print(f"CIRCO lite: {len(needed)} query images in {lite}")

    cache = Path(cache_dir) / f"circo_val_{clip_model_name}.pt"
    if cache.exists():
        print(f"gallery cache exists: {cache}")
        return
    from models import build_text_encoder
    from utils import device

    class A:
        pass
    args = A()
    args.clip_model_name, args.mixed_precision, args.cache_dir = clip_model_name, "no", "./hf_models"
    image_encoder, preprocess, _, _ = build_text_encoder(args)
    image_encoder = image_encoder.float().to(device).eval()
    loader = torch.utils.data.DataLoader(_ZipImages(img_zip, members, ids, preprocess), batch_size=batch_size,
                                         num_workers=workers, shuffle=False)
    feats, names, t = [], [], time.time()
    with torch.no_grad():
        for b, (pix, bid) in enumerate(loader):
            # fp32 like scripts/eval_per_query.py gallery features, so cached and fresh features agree
            feats.append(image_encoder(pixel_values=pix.to(device)).image_embeds.float().cpu())
            names.extend(bid)
            if b % 100 == 0:
                print(f"  gallery {len(names)}/{len(ids)} ({time.time() - t:.0f}s)", flush=True)
    cache.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"features": torch.cat(feats), "names": names}, cache)
    print(f"gallery cache -> {cache} ({len(names)} images, {(time.time() - t) / 60:.1f} min)")


def prep_coco(out, dl):
    root = out / "COCO"
    ann = fetch(f"{COCO}/annotations/annotations_trainval2017.zip", dl / "annotations_trainval2017.zip")
    (root / "annotations").mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ann) as z:
        (root / "annotations" / "captions_val2017.json").write_bytes(z.read("annotations/captions_val2017.json"))
    if not (root / "val2017").exists():
        with zipfile.ZipFile(fetch(f"{COCO}/zips/val2017.zip", dl / "val2017.zip")) as z:
            z.extractall(root)
    print(f"COCO val2017: {len(list((root / 'val2017').glob('*.jpg')))} images")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--what", nargs="+", choices=["fiq", "circo", "coco"], required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--download_dir", default="/tmp/dl")
    ap.add_argument("--feature_cache", default="experiments/feature_cache")
    ap.add_argument("--clip_model_name", default="large")
    ap.add_argument("--batch_size", type=int, default=128)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    out, dl = Path(a.out), Path(a.download_dir)
    if "fiq" in a.what:
        prep_fiq(out)
    if "coco" in a.what:
        prep_coco(out, dl)
    if "circo" in a.what:
        prep_circo(out, dl, a.feature_cache, a.clip_model_name, a.batch_size, a.workers)


if __name__ == "__main__":
    main()
