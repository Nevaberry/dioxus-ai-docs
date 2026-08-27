# Tokenizers, processors, and multimodal inputs

## Tokenizer backend and call migration

### Unified backends and blank construction (5.0.0)

Each tokenizer now uses one of `TokenizersBackend`, `SentencePieceBackend`,
`PythonBackend`, or `MistralCommonBackend`; `AutoTokenizer.from_pretrained()`
selects it. `PythonBackend` replaces the old `PreTrainedTokenizer` role for
custom Python tokenizers, while `PreTrainedTokenizerBase` is the minimal
backend-independent API.

Tokenizers backed by `tokenizers` can be created empty for training or from
`vocab` and `merges`. Their constructor does not accept `vocab_file`; use
`from_pretrained` for file-based loading.

```python
blank = LlamaTokenizer()
tokenizer = LlamaTokenizer(vocab=vocab, merges=merges)
```

### Calls, decoding, and chat-template returns (5.0.0)

Call a tokenizer directly instead of using deprecated `encode_plus`. `decode`
accepts single and batched inputs, so `batch_decode` is not required.
`apply_chat_template` returns a `BatchEncoding`; select `input_ids` or another
field instead of treating its result as a tensor or token-ID list.

```python
chat = tokenizer.apply_chat_template(messages, return_tensors="pt")
input_ids = chat["input_ids"]
```

### Target encoding and subclass contracts (5.0.0)

`sanitize_special_tokens()` and target-mode helpers such as
`as_target_tokenizer()` were removed. Use `text_target`; treat
`prepare_seq2seq_batch()` as deprecated and replace `BatchEncoding.words()`
with `word_ids()`.

```python
model_inputs = tokenizer(source_texts, text_target=target_texts)
model_inputs["labels"] = model_inputs.pop("input_ids_target")
```

Custom tokenizer subclasses must implement
`create_token_type_ids_from_sequences`, `prepare_for_model`,
`build_inputs_with_special_tokens`, and `truncate_sequences`, or inherit the
behavior through `PythonBackend`; the base implementations are gone.

### Serialization and special-token layout (5.0.0)

New saves put named special tokens in `tokenizer_config.json` and added tokens
in `tokenizer.json`. Older `special_tokens_map.json` and `added_tokens.json` are
still read but no longer written. `special_tokens_map` contains named
attributes only; put extra tokens in `extra_special_tokens`.
`additional_special_tokens` is converted for compatibility, and extended
special-token accessors were removed.

### Type inference and selection (5.2.0, 5.7.0, 5.8.0)

`AutoTokenizer` no longer infers a type from substrings such as `bert` in a
directory name when configuration lacks `model_type`; old repositories must
declare it. A later class-selection change that chose the wrong tokenizer for
models such as DeepSeek R1 was reverted. Automatic DeepSeek OCR loading now
selects its intended tokenizer class.

### Tokenizer cleanup behavior (5.4.0, 5.7.0)

Llama 3 conversion sets `clean_up_tokenization_spaces=False`.
`PreTrainedTokenizerFast` skips `clean_up_tokenization` for BPE tokenizers.

## Reproducibility and tokenizer-aware training

### Whole-word masking (4.51.0)

`DataCollatorForWholeWordMask` accepts a seed, making random masking
reproducible.

### Training-time special tokens (4.56.0)

`Trainer` aligns special-token settings in the model configuration with the
tokenizer at training time.

### Model-specific preprocessing defaults (5.1.0)

`Siglip2Tokenizer` enforces the text preprocessing used during training.
`BeitConfig.segmentation_indices` migrated to `out_indices`, and
`BeitImageProcessorFast.reduce_label` returns `labels`, not `label`.

## Processor architecture

### Fast processors (4.52.1, 4.55.0)

Most vision and vision-language families can use torch/torchvision functional
fast image processors on CPU or CUDA. Fast implementations expanded to
SuperPoint, SegFormer, Janus, DeepSeek-VL, and DeepSeek-VL Hybrid in 4.55.0.

### Separate video processors and templates (4.52.1)

