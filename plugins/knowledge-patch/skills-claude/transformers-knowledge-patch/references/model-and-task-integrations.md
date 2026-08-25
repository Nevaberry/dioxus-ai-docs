# Model and task integrations

Use this reference to identify native architectures, modalities, task heads,
and model-specific input constraints. Loading and runtime details live in the
other topic references.

## Language, reasoning, and embedding models

### Gemma, Qwen, Llama, and Phi families (4.50.0, 4.51.0)

Gemma 3, ShieldGemma 2, and Mistral 3.1 arrived with Aya Vision, SmolVLM2,
SigLIP2, and Prompt Depth Anything in 4.50.0. Aya Vision handles image/text in
23 languages; Mistral 3.1 adds vision and 128K context; SmolVLM2 handles
multi-image and video input; SigLIP2 NaFlex preserves variable aspect ratios and
resolutions; ShieldGemma 2 classifies image-safety categories; Prompt Depth
Anything uses an iPhone LiDAR prompt to produce metric depth.

Llama 4 Maverick and Scout load through `Llama4ForConditionalGeneration` and
accept text and images; the documented setup installs `transformers[hf_xet]`.
Phi-4 Multimodal accepts text, image, and audio, emits text, and supports a 128K
context. Qwen3 and Qwen3MoE architecture code shipped before weights, and the
DeepSeek-V3 contribution was still work in progress in 4.51.0.

### Additional 4.x language architectures (4.53.0, 4.54.0)

Arcee, MiniMax-Text-01, T5Gemma, GLM-4.1V, Falcon H1, dots.llm1, and SmolLM3
are native in 4.53.0. T5Gemma is the encoder-decoder Gemma family;
MiniMax-Text-01 supports inference contexts up to four million tokens; GLM-4.1V
architecture support initially preceded checkpoints.

Ernie 4.5's dense 0.3B text model, LFM2, DeepSeek V2, ModernBERT Decoder, Doge,
xLSTM, and EXAONE 4.0 arrived in 4.54.0. ModernBERT Decoder is causal with
sequences to 8192 tokens. EXAONE 4.0 has reasoning/non-reasoning modes, tools,
and English/Korean/Spanish support. LFM2's 350M, 700M, and 1.2B variants target
CPU, GPU, and NPU edge use.

### GPT-OSS and later 4.x families (4.55.0, 4.56.0, 4.57.0)

GPT-OSS includes native 20B and 120B MoE reasoning checkpoints with MXFP4
weights. Ovis2, HunYuan, Seed-OSS, and GLM-4.5V followed in 4.56.0.

Qwen3-Next, VaultGemma, LongCat-Flash, FlexOlmo, BLT, OLMO3, and Ministral are
supported in 4.57.0. Qwen3-Next is a hybrid Gated DeltaNet/attention model with
an 80B-A3B checkpoint. VaultGemma is a 1B differentially private research model
with a 1024-token sequence length. LongCat-Flash targets 128K reasoning and tool
use. FlexOlmo domain experts can be included or excluded at inference. BLT uses
UTF-8 bytes without a fixed vocabulary and dynamically creates patches.

### Early 5.x language and encoder integrations (5.1.0, 5.2.0, 5.3.0)

K-EXAONE uses EXAONE-MoE, and Youtu-LLM is a 1.96B model with 128K context and a
`use_deterministic` option. GLM-5 uses `GlmMoeDsa` and DeepSeek Sparse
Attention. Qwen3.5 and Qwen3.5 MoE are native; the first checkpoint is a 397B
total/17B active vision-language model with hybrid Gated Delta Networks and
sparse MoE. Ernie 4.5 VL MoE is also supported, with class and config names
renamed in 5.3.0 to match vLLM and SGLang conventions.

EuroBERT is a bidirectional Llama-like multilingual encoder with an 8192-token
length. OLMo Hybrid interleaves full attention and Gated DeltaNet while caching
both KV and recurrent state. Nemotron 3 is native, and Qwen3.5 has a
sequence-classification head.

