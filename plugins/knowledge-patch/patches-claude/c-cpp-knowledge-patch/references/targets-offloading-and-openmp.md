# Targets, offloading, and OpenMP

Use this reference for architecture flags, target defaults, platform ABIs,
CUDA/HIP/OpenACC, WebAssembly, OpenMP syntax, and device-runtime builds.

## X86 and AVX10

### Clang 20 architecture support

Clang 20 adds AVX10.2, MOVRS, AMX-FP8, AMX-TRANSPOSE, AMX-MOVRS,
AMX-AVX512, and AMX-TF32 support, plus
`-march/-mtune=diamondrapids` (`clang-20.1`). Header intrinsics using `__m64`
now require SSE2 and XMM registers; MMX-only configurations must migrate or use
supported inline assembly.

### Clang 21 AVX10 spelling and width

Clang 21 makes `-mavx10.1` select a 512-bit maximum vector width because
AVX10/256 was removed from the specification (`clang-21.1`).
`-mavx10.x-256`, `-mavx10.x-512`, and `-m[no-]evex512` warn and are scheduled
for removal. Use `-m[no-]avx10.x`.

### Clang 22 AVX10 and clang-cl

Clang 22 removes the suffixed AVX10 and EVEX512 spellings; intrinsic feature
requests use unsuffixed `avx10.x` (`clang-22.1`). It adds
`-march=wildcatlake` and `-march=novalake`.

clang-cl adds `/arch:AVX10.1`, `/arch:AVX10.2`, `/vlen`, `/vlen=256`, and
`/vlen=512`. More SSE, AVX, and AVX512 intrinsics become constant-expression
capable. Keep the requested ISA, maximum vector width, and deployment CPU
aligned.

## Arm and AArch64

### Frame pointers and ABI details

In Clang 20, `-fno-omit-frame-pointer` retains frame pointers in leaf functions
unless combined with `-momit-leaf-frame-pointer` (`clang-20.1`). On 32-bit Arm,
empty C++ structs are passed as one-byte objects; `-fclang-abi-compat=19`
restores the former convention. SME function-type attributes participate in
mangling.

Clang 20 also adds Arm SVE2.1/SME2.1 and AArch64 `fujitsu-monaka` support
(`clang-20.1`).

### Feature removal and pointer authentication

Clang 21's Arm assembler includes FPU features implied by the selected CPU or
architecture (`clang-21.1`). Use explicit `+no...` modifiers to remove them;
`+nosimd` now actually disables NEON and dependent features.

AArch64 gains `-mexecute-only`/`-mpure-code` and
`-msve-streaming-vector-bits=`. Replace deprecated pointer-authentication
`__has_feature` checks with `__PTRAUTH__`.

Clang 21 also adds Cortex-A320 (`clang-21.1`).

### Newer AArch64 defaults and deprecations

GCC 16 deprecates PC-relative literal loads on AArch64 (`gcc-16.1`). Migrate
assembly or low-level code that emits them.

Clang 22 changes argument passing for empty C++ classes with large explicit
alignment (`clang-22.1`). ACLE function multiversioning reaches release status
with PAC/BTI-aware resolvers, overridable version priority, and diagnostics for
unreachable versions.

## RISC-V, LoongArch, Hexagon, and other CPU targets

### Clang 20 additions

Clang 20 adds `gfx950`, RISC-V `-mcmodel=large`, RVV intrinsics 1.0, and
architecture support relevant to CUDA SDK 12.6 and `sm_100` (`clang-20.1`).

`target_version` is limited to AArch64 and RISC-V. On AArch64,
`target_version("default")` by itself creates a mangled default function
version.

### Clang 21 target changes

AMDGPU defaults to code object version 6 in Clang 21, requiring ROCm 6.3 at
run time (`clang-21.1`). Hexagon's default moves from V60 to V68. LoongArch
`_BitInt(N)` values wider than 64 bits consistently use 16-byte alignment.

New support includes MIPS little-endian Windows targets, OHOS and
`_Float16`/`__bf16` on LoongArch, RISC-V `-mtune=generic-ooo`, SiFive and
Qualcomm interrupt attributes, and `__builtin_riscv_pause()`.

