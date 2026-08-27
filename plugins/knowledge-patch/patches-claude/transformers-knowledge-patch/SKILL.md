---
name: transformers-knowledge-patch
description: Transformers
version: "5.9.0"
license: MIT
metadata:
  author: Nevaberry
---


# Transformers Knowledge Patch

Use this skill when writing, migrating, reviewing, or debugging Python that uses
Hugging Face Transformers. It emphasizes API removals, changed defaults,
loading and generation contracts, cache and attention behavior, distributed
execution, multimodal processing, serving, and newly integrated model families.

## How to use this skill

1. Inspect the project's pinned `transformers`, Python, PyTorch, quantization,
   and accelerator versions before changing code.
2. Start with the breaking-change checks below when moving from a 4.x project
   or when old examples fail under 5.x.
3. Open the topic reference that matches the code path under review.
4. Prefer public APIs and explicit configuration over private helpers, inferred
   defaults, or model-specific cache workarounds.
5. Re-run numerical, generation, preprocessing, and distributed tests after an
   upgrade; several fixes intentionally change results.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migration and runtime](references/migration-and-runtime.md) | Runtime floors, loading defaults, configuration migrations, removed APIs, serialization, backend behavior |
| [Generation, attention, and caches](references/generation-attention-and-caches.md) | Decoding, attention backends, custom attention, KV caches, speculative decoding, continuous batching |
| [Loading, quantization, and kernels](references/loading-quantization-and-kernels.md) | Checkpoint conversion, quantizers, GGUF, FP8/MXFP4/NVFP4, torchao, downloadable and custom kernels |
| [Tokenizers, processors, and multimodal inputs](references/tokenizers-processors-and-multimodal.md) | Tokenizer backend migration, chat templates, image/video/audio preprocessing, embedding and position-ID contracts |
| [Training and distributed execution](references/training-and-distributed.md) | Trainer changes, tensor/expert/sequence parallelism, FSDP, compilation, weight tying and export |
| [Serving, pipelines, and tools](references/serving-pipelines-and-tools.md) | `transformers serve`, chat CLI, pipelines, observability, visualization and callbacks |
| [Model and task integrations](references/model-and-task-integrations.md) | Language, vision, document, audio, multimodal, time-series, robotics and scientific architectures |

## Breaking-change checklist

### Use `dtype`, not `torch_dtype`

Pass `dtype=` to loading and pipeline APIs. Loading now defaults to `auto`, so
it preserves the checkpoint dtype rather than forcing float32. Specify a dtype
when exact precision is required.

```python
model = AutoModelForCausalLM.from_pretrained(model_id, dtype="auto")
```

### Move quantization flags into a configuration

Top-level `load_in_4bit` and `load_in_8bit` arguments are removed. Use a
quantization configuration.

```python
from transformers import BitsAndBytesConfig

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    quantization_config=BitsAndBytesConfig(load_in_4bit=True),
)
```

### Replace authentication and agent APIs

- Replace `use_auth_token=` with `token=`.
- Use `smolagents`; `transformers.agents` is removed.
- Treat every custom generation implementation as executable code. Whether it
  comes from the Hub or a local directory, opt in with
  `trust_remote_code=True` only after reviewing it.

### Update tokenizer calls and outputs

- Call the tokenizer instead of `encode_plus`.
- Use `text_target=` instead of `as_target_tokenizer()` or target-mode helpers.
- Use `word_ids()` instead of `BatchEncoding.words()`.
- Expect `apply_chat_template()` to return a `BatchEncoding`; read
  `input_ids` or the required field explicitly.
- Use `extra_special_tokens` for unnamed additions. Newly saved tokenizers no
  longer write `special_tokens_map.json` or `added_tokens.json`.

```python
chat = tokenizer.apply_chat_template(messages, return_tensors="pt")
input_ids = chat["input_ids"]
```

### Migrate configuration access

- Construct configuration dataclasses with keyword arguments only.
- Read rotary settings from `config.rope_parameters`.
- Read multimodal values from their subconfigurations, such as
  `config.text_config.vocab_size`.
- Use `config.backbone_config` as the source of backbone selection.
- Do not assume non-generative configs contain `generation_config`.
- Preserve heterogeneous `per_layer_config` instead of flattening it into one
  global attention configuration.

### Remove legacy model and pipeline hooks

- Head masking, head pruning, and BERT-style relative positional biases are not
  supported; keep such workloads on 4.x or redesign them.
- Replace Transformers `torchscript` and `torch.fx` integrations with PyTorch
  `dynamo` or `export`.
