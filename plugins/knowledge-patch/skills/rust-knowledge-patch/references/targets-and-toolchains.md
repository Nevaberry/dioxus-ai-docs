# Targets, Linkers, and Toolchains

Use this reference when selecting a compilation target, upgrading low-level build infrastructure, diagnosing linker or ABI changes, or building the compiler itself.

## Host targeting and compiler defaults

### Query the host triple

`rustc --print host-tuple` prints the compiler's host target tuple from 1.84.0, avoiding parsing verbose version output. Cargo also accepts the portable `host-tuple` placeholder from 1.91.0.

### Optimization shorthand

`rustc -O` means `-C opt-level=3` from 1.86.0 rather than level 2, matching Cargo's default optimized profile.

### Jump tables

`-Cjump-tables=<bool>` is stable from 1.93.0 and replaces the nightly `-Zno-jump-tables` spelling.

```console
rustc -Cjump-tables=no main.rs
```

### Scoped path remapping

`rustc --remap-path-scope` is stable from 1.95.0 and controls where remapped paths affect the resulting binary.

### Custom JSON targets

Stable rustc no longer accepts custom JSON target specifications from 1.95.0. Direct nightly invocation requires `-Z unstable-options`; Cargo provides `-Z json-target-spec` to pass the compiler option. Workflows that also build `core` for a custom target already require nightly facilities.

## Linux GNU linking and symbols

### LLD default

`x86_64-unknown-linux-gnu` uses LLD by default from 1.90.0. Opt out only when a confirmed incompatibility requires the prior linker path:

```toml
[target.x86_64-unknown-linux-gnu]
rustflags = ["-Clinker-features=-lld"]
```

### Unwind tables for aborting builds

Linux `-C panic=abort` builds retain unwind tables by default from 1.92.0 so backtraces work. Use `-C force-unwind-tables=no` for an explicit size-oriented opt-out.

### v0 symbol mangling

Stable rustc emits Rust-specific v0-mangled symbols by default from 1.97.0 without `-Csymbol-mangling-version=v0`. Older debuggers and profilers may not demangle them, and backtrace spelling can change. Selecting the legacy scheme requires nightly and is planned for removal.

## WebAssembly

### WASI and bare targets

- `wasm32-wasi` was removed in 1.84.0; use `wasm32-wasip1`.
- `wasm32v1-none` became Tier 2 in 1.84.0.
- WebAssembly `multivalue`, `reference-types`, and `tail-call` target features are stable from 1.84.0.

### C ABI compatibility

On `wasm32-unknown-unknown`, C-ABI functions use a standards-compliant convention from 1.89.0. This is an ABI break: do not assume callers and callees compiled under the old and new conventions interoperate.

The earlier `wasm_c_abi` future-compatibility warning became a hard error in 1.86.0. `wasm-bindgen` must be version 0.2.89 or newer.

### Explicit undefined imports

Rust no longer passes `--allow-undefined` for WebAssembly links from 1.96.0, so unresolved symbols fail instead of implicitly becoming `env` imports. Declare an intentional import with `#[link(wasm_import_module = "env")]`. The old broad behavior can be restored explicitly with `RUSTFLAGS=-Clink-arg=--allow-undefined`.

### Import-module regression

Rust 1.91.0 could report `import module mismatch` or call the wrong function when different crates imported the same Wasm symbol name from different `#[link(wasm_import_module)]` modules. Upgrade to 1.91.1 or later.

### Emscripten exceptions

Emscripten `panic=unwind` uses the Wasm exception-handling ABI from 1.93.0 instead of the JavaScript exception convention. Compile linked C or C++ objects with `-fwasm-exceptions` so unwinding matches.

### WASI component regression

Rust 1.93.1 fixes file-descriptor leaks in the distributed `wasm32-wasip2` component. Independently built toolchains must verify their own Wasm dependencies.

## Musl targets

### Dynamic-link defaults

The following targets link dynamically by default from 1.90.0:

- `mips64-unknown-linux-muslabi64`
- `powerpc64-unknown-linux-musl`
- `powerpc-unknown-linux-musl`
- `powerpc-unknown-linux-muslspe`
- `riscv32gc-unknown-linux-musl`
- `s390x-unknown-linux-musl`
- `thumbv7neon-unknown-linux-musleabihf`

`mips64el-unknown-linux-muslabi64` follows with a dynamic-link default in 1.92.0.

### Bundled musl release

All `*-linux-musl` targets bundle musl 1.2.5 from 1.93.0. Static x86_64, AArch64, and little-endian PowerPC64 builds move from 1.2.3 and gain the newer DNS resolver. Legacy compatibility symbols were removed; affected projects need `libc` 0.2.146 or newer.

### Support tiers

- `powerpc64le-unknown-linux-musl` is Tier 2 with host tools from 1.85.0.
- `powerpc64-unknown-linux-musl` becomes Tier 2 with host tools in 1.95.0.

## Windows and 32-bit x86

### Target tiers and replacements

- `i586-pc-windows-msvc` warned ahead of its 1.87 removal in favor of `i686-pc-windows-msvc` (1.86.0).
- Disabling SSE2 on i686 32-bit x86 hard-float targets warned in 1.86.0 ahead of an error; use an i586 target for pre-SSE2 hardware.
- `i686-pc-windows-gnu` moved from Tier 1 to Tier 2 in 1.88.0. Rustup still distributes its compiler and standard-library artifacts, but the target receives less testing.
- `aarch64-pc-windows-msvc` is Tier 1 from 1.91.0.
- `aarch64-pc-windows-gnullvm` and `x86_64-pc-windows-gnullvm` are Tier 2 with host tools from 1.91.0, but lack LLVM tools and MSI installers.

