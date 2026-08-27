---
name: wasm-wasi-knowledge-patch
description: WebAssembly / WASI
version: "Wasm 3.0 / WASI 0.3.0"
license: MIT
metadata:
  author: Nevaberry
---


# WebAssembly and WASI Compatibility

Use this skill when a task involves:

- writing or reviewing WIT interfaces, packages, resources, or worlds;
- selecting core WebAssembly features or reasoning about current standard behavior;
- migrating a component from WASI 0.2 interfaces to native WASI async;
- implementing async stream, future, HTTP, filesystem, CLI, or socket bindings;
- checking whether a runtime or toolchain can consume newer WASI components.

Start by identifying the component's WIT package, imported world, target WASI
line, runtime, binding generator, and host language. Keep core WebAssembly,
the Component Model/WIT layer, WASI interfaces, and host embeddings distinct:
support in one layer does not establish support in all the others.

## Reference index

| Reference | Topics |
| --- | --- |
| [Core WebAssembly](references/core-webassembly.md) | Live standards, standardized proposals, memory64, multi-memory, exceptions, determinism, annotations, JavaScript strings |
| [WIT language](references/wit-language.md) | Identifiers, comments, results, floats, type rules, resources, imports, worlds, packages, maps, interface instances |
| [WASI async](references/wasi-async.md) | Streams, futures, ownership, scheduling, reads, writes, collapsed operations, language bindings |
| [WASI interfaces](references/wasi-interfaces.md) | 0.2 interoperation, I/O replacement, HTTP roles, sockets, filesystem, clocks, and CLI changes |
| [Toolchains](references/toolchains.md) | Initial runtime, binding-generator, registry, JavaScript, and Rust requirements |

## Breaking changes and migration decisions

### Treat WASI 0.3 as additive

Do not force a 0.2 component to migrate merely because the host supports 0.3.
Hosts may continue exposing 0.2, and a 0.3 runtime can polyfill 0.2 imports at
the host boundary. Migrate when the component needs composable cross-component
async or one of the reshaped interfaces.

### Replace readiness-oriented I/O

WASI 0.3 has no `wasi:io` package. Translate its resources by purpose:

| WASI 0.2 concept | Native async shape |
| --- | --- |
| `pollable` | `future<T>` |
| `input-stream` | `stream<u8>` |
| `output-stream` | caller passes `stream<u8>` into an operation |
| poll an operation | await its future |
| `subscribe()` | return a future from the operation |

Do not preserve `start-foo`/`finish-foo` pairs mechanically. Collapse each pair
and its `pollable` into one operation. Use `async func` when the host operation
can suspend; use plain `func` when the old split only enabled nonblocking
dispatch.

### Keep data and terminal status independent

Model a read as a data stream plus a terminal-result future:

```wit
read-via-stream: func(offset: filesize)
    -> tuple<stream<u8>, future<result<_, error-code>>>;
```

The terminal future resolves even if the caller samples or drops the stream.
Use the same shape for stdin, TCP receive, and directory listing operations.

For writes, reverse the direction: pass a byte stream to the host and await a
future that completes after consumption.

```wit
write-via-stream: func(data: stream<u8>)
    -> future<result<_, error-code>>;
```

Apply this shape to stdout, stderr, filesystem writes, and TCP sends.

### Transfer async handles; do not borrow them

Treat every `stream<T>` and `future<T>` as an owned Canonical ABI value.
Passing one across a component boundary transfers ownership to the callee.
Unlike a resource handle, an async handle cannot be borrowed. It may still be
forwarded across multiple component boundaries.

### Reshape HTTP roles

Represent HTTP with `request` and `response`; use `stream<u8>` bodies and a
future for trailers. Return a response directly from the handler:

```wit
handle: async func(request: request) -> result<response, error-code>;
```

Use the `service` world for a component that imports the client and exports the
incoming handler. Use `middleware` when it must also import a downstream
handler. Do not carry the 0.2 `proxy` world forward.

### Reshape socket capabilities

Do not thread a `network` resource through bind, connect, and name lookup.
Grant network access at the world level. Consolidate socket APIs around
`types` and `ip-name-lookup`, and model TCP listen results as
`stream<tcp-socket>` rather than a separate accept loop.

### Gate WASI 0.3.1 inputs

