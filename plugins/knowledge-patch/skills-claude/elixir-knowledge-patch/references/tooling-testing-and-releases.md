# Tooling, Testing, and Releases

## ExUnit

### Parameterized modules and concurrency groups (`1.18.0`)

`ExUnit.Case` accepts `parameterize: [...]`, running the whole module once per
parameter map and merging it into each test context. Parameter instances may run
concurrently with `async: true`. The context includes the test process under
`:test_pid`.

```elixir
use ExUnit.Case,
  async: true,
  parameterize: [%{partitions: 1}, %{partitions: 8}]
```

Async modules may also set `group: value`. Modules in the same group never run
at the same time; different groups may, so unrelated shared resources can be
tested in parallel.

```elixir
use ExUnit.Case, async: true, group: :postgres
```

### Context, doctests, and logging (`1.19.0`, `1.20.0`)

Test contexts include `:test_group`. Doctests support ellipses matching the rest
of an expected exception and accept `:inspect_opts`. `ExUnit.CaptureLog` accepts
a `:formatter` option for custom log formatting.

## Formatting and source tooling

### Automated syntax migrations (`1.18.0`)

`mix format --migrate` rewrites deprecated forms: known bitstring modifiers lose
parentheses, custom modifiers gain them, charlists become `~c` sigils, and
`unless` becomes negated `if`. Because this rewrites AST, review the result near
macros that also transform AST. `unless` is soft-deprecated.

### Parser, formatter, and fragment APIs (`1.19.0`)

- `Code.string_to_quoted/2` accepts `:indentation` and returns an error for
  invalid Unicode rather than raising.
- The formatter supports `:migrate_call_parens_on_pipe`.
- `Code.Fragment` adds `:block_keyword_or_binary_operator` and `lines/1` for
  more precise editor tooling.

### Current source commands (`1.19.0`, `1.20.0`)

`mix format` can exclude files. `Code.Fragment.container_cursor_to_quoted` can
preserve sigil metadata. IEx adds `source/1`, while Mix adds:

```console
mix source Enum.map/2
mix format --no-compile
```

## Compilation behavior

### Cross-process coordination (`1.18.0`)

`mix compile` and `mix deps.get` lock their work so separate OS processes do not
race on the same build. Configure `:listeners` for compilation events from the
same or another process. IEx can reload modules compiled elsewhere:

```elixir
IEx.configure(auto_reload: true)
```

### Deterministic artifacts (`1.18.0`)

Set `ERL_COMPILER_OPTIONS=deterministic` for deterministic Elixir and Erlang
builds. It strips source and other compile-time metadata, so avoid it when those
details are required.

### Lazy project-module loading (`1.19.0`)

Compiled project modules no longer load immediately. Compiler-time concurrency
that calls another project module must use `Kernel.ParallelCompiler.pmap/2` or
call `Code.ensure_compiled!/1` before spawning. If an `@on_load` callback must
make that call, annotate the invoked module with `@compile {:autoload, true}`.

### Parallel dependency compilation (`1.19.0`)

Set `MIX_OS_DEPS_COMPILE_PARTITION_COUNT` above one to compile dependencies in
separate OS processes. Roughly half the available cores is a useful starting
point, but more parallelism consumes more memory.

```console
MIX_OS_DEPS_COMPILE_PARTITION_COUNT=8 mix deps.compile
```

### Parallel compiler diagnostics (`1.19.0`)

Pass `return_diagnostics: true` to `Kernel.ParallelCompiler.compile`,
`compile_to_path`, and `require`; omitting it is hard-deprecated. The compiler
adds an `each_long_verification_threshold` callback. With configured thresholds,
`MIX_DEBUG=1` reports compiler or type-checker PIDs.

### Interpreted module definitions (`1.20.0`)

Set `module_definition: :interpreted` to run `defmodule` contents in the
interpreter, potentially shortening compilation without changing the generated
BEAM.

```elixir
# mix.exs
elixirc_options: [module_definition: :interpreted]
```

Compilation errors can have less precise stacktraces. Anonymous functions
directly inside `defmodule` are limited to 20 arguments; functions declared with
`def` retain the 255-argument limit.

## Mix and IEx

### Warnings as errors (`1.18.0`)

Do not set `:warnings_as_errors` with `Code.put_compiler_option/2`,
`:elixirc_options`, or `:test_elixirc_options`. Pass `--warnings-as-errors` to
`mix compile` or `mix test`, optionally through task aliases.

### Help, tests, and Xref (`1.19.0`, `1.20.0`)

`mix help` accepts module, atom, function, arity, and `app:package` targets.
`mix test` adds `--name-pattern`, `--dry-run`, and distinguishable warning and
failure exit statuses. `mix xref graph` supports JSON output.

```console
mix help Mod.fun/arity
mix test --name-pattern PATTERN
mix test --dry-run
mix xref graph --format json
```

`mix` now requires `:elixirc_paths` to be a list of strings.

### Custom compiler orchestration (`1.19.0`)

Mix adds a `:compilers` option, `Mix.Task.Compiler.run/2`, and
`Mix.Tasks.Compiler.reenable/1`. Replace the older
`Mix.Tasks.Compile.compilers/0` with `Mix.Task.Compiler.compilers/0` (`1.18.0`).

### `mix cmd` and app selection (`1.18.0`, `1.19.0`)

Use `mix do --app APP` instead of `mix cmd --app APP`. `mix cmd` now preserves
argument quoting and performs no shell expansion; put `--shell` before the
command name to request the older shell-expanded behavior.

### Project and CLI configuration (`1.19.0`)

Move `:default_task`, `:preferred_cli_env`, and `:preferred_cli_target` from
`project/0` into `cli/0` as `:default_task`, `:preferred_envs`, and
`:preferred_targets`. Join `mix do` tasks with `+`, rename
`--no-protocol-consolidation` to `--no-consolidate-protocols`, and stop calling
the now-inert `mix compile.protocols` task.

Move `xref: [exclude: ...]` to
`elixirc_options: [no_warn_undefined: ...]` (`1.20.0`).

### IEx prompts and completion groups (`1.19.0`)

IEx supports multiline prompts, so `:continuation_prompt` and
`:alive_continuation_prompt` are no longer valid configuration. Functions with
`@doc group: "Name"` metadata appear under that group in completion results.

## Documentation and release artifacts

### ExDoc cheatsheets (`release-and-news-index`)

ExDoc's Cheatsheet feature includes task-oriented quick-reference material beside
generated documentation.

### Release SBOMs and attestations (`release-and-news-index`)

Elixir releases include source SBOMs in CycloneDX 1.6 and SPDX 2.3 formats plus
an attestation as part of the project's OpenChain ISO/IEC 5230 conformance. Use
them for license-compliance and software-supply-chain verification.