### Calling convention and native libraries

- i686 targets pass SIMD arguments with SSE2 from 1.87.0, changing low-level calls.
- Except on Windows 7 targets, the standard library stopped linking `advapi32` in 1.87.0. Native libraries relying on that transitive dependency must link it directly.

### Windows 7 GNU targets

`x86_64-win7-windows-gnu` and `i686-win7-windows-gnu` were added as Tier 3 targets in 1.86.0.

## Apple targets and linking

### Support and frame pointers

- Rust 1.89.0 is the last release with `x86_64-apple-darwin` at Tier 1. Its planned Tier 2-with-host-tools status retains distributed compiler and standard-library artifacts without guaranteeing the full automated suite passes.
- Apple frame-pointer defaults became architecture-specific in 1.89.0.
- `aarch64-apple-{tvos,tvos-sim,watchos,watchos-sim,visionos,visionos-sim}` targets are Tier 2 from 1.95.0.

### SDK search behavior

When linking through `cc`, rustc always supplies the Apple SDK root and sets `SDKROOT` from 1.91.0. `/usr/local/lib` may therefore no longer be searched implicitly. An affected build script should emit:

```text
cargo::rustc-link-search=/usr/local/lib
```

## Other target baselines and tiers

### Solaris, AIX, Redox, and Hurd

- The Solaris baseline for `sparcv9-sun-solaris` and `x86_64-pc-solaris` is 11.4 from 1.85.0.
- `powerpc64-ibm-aix` uses large code addressing by default from 1.85.0.
- `i686-unknown-redox` was replaced by `i586-unknown-redox` in 1.86.0.
- `i686-unknown-hurd-gnu` assumes a Pentium 4 CPU from 1.86.0.

### QNX, bare-metal, and NuttX Tier 3 additions

Rust 1.86.0 adds:

- QNX 7.1 io-socket: `{aarch64-unknown,x86_64-pc}-nto-qnx710_iosock`
- QNX 8: `{aarch64-unknown,x86_64-pc}-nto-qnx800`, limited to `no_std`
- GPU and Unix-like: `amdgcn-amd-amdhsa`, `x86_64-pc-cygwin`
- Bare metal: `{mips,mipsel}-mti-none-elf`, `m68k-unknown-none-elf`
- NuttX: `armv7a-nuttx-{eabi,eabihf}`, `aarch64-unknown-nuttx`, `thumbv7a-nuttx-{eabi,eabihf}`

### LoongArch, RISC-V, and s390x

- LoongArch gains stable `f`, `d`, `frecipe`, `lasx`, `lbt`, `lsx`, and `lvz` features in 1.89.0. `loongarch32-unknown-none` and `loongarch32-unknown-none-softfloat` are new Tier 3 targets in that release.
- LoongArch32 inline assembly is stable from 1.91.0.
- `riscv64a23-unknown-linux-gnu` is Tier 2 without host tools from 1.93.0.
- Several s390x vector features and `is_s390x_feature_detected!` are stable from 1.93.0.
- Twenty-nine more RISC-V features, including much of RVA22U64 and RVA23U64, are stable from 1.94.0; `riscv64im-unknown-none-elf` is a new Tier 3 target.
- `riscv64gc-unknown-fuchsia` requires RVA22 plus vector support from 1.96.0.

### AArch64, Arm64EC, and soft float

- AArch64 Linux and Arm64EC Windows retain non-leaf frame pointers by default from 1.89.0.
- Enabling `neon` on `aarch64-unknown-none-softfloat` warns from 1.89.0 because mixing code with and without it is not properly supported.
- AArch64 soft-float JSON targets must set `rustc_abi` to `"softfloat"` from 1.96.0; `-Csoft-float` was removed.

## Architecture feature stabilization

### x86

- AVX-512 target features and intrinsics plus `kl`, `widekl`, `sha512`, `sm3`, and `sm4` are stable from 1.89.0.
- `sse4a` and `tbm` are stable from 1.91.0.
- x86 AVX-512 FP16 intrinsics are stable from 1.94.0 except those directly requiring the still-unstable `f16` type.

### AArch64 half precision

AArch64 NEON FP16 intrinsics are stable from 1.94.0 except intrinsics directly requiring the unstable `f16` type.

### Primitive-alignment cfg and newer features

`cfg(target_has_atomic_primitive_alignment)` and the `div32`, `lam-bh`, `lamcas`, `ld-seq-sa`, and `scq` target features are stable from 1.97.0. NVPTX no longer supports older architectures and instruction-set versions in that release; review the selected GPU baseline during an upgrade.

## PowerPC ABI

PowerPC64 code generation uses the ELF ABI version specified by the target from 1.95.0 instead of guessing, correcting OpenBSD output.

## External LLVM requirements

Building rustc against an external LLVM requires:

- LLVM 19 or newer for Rust 1.88.0;
- LLVM 20 or newer for Rust 1.92.0;
- LLVM 21 or newer for Rust 1.96.0.

Match the LLVM floor to the compiler release being built.

## Target cfg spelling

Use `target_env = "macabi"` and `target_env = "sim"` instead of corresponding `target_abi` predicates from 1.91.0.