- Replace imports from removed `image_processing_utils_fast` with
  `image_processing_utils`.
- Audit removed or renamed pipeline tasks, especially question answering,
  visual question answering, and image-to-image.
- Replace Apex mixed precision and fused operations with native PyTorch.

## Generation and cache essentials

### Let generation own cache positions

Custom `prepare_inputs_for_generation` implementations now receive full
`input_ids`; do not slice them by `cache_position`. Most model `forward` methods
also no longer accept `cache_position` because `generate` manages it.

Cache objects are first-class and per-layer. Use native dynamic,
sliding-window, hybrid, Mamba, and paged cache types instead of legacy tuples or
model-specific workarounds. Crop caches with a negative relative offset:

```python
cache.crop(-tokens_to_remove)
```

### Supply token IDs when penalties need them

Repetition penalties require `input_ids`, even when a generation path otherwise
starts from embeddings. Gemma 4 generation additionally supports
`inputs_embeds` and `per_layer_inputs`.

### Select attention explicitly when reproducibility matters

Unsupported attention/output combinations fail instead of silently falling
back. T5-family models can dispatch to SDPA and registered backends; set
`attn_implementation="eager"` when the eager path is required. Hub kernel
references may include a revision suffix.

```python
model.set_attn_implementation("kernels-community/flash-attn3@main")
```

Linear-attention and convolution-only families use native fallbacks unless
loaded with `use_kernels=True`.

## Loading and quantization essentials

### Treat checkpoint conversion as declarative

Use `WeightConverter` operations for reversible key mapping, tensor reshape,
merge, split, quantization, and parallelism conversion. Conversion applies
recursively to nested model structures.

### Validate device and quantizer combinations

- GGUF cannot be disk-offloaded.
- Quantized tensor parallelism is method-dependent.
- Do not quantize a model that is already quantized.
- MXFP4 can dequantize on CPU when the device map includes CPU.
- Torchao requires a recent compatible release; validate serialization paths
  for NVFP4 and custom parameter names.
- FP-Quant acceleration is hardware- and library-dependent; pseudoquant is an
  emulation path, not accelerated quantization.

## Training and distributed essentials

- `TrainingArguments.average_tokens_across_devices` is enabled by default.
- The final partial gradient-accumulation window now receives correct loss
  scaling; expect changed results for uneven batch counts.
- Review tensor-parallel conversion mappings after corrected decoder all-reduce
  handling.
- Treat expert-parallel and FSDP upgrades as numerically significant because
  fixes address silent wrong results, NaNs, and non-primary-rank weight damage.
- Use `ddp_static_graph` only when the graph is actually static.
- Prefer the native FSDP2 migration path for new distributed work.
- Compilation defaults to `fullgraph=False`; continuous batching has its own
  configurable compile level.

## Multimodal and preprocessing essentials

- Standardize embedding arguments on plural `inputs_embeds`.
- Use full text embeddings, not pooled outputs, for SAM3-family `text_embeds`.
- Preserve model-specific preprocessing: Gemma 4 has fixed patch budgets,
  divisible-by-48 dimensions, and internal `[-1, 1]` scaling, so do not apply
  ordinary ImageNet normalization.
- Expect CUDA Lanczos requests to fall back to bicubic; CPU and accelerator
  preprocessing can differ.
- Use the shared 3D position-ID interface for affected vision-language models.
- Keep heterogeneous image, video, and audio chat inputs in processor-supported
  message structures rather than private helper calls.

## Serving and batching essentials

`transformers serve` is a local experimentation and private-use server with
OpenAI-compatible model, chat, response, transcription, and completion APIs.
Its pinned model is authoritative; mismatched request model names receive HTTP
400. The models response reports `owned_by` as a string.

Continuous batching supports paged attention, sliding windows, CPU offload,
tensor parallelism, request ordering, per-request sampling, and request-count
limits. Validate long-context memory estimates and do not depend on the removed
continuous-batching OpenTelemetry integration.

## Upgrade validation

After changing versions, exercise all applicable paths:

- load/save round trips, tied weights, sharding, GGUF and quantized checkpoints;
- tokenizer serialization, special tokens, chat templates, and target encoding;
- cached and uncached generation, long sliding-window prompts, speculative
  rollback, repetition penalties, stop strings, and selected attention backend;
- CPU/CUDA image preprocessing plus batched image, video, and audio inputs;
- the final partial accumulation window and every distributed rank;
- serving schemas, model-name rejection, tool-call parsing, timeouts, and batch
  request ordering;
- numerical regression fixtures for model-specific attention, RoPE, cache,
  resizing, and interpolation corrections.
