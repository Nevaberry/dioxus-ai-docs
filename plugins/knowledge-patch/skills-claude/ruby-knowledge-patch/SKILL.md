---
name: ruby-knowledge-patch
description: Ruby
version: 4.0.0
license: MIT
metadata:
  author: Nevaberry
---


# Ruby Knowledge Patch

Use this skill when upgrading Ruby applications, libraries, tooling, or native
extensions, or when code depends on recently changed runtime behavior. Start
with the compatibility notes below, then open the reference covering the
subsystem being changed.

## Reference index

| Reference | Topics |
| --- | --- |
| [Language and core types](references/language-and-core-types.md) | Syntax, strings, numeric operations, ranges, enumerators, reflection, inspection |
| [Concurrency and Ractors](references/concurrency-and-ractors.md) | Ractor ports and isolation, exception propagation, fiber scheduler hooks, backtraces |
| [I/O, networking, and standard library](references/io-networking-and-standard-library.md) | Sockets, URI parsing, files, process opening, Set and Pathname, bundled gems, CGI and Net::HTTP |
| [Runtime, diagnostics, and JIT](references/runtime-diagnostics-and-jit.md) | GC configuration, modular GC, warnings, backtrace formatting, YJIT and ZJIT |
| [Extensions, builds, and packaging](references/extensions-builds-and-packaging.md) | Removed Ruby and C APIs, extension I/O contracts, Set C API, Windows builds, gem attestations and checksums |

## Upgrade-critical quick reference

### Replace removed process and Ractor interfaces

Do not open subprocesses by passing a leading `|` command to `Kernel#open` or
the IO class methods. That deprecated process-creation behavior is removed.

Ractor communication now uses `Ractor::Port`. Replace `Ractor.yield`,
`Ractor#take`, `#close_incoming`, and `#close_outgoing`, all of which are
removed. A port supports `receive`, `send` or `<<`, `close`, and `closed?`.
Ractors also expose `join`, `value`, and a `default_port`.

```ruby
port = Ractor::Port.new
worker = Ractor.new(port) { |out| out << 1 }
result = port.receive
worker.join
```

`Ractor.select` accepts only Ractors and Ports and treats Ractor termination as
selectable. Use `Ractor.shareable_proc` or `Ractor.shareable_lambda` when a
callable must cross Ractor boundaries.

### Audit removed and deprecated Ruby APIs

Replace or remove these compatibility hazards:

- `Refinement#refined_class` is removed.
- Mutation through `DidYouMean::SPELL_CHECKERS` is removed.
- Deprecated Net::HTTP proxy, response-code, and receiver constants are
  removed.
- `Process::Status#&` and `Process::Status#>>` are removed.
- `ObjectSpace._id2ref` is deprecated.
- `rb_path_check` is removed.
- `rb_thread_fd_close` is deprecated and is now a no-op.
- `--rjit` is removed.

For extensions, replace `rb_newobj`, `rb_newobj_of`, their allocation macros,
and `rb_gc_force_recycle`. Extensions exposing file descriptors should create
an `IO` with `RUBY_IO_MODE_EXTERNAL` and close it through `rb_io_close`.

### Fix changed request and socket behavior

Net::HTTP no longer assigns
`Content-Type: application/x-www-form-urlencoded` automatically to requests
with bodies. Set that header explicitly when the endpoint expects it.

Happy Eyeballs v2 is enabled for `Socket.tcp` and `TCPSocket.new`. Disable it
globally with `RUBY_TCP_NO_FAST_FALLBACK=1` or
`Socket.tcp_fast_fallback = false`, or pass `fast_fallback: false` to an
individual connection.

Both connection APIs accept `open_timeout:`. A user-specified timeout in
`TCPSocket.new` consistently raises `IO::TimeoutError`; OS-level timeouts can
still raise `Errno::ETIMEDOUT`, and `Socket.tcp` retains additional paths that
can raise it.

```ruby
socket = TCPSocket.new(host, port,
  open_timeout: 5,
  fast_fallback: false)
```

### Update string mutation and parsing code

With deprecation warnings enabled, mutating a string literal in a file without
a `frozen_string_literal` comment warns. Unary `+` duplicates a string when
mutation would produce that warning:

```ruby
buffer = +"value"
buffer << "!"
```

