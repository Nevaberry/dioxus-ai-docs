# Generation, caches, and serving

Use this reference for `generate`, custom generation, speculative decoding,
cache implementations, continuous batching, the chat CLI, and local serving.

## Generation entry points

### Assisted generation (4.50.0)

The assistant can be any compatible model rather than the same model family,
and assisted generation works with sampling.

```python
from transformers import pipeline

pipe = pipeline(
    "text-generation",
    model="google/gemma-2-9b",
    assistant_model="double7/vicuna-68m",
    do_sample=True,
)
result = pipe("Alice and Bob", max_new_tokens=50, do_sample=True)
```

### Custom generation

`model.generate()` can load a generation implementation from a Hub repository
through `custom_generate` (4.52.1). This executes repository code, so opt in
with `trust_remote_code=True`. Relative imports inside custom implementations
work as of 4.57.0.

```python
output = model.generate(
    **inputs,
    custom_generate="transformers-community/custom_generate_example",
    trust_remote_code=True,
)
```

A `custom_generate` implementation loaded from a local directory also requires
`trust_remote_code=True` as of 5.15.1. Treat both local and remote custom code
as an explicit trust boundary.

### Removed strategies

- DoLa and Contrastive Search leave the built-in library in 4.56.0; use the
  remote implementations `transformers-community/dola` and
  `transformers-community/contrastive-search` with explicit trust.
- Group Beam Search and Constrained Beam Search are removed in 4.57.0. Remove
  these options from generation configs and callers.

### Inputs and penalties

Generation accepts `inputs_embeds` consistently. Gemma 4 generation supports
both `inputs_embeds` and `per_layer_inputs` as of 5.9.0, with
`per_layer_inputs` exposed on every variant. Calls using a repetition penalty
must supply `input_ids` in 5.9.0.

## Cache architecture and migration

### Per-layer cache objects (4.54.0)

KV caches are represented per layer, allowing hybrid caches that mix attention
types. `CacheProcessor` separates cache quantization and offloading so each
behavior can be customized independently. Non-generative models no longer use
a KV cache.

### Explicit caches and argument names (4.56.0)

Model implementations initialize caches explicitly and return `Cache` objects.
Deprecated cache objects are removed. Use `past_key_values` instead of the
singular `past_key_value`; `from_legacy_cache` is being prepared for
deprecation.

### Sliding-window caches

`DynamicSlidingWindowLayer` and its cache retain and pass only the required
past state for sliding-window and chunk-attention models (4.56.0). A
checkpoint's `cache_implementation="hybrid"` default is ignored in favor of
dynamic sliding-window caching, avoiding the slow first generation associated
with static hybrid caches.

Generation cache preparation enforces configured sliding-window limits as of
5.1.0. Code that relied on an effectively unbounded cache can produce different
output or require shorter inputs.

### Native state-space and hybrid caches (5.5.0)

Mamba-only and mixed Mamba-plus-attention architectures use first-class native
cache classes. Remove earlier custom cache classes and workarounds.

### Relative cropping (5.15.1)

`Cache.crop` no longer accepts an absolute target length. Remove a relative
number of tokens with a negative offset:

```python
cache.crop(-tokens_to_remove)
```

### Static and rollback behavior

Vision encoder-decoder models support static caches as of 4.55.0. Passing a
tensor `cache_position` to `generate()` no longer fails during argument
handling in that release.

CPU paged caches are supported as of 5.1.0.

Sliding-window cache layers can be rolled back during speculative decoding as
of 5.15.1. That release also supports stop strings that span byte-fragment
tokens.

## Result-affecting cache and attention corrections

- Flash Attention 2 can continue from an existing cache as of 4.56.0.
- Sliding-window size in Flash Attention is no longer off by one (4.56.0), so
  output can change when the initial context exceeds the window.
- Flash Attention causality handling supports bidirectional attention
  (4.56.0).
- T5Gemma2 long-input cross-attention selects the correct cache-layer type
  (5.7.0).
- Qwen3.5 Gated DeltaNet handles multi-token cached forwards correctly
  (5.7.0).
- Attention-only GraniteMoeHybrid configs no longer update a nonexistent Mamba
  mask and crash (5.7.0).
- Gemma 3 and Gemma 4 image-token attention in local layers respects
  sliding-window boundaries (5.15.1), potentially changing output.
- Multi-head Latent Attention cache compression and recurrent-layer padding
  masks during chunked prefill or continuation are corrected (5.15.1), also
  potentially changing cached output.

## Continuous batching

### Stable batch generation (4.57.0)

Use `generate_batch` for stable continuous batching with full- or
sliding-window attention. Paged SDPA is the documented setup. The feature
targets workloads such as GRPO training and evaluation and is integrated with
`transformers serve`.

```python
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen3-4B-Instruct-2507",
    dtype=torch.bfloat16,
    _attn_implementation="sdpa_paged",
    device_map="auto",
)
model.generation_config.max_new_tokens = 32
tokenizer = AutoTokenizer.from_pretrained(
    "Qwen/Qwen3-4B-Instruct-2507", padding_side="left"
)
inputs = [
    tokenizer("Explain continuous batching.")["input_ids"],
    tokenizer("Write a haiku.")["input_ids"],
]
outputs = model.generate_batch(inputs=inputs)
```

### Ordering, offload, and long contexts

- Incoming request order is preserved as of 5.1.0.
- CPU request offload arrives in 5.7.0. KV deduplication and memory estimation
  are corrected for generations of 16K tokens or more, and per-request sampling
  settings are documented.
- Tensor parallelism arrives in 5.9.0. `generate_batch()` restores
  `_attn_implementation` and fixes request offsets. Its OpenTelemetry
  integration is removed.
- As of 5.15.1, `max_requests_per_batch` and a configurable default compile
  level are available, and batching switches to Flash Attention automatically
  when appropriate.

## Speculative and multimodal generation

Gemma 4 Assistant adds Multi-Token Prediction speculative decoding in 5.8.0.
It reuses the target's KV cache to skip assistant prefill and cross-attends to
target context while drafting.

Generation gains Multi-Token Prediction decoding and static ensemble
verification for lossy speculative decoding in 5.15.1. Batched audio generation
is supported for Qwen2.5-Omni and Qwen3-Omni.

## Chat CLI

The simplified entry point is `transformers chat MODEL` as of 4.52.1.
Generation settings follow the model as `GenerationConfig`-style `key=value`
arguments.

```bash
transformers chat Qwen/Qwen2.5-0.5B-Instruct do_sample=False max_new_tokens=10
```

The CLI can use the same model served by `transformers serve`.

## Local serving

### Initial server (4.54.0)

`transformers serve` is a separate utility for experimentation and private
local use across supported modalities. It exposes these endpoint paths:

- `/v1/chat/completions`
- `/v1/responses`
- `/v1/audio/transcriptions`
- `/v1/models`

### Expanded server behavior (5.6.0)

The server adds legacy `/v1/completions`, audio and video inputs,
`--compile`, and `--model-timeout`. It forwards `tool_calls` and
`tool_call_id` into processor inputs and uses `parse_response` for tool calls.
A request naming a model other than the pinned server model returns HTTP 400.

### Response schema (5.9.0)

`GET /v1/models` returns `owned_by` as a string rather than the former
erroneous list.
