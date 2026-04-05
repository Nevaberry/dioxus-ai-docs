# APIs, Mix & Compilation

## New APIs (1.19)

- `Access.values/0` — traverses all values in maps/keyword lists
- `String.count/2` — counts occurrences of a pattern in a string
- `min/2` and `max/2` now work as guards
- `Regex.to_embed/2` — returns embeddable representation for use inside another regex
- `OptionParser` supports `:regex` type
- `Inspect` derive supports `optional: :all`

## New APIs (1.20)

- `Integer.ceil_div/2` — ceiling division
- `Integer.popcount/1` — count set bits
- `IO.iodata_empty?/1` — check if iodata is empty
- `List.first!/1`, `List.last!/1` — raise on empty list
- `Regex.import/1` — import regexes defined with `/E` flag
- `Process.get_label/1` — get process label
- `Code` eval functions: `:module_definition` option (`:interpreted` skips compilation for faster eval)

## Compilation Changes (1.19)

- Modules are now lazily loaded. If you spawn processes during compilation that call other project modules, use `Code.ensure_compiled!/1` or `Kernel.ParallelCompiler.pmap/2` first.
- `@on_load` callbacks calling other project modules need `@compile {:autoload, true}` on the called module.
- `MIX_OS_DEPS_COMPILE_PARTITION_COUNT=N` compiles deps in parallel OS processes (set to half your cores).

## Mix Changes (1.19)

- `mix help Mod`, `mix help Mod.fun/arity`, `mix help app:package` — docs in shell
- `mix test --name-pattern` — filter tests by name pattern
- `mix xref graph --format json`
- `mix do` separator: use `+` instead of `,` (deprecated)
- `:default_task`, `:preferred_cli_env`, `:preferred_cli_target` move from `def project` to `def cli`
- `:migrate_call_parens_on_pipe` formatter option

## Mix Changes (1.20)

- `mix test --dry-run` — list tests without running them
- `mix deps` supports `--override` for specific dependencies
- `mix deps` output filtering

## Logger (1.19)

`:backends` config is deprecated. Use `:default_handler` or start backends in application callback.

## Breaking Changes (1.20)

- `map.foo()` (field access with parens) and `mod.foo` (function call without parens) now **raise** instead of warning
- `File.stream!(path, modes, lines_or_bytes)` → `File.stream!(path, lines_or_bytes, modes)` (arg order swapped, old form deprecated)
- Bitstring size matching requires pin: `<<data::size(^size)>>` (previously `<<data::size(size)>>`)
- `require SomeModule` no longer expands to the module at compile-time (breaks `require(Mod).macro()` pattern)

## Deprecations (1.20)

- `Kernel.ParallelCompiler.async/1` → use `pmap/2`
- `Logger.enable/1`, `Logger.disable/1` → use `Logger.put_process_level/2`, `Logger.delete_process_level/1`
- `Logger.*_backend` functions → use handlers (or `:logger_backends` package)

## OTP Compatibility

- Elixir 1.20 requires OTP 27+ (compatible with OTP 29)