Mutating the result of `Symbol#to_s` also warns under `-W:deprecated`; duplicate
it first. For binary assembly, `String#append_as_bytes` appends without encoding
validation or conversion.

The default URI parser follows RFC 3986 rather than RFC 2396. Recheck validation
and interpretation of edge-case URIs. `Float()` and `String#to_f` accept a
decimal point without following fractional digits, including before an
exponent.

### Rewrite changed language and reflection forms

Index assignment does not permit explicit block passing or keyword arguments.
Rewrite forms such as these:

```ruby
# Unsupported
items[0, &block] = value
items[0, mode: :fast] = value
```

Leading `||`, `&&`, `and`, and `or` continue the preceding line. Also note that
`*nil` no longer calls `nil.to_a`.

Numbered parameters and `it` no longer appear through the ordinary
`Binding#local_variables` family. Use `Binding#implicit_parameters`,
`#implicit_parameter_get`, and `#implicit_parameter_defined?`.
`Proc#parameters` reports an anonymous optional parameter as `[:opt]`.

### Migrate Set, Pathname, and CGI assumptions

`Pathname` and `Set` are core classes. `Set#inspect` renders as
`Set[1, 2, 3]`; arguments to `Set#to_set` and `Enumerable#to_set` are
deprecated. `SortedSet` is no longer autoloaded, so install and require
`sorted_set` explicitly.

The complete CGI library is no longer a default gem. Only `cgi/escape` remains,
with its escape and unescape, HTML, URI-component, and element helpers.

Several former default gems are now bundled gems: `ostruct`, `pstore`,
`benchmark`, `logger`, `rdoc`, `win32ole`, `irb`, `reline`, `readline`, and
`fiddle`.

### Review observable output

Backtrace labels use single quotes and permanent class names, omit extra
`rescue` and `ensure` frames, hide `internal` frames, and attribute
C-implemented methods like Ruby source methods. Wrong-arity `ArgumentError`
output includes caller and callee snippets plus receiver-qualified labels.

`Hash#inspect` now favors `{user: 1}` for symbol keys and spaces other
associations as `{"user" => 1}`. Audit snapshot tests and parsers that compare
these strings.

Classes can restrict default `Kernel#inspect` output by defining
`instance_variables_to_inspect`, which is useful for omitting secrets:

```ruby
class Config
  def initialize
    @host, @password = "db.example", "secret"
  end

  private def instance_variables_to_inspect = [:@host]
end
```

## High-value runtime features

### Use the expanded Ractor facilities

`require` can run inside a Ractor; loading occurs on the main Ractor, and
`Ractor._require` exposes that behavior. Use `Ractor.main?` to test the current
Ractor, `Ractor.[]` and `Ractor.[]=` for local state, and
`Ractor.store_if_absent` for atomic initialization.

The experimental `Ruby::Box` isolates loaded definitions, libraries, monkey
patches, globals, and class variables. Enable it with `RUBY_BOX=1`.

### Configure schedulers and exception propagation

Schedulers can offload blocking work through the optional
`blocking_operation_wait` hook. They may also implement `fiber_interrupt` and
`yield`; asynchronous `io_close` is restored, and flushing an IO write buffer
invokes `io_write`.

`Thread#raise` and `Fiber#raise` accept `cause:`. They, `Kernel#raise`, and
`Exception#set_backtrace` accept arrays of `Thread::Backtrace::Location`, so
callers can preserve structured locations.

### Select runtime and JIT controls deliberately

`GC.config` can change collector settings. Setting
`rgengc_allow_full_mark: false` restricts collection to marking young objects;
the default is `true`.

Modular GC requires a build configured with `--with-modular-gc`; select a built
collector with `RUBY_GC_LIBRARY`. The experimental MMTk collector needs Rust at
build time.

YJIT adds unified memory sizing, logging, exit tracing, code-generation
profiling, and more runtime statistics. ZJIT is experimental, requires Rust
1.85.0 or newer to build, and is not recommended for production.

## Working method

1. Confirm the application and extension runtime before applying an item.
2. Start with removed APIs and changed defaults that can break execution.
3. Review observable strings separately from functional behavior.
4. Open the relevant topic reference before editing scheduler, Ractor, GC, JIT,
   socket, standard-library, or C-extension code.
5. Keep fallback behavior explicit where the runtime can raise more than one
   exception type or a feature depends on OS, kernel, filesystem, build flags,
   or environment variables.
