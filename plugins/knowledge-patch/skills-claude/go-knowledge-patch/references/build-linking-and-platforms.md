# Build, Linking, and Platforms

## Cgo and linker controls

### C linker arguments and binding (1.23.0)

`cmd/cgo` accepts `-ldflags` for C-linker arguments. The `go` command uses it
automatically, avoiding process argument-list overflow from very large
`CGO_LDFLAGS`.

For dynamically linked ELF executables, including PIE, `-bindnow` enables
immediate function binding:

```sh
go build -ldflags=-bindnow ./...
```

### Cgo call contracts (1.24.0)

`#cgo noescape f` promises that pointers passed to C function `f` do not
escape; `#cgo nocallback f` promises it never calls back into Go. These enable
cheaper calls but must describe the C implementation exactly. Receiver methods
whose receiver is a cgo-generated type are rejected even if an alias hides it.

### Native build identifiers (1.24.0)

The linker emits a GNU build ID on ELF and a UUID on Mach-O by default, derived
from the Go build ID. Use `-B none` to suppress it or `-B 0xNNNN` for a supplied
hexadecimal value.

### DWARF 5 by default (1.25.0)

The compiler and linker emit DWARF 5. Use `GOEXPERIMENT=nodwarf5` only as a
temporary compatibility measure for tooling that cannot yet consume it.

### Executable layout changes (1.26.0)

`windows/arm64` cgo programs may request internal linking with
`-ldflags=-linkmode=internal`. Binary analyzers and linker scripts must handle:

- A new `.go.module` section.
- Relocation-free `.gopclntab` with a zero text address in `pcHeader`.
- Moved funcdata and findfunctab data.
- Removal of `.gosymtab`.
- Address-sorted sections in internally linked ELF binaries.

### macOS linker metadata (1.27.0)

The linker accepts `-macos` and `-macsdk` to select OS and SDK versions recorded
in `LC_BUILD_VERSION`.

## Architecture feature profiles and experiments

### ARM64 and RISC-V targets (1.23.0)

`GOARM64` accepts `v8.0` through `v8.9` and `v9.0` through `v9.5`, optionally
with `,lse` or `,crypto`; its default is `v8.0`. `GORISCV64` accepts
`rva20u64` or `rva22u64` and defaults to `rva20u64`.

```sh
GOOS=linux GOARCH=arm64 GOARM64=v8.2,lse go build ./...
GOOS=linux GOARCH=riscv64 GORISCV64=rva22u64 go build ./...
```

### SIMD evolution (1.26.0, 1.27.0)

`GOEXPERIMENT=simd` initially exposed unstable, non-portable
`simd/archsimd` on amd64 with 128-, 256-, and 512-bit vector types. It now also
exposes vector-size-agnostic operations through portable `simd` on every
architecture. `simd/archsimd` was revised on amd64 and adds 128-bit Neon on
arm64 and 128-bit SIMD on WebAssembly. Keep architecture-specific code behind
feature and platform checks; the experiment is not a stable API contract.

## WASI and WebAssembly

### Runner and reactor requirements (1.23.0, 1.24.0)

`GOROOT/misc/wasm/go_wasip1_wasm_exec` requires Wasmtime 14.0.0 or newer.

For `GOOS=wasip1 GOARCH=wasm`, `-buildmode=c-shared` creates an exportable
reactor/library. `//go:wasmexport` exports functions to the host. Imports and
exports accept `bool`, `string`, `uintptr`, permitted pointer types, numeric
types, and `unsafe.Pointer`.

### WebAssembly instruction floor (1.26.0)

WebAssembly targets require sign-extension and non-trapping float-conversion
instructions. `GOWASM=signext` and `GOWASM=satconv` are ignored because those
features can no longer be disabled.

## Toolchain and operating-system floors

### Bootstrap and host requirements (1.24.0, 1.26.0)

Bootstrapping Go 1.24 requires Go 1.22.6 or later. Linux targets require kernel
3.2 or later. Go 1.24 was the final release for macOS 11 and marked
`windows/arm` broken.

Building the Go 1.26 toolchain from source requires Go 1.24.6 or later.

### Architecture and port transitions (1.25.0, 1.26.0)

Go 1.25 requires macOS 12 and is the final release with `windows/arm`. At
`GOAMD64=v3` or higher, fused operations can change floating-point results;
`float64(a*b)+c` prevents fusion. `linux/loong64` adds race, cgo traceback, and
internal-link support. RISC-V adds plugins and the `rva23u64` profile.

Go 1.26 is the last release for macOS 12 and the ELFv1 ABI on `linux/ppc64`.
`freebsd/riscv64` is broken; `linux/riscv64` adds race-detector support; s390x
passes function arguments and results in registers.

### Linux PowerPC64 ELFv2 (1.27.0)

`linux/ppc64` emits ELFv2 and requires Linux 3.13-equivalent kernel support,
including the RHEL 7 backport. Cgo, PIE, and external linking are newly
supported, but require an ELFv2-compatible libc and every other linked or
loaded library to use the compatible ABI.
