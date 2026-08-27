# Runtime, GC, and JITs

## Isolate definitions with Ruby Box

The experimental `Ruby::Box` isolates definitions loaded in one box from
other boxes (since 4.0.0). Isolation covers monkey patches, global and class
variables, class and module definitions, and loaded Ruby or native libraries.
Enable the feature through the environment:

```sh
RUBY_BOX=1 ruby app.rb
```

Treat this as an experimental boundary and test library loading and shared
state explicitly.

## Configure the collector at runtime

`GC.config` sets collector configuration (since 3.4.0). The
`rgengc_allow_full_mark` option defaults to `true`; setting it to `false`
restricts collection to marking young objects:

```ruby
GC.config(rgengc_allow_full_mark: false)
```

## Build and load modular collectors

Modular GC requires Ruby to be configured with `--with-modular-gc` (since
3.4.0). Build a collector with either of these forms:

```sh
make modular-gc MODULAR_GC=default
make modular-gc MODULAR_GC=mmtk
```

Select the collector at runtime with `RUBY_GC_LIBRARY`:

```sh
RUBY_GC_LIBRARY=default ruby app.rb
```

The experimental MMTk collector requires Rust at build time.

## Configure and diagnose YJIT

`--yjit-mem-size` is a unified-memory alternative to the older
execution-memory-only limit and defaults to 128 MiB (since 3.4.0). Available
diagnostics and controls include:

- `--yjit-log`
- `RubyVM::YJIT.enable(log: true)`
- `RubyVM::YJIT.log`
- `--yjit-trace-exits=COUNTER`
- `--yjit-perf=codegen`
- the `:iseq_calls` runtime statistic

`RubyVM::YJIT.enable` later accepts `mem_size:` and `call_threshold:` (since
4.0.0). The `ratio_in_yjit` statistic requires Ruby to be configured with
`--enable-yjit=stats` and launched with `--yjit-stats`. Default statistics add
`invalidate_everything` for TracePoint-driven global invalidations.

## Evaluate ZJIT carefully

The experimental ZJIT is enabled with `--zjit` or `RubyVM::ZJIT.enable` (since
4.0.0). Building it requires Rust 1.85.0 or newer. It is not recommended for
production. The `--rjit` option is removed.