Before accepting a component that uses `implements` or `map<K, V>`, verify
that its runtime and toolchain support WASI 0.3.1 or later. `implements` allows
multiple distinctly named instances of one interface; `map<K, V>` replaces
the common `list<tuple<K, V>>` encoding for dynamic key-value data.

## WIT quick reference

### Names and comments

- Write identifiers as ASCII kebab-case. Each hyphen-delimited word must be
  entirely lowercase or entirely uppercase.
- Prefix a keyword used as a name with `%`.
- Use `///` or `/** ... */` to document the following item.
- Ordinary `/* ... */` comments may nest.

### Results and floats

- `result<T>` omits the error payload.
- `result<_, E>` omits the success payload.
- Bare `result` omits both payloads.
- Treat a WIT `f32` or `f64` NaN as one logical `nan`; do not rely on a NaN
  payload's bit pattern surviving an interface crossing.

### Types and resources

Do not add type parameters to records or variants. Only built-in generic types
such as `list<T>`, `option<T>`, and `result<T, E>` are parameterized.

A resource may declare at most one `constructor`. Ordinary methods receive an
implicit borrowed `self`; `static func` members have no `self`.
`borrow<resource>` loans a handle for the call only, while passing an owned
resource handle transfers responsibility for eventually destroying it.

### Imports, worlds, and packages

- Import interface types with `use interface-name.{type-name, ...}`. Braces
  are required even for one type, including across peer files in a package.
- A world may import or export whole interfaces or individual functions,
  declare an interface inline, and `include` another world.
- Name an external interface as `package/interface`; package resolution belongs
  to tooling.
- Use package IDs of the form `namespace:name` with optional `@semver`.
- A package may span peer `.wit` files in one directory. Only one file needs
  the package declaration; repeated declarations must match.

## Native async quick reference

Use `stream<T>` for incrementally produced ordered values, `future<T>` for one
later value, and `async func` for a call that may suspend. These are Canonical
ABI values, so they may be parameters, results, and forwarded values. Bindings
should expose the host language's normal async form.

The host runs one event loop for all composed components. Delivering a future
value schedules its awaiting task even after the future crosses component
boundaries. The producer can be the host, another component, or the same
component. The ABI reports completion rather than readiness; emulate an
`epoll`- or `kqueue`-style layer only when ported software requires it.

Support stackful and stackless bindings side by side. A Go binding may expose
synchronous-looking functions and blocking stream operations because the
runtime parks only the calling goroutine at the ABI boundary and resumes it
when the stream becomes ready.

## Core WebAssembly quick reference

- Treat the GitHub-hosted WebAssembly specification as the current evergreen
  text rather than assuming Candidate Recommendation snapshots are frozen.
- WebAssembly 2.0 remains backward compatible while standardizing SIMD, bulk
  memory/table operations, multi-value signatures, reference types and typed
  tables, non-trapping conversions, and sign extension.
- For WebAssembly 3.0, check runtime support before using memory64,
  multi-memory, garbage collection, typed references, tail calls, native
  exceptions, relaxed SIMD, deterministic execution, or text annotations.
- A memory64 declaration expands the theoretical address space, but the web
  embedding still caps a 64-bit memory at 16 GiB.
- The deterministic profile affects only implementations that choose it; do
  not assume ordinary relaxed SIMD produces identical results across platforms.

## Toolchain gate

For initial WASI 0.3 work, require Wasmtime 46+, `wit-bindgen` 0.46+ with its
`async` feature, and `wkg` 0.15+. Use jco's `preview3-shim` for JavaScript host
bindings. Check the Rust linker constraint before selecting stable Rust; the
initial toolchain guidance requires nightly because stable Rust's bundled
`wasm-component-ld` is too old for the 0.3 output from `wit-bindgen` 0.58.

## Review checklist

1. Confirm the target world and WASI line.
2. Separate core Wasm support from Component Model, WASI, and host API support.
3. Audit every resource, stream, and future for ownership transfer.
4. Check that read completion is observable without draining its stream.
5. Replace readiness and two-step APIs with completion-based operations.
6. Verify HTTP, socket, clocks, filesystem, and CLI interface names and roles.
7. Gate `implements` and `map<K, V>` on WASI 0.3.1-compatible tooling.
8. Verify runtime, binding-generator, registry, language, and linker support.
