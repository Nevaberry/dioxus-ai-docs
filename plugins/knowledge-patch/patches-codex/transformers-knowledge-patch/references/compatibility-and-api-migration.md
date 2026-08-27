# Compatibility and API migration

Use this reference when upgrading runtimes, public APIs, custom integrations,
tokenizers, processors, or configuration code.

## Release artifacts and runtime floors

### Model-specific Git tags (4.50.0)

Some integrations ship as Git-only tags such as `v4.49.0-Gemma-3` between
monthly package releases. A tag starts from `main` at the model release and can
be updated as model-specific fixes land, so its contents can change and can
include unrelated integrations already on `main`. Pin a commit when exact
reproducibility matters.

### Runtime changes

- TensorFlow and JAX backends are deprecated (4.53.0).
- PyTorch 2.0 support is being phased out as of 4.52.1.
- PyTorch 2.2 is the minimum supported version as of 4.56.0; the former
  `triton_kernels` dependency is replaced by `kernels`.
- PyTorch 2.4 is the minimum supported version as of 5.1.0. The GPT-OSS kernel
  package is renamed to `gpt-oss-triton-kernels`.
- Python 3.10 or newer is required as of 5.2.0.

### Patch numbering (5.15.1)

Version 5.10.3 was not published to PyPI; that patch was published as 5.10.4.

## High-impact removals and replacements

| Removed or deprecated API | Migration |
| --- | --- |
| `transformers.agents` deprecated in 4.50.0 and removed in 4.52.1 | Use the separate `smolagents` library. |
| `pad_to_max_length` removed in 4.52.1 | Use explicit padding and truncation options. |
| DoLa and Contrastive Search removed in 4.56.0 | Use `transformers-community/dola` or `transformers-community/contrastive-search` through trusted custom generation. |
| Group Beam Search and Constrained Beam Search removed in 4.57.0 | Remove these choices from generation configurations and callers. |
| `use_auth_token` deprecated in 5.0.0 | Pass `token` with the same value. |
| Top-level `load_in_4bit` and `load_in_8bit` removed in 5.0.0 | Pass a quantization configuration such as `BitsAndBytesConfig`. |
| Head masking, head pruning, and BERT-like relative positional biases removed in 5.0.0 | Stay on 4.x if the workload fundamentally requires them. |
| Transformers `torchscript` and `torch.fx` integrations removed in 5.0.0 | Use PyTorch `dynamo` and `export`. |
| `AnnotionFormat` removed in 5.1.0 | Use the correctly spelled `AnnotationFormat`. |
| ASR pipeline `num_frames` removed in 5.1.0 | Stop reading or supplying that entry. |
| `EncoderDecoderCache.batch_split` removed in 5.2.0 | Refactor code around supported cache operations. |
| Apex integration removed in 5.8.0 | Use native PyTorch mixed precision or fused operations. |

## Tokenizer migration

### Unified backends and construction (5.0.0)

Tokenizers use one implementation selected from `TokenizersBackend`,
`SentencePieceBackend`, `PythonBackend`, or `MistralCommonBackend`.
`AutoTokenizer.from_pretrained()` still selects the backend automatically.
`PythonBackend` takes the former `PreTrainedTokenizer` role for custom Python
tokenizers; `PreTrainedTokenizerBase` is the minimal backend-independent API.

Tokenizers backed by `tokenizers` can be created empty for training or directly
from `vocab` and `merges`. Constructors do not accept `vocab_file`; use
`from_pretrained` for file-backed loading.

```python
from transformers import LlamaTokenizer

blank = LlamaTokenizer()
tokenizer = LlamaTokenizer(vocab=vocab, merges=merges)
```

### Unified calls and return types (5.0.0)

- Calling the tokenizer replaces `encode_plus`.
- `decode` handles both single and batched input, removing the need to select
  `batch_decode` for batches.
- `apply_chat_template` returns `BatchEncoding`; select `input_ids` or another
  field explicitly.

```python
encoded = tokenizer(["hello", "world"])
texts = tokenizer.decode(encoded["input_ids"])
chat = tokenizer.apply_chat_template(messages, return_tensors="pt")
input_ids = chat["input_ids"]
```

### Serialization and special tokens (5.0.0)

New saves put named special tokens in `tokenizer_config.json` and added tokens
in `tokenizer.json`. Older `special_tokens_map.json` and `added_tokens.json`
files remain readable but are not written. `special_tokens_map` contains only
named attributes; put extra tokens in `extra_special_tokens`.
`additional_special_tokens` is converted for compatibility, and extended
special-token accessors are removed.

### Target encoding and subclass responsibilities (5.0.0)

- `sanitize_special_tokens()` and target-mode helpers such as
  `as_target_tokenizer()` are removed.
- Use `text_target` for target encoding; `prepare_seq2seq_batch()` is
  deprecated.
