# Models, Multimodal Integration, Adapters, and Lifecycle

## Custom model integration

### V1 forward contract

From `0.7-0.10`, custom model `forward` methods no longer receive `kv_cache`
or `attn_metadata`; attention backends obtain both from `forward_context`.
`SupportsV0Only` briefly allowed definitions to declare an old-engine
requirement, but V0 was subsequently removed.

### Multimodal extension contract

An out-of-tree model that implements the merged multimodal processor and the
appropriate `get_*_embeddings` methods is automatically supported by V1. The
legacy input mapper was deprecated in `0.7-0.10`. The Transformers modeling
backend later gained VLM support and multimodal caching.

Multimodal preprocessing runs outside the engine loop. Preprocessed inputs can
be shared across requests, image hashes participate in prefix-cache lookup,
and an independent encoder cache retains vision embeddings. This separation
lets the scheduler split the text prefill across steps instead of coupling all
text with the media item.

### Encoder execution controls

Processor caching has `--mm-processor-cache-type` and a shared-memory
object-size cap. The encoder independently selects tensor-parallel mode,
attention backend, and attention dtype. Encoder FP8 scales can be loaded or
saved with a configurable save margin. Multimodal tensor IPC has its own mode
and GPU-memory budget.

### Streaming and embedding inputs

V1 added prompt embeddings in `0.11-0.14`, and chat completions gained audio
embeddings. Engines can consume async generators of `StreamingInput` objects
while preserving KV-cache alignment (`0.15-0.18`), providing a session-style
path for workloads such as ASR. Image embeddings, multiple image/audio items,
and `mm_processor_kwargs` are supported on the corresponding request paths.

## Runtime lifecycle and training integration

### Sleep, wake, RPC, and model application

Batch `0.7-0.10` added `LLM.sleep`, `LLM.wake_up`, `LLM.collective_rpc`, and
`LLM.reset_prefix_cache` for post-training integrations. It later extended RPC
with runtime weight reload and configuration updates. Batch `0.11-0.14` added
sharded state loading, `LLM.apply_model`, and pause/resume generation for
asynchronous RL training.

### Weight synchronization and request preservation

Batch `0.15-0.18` added native NCCL weight sync, layerwise reloading, and
pause/resume that preserves requests. It then added an IPC weight-sync path and
sleep level 0 with an enqueue/wait pattern. Batch `0.19-0.22` exposed
`/start_weight_update` and `/finish_weight_update` for explicit RLHF update
boundaries.

In `0.27.1`, RL rollout paths can attach a version to weights. The FlashInfer
monolithic MoE kernel can return router-replay output for training
integrations.

## LoRA adapters and resolvers

### Initial V1 and platform expansion

Rank-Stabilized LoRA arrived in `0.7-0.10`, followed by V1 LoRA and LoRA for
`TransformersModel`. Multi-LoRA expanded across x86, TPU, and Neuron. A
default local-directory LoRA resolver and Tensorizer loading for both V1 and
LoRA followed.

### Sharded and multimodal adapters

Batch `0.11-0.14` added `--fully-sharded-loras` for fused MoE. It later added
LoRA on multimodal towers/connectors for LLaVA, PaliGemma, DotsOCR, and GLM4-V;
DeepSeek-OCR, Qwen3-Next, and PLaMo 2/3; vision-LoRA processor caching; and MoE
expert `base_layer` loading.

Batch `0.23-0.26` added language-backbone LoRA for MiniCPM-V 4.6,
FlashInfer MoE LoRA for BF16 models, and tower/connector LoRA for
LLaVA-Next-Video.

### Remote, quantized, audio, and targeted adapters

Batch `0.15-0.18` added a Hugging Face Hub resolver, direct loading of
quantized adapters such as QLoRA, Whisper LoRA, and an FP8 dense LoRA kernel.

`--lora-target-modules` restricts adapters to selected modules
(`0.19-0.22`). The same batch added H2OVL tower/connector LoRA, adapters for
Qwen3-ASR, Gemma 4, and DeepSeek V3.2, XPU and expert-parallel support, and
simultaneous 2D and 3D MoE LoRA adapters.

