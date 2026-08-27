# Models, Multimodal Processing, and LoRA

Use this reference for model-family support, pooling and task interfaces,
multimodal preprocessing and encoder control, Transformers-backed models, and
adapter loading.

## Model integration contracts

### Custom forward methods (`0.7-0.10`)

Custom model forward methods no longer receive `kv_cache` or `attn_metadata`;
attention backends obtain both through `forward_context`. During the V0
transition, model definitions could implement `SupportsV0Only` to declare the
old-engine requirement; V1 is now the only engine.

### Multimodal extension path (`0.7-0.10`)

A model that implements the merged multimodal processor and appropriate
`get_*_embeddings` methods is automatically supported in V1. The legacy input
mapper for out-of-tree multimodal models was deprecated. Vision-language
models can use the Transformers backend, including multimodal caching.

### Multiple tasks and poolers (`0.7-0.10`)

One model can advertise multiple tasks and poolers and select pooling
parameters dynamically. Integrations should not assume one fixed task/pooler.

### Independent multimodal encoder controls (`engine-and-openai-server`)

Processor caching has `--mm-processor-cache-type` and a shared-memory object
size cap. The encoder has separate tensor-parallel mode, attention backend,
and attention dtype controls. Encoder FP8 scales can be loaded or saved with a
configurable save margin. Multimodal tensor IPC has its own mode and GPU-memory
budget.

### Diffusion models (`0.23-0.26`)

DiffusionGemma supports CPU execution and structured-output guardrails for
diffusion decoders. Tensor parallelism and Hugging Face stability-window
semantics are also supported.

### Transformers audio (`0.27.1`)

Audio models can run through the Transformers modeling backend.

## LoRA and adapter paths

### V1, multi-platform, and local resolution (`0.7-0.10`)

Rank-Stabilized LoRA, V1 LoRA, and LoRA for `TransformersModel` are supported.
Multi-LoRA covers x86, TPU, and Neuron. A default local-directory resolver and
Tensorizer loading work with V1 and LoRA.

### Sharded and multimodal LoRA (`0.11-0.14`)

`--fully-sharded-loras` supports fused MoE. LoRA can target multimodal towers
and connectors for LLaVA, PaliGemma, DotsOCR, and GLM4-V. It also supports
DeepSeek-OCR, Qwen3-Next, PLaMo 2/3, vision-LoRA processor caching, and MoE
expert `base_layer` loading.

### Remote, quantized, and audio adapters (`0.15-0.18`)

A Hugging Face Hub resolver can load LoRA. Directly loaded quantized adapters
such as QLoRA are supported. Whisper LoRA and an FP8 dense LoRA kernel are
available.

### Targeted and distributed adapters (`0.19-0.22`)

`--lora-target-modules` restricts adapters to selected modules. Tower and
connector LoRA works for H2OVL; adapters also cover Qwen3-ASR, Gemma 4,
DeepSeek V3.2, XPU, and expert parallelism. Simultaneous 2D and 3D MoE LoRA
adapters are supported.

### New multimodal and MoE adapters (`0.23-0.26`)

MiniCPM-V 4.6 supports language-backbone LoRA. BF16 models support FlashInfer
MoE LoRA, and LLaVA-Next-Video supports tower/connector LoRA.

## Model and task coverage

### Early generation, speech, reward, and embedding families (`0.7-0.10`)

Coverage includes CogAgent, DeepSeek-VL2, InternLM3, Whisper, Qwen2 PRM,
InternLM2 reward models, Gemma 3, Mistral Small 3.1, Phi-4 multimodal, Grok1,
QwQ-32B tool calling, Zamba2, MiMo-7B, MiniMax-VL-01, Ovis 2, Falcon-H1,
LlamaGuard 4, Llama 4 with EAGLE, EXAONE 4.0, Hunyuan V1, JinaVL Reranker,
Arcee, Voxtral, more embedding families, attention-free architectures, and
hybrid SSM/attention models.

Gemma 3 on 0.8 requires Transformers from its main branch and should use
`bfloat16` or `float32`, not numerically unstable `float16`. Falcon-H1 on 0.9
also requires a development Transformers build.

### Encoder-only, multimodal pooling, and new families (`0.11-0.14`)

Coverage includes DeepSeek-V3.2-Exp, Qwen3-VL, OLMo3, Dots OCR, CWM, PLaMo-3,
OpenCUA-7B, Mistral Large 3, Ministral 3, RADIO, Transformers encoder-only
models, BERT token classification/NER, multimodal pooling, and Qwen3 Omni
audio-in-video.

Additional families include BAGEL in autoregressive mode, AudioFlamingo3,
latent MoE, Grok-2, LFM2-VL, MiMo-V2-Flash, openPangu MoE, IQuestCoder,
Nemotron Parse 1.1, GLM-ASR, Isaac vision, Kanana 1.5, and K-EXAONE. Qwen3-VL
supports embeddings and reranking.

### Speech, vision, retrieval, and hybrid families (`0.15-0.18`)

Coverage includes Kimi-K2.5, Molmo2, Step1, Eagle2.5-8B VLM, GLM-OCR,
Qwen3-ASR, Intern-S1-Pro, openPangu7B-VL, MusicFlamingo, GLM-5, Qwen3.5,
Ring 2.5, Ovis 2.6, FunASR, FireRedASR2, Sarvam MoE, OLMo Hybrid,
HyperCLOVAX-SEED-Think-14B, ColPali retrieval, and ERNIE pooling models.

### Gemma 4 and expanded serving support (`0.19-0.22`)

Gemma 4 supports MoE, multimodal input, reasoning, and tools, but requires
`transformers>=5.5.0`; the `vllm/vllm-openai:gemma4` image is the recommended
ready-to-run path.

Other additions include Cohere ASR, ColQwen3.5, Granite 4 Speech and 4.1
Vision, Qwen3-ForcedAligner, DeepSeek V4, Hunyuan v3 preview, EXAONE-4.5,
Phi-4 Reasoning Vision, TeleChat3, Jina Reranker v3, Nemotron-v3 VL,
MiMo-V2.5, Laguna XS.2, Moondream3, Cohere MoE and Eagle, MiniCPM-V 4.6, and
InternS2 Preview. DeepSeek V4 supports ROCm, pipeline/disaggregated serving,
MTP speculation, and NVFP4 MoE.

### Diffusion, OCR, classification, and translation (`0.23-0.26`)

Coverage includes Step-3.7-Flash, Cosmos3 Reasoner, Mellum v2, Cohere Mini
Code, and encoder-free Gemma 4 Unified. MiniMax-M3 is explicitly unsupported
in 0.23 and arrives in 0.24 with DiffusionGemma, HrmText, and OpenMOSS.

Later additions include LLaVA-OneVision-2, Unlimited OCR,
MOSS-Transcribe-Diarize, Hy3, Inkling, RoBERTa/XLM-RoBERTa token
classification, Cosmos3 Edge Reasoner, and TranslateGemma.

### Kimi K3 and current families (`0.27.1`)

Kimi K3 runs through the Python and Rust frontends with native kernels,
AttnRes, DeepGEMM, compressed-tensors checkpoints, and DSpark autoregressive
fusion. Its shared expert may be sharded rather than replicated.

Current additions include Qwen3.5 text-only dense and MoE,
K-EXAONE-2.0-750B-A37B, VaultGemma through the Transformers modeling backend,
and jina-embeddings-v5-text-nano with EuroBERT. Inkling checkpoints accept
`llm-compressor` NVFP4 or compressed-tensors dynamic FP8.
