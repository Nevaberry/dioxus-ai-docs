---
name: transformers-knowledge-patch
description: Transformers
version: "5.9.0"
license: MIT
metadata:
  author: Nevaberry
---


# Transformers Knowledge Patch

Load this skill before changing Transformers applications, integrations, custom
models, tokenizers, processors, training loops, or serving code. Determine the
installed Transformers version first and apply only guidance introduced at or
below that version. Prefer the project's manifests, code, and tests whenever
they disagree with this patch.

## Reference index

| Reference | Topics |
| --- | --- |
| [Compatibility and API migration](references/compatibility-and-api-migration.md) | Runtime floors, removals, tokenizers, configuration, renamed and changed APIs |
| [Generation, caches, and serving](references/generation-caches-and-serving.md) | Generation contracts, cache behavior, continuous batching, chat CLI, local serving |
| [Loading, quantization, and kernels](references/loading-quantization-and-kernels.md) | Checkpoint loading, quantizers, attention backends, custom kernels, serialization |
| [Model and task integrations](references/model-and-task-integrations.md) | Language, multimodal, vision, audio, document, scientific, and robotics architectures |
| [Multimodal processing and pipelines](references/multimodal-processing-and-pipelines.md) | Processors, chat templates, media inputs, pipeline behavior, visualization |
| [Training and distributed execution](references/training-and-distributed-execution.md) | Trainer behavior, tensor/expert/sequence parallelism, FSDP, optimizers, backends |

## Start with the breaking changes

### Update runtime dependencies

- Transformers 5.2.0 requires Python 3.10 or newer.
- Transformers 5.1.0 requires PyTorch 2.4 or newer; 4.56.0 had already raised
  the floor to PyTorch 2.2.
- TensorFlow and JAX backends are deprecated since 4.53.0.

### Migrate tokenizer code for v5

- Call the tokenizer instead of `encode_plus`.
- `decode` accepts single and batched inputs; `batch_decode` is no longer
  required for the batched case.
- `apply_chat_template` returns `BatchEncoding`; select `input_ids` rather
  than treating the result as a tensor or list.
- Use `text_target` instead of `as_target_tokenizer`; use `word_ids()` instead
  of `BatchEncoding.words()`.
- A tokenizer constructor does not accept `vocab_file`; use `from_pretrained`
  for file-backed loading, or construct with `vocab` and `merges`.
- Repositories must declare `model_type`; `AutoTokenizer` no longer infers it
  from a directory name as of 5.2.0.

### Migrate model loading

- Prefer `dtype`; `torch_dtype` is transitional. In v5, `from_pretrained`
  defaults `dtype="auto"`, preserving the checkpoint dtype.
- Replace `use_auth_token` with `token`.
- Replace top-level `load_in_4bit` and `load_in_8bit` with a
  `quantization_config`, such as `BitsAndBytesConfig`.
- Pass configuration values by keyword: configuration classes are dataclasses
  and reject positional arguments as of 5.4.0.
- Use a local directory or Hub repository for configs; arbitrary config URLs
  are not supported in v5.

### Migrate configuration access

- Read rotary settings from `config.rope_parameters`, not direct attributes
  such as `config.rope_theta`.
- Read architecture-specific values from subconfigs, for example
  `config.text_config.vocab_size` for Qwen-VL.
- Use `config.backbone_config` as the source of truth for backbone models.
- Non-generative configs do not have `generation_config`.
- Preserve heterogeneous `per_layer_config` data instead of assuming one
  global attention configuration.

### Remove retired APIs and strategies

- `transformers.agents` is removed; migrate agent code to `smolagents`.
- DoLa, Contrastive Search, Group Beam Search, and Constrained Beam Search are
  no longer built in. The first two are available as trusted custom-generation
  implementations.
- Head masking, head pruning, BERT-like relative positional biases,
  `torchscript`, and `torch.fx` integrations are removed in v5.
- `pad_to_max_length`, `EncoderDecoderCache.batch_split`, the ASR pipeline's
  `num_frames`, and the misspelled `AnnotionFormat` are removed.
- The Apex integration is removed; use native PyTorch mixed precision and
  fused operations.

### Update custom model and attention code

- Custom attention implementations must adopt the 5.2.0 attention-mask
  interface and call rotary functions directly rather than through
  `self.rotary_fn` as of 5.6.0.
