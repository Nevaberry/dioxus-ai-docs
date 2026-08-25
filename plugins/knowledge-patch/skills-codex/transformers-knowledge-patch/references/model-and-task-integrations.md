# Model and task integrations

Use this catalog to identify native architecture, modality, task, and important
checkpoint capabilities. Entries are grouped by developer task rather than by
release.

## Language and reasoning models

### Dense, MoE, and hybrid decoders

- **Gemma 3** (4.50.0) joins the library alongside the image-safety
  **ShieldGemma 2** integration.
- **Qwen3** and **Qwen3MoE** architectures ship in 4.51.0 before their model
  weights. The **DeepSeek-V3** contribution is still marked work in progress in
  that release.
- **GraniteMoeHybrid** and low-bit **BitNet** arrive in 4.52.1.
- **Arcee**, **MiniMax-Text-01**, **T5Gemma**, **Falcon H1**, **dots.llm1**, and
  **SmolLM3** arrive in 4.53.0. T5Gemma is an encoder-decoder Gemma family;
  MiniMax-Text-01 supports inference contexts up to four million tokens.
- **Ernie 4.5** dense 0.3B, **LFM2**, **DeepSeek V2**, **ModernBERT Decoder**,
  **Doge**, **xLSTM**, and **EXAONE 4.0** arrive in 4.54.0. ModernBERT Decoder
  handles up to 8,192 tokens. EXAONE 4.0 supports reasoning and non-reasoning
  modes, tools, and English, Korean, and Spanish. LFM2 provides 350M, 700M, and
  1.2B variants aimed at edge CPU, GPU, and NPU use.
- Native **GPT-OSS 20B and 120B** loading arrives in 4.55.0, including MXFP4
  mixture-of-experts weights and a default tensor-parallel plan for 120B.
- **Ovis2**, **HunYuan**, **Seed-OSS**, and **GLM-4.5V** are integrated in
  4.56.0.
- **Qwen3-Next**, **VaultGemma**, **LongCat-Flash**, **FlexOlmo**, **BLT**,
  **OLMO3**, and **Ministral** arrive in 4.57.0. Qwen3-Next combines Gated
  DeltaNet and attention in an 80B-A3B checkpoint. VaultGemma is a 1B
  differentially private research checkpoint limited to 1,024 tokens.
  LongCat-Flash has 128K context, reasoning, and tool use. FlexOlmo domain
  experts can be included or excluded at inference. BLT tokenizes UTF-8 bytes
  with dynamic patching rather than using a fixed vocabulary.
- **K-EXAONE** through EXAONE-MoE and the 1.96B **Youtu-LLM** with 128K context
  arrive in 5.1.0. Youtu-LLM exposes `use_deterministic` for consistent
  execution.
- **GLM-5** through `GlmMoeDsa`, including DeepSeek Sparse Attention, plus
  **Qwen3.5**, **Qwen3.5 MoE**, and **Ernie 4.5 VL MoE** arrive in 5.2.0. The
  first Qwen3.5 checkpoint is a 397B-total, 17B-active native vision-language
  architecture with hybrid Gated Delta Networks and sparse MoE layers.
- **OLMo Hybrid** (5.3.0) interleaves full attention with Gated DeltaNet and
  maintains both KV and recurrent cache state. **Nemotron 3** is supported, and
  Qwen3.5 gains sequence classification.
- **Gemma 4** (5.5.0) has pretrained and instruction variants at 1B, 13B, and
  27B parameters.
- **Laguna XS.2** (5.7.0) permits per-layer query-head counts while preserving
  one KV-cache shape; its sigmoid router uses element-wise scores plus learned
  per-expert bias. **SonicMoe** also becomes a supported architecture.
- **DeepSeek-V4-Flash**, **DeepSeek-V4-Pro**, and Base variants arrive in 5.8.0
  with hybrid local/long-range attention, Manifold-Constrained
  Hyper-Connections, and a static token-to-expert hash table in early MoE
  layers.
- **Cohere2Moe** supports **Command A+** in 5.9.0 with hybrid sliding/full
  attention, shared and routed experts, a very large context, and a corrected
  tensor-parallel plan. **HRM-Text** is a non-chat base autoregressive model
  with slow planning and fast computation stacks, PrefixLM attention, per-head
  sigmoid gates, and parameterless RMSNorm.
