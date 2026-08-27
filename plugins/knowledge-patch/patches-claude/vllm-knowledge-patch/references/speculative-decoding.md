# Speculative Decoding

## Configure the method explicitly

`--spec-method`, `--spec-model`, and `--spec-tokens` populate the corresponding
fields of `--speculative-config`. A shorthand and the JSON object cannot both
set the same field. Automatic speculator detection is skipped for cloud-storage
model URIs, so those models need an explicit speculative configuration.

Inside `speculative_config`, use `draft_tensor_parallel_size`, not
`tensor_parallel_size`, for the draft model. `max_model_len` there also applies
to the draft model, while `temperature` and `top_p` remain sampling parameters.

## Suffix decoding

`method="suffix"` provides dynamic-depth speculation without another model.
Defaults are tree depth 24, a 10,000-request global cache, speculation factor
1.0, and minimum token probability 0.1. A zero cache limit disables the global
cache.

```bash
vllm serve MODEL --speculative-config '{
  "method": "suffix",
  "num_speculative_tokens": 8,
  "suffix_decoding_max_cached_requests": 0
}'
```

## N-gram lookup

When both `prompt_lookup_min` and `prompt_lookup_max` are omitted, they default
to 5. If only one is provided, the omitted bound copies it, so one bound
selects an exact lookup width.

```bash
vllm serve MODEL --speculative-config '{
  "method": "ngram",
  "num_speculative_tokens": 4,
  "prompt_lookup_min": 3
}'
```

N-gram speculation moved onto the GPU and became compatible with async
scheduling in `0.15-0.18`.

## Custom proposer classes

For an experimental custom backend, set `method="custom_class"` and place the
fully qualified proposer class name in `model`. The class receives a
`VllmConfig` and implements `propose`.

```python
llm = LLM(
    model="target-model",
    speculative_config={
        "method": "custom_class",
        "model": "my_package.MyProposer",
    },
)
```

A custom callable proposer is also accepted in `0.19-0.22`. Keep callable or
class loading explicit, especially when automatic detection is unavailable.

## Gemma 4 MTP assistants

A Gemma 4 assistant checkpoint uses `method="mtp"`, not the generic draft
model path. If startup resolves it as `draft_model`, upgrade to a build with
Gemma 4 MTP support rather than forcing that path.

```python
speculative_config={
    "method": "mtp",
    "model": "gemma-4-assistant-checkpoint",
}
```

## Heterogeneous vocabularies

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

Universal heterogeneous-vocabulary speculation later added TLI and DSpark
drafters (`0.23-0.26`). These additions do not remove the method and sampling
constraints of the configuration being used.

## Draft execution and acceptance

`parallel_drafting` is limited to EAGLE and draft-model methods. Rejection
sampling supports `strict` (default), `probabilistic`, or `synthetic`;
`synthetic_acceptance_rate` must be in `[0, 1]`.

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

Rejection sampling is intended to preserve the target distribution up to
numerical precision, and greedy decoding is validated against
non-speculative decoding. Token log probabilities are not guaranteed stable:
hardware precision and batch composition can still change probabilities or
outputs.

## Scheduling and parallel combinations

### Async scheduling

`--async-scheduling` was experimental in `0.7-0.10`. In 0.10.2 and early
`0.11-0.14`, it could corrupt output under preemption and other cases. It
later became default for supported configurations, initially excluding most
speculative decoding except MTP/Eagle.

Batch `0.15-0.18` added Unified Parallel Drafting, structured-output
compatibility, `min_tokens`, Mamba cache-align support, and async-compatible
GPU N-gram speculation.

Batch `0.19-0.22` made async scheduling and speculative decoding work together
with zero-bubble overlap. `--speculative-config` (`-sc`) can select a separate
MoE backend for the draft model. CPU draft-model speculation, thinking-budget
support, and an independent drafter attention backend followed.

### Pipeline and model-runner paths

Model Runner V2 expanded across `0.15-0.18` to pipeline and decode-context
parallelism plus probabilistic rejection sampling. It later gained
greedy/logprob rejection modes, multiple prompt logprobs, and multimodal
speculative embeddings (`0.19-0.22`).

Mamba block-aligned prefix caching became speculative-compatible in
`0.15-0.18`. In `0.23-0.26`, MRV2 added dynamic speculation under full CUDA
graphs and support for Mamba-hybrid paths.

## DFlash, DSpark, and dynamic speculation

Batch `0.23-0.26` added causal DFlash, dynamic speculative decoding, and a
FlashInfer-backed DFlash path. It then added universal heterogeneous-vocabulary
speculation through TLI and DSpark, runtime draft-weight updates,
hybrid sliding-window/full-attention DFlash drafters, and a separate
`kv_cache_dtype` inside `speculative_config`.

In `0.27.1`, quantized DSpark Markov heads are supported. A DSpark Markov head
is replicated across tensor-parallel ranks, and `sample_from_anchor` is loaded
from speculator configuration. When multiple stop strings match, speculative
decoding selects the earliest-completing match.

## Structured output and reasoning boundaries

Structured output became compatible with speculative decoding in
`0.7-0.10`, and Unified Parallel Drafting gained structured-output support in
`0.15-0.18`. In `0.27.1`, the structured-output grammar advances across the
boundary between reasoning and final output instead of treating that
transition as outside grammar state.

Unsupported speculative sampling parameters are rejected instead of silently
ignored (`0.11-0.14`). Test the exact combination of parser, grammar,
reasoning mode, acceptance method, and runner.

## Model-specific combinations

Llama 4 gained EAGLE support in `0.7-0.10`. DeepSeek V4 later gained MTP
speculation, and Gemma 4 uses the dedicated MTP assistant path
(`0.19-0.22`). MRV2 in `0.27.1` supports a multi-layer MTP speculator.

## Troubleshooting checklist

- Print the resolved method, proposer model/class, draft TP size, draft context
  length, KV-cache dtype, and acceptance method.
- Check whether shorthands and the JSON object set the same field.
- For cloud model URIs, supply the method explicitly.
- For heterogeneous vocabularies, validate shared normalized tokens and greedy
  sampling.
- If output diverges, compare target-only greedy decoding before treating
  logprob variation as a losslessness failure.
- If structured output fails around reasoning, verify grammar advancement and
  parser compatibility on the installed build.