### LoRA migration notes

LoRA extra vocabulary was removed in `0.11-0.14`. Long-context LoRA was part
of the V0 cleanup. Quantized checkpoints and adapters must still match the
selected kernel, layer type, sharding, and accelerator support; model-level
LoRA support does not imply every quantized or multimodal path is available.

## Loading formats and checkpoint behavior

Batch `0.11-0.14` accepts `repo_id:quant_type` when selecting a GGUF model,
auto-detects Mistral format, and supports multimodal Gemma 3 GGUF loading.
Batch `0.7-0.10` added Tensorizer loading for V1 and LoRA.

Security-sensitive loading became stricter in `0.15-0.18`: NemotronVL and
KimiK25 honor `trust_remote_code`, and RLHF weight-sync deserialization is
gated by the insecure-serialization setting. Earlier hardening loads PyTorch
weights with `weights_only=True`.

Offline Hugging Face mode resolves non-cloud model and tokenizer repository
IDs to revision-specific local paths. Cloud-storage URIs remain unchanged.
`EngineArgs(tokens_only=True)` separately skips tokenizer initialization.

## Pooling, embedding, classification, and scoring models

From `0.7-0.10`, one model can advertise multiple tasks and poolers, with
pooling parameters selected dynamically at runtime. Do not assume one fixed
task/pooler per integration.

Batch `0.11-0.14` expanded support to RADIO and Transformers encoder-only
models, BERT token classification/NER, multimodal pooling, Qwen3 Omni
audio-in-video, and Qwen3-VL embedding/reranking. Batch `0.15-0.18` added
BGE-M3 sparse and ColBERT embeddings, multimodal late-interaction scoring,
sparse-embedding IO, Cohere Embed v2 compatibility, ColPali retrieval, and
ERNIE pooling models.

Batch `0.23-0.26` added RoBERTa/XLM-RoBERTa token classification. In
`0.27.1`, MRV2 covers encoder-only attention, sequence pooling for embedding
and classification, encoder token classification and embeddings, and BGE-M3
pooling; `jina-embeddings-v5-text-nano` arrived with its EuroBERT encoder.

## Diffusion and attention-free workloads

Batch `0.23-0.26` added DiffusionGemma with CPU execution and
structured-output guardrails for diffusion decoders, then tensor parallelism
and Hugging Face stability-window semantics. In `0.27.1`, DiffusionGemma also
accepts `top_k` and `top_p`.

Attention-free architectures and hybrid SSM/attention models arrived during
`0.7-0.10`. MRV2 later expanded to Qwen3.5/Mamba hybrids, Mamba-hybrid prefix
caching, and additional hybrid-model paths.

## Model and task compatibility catalog

### Text, multimodal, reward, and speech additions

Batch `0.7-0.10` added CogAgent, DeepSeek-VL2, InternLM3, Whisper, Qwen2 PRM,
InternLM2 reward models, Gemma 3, Mistral Small 3.1, Phi-4 multimodal, Grok1,
QwQ-32B tool calling, and Zamba2. It later added MiMo-7B, MiniMax-VL-01,
Ovis 2, Falcon-H1, LlamaGuard 4, Llama 4 with EAGLE, EXAONE 4.0, Hunyuan V1,
JinaVL Reranker, Arcee, Voxtral, additional embedding families,
attention-free architectures, and hybrid SSM/attention models.

Gemma 3 on 0.8 requires Transformers from its main branch and should use
`bfloat16` or `float32`; `float16` is numerically unstable. Falcon-H1 on 0.9
also requires a development Transformers installation.

### V1-era architecture expansion

Batch `0.11-0.14` added DeepSeek-V3.2-Exp, Qwen3-VL, OLMo3, Dots OCR, CWM,
PLaMo-3, OpenCUA-7B, Mistral Large 3, Ministral 3, BAGEL (autoregressive only),
AudioFlamingo3, latent MoE, Grok-2, LFM2-VL, MiMo-V2-Flash, openPangu MoE,
IQuestCoder, Nemotron Parse 1.1, GLM-ASR, Isaac vision, Kanana 1.5, and
K-EXAONE.