### Embeddings, Mamba, and Gemma 4 (5.4.0, 5.5.0)

Jina Embeddings v3 provides multilingual task-specific embeddings, five built-in
LoRA adapters, and sequences to 8192 tokens. NomicBERT is a native dense
embedding model for search, clustering, and classification with an 8192-token
context; prefix inputs with task-specific instructions.

Gemma 4 has pretrained and instruction variants at 1B, 13B, and 27B. Mamba-only
and Mamba/attention hybrids use native cache classes. `AutoConfig` can select an
explicit `model_type` and prefers registered native configurations.

### Recent language and hybrid architectures (5.6.0, 5.7.0, 5.8.0, 5.9.0)

OLMo gains sequence-classification heads, Nemotron-H supports MLP mixers, and
Qwen Thinker base checkpoints load without a generative head. Laguna XS.2 has
per-layer query-head counts with a common KV shape and a sigmoid router that
combines elementwise scores with learned expert bias. SonicMoe is supported.

`DeepSeek-V4-Flash`, `DeepSeek-V4-Pro`, and their Base variants replace
Multi-head Latent Attention with hybrid local/long-range attention, replace residuals with
Manifold-Constrained Hyper-Connections, and use a static token-to-expert hash in
their first MoE layers. EXAONE 4.5 is a 33B vision-language model with a 1.2B
visual encoder, 153,600-token vocabulary, contexts to 256K, Multi-Token
Prediction, and open weights.

Cohere2Moe supports Command A+, combining sliding-window and full-attention
layers with shared/routed experts and a very large context; its tensor-parallel
plan was corrected in 5.9.0. HRM-Text is a base model without instruction tuning
or chat templates. It uses slow planning and fast computation recurrences,
PrefixLM attention, per-head sigmoid gates, and parameterless RMSNorm.

### Long-context and hybrid families (5.15.1)

DeepSeek-V3.2 adds DeepSeek Sparse Attention. MiMo-V2-Flash has a 256K extended
context with reduced KV storage. ZAYA1 uses compressed convolutional attention
and a nonlinear MoE router. MiniCPM3 combines Multi-head Latent Attention, dense
SwiGLU, and explicit residual scaling.

GraniteSWA, GraniteMoeSWA, A.X-K1, A.X-K2, Cosmos3, Cosmos3 Edge, TIPSv2, and
TIPSv2 DPT are also supported architectures.

## Multimodal and vision-language models

### Omni, moderation, and image generation (4.52.1)

Qwen2.5-Omni, SAM-HQ, GraniteMoeHybrid, D-FINE, CSM, BitNet, Llama Guard 4,
TimesFM, MLCD, Janus/Janus-Pro, and InternVL3 expand multimodal streaming text
and speech, high-quality promptable segmentation, detection, contextual TTS,
moderation, forecasting, and image generation.

Qwen2.5-Omni accepts text, image, audio, and video and streams text and speech.
Janus accepts image/text and generates text or images, but callers choose one
output mode rather than interleaving them. SAM-HQ fine-tuning was not yet
supported in this batch.

### Gemma 3n, Command A Vision, and Qwen3-VL (4.53.0, 4.55.0, 4.57.0)

Gemma 3n accepts text, image, video, and audio and emits text. Command A Vision
uses Cohere2 Vision for captioning, visual QA, and document/chart understanding.
Qwen3-VL has dense and MoE Instruct and Thinking variants; Qwen3 Omni MoE adds
unified multimodal generation.

LFM2-VL accepts text and variable-resolution images. It preserves native
resolution through 512×512, splits larger images into 512×512 patches without
forced upscaling or distortion, and gives the 1.6B variant a global thumbnail.

### Mistral 4 and robotics (5.4.0)

Mistral 4 unifies instruction and reasoning with text/image input and a 256K
context. PI0 generates robot actions from visual observations and language
instructions.

### Privacy, OCR, and segmentation models (5.6.0)

