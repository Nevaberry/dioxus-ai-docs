# Targets, Linkers, and Toolchains

## Host and compiler invocation

- Since 1.84.0, `rustc --print host-tuple` prints the compiler's host target directly.
- Since 1.86.0, `rustc -O` means `-C opt-level=3`, not level 2, matching Cargo's optimized profile.
- The nightly `-Zpolymorphize` flag was removed in 1.85.0.
- Stable rustc stopped accepting custom JSON targets in 1.95.0. Nightly requires `-Z unstable-options`; nightly Cargo's `-Z json-target-spec` forwards it.
- `-Csoft-float` was removed in 1.96.0.

## WebAssembly

### Target names and features

- The old `wasm32-wasi` target is gone as of 1.84.0; use `wasm32-wasip1`.
- `wasm32v1-none` became Tier 2 in 1.84.0, and `multivalue`, `reference-types`, and `tail-call` became stable WebAssembly target features.

### C ABI transition

`wasm32-unknown-unknown` adopted the standards-compliant C ABI in 1.89.0. Rebuild all components across an `extern "C"` boundary; do not mix old and new conventions. The earlier `wasm_c_abi` compatibility warning became a hard error in 1.86.0, and affected `wasm-bindgen` users need 0.2.89 or newer.

### Undefined imports

Since 1.96.0, WebAssembly linkers no longer receive `--allow-undefined`; unresolved symbols are errors rather than implicit imports from `"env"`. Declare intentional imports with `#[link(wasm_import_module = "env")]`, or deliberately restore the old linker option with `-C link-arg=--allow-undefined`.

### Emscripten

Since 1.93.0, Emscripten `panic=unwind` uses the Wasm exception ABI rather than the JavaScript exception ABI. Mixed Rust/C/C++ links need `-fwasm-exceptions`.

### Point-release repair

Rust 1.91.1 fixed possible mislinking when different crates imported the same Wasm symbol name from different modules; 1.91.0 could fail linking or exhibit undefined behavior.

## Linkers and native libraries

### Linux LLD default

`x86_64-unknown-linux-gnu` uses LLD by default since 1.90.0. For a verified incompatibility, opt out explicitly:

```toml
[target.x86_64-unknown-linux-gnu]
rustflags = ["-Clinker-features=-lld"]
```

### Apple native lookup

Since 1.91.0, rustc linking through `cc` always supplies the Apple SDK root and exports `SDKROOT`. `/usr/local/lib` may no longer be searched implicitly; an affected build script should emit `cargo::rustc-link-search=/usr/local/lib`.

### Windows native libraries

Except on Windows 7 targets, the standard library stopped linking `advapi32` transitively in 1.87.0. Native code needing it must link it explicitly.

## External LLVM and compiler builds

- Rust 1.88.0 requires LLVM 19 or newer for an external-LLVM compiler build.
- Rust 1.92.0 raises that minimum to LLVM 20.
- Rust 1.96.0 raises it to LLVM 21.
- Rust 1.88.0 also rejects a vector type in a non-Rust ABI unless the required target feature is enabled.
- Rust 1.97.1 backports an LLVM fix and disables a 1.97.0 IR change that increased exposure to an optimization miscompilation present since at least 1.87. Affected users on 1.87–1.97.0 should upgrade to 1.97.1.

## Platform baselines and target tiers

### Changes in 1.85.0

- `powerpc64le-unknown-linux-musl` is Tier 2 with host tools.
- `sparcv9-sun-solaris` and `x86_64-pc-solaris` require Solaris 11.4.
- `powerpc64-ibm-aix` defaults to the large code model.

### Changes in 1.86.0

