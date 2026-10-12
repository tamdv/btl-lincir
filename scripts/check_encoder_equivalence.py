"""Check that the rewritten text encoder (code/encode_with_pseudo_tokens.py) matches HuggingFace CLIP.

1) Without pseudo tokens, encode_with_pseudo_tokens_HF must equal CLIPTextModelWithProjection(...).text_embeds.
2) The "$" placeholder must be token id 259 for both the eval tokenizer (compat.tokenize) and the training
   tokenizer ("[$]" added to the SDXL tokenizer_2, id 49408, remapped to 259 in loader.py).

Usage: python scripts/check_encoder_equivalence.py [--model openai/clip-vit-base-patch32]
"""
import argparse
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
from transformers import CLIPTextModelWithProjection, CLIPTokenizer  # noqa: E402

import compat  # noqa: E402
from encode_with_pseudo_tokens import encode_with_pseudo_tokens_HF  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--model", default="openai/clip-vit-base-patch32")
args = ap.parse_args()

model = CLIPTextModelWithProjection.from_pretrained(args.model).eval()
texts = ["a photo of a cat sleeping on a red pillow", "grow purple flowers behind the dog", "shirt"]
ids = compat.tokenize(texts)
with torch.no_grad():
    ref = model(input_ids=ids).text_embeds
    dummy = torch.zeros(len(texts), model.config.hidden_size)
    ours = encode_with_pseudo_tokens_HF(model, ids, dummy)
diff = (ref - ours).abs().max().item()
print(f"[1] max |HF - ours| = {diff:.2e}")
ok1 = diff < 1e-4

dollar_eval = compat.tokenize(["a photo of $ that is red"])[0].tolist()
ok2 = 259 in dollar_eval
print(f"[2] eval tokenizer puts '$' at id 259: {ok2}")

tok = CLIPTokenizer.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", subfolder="tokenizer_2")
tok.add_special_tokens({"additional_special_tokens": ["[$]"]})
train_ids = tok("[$] sleeps on [$]")["input_ids"]
ok3 = train_ids.count(49408) == 2
print(f"[3] training tokenizer maps '[$]' to 49408 (remapped to 259): {ok3}  ids={train_ids}")

with torch.no_grad():  # pseudo token actually changes the output only where "$" sits
    ps = torch.randn(1, model.config.hidden_size)
    out_a = encode_with_pseudo_tokens_HF(model, compat.tokenize(["a photo of $ that is red"]), ps)
    out_b = encode_with_pseudo_tokens_HF(model, compat.tokenize(["a photo of $ that is red"]), ps * 2)
ok4 = (out_a - out_b).abs().max().item() > 1e-3
print(f"[4] pseudo token embedding affects the output: {ok4}")

sys.exit(0 if (ok1 and ok2 and ok3 and ok4) else 1)
