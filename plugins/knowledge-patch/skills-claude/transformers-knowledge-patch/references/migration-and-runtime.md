# Migration and runtime

## Release and dependency behavior

### Model-specific Git tags (4.50.0)

Model integrations can ship between monthly PyPI releases as tags such as
`v4.49.0-Gemma-3`. Such a tag starts from `main` at model release time and may
be updated with fixes, so its contents can change and can include unrelated
integrations that were already on `main`.

### Runtime floors and backends (4.53.0, 4.56.0, 5.1.0, 5.2.0)

TensorFlow and JAX support was deprecated in 4.53.0. PyTorch's minimum rose to
2.2 in 4.56.0 and then to 2.4 in 5.1.0; current 5.x environments should satisfy
the latter. Python 3.10 or newer is required from 5.2.0. The unmaintained
`jieba` dependency was replaced with `rjieba` in 4.57.0, and MUSA gained TF32
flag support there. Initial `torch_tpu` backend support arrived in 5.9.0.

### Package and patch numbering (5.15.1)

Version 5.10.3 was not published to PyPI; the corresponding patch was published
as 5.10.4. Do not pin the nonexistent artifact.

## Removed and replaced APIs

### Agents and padding (4.50.0, 4.52.1)

`transformers.agents` was first deprecated in favor of `smolagents` and then
removed in 4.52.1. The deprecated `pad_to_max_length` argument was also removed.
PyTorch 2.0 support was already being phased out in that batch.

### Generation strategies (4.56.0, 4.57.0)

DoLa and Contrastive Search moved out of the library to the executable
`transformers-community/dola` and
`transformers-community/contrastive-search` repositories. Group Beam Search
and Constrained Beam Search were removed in 4.57.0. Remove those selections
from generation configurations or consciously adopt the remote implementation.

### Attention and PyTorch integration removals (5.0.0)

Head masking, head pruning, and relative positional biases in BERT-like models
were removed. Workloads that require them must stay on Transformers 4.x or be
redesigned. The Transformers `torchscript` and `torch.fx` integrations were
also dropped; use PyTorch `dynamo` and `export`.

### Renamed and removed symbols (5.1.0)

Use `AnnotationFormat`; the deprecated `AnnotionFormat` misspelling is gone.
The ASR pipeline no longer returns `num_frames`. Bamba, FalconH1, and
GraniteMoeHybrid expose formerly hardcoded `time_step` parameters in their
configurations.

### Pipeline task cleanup (5.3.0)

The v5 pipeline cleanup removes or changes `question-answering`,
`visual-question-answering`, and `image-to-image`. Migrate old task names to
the replacement or updated pipelines rather than relying on aliasing.

### Apex removal (5.8.0)

The Apex integration, Apex RMSNorm use in T5, and related model paths were
removed. Migrate Apex mixed precision and fused operations to native PyTorch.

## Loading and serialization defaults

### Preferred dtype argument (4.53.0, 4.56.0, 5.0.0)

Pipelines default to `dtype="auto"`. Across loading APIs, `dtype` replaces
`torch_dtype`, which remained accepted during the transition. In 5.0,
`from_pretrained` itself defaults to `dtype="auto"`, preserving the saved
checkpoint dtype instead of coercing to float32. Pass an explicit dtype when a
specific precision is part of the application contract.

### Authentication and quantization arguments (5.0.0)

Replace `use_auth_token` with `token`. Top-level `load_in_4bit` and
`load_in_8bit` are removed; express them through `quantization_config`, such as
`BitsAndBytesConfig(load_in_4bit=True)`.

### Shard size and tied checkpoint keys (5.0.0, 5.4.0)

The default maximum save shard size increased from 5 GB to 50 GB. Weight tying
now occurs even when a checkpoint contains both tied keys with identical
values, so verify `.bin` checkpoints containing duplicate tied keys after an
upgrade.

### Memory mapping (5.6.0)

`from_pretrained` accepts `disable_mmap` and detects hf-mount automatically.
Use the flag when memory-mapped checkpoint access is unsuitable for the storage
environment.

### Native LightGlue and configuration selection (5.5.0)

LightGlue is native and no longer supports remote-code execution; remove
`trust_remote_code=True` for it. `AutoConfig.from_pretrained` accepts an
explicit `model_type` override and prefers a registered configuration over
remote code when one exists.

## Configuration migration

### Constructors, URLs, rotary settings, and subconfigs (5.0.0)

Use ordinary nested-config constructors instead of removed `from_xxx_config`
helpers. Configuration files cannot be loaded from arbitrary URLs; use a local
path or Hub repository.

Rotary settings such as `rope_theta` and `rope_type` live under
`config.rope_parameters`, sometimes as mappings by layer type. Direct
`config.rope_theta` access fails. Read Qwen-VL values from subconfigs, for
example `config.text_config.vocab_size`. Non-generative configurations no
longer contain `generation_config`, so `model.config.generation_config` raises
an attribute error.

### Central backbone configuration (5.1.0)

For backbone-based models, `config.backbone_config` is the single source of
truth; redundant backbone-selection arguments were removed. Backbones are
constructed from configuration, and pretrained weights are loaded only if the
checkpoint actually contains backbone weights.

### Keyword-only dataclass configs (5.4.0)

`PreTrainedConfig` and model configuration classes are dataclasses and reject
positional arguments. Pass every configuration value by keyword.

### Heterogeneous layers (5.15.1)

Configurations may differ per layer. Gemma 4 represents its mixed attention
layout in `per_layer_config`; custom configs and checkpoint converters must
preserve that structure instead of assuming one global attention configuration.

## Custom integration migration

### Standardized modeling internals (5.15.1)

Downstream integrations that use private layer declarations, attention-mask or
cache construction, hybrid-attention handling, or legacy linear-layer type
names must migrate to standardized modeling internals. Private multimodal
processor helpers such as `_is_url` and `_build_image_tokens` were removed.

### GPTNeoX and GPTBigCode compatibility (5.15.1)

GPTNeoX checkpoint handling remaps `embed_out` to `lm_head`; update code tied
to the old key. GPTBigCode advertises attention-backend support through
`_supports_attention_backend = True`, which can change backend dispatch in
downstream systems such as vLLM.

## Result-affecting runtime changes

### Preprocessing and model execution (4.57.0, 5.1.0)

Fast `center_crop` now matches the slow implementation, and Whisper feature
extraction keeps `input_features` and `attention_mask` lengths consistent.
Janus resizing rounds rather than truncates dimensions, which can create small
numeric differences. `Siglip2Tokenizer` enforces its training-time text
preprocessing defaults.

### Correctness fixes that warrant regression tests (5.6.0, 5.7.0, 5.15.1)

Qwen2.5-VL no longer applies temporal RoPE scaling to still images, and
`Zamba2MambaMixer` respects `use_mamba_kernels=False`. Later cached-attention
fixes affect T5Gemma2 long cross-attention, Qwen3.5 Gated DeltaNet multi-token
cached forwards, and attention-only GraniteMoeHybrid. Gemma 3/4 local image
attention now respects sliding-window bounds; Multi-head Latent Attention cache
compression and recurrent-layer padding masks during chunked prefill or cache
continuation were also corrected. Re-baseline results where these paths matter.