- `i686-unknown-redox` is replaced by `i586-unknown-redox`.
- `i686-unknown-hurd-gnu` assumes Pentium 4.
- `i586-pc-windows-msvc` warns before removal in favor of `i686-pc-windows-msvc`.
- Disabling SSE2 on i686 32-bit x86 hard-float targets warns ahead of becoming an error; pre-SSE2 hardware should use an i586 target.
- New Tier 3 targets cover QNX 7.1 io-socket and QNX 8 (`aarch64-unknown-nto-qnx710_iosock`, `x86_64-pc-nto-qnx710_iosock`, `aarch64-unknown-nto-qnx800`, `x86_64-pc-nto-qnx800`), with QNX 8 limited to `no_std`.
- Other new Tier 3 targets: `x86_64-win7-windows-gnu`, `i686-win7-windows-gnu`, `amdgcn-amd-amdhsa`, `x86_64-pc-cygwin`, `mips-mti-none-elf`, `mipsel-mti-none-elf`, `m68k-unknown-none-elf`, `armv7a-nuttx-eabi`, `armv7a-nuttx-eabihf`, `aarch64-unknown-nuttx`, `thumbv7a-nuttx-eabi`, and `thumbv7a-nuttx-eabihf`.

### Changes in 1.88.0 and 1.89.0

- `i686-pc-windows-gnu` is Tier 2 as of 1.88.0.
- Rust 1.89.0 is expected to be the last Tier 1 release for `x86_64-apple-darwin`; Tier 2 with host tools retains distributed compiler/library builds but not the guarantee that automated tests pass.
- `loongarch32-unknown-none` and `loongarch32-unknown-none-softfloat` are Tier 3 in 1.89.0.

### Changes in 1.90.0 through 1.92.0

- `mips64-unknown-linux-muslabi64`, `powerpc64-unknown-linux-musl`, `powerpc-unknown-linux-musl`, `powerpc-unknown-linux-muslspe`, `riscv32gc-unknown-linux-musl`, `s390x-unknown-linux-musl`, and `thumbv7neon-unknown-linux-musleabihf` link dynamically by default from 1.90.0.
- In 1.91.0, use Apple `target_env = "macabi"` and `target_env = "sim"` rather than equivalent `target_abi` values.
- `aarch64-pc-windows-msvc` is Tier 1 from 1.91.0. AArch64/x86-64 Windows GNU and LLVM targets are Tier 2 with host tools but without `llvm-tools` or MSI installers.
- `File::lock` support on illumos, regressed in 1.91.0, is restored by 1.91.1.
- `mips64el-unknown-linux-muslabi64` links dynamically by default from 1.92.0.

### Changes in 1.93.0 and later

- All `*-linux-musl` targets ship musl 1.2.5 from 1.93.0, including the newer resolver. Removed legacy symbols require `libc` 0.2.146 or newer.
- Rust 1.94.0 recognizes 29 more RISC-V target features covering much of RVA22U64/RVA23U64 and adds Tier 3 `riscv64im-unknown-none-elf`.
- `powerpc64-unknown-linux-musl` is Tier 2 with host tools in 1.95.0. AArch64 Apple tvOS, watchOS, and visionOS device/simulator targets are also Tier 2.
- `riscv64gc-unknown-fuchsia` requires an RVA22 vector-capable baseline from 1.96.0.
- `nvptx64-nvidia-cuda` dropped older GPU architectures and instruction-set versions in 1.97.0; audit legacy CUDA targets.

## CPU features and debug information

- `-C dwarf-version` is stable since 1.88.0.
- Since 1.89.0, stable x86 supports AVX-512 plus `sha512`, `sm3`, `sm4`, `kl`, and `widekl`; LoongArch supports `f`, `d`, `frecipe`, `lasx`, `lbt`, `lsx`, and `lvz`.
- Since 1.94.0, AVX-512 FP16 intrinsics on x86 and NEON FP16 intrinsics on AArch64 are stable except where an operation directly requires unstable `f16`.
- Since 1.97.0, `cfg(target_has_atomic_primitive_alignment)` and target features `div32`, `lam-bh`, `lamcas`, `ld-seq-sa`, and `scq` are stable.

## Platform modules

`std::os::darwin` is public since 1.84.0 and provides shared Darwin-family platform interfaces.