AIX compiler runtimes move from `lib/clang/20/lib/aix` to per-target Clang 21
directories. Update packaging and runtime discovery.

### Clang 22 target changes

LoongArch64 enables linker relaxation by default and LoongArch32 is supported
(`clang-22.1`). RISC-V adds `-march=unset`, which falls back to `-mcpu` or
platform defaults, and defines `__GCC_CONSTRUCTIVE_SIZE` and
`__GCC_DESTRUCTIVE_SIZE` as 64.

`wasm32-wasi` is deprecated in favor of `wasm32-wasip1`. Update target triples
in build, package, and deployment metadata.

## Platform driver defaults

### WebAssembly

Clang 20's WebAssembly `generic` CPU enables bulk memory and non-trapping
float-to-int conversion by default (`clang-20.1`). Pin features when an older
runtime cannot execute them. COFF targets also add `#pragma clang section`, and
clang-cl adds `/std:c++23preview`.

### AArch32 thread-pointer access

Clang 21 makes AArch32 `-mtp` default to `auto`, choosing `TPIDRURO` where
available instead of calling `__aeabi_read_tp` (`clang-21.1`). Use `-mtp=soft`
when the call is required. The default `-fbracket-depth` also rises from 256 to
2048.

## CUDA and HIP

### CUDA offloading driver

Clang 20 uses the new CUDA offloading driver by default (`clang-20.1`). It
supports native `-fgpu-rdc` static libraries, but its RDC binary format is
incompatible with NVIDIA's. Keep all device-link inputs in one compatible
format; `--no-offload-new-driver` restores the former Clang path temporarily.

The release adds CUDA SDK 12.6 and `sm_100` support.

### Device-side deduction guides

Clang 22 treats C++17 deduction guides for CUDA/HIP as implicit
`__host__ __device__` declarations (`clang-22.1`). Duplicate implicit guides
are suppressed while constraint-distinct guides remain.

Explicit target-only guides are errors. Explicit host-plus-device guides remain
accepted but are deprecated because deduction guides do not participate in
code generation.

### Target-aware feature queries

During offloading, Clang 22's `__has_builtin` considers only the currently
active target (`clang-22.1`). Do not cache a host result for device compilation.

OpenCL's formerly unconditional header-only feature macros are removed;
extension and feature availability is centralized and controlled through
`-cl-ext`.

## OpenACC

Clang 21's `-fopenacc` covers OpenACC 3.4 semantic analysis and AST construction
(`clang-21.1`). Partial lowering exists only in a Clang-IR-enabled compiler with
`-fclangir`; the ACC MLIR dialect cannot lower to LLVM IR. Frontend acceptance
therefore does not provide executable OpenACC code generation.

## OpenMP

### Clang 20 syntax and runtime construction

Clang 20 adds `omp assume`, `omp scope`, allocator and alignment modifiers on
`allocate`, and combined masked-taskloop forms with optional `parallel` and
`simd` (`clang-20.1`).

DeviceRTL now uses generic IR. `LIBOMPTARGET_DEVICE_ARCHITECTURES` is unused,
and runtime builds always cover AMDGPU and NVPTX. Remove build logic that
expects that variable to select runtime architectures.

### Clang 21 syntax

Clang 21 adds the `no_openmp_constructs` assumption clause, `self_maps` in map
and requirement clauses, `omp stripe`, and private-variable reduction
(`clang-21.1`). The delimited form of `declare target` is deprecated.

### Clang 22 syntax and mapping

Clang 22 adds (`clang-22.1`):

- `need_device_addr` for `adjust_args`;
- `threadset`, `groupprivate`, `omp fuse`, and omitted array-section lengths;
- the new `uses_allocators` syntax;
- `variable-category`;
- `defaultmap(storage|private)`; and
- `default` on `target`.

OpenMP 6.0 permits an optional `nowait` argument. OpenMP 6.1 adds `fb_nullify`
and `fb_preserve` fallbacks to `need_device_ptr`. `use_device_ptr` and
`use_device_addr` preserve host addresses when lookup fails. Test the exact
compiler/runtime pairing and map-failure behavior on the target device.
