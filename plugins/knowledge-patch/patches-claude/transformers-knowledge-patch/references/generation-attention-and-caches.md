# Generation, attention, and caches

## Assisted and custom generation

### Universal assistants (4.50.0)

Assisted generation can use an assistant from a different model family and can
run while sampling with `do_sample=True`; matching architectures are no longer
required.

```python
pipe = pipeline(
    "text-generation",
    model="google/gemma-2-9b",
    assistant_model="double7/vicuna-68m",
    do_sample=True,
)
```

### Hub and local custom generation (4.52.1, 4.57.0, 5.15.1)

`model.generate(custom_generate=...)` can load an implementation from a Hub
repository, and custom implementations may use relative imports. Because the
implementation executes code, set `trust_remote_code=True` only after review.
The same explicit trust is required when `custom_generate` points to a local
directory.

### Removed decoding modes (4.56.0, 4.57.0)

DoLa and Contrastive Search moved to the
`transformers-community/dola` and
`transformers-community/contrastive-search` remote-code repositories. Group
Beam Search and Constrained Beam Search were removed outright.

### Generation inputs and penalties (5.3.0, 5.9.0)

Generation always supplies full `input_ids` to
`prepare_inputs_for_generation` and no longer expects overrides to slice inputs
using `cache_position`. A repetition penalty requires `input_ids`, even if the
rest of a path begins from embeddings. Gemma 4 generation accepts
`inputs_embeds` and `per_layer_inputs`, with the latter exposed on every Gemma 4
variant.

### Speculative and multimodal decoding (5.8.0, 5.15.1)

Gemma 4 Assistant provides Multi-Token Prediction drafting: it reuses the
target's KV cache to skip assistant prefill and cross-attends to the target
context. Generation later added general Multi-Token Prediction decoding and
static ensemble verification for lossy speculative decoding. Sliding-window
cache layers can roll back during speculation, stop strings can match across
byte-fragment tokens, and Qwen2.5-Omni and Qwen3-Omni support batched audio
generation.

## Attention registration and selection

### Custom attention (4.51.0, 5.2.0, 5.6.0)

Attention functions can be registered for Transformers models. The library-wide
attention-mask interface changed in 5.2.0, so older custom functions and model
integrations need migration. Custom attention code must also call the rotary
function directly; it is no longer installed as `self.rotary_fn(...)`.

### No silent eager fallback (4.53.0)

Unsupported combinations of `output_attentions=True` and a selected attention
implementation fail early. Attention implementations no longer silently fall
back to eager. Flash Attention 3 is supported across widely used models.

### Runtime and Hub-selected implementations (4.54.0, 4.56.0)

Use `set_attn_implementation` to change an implementation at runtime. A Hub
kernel package selects a build compatible with installed CUDA and PyTorch, and
Hub references may include an `@revision` suffix.

```python
model.set_attn_implementation("kernels-community/flash-attn3@main")
```

### Flash Attention behavior and requirements (4.55.0, 4.56.0, 5.4.0)

GPT-OSS can use the sink-aware
`kernels-community/vllm-flash-attn3` implementation on Hopper with PyTorch 2.7
or 2.8 after upgrading `kernels`. Flash Attention's sliding-window boundary is
no longer off by one, Flash Attention 2 can continue from an existing cache,
and causality handling supports bidirectional attention. Flash Attention 2
requires 2.3.3 or newer. Initial Flash Attention 4 support includes a `kernels`
fallback.

### Model-family backend defaults (5.1.0, 5.2.0, 5.15.1)

T5Gemma2 propagates the chosen implementation into all subconfigurations,
including `config.encoder.text_config`; bidirectional attention is supported
across models, and Attention and Experts can be used as standalone components.
ModernBERT no longer implicitly chooses Flash Attention. T5, MT5, LongT5, and
related families now support SDPA and registered backends; request
`attn_implementation="eager"` when eager behavior is required.

### Linear-attention kernel opt-in (5.15.1)

Mamba, GDN, and convolution-only families use native fallbacks unless loaded
with `use_kernels=True`. Make the opt-in explicit when retaining kernel-backed
execution is intentional.

