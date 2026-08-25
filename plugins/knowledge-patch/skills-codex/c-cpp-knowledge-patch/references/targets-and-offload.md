# Targets and Offload

Use this reference for architecture flags, platform ABI defaults, target retirement, GPU builds, OpenMP, OpenACC, OpenCL, and WebAssembly.

## X86 and vector-width changes

Clang 20 (`clang-20.1`) makes `*mmintrin.h` intrinsics on `__m64` use SSE2 and XMM registers. They no longer support MMX-only targets or `-mmmx -mno-sse2`; MMX inline assembly remains available. Direct users of the removed `__builtin_ia32_*` implementation builtins must use the header intrinsics.

Clang 21 (`clang-21.1`) makes `-mavx10.1` select a 512-bit maximum vector width because AVX10/256 was removed from the specification. The suffixed `-mavx10.x-256`, `-mavx10.x-512`, and `-m[no-]evex512` forms warn; use unsuffixed `-m[no-]avx10.x`.

Clang 22 (`clang-22.1`) removes the deprecated suffixed AVX10 and EVEX512 spellings, and intrinsic feature requests use unsuffixed `avx10.x`. It adds `-march=wildcatlake` and `-march=novalake`. clang-cl adds `/arch:AVX10.1`, `/arch:AVX10.2`, `/vlen`, `/vlen=256`, and `/vlen=512`; more SSE, AVX, and AVX512 intrinsics are constant-expression capable.

## Arm and AArch64

Clang 20 (`clang-20.1`) changes 32-bit Arm empty-struct argument passing to one-byte objects and makes SME function-type attributes participate in mangling. `-fno-omit-frame-pointer` now retains leaf-function frame pointers unless combined with `-momit-leaf-frame-pointer`.

Clang 21 (`clang-21.1`) makes the Arm assembler include FPU features implied by the selected CPU or architecture; remove them with explicit `+no...` choices. `+nosimd` now disables NEON and dependent features. AArch64 gains `-mexecute-only`/`-mpure-code` and `-msve-streaming-vector-bits=`. Replace deprecated pointer-authentication `__has_feature` probes with `__PTRAUTH__`.

AArch32 `-mtp` now defaults to `auto`, selecting `TPIDRURO` where available rather than calling `__aeabi_read_tp`; use `-mtp=soft` when that call is required. The general `-fbracket-depth` default rises from 256 to 2048.

Clang 22 (`clang-22.1`) changes AArch64 argument passing for explicitly over-aligned empty C++ classes. ACLE function multiversioning reaches release status with PAC/BTI-aware resolvers, overridable version priority, and unreachable-version diagnostics.

GCC 15 (`gcc-15.1`) deprecates AArch64 ILP32 (`-mabi=ilp32`). GCC 16 (`gcc-16.1`) deprecates PC-relative literal loads on AArch64; migrate assembly and low-level emitters away from them.

## GPU and accelerator targets

### CUDA and HIP driver behavior

Clang 20 (`clang-20.1`) makes the new CUDA offloading driver the default, including native `-fgpu-rdc` static-library support. Its RDC binary format is incompatible with NVIDIA's; `--no-offload-new-driver` selects the old path during migration.

The same release supports CUDA SDK 12.6 and `sm_100`, as well as AMDGPU `gfx950`.

Clang 22 (`clang-22.1`) treats C++17 deduction guides as implicit `__host__ __device__` declarations for CUDA and HIP. Duplicate implicit guides are suppressed and constraint-distinct guides remain. Explicit target-only guides are errors. Explicit host-plus-device guides still work but are deprecated because deduction guides do not participate in code generation.

### AMDGPU defaults

Clang 21 (`clang-21.1`) makes AMDGPU code object version 6 the default, requiring ROCm 6.3 at runtime. `[[clang::atomic(...)]]` can control AMDGPU atomic metadata per statement.

## OpenMP

### Syntax and runtime build changes

Clang 20 (`clang-20.1`) adds `omp assume`, `omp scope`, allocator and alignment modifiers on `allocate`, and combined masked-taskloop forms with optional `parallel` and `simd`.

