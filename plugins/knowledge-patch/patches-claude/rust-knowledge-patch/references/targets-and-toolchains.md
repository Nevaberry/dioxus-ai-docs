# Targets, Linkers, and Toolchains

## Host and target selection

`rustc --print host-tuple` prints the host target tuple from `1.84.0`; “tuple”
is the preferred term over “triple.” Cargo `--target host-tuple` and
`build.target = "host-tuple"` provide a portable explicit-host build mode from
`1.91.0`.

Custom JSON target specifications require nightly again from `1.95.0`: invoke
rustc with `-Z unstable-options`, or use Cargo's `-Z json-target-spec`. Stable
toolchains were not able to build `core` for those custom targets.

The shorthand `-O` means `-C opt-level=3` from `1.86.0`, rather than level 2.

## Linker and symbol behavior

### LLD on Linux x86-64

`x86_64-unknown-linux-gnu` uses bundled `rust-lld` rather than system BFD by
default from `1.90.0`. For a confirmed BFD-specific linker script or link
argument requirement, disable the feature:

```toml
# .cargo/config.toml
[target.x86_64-unknown-linux-gnu]
rustflags = ["-Clinker-features=-lld"]
```

`-C linker-features` accepts `+`/`-` feature names, not a linker path.

### Linker diagnostics

Successful-link stderr is no longer discarded in `1.97.0`. The
`linker_messages` warn-by-default lint reports it after filtering known false
positives. This lint is outside the normal `warnings` group, so neither
`-Dwarnings` nor Cargo `build.warnings = "deny"` escalates it. Silence it per
package if necessary:

```toml
[lints.rust]
linker_messages = "allow"
```

### Rust symbol mangling

Stable rustc defaults to `-Csymbol-mangling-version=v0` from `1.97.0`.
The legacy Itanium-style Rust scheme is nightly-only and scheduled for removal.
V0 symbols encode actual generic arguments rather than only a hash, so older
debuggers, profilers, demanglers, and backtrace-text expectations may need an
update.

### Unwind tables with aborting panic

Linux `-Cpanic=abort` builds emit unwind tables from `1.92.0`, restoring
backtraces without `-Cforce-unwind-tables=yes` at the cost of binary size. Use
`-Cforce-unwind-tables=no` to restore the earlier size behavior.

### Path-remapping scope

rustc `--remap-path-scope` (`1.95.0`) restricts
`--remap-path-prefix` to comma-separated scopes such as `macro`,
`diagnostics`, `debuginfo`, `object`, or `all`. The default remains remapping
everything. Rustdoc stabilizes `--remap-path-prefix` and `--emit` in `1.97.0`.

## WebAssembly and WASI

### Target changes

`wasm32-wasi` is removed in `1.84.0`; use `wasm32-wasip1`.
The new Tier 2 `wasm32v1-none` target restricts bare-metal Wasm to the
WebAssembly 1.0/MVP feature set, unlike `wasm32-unknown-unknown`, which assumes
newer features. The `multivalue`, `reference-types`, and `tail-call` target
features are stable.

### C ABI transition

`wasm32-unknown-unknown` adopts the standards-compliant C ABI in `1.89.0`.
Objects built with the older convention are silently ABI-incompatible; rebuild
all objects on both sides rather than mixing them.

The earlier `wasm_c_abi` future-compatibility warning becomes a hard error in
`1.86.0`; affected projects need `wasm-bindgen` 0.2.89 or newer.

### Undefined symbols and explicit imports

Wasm targets stop passing `--allow-undefined` to the linker in `1.96.0`.
Undefined symbols now fail rather than becoming imports from the `env` module.
Restore the old policy intentionally with
`RUSTFLAGS=-Clink-arg=--allow-undefined`, or declare the import with
`#[link(wasm_import_module = "env")]`.

`1.91.1` fixes a cross-crate regression where identical symbol names imported
from two Wasm modules could cause an import-module mismatch or silently call
the wrong import.

### Wasm platform point fixes

`1.93.1` fixes file-descriptor leaks on `wasm32-wasip2`.
`1.94.1` fixes `std::thread::spawn` on `wasm32-wasip1-threads`.

Emscripten `panic=unwind` uses the Wasm exception ABI from `1.93.0`; C/C++
objects linked into such a build require `-fwasm-exceptions`.

## Apple platforms

