'''
LinCIR
Copyright (c) 2023-present NAVER Corp.
CC BY-NC-4.0 (https://creativecommons.org/licenses/by-nc/4.0/)
'''
import torch
import torch.nn.functional as F
from transformers import CLIPTextModelWithProjection


# [NHOM8] The original version called `text_model.encoder(..., causal_attention_mask=...)`, an internal
# transformers API (v4.34) whose signature changed in later releases. The forward pass below rebuilds the
# CLIP text transformer from its sub-modules (layer norms, q/k/v/out projections, MLP), which keep the same
# names across versions, and uses a causal scaled-dot-product attention. Output is numerically identical to
# `CLIPTextModelWithProjection(input_ids).text_embeds` when no pseudo token is present (checked by
# scripts/check_encoder_equivalence.py).
def _clip_text_encoder_forward(text_model, x: torch.Tensor) -> torch.Tensor:
    for layer in text_model.encoder.layers:
        attn = layer.self_attn
        residual = x
        h = layer.layer_norm1(x)
        bsz, seq_len, dim = h.shape
        num_heads = attn.num_heads
        head_dim = dim // num_heads
        q = attn.q_proj(h).view(bsz, seq_len, num_heads, head_dim).transpose(1, 2)
        k = attn.k_proj(h).view(bsz, seq_len, num_heads, head_dim).transpose(1, 2)
        v = attn.v_proj(h).view(bsz, seq_len, num_heads, head_dim).transpose(1, 2)
        h = F.scaled_dot_product_attention(q, k, v, is_causal=True, scale=head_dim ** -0.5)
        h = attn.out_proj(h.transpose(1, 2).reshape(bsz, seq_len, dim))
        x = residual + h
        x = x + layer.mlp(layer.layer_norm2(x))
    return x


def encode_with_pseudo_tokens_HF(clip_model: CLIPTextModelWithProjection, text: torch.Tensor, pseudo_tokens: torch.Tensor,
                              num_tokens=1, return_last_states=False) -> torch.Tensor:
    x = clip_model.text_model.embeddings.token_embedding(text).type(clip_model.dtype)  # [batch_size, n_ctx, d_model]
    x = torch.where(text.unsqueeze(-1) == 259,
                    pseudo_tokens.unsqueeze(1).type(clip_model.dtype),
                    x)
    position_ids = clip_model.text_model.embeddings.position_ids[:, :x.shape[1]]  # [NHOM8] allow shorter inputs
    x = x + clip_model.text_model.embeddings.position_embedding(position_ids)
    x = _clip_text_encoder_forward(clip_model.text_model, x)
    x_last = clip_model.text_model.final_layer_norm(x)
    x = x_last[torch.arange(x_last.shape[0], device=x_last.device),
          text.to(dtype=torch.int, device=x_last.device).argmax(dim=-1),
          ]
    if hasattr(clip_model, 'text_projection'):
        x = clip_model.text_projection(x)

    if return_last_states:
        return x, x_last
    else:
        return x