- Generation now supplies full `input_ids` to `prepare_inputs_for_generation`;
  do not slice inputs with `cache_position`.
- Most direct model `forward` methods no longer accept `cache_position` as of
  5.4.0; let `generate` manage it.
- Inputs use the plural name `inputs_embeds`.
- Custom integrations must migrate away from private layer, mask, cache,
  hybrid-attention, linear-layer, and multimodal processor helpers.

## Loading and execution quick reference

### Make kernel selection explicit

- Installing `kernels` does not activate decorated forward methods. Pass
  `use_kernels=True` or choose a registered `attn_implementation`.
- Linear-attention families use native fallbacks by default as of 5.15.1;
  pass `use_kernels=True` to retain kernel-backed execution.
- ModernBERT no longer chooses Flash Attention implicitly as of 5.2.0.
- T5-family models can select SDPA or another registered backend; request
  `attn_implementation="eager"` when eager execution is required.
- Unsupported `output_attentions=True` combinations fail instead of silently
  falling back to eager attention.

### Respect quantization constraints

- Tensor-parallel quantized inference in 4.52.1 supports only
  `compressed-tensors`, `fp8`, and `fp8-fbgemm`.
- FP-Quant initially implements post-training MXFP4; accelerated execution
  needs Blackwell hardware and QuTLASS, while `pseudoquant=True` emulates it.
- Quantizing an already quantized model is an error as of 4.56.0.
- torchao requires version 0.15.0 or newer as of 5.4.0.
- Use the full loading and kernel matrix in the loading reference before
  combining quantization, device maps, tensor parallelism, or custom kernels.

## Generation and serving quick reference

### Use current cache contracts

- Cache implementations initialize caches explicitly and return `Cache`
  objects; use `past_key_values`, not `past_key_value`.
- Sliding-window generation enforces configured limits and retains only needed
  state. Output can differ from older effectively unbounded behavior.
- Crop a cache by negative relative offset, for example
  `cache.crop(-tokens_to_remove)`; absolute target lengths are unsupported as
  of 5.15.1.
- Native caches replace custom Mamba and mixed Mamba-attention workarounds.

### Choose the right generation path

- Assisted generation accepts an assistant from another architecture and also
  works with sampling.
- `custom_generate` executes code. Both Hub and local implementations require
  explicit `trust_remote_code=True` where specified.
- Continuous batching uses `generate_batch`; it supports paged attention,
  sliding-window models, CPU offload, tensor parallelism, and request controls.
- Repetition penalties require `input_ids` as of 5.9.0.

### Serve locally

- `transformers serve` is intended for experimentation and private local use.
  It exposes chat, responses, transcription, model-listing, and legacy
  completions endpoints.
- Requests naming a model other than the server's pinned model receive HTTP
  400. Use `--compile` and `--model-timeout` where appropriate.
- `transformers chat MODEL key=value` accepts `GenerationConfig`-style
  settings and can target the same local server.

## Processing and training quick reference

### Handle multimodal inputs deliberately

- `apply_chat_template` accepts in-memory video, PIL images, audio/video chat
  content, and `image_url` entries where supported.
- SAM3-family `text_embeds` expects full text embeddings, not pooler output.
- Gemma 4 vision preprocessing uses fixed soft-token budgets and internal
  scaling; do not add ImageNet normalization.
- The unified image-processor backend lives in `image_processing_utils`; the
  old fast module is removed.

### Check changed training semantics

- `TrainingArguments.average_tokens_across_devices` defaults to enabled.
- Final partial gradient-accumulation windows now receive correct loss scaling.
- `Trainer` aligns model special tokens with the tokenizer and supports
  sequence parallel evaluation plus `ddp_static_graph`.
- Corrected expert-parallel and FSDP behavior can change formerly wrong or NaN
  results; re-baseline affected training jobs.

## Working method

1. Inspect the installed Transformers, Python, PyTorch, accelerator, and
   quantization-package versions.
2. Locate the task in the reference index and apply only relevant guidance.
3. Treat explicit trust flags as security boundaries, especially for custom
   generation and previously remote-code model integrations.
4. Re-run representative preprocessing, generation, cached decoding, and
   training tests when a result-affecting correction applies.
5. Pin revisions for Hub kernels or Git-only model releases when reproducible
   artifacts matter.
