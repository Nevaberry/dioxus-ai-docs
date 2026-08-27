# Quantization Formats, Hardware, and Extensions

## Start with the hardware matrix

AWQ supports NVIDIA Turing through Hopper, Intel GPU, and x86 CPU; GPTQ adds
Volta. Marlin requires NVIDIA Turing or newer, but MXFP4 is unavailable on
Turing. `llm-compressor` INT8 W8A8 supports NVIDIA Turing or newer plus x86
and Arm CPUs, INT8 W4A8 is Arm-only, and FP8 W8A8 supports Ada, Hopper, and
AMD. bitsandbytes and DeepSpeedFP support NVIDIA Volta or newer. GGUF covers
those NVIDIA generations plus AMD.

Volta, Turing, Ampere, Ada, and Hopper correspond to SM 7.0, 7.5, 8.0/8.6,
8.9, and 9.0. Gaudi quantization support lives in vLLM-Gaudi; TPU
compatibility is maintained separately. A checkpoint format being loadable
does not imply every accelerator, KV-cache dtype, LoRA path, or fused-MoE
kernel is supported.

## Configure quantization by layer kind

`--quantization-config` accepts per-layer-kind `QuantSpec` values for `linear`
and `moe` layers plus ignore patterns. An online-quantization shorthand passed
through `--quantization` populates this structured configuration.
`--allow-deprecated-quantization` explicitly permits deprecated schemes.

Online and low-bit selection evolved into a general online-quantization
frontend in `0.19-0.22`; preserve structured layer intent instead of relying
on an old backend-specific shorthand.

## Build an out-of-tree quantization method

### Register the configuration

Decorate a `QuantizationConfig` subclass with
`@register_quantization_config("name")`. Implement `get_name`,
`get_supported_act_dtypes`, `get_min_capability`, `get_config_filenames`,
`from_config`, and `get_quant_method`. The final method dispatches on layer
type and returns a quantization method or `None`. Import the registration
module before selecting the method:

```python
import my_quant_plugin
from vllm import LLM

llm = LLM(model="your-model", quantization="my_quant")
```

### Implement linear layers

For `LinearBase`, return a `QuantizeMethodBase` implementation;
`UnquantizedLinearMethod` is a starting point. Weight creation receives
metadata, and application receives an optional bias:

```python
class MyQuantLinearMethod(UnquantizedLinearMethod):
    def create_weights(self, layer, *weight_args, **extra_weight_attrs):
        ...

    def apply(self, layer, x, bias=None):
        ...
```

### Implement fused MoE separately

For `FusedMoE`, return a `FusedMoEMethodBase` initialized from
`layer.moe_config`, or `UnquantizedFusedMoEMethod` to leave the layer
unquantized. A custom method creates weights, applies routed execution, and
returns a `FusedMoEQuantConfig`:

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

## Checkpoint and kernel format evolution

### FP4, GGUF, GPTQ, and ModelOpt foundations

Batch `0.7-0.10` added ModelOpt FP4, NVFP4, GPTQAllSpark, DeepSeek GGUF,
Quark MXFP4, torchao models with `AOPerModuleConfig`, and
`nvidia/DeepSeek-R1-FP4`. It then added MXFP4 for MoE, BitsAndBytes for
Mixtral and more MoE models, and in-flight MoE quantization. FP4 emulation was
removed; pre-SM100 devices fall back to Marlin.

### Dense, MoE, streaming, and Marlin expansion

Batch `0.11-0.14` added dense NVFP4; per-token-group and blocked-MoE FP8;
Turing AWQ compressed tensors; Hopper W4A8 grouped GEMM; online FP8 streaming
and weight reload; MoE AWQ/GPTQ Marlin; Turing Marlin; Quark int4-FP8 W4A8
MoE; dense MXFP4 W4A16; additional ModelOpt FP8 variants; and NVFP4 Marlin.
It removed deprecated quantization schemes and made Marlin the default MXFP4
LoRA backend.

GGUF selection accepts `repo_id:quant_type`, Mistral format can be detected
automatically, and multimodal Gemma 3 GGUF is supported.

### MXFP, FP8 KV scales, and quantized adapters

Batch `0.15-0.18` added compressed-tensors MXFP4 W4A16 MoE, per-head FP8
KV-cache scales, block-FP8 W8A16, dense and MoE ModelOpt MXFP8, directly
loaded quantized LoRA, mixed-precision ModelOpt, and ROCm Quark W4A8
MXFP4/FP8 paths.

It removed DeepSpeedFp8 and RTN, then BitBlas and Marlin 24. Directly loaded
quantized adapters such as QLoRA and an FP8 dense LoRA kernel require their
respective newer paths. Qwen3.5 on B200 has a degraded-accuracy caveat with an
FP8 KV cache in this batch.

### Online MXFP8, TurboQuant, and low-bit KV

Batch `0.19-0.22` added online MXFP8 for dense and MoE, then moved it into the
general online-quantization frontend. TurboQuant 2-bit KV cache supports
FA3/FA4 prefill and later hybrid models; NVFP4 KV cache was also added.

Checkpoint support in the same batch added CPU W4A16 and XPU W4A8 compressed
tensors, ROCm AWQ Marlin, compressed-tensors W8A8 MXFP8, ModelOpt NVFP4
W4A16, MXFP4 linear-layer loading, Quark NVFP4, and AutoRound W4A16.
`gptq_marlin` was consolidated under `auto_gptq`.

That batch deprecated `--calculate-kv-scales` and removed per-tensor and
per-channel FP8 plus Sparse24 integration.

### W2-W7, online per-channel FP8, and plugin GGUF

