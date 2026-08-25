# Platforms, Extensions, and Runtime

## Contents

- [Choose wheels and CUDA builds](#choose-wheels-and-cuda-builds)
- [Match the Linux C++ ABI](#match-the-linux-c-abi)
- [Use the limited stable extension ABI](#use-the-limited-stable-extension-abi)
- [Autoload device extensions](#autoload-device-extensions)
- [Target Intel GPUs](#target-intel-gpus)
- [Build XPU extensions and use XPUGraph](#build-xpu-extensions-and-use-xpugraph)
- [Compile quantized workloads](#compile-quantized-workloads)
- [Target ROCm](#target-rocm)
- [Target MPS](#target-mps)
- [Interoperate with native streams](#interoperate-with-native-streams)
- [Control autograd storage](#control-autograd-storage)
- [Use sparse complex views](#use-sparse-complex-views)
- [Bound profiler post-processing](#bound-profiler-post-processing)

## Choose wheels and CUDA builds

PyTorch 2.7.0 added prototype NVIDIA Blackwell support and prebuilt CUDA 12.8
wheels for Linux x86 and arm64. Its bundled Triton 3.3 supports Blackwell under
`torch.compile`:

```sh
pip install torch==2.7.0 --index-url https://download.pytorch.org/whl/cu128
```

Linux aarch64 wheels became available for every supported CUDA version in
2.9.0.

In 2.11.0, plain `pip install torch` from PyPI installs CUDA 13.0 on Linux
x86_64 and aarch64. Systems whose drivers support only CUDA 12.x may require an
explicit build. CUDA 13 supports Turing (SM 7.5) and later on Linux x86_64.
CUDA 12.8 and 12.9 binaries also drop Volta, so Maxwell, Pascal, and Volta users
should select CUDA 12.6:

```sh
pip install torch --index-url https://download.pytorch.org/whl/cu126
```

Experimental Wheel Variants arrived in 2.8.0. Multiple wheels for one package
version declare hardware properties and provider plugins choose a compatible
variant. The initial flow detected NVIDIA GPUs and CUDA drivers on Linux x86,
aarch64, and macOS. Install the variant-aware `uv` build with:

```sh
curl -LsSf https://astral.sh/uv/install.sh | INSTALLER_DOWNLOAD_URL=https://wheelnext.astral.sh sh
```

In 2.9.0, provider plugins added AMD ROCm, Intel XPU, and NVIDIA CUDA 13
detection. CUDA variants cover Linux and Windows; ROCm and XPU variants remain
Linux-only.

## Match the Linux C++ ABI

Experimental 2.6.0 CUDA 12.6.3, AArch64, ROCm 6.2.4, and XPU Linux binaries use
Manylinux 2.28 and `CXX11_ABI=1`. Build custom C++ and CUDA extensions loaded by
these distributions with CXX11 ABI 1 as well.

## Use the limited stable extension ABI

PyTorch 2.8.0 introduced the API-unstable `STABLE_TORCH_LIBRARY` registration
API and `torch::stable::Tensor`. An extension restricted to this limited stable
libtorch API subset can be compiled against one PyTorch version and used by
another without rebuilding.

The 2.9.0 surface adds device-guard and stream helpers in
`torch/csrc/stable/accelerator.h`; a default `torch::stable::Tensor`
constructor; tensor `is_cpu`, `scalar_type`, and `get_device_index`; and stable
`amax`, `narrow`, `pad`, `new_empty`, and `new_zeros`, including dtype variants
for tensor creation.

The 2.11.0 additions are `Float8_e8m0fnu`, packed
`Float4_e2m1fn_x2`, and `torch::stable::Tensor::layout()`.

## Autoload device extensions

Since 2.5.0, out-of-tree device integrations can register through the
`torch.backends` entry point and load automatically, eliminating a mandatory
manual import. An environment variable can disable autoloading when explicit
extension control is required.

## Target Intel GPUs

PyTorch 2.5.0 preview and nightly wheels expanded Intel GPU support to Data
Center GPU Max and client GPUs, including Core Ultra integrated Arc and
discrete Arc. Initial Windows support targeted client GPUs. Both eager ATen and
`torch.compile` gained broader Intel operator and workload coverage.

In 2.6.0, `torch-xpu` wheels no longer require separately installing and
activating development bundles. Windows release binaries cover `torch`,
`torchvision`, and `torchaudio`; hardware support includes Intel Arc B-Series.

In 2.7.0, Intel GPUs gained `torch.compile` on Windows 11, AOTInductor and
`torch.export` on Linux, full-graph PT2E post-training quantization pipelines,
and profiler support on Windows and Linux.

In 2.10.0, support expands to Core Ultra Series 3 with Arc Graphics on Windows
and Linux, FP8 basic operations and scaled matrix multiplication with
tensor-wise or channel-wise scaling, and complex ATen `MatMul`.

## Build XPU extensions and use XPUGraph

The C++ Extension API has supported custom Intel GPU operators implemented as
SYCL kernels on Linux since 2.8.0 and on Windows since 2.10.0.

The API-unstable XPUGraph facility in 2.11.0 captures a sequence of Intel GPU
operations and replays it, avoiding repeated Python and kernel-launch overhead.
XPU also adds AOTInductor standalone compilation and multi-architecture kernel
paths, memory-history and snapshot APIs, and
`torch.accelerator.get_device_capability()` support.

Use XCCL for Intel distributed training as described in
[distributed-and-checkpointing.md](distributed-and-checkpointing.md#select-xccl-for-intel-gpus).

## Compile quantized workloads

On recent Intel CPUs, Inductor 2.8.0 can recognize quantized GEMM patterns under
`torch.compile` and lower them to native max-autotuned kernels. Supported
configurations include A16W8, DA8W8, and A16W4.

TorchAO 2.8.0 supports A16W4 weight-only LLM inference on Intel GPUs with BF16
or FP16 activations. Choose rounding-to-nearest (RTN) or automatic weight
quantization (AWQ).

## Target ROCm

PyTorch 2.8.0 adds functional gfx950 support on ROCm 7. Inductor and
AOTInductor's Composable Kernel backend provide max-autotune templates for
`matmul`, `addmm`, `conv2d`, `bmm`, and `_scaled_mm`.

Release binaries move to ROCm 7.2 in 2.11.0. Build with `TORCH_USE_HIP_DSA` to
enable device-side assertions. ROCm exposes more clock, memory-clock, bus-width,
and per-block memory properties and broadens attention, grouped matrix
multiplication, triangular solve, and MIOpen CTC-loss coverage on newer GPUs.

ROCm hipify v2 no longer applies the old Caffe2-style CUDA-to-HIP class
renaming; it renames only CUDA Runtime APIs. The `*MasqueradingAsCUDA` classes
remain deprecated compatibility shells. Extensions directly including those
headers or calling those APIs may need source changes.

MIOpen channels-last suggestions are opt-in again. Enable general-operation and
batch-normalization suggestions separately:

```sh
PYTORCH_MIOPEN_SUGGEST_NHWC=1 \
PYTORCH_MIOPEN_SUGGEST_NHWC_BATCHNORM=1 python app.py
```

## Target MPS

MPS in 2.11.0 adds Metal 4 support and reports asynchronous GPU failures when
execution synchronizes. Synchronize to surface a deferred error at a controlled
point:

```python
x = torch.rand(10, 1, 10, device="mps")
y = x[:, [1]]
torch.mps.synchronize()  # raises the deferred out-of-bounds error
```

Operator coverage adds more distribution functions, `erfcx`, every
`grid_sampler_2d` mode, `index_fill` backward, and integer or complex `baddbmm`
and `addbmm`.

## Interoperate with native streams

`torch.Stream.native_handle` in 2.11.0 exposes the backend-specific opaque
handle, such as `cudaStream_t` on CUDA or `sycl::queue*` on XPU, for integration
with third-party libraries:

```python
stream = torch.accelerator.current_stream()
handle = stream.native_handle
```

## Control autograd storage

In 2.11.0, a custom `torch.autograd.Function` can set
`clear_saved_tensors_on_access` to release saved tensors automatically after
access. Use it to shorten the lifetime of storage needed only during backward.

## Use sparse complex views

`torch.view_as_real()` and `torch.view_as_complex()` accept sparse tensors as of
2.11.0.

## Bound profiler post-processing

The 2.11.0 memory profiler adds `skip_actions` to filter events. The profiler
adds `post_process_timeout_s` so post-processing cannot indefinitely block the
next execution.
