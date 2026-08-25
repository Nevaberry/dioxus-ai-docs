# Training and distributed execution

## Parallel training and loading

### Tensor-parallel training (4.50.0)

Accelerate workflows support tensor-parallel training.

### Llama 4 expert parallelism (4.54.0)

Set `distributed_config.enable_expert_parallel=True` to train sparse Llama 4
MoE experts independently across devices, reducing the communication required
by tensor parallelism.

### Quantized tensor parallelism (4.52.1)

The initial distributed-inference combination was limited to
`compressed-tensors`, `fp8`, and `fp8-fbgemm`. Other quantizers could not be
combined with tensor parallelism in that release; verify support before
building a mixed stack.

### Removed sequence-parallel path (4.56.0)

Llama 4's sequence-parallel implementation was removed. Do not depend on that
model-specific path.

### Sequence-parallel evaluation (5.2.0)

`Trainer` can evaluate while sequence parallelism is active.

### Decoder tensor-parallel migration (5.3.0)

Corrected all-reduce handling for dense and MoE decoder-only models requires
updates to existing tensor-parallel configurations and checkpoint-conversion
mappings.

### Adapters, Gemma 4, and DDP (5.6.0)

Adapters can load under tensor parallelism. Gemma 4 MoE has a tensor-parallel
plan, and `gemma-4-26B-A4B-it` supports expert parallelism. `Trainer` exposes
`ddp_static_graph` for genuinely static graphs.

### FSDP2 (5.15.1)

Training includes a native FSDP2 module and migration path. Prefer that path
when updating FSDP integrations.

## Loss and optimizer behavior

### Cross-device token averaging and StableAdamW (4.54.0)

`TrainingArguments.average_tokens_across_devices` is enabled by default.
StableAdamW is available as an optimizer.

### Partial accumulation windows (4.55.0)

`Trainer` correctly scales loss when the final gradient-accumulation window has
fewer steps than configured. Runs whose batch count is not evenly divisible can
produce intentionally different updates.

### D-FINE without denoising (5.7.0)

D-FINE computes auxiliary losses when denoising is disabled, correcting the
training objective for that configuration.

## Correctness and numerical safety

### Expert-parallel and FSDP fixes (5.6.0)

Expert-parallel execution was corrected in cases that could silently return
wrong results or NaN loss. FSDP cases that produced NaN weights on ranks other
than rank 0 were also fixed. Re-run multi-rank numerical tests and inspect every
rank after upgrading.

### Gemma 4 and Nemotron-H (5.6.0, 5.7.0)

Gemma 4 training accepts text-only samples. `NemotronHPreTrainedModel` now
advertises gradient-checkpointing support.

### DiffusionGemma training (5.15.1)

DiffusionGemma's block-denoising text architecture is trainable. Its objective
is not ordinary left-to-right next-token decoding, so use the integration's
training path.

## Compilation and export

### Compilation default (4.56.0)

Compilation defaults to `fullgraph=False`, avoiding a full-graph requirement
that is especially restrictive for mixture-of-experts models.

### Exportable inputs and recursive tying (4.56.0)

Torch-exportable decoders accept `inputs_embeds`. Weight tying recurses through
all submodels, and `Trainer` synchronizes tokenizer special-token settings into
the model configuration.

### XPU and automatic hardware compilation (5.1.0, 5.6.0)

DiffLlama can use compile mode on XPU. Neuron devices are included in the
automatic compilation hardware list.

### Continuous-batching compile control (5.15.1)

Continuous batching has a configurable default compile level and can switch to
Flash Attention automatically when suitable.

## Weights, backbones, and integrations

### Checkpoint weight tying (5.4.0)

Weights are tied even if both equivalent tied keys are stored in a checkpoint.
Verify `.bin` checkpoints with duplicate tied keys because load behavior can
change.

### Timm and Trackio (5.2.0)

Timm backbones retain `out_features` across save/load. `TrackioCallback` no
longer provides GPU tracking or environment-variable configuration.

### Static FP8 experts (5.4.0)

Static FP8 experts support multi-GPU configurations. Torchao integrations in
the same batch require torchao 0.15.0 or newer.

## Validation checklist

- Compare losses and updates for a final partial accumulation window.
- Validate every rank for finite weights and loss under expert parallelism and
  FSDP.
- Rebuild tensor-parallel mappings after decoder all-reduce changes.
- Test adapter loading, checkpoint conversion, and quantizer compatibility in
  the exact parallel topology used in production.
- Check export with `inputs_embeds`, nested weight tying, and the chosen compile
  mode.
- Treat static-graph DDP, sequence parallelism, expert parallelism, FSDP2, and
  quantized tensor parallelism as separate compatibility dimensions.
