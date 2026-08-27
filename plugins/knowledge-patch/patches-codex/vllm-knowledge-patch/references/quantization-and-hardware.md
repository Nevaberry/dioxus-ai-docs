# Quantization and Hardware

Use this reference to select checkpoint formats, online quantization, KV-cache
dtypes, custom quantization implementations, and compatible accelerators.

## Hardware boundaries

### Method compatibility (`quantization`)

- AWQ supports NVIDIA Turing through Hopper, Intel GPU, and x86 CPU.
- GPTQ also supports Volta.
- Marlin requires NVIDIA Turing or newer; MXFP4 is unavailable on Turing.
- `llm-compressor` INT8 W8A8 supports NVIDIA Turing or newer plus x86 and Arm
  CPU. Its INT8 W4A8 path is Arm-only; FP8 W8A8 supports Ada, Hopper, and AMD.
- bitsandbytes and DeepSpeedFP support NVIDIA Volta or newer.
- GGUF supports those NVIDIA generations and AMD.

Volta, Turing, Ampere, Ada, and Hopper map to SM 7.0, 7.5, 8.0/8.6, 8.9, and
9.0. Gaudi support is maintained in vLLM-Gaudi; TPU compatibility is a separate
hardware path.

### Early backend additions (`0.7-0.10`)

TPU supports W8A8 and later FP8 KV-cache quantization. CPU supports FP8 KV
cache and ARM CPU INT8. AMD supports V1 FP8 KV cache. Native Apple Silicon,
out-of-tree platforms, s390x CPU, PPC64LE, and ARM V1 execution were added.

### New targets (`0.11-0.14`)

RISC-V 64-bit CPU is supported. SM103/GB300 is supported with CUDA 13, CUDA 13
AArch64 wheels are available, Whisper can run on CPU, and x86 CPU wheels have
a dedicated pipeline.

### New accelerators (`0.27.1`)

The runtime targets NVIDIA Rubin `sm_107` and includes NVLink all-reduce paths
for SM107. ROCm `gfx1250` is also supported.

## Structured and online quantization configuration

### Per-layer-kind configuration (`engine-and-openai-server`)

`--quantization-config` accepts per-layer-kind `QuantSpec` entries for
`linear` and `moe` plus ignore patterns. An online shorthand passed through
`--quantization` automatically populates this structure.
`--allow-deprecated-quantization` explicitly permits deprecated methods.

### TurboQuant attention constraint (`engine-and-openai-server`)

If the resolved KV-cache dtype is TurboQuant, an unset or version-3-or-newer
FlashAttention choice is overridden to version 2. Set
`--attention-config.flash_attn_version=2` explicitly to avoid the warning.

## Checkpoint and kernel progression

### FP4, GGUF, torchao, and MoE (`0.7-0.10`)

Checkpoint support includes ModelOpt FP4, NVFP4, GPTQAllSpark, DeepSeek GGUF,
Quark MXFP4, torchao with `AOPerModuleConfig`, and
`nvidia/DeepSeek-R1-FP4`. MXFP4 covers MoE, BitsAndBytes covers Mixtral and
additional MoE models, and in-flight MoE quantization is available. FP4
emulation was removed; pre-SM100 devices fall back to Marlin.

### GGUF selection and expanded kernels (`0.11-0.14`)

GGUF selection accepts `repo_id:quant_type`, Mistral format is auto-detected,
and multimodal Gemma 3 GGUF can load directly.

Quantization coverage includes dense NVFP4; per-token-group and blocked-MoE
FP8; Turing AWQ compressed tensors; Hopper W4A8 grouped GEMM; online FP8
streaming and weight reload; MoE AWQ/GPTQ Marlin; Turing Marlin; Quark
int4-FP8 W4A8 MoE; dense MXFP4 W4A16; new ModelOpt FP8 variants; and NVFP4
Marlin. Deprecated schemes were removed, and Marlin became the default MXFP4
LoRA backend.

### Mixed precision and direct LoRA loading (`0.15-0.18`)

The runtime supports compressed-tensors MXFP4 W4A16 MoE, per-head FP8 KV
scales, block-FP8 W8A16, dense and MoE ModelOpt MXFP8, directly loaded
quantized LoRA, mixed-precision ModelOpt, and ROCm Quark W4A8 MXFP4/FP8.

Qwen3.5 with an FP8 KV cache has a known degraded-accuracy issue on B200 in
0.18.

### Online MXFP8 and low-bit KV cache (`0.19-0.22`)

Online MXFP8 supports dense and MoE models and is exposed through the general
online-quantization frontend. TurboQuant supplies a 2-bit KV cache with FA3
and FA4 prefill support and later covers hybrid models. NVFP4 KV cache is also
supported.

Checkpoint formats include CPU W4A16, XPU W4A8 compressed tensors, ROCm AWQ
Marlin, compressed-tensors W8A8 MXFP8, ModelOpt NVFP4 W4A16, MXFP4 linear
loading, Quark NVFP4, and AutoRound W4A16. `gptq_marlin` was consolidated
under `auto_gptq`.

### Packed low-bit and per-token quantization (`0.23-0.26`)

ModelOpt supports LM-head and non-gated-MoE MXFP8. Compressed tensors support
WNA8O8Int linear, WNInt embeddings, and asymmetric MoE WNA16. Online FP8
supports per-token-per-channel scaling; `fp8_e5m2` KV cache can be used with a
non-FP8 checkpoint; GGUF quantization moved to a plugin.

Later formats include Humming packed 2/3/5/6/7-bit weight-only,
compressed-tensors W2-W7/A4-A8, Triton INT4 per-token-head KV cache, XPU INT2
weight-only linear, and `nvfp4_per_token` online MoE quantization.

### Current checkpoint and attention additions (`0.27.1`)

Inkling checkpoints support `llm-compressor` NVFP4 weights or
compressed-tensors dynamic FP8. FlashAttention 4 supports FP8 KV cache and
head dimension 256 on SM100.

## Custom quantization plugins

### Register a configuration (`quantization`)

Create a `QuantizationConfig` subclass and decorate it with
`@register_quantization_config("name")`. Implement `get_name`,
`get_supported_act_dtypes`, `get_min_capability`, `get_config_filenames`,
`from_config`, and `get_quant_method`. The last method dispatches on layer type
and returns a method or `None`. Import the registration module before choosing
its name:

```python
import my_quant_plugin
from vllm import LLM

llm = LLM(model="your-model", quantization="my_quant")
```

### Implement linear layers (`quantization`)

For `LinearBase`, return a `QuantizeMethodBase`; use
`UnquantizedLinearMethod` as a starting point. Weight creation receives layer
metadata and application receives an optional bias:

```python
class MyQuantLinearMethod(UnquantizedLinearMethod):
    def create_weights(self, layer, *weight_args, **extra_weight_attrs):
        ...

    def apply(self, layer, x, bias=None):
        ...
```

### Implement fused MoE (`quantization`)

For `FusedMoE`, return a `FusedMoEMethodBase` initialized from
`layer.moe_config`, or `UnquantizedFusedMoEMethod` to keep MoE unquantized.
A custom method defines weight creation, routed application, and its
`FusedMoEQuantConfig`:

```python
class MyQuantMoEMethod(FusedMoEMethodBase):
    def create_weights(
        self, layer, num_experts, hidden_size,
        intermediate_size_per_partition, params_dtype, **extra_weight_attrs,
    ):
        ...

    def apply(self, layer, router, x, router_logits):
        ...

    def get_fused_moe_quant_config(self, layer):
        ...
```