OpenAI Privacy Filter performs on-premises bidirectional token classification
for PII detection and masking in one pass, producing token probabilities across
eight privacy categories and coherent spans. Qianfan-OCR is a 4B image-to-text
document model for structured parsing, tables, charts, QA, and key information;
Layout-as-Thought emits a layout representation before the final result.

SAM3-LiteText combines SAM3's ViT-H encoder with a distilled MobileCLIP-based
text encoder. SLANet and SLANet_plus are lightweight CPU-oriented table
structure recognizers for documents and natural scenes.

### Gemma 4 Assistant and document VLMs (5.8.0)

Gemma 4 Assistant is a small text-only Multi-Token Prediction draft model that
reuses the target KV cache and cross-attends to target context. Granite 4.1
Vision combines SigLIP2 with Window Q-Former projectors and injects visual
features at eight language-model locations for chart, table, and semantic
key-value extraction.

### Muse, Inkling, Kimi, and MiniMax (5.15.1)

Muse Glimmer is a dense 30B local-agentic multimodal model with a 2B ViT-style
Perception Encoder and 28B text decoder under Apache 2.0. Inkling is 975B total
and 41B active; it accepts text, image, and audio and generates text for
multilingual, coding, tool, and conversational tasks.

Kimi K2.5 architecture support covers K2.5 through K2.7 for native multimodal
agentic and coding use. MiniMax-M3-VL combines a CLIP-style tower, 3D rotary
positions, the MiniMax-M3 backbone, mixed dense/sparse MoE decoding, and
block-sparse attention.

## Vision, video, document, and spatial tasks

### Retrieval, matching, and world models (4.53.0, 4.54.0)

V-JEPA 2 provides a video encoder and action-conditioned world model. ColQwen2
turns document-page images into multi-vector embeddings for late-interaction
retrieval. LightGlue matches local features between image pairs and can pair
with SuperPoint for pose or homography estimation.

EoMT supports pipeline image segmentation; AIMv2 supplies vision encoders;
PerceptionLM handles image/video understanding; EfficientLoFTR estimates image
correspondences and pose/homography; DeepSeek VL accepts image/text and emits
text.

### Grounding, dense features, segmentation, and OCR (4.55.0, 4.56.0)

MM Grounding DINO supports zero-shot grounding/detection with its original and
LLMDet checkpoints. DINOv3 supplies dense visual features; MetaCLIP 2 provides
multilingual image-text representations; Florence-2 handles prompted captioning,
detection, and segmentation; SAM 2 supports point/box-prompted image and video
segmentation; Kosmos-2.5 provides spatially grounded OCR and image-to-Markdown.

### Video segmentation and visual documents (4.57.0, 5.1.0, 5.3.0)

EdgeTAM targets mobile real-time video segmentation. PP-DocLayoutV3 predicts
instance-segmented layout and reading order, and can feed regions to GLM-OCR in
a two-stage parallel recognition pipeline.

PP-DocLayoutV2 combines RT-DETR element detection/classification with
pointer-network reading order. ModernVBert pairs ModernBERT and SigLIP for
visual-document understanding/retrieval; ColModernVBert emits ColPali-style
multi-vector document-image embeddings.

### Document rectification, OCR, earth observation, and video (5.4.0)

VidEoMT performs online video segmentation. UVDoc rectifies one or batches of
document images. SLANeXt recognizes table structure. PP-OCRv5 has mobile/server
detectors and recognizers for multilingual document and scene text. PPLCNet
adds document orientation, table, and text-line orientation classifiers;
PPLCNetV3 is a CPU-oriented backbone. CHMv2 estimates forest-canopy height from
high-resolution optical satellite imagery.

### Object detection and formula recognition (5.7.0, 5.8.0)

DEIMv2 provides real-time detection in eight sizes from X to Atto. Large models
adapt single-scale DINOv3 features into multiple scales with a Spatial Tuning
Adapter; small models use pruned HGNetv2 backbones. PP-FormulaNet-L and
PP-FormulaNet_plus-L recognize formulas and table structures in documents and
natural scenes.

### Video encoders and OCR deployment (5.15.1)