`x86_64-apple-darwin` is last Tier 1 in `1.89.0` and is Tier 2 with host tools
from `1.90.0`. Rustup still distributes rustc and Cargo, but the test suite is
not guaranteed to pass. Account for this when promising Intel-Mac support or
selecting CI runners.

From `1.91.0`, rustc always gives `cc` the Apple SDK root through `SDKROOT`.
This fixes builds under Xcode but stops implicitly finding libraries in
`/usr/local/lib`; a dependent crate must emit the search path itself:

```rust
// build.rs
println!("cargo::rustc-link-search=/usr/local/lib");
```

`target_env = "macabi"` and `target_env = "sim"` replace the corresponding
`target_abi` cfg values for Mac Catalyst and simulator targets.

The aarch64 tvOS, watchOS, and visionOS targets, including simulators, become
Tier 2 in `1.95.0`.

## Windows targets and behavior

`i686-*` hard-float targets require SSE2 from `1.86.0`; use an `i586` target for
pre-SSE2 hardware. `i586-pc-windows-msvc` is removed in `1.87.0`; migrate to
`i686-pc-windows-msvc`.

Std stops linking `advapi32` on Windows except win7 in `1.87.0`; native
dependencies that relied on that transitive link must link it themselves.

`aarch64-pc-windows-msvc` becomes Tier 1 in `1.91.0`.
`aarch64-pc-windows-gnullvm` and `x86_64-pc-windows-gnullvm` become Tier 2 with
host tools.

## Linux, musl, and Unix platforms

Tier 3 musl targets for powerpc, s390x, riscv32gc, mips64, and thumbv7neon link
dynamically by default from `1.90.0`.

All `*-linux-musl` targets bundle musl 1.2.5 from `1.93.0`, replacing 1.2.3 on
several major targets. This fixes static-binary DNS behavior for large records
and recursive resolvers. Because musl 1.2.4 removed legacy symbols,
dependencies need `libc` 0.2.146 or newer.

`powerpc64-unknown-linux-musl` becomes Tier 2 with host tools in `1.95.0`.

## Embedded and architecture-specific changes

- `core::ffi::c_char` changes signedness on many Tier 2/3 embedded Arm and
  RISC-V targets in `1.85.0` to match their C compilers. `libc` 0.2.169 or
  newer matches it.
- Enabling `neon` on `aarch64-unknown-none-softfloat` warns from `1.89.0`.
- AVX-512, x86 `sha512`, `sm3`, `sm4`, `kl`, and `widekl`, plus LoongArch
  features, stabilize in `1.89.0`.
- x86 `avx512fp16`, most AArch64 NEON fp16 intrinsics, and 29 RISC-V target
  features stabilize in `1.94.0`. `riscv64im-unknown-none-elf` is Tier 3.
- Inline assembly stabilizes on PowerPC/PowerPC64 in `1.95.0` and supports s390x
  vector registers from `1.96.0`.
- `-Csoft-float` is removed in `1.96.0`.
- AVR `c_double` becomes `f32` in `1.96.0` to match C.

## ABI validation and target-dependent rejection

Declaring a function with an ABI unsupported by the current target is a hard
error from `1.84.0`. From `1.90.0`, unsupported ABI strings are rejected in all
positions, including function-pointer types inside trait impls.

Using a vector type in a non-Rust ABI without its required target feature is a
hard error from `1.88.0`.

`i128` and `u128` in `extern "C"` match C `__int128` where it exists from
`1.89.0`, but do not match `_BitInt(128)` on x86-64. AVR's `c_double` change is
described above.

## Compiler build requirements and backend updates

- Building rustc from source requires LLVM 19 or newer in `1.88.0`.
- `1.92.0` raises the external LLVM requirement to 20 or newer.
- `1.96.0` requires external LLVM 21 or newer.
- The bundled compiler backend updates to LLVM 22 in `1.95.0`.

`1.96.1` fixes a miscompilation in a MIR optimization.

## Toolchain-sensitive layout and diagnostics

Raw-pointer `Debug` output includes metadata from `1.87.0`; profiler or snapshot
expectations may change. Rust diagnostic paths preserve original relative-ness
and path-prefix remapping from `1.94.0`, so downstream diagnostics for path
dependencies and workspace members may become relative. Parsers of compiler
output must allow that form.

The layouts of types without explicit representation are not promises. The
layout algorithm for representation-unspecified enums changes again in
`1.97.0`.
