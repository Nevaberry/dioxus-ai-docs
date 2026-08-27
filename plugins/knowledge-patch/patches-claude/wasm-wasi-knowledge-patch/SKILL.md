---
name: wasm-wasi-knowledge-patch
description: WebAssembly / WASI
version: "Wasm 3.0 / WASI 0.3.0"
license: MIT
metadata:
  author: Nevaberry
---


# WebAssembly and WASI

Use this skill when writing, reviewing, or migrating Core WebAssembly, WIT,
Component Model, or WASI code. Start with the compatibility notes below, then
open the reference file that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [WIT language and composition](references/wit-language.md) | Identifiers, comments, results, types, resources, imports, worlds, packages, maps, and interface instances |
| [Core WebAssembly](references/core-webassembly.md) | Live standards, standardized proposals, 64-bit and multiple memories, exceptions, determinism, annotations, and JavaScript strings |
| [WASI interface migration](references/wasi-interface-migration.md) | 0.2 interoperation, `wasi:io` replacement, stream-based I/O, HTTP, sockets, clocks, CLI, and toolchains |
| [Async Component Model](references/async-component-model.md) | Async WIT values, ownership, scheduling, language bindings, service, and middleware roles |

## Migration and compatibility first

### Treat WASI 0.3 as additive

Do not force every component to migrate from 0.2. Hosts may continue exposing
0.2, and a 0.3 runtime can polyfill 0.2 imports at the host boundary.

Migrate when the design needs composable async across component boundaries or
depends on reshaped 0.3 interfaces.

### Replace `wasi:io` concepts

There is no 0.3 release of `wasi:io`. Translate its resources as follows:

| WASI 0.2 concept | WASI 0.3 shape |
| --- | --- |
| `pollable` | `future<T>` |
| `input-stream` | `stream<u8>` |
| `output-stream` | A `stream<u8>` passed into an operation |
| Polling | Awaiting a future |
| `subscribe()` | Returning a future from the operation |

### Separate read data from completion

Model reads as a data stream plus an independent terminal-result future:

```wit
read-via-stream: func(offset: filesize)
    -> tuple<stream<u8>, future<result<_, error-code>>>;
```

The completion future resolves even when the caller samples or drops the data
stream early. Apply this shape to files, stdin, TCP receives, and directory
listings.

### Reverse write data flow

Pass a byte stream to the host and await the future returned after consumption:

```wit
write-via-stream: func(data: stream<u8>)
    -> future<result<_, error-code>>;
```

Use this pattern for stdout, stderr, filesystem writes, and TCP sends instead
of acquiring a host-owned output resource and pushing bytes into it.

### Collapse split operations

Replace 0.2 `start-foo`/`finish-foo` pairs and their `pollable` with one call.
Use `async func` when the host operation suspends, as TCP connect does. A split
that only enabled nonblocking dispatch, such as bind or listen, may become a
plain `func`.

### Reshape HTTP roles and values

Use `request` and `response` rather than the former nine-resource design.
Represent bodies as `stream<u8>`, trailers as a future, and return the response
directly from the handler:

```wit
handle: async func(request: request) -> result<response, error-code>;
```

Use the `service` world for an HTTP service and `middleware` when a component
both accepts requests and invokes a downstream handler. Do not retain the 0.2
`proxy` world name.

### Update sockets and shared interfaces

Grant network access at the world level rather than threading a `network`
resource through bind, connect, and lookup operations. Expect socket APIs to
consolidate into `types` and `ip-name-lookup`, with TCP `listen` returning a
`stream<tcp-socket>`.

Account for async filesystem methods, the clock renames from `wall-clock` to
`system-clock` and `datetime` to `instant`, and shared CLI types in
`wasi:cli/types`.

### Verify the initial toolchain floor

For the first 0.3 release line, use Wasmtime 46+, `wit-bindgen` 0.46+ with its
`async` feature, and `wkg` 0.15+. JavaScript hosts use jco's `preview3-shim`.
Rust builds currently need nightly when stable Rust's bundled
`wasm-component-ld` is too old for output from `wit-bindgen` 0.58.

## High-value new capabilities

### Use native async WIT values

Use `stream<T>` for incrementally produced ordered values, `future<T>` for one
later value, and `async func` for a call that may suspend. Streams and futures
are Canonical ABI values, so they can be parameters, results, and forwarded
across component boundaries.

Treat every stream or future as an owned handle. Passing it across a component
boundary transfers ownership; unlike a resource handle, it cannot be borrowed.

### Design for completion-based scheduling

The host runs one event loop across composed components. Delivering a future
value schedules its waiter even after the future crosses several boundaries.
The producer may be the host, another component, or the same component.

The ABI reports completion, not readiness. Emulate an `epoll`- or
`kqueue`-style readiness layer only when ported software requires one.

### Use 64-bit and multiple memories deliberately

A memory or table may use `i64` addresses, giving a theoretical 16 EiB address
space rather than 4 GiB. Web embeddings still cap a 64-bit memory at 16 GiB.

A module may define or import multiple memories, access them directly, and
copy data between them. This enables separate address spaces and removes a
module-merging limitation.

### Use native exception dispatch

Declare payload data on exception tags. Handler blocks dispatch with tag/label
pairs or catch-all labels to choose where control continues after a throw.

### Request determinism explicitly

Use the deterministic execution profile when results must reproduce across
participating platforms. It constrains floating-point NaN generation and
relaxed SIMD edge cases whose base semantics otherwise allow several results.
Ordinary relaxed SIMD may still choose any specified legal outcome.

### Use current WIT composition features

Import types with mandatory braces:

```wit
use types.{point};
```

Compose worlds from whole interfaces, individual functions, inline
interfaces, and `include`. Let tooling resolve external `package/interface`
names.

Use `map<K, V>` for dynamic key-value collections. When one component needs
several instances of the same interface under different names, use the
Component Model `implements` feature and require compatible runtimes and
toolchains.

## WIT correctness checklist

- Keep identifiers ASCII kebab-case; each hyphen-delimited word is wholly
  lowercase or wholly uppercase.
- Prefix a keyword used as a name with `%`.
- Use `///` or `/** ... */` for documentation of the following item.
- Allow nesting only for ordinary `/* ... */` comments.
- Use `result<T>`, `result<_, E>`, or bare `result` when a payload is absent.
- Do not depend on a NaN payload surviving a WIT interface crossing.
- Parameterize only built-in generic types; records and variants are not
  generic.
- Give a resource at most one constructor.
- Remember that ordinary resource methods borrow implicit `self`; static
  functions have no `self`.
- Treat `borrow<resource>` as call-scoped and owned handles as responsibility
  transfers.
- Keep peer `.wit` files for one package in one directory.
- Use `namespace:name` with optional `@semver` for package IDs.
- Ensure repeated package declarations match exactly.

## Review checklist

- Identify whether each boundary is Core Wasm, WIT, a component, or a WASI
  interface before choosing syntax and ownership rules.
- Check the host, runtime, bindings generator, package tooling, and linker
  together when adopting WASI async features.
- Trace ownership of every resource, stream, and future across calls.
- Confirm terminal errors remain observable when data streams are ignored or
  dropped early.
- Replace 0.2 readiness resources and split operations with their 0.3 async
  shapes only where migration is actually needed.
- Validate world-level capabilities, especially network access, separately
  from interface value types.
- Require 0.3.1-capable tooling before emitting `map<K, V>` or depending on
  multiple named instances through `implements`.
- Open the relevant reference file before finalizing code; the references
  preserve details intentionally condensed here.
