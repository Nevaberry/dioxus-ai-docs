# Attention Ops (2.10–2.11)

## varlen_attn() for Variable-Length Sequences (2.10)

New attention op for ragged/packed sequences without padding.

```python
from torch.nn.attention.varlen import varlen_attn

# q, k, v are packed (total_tokens, num_heads, head_dim)
# cu_seqlens marks sequence boundaries: [0, seq1_len, seq1_len+seq2_len, ...]
output = varlen_attn(q, k, v, cu_seqlens_q, cu_seqlens_k, max_seqlen_q, max_seqlen_k)
# Supports forward + backward, torch.compile-able. Requires A100+, BF16/FP16.
```

## FlexAttention + FlashAttention-4 Backend (2.11)

FlexAttention on Hopper/Blackwell GPUs uses FA4 kernels: 1.2x–3.2x speedup over Triton backend on compute-bound workloads. Automatic via `flex_attention()`.