Batch `0.23-0.26` added ModelOpt LM-head and non-gated-MoE MXFP8;
compressed-tensors WNA8O8Int linears, WNInt embeddings, and asymmetric MoE
WNA16; online FP8 per-token-per-channel quantization; and `fp8_e5m2` KV cache
with non-FP8 checkpoints. GGUF quantization moved to a plugin.

Later additions in that batch include Humming packed 2/3/5/6/7-bit
weight-only; W2-W7/A4-A8 compressed-tensors; Triton INT4 per-token-head KV
cache; XPU INT2 weight-only linear; and `nvfp4_per_token` online MoE
quantization. `gptq_marlin` was removed on ROCm, and the old online FP8 MoE
class was deprecated.

### Current checkpoint additions

In `0.27.1`, Kimi K3 supports compressed-tensors checkpoints; Inkling supports
llm-compressor NVFP4 or compressed-tensors dynamic FP8. Quantized DSpark
Markov heads are supported. FlashAttention 4 supports FP8 KV caches and head
dimension 256 on SM100.

## Hardware-specific KV and weight quantization

TPU gained W8A8 in `0.7-0.10`; CPU gained FP8 KV cache; AMD gained FP8 KV
cache on V1; TPU later gained FP8 KV-cache quantization; and Arm CPU gained
INT8 quantization.

On Blackwell, MLA initially defaulted to FlashInfer and prefill to TRTLLM
(`0.15-0.18`). Sparse MLA with FP8 KV later defaulted to FlashInfer, while
FlashAttention 4 became the MLA prefill default on SM90+
(`0.19-0.22`).

When the resolved KV-cache dtype is TurboQuant, an unset or version-3-or-newer
FlashAttention selection is overridden to version 2. Set
`--attention-config.flash_attn_version=2` to avoid the warning.

Generation models can keep `lm_head` in FP32 with `head_dtype`, including on
the LoRA path (`0.23-0.26`). Per-cache-group attention backends allow hybrid
models to mix kernels when their cache groups have different capabilities.

## Runtime, wheel, and toolchain transitions

### PyTorch and CUDA changes

Batch `0.7-0.10` moved first to PyTorch 2.6 with CUDA 12.4 wheels, then
PyTorch 2.7 with CUDA 12.8 as the default. CUDA 12.4 support was removed;
CUDA 12.6 was offered as a GitHub artifact. The later point release used
PyTorch 2.7.1, and `--torch-backend=auto` was available in the CUDA 12.8
installation flow.

Batch `0.11-0.14` moved CPU builds to PyTorch 2.8 and ROCm to 7.0, then
required PyTorch 2.9.0 with CUDA 12.9 and Transformers 4.57.3. It later
required PyTorch 2.9.1, with `cu129` as the default wheel.

Batch `0.15-0.18` upgraded to PyTorch 2.10.0; an updated wheel fixed the
CUDA 12.9+ library-mismatch failure. XPU moved from IPEX to
`vllm-xpu-kernels`, ROCm renamed `aiter` to `amd-aiter`, and Ray left the
default dependency set.

Batch `0.19-0.22` changed the default PyPI wheel and compatible server image
to CUDA 13.0, upgraded CUDA and XPU builds to PyTorch 2.11, added Python 3.14,
and moved to `transformers>=5`. CUDA 12.9 users were advised to install via
`uv` with `--torch-backend=cu129`. Transformers v4 was deprecated and a
C++20-compatible compiler became mandatory.

Batch `0.23-0.26` moved ROCm to PyTorch 2.11, XPU to torch-xpu 2.12, CUDA
container builds to GCC 12, and made `mistral_common` optional. Starlette must
be at least 1.0.1 for its security fix. Transformers integration moved to
5.13.0.

In `0.27.1`, the runtime baseline moved to PyTorch 2.13.0, torchvision 0.28.0,
and Triton 3.7.1; CPU and XPU builds also use torch 2.13. Rebuild images and
native extensions for this breaking environment transition.

### Packaging and containers

CUDA 13.0 wheels in 0.21 and CUDA 12.9 wheels in 0.22 moved to PyTorch's
`manylinux_2_28` base (`0.19-0.22`). A non-root `vllm-openai` Docker target
and optional Python-only installation were added. Constrained containers must
also satisfy cgroup memory and `/dev/shm` checks (`0.27.1`).

## Architecture and accelerator targets

Native Apple Silicon and out-of-tree platform support arrived in
`0.7-0.10`, followed by s390x CPU inference, PPC64LE, and Arm V1 support.

Batch `0.11-0.14` added RISC-V 64-bit CPU, then SM103/GB300 with CUDA 13,
CUDA 13 AArch64 wheels, CPU Whisper, and an x86 CPU wheel pipeline.

In `0.27.1`, vLLM added NVIDIA Rubin `sm_107` targeting with NVLink
all-reduce paths on SM107 and ROCm `gfx1250` support.

## Validation checklist

- Match the checkpoint scheme to the layer kind, activation dtype, minimum
  compute capability, backend, and KV-cache dtype.
- Confirm whether the format is native, compressed-tensors, llm-compressor,
  ModelOpt, Quark, AutoRound, GGUF-plugin, or an online quantization path.
- Rebuild for PyTorch, CUDA/ROCm/XPU, Triton, compiler, Python, and manylinux
  transitions; do not reuse extensions across ABI baselines.
- On accuracy regressions, test a non-quantized KV cache and FP32 generation
  head before changing the model or parser.
- For custom plugins, import registration before construction and return a
  layer-appropriate method for both linear and fused-MoE layers.