- Replace `BatchEncoding.words()` with `word_ids()`.
- Custom subclasses cannot rely on base implementations of
  `create_token_type_ids_from_sequences`, `prepare_for_model`,
  `build_inputs_with_special_tokens`, or `truncate_sequences`; implement these
  behaviors or obtain them from `PythonBackend`.

```python
model_inputs = tokenizer(
    source_texts,
    text_target=target_texts,
    max_length=128,
    return_tensors="pt",
)
model_inputs["labels"] = model_inputs.pop("input_ids_target")
```

### Automatic selection and text cleanup

As of 5.2.0, `AutoTokenizer` does not infer a tokenizer type from a model
directory name when configuration lacks `model_type`. Repositories that relied
on substrings such as `bert` must declare the type.

The class-selection change that chose the wrong tokenizer for models such as
DeepSeek R1 was reverted in 5.7.0. `PreTrainedTokenizerFast` also skips
`clean_up_tokenization` for BPE tokenizers. In 5.8.0, DeepSeek OCR tokenizer
mapping was corrected so automatic loading selects the intended class.

The unmaintained `jieba` dependency is replaced by `rjieba` as of 4.57.0.

### Model-specific tokenizer behavior

- `Siglip2Tokenizer` enforces its training-time preprocessing defaults
  (5.1.0).
- Llama 3 conversion sets `clean_up_tokenization_spaces=False` (5.4.0).

## Configuration migration

### v5 construction and access (5.0.0)

- Replace removed `from_xxx_config` helpers with ordinary constructors.
- Configs cannot load from arbitrary URL files; use a local path or Hub
  repository.
- Rotary settings such as `rope_theta` and `rope_type` live under
  `config.rope_parameters`. Some architectures provide a nested mapping per
  layer type.
- Qwen-VL values are in subconfigs, for example
  `config.text_config.vocab_size` rather than a top-level field.
- Non-generative configs do not expose `generation_config`; direct access on
  `model.config` raises `AttributeError`.

### Backbone source of truth (5.1.0)

Backbone models use `config.backbone_config`; redundant backbone-selection
arguments are removed. Backbones are constructed from configuration, and
pretrained weights load only when the checkpoint includes backbone weights.
T5Gemma2 propagates the chosen attention implementation through every
subconfiguration, including `config.encoder.text_config`, and
`AutoModel` can load `T5Gemma2Encoder`.

### Dataclass configurations (5.4.0)

`PreTrainedConfig` and model config classes are dataclasses and reject
positional arguments. Pass every configuration value by keyword.

### Explicit model selection (5.5.0)

`AutoConfig.from_pretrained` accepts an explicit `model_type` override. A
registered configuration is preferred over remote code when available.

### Heterogeneous layer configuration (5.15.1)

Models can declare per-layer configuration. Gemma 4 uses
`per_layer_config` for mixed attention. Preserve this structure in custom
configuration and checkpoint conversion code instead of collapsing it into a
single global attention configuration.

## Custom integration migrations

### Attention and rotary interfaces

Custom attention implementations must adopt the new library-wide attention
mask interface introduced in 5.2.0. ModernBERT no longer chooses Flash
Attention by default, so integrations must not depend on the former implicit
backend.

As of 5.6.0, attention implementations must call the rotary function directly;
the formerly hidden kernel function is no longer registered as
`self.rotary_fn(...)`.

### Input and generation contracts

Inputs use the plural `inputs_embeds` as of 5.2.0; rename integrations that use
`input_embeds`.

Generation no longer uses `cache_position` to prepare inputs as of 5.3.0 and
always supplies full `input_ids` to `prepare_inputs_for_generation`. Custom
overrides must stop using `cache_position` for input slicing. Most major direct
`forward` methods also stop accepting `cache_position` in 5.4.0 because
`generate` manages cache positions.

### Standardized modeling internals (5.15.1)

Custom integrations that depend on internal layer declarations, mask or cache
construction, hybrid-attention handling, or legacy linear-layer type names must
migrate to standardized modeling internals. Private multimodal processor
helpers including `_is_url` and `_build_image_tokens` are removed.

GPTNeoX checkpoint handling remaps `embed_out` to `lm_head`; update code tied
to the old key. GPTBigCode now declares
`_supports_attention_backend = True`, which can alter backend dispatch in
downstream runtimes.

## Smaller renamed or changed APIs

- `plot_keypoint_matching` is deprecated in favor of
  `visualize_keypoint_matching` (4.55.0).
- `BeitConfig.segmentation_indices` migrates to `out_indices`, and
  `BeitImageProcessorFast.reduce_label` returns `labels` rather than `label`
  (5.1.0).
- Formerly hardcoded `time_step` settings for Bamba, FalconH1, and
  GraniteMoeHybrid are configurable (5.1.0).
- Ernie 4.5 VL MoE class and config names follow vLLM and SGLang conventions;
  replace old names (5.3.0).
- The v5 pipeline cleanup removes or changes `question-answering`,
  `visual-question-answering`, and `image-to-image`; migrate callers to the
  replacement pipelines or current task names (5.3.0).