Video processors are separate classes. Saving and loading multiple raw chat
template files is supported. `Dinov2ForImageClassification` correctly handles
checkpoints with register tokens.

### Unified image-processor backend (5.4.0)

The split between `BaseImageProcessor` and `BaseImageProcessorFast` was
replaced by one backend architecture. `image_processing_utils_fast` was
removed; import from `image_processing_utils` and update custom processors.

### PIL-only and CUDA interpolation behavior (5.5.0, 5.15.1)

PIL-backed processors can run without `torchvision`. On CUDA, requested Lanczos
interpolation falls back to bicubic, so accelerator output can differ from CPU
Lanczos preprocessing.

## Chat, embedding, and multimodal input contracts

### Audio and video chat inputs (4.51.0, 4.55.0)

Chat templates can load audio from video input. `apply_chat_template` accepts
in-memory videos as well as paths and URLs.

### OpenAI-style image entries (5.2.0)

`apply_chat_template` accepts content entries using the `image_url` form.

### Custom field prefilling (5.9.0)

Chat templates can prefill custom fields such as `reasoning_content` and
`thinking`.

### Standard plural embedding argument (5.2.0)

Model inputs use `inputs_embeds`; rename integrations that pass the singular
`input_embeds`.

```python
outputs = model(inputs_embeds=embeddings)
```

### Multimodal position IDs (5.3.0)

Vision-language models use a shared Qwen2-VL-derived interface for 3D position
IDs. Update custom processors and manual position-ID code for affected models,
including Ernie and GLM4V.

### Token types and nested language embeddings (5.4.0, 5.9.0)

Multimodal inputs may supply `mm_token_type` as non-padded lists. Generic
`get_input_embeddings` and `set_input_embeddings` now find a multimodal
model's nested `language_model` component.

### SAM3-family text embeddings (5.9.0)

`text_embeds` for SAM3, EdgeTAM, and SAM3-Lite-Text means full text embeddings,
not pooler output. Update callers that pass pooled representations.

### Private helper removal (5.15.1)

Do not call private multimodal processor helpers such as `_is_url` or
`_build_image_tokens`; they were removed. Use public processor and chat-template
inputs.

## Image, video, and audio behavior

### Pipeline post-processing and speech dithering (4.50.0)

The `image-text-to-text` pipeline accepts post-processing keyword arguments.
`Speech2TextFeatureExtractor` exposes dithering.

### Gemma 3n image prompt (4.53.0)

The `image-text-to-text` pipeline can pair an image URL with text containing
`<image_soft_token>` for Gemma 3n.

### Video and batch correctness (4.56.0, 4.57.0)

PerceptionLM receives video and correctly preprocesses non-tiled images. Fixes
also cover Fuyu image inference, Qwen-VL video beam search, LLaVA-OneVision
batch inference, and tensor devices in Idefics2, Idefics3, and SmolVLM.
Image-text inference supports batches larger than one, and
`ProcessorMixin.apply_chat_template` correctly loads PIL images.

`WhisperFeatureExtractor` keeps `input_features` and `attention_mask` lengths
consistent, and fast `center_crop` matches the slow path.

### Model-specific processor changes (5.1.0)

Janus resizing rounds dimensions instead of truncating them, so small numeric
differences are expected. LLaVA-OneVision accepts `image_sizes`, GLM-Image can
batch more than one image, `Sam3VideoModel` can disable its progress bar, and
`make_batched_video` handles five-dimensional arrays. `CLIPOutput` includes
attentions, and Flash Attention utilities accept one-dimensional `position_ids`.

### Gemma 4 fixed-budget preprocessing (5.5.0)

The processor preserves aspect ratio and targets 70, 140, 280, 560, or 1,120
soft tokens per image; 280 is the default. Pixels must fit the selected patch
budget, and processed height and width must both be divisible by 48. Do not
apply ImageNet mean/std normalization: patch embedding performs final scaling
to `[-1, 1]` internally.

### Result-affecting vision correction (5.6.0)

Qwen2.5-VL no longer applies temporal RoPE scaling to still images. Re-baseline
affected outputs after upgrading.
