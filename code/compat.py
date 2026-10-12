'''
[NHOM8] Compatibility helpers for recent Python / transformers versions.

The original code imports OpenAI's `clip` package only for `clip.tokenize` (and `clip.load` on the
OTI/SEARLE evaluation paths, which this project does not use). That package is hard to install on
Python >= 3.13, so `tokenize` falls back to the HuggingFace CLIP tokenizer, which uses the same BPE
vocabulary (the "$" placeholder is token id 259 in both).

Usage in place of `import clip`:  `import compat as clip`
'''
from functools import lru_cache
from typing import List, Union

import torch

try:  # prefer the original implementation when it is installed
    import clip as _openai_clip
except ImportError:  # pragma: no cover - depends on the environment
    _openai_clip = None

PSEUDO_TOKEN_ID = 259  # BPE id of "$", replaced by the projected token embedding


@lru_cache(maxsize=1)
def _hf_tokenizer():
    from transformers import CLIPTokenizer
    return CLIPTokenizer.from_pretrained('openai/clip-vit-large-patch14')


def tokenize(texts: Union[str, List[str]], context_length: int = 77, truncate: bool = True) -> torch.Tensor:
    """Same output layout as `clip.tokenize`: [SOT] tokens [EOT] then zero padding."""
    if _openai_clip is not None:
        return _openai_clip.tokenize(texts, context_length=context_length, truncate=truncate)
    if isinstance(texts, str):
        texts = [texts]
    tok = _hf_tokenizer()
    ids = tok(texts, padding=False, truncation=True, max_length=context_length)['input_ids']
    out = torch.zeros(len(ids), context_length, dtype=torch.long)
    for i, seq in enumerate(ids):
        out[i, :len(seq)] = torch.tensor(seq)
    return out


def load(*args, **kwargs):
    if _openai_clip is None:
        raise ImportError("OpenAI `clip` package is required for this evaluation path "
                          "(pip install git+https://github.com/openai/CLIP.git)")
    return _openai_clip.load(*args, **kwargs)


def best_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device('cuda')
    if torch.backends.mps.is_available():
        return torch.device('mps')
    return torch.device('cpu')
