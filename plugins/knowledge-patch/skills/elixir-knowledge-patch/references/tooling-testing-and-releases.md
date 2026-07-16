# Tooling, Testing, and Releases

Batch attribution: `1.18.0`, `1.19.0`, `1.20.0`, and `release-and-news-index`.

## Contents

- [Migrate source formatting](#migrate-source-formatting)
- [Coordinate compilation](#coordinate-compilation)
- [Configure warnings and Mix tasks](#configure-warnings-and-mix-tasks)
- [Navigate source and tasks](#navigate-source-and-tasks)
- [Run and structure tests](#run-and-structure-tests)
- [Inspect project graphs and source](#inspect-project-graphs-and-source)
- [Publish documentation and verify releases](#publish-documentation-and-verify-releases)

## Migrate source formatting

### Run formatter migrations and review macro-heavy code

`mix format --migrate` rewrites deprecated constructs:

- known bitstring modifiers lose parentheses;
- custom bitstring modifiers gain parentheses;
- charlists become `~c` sigils; and
- `unless` becomes a negated `if` because `unless` is soft-deprecated.

The migration rewrites AST. Review changes around macros that transform AST themselves.

The formatter also accepts `:migrate_call_parens_on_pipe`. Use `mix format` exclusions to omit selected files, and use `mix format --no-compile` when formatting must not compile the project.

### Update EEx and helper APIs

- Write EEx comments as `<%!-- ... --%>` or `<% # ... %>` rather than `<%#`.
- Implement `EEx.handle_text/3` instead of arity two.
- Replace `List.zip/1` with `Enum.zip/1`.
- Replace `Module.eval_quoted/3` with `Code.eval_quoted/3`.
- Replace `Tuple.append/2` with `Tuple.insert_at/3`.
- Replace `Mix.Tasks.Compile.compilers/0` with `Mix.Task.Compiler.compilers/0`.
- Use `mix do --app APP` instead of `mix cmd --app APP`.

## Coordinate compilation

### Rely on cross-process locks and listeners

`mix compile` and `mix deps.get` lock their work so separate operating-system processes do not race over the same build. Configure project `:listeners` to receive compilation events from this or another process. Let IEx reload modules compiled elsewhere with:

```elixir
IEx.configure(auto_reload: true)
```

### Account for lazy project-module loading

Compiled modules are no longer loaded immediately. Compiler-time concurrency that invokes another project module must use `Kernel.ParallelCompiler.pmap/2` or call `Code.ensure_compiled!/1` before spawning.

If an `@on_load` callback must call a project module, annotate the invoked module with:

```elixir
@compile {:autoload, true}
```

### Return compiler diagnostics explicitly

Omitting `return_diagnostics: true` is hard-deprecated for `Kernel.ParallelCompiler.compile`, `compile_to_path`, and `require`.

Use the `each_long_verification_threshold` callback to observe long verification work. With configured thresholds, `MIX_DEBUG=1` reports compiler or type-checker PIDs.

### Define and re-enable custom compilers

Mix provides a `:compilers` option, `Mix.Task.Compiler.run/2`, and `Mix.Tasks.Compiler.reenable/1` for custom compiler orchestration.

### Parallelize dependency compilation cautiously

Set `MIX_OS_DEPS_COMPILE_PARTITION_COUNT` above `1` to compile dependencies in multiple OS processes:

```console
MIX_OS_DEPS_COMPILE_PARTITION_COUNT=8 mix deps.compile
```

About half the available core count is a useful starting point. More workers also consume more memory.

### Choose deterministic or interpreted compilation intentionally

Set `ERL_COMPILER_OPTIONS=deterministic` for deterministic Elixir and Erlang builds. This removes source and other compile-time information from the artifacts, so do not use it when that metadata is required.

Set `module_definition: :interpreted` to execute `defmodule` contents in the interpreter while producing the same generated BEAM file, often shortening compilation:

```elixir
# mix.exs
elixirc_options: [module_definition: :interpreted]
```

Compilation errors can have less precise stacktraces. Anonymous functions directly inside `defmodule` are limited to 20 arguments in this mode; functions declared with `def` retain the 255-argument limit.

## Configure warnings and Mix tasks

### Pass warnings-as-errors to tasks

Do not set `:warnings_as_errors` with `Code.put_compiler_option/2`, `:elixirc_options`, or `:test_elixirc_options`; those paths are deprecated. Pass `--warnings-as-errors` to `mix compile` or `mix test`, optionally through task aliases.

### Move CLI settings into `cli/0`

Move these values from `project/0`:

| Old project key | `cli/0` key |
|---|---|
| `:default_task` | `:default_task` |
| `:preferred_cli_env` | `:preferred_envs` |
| `:preferred_cli_target` | `:preferred_targets` |

Use `+` rather than commas between `mix do` tasks. Replace `--no-protocol-consolidation` with `--no-consolidate-protocols`, and stop invoking the now-inert `mix compile.protocols` task.

Move `xref: [exclude: ...]` from project configuration to `elixirc_options: [no_warn_undefined: ...]`.

Ensure `:elixirc_paths` is a list of strings.

### Account for `mix cmd` quoting

`mix cmd` preserves argument quoting and no longer performs shell expansion. Put `--shell` before the command name when shell-expanded behavior is required.

## Navigate source and tasks

### Use expanded help targets

`mix help` accepts a module, atom, function, arity, or `app:package` target:

```console
mix help Mod.fun/arity
```

### Locate definitions from Mix and IEx

Use IEx's `source/1` helper or the `mix source` task:

```console
mix source Enum.map/2
```

### Build precise editor tooling

- `Code.string_to_quoted/2` accepts `:indentation` and returns an error for invalid Unicode rather than raising.
- `Code.Fragment` adds the `:block_keyword_or_binary_operator` fragment kind and `lines/1`.
- `Code.Fragment.container_cursor_to_quoted` can preserve sigil metadata.

### Group IEx completion entries

Functions carrying `@doc group: "Name"` metadata appear under that group in autocompletion.

IEx supports multiline prompts. The `:continuation_prompt` and `:alive_continuation_prompt` configuration values are no longer supported.

## Run and structure tests

### Parameterize entire ExUnit modules

Pass `parameterize: [...]` to `ExUnit.Case` to run the complete module once per parameter map. ExUnit merges the map into each test context. Instances may execute concurrently when `async: true`, and the context exposes the test process as `:test_pid`:

```elixir
use ExUnit.Case,
  async: true,
  parameterize: [%{partitions: 1}, %{partitions: 8}]
```

### Isolate shared resources with concurrency groups

Set `group: value` on async test modules. Modules in the same group never execute concurrently; modules in distinct groups may:

```elixir
use ExUnit.Case, async: true, group: :postgres
```

Every test context includes `:test_group`.

### Extend doctests and log capture

Doctest expected exceptions may use ellipses to match the remainder, and doctests accept `:inspect_opts`. `ExUnit.CaptureLog` accepts a `:formatter` option for custom log formatting.

### Select and preview tests

Use `mix test --name-pattern PATTERN` to select by name. Warning-only and failing runs now have distinguishable exit statuses. Use `mix test --dry-run` to inspect selection without executing tests.

## Inspect project graphs and source

Request machine-readable Xref graph output:

```console
mix xref graph --format json
```

Use `OptionParser` with `:regex` when a CLI option should compile a regular expression.

## Publish documentation and verify releases

### Add task-oriented ExDoc cheatsheets

Use ExDoc's dedicated Cheatsheet feature to publish concise, task-oriented quick references beside generated API documentation.

### Consume release SBOMs and attestation

Elixir releases include source SBOMs in CycloneDX 1.6 and SPDX 2.3 formats plus an attestation. Use these OpenChain ISO/IEC 5230 conformance artifacts for license-compliance and software-supply-chain verification.