- **Inkling** (5.15.1) is a 975B-total, 41B-active general-purpose multimodal
  architecture for multilingual, coding, tool-use, and conversation.
  **DeepSeek-V3.2** adds DeepSeek Sparse Attention; **MiMo-V2-Flash** provides a
  256K extended context with reduced KV storage; **ZAYA1** uses compressed
  convolutional attention and a nonlinear MoE router; **MiniCPM3** combines
  Multi-head Latent Attention, dense SwiGLU, and explicit residual scaling.
- **GraniteSWA**, **GraniteMoeSWA**, **A.X-K1**, **A.X-K2**, **Cosmos3**,
  **Cosmos3 Edge**, **TIPSv2**, and **TIPSv2 DPT** are additional architectures
  supported in 5.15.1.

### Encoders, embeddings, and classifiers

- **ModernBERT** gains question answering in 4.51.0.
- **EuroBERT** (5.3.0) is a bidirectional Llama-like multilingual encoder with
  an 8,192-token sequence length.
- **Jina Embeddings v3** (5.4.0) provides multilingual, task-specific
  embeddings, five built-in LoRA adapters, and sequences up to 8,192 tokens.
- **NomicBERT** (5.5.0) is a native dense embedding model with an 8,192-token
  context for search, clustering, and classification. Prefix inputs with the
  appropriate task instruction.
- **OpenAI Privacy Filter** (5.6.0) provides bidirectional on-premises token
  classification for PII detection and masking, producing per-token
  probabilities across eight categories and coherent decoded spans in one
  forward pass.
- OLMo-family sequence-classification heads and Nemotron-H MLP mixers arrive in
  5.6.0. Qwen Thinker base checkpoints can load without a generative head.

## Multimodal language and agentic models

### Image, video, audio, and text inputs

- **Aya Vision** (4.50.0) accepts images and text across 23 languages.
  **Mistral 3.1** adds vision and a 128K context. **SmolVLM2** accepts
  multi-image and video input. **SigLIP2 NaFlex** preserves variable aspect
  ratios and resolutions.
- **Llama 4 Maverick and Scout** use `Llama4ForConditionalGeneration` in
  4.51.0 and accept text and images. The documented setup installs
  `transformers[hf_xet]`. **Phi-4 Multimodal** accepts text, images, and audio,
  emits text, and supports 128K context.
- **Qwen2.5-Omni** (4.52.1) accepts text, images, audio, and video and streams
  text and speech. **Janus** and **Janus-Pro** accept image and text and emit
  text or images; select one output mode because interleaved image/text output
  is unsupported. **InternVL3** also joins the multimodal integrations.
- **Gemma 3n** (4.53.0) accepts text, image, video, and audio and emits text.
  **GLM-4.1V** architecture code ships before any matching checkpoint.
- **Voxtral** (4.54.0) adds audio input to Ministral-based language models for
  transcription, translation, Q&A, summarization, and voice-driven function
  calling. Mini 3B and Small 24B checkpoints have 32K context and support up to
  30 minutes of transcription or 40 minutes of broader audio understanding.
  **DeepSeek VL** accepts images and text and emits text.
- **Command A Vision** (4.55.0) supports captioning, visual question answering,
  and document/chart understanding.
- **Qwen3-VL** (4.57.0) includes dense and MoE Instruct and Thinking variants.
  **LFM2-VL** accepts text and variable-resolution images; it preserves native
  resolution through 512×512, patches larger inputs, and gives its 1.6B variant
  a global thumbnail. **Qwen3 Omni MoE** provides unified multimodal generation.
- **Mistral 4** (5.4.0) unifies instruction and reasoning modes with text and
  image input and a 256K context.
- **Muse Glimmer** (5.15.1) combines a 2B ViT-style perception encoder with a
  28B text decoder for local agentic multimodal applications and ships under
  Apache 2.0. **Inkling** accepts text, images, and audio and produces text.
  The **Kimi K2.5**
  architecture used by K2.5 through K2.7 supports native multimodal agentic and
  coding tasks. **MiniMax-M3-VL** combines a CLIP-style tower and 3D rotary
  positions with a mixed dense/sparse MoE text decoder and block-sparse
  attention.

