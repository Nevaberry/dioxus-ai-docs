# Multimodal processing and pipelines

Use this reference for image, video, audio, text, chat-template, processor, and
pipeline inputs and outputs.

## Pipeline defaults and arguments

### Image-text post-processing (4.50.0)

The `image-text-to-text` pipeline accepts post-processing keyword arguments.

### Pipeline dtype (4.53.0)

Pipeline `dtype` defaults to `auto`. Pass an explicit dtype when the application
requires a fixed representation.

### Image-text batching (4.57.0)

Image-text inference supports batch sizes greater than one, and DeepSeek V3
adds `DeepseekV3ForTokenClassification`.

### Gemma 3n image-text input (4.53.0)

The `image-text-to-text` pipeline accepts an image URL and a prompt containing
`<image_soft_token>` for Gemma 3n.

```python
from transformers import pipeline

pipe = pipeline("image-text-to-text", model="google/gemma-3n-e4b")
output = pipe(image_url, text="<image_soft_token> in this image, there is")
```

### Pipeline task cleanup (5.3.0)

The v5 cleanup removes or changes `question-answering`,
`visual-question-answering`, and `image-to-image`. Replace old task names with
their current pipeline or updated name.

## Chat templates and media content

### Audio, video, and image inputs

- Chat templates can load audio from video inputs as of 4.51.0.
- `apply_chat_template` accepts in-memory video objects, not only file paths and
  URLs, as of 4.55.0.
- PIL image inputs load correctly through `ProcessorMixin.apply_chat_template`
  as of 4.57.0.
- OpenAI-style `image_url` content entries are accepted by
  `apply_chat_template` as of 5.2.0.

### Saved templates and return types

Video processors become separate classes in 4.52.1, and processors can save
and load multiple raw chat-template files. In 5.0.0,
`apply_chat_template` returns a `BatchEncoding`; select fields such as
`input_ids` rather than treating the result as raw IDs or a tensor.

### Custom field prefilling (5.9.0)

`apply_chat_template` can prefill custom fields such as `reasoning_content` and
`thinking`.

### Serve tool inputs (5.6.0)

`transformers serve` forwards `tool_calls` and `tool_call_id` to processor
inputs and uses `parse_response` to interpret tool calls. It also accepts audio
and video request content.

## Image processor architecture

### Fast processors on CPU and CUDA

Most vision and vision-language architectures can use fast processors backed
by `torch` and `torchvision` functional transforms on both CPU and CUDA as of
4.52.1. Fast implementations are added for SuperPoint, SegFormer, Janus,
DeepSeek-VL, and DeepSeek-VL Hybrid in 4.55.0.

### Unified backend (5.4.0)

The separate `BaseImageProcessor` and `BaseImageProcessorFast` design is
replaced by one backend architecture. `image_processing_utils_fast` is removed;
custom processors and direct imports must use `image_processing_utils`.

### PIL-only processing (5.5.0)

PIL-backed processors no longer incorrectly require `torchvision`. A PIL-only
preprocessing path can run without that dependency.

### CUDA interpolation fallback (5.15.1)

Lanczos interpolation requests on CUDA fall back to bicubic. Accelerator output
can therefore differ from CPU Lanczos preprocessing.

## Model-specific image and video preprocessing

### Gemma 4 fixed-budget images (5.5.0)

Gemma 4 preserves aspect ratio while choosing one of 70, 140, 280, 560, or
1,120 soft tokens per image; 280 is the default. Total pixels must fit the
selected patch budget, and processed width and height must both be divisible by
48.

Do not apply standard ImageNet mean/std normalization. Gemma 4's patch embedding
performs final scaling to `[-1, 1]` internally.

### LFM2-VL resolution behavior (4.57.0)

LFM2-VL preserves native image sizes through 512×512 without forced upscaling
or aspect-ratio distortion. It splits larger images into 512×512 patches; the
1.6B variant receives a thumbnail for global context.

### Corrected multimodal processing

- `Dinov2ForImageClassification` handles register-token checkpoints correctly
  (4.52.1).
- PerceptionLM receives video and preprocesses non-tiled images correctly;
  Fuyu image inference and Qwen-VL video beam search are repaired (4.56.0).
- LLaVA-OneVision batch inference and tensor-device handling in Idefics2,
  Idefics3, and SmolVLM are corrected (4.56.0).
- Janus image resizing rounds dimensions rather than truncating them, causing
  small numerical differences (5.1.0).
- Qwen2.5-VL no longer applies temporal RoPE scaling incorrectly to still
  images, so outputs can change after upgrading (5.6.0).

### Multimodal token metadata

Callers can pass `mm_token_type` as non-padded lists as of 5.4.0. In 5.3.0,
vision-language architectures converge on a Qwen2-VL-derived interface for 3D
position IDs. Custom processors and manual position-ID construction for
architectures such as Ernie and GLM4V must migrate.

## Embeddings and model inputs

### Standardized embedding names (5.2.0)

Use the plural `inputs_embeds` rather than `input_embeds`.

```python
outputs = model(inputs_embeds=embeddings)
```

### Full text embeddings for SAM3 family (5.9.0)

The `text_embeds` input for SAM3, EdgeTAM, and SAM3-Lite-Text expects full text
embeddings rather than pooler output. Update callers that pass pooled
representations.

### Nested language model embeddings (5.9.0)

Generic `get_input_embeddings` and `set_input_embeddings` logic recognizes the
nested `language_model` component of multimodal architectures.

### Gemma 4 per-layer inputs (5.9.0)

Gemma 4 generation accepts `inputs_embeds` and `per_layer_inputs`, with the
latter exposed across every Gemma 4 variant.

## Audio and speech preprocessing

### Dithering (4.50.0)

`Speech2TextFeatureExtractor` exposes dithering in its public API.

### Whisper behavior

- Word timestamps interpret a timestamp token as the end of the token's time
  span as of 4.54.0.
- Transcription accepts a progress callback as of 4.55.0.
- `WhisperFeatureExtractor` keeps `input_features` and `attention_mask` lengths
  consistent as of 4.57.0.

### Batched video utility (5.1.0)

`make_batched_video` accepts five-dimensional arrays.

## Visualization and inspection

### Attention masks (4.50.0)

`AttentionMaskVisualizer` loads a tokenizer and model from an ID and displays
the resulting attention layout, including sliding-window and multimodal masks.

```python
from transformers.utils.attention_visualizer import AttentionMaskVisualizer

visualizer = AttentionMaskVisualizer("meta-llama/Llama-3.2-3B-Instruct")
visualizer("A normal attention mask")
```

### Keypoint matching (4.55.0)

`plot_keypoint_matching` is deprecated. Use the standardized
`visualize_keypoint_matching` helper.

## Output and preprocessing corrections

- Fast `center_crop` now matches the slow implementation (4.57.0).
- `CLIPOutput` includes attentions, and Flash Attention utilities accept
  one-dimensional `position_ids` (5.1.0).
- `BeitImageProcessorFast.reduce_label` returns `labels` rather than `label`,
  while `BeitConfig.segmentation_indices` migrates to `out_indices` (5.1.0).
- `Siglip2Tokenizer` enforces the preprocessing defaults used during training
  (5.1.0).
- Llama 3 tokenizer conversion sets `clean_up_tokenization_spaces=False`
  (5.4.0).
- `AutoProcessor.from_pretrained` forwards Hub keyword arguments instead of
  silently discarding them (5.4.0).
