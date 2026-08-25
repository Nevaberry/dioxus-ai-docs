# Runtime, Diagnostics, and JIT

## Garbage collection

### Runtime collector configuration

`GC.config` can set collector configuration since 3.4.0. The
`rgengc_allow_full_mark` option defaults to `true`. Setting it to `false`
restricts collection to marking young objects.

```ruby
GC.config(rgengc_allow_full_mark: false)
```

### Modular collectors

Loading an alternative collector requires a Ruby build configured with
`--with-modular-gc`. Build a collector with:

```sh
make modular-gc MODULAR_GC=default
```

Use `MODULAR_GC=mmtk` for the experimental MMTk collector, which requires Rust
at build time. Select the built collector at runtime through
`RUBY_GC_LIBRARY`:

```sh
RUBY_GC_LIBRARY=default ruby app.rb
```

These controls are available since 3.4.0.

## Warnings

Since 3.4.0, `strict_unused_block` reports blocks passed to methods that do not
use them. The `performance` category reports redefinition of specially
optimized core methods.

```ruby
Warning[:strict_unused_block] = true
Warning[:performance] = true
```

## Observable diagnostics

### Backtrace and inspect formatting

Since 3.4.0:

- Backtrace method labels use single quotes.
- Labels include a permanent class name.
- Extra `rescue` and `ensure` frames are omitted.
- `Hash#inspect` uses `{user: 1}` for symbol keys and spaces other
  associations as `{"user" => 1}`.

Since 4.0.0:

- Wrong-arity `ArgumentError` output shows caller and callee snippets.
- Wrong-arity backtrace labels include the receiver class or module.
- Backtraces no longer expose `internal` frames.
- C-implemented methods are attributed like Ruby source methods.

Treat these as observable compatibility changes for snapshot tests, log
processing, and parsers.

## YJIT

### Memory and diagnostics

Since 3.4.0, `--yjit-mem-size` is a unified-memory alternative to the older
execution-memory-only limit and defaults to 128 MiB.

Diagnostics and controls include:

- `--yjit-log`
- `RubyVM::YJIT.enable(log: true)`
- `RubyVM::YJIT.log`
- `--yjit-trace-exits=COUNTER`
- `--yjit-perf=codegen`
- the `:iseq_calls` runtime statistic

### Enable-time options and statistics

Since 4.0.0, `RubyVM::YJIT.enable` accepts `mem_size:` and `call_threshold:`.

The `ratio_in_yjit` statistic requires both:

- `--enable-yjit=stats` when configuring the build.
- `--yjit-stats` at runtime.

Default statistics include `invalidate_everything` for TracePoint-driven global
invalidations.

## ZJIT and RJIT

The experimental ZJIT is available since 4.0.0 through `--zjit` or
`RubyVM::ZJIT.enable`. Building it requires Rust 1.85.0 or newer. It is not yet
recommended for production.

The `--rjit` option is removed.