### Safety and moderation

- **ShieldGemma 2** classifies image-safety categories (4.50.0).
- **Llama Guard 4** provides multimodal moderation (4.52.1).

## Vision, video, and geometry

### Detection and segmentation

- **SAM-HQ** adds promptable high-quality segmentation in 4.52.1; fine-tuning
  is not supported in that release. **D-FINE** provides object detection.
- **EoMT** provides pipeline-compatible image segmentation (4.54.0) and can
  use a DINOv3 backbone as of 5.1.0.
- **MM Grounding DINO** (4.55.0) supports zero-shot grounding and detection
  with its original checkpoints and LLMDet checkpoints.
- **Florence-2** (4.56.0) supports prompted captioning, detection, and
  segmentation. **SAM 2** provides point- or box-prompted image and video
  segmentation.
- **EdgeTAM** (4.57.0) targets mobile real-time video segmentation.
- **VidEoMT** (5.4.0) provides online video segmentation.
- **SAM3-LiteText** (5.6.0) combines SAM3's ViT-H encoder with a compact
  distilled MobileCLIP text encoder for lightweight vision-language
  segmentation.
- **DEIMv2** (5.7.0) supplies eight real-time detector sizes from X through
  Atto. Larger variants adapt single-scale DINOv3 features with a Spatial
  Tuning Adapter; the smallest use pruned HGNetv2 backbones.

### Visual representation, matching, and depth

- **Prompt Depth Anything** (4.50.0) produces metric depth maps from an iPhone
  LiDAR prompt. **Distill Any Depth** is added in 4.51.0.
- **V-JEPA 2** (4.53.0) adds a video encoder and action-conditioned world
  model. **LightGlue** matches local features between image pairs and can pair
  with SuperPoint for pose or homography estimation.
- **AIMv2** vision encoders, **PerceptionLM** image/video understanding, and
  **EfficientLoFTR** correspondence and pose/homography estimation arrive in
  4.54.0.
- **DINOv3** dense visual features and **MetaCLIP 2** multilingual image-text
  representation arrive in 4.56.0.
- **VideoPrism** (5.15.1) is a frozen general-purpose video encoder. **RADIO**
  emits both image-level embeddings and dense spatial features at variable
  input resolutions.

## Documents, OCR, and visual retrieval

### Layout, OCR, and formula recognition

- **ColQwen2** (4.53.0) treats document pages as images and produces
  multi-vector embeddings for late-interaction retrieval.
- **Kosmos-2.5** (4.56.0) performs spatially grounded OCR and
  image-to-Markdown conversion.
- **PP-DocLayoutV3** and **GLM-OCR** (5.1.0) can form a two-stage document
  pipeline: instance-segmented layout and reading-order analysis, followed by
  parallel recognition.
- **PP-DocLayoutV2** (5.3.0) combines RT-DETR element detection/classification
  with pointer-network reading order. **ModernVBert** pairs ModernBERT and
  SigLIP for visual-document understanding and retrieval;
  **ColModernVBert** emits ColPali-style multi-vector document embeddings.
- **UVDoc** (5.4.0) rectifies single images or batches. **SLANeXt** recognizes
  table structure. **PP-OCRv5** mobile/server detectors and recognizers handle
  multilingual document and scene text. **PPLCNet** covers document
  orientation, tables, and text-line orientation; **PPLCNetV3** is a
  CPU-oriented vision backbone.
- **Qianfan-OCR** (5.6.0) is a 4B image-to-text document model for structured
  parsing, table extraction, chart understanding, document Q&A, and key-value
  extraction. Layout-as-Thought emits structured layout before the result.
  **SLANet** and **SLANet_plus** add lightweight CPU-oriented table structure
  recognition.
- **Granite 4.1 Vision** (5.8.0) handles document chart, table, and semantic
  key-value extraction using SigLIP2, Window Q-Former projectors, and eight
  visual-feature injection points. **PP-FormulaNet-L** and
  **PP-FormulaNet_plus-L** recognize mathematical formulas and table structures.
