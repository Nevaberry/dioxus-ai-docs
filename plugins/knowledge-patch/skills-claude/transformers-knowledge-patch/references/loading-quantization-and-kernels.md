# Loading, quantization, and kernels

## Extensible loading

### Custom quantizer registration (4.50.0)

Register the configuration and quantizer under the same method name. The custom
configuration then works through ordinary `from_pretrained` loading.

```python
@register_quantization_config("custom")
class CustomConfig(QuantizationConfigMixin):
    pass

@register_quantizer("custom")
class CustomQuantizer(HfQuantizer):
    pass
```

### Dynamic checkpoint conversion (5.0.0, 5.4.0)

`WeightConverter` declaratively maps checkpoint keys to model keys and can
apply reversible reshape, merge, split, quantization, or parallelism operations.
Use operations such as `Concatenate(dim=0)` to fuse QKV tensors rather than
embedding conversion inside `from_pretrained`. Conversion recurses through
nested model structures as of 5.4.0.

### Dtype, authentication, and shard defaults (5.0.0)

`from_pretrained` defaults to `dtype="auto"`, preserving checkpoint precision;
pass an explicit dtype to force another. Use `token` instead of
`use_auth_token`. Saved-model shards default to at most 50 GB rather than 5 GB.

### Memory mapping and Hub arguments (5.4.0, 5.6.0)

`AutoProcessor.from_pretrained` forwards Hub keyword arguments instead of
dropping them. Model loading accepts `disable_mmap` and automatically detects
hf-mount.

## Quantization methods

### Quark and torchao configuration (4.50.0)

After installing `amd-quark`, load Hub repositories containing Quark-quantized
weights through normal `AutoModelForCausalLM.from_pretrained`. Torchao added
autoquant, CPU quantization, and advanced `AOBaseConfig` configurations in this
batch; note that `torchao.autoquant` was later removed in 5.1.0.

### FP8 and GGUF constraints (4.51.0)

The PyTorch loader accepts FP8 safetensors, including DeepSeek checkpoints.
GGUF cannot be offloaded to disk, so ensure the device map contains no disk
target.

### AutoRound and Gemma 3 GGUF (4.52.1)

AutoRound is supported for low-bit rounding and clipping optimization. GGUF
loading supports the Gemma 3 text backbone and Gemma 3 QAT checkpoints.

### Tensor parallelism limits (4.52.1)

At this point, quantized tensor-parallel inference was limited to
`compressed-tensors`, `fp8`, and `fp8-fbgemm`. Validate the installed release
before combining any other quantization method with tensor parallelism.

### FP-Quant (4.54.0)

`FPQuantConfig` performs on-the-fly FP-Quant loading. Only post-training MXFP4
was initially implemented. Accelerated execution requires an NVIDIA Blackwell
GPU and QuTLASS; `FPQuantConfig(pseudoquant=True)` emulates the quantization
without QuTLASS.

```python
model = AutoModelForCausalLM.from_pretrained(
    "qwen/Qwen3-8B",
    quantization_config=FPQuantConfig(),
    device_map="cuda",
    dtype=torch.bfloat16,
)
```

### GPT-OSS MXFP4 and fallback kernels (4.55.0)

Native GPT-OSS loading supports the `openai/gpt-oss-20b` and
`openai/gpt-oss-120b` MXFP4 MoE checkpoints. The 20B weights fit in 16 GB and
the 120B weights in 80 GB with MXFP4; the 120B model provides a default plan
through `tp_plan="auto"`. When MXFP4 is unavailable,
`use_kernels=True` selects the downloadable MegaBlocks MoE path. That fallback
requires bfloat16 and consumes more memory.

### Qwen3 MoE GGUF (4.55.0, 4.56.0)

The GGUF loader supports Qwen3 mixture-of-experts checkpoints. The following
batch corrected the architecture used for that path.

### Expanded MXFP4 and CPU support (4.56.0)

MXFP4 can dequantize on CPU and selects that route when a `device_map` contains
CPU. GPT-OSS MXFP4 works on NVIDIA `sm75+`; MXFP4 also has a quantization-aware
save path. Int4 models can execute on CPU. Attempting to quantize an already
quantized model now raises an error.

### SINQ, MLX, and Four Over Six (5.2.0, 5.3.0)

SINQ is available as a v5 quantization strategy. MLX quantization works on MPS,
and Four Over Six (4/6) NVFP4 targets NVIDIA Blackwell GPUs. Four Over Six
later gained configurable dtype choices in 5.6.0.

### Torchao and distributed FP8 (5.4.0)

Torchao integrations require torchao 0.15.0 or newer. Static FP8 experts can
run in multi-GPU configurations.

### GPT-OSS GGUF and torchao serialization (5.6.0, 5.7.0, 5.15.1)

GPT-OSS supports full GGUF loading. Torchao NVFP4 models serialize correctly as
of 5.7.0, and TorchAO safetensor loading later accepts parameter names that are
not conventional weight names.

## Kernels and attention implementations

### Explicit kernel opt-in (4.53.0)

Installing `kernels` no longer swaps decorated forwards automatically.
`@use_kernel_forward_from_the_hub` records a kernel name; `kernelize` applies
it, and `from_pretrained(..., use_kernels=True)` opts a model in.

### Hub attention kernels (4.54.0, 4.56.0)

Select a Hub implementation with `set_attn_implementation`; the fetched build
matches installed CUDA and PyTorch. References support revisions, for example:

```python
model.set_attn_implementation("kernels-community/flash-attn3@main")
```

### Dependency rename and GPT-OSS package (4.56.0, 5.1.0)

The old `triton_kernels` dependency was replaced with `kernels`. The GPT-OSS
Triton implementation was later renamed to `gpt-oss-triton-kernels`. XPU also
gained a MegaBlocks MoE kernel in 5.1.0.

### Flash and paged attention kernels (5.4.0)

Flash Attention 2 requires version 2.3.3 or newer. Flash Attention 4 has an
initial `kernels` fallback. Kernel integrations include `paged_attention` for
continuous batching and support custom kernels on Neuron.

### Expert and rotary kernels (5.7.0)

Hub-registered custom expert kernels load correctly. Kernel configuration and
error handling work with FP8 checkpoints, and Gemma3n and Gemma4 can use the
rotary kernel.

### Extended kernel configuration (5.15.1)

`KernelConfig` supports n-to-1 module fusion and parameter transformation. The
Triton integration adds fine-grained FP8 and FP4 kernels.

### Linear-attention families (5.15.1)

Mamba, GDN, and convolution-only models select native fallbacks by default.
Pass `use_kernels=True` during loading to retain kernel-backed execution.

## Loading validation checklist

- Reject device maps that disk-offload GGUF files.
- Test CPU branches for int4 and MXFP4 device maps.
- Confirm hardware, PyTorch, CUDA, torchao, QuTLASS, and kernel-package
  requirements before choosing an accelerated path.
- Verify tied weights and duplicate checkpoint keys after model-load changes.
- Round-trip quantized saves, including NVFP4 and nonstandard parameter names.
- Never stack a new quantizer on a checkpoint that is already quantized.