DeviceRTL now uses generic IR. `LIBOMPTARGET_DEVICE_ARCHITECTURES` is unused, and runtime builds always cover AMDGPU and NVPTX.

### Assumptions, maps, and reductions

Clang 21 (`clang-21.1`) adds the `no_openmp_constructs` assumption clause, `self_maps` in map and requirement clauses, `omp stripe`, and private-variable reduction. The delimited form of `declare target` is deprecated.

### Mapping and allocator behavior

Clang 22 (`clang-22.1`) adds `need_device_addr` for `adjust_args`, `threadset`, `groupprivate`, `omp fuse`, omitted array-section lengths, new `uses_allocators` syntax, `variable-category`, `defaultmap(storage|private)`, and `default` on `target`.

OpenMP 6.0 permits an optional `nowait` argument. OpenMP 6.1 adds `fb_nullify` and `fb_preserve` fallbacks to `need_device_ptr`. `use_device_ptr` and `use_device_addr` preserve host addresses when lookup fails.

## OpenACC and OpenCL

Clang 21 (`clang-21.1`) provides OpenACC 3.4 semantic analysis and AST construction with `-fopenacc`. Partial lowering requires a Clang-IR-enabled compiler and `-fclangir`, but the ACC MLIR dialect cannot lower to LLVM IR, so executable OpenACC code generation is not available.

Clang 22 (`clang-22.1`) removes formerly unconditional OpenCL header-only feature macros. Extension and feature availability are centralized under `-cl-ext`. During offloading, `__has_builtin` considers only the active target, so host and device probes can differ.

## WebAssembly and COFF

Clang 20 (`clang-20.1`) makes WebAssembly's `generic` CPU enable bulk memory and non-trapping float-to-int conversion. clang-cl adds `/std:c++23preview`, and COFF targets add `#pragma clang section`.

Clang 22 (`clang-22.1`) deprecates `wasm32-wasi` in favor of `wasm32-wasip1`.

## RISC-V, LoongArch, Hexagon, and other targets

### Clang 20 target additions

Clang 20 (`clang-20.1`) adds AVX10.2, MOVRS, AMX-FP8/TRANSPOSE/MOVRS/AVX512/TF32, `-march/-mtune=diamondrapids`, Arm SVE2.1/SME2.1, AArch64 `fujitsu-monaka`, RISC-V `-mcmodel=large`, and RVV intrinsics 1.0.

`target_version` becomes limited to AArch64 and RISC-V. On AArch64, `target_version("default")` by itself creates a mangled default function version.

### Clang 21 target additions and defaults

Clang 21 (`clang-21.1`) moves Hexagon's default target from V60 to V68. LoongArch `_BitInt(N)` wider than 64 bits gets consistent 16-byte alignment, which can alter record layout.

New target support includes Cortex-A320, MIPS little-endian Windows, OHOS and `_Float16`/`__bf16` on LoongArch, RISC-V `-mtune=generic-ooo`, SiFive and Qualcomm interrupt attributes, and `__builtin_riscv_pause()`. AIX compiler runtimes move from `lib/clang/20/lib/aix` into per-target Clang 21 directories.

### Clang 22 target additions and defaults

Clang 22 (`clang-22.1`) enables linker relaxation by default on LoongArch64 and supports LoongArch32. RISC-V adds `-march=unset` to fall back to `-mcpu` or platform defaults, and sets `__GCC_CONSTRUCTIVE_SIZE` and `__GCC_DESTRUCTIVE_SIZE` to 64.

## Removed or restricted targets

Clang 20 (`clang-20.1`) removes `le32`, `le64`, and RenderScript target support. On SPARC Linux, `clang -m32` defaults to `-mcpu=v9`; pass `-mcpu=v8` for retained SPARC V8 environments.

GCC 15 (`gcc-15.1`) removes Nios II and Solaris 11.3, and it is the last release supporting the `reload` register allocator before GCC 16 removes it.
