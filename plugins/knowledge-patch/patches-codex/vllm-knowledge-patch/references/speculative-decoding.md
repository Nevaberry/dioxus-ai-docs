# Speculative Decoding

Use this reference to choose and configure draft models, MTP, n-gram, suffix,
custom, DFlash, DSpark, and heterogeneous-vocabulary speculation.

## Configuration surface

### Component shorthands (`engine-and-openai-server`)

`--spec-method`, `--spec-model`, and `--spec-tokens` populate corresponding
fields in `--speculative-config`. Do not set one field through both a shorthand
and the JSON object. Cloud-storage model URIs skip automatic speculator
detection and therefore need an explicit speculative configuration.

### Drafter-specific settings (`speculative-decoding`)

Inside `speculative_config`, use `draft_tensor_parallel_size`, not
`tensor_parallel_size`. Its `max_model_len` also belongs to the draft model;
`temperature` and `top_p` remain sampling parameters. `parallel_drafting` is
limited to EAGLE and draft-model methods.

Rejection sampling accepts `strict` (default), `probabilistic`, or `synthetic`.
For synthetic acceptance, `synthetic_acceptance_rate` must be within `[0, 1]`:

```python
speculative_config={
    "method": "draft_model",
    "model": "draft-model",
    "draft_tensor_parallel_size": 2,
    "parallel_drafting": True,
    "rejection_sample_method": "synthetic",
    "synthetic_acceptance_rate": 0.8,
}
```

## Draft-free and lookup methods

### Suffix decoding (`speculative-decoding`)

`method="suffix"` provides dynamic-depth speculation without another model.
Defaults are tree depth 24, a 10,000-request global cache, speculation factor
1.0, and minimum token probability 0.1. Set the cache limit to zero to disable
shared global state:

```bash
vllm serve MODEL --speculative-config '{
  "method": "suffix",
  "num_speculative_tokens": 8,
  "suffix_decoding_max_cached_requests": 0
}'
```

### N-gram lookup (`speculative-decoding`)

When both `prompt_lookup_min` and `prompt_lookup_max` are omitted, each
defaults to 5. If only one is set, the omitted bound copies it, selecting an
exact width:

```bash
vllm serve MODEL --speculative-config '{
  "method": "ngram",
  "num_speculative_tokens": 4,
  "prompt_lookup_min": 3
}'
```

GPU NGram execution and combination with async scheduling arrived in
`0.15-0.18`.

## Custom proposers and assistant checkpoints

### Custom class (`speculative-decoding`)

Set `method="custom_class"` and place the fully qualified proposer class in
`model`. The class is constructed with `VllmConfig` and implements `propose`:

```python
llm = LLM(
    model="target-model",
    speculative_config={
        "method": "custom_class",
        "model": "my_package.MyProposer",
    },
)
```

Custom callable proposers were also added to the normal runtime in
`0.19-0.22`.

### Gemma 4 assistant via MTP (`speculative-decoding`)

Configure a Gemma 4 assistant checkpoint with `method="mtp"`, not as a generic
draft model. If startup resolves it to `draft_model`, upgrade to a build with
Gemma 4 MTP support rather than forcing the wrong path:

```python
speculative_config={
    "method": "mtp",
    "model": "gemma-4-assistant-checkpoint",
}
```

## Heterogeneous vocabularies

### Draft-model restriction (`speculative-decoding`)

Set `use_heterogeneous_vocab=True` only with `method="draft_model"`.
Initialization intersects normalized token strings and constrains proposals to
shared tokens. This mode is greedy-only; probabilistic draft sampling is not
supported.

```python
speculative_config={
    "method": "draft_model",
    "model": "different-tokenizer-draft-model",
    "num_speculative_tokens": 3,
    "use_heterogeneous_vocab": True,
}
```

### Universal heterogeneous speculation (`0.23-0.26`)

TLI enables universal speculation across heterogeneous vocabularies, with
DSpark drafters available on that path.

## Execution combinations and new methods

### Structured output and cache alignment (`0.15-0.18`)

Unified Parallel Drafting and structured-output compatibility were added.
Speculation supports `min_tokens` and Mamba cache-align mode. GPU NGram can run
with async scheduling.

### CPU drafts and independent backends (`0.19-0.22`)

Speculation combines with async scheduling using zero-bubble overlap. A draft
model may select a per-model MoE backend through `--speculative-config` (`-sc`).
CPU draft models are supported. Thinking budgets are honored, and the drafter
may choose an independent attention backend.

### DFlash, DSpark, and runtime updates (`0.23-0.26`)

Causal DFlash, dynamic speculation, and FlashInfer-backed DFlash are supported.
Draft weights can be updated at runtime. DFlash supports hybrid
sliding-window/full-attention drafters, and `speculative_config` has a distinct
`kv_cache_dtype`.

### DSpark Markov heads (`0.27.1`)

Quantized DSpark Markov heads are supported. A Markov head is replicated across
tensor-parallel ranks, and `sample_from_anchor` loads from speculator
configuration. If multiple stop strings match, speculation selects the one
that completes earliest.

### Structured reasoning boundary (`0.27.1`)

The structured-output grammar advances across the transition between reasoning
and final output while speculation is active.

## Correctness expectations

### Sampling validation (`0.11-0.14`)

Unsupported speculative-decoding sampling parameters are rejected instead of
being silently ignored.

### Distribution versus exact log probabilities (`speculative-decoding`)

Rejection sampling preserves the target distribution up to numerical
precision, and greedy decoding is validated against non-speculative decoding.
Token log probabilities are not stable guarantees: hardware precision and
batch composition can change probabilities or outputs across runs.
