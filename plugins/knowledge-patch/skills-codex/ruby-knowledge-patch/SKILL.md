---
name: ruby-knowledge-patch
description: Ruby
version: 4.0.0
license: MIT
metadata:
  author: Nevaberry
---


# Ruby Knowledge Patch

Use this skill when upgrading Ruby applications, reviewing version-sensitive
Ruby code, maintaining gems or native extensions, or diagnosing behavior that
changed in the language, runtime, standard library, networking stack, or JITs.

Prefer the project's declared Ruby version, lockfile, build configuration, and
tests over assumptions. Read the reference file that matches the work before
changing code. Treat experimental facilities as opt-in and verify platform
support where the behavior depends on the OS, filesystem, compiler, or build.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/language-and-core.md](references/language-and-core.md) | Syntax, coercion, strings, ranges, reflection, enumerators, inspection, math, warnings, and removed Ruby APIs |
| [references/concurrency-and-io.md](references/concurrency-and-io.md) | Ractors, scheduler hooks, exception backtraces and causes, file metadata, IO, and process opening |
| [references/runtime-and-jit.md](references/runtime-and-jit.md) | Ruby Box, GC configuration, modular GC, YJIT, and ZJIT |
| [references/stdlib-networking-and-packaging.md](references/stdlib-networking-and-packaging.md) | Gems, lockfile integrity, URI, sockets, Set, Pathname, Unicode, CGI, Net::HTTP, and diagnostics |
| [references/native-extensions.md](references/native-extensions.md) | Removed allocation APIs, descriptor shutdown, GVL calls, Set's C API, path checking, and Windows builds |

## Upgrade triage

Start with these compatibility breaks:

1. Find code that mutates string literals or the result of `Symbol#to_s`.
   Create an owned mutable string with unary `+` or `dup`.
2. Rewrite index assignments that pass keywords or an explicit block.
3. Replace leading-`|` process creation through `Kernel#open` or IO class
   methods with an explicit process API.
4. Migrate Ractor messaging from `Ractor.yield` and `Ractor#take` to
   `Ractor::Port`, `default_port`, `send`, and `receive`.
5. Audit standard-library dependencies that are no longer default gems and add
   required gems explicitly.
6. Set `Content-Type` explicitly for Net::HTTP form-style request bodies.
7. Update native extensions away from removed allocation, GC recycling, and
   path-checking APIs; replace descriptor-close integration as described in
   the native-extension reference.
8. Refresh snapshots that depend on `Hash#inspect`, `Set#inspect`, exception
   messages, or backtrace labels.

## Mutable strings

With deprecation warnings enabled, mutating an unfrozen literal in a file that
lacks a `frozen_string_literal` comment warns. Unary `+` duplicates a string
when the mutation would warn, so use it for migration-safe buffers:

```ruby
buffer = +"value"
buffer << "!"
```

`--disable-frozen-string-literal` opts out. A string returned by `Symbol#to_s`
is also intended to become frozen and warns on mutation under `-W:deprecated`.
Duplicate it first:

```ruby
name = :user.to_s.dup
name << "!"
```

For byte-oriented protocols, `String#append_as_bytes` appends without encoding
validation or conversion:

```ruby
packet = +"".b
packet.append_as_bytes("\xFF".b)
```

## Syntax, coercion, and reflection

Leading `||`, `&&`, `and`, and `or` continue the preceding line. This allows a
condition to be formatted similarly to a fluent call chain:

```ruby
if ready
   && authorized
  run
end
```

Do not rely on `*nil` calling `nil.to_a`; it no longer does. Keep numbered
parameters and `it` out of the ordinary `Binding` local-variable APIs. Use
`Binding#implicit_parameters`, `#implicit_parameter_get`, and
`#implicit_parameter_defined?` for them.

When an `Enumerator.produce` sequence has a meaningful bound, supply `size:`
as an integer, `Float::INFINITY`, a callable, or `nil`. Omitting it preserves
the infinite default.

## Ractor migration

`require` can run inside a Ractor; loading is performed on the main Ractor.
Use `Ractor._require` when that behavior should be explicit. Ractor-local state
is available through `Ractor.[]`, `Ractor.[]=`, and atomic
`Ractor.store_if_absent`; `Ractor.main?` identifies the main Ractor.

For current message flows, create a `Ractor::Port` and use `send`/`<<`,
`receive`, `close`, and `closed?`:

```ruby
port = Ractor::Port.new
worker = Ractor.new(port) { |out| out << 1 }
port.receive
worker.join
worker.value
```

Each Ractor has a `default_port` backing `Ractor.send` and `Ractor.receive`.
`Ractor.select` accepts only Ractors and Ports, and Ractor termination is
selectable. Use `Ractor.shareable_proc` or `Ractor.shareable_lambda` when a
callable must cross a Ractor boundary.

## Scheduler and exception integration

A scheduler can offload blocking work through the optional
`blocking_operation_wait` hook. It can also implement `fiber_interrupt` to
interrupt a fiber with an exception and `yield` to continue processing while
signal exceptions are disabled. The asynchronous `io_close` hook is restored,
and flushing an IO write buffer invokes `io_write`.

`Thread#raise` and `Fiber#raise` accept `cause:`. Exception backtrace setters
and raisers accept arrays of `Thread::Backtrace::Location`, avoiding a
round-trip through strings:

```ruby
error.set_backtrace(caller_locations)
```

## Networking checks

Happy Eyeballs v2 is active for `Socket.tcp` and `TCPSocket.new`. Disable fast
fallback globally with `RUBY_TCP_NO_FAST_FALLBACK=1` or
`Socket.tcp_fast_fallback = false`, or per call with `fast_fallback: false`.

Use `open_timeout:` to bound initial connection setup:

```ruby
TCPSocket.new(host, port, open_timeout: 5)
```

A user timeout in `TCPSocket.new` raises `IO::TimeoutError` consistently.
OS-level timeouts can still raise `Errno::ETIMEDOUT`, and `Socket.tcp` retains
additional cases that can raise it, so handle both where portability matters.

## Runtime and JIT choices

Enable experimental `Ruby::Box` definition isolation with `RUBY_BOX=1`. A box
isolates loaded definitions and libraries, monkey patches, globals, and class
variables; do not assume definitions leak between boxes.

Use `GC.config` for collector settings such as `rgengc_allow_full_mark`.
Disabling full marking restricts collection to young-object marking. Modular
GC must be enabled when Ruby is built, and the collector is selected with
`RUBY_GC_LIBRARY`.

For YJIT, prefer the unified `--yjit-mem-size` budget and use logging, traced
exit counters, code-generation profiling, and runtime statistics only as
needed. Enabling `ratio_in_yjit` requires both build-time stats support and the
runtime stats option.

ZJIT is experimental, requires a Rust-enabled build, and is not recommended
for production. The `--rjit` option is gone.

## Validation checklist

- Run the application with deprecation, strict unused-block, and performance
  warnings enabled where practical.
- Run tests under the project's actual Ruby build and platform.
- Refresh lockfile checksums and verify gem requirements after packaging
  changes.
- Exercise socket failure paths for both Ruby timeout and OS timeout errors.
- Re-run scheduler tests around buffered writes, close, interruption, and
  signal handling.
- Test Ractor shutdown, port closure, selection, joining, and value retrieval.
- Rebuild native extensions and run pending-IO shutdown tests.
- Review snapshots and parsers that consume `inspect`, exception messages, or
  formatted backtraces.

