# Core WebAssembly

## Evergreen standards

### WebAssembly 2.0 (`wasm-2.0`)

WebAssembly 2.0 reached W3C Candidate Recommendation in December 2024 after
the language specification was completed in early 2022. Candidate
Recommendation 2.0 is maintained in place as an evergreen standard; use the
GitHub-hosted specification for the latest fixes and formats.

The backward-compatible standard includes:

- 128-bit SIMD;
- bulk memory and table operations;
- multi-value results and block inputs;
- first-class function and external references with multiple typed tables;
- non-trapping float-to-integer conversions; and
- sign-extension instructions.

### WebAssembly 3.0 (`wasm-3.0`)

WebAssembly 3.0 is the live standard. It completes memory64, multi-memory,
garbage collection, typed references, tail calls, native exception handling,
relaxed SIMD, a deterministic profile, and text annotations. Its JavaScript
embedding also includes string builtins.

## Memory64 and 64-bit tables

Memories and tables may select `i64` instead of `i32` for their address type.
This increases the theoretical address space from 4 GiB to 16 EiB. The web
embedding imposes a smaller limit: a 64-bit memory is capped at 16 GiB.

Treat the address type and the embedding's size limit as separate constraints.

## Multiple memories

A module may define or import multiple memories, address them directly, and
copy data between them. This removes the former multi-memory constraint from
module-merging tools and permits intentionally separate address spaces.

## Native exception dispatch

Exception tags declare their payload. A handler block uses a dispatch list of
tag/label pairs, or catch-all labels, to choose where execution continues after
a throw. This keeps exception handling portable within Wasm rather than
requiring control to escape to the host.

## Deterministic execution profile

The deterministic profile specifies results where base semantics allow several
legal outcomes. It currently covers floating-point NaN generation and relaxed
SIMD edge cases.

Reproducibility is guaranteed only between platforms that choose to implement
the profile. Without it, ordinary relaxed SIMD may choose any specified legal
outcome.

## Custom text annotations

The text format accepts generic, optionally ignored annotations analogous to
binary custom sections. Core Wasm assigns no semantics to them; downstream
standards may define concrete meanings.

## JavaScript string builtins

The JavaScript API exposes an importable primitive library for directly
accessing and manipulating JavaScript strings passed to Wasm as external
references.