VideoPrism is a frozen general-purpose video encoder. RADIO produces global
image embeddings and dense spatial features at variable resolutions. PP-OCRv6
provides official medium, small, and tiny detection/recognition weights for
server through edge deployment.

## Speech, audio, and music

### Dialogue TTS and streaming recognition (4.53.0)

Dia performs dialogue-oriented TTS with nonverbal cues and audio conditioning.
Kyutai STT uses a streaming codec; `kyutai/stt-1b-en_fr` is bilingual and
`kyutai/stt-2.6b-en` is English-only.

### Voxtral and X-Codec (4.54.0, 4.56.0)

Voxtral adds audio to Ministral for transcription, translation, Q&A,
summarization, and voice-driven function calls. The
`mistralai/Voxtral-Mini-3B-2507` and
`mistralai/Voxtral-Small-24B-2507` checkpoints have 32K context and handle up
to 30 minutes for transcription or 40 minutes for broader understanding.

X-Codec adds semantic-aware audio tokenization, music continuation, and
text-to-sound synthesis.

### Parakeet, realtime ASR, and acoustic tokenization (4.57.0, 5.2.0)

`ParakeetForCTC` adds CTC speech recognition. VoxtralRealtime consumes arriving
chunks for low-latency incremental ASR. VibeVoice Acoustic Tokenizer supports
the continuous tokens used by long-form multi-speaker synthesis.

### VibeVoice, Higgs, and VITS (5.3.0)

VibeVoice ASR processes up to 60 minutes of 24 kHz audio with hotwords,
transcription, diarization, timestamps, 50+ languages, and code switching.
Higgs Audio V2 provides single/multi-speaker generation and zero-shot cloning;
its separate 24 kHz tokenizer represents speech, music, and sound at 25 fps
without diffusion. VITS accepts `speaking_rate` in `forward`.

### Music Flamingo and Granite Speech Plus (5.5.0, 5.8.0)

Music Flamingo reasons over speech, sound, and music for sequences up to 20
minutes. Granite Speech Plus provides prompted transcription with speaker labels
and word timestamps; its projector concatenates final encoder state with a
configurable subset of intermediate states.

### Parakeet TDT and AudioFlamingoNext (5.9.0)

Parakeet TDT is distinct from the existing CTC integration.
AudioFlamingoNext checkpoints are supported.

### Streaming and aligned ASR (5.15.1)

Nemotron 3.5 ASR supports multilingual cached streaming and batch transcription
with 80, 160, 560, or 1,120 ms chunks; Nemotron ASR Streaming is English-only.
Qwen3 ASR detects language, transcribes multiple languages, and force-aligns an
existing transcript for timestamps. `ParakeetForRNNT` supplies greedy RNN-T
decoding over a Fast Conformer encoder.

## Forecasting, scientific, and generative tasks

### Time series and proteins (4.52.1, 4.53.0, 4.54.0)

TimesFM supports time-series forecasting, and
`AutoModelForTimeSeriesPrediction` is directly importable. EVOLLA generates
protein language over sequences, structures, and user queries.

### TimesFM 2.5 (5.3.0)

TimesFM 2.5 is a decoder-only zero-shot forecaster with continuous quantile
prediction.

### DiffusionGemma (5.15.1)

DiffusionGemma generates text by iteratively denoising token blocks with
multi-canvas sampling rather than strict left-to-right decoding. The integration
is trainable.

## Task-head and execution additions

### Additional heads and loading paths (4.51.0, 4.57.0, 5.1.0)

ModernBERT has a question-answering module, and Distill Any Depth is integrated.
DeepSeek V3 adds `DeepseekV3ForTokenClassification`.
`AutoModel` can load `T5Gemma2Encoder`. Moonshine supports streaming, EoMT can
use a DINOv3 backbone, GLM-Image handles batch sizes greater than one, and
LLaVA-OneVision accepts `image_sizes`.

### Audio and hardware runtime compatibility (5.6.0)

Audio models have vLLM compatibility, and Neuron devices participate in
automatic compilation.
