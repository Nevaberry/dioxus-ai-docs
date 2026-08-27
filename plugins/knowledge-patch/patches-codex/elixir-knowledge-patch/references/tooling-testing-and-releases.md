# Tooling, Testing, and Releases

## Parameterize and schedule ExUnit modules

`ExUnit.Case` in `1.18.0` accepts `parameterize: [...]`. ExUnit runs the whole
module once for each parameter map and merges that map into every test context.
Instances may run concurrently under `async: true`, and `:test_pid` identifies
the test process:

```elixir
use ExUnit.Case,
  async: true,
  parameterize: [%{partitions: 1}, %{partitions: 8}]
```

Async test modules may also declare `group: value`. Modules in one group never
run concurrently, while different groups may, making groups suitable for
shared external resources:

```elixir
use ExUnit.Case, async: true, group: :postgres
```

In `1.19.0`, contexts also include `:test_group`. Doctests accept
`:inspect_opts` and support an ellipsis matching the remainder of an expected
exception.

`ExUnit.CaptureLog` accepts a `:formatter` option in `1.20.0` for custom log
formatting.

## Run and select tests

Mix adds `--name-pattern` in `1.19.0` and gives warning exits a status distinct
from test failures:

```console
mix test --name-pattern PATTERN
```

Use `mix test --dry-run` in `1.20.0` to discover tests without running them.
Pass `--warnings-as-errors` directly to `mix test` or `mix compile`; setting
`:warnings_as_errors` through `Code.put_compiler_option/2`, `:elixirc_options`,
or `:test_elixirc_options` is deprecated since `1.18.0`.

## Format and migrate source

`mix format --migrate` in `1.18.0` rewrites deprecated constructs:

- known bitstring modifiers lose parentheses;
- custom bitstring modifiers gain parentheses;
- charlists become `~c` sigils; and
- `unless` becomes a negated `if` because `unless` is soft-deprecated.

Migration rewrites AST, so review results around macros that also transform
AST.

The `1.19.0` formatter adds `:migrate_call_parens_on_pipe`, and `mix format`
can exclude files. Use `mix format --no-compile` in `1.20.0` when formatting
must not compile the project.

`Code.string_to_quoted/2` accepts an `:indentation` option in `1.19.0` and
returns an error for invalid Unicode rather than raising. `Code.Fragment` adds
`:block_keyword_or_binary_operator` plus `lines/1`; in `1.20.0`,
`Code.Fragment.container_cursor_to_quoted` can preserve sigil metadata.

## Coordinate compilation across processes

Since `1.18.0`, `mix compile` and `mix deps.get` lock their work so independent
OS processes cannot race on the same build. Configure `:listeners` to receive
compilation events from the current or another process; IEx can reload modules
compiled elsewhere:

```elixir
IEx.configure(auto_reload: true)
```

In `1.19.0`, compiled modules are no longer loaded immediately. Compiler-time
concurrency that invokes another project module must use
`Kernel.ParallelCompiler.pmap/2` or call `Code.ensure_compiled!/1` before
spawning. If an `@on_load` callback must call such a module, mark the invoked
module with `@compile {:autoload, true}`.

Call `Kernel.ParallelCompiler.compile`, `compile_to_path`, and `require` with
`return_diagnostics: true`; omitting it is hard-deprecated in `1.19.0`. The
parallel compiler also supports an `each_long_verification_threshold`
callback. With configured thresholds, `MIX_DEBUG=1` prints the compiler or type
checker PIDs that cross them.

## Compile dependencies in parallel

Set `MIX_OS_DEPS_COMPILE_PARTITION_COUNT` above 1 to let
`mix deps.compile` build multiple dependencies in separate OS processes
(`1.19.0`). Starting near half the available core count is reasonable, but
extra workers consume more memory:

```console
MIX_OS_DEPS_COMPILE_PARTITION_COUNT=8 mix deps.compile
```