- **PP-OCRv6** (5.15.1) provides official medium, small, and tiny detection and
  recognition weights for server-to-edge deployment.

## Speech, audio, and music

### Recognition and transcription

- **Kyutai STT** (4.53.0) performs streaming-codec speech recognition through
  bilingual `kyutai/stt-1b-en_fr` and English-only `kyutai/stt-2.6b-en`.
- **ParakeetForCTC** arrives in 4.57.0. **Parakeet TDT** is a distinct Parakeet
  integration in 5.9.0.
- **Moonshine** gains streaming in 5.1.0.
- **VoxtralRealtime** (5.2.0) performs low-latency incremental ASR on arriving
  chunks rather than requiring a whole file.
- **VibeVoice ASR** (5.3.0) processes up to 60 minutes of 24 kHz audio with
  hotwords, transcription, diarization, timestamps, more than 50 languages,
  and code-switching.
- **Granite Speech Plus** (5.8.0) provides prompted speech-to-text with speaker
  annotations and word-level timestamps. Its projector combines the final
  speech-encoder state with configurable intermediate states.
- **Nemotron 3.5 ASR** (5.15.1) supports multilingual cached streaming and
  batch transcription with 80, 160, 560, or 1,120 ms chunks; Nemotron ASR
  Streaming is English-only. **Qwen3 ASR** adds automatic language detection,
  multilingual transcription, and forced alignment for timestamping an
  existing transcript. `ParakeetForRNNT` adds greedy RNN-T decoding over a Fast
  Conformer encoder.

### Speech, sound, and music generation

- **CSM** adds contextual text-to-speech in 4.52.1.
- **Dia** (4.53.0) provides dialogue-oriented text-to-speech with nonverbal
  cues and audio conditioning.
- **X-Codec** (4.56.0) provides semantic-aware audio tokenization, music
  continuation, and text-to-sound synthesis.
- **VibeVoice Acoustic Tokenizer** (5.2.0) supports the continuous tokenization
  design used by long-form, multi-speaker speech synthesis.
- **Higgs Audio V2** (5.3.0) supports single- and multi-speaker generation and
  zero-shot voice cloning. Its separate 24 kHz tokenizer encodes speech, music,
  and sound at 25 fps without diffusion.
- **Music Flamingo** (5.5.0) handles audio-language reasoning across speech,
  sound, and music for inputs up to 20 minutes.
- **AudioFlamingoNext** checkpoints are supported in 5.9.0.

## Time series, science, earth, and robotics

- **TimesFM** adds time-series forecasting in 4.52.1;
  `AutoModelForTimeSeriesPrediction` becomes directly importable in 4.53.0.
- **TimesFM 2.5** (5.3.0) is a decoder-only zero-shot forecaster with
  continuous quantile prediction.
- **EVOLLA** (4.54.0) generates protein language over sequences, structures,
  and user queries.
- **CHMv2** (5.4.0) estimates forest-canopy height from high-resolution optical
  satellite imagery.
- **PI0** (5.4.0) performs vision-language-action inference, generating robot
  actions from visual observations and instructions.

## Image generation and diffusion

- **MLCD** and **Janus/Janus-Pro** add image-generation-related task support in
  4.52.1; Janus callers select text or image output rather than interleaving.
- **GLM-Image** supports batch sizes greater than one as of 5.1.0.
- **DiffusionGemma** (5.15.1) generates text by iteratively denoising token
  blocks with multi-canvas sampling instead of strict left-to-right decoding;
  the integration is trainable.

## Model-specific execution switches

- `Sam3VideoModel` can disable its progress bar, and LLaVA-OneVision accepts
  `image_sizes` (5.1.0).
- VITS forward calls accept `speaking_rate`, for example
  `model(**inputs, speaking_rate=1.2)` (5.3.0).
- Gemma 4 Assistant (5.8.0) supplies Multi-Token Prediction speculative
  decoding; see the generation reference for cache reuse and verification.
- **EXAONE 4.5** (5.8.0) is a 33B vision-language model with a 1.2B visual
  encoder, 153,600-token vocabulary, contexts up to 256K, and Multi-Token
  Prediction.
