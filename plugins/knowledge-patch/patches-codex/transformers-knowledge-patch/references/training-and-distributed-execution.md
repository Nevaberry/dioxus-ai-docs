# Training and distributed execution

Use this reference for `Trainer`, masking, optimizers, compilation, tensor,
expert, sequence, and data parallelism, accelerator backends, and
result-affecting training corrections.

## Trainer behavior

### Token accounting (4.54.0)

`TrainingArguments.average_tokens_across_devices` defaults to enabled. Check
custom loss normalization that previously assumed per-device token counts.

### Partial accumulation windows (4.55.0)

`Trainer` correctly scales loss when the final gradient-accumulation window has
fewer steps than configured. Training behavior changes when a batch count is
not evenly divisible by the accumulation length.

### Tokenizer and model configuration alignment (4.56.0)

`Trainer` aligns special-token settings in model configuration with the
tokenizer during training.

### Distributed options

- `Trainer` can evaluate under sequence parallelism as of 5.2.0.
- `ddp_static_graph` is available as of 5.6.0.
- A native FSDP2 module and migration path arrive in 5.15.1.

## Data collation and objectives

### Reproducible whole-word masking (4.51.0)

`DataCollatorForWholeWordMask` accepts a seed, making random masking
reproducible.

### D-FINE auxiliary loss (5.7.0)

D-FINE computes auxiliary losses when denoising is disabled. This corrects the
training objective for that configuration; re-baseline affected jobs.

### Gradient checkpointing (5.7.0)

`NemotronHPreTrainedModel` advertises gradient-checkpointing support.

## Tensor and expert parallelism

### Tensor-parallel training (4.50.0)

Accelerate workflows support tensor-parallel training.

### Quantized tensor parallelism (4.52.1)

Tensor-parallel distributed inference can combine only with
`compressed-tensors`, `fp8`, and `fp8-fbgemm` in this release. Other
quantization methods are unsupported with tensor parallelism.

### Llama 4 expert parallelism (4.54.0)

Set `enable_expert_parallel=True` on `distributed_config` to train sparse MoE
experts across devices independently, reducing tensor-parallel communication.

### Decoder-only tensor-parallel migration (5.3.0)

Corrected all-reduce handling for dense and MoE decoder-only architectures
requires updates to existing tensor-parallel configurations and checkpoint
conversion mappings.

### Expanded model plans (5.6.0)

Adapters can load with tensor parallelism. Gemma 4 MoE has a tensor-parallel
plan, and `gemma-4-26B-A4B-it` supports expert parallelism.

This release corrects expert-parallel cases that could silently produce wrong
results or NaN loss. It also corrects FSDP cases that could produce NaN weights
on non-rank-0 processes. Re-run representative jobs rather than assuming old
checkpoints reflect correct execution.

### Continuous-batching tensor parallelism (5.9.0)

Continuous batching supports tensor parallelism. Its `generate_batch()` path
restores `_attn_implementation` and corrects request offsets; see the generation
reference for serving details.

## Compilation and export

### Compilation default (4.56.0)

Compilation uses `fullgraph=False` by default, which avoids requiring one
complete graph and is especially useful for mixture-of-experts architectures.

### Export inputs (4.56.0)

Torch-exportable decoders accept `inputs_embeds`.

### Hardware compilation support

- DiffLlama can use compile mode on XPU (5.1.0).
- Neuron devices join the automatic compilation hardware list (5.6.0).
- Audio architectures gain vLLM runtime compatibility in 5.6.0.
- Continuous batching gains a configurable default compile level in 5.15.1
  and can switch to Flash Attention automatically.

## Optimizers

### StableAdamW (4.54.0)

StableAdamW is available as a training optimizer.

### Apex removal (5.8.0)

The Apex integration, including Apex RMSNorm use by T5 and related
architectures, is removed. Migrate mixed precision and fused operations to
native PyTorch equivalents.

## Backend-specific execution

### MUSA (4.57.0)

The MUSA backend supports TF32 flags.

### XPU (5.1.0)

XPU provides a MegaBlocks MoE kernel implementation. DiffLlama also supports
XPU compilation.

### MPS and Blackwell (5.3.0)

MLX quantization is available on MPS. NVIDIA Blackwell supports Four Over Six
NVFP4 quantization.

### Neuron (5.4.0)

Kernel integrations support custom kernels on Neuron devices.

### TPU (5.9.0)

Transformers has initial `torch_tpu` backend support.

## Model-specific training behavior

### Gemma 4 (5.6.0)

Gemma 4 training accepts text-only samples. Gemma 4 and Gemma 3n share KV state
independently of whether callers use a `Cache` object, so cache choice no longer
controls state sharing.

### Zamba2 kernel selection (5.6.0)

`Zamba2MambaMixer` honors `use_mamba_kernels=False` instead of continuing to
execute Mamba kernels.

### Llama 4 sequence parallelism (4.56.0)

The Llama 4 sequence-parallel path is removed.

### Timm backbone state (5.2.0)

Timm backbones preserve `out_features` across save and load.

### Trackio callback (5.2.0)

`TrackioCallback` no longer provides GPU tracking or environment-variable
configuration.

## Loading and serialization during distributed work

### Parallel checkpoint loading (5.6.0)

Distributed model support expands alongside parallel loading: adapters load
under tensor parallelism, Gemma 4 gains tensor/expert plans, and corrected
expert/FSDP paths avoid silent wrong results and NaNs.

### Distributed FP8 (5.4.0)

Static FP8 experts are supported in multi-GPU configurations. torchao must be
0.15.0 or newer.

### NVFP4 serialization (5.7.0)

torchao NVFP4 models serialize correctly.

## Output-affecting changes to verify

- Recursive weight tying reaches all submodels as of 4.56.0.
- T5Gemma2 attention selection propagates into every subconfiguration in
  5.1.0.
- Bidirectional attention is available across all architectures in 5.1.0;
  Attention and Experts components are reusable standalone modules.
- Gemma 4 and Gemma 3n cache-state sharing no longer depends on cache-object
  choice in 5.6.0.
- Corrected Qwen2.5-VL still-image temporal RoPE and corrected expert/FSDP
  execution in 5.6.0 can change results after upgrade.
