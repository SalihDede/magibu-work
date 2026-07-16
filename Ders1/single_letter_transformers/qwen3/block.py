"""A single transformer block (decoder layer), Qwen3 pre-norm style.

The pattern is "normalize, transform, add back the residual" twice:

    x = x + attention(norm(x))
    x = x + mlp(norm(x))

Normalizing before each sub-layer (pre-norm) keeps the residual path clean,
which makes deep stacks train stably.
"""

import torch
from torch import nn

from Ders1.single_letter_transformers.qwen3.config import ModelConfig
from Ders1.single_letter_transformers.qwen3.rms_norm import RMSNorm
from Ders1.single_letter_transformers.qwen3.attention import Attention
from Ders1.single_letter_transformers.qwen3.mlp import MLP


class TransformerBlock(nn.Module):
    def __init__(self, cfg: ModelConfig):
        super().__init__()
        self.input_layernorm = RMSNorm(cfg.hidden_size, cfg.rms_norm_eps)
        self.attn = Attention(cfg)
        self.post_attention_layernorm = RMSNorm(cfg.hidden_size, cfg.rms_norm_eps)
        self.mlp = MLP(cfg)

    def forward(self, x: torch.Tensor, cos: torch.Tensor, sin: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.input_layernorm(x), cos, sin)
        x = x + self.mlp(self.post_attention_layernorm(x))
        return x