The same batch expanded tasks to RADIO, Transformers encoder-only models,
BERT token classification/NER, multimodal pooling, Qwen3 Omni audio-in-video,
and Qwen3-VL embedding/reranking.

### Realtime, ASR, retrieval, and hybrid expansion

Batch `0.15-0.18` added Kimi-K2.5, Molmo2, Step1, Eagle2.5-8B VLM, GLM-OCR,
Qwen3-ASR, Intern-S1-Pro, openPangu7B-VL, MusicFlamingo, GLM-5, Qwen3.5,
Ring 2.5, Ovis 2.6, FunASR, FireRedASR2, Sarvam MoE, OLMo Hybrid,
HyperCLOVAX-SEED-Think-14B, ColPali retrieval, and ERNIE pooling models.

Qwen3.5 with an FP8 KV cache on B200 has a known degraded-accuracy issue in
that batch; select another cache dtype when accuracy is critical.

### Gemma 4 and later serving models

Batch `0.19-0.22` added Cohere ASR, ColQwen3.5, Granite 4 Speech and 4.1
Vision, Qwen3-ForcedAligner, DeepSeek V4, Hunyuan v3 preview, EXAONE-4.5,
Phi-4 Reasoning Vision, TeleChat3, Jina Reranker v3, Nemotron-v3 VL,
MiMo-V2.5, Laguna XS.2, Moondream3, Cohere MoE and Eagle, MiniCPM-V 4.6, and
InternS2 Preview. DeepSeek V4 gained ROCm, pipeline/disaggregated serving, MTP
speculation, and NVFP4 MoE support.

Gemma 4 support includes MoE, multimodal, reasoning, and tool use, but requires
`transformers>=5.5.0`. The recommended ready-to-run path in that batch is the
`vllm/vllm-openai:gemma4` image.

### Dense, diffusion, and encoder additions

Batch `0.23-0.26` added Step-3.7-Flash, Cosmos3 Reasoner, Mellum v2, Cohere
Mini Code, encoder-free Gemma 4 Unified, MiniMax-M3, DiffusionGemma, HrmText,
OpenMOSS, LLaVA-OneVision-2, Unlimited OCR, MOSS-Transcribe-Diarize, Hy3,
Inkling, RoBERTa/XLM-RoBERTa token classification, Cosmos3 Edge Reasoner, and
TranslateGemma. MiniMax-M3 was explicitly unsupported in 0.23 and arrived in
0.24.

### Kimi K3 and current additions

In `0.27.1`, Kimi K3 landed in the Python and Rust frontends with native
kernels, AttnRes, DeepGEMM, compressed-tensors checkpoints, and DSpark
autoregressive fusion. Its shared expert can be sharded instead of replicated.

The same batch added Qwen3.5 text-only dense and MoE models,
K-EXAONE-2.0-750B-A37B, VaultGemma through the Transformers modeling backend,
and `jina-embeddings-v5-text-nano` with EuroBERT. Inkling checkpoints can use
llm-compressor NVFP4 or compressed-tensors dynamic FP8. The Transformers
backend also accepts audio models.

## Retired models and integration paths

Batch `0.23-0.26` deprecated `JAISLMHeadModel` and first-generation Qwen and
QwenVL. It removed ERNIE, Xverse, Bamba, the InternLM registry alias,
Baichuan, Aquila, Tarsier, Tarsier2, Mantis, TeleChat, Persimmon, and Fuyu.
The same batch removed `P2pNcclConnector`, dropped `gptq_marlin` on ROCm,
moved legacy `api_server.py` to examples, and deprecated the old online FP8
MoE class.

Earlier removals include V0-only CPU/XPU/TPU/HPU backends, long-context LoRA,
Phi3-Small, BlockSparse Attention, and legacy multimodal input fallbacks. Check
the installed version before retaining a compatibility shim for any of these.
