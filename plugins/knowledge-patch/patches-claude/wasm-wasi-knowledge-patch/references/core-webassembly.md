# Core WebAssembly Standard and Semantics

Use this reference for Core Wasm modules, instructions, text format, and web
embedding behavior. Source batch attributions are `wasm-2.0` and `wasm-3.0`.

## The evergreen standard model

WebAssembly 2.0 reached W3C Candidate Recommendation in December 2024 after
the language specification was completed in early 2022. Starting with 2.0,
the Candidate Recommendation is updated in place as an evergreen standard.
The GitHub-hosted specification carries the newest fixes and formats.

Release 3.0 became the live standard. It completes memory64, multi-memory,
garbage collection, typed references, tail calls, native exception handling,
relaxed SIMD, a deterministic profile, and text annotations. The JavaScript
embedding also adds string builtins.

## Capabilities standardized by WebAssembly 2.0

WebAssembly 2.0 remains fully backward compatible while standardizing:

- 128-bit SIMD;
- bulk memory and table operations;
- multi-value results and block inputs;
- first-class function and external references with multiple typed tables;
- non-trapping float-to-integer conversions; and
- sign-extension instructions.

## 64-bit memories and tables

A memory or table may use `i64` instead of `i32` as its address type. This
expands the theoretical address space from 4 GiB to 16 EiB. Web embeddings
still limit a 64-bit memory to 16 GiB.

## Multiple memories

One module may define or import multiple memories and access them directly,
including copying data between memories. Multi-memory removes the former
limitation faced by module-merging tools and permits intentionally separate
address spaces.

## Native exception dispatch

Exception tags declare payload data. Handler blocks use dispatch lists made of
tag/label pairs or catch-all labels to select where execution continues after
a throw. This gives Wasm portable in-module exception handling without an
escape to the host.

## Deterministic execution profile

The deterministic profile defines behavior for instructions whose ordinary
semantics permit multiple results. It currently covers floating-point NaN
generation and relaxed SIMD edge cases.

Reproducibility applies between platforms that choose to implement the
profile. Outside it, relaxed SIMD may select any outcome allowed by the base
semantics.

## Custom text annotations

The text format supports generic annotations that implementations may ignore,
analogous to binary custom sections. Core Wasm assigns them no meaning, so a
downstream standard can define concrete annotations.

## JavaScript string builtins

The JavaScript API provides an importable primitive library. A Wasm module can
use it to access and manipulate JavaScript strings passed as external
references.
