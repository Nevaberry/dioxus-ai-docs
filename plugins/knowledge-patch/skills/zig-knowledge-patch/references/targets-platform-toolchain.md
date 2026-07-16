# Targets, platform, and toolchain

## Target triples

Target triples were corrected and expanded in 0.14.0:

- Windows ARM is `thumb-windows-gnu`, not `arm-windows-gnu`.
- Big-endian Windows triples were removed.
- MIPS and PowerPC hard-float musl names end in `musleabihf`.
- MIPS64 musl uses `muslabi64`.
- Thumb, soft-float MIPS/PowerPC, MIPS n32, and x86-64 x32 variants were added.

## Supported OS floors

As of 0.15.1, the standard library—and therefore the compiler—requires at least:

| OS | Minimum |
|---|---|
| Linux | 5.10 |
| macOS | 13 |
| Windows | 10 |
| FreeBSD | 14.0 |
| NetBSD | 10.1 |
| OpenBSD | 7.6 |
| DragonFly BSD | 6.0 |
| Solaris | 11 |

## Calling conventions and stack alignment

In 0.14.0, `std.builtin.CallingConvention` became a tagged union with
target-specific lowercase tags such as `.x86_64_sysv` and payload options such as
`incoming_stack_alignment`. `.c` is a declaration that selects the current
target's C convention.

`@setAlignStack` was removed. Express incoming stack alignment in the calling
convention instead:

```zig
export fn callback() callconv(.withStackAlign(.c, 4)) void {}
```

## C interoperability and sanitization

Since 0.14.0, C code in Debug builds gets Zig's UBSan runtime by default, with
Zig-style panics and traces. Override runtime detection with `-fubsan-rt` or
`-fno-ubsan-rt`.

In 0.15.1, C undefined-behavior sanitization has full and trap modes:

- `-fsanitize-c=full` links the runtime; the old `-fsanitize-c` means `full`.
- `-fsanitize-c=trap` uses smaller trap-based instrumentation.
- Build configuration uses `?std.zig.SanitizeC`; replace booleans with `.full`
  and `.off`.
- `zig cc` accepts `-fsanitize-trap=undefined`.

## Backends and code generation

The self-hosted x86-64 backend became the Debug default in 0.15.1 except on
NetBSD, OpenBSD, and Windows. Force LLVM with `-fllvm` or `.use_llvm = true` on a
compile step when backend behavior or code quality requires it.

LLVM SPIR-V is selectable in 0.15.1: the bundled LLVM 20 toolchain emits SPIR-V
with `-fllvm`; Zig's self-hosted SPIR-V backend remains the default.

## Cross-libc and linker support

Zig 0.15.1 can dynamically cross-link against FreeBSD 14+ and NetBSD 10.1+ libc
using bundled headers and stubs. glibc 2.42 is available as a cross target. Native
glibc may be linked statically, while cross-provided glibc remains dynamic-only.
`zig cc` now respects `-static` and `-dynamic`, including dynamic cross-compiled
musl.