## Cache model and migrations

### Per-layer cache architecture (4.54.0)

KV caches are represented per layer, enabling hybrids that mix attention types.
`CacheProcessor` encapsulates quantization and offload policy independently of
the cache representation. Non-generative models no longer use KV caches.

### Static and sliding-window caches (4.55.0, 4.56.0)

Vision encoder-decoder models support static caches, and `generate()` accepts a
tensor `cache_position`. `DynamicSlidingWindowLayer` and its cache retain only
the states required by sliding-window and chunk attention. A checkpoint default
of `cache_implementation="hybrid"` is ignored in favor of the dynamic
sliding-window cache, avoiding a slow static-cache first generation.

Model implementations initialize caches explicitly, return `Cache` objects,
and standardize the argument name as `past_key_values`, not `past_key_value`.
Deprecated cache objects were removed, and `from_legacy_cache` was placed on a
deprecation path.

### Sliding-window enforcement and paged CPU caches (5.1.0)

Generation cache preparation receives the model configuration and enforces its
sliding-window limit. Code that depended on an effectively unbounded cache can
change output or require shorter sequences. Paged caches can reside on CPU.

### Removed split and forward-position APIs (5.2.0, 5.4.0)

`EncoderDecoderCache.batch_split` was removed. Most major model `forward`
methods no longer accept `cache_position`; remove it from direct calls because
`generate` manages positions.

### Native Mamba and shared multimodal KV state (5.5.0, 5.6.0)

Mamba-only and Mamba/attention hybrids have native cache classes; replace
custom cache workarounds. Gemma 4 and Gemma 3n share KV states independently of
whether the caller passes a `Cache` object, so object choice no longer controls
sharing.

### Relative crop contract (5.15.1)

Cache cropping accepts a relative removal count rather than an absolute target
length:

```python
cache.crop(-tokens_to_remove)
```

### Result-affecting cache fixes (5.7.0, 5.15.1)

T5Gemma2 long cross-attention selects the correct cache-layer type; Qwen3.5
Gated DeltaNet handles multi-token cached forwards; and attention-only
GraniteMoeHybrid does not update a nonexistent Mamba mask. Gemma 3/4 image-token
attention respects local sliding windows. Multi-head Latent Attention cache
compression and recurrent-layer padding masks were corrected for chunked
prefill and cache continuation.

## Continuous batching

### Stable batched generation (4.57.0)

`generate_batch` supports stable batching for full- and sliding-window models.
The documented path uses `_attn_implementation="sdpa_paged"` with a
left-padding tokenizer and is suitable for training/evaluation workloads such
as GRPO as well as `transformers serve`. Inputs are lists of token-ID sequences,
and results are keyed by request ID.

```python
model.generation_config.max_new_tokens = 32
tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side="left")
outputs = model.generate_batch(inputs=[first_ids, second_ids])
```

### Ordering, media, offload, and long context (5.1.0, 5.7.0)

Batching preserves request arrival order. `make_batched_video` accepts
five-dimensional arrays. Requests can be offloaded to CPU, and per-request
sampling parameters are available. KV deduplication and memory estimation were
corrected for generations of 16K tokens or more.

### Parallelism, state restoration, and telemetry (5.9.0)

Continuous batching supports tensor parallelism. `generate_batch()` restores
`_attn_implementation` and uses corrected request offsets. Its OpenTelemetry
integration was removed.

### Request and compilation controls (5.15.1)

Use `max_requests_per_batch` to cap a batch, select the default compile level,
and allow automatic switching to Flash Attention where appropriate.

## Diagnostics

### Attention-mask visualization (4.50.0)

`AttentionMaskVisualizer` loads a tokenizer and model ID and displays ordinary,
sliding-window, and multimodal attention layouts.

```python
from transformers.utils.attention_visualizer import AttentionMaskVisualizer

AttentionMaskVisualizer("meta-llama/Llama-3.2-3B-Instruct")(
    "A normal attention mask"
)
```