## Choose interpreted module definitions

Set `module_definition: :interpreted` in `1.20.0` to execute the contents of
`defmodule` in the interpreter and potentially shorten compilation without
changing the generated BEAM:

```elixir
elixirc_options: [module_definition: :interpreted]
```

Compilation errors may have less precise stacktraces. Anonymous functions
directly inside `defmodule` are limited to 20 arguments, while functions made
with `def` retain the 255-argument limit.

## Build deterministically

Set `ERL_COMPILER_OPTIONS=deterministic` for deterministic Elixir and Erlang
artifacts (`1.18.0`). This removes source and other compile-time metadata from
the output, so do not enable it when tools or releases require that metadata.

## Orchestrate custom compilers

Mix `1.19.0` adds the `:compilers` option, `Mix.Task.Compiler.run/2`, and
`Mix.Tasks.Compiler.reenable/1` for custom compiler orchestration.

`Mix.Task.Compiler.compilers/0` replaces
`Mix.Tasks.Compile.compilers/0` (`1.18.0`). In `1.20.0`, `:elixirc_paths` must
be a list of strings.

## Discover source and CLI targets

In `1.19.0`, `mix help` accepts module, atom, function, arity, and
`app:package` targets. `mix xref graph` supports JSON output:

```console
mix help Mod.fun/arity
mix xref graph --format json
```

Elixir `1.20.0` adds IEx `source/1` and its Mix counterpart:

```console
mix source Enum.map/2
```

IEx supports multiline prompts in `1.19.0`, so the
`:continuation_prompt` and `:alive_continuation_prompt` settings are no longer
supported. Functions carrying `@doc group: "Name"` appear in that group in
autocompletion.

## Update Mix CLI semantics

`mix cmd` preserves argument quoting and skips shell expansion in `1.19.0`.
Put `--shell` before the command to request the former shell-expanded behavior.

Move `:default_task`, `:preferred_cli_env`, and `:preferred_cli_target` out of
`project/0` and define them in `cli/0` as `:default_task`, `:preferred_envs`,
and `:preferred_targets`. Join `mix do` tasks with `+`, replace
`--no-protocol-consolidation` with `--no-consolidate-protocols`, and remove
calls to the now-inert `mix compile.protocols` task.

Use `mix do --app APP` instead of `mix cmd --app APP` (`1.18.0`).

## Migrate compiler, protocol, and template APIs

A protocol can define its own optional `__deriving__/1` macro callback in
`1.18.0`; an empty implementation is not required. The older
`__deriving__/3` callback on the protocol's `Any` implementation is deprecated.

Use the following replacements:

| Deprecated form | Replacement |
|---|---|
| `<%# ... %>` | `<%!-- ... --%>` or `<% # ... %>` |
| `EEx.handle_text/2` | `EEx.handle_text/3` |
| `List.zip/1` | `Enum.zip/1` |
| `Module.eval_quoted/3` | `Code.eval_quoted/3` |
| `Tuple.append/2` | `Tuple.insert_at/3` |

These migrations are from `1.18.0`.

## Migrate Logger and Xref configuration

In `1.19.0`, Logger's `:backends` setting is deprecated. Disable
`:default_handler` or start custom backends from the application start callback.

For `1.20.0`, replace `Logger.enable/1` and `Logger.disable/1` with
`Logger.put_process_level/2` and `Logger.delete_process_level/1`. Move
`xref: [exclude: ...]` to `elixirc_options: [no_warn_undefined: ...]`.

## Build documentation and inspect releases

ExDoc's Cheatsheet feature includes task-oriented quick-reference material in
generated documentation (`release-and-news-index`).

Elixir releases provide source SBOMs in CycloneDX 1.6 and SPDX 2.3 formats,
plus an attestation, as part of OpenChain ISO/IEC 5230 conformance. Use these
artifacts for license-compliance and software-supply-chain checks.
