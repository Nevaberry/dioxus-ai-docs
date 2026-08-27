# Build, Linking, and Platforms

## Cgo, linker output, and executable analysis

### Passing linker flags through cgo (`1.23.0`)

`cmd/cgo` accepts `-ldflags` for C-linker arguments. The `go` command uses it
automatically, preventing very large `CGO_LDFLAGS` values from overflowing the
process argument list.

### Immediate ELF symbol binding (`1.23.0`)

Linker flag `-bindnow` enables immediate function binding for dynamically
linked ELF executables, including PIE binaries.

```sh
go build -ldflags=-bindnow ./...
```

### Cgo call-contract annotations (`1.24.0`)

`#cgo noescape f` promises that pointers passed to C function `f` do not
escape, and `#cgo nocallback f` promises it never calls back into Go. These
enable cheaper calls but must reflect reality. Receiver methods whose type is
cgo-generated are rejected even when an alias hides that receiver type.

### Native build IDs by default (`1.24.0`)

The linker emits a GNU build ID on ELF and a UUID on Mach-O, derived from the Go
build ID. Pass `-B none` to suppress it or `-B 0xNNNN` to supply hexadecimal
bytes.

### AddressSanitizer leak detection (`1.25.0`)

Programs built with `go build -asan` perform leak detection at process exit by
default. Set `ASAN_OPTIONS=detect_leaks=0` while running to disable reports.

### DWARF 5 debug information (`1.25.0`)

The compiler and linker emit DWARF 5 by default.
`GOEXPERIMENT=nodwarf5` temporarily restores the prior format for incompatible
tools.

### Linker capabilities and executable layout (`1.26.0`)

On `windows/arm64`, cgo programs may request internal linking with
`-ldflags=-linkmode=internal`. Executable analyzers and linker scripts must
handle the new `.go.module` section, a relocation-free `.gopclntab` whose
`pcHeader` text address is zero, moved funcdata and findfunctab data, removal of
`.gosymtab`, and address-sorted internally linked ELF sections.

### macOS linker version controls (`1.27.0`)

For macOS targets, linker flags `-macos` and `-macsdk` set the OS and SDK
versions recorded in `LC_BUILD_VERSION`.

## Architecture profiles and toolchain floors

### Architecture target profiles (`1.23.0`)

`GOARM64` selects `v8.0` through `v8.9` or `v9.0` through `v9.5`, optionally
followed by `,lse` or `,crypto`; it defaults to `v8.0`. `GORISCV64` selects
`rva20u64` or `rva22u64` and defaults to `rva20u64`.

```sh
GOOS=linux GOARCH=arm64 GOARM64=v8.2,lse go build ./...
GOOS=linux GOARCH=riscv64 GORISCV64=rva22u64 go build ./...
```

### Toolchain and platform floors (`1.24.0`)

Bootstrapping the 1.24 toolchain requires Go 1.22.6 or later. Linux targets
require kernel 3.2 or later. This is the final release supporting macOS 11, and
the 32-bit `windows/arm` port is marked broken.

### Architecture and port changes (`1.25.0`)

Go 1.25 requires macOS 12 and is the final release supporting `windows/arm`.
At `GOAMD64=v3` or higher, fused operations may change floating-point results;
`float64(a*b)+c` prevents fusion. `linux/loong64` gains race, cgo traceback, and
internal-link support. RISC-V gains plugin support and
`GORISCV64=rva23u64`.

### Bootstrap requirement (`1.26.0`)

Building the 1.26 toolchain from source requires Go 1.24.6 or later.

### Port and platform transitions (`1.26.0`)

Go 1.26 is the final release for macOS 12 and the ELFv1 ABI on
`linux/ppc64`. `freebsd/riscv64` is broken. `linux/riscv64` gains race-detector
support, and s390x passes function arguments and results in registers.
WebAssembly requires sign-extension and non-trapping float-conversion
instructions; `GOWASM` settings `signext` and `satconv` are ignored.

### Linux PowerPC64 ELFv2 transition (`1.27.0`)

`linux/ppc64` emits ELFv2 binaries and requires kernel support equivalent to
Linux 3.13, including the RHEL 7 backport. Cgo, PIE, and external linking are
supported but require an ELFv2-compatible libc and every linked or loaded
library to use ELFv2.

## WebAssembly and WASI

### WASI runner requirement (`1.23.0`)

`GOROOT/misc/wasm/go_wasip1_wasm_exec` requires Wasmtime 14.0.0 or newer.

### Exportable WASI reactors (`1.24.0`)

For `GOOS=wasip1 GOARCH=wasm`, `-buildmode=c-shared` builds a reactor or library
rather than a command. `//go:wasmexport` exports Go functions to the host. Wasm
imports and exports accept `bool`, `string`, `uintptr`, and permitted pointer
types in addition to numeric types and `unsafe.Pointer`.

## SIMD and secret handling experiments

### Experimental architecture-specific SIMD (`1.26.0`)

`GOEXPERIMENT=simd` exposes unstable, non-portable `simd/archsimd` on amd64,
with 128-, 256-, and 512-bit vector types and architecture-specific operations.
It is distinct from portable SIMD.

### Experimental secret erasure (`1.26.0`)

`GOEXPERIMENT=runtimesecret` exposes `runtime/secret` for erasing
secret-bearing temporaries from registers, stacks, and new heap allocations.
The initial implementation supports only Linux amd64 and arm64.

### Portable SIMD experiment (`1.27.0`)

With `GOEXPERIMENT=simd`, `simd` supplies vector-size-agnostic operations on
every architecture.

### Expanded architecture-specific SIMD (`1.27.0`)

`simd/archsimd` is revised on amd64 and adds 128-bit Neon on arm64 and 128-bit
SIMD on WebAssembly.
