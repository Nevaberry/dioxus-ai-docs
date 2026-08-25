# Loading, quantization, and kernels

Use this reference for checkpoint I/O, dtype and device-map behavior,
quantization, attention implementations, custom kernels, and model
serialization.

## Loading defaults and checkpoint conversion

### Dtype migration

`dtype` is preferred across the API as of 4.56.0; `torch_dtype` remains
accepted during the transition.

```python
model = AutoModelForCausalLM.from_pretrained(
    "facebook/opt-350m",
    dtype="auto",
)
```

In 5.0.0, `from_pretrained` defaults `dtype` to `auto`, preserving the saved
checkpoint dtype rather than forcing float32. Pass an explicit dtype when the
application requires float32 or another representation. The default maximum
shard size for saving models rises from 5 GB to 50 GB.

### Dynamic weight conversion

`WeightConverter` (5.0.0) maps checkpoint keys to model keys while applying
reversible reshape, merge, split, quantization, or parallelism operations.
Integrations can declaratively fuse Q, K, and V tensors instead of embedding
the transformation in `from_pretrained`.

```python
conversion = WeightConverter(
    ["self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj"],
    "self_attn.qkv_proj",
    operations=[Concatenate(dim=0)],
)
```

Conversion recurses through nested model structure as of 5.4.0. Preserve
heterogeneous per-layer configuration when authoring conversions for models
that mix attention types.

### Authentication and memory mapping

Replace `use_auth_token` with `token` in 5.0.0. As of 5.6.0,
`from_pretrained` accepts `disable_mmap` and automatically detects hf-mount
environments.

### Weight tying (5.4.0)

Weights are tied even when both tied checkpoint keys contain the same values.
Verify `.bin` checkpoints containing duplicate tied keys because load behavior
can differ.

## Quantization configuration

### Register custom methods (4.50.0)

Register a configuration and quantizer under the same method name. The
registered config is then accepted by `from_pretrained`.

```python
@register_quantization_config("custom")
class CustomConfig(QuantizationConfigMixin):
    pass

@register_quantizer("custom")
class CustomQuantizer(HfQuantizer):
    pass

model = AutoModelForCausalLM.from_pretrained(
    "facebook/opt-350m",
    quantization_config=CustomConfig(),
    dtype="auto",
)
```

### Loading argument migration (5.0.0)

Top-level `load_in_4bit` and `load_in_8bit` are removed. Put these choices in
a `quantization_config`.

```python
from transformers import AutoModelForCausalLM, BitsAndBytesConfig

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-3B",
    token=token,
    device_map="auto",
    quantization_config=BitsAndBytesConfig(load_in_4bit=True),
)
```

### Quark and torchao (4.50.0)

After installing `amd-quark`, load repositories containing Quark weights with
the ordinary `AutoModelForCausalLM.from_pretrained` path. torchao supports
autoquant, CPU quantization, and advanced `AOBaseConfig` configuration in this
release.

The `torchao.autoquant` integration is removed in 5.1.0. torchao itself must be
0.15.0 or newer in 5.4.0. NVFP4 torchao models serialize correctly as of
5.7.0, and TorchAO safetensor loading accepts non-weight parameter names in
5.15.1.

### FP-Quant (4.54.0)

`FPQuantConfig` enables on-the-fly FP-Quant loading. Initially, only
post-training MXFP4 is implemented. Accelerated execution requires a
Blackwell-generation NVIDIA GPU and QuTLASS; `pseudoquant=True` emulates the
quantization without QuTLASS.

```python
import torch
from transformers import AutoModelForCausalLM, FPQuantConfig

model = AutoModelForCausalLM.from_pretrained(
    "qwen/Qwen3-8B",
    quantization_config=FPQuantConfig(),
    device_map="cuda",
    dtype=torch.bfloat16,
)
```

### AutoRound, SINQ, MLX, and Four Over Six

- AutoRound low-bit rounding and clipping optimization is supported as of
  4.52.1.
- SINQ is available as a v5 quantization strategy in 5.2.0.
- MLX quantization is supported on MPS, and Four Over Six NVFP4 is supported on
  Blackwell GPUs as of 5.3.0.
- Four Over Six gains configurable dtype options in 5.6.0.

### Tensor-parallel and distributed constraints

In 4.52.1, tensor-parallel distributed inference can combine only with
`compressed-tensors`, `fp8`, or `fp8-fbgemm`. Other quantizers are unsupported
with tensor parallelism in that release. Static FP8 experts work in multi-GPU
configurations as of 5.4.0.

## Quantized checkpoint formats

### FP8 and GGUF

- PyTorch can load FP8 safetensors such as DeepSeek checkpoints (4.51.0).
- GGUF cannot be disk-offloaded as of 4.51.0; its device map must avoid disk.
- Gemma 3 text-backbone and Gemma 3 QAT GGUF checkpoints load as of 4.52.1.
- Qwen3 MoE GGUF loads as of 4.55.0; its architecture mapping is corrected in
  4.56.0.
- GPT-OSS gains full GGUF loading in 5.6.0.

### MXFP4 and GPT-OSS

Transformers loads the `gpt-oss-20b` and `gpt-oss-120b` MoE checkpoints,
including MXFP4 MoE weights, as of 4.55.0. The 20B checkpoint fits in 16 GB
with MXFP4; the 120B fits in 80 GB and has a default tensor-parallel plan
selectable with `tp_plan="auto"`.

```python
model = AutoModelForCausalLM.from_pretrained(
    "openai/gpt-oss-20b",
    device_map="auto",
    dtype="auto",
)
```

In 4.56.0, MXFP4 can dequantize on CPU and automatically does so when a
`device_map` contains CPU. GPT-OSS MXFP4 also supports NVIDIA `sm75+`, gains a
quantization-aware save path, and `int4` models can run on CPU. Attempting to
quantize an already quantized model raises an error.

## Kernel activation

### Explicit opt-in (4.53.0)

Installing `kernels` no longer replaces decorated forward methods. Pass
`use_kernels=True`; `@use_kernel_forward_from_the_hub` records a kernel name,
and `kernelize` applies it.

```python
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3.2-1B-Instruct",
    use_kernels=True,
)
```

Linear-attention families including Mamba, GDN, and convolution-only models
also use native fallbacks unless `use_kernels=True` is explicit as of 5.15.1.

### Hub attention and expert kernels

Select an attention implementation at runtime with
`set_attn_implementation` (4.54.0). A Hub kernel reference fetches a build
matching installed CUDA and PyTorch versions.

```python
model.set_attn_implementation("kernels-community/flash-attn3")
```

References accept `@revision` suffixes as of 4.56.0, for example
`kernels-community/flash-attn3@main`. Custom expert kernels from the Hub load
correctly in 5.7.0; FP8 kernel configuration and error handling are also fixed,
and Gemma3n and Gemma4 can use the rotary kernel.

### Extended custom kernels (5.15.1)

`KernelConfig` supports n-to-1 module fusion and parameter transformation. The
Triton integration provides fine-grained FP8 and FP4 kernels.

## Attention backend behavior

Custom attention functions can be registered for Transformers dispatch as of
4.51.0. Registered implementations must also follow later attention-mask and
rotary-function interface changes described in the compatibility reference.

### Flash Attention

- Flash Attention 3 is supported across popular architectures in 4.53.0.
- Unsupported combinations of `output_attentions=True` and an attention
  implementation fail early instead of silently falling back to eager
  attention (4.53.0).
- Flash Attention sliding-window size, cache continuation, and causality are
  corrected in 4.56.0.
- Flash Attention 2 requires 2.3.3 or newer in 5.4.0. Initial Flash Attention 4
  support includes a `kernels` fallback.
- Kernel integrations add `paged_attention` for continuous batching and custom
  kernel support on Neuron in 5.4.0.

### GPT-OSS kernels (4.55.0)

On Hopper GPUs with PyTorch 2.7 or 2.8, GPT-OSS can use sink-aware Flash
Attention 3 after upgrading `kernels`. If MXFP4 is unavailable,
`use_kernels=True` opts into a downloadable MegaBlocks MoE implementation;
that path requires bfloat16 and uses more memory.

```python
model = AutoModelForCausalLM.from_pretrained(
    "openai/gpt-oss-20b",
    attn_implementation="kernels-community/vllm-flash-attn3",
    device_map="auto",
    dtype="auto",
)
```

XPU gains a MegaBlocks MoE kernel in 5.1.0. The renamed GPT-OSS Triton package
in that release is `gpt-oss-triton-kernels`.

### ModernBERT and T5 defaults

ModernBERT no longer selects Flash Attention by default in 5.2.0. T5, MT5,
LongT5, and related architectures support SDPA and other registered backends as
of 5.15.1. Set `attn_implementation="eager"` when eager execution is required
for reproducibility or compatibility.

### Compilation (4.56.0)

Transformers compilation defaults to `fullgraph=False`, avoiding a restrictive
full-graph requirement, especially for mixture-of-experts architectures.

## Native integrations and remote code

Native LightGlue loading no longer supports remote-code execution as of 5.5.0.
Remove `trust_remote_code=True` and use the standard native API. Conversely,
custom generation remains executable code and requires explicit trust as
documented in the generation reference.
