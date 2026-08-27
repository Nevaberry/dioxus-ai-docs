---
name: elixir-knowledge-patch
description: Elixir
version: "1.20.0-rc"
license: MIT
metadata:
  author: Nevaberry
---


# Elixir Knowledge Patch

Use this index to load only the references relevant to the task. Apply migration
notes before adopting newer APIs, especially when upgrading an existing runtime,
application, or framework dependency.

## Reference index

| Reference | Topics |
|---|---|
| [ecto.md](references/ecto.md) | Ecto queries, schemas, changesets, repositories, adapter migrations |
| [elixir-language-and-core.md](references/elixir-language-and-core.md) | Elixir syntax, core APIs, JSON, files, regexes, processes, compatibility |
| [erlang-otp.md](references/erlang-otp.md) | Erlang syntax and libraries, processes, tracing, profiling, storage, security |
| [interop-and-portability.md](references/interop-and-portability.md) | Browser Elixir, C++, Zig, Python, and Swift interoperability |
| [phoenix-and-liveview.md](references/phoenix-and-liveview.md) | Phoenix generators and scopes, layouts, authentication, LiveView components and tests |
| [tooling-testing-and-releases.md](references/tooling-testing-and-releases.md) | Mix, compiler behavior, formatter, IEx, ExUnit, ExDoc, release artifacts |
| [types-and-static-analysis.md](references/types-and-static-analysis.md) | Set-theoretic types, inference, diagnostics, Dialyzer nominal types |

## Breaking changes and required migrations

### Check runtime compatibility

- Run Elixir 1.20 on Erlang/OTP 27 or newer; it is compatible with OTP 29.
- Run Phoenix 1.8 on OTP 25 or newer; when upgrading, install its matching generator with `mix archive.install hex phx_new 1.8.0 --force`.
- Treat Elixir 1.18 as the last release supporting OTP 25. On Windows, use OTP
  26 or newer; WERL is unsupported.

### Update source constructs

- Split `require(SomeModule).some_macro()` into `require SomeModule` followed by `SomeModule.some_macro()`; `require/1` no longer expands to module AST.
- Pin an already-bound bitstring size: `<<value::size(^size)>>`.
- Explicitly match a struct before updating it:
  `def set_path(%URI{} = uri), do: %{uri | path: "/"}`.
- Remove recursive pattern-variable cycles and express equality in guards.
- Separate scripts in identifiers with underscores. Direct mixed-script
  identifiers are rejected, and bidirectional confusables warn.
- Give descending `Range.new/3` calls an explicit negative step.
- Remove raw carriage returns and U+2028/U+2029 line breaks from affected source
  strings and comments.

### Migrate deprecated APIs and options

- Call `File.stream!(path, lines_or_bytes, modes)` in that order.
- Replace `Logger.enable/1` and `Logger.disable/1` with `Logger.put_process_level/2` and `Logger.delete_process_level/1`.
- Replace Logger `:backends` configuration by disabling `:default_handler` or
  starting custom backends from the application callback.
- Move `xref: [exclude: ...]` to `elixirc_options: [no_warn_undefined: ...]`.
- Move `:default_task`, `:preferred_cli_env`, and `:preferred_cli_target` from
  `project/0` to `cli/0` as `:default_task`, `:preferred_envs`, and
  `:preferred_targets`.
- Join `mix do` tasks with `+`, rename `--no-protocol-consolidation` to `--no-consolidate-protocols`, and stop invoking inert `mix compile.protocols`.
- Pass `--warnings-as-errors` to `mix compile` or `mix test`; do not set `:warnings_as_errors` through compiler options.
- Use `mix do --app APP` instead of `mix cmd --app APP`. `mix cmd` now preserves
  quoting and skips shell expansion unless `--shell` precedes the command.
- Replace `List.zip/1`, `Module.eval_quoted/3`, `Tuple.append/2`, and
  `Mix.Tasks.Compile.compilers/0` with `Enum.zip/1`, `Code.eval_quoted/3`,
  `Tuple.insert_at/3`, and `Mix.Task.Compiler.compilers/0`.
- Write EEx comments as `<%!-- ... --%>` or `<% # ... %>`, and implement `EEx.handle_text/3` rather than arity two.
- Replace protocol `Any.__deriving__/3` callbacks with a protocol-owned optional
  `__deriving__/1` macro.

### Account for compiler and regex behavior

- Do not assume project modules load immediately during compilation. Use `Kernel.ParallelCompiler.pmap/2` or `Code.ensure_compiled!/1` before spawning compiler-time work.
- Pass `return_diagnostics: true` to `Kernel.ParallelCompiler.compile`, `compile_to_path`, and `require`.
- Do not define a struct or exception inside `defprotocol`.
- Initialize regex struct fields at construction time on OTP 28 rather than
  using compiled regexes as struct defaults.
- Recompile regexes per node and runtime version. OTP's PCRE2-backed `re` parser rejects some formerly tolerated escapes, and compiled representations are not portable.
- Replace `Inspect.Algebra.next_break_fits` with optimistic or pessimistic
  groups.
- Remove `on_undefined_variable: :warn`; undefined identifiers no longer fall
  back to function calls.

### Update Ecto integrations

- Make adapters handle `distinct`, `group_by`, `order_by`, and `window` as `Ecto.Query.ByExpr`, not `QueryExpr`.
- Initialize parameterized types with `Ecto.ParameterizedType.init/2`; do not
  depend on their changed private tuple representation.
- Remove the deleted `:array_join` join type.
- Use `allow_stale: true` only when intentionally accepting a stale struct or
  changeset write.

### Upgrade LiveView wiring and tests

- Put `:phoenix_live_view` before standard Mix compilers, add LazyHTML for tests, and remove Floki only if no other dependency uses it.
- For colocated code, update esbuild, add `--alias:@=.`, and configure
  `NODE_PATH` for dependency and build paths.
- Rename old global hook names beginning with `.`; leading-dot colocated hooks
  are now module-prefixed.
- Replace Floki-only `fl-contains` and `fl-icontains` selectors with LiveViewTest
  text filters.
- Fix duplicate DOM and LiveComponent IDs; `live/3` and `live_isolated/3` raise for duplicates by default.
- Add `annotate_slot/4` to custom `Phoenix.LiveView.TagEngine`
  implementations.

## Core language quick reference

### Use built-in JSON

Encode and decode with `JSON`; object keys decode as binaries. Derive selected
struct fields through `JSON.Encoder`:

```elixir
defmodule User do
  @derive {JSON.Encoder, only: [:id, :name]}
  defstruct [:id, :name, :email]
end

json = JSON.encode!(%User{id: 1, name: "Ada"})
%{"id" => 1, "name" => "Ada"} = JSON.decode!(json)
```

Calendar types already implement the protocol. In Erlang, the `json` module
also decodes object keys as binaries by default.

### Read type warnings structurally

- Expect inference across guards, anonymous functions, protocols, calls, returns, and all other language constructs.
- Read `dynamic(t)` as `dynamic() and t`, not as an unconstrained escape hatch.
- Write open maps with leading `...`, optional fields with `if_set(type)`,
  forbidden fields with `not_set()`, and open tuples with trailing `...`.
- Remember that later clauses exclude inputs definitely accepted earlier.
- During local inference, another module in the same project is `dynamic()`; whole-project checking still compares modules afterward.
- Guard a comprehension with an explicit non-empty check when one-iteration
  inference creates a false positive.

### Use inferred map operations

```elixir
Map.put(map, :key, 123)     # key becomes required
Map.delete(map, :key)       # key becomes forbidden
Map.replace(map, :key, 123) # key remains optional
```

Bang operations propagate required-key information and reveal calls statically
known to fail.

### Reach for current core APIs

- Normalize calendar-style durations with `Kernel.to_timeout/1`.
- Use `File.read(path, [:raw])` for raw reads. `File.cp_r/3` skips special files, preserves directory permissions, and avoids symlink and nested-destination loops.
- Import uppercase `/E` regular expressions with `Regex.import/1`; use
  `Regex.to_embed/2` when embedding one regex in another.
- Use `min/2` and `max/2` in guards.
- Pass `{:via, module, term}` names to `PartitionSupervisor.count_children/1` and `stop/3`.
- Customize embedded `dbg` evaluation with `:dbg_callback`; pipeline debugging
  prints every intermediate stage.

## Testing, compilation, and framework quick reference

### Structure concurrent ExUnit suites

```elixir
use ExUnit.Case,
  async: true,
  group: :postgres,
  parameterize: [%{partitions: 1}, %{partitions: 8}]
```

Read parameter values from the test context. It also includes `:test_pid` and
`:test_group`. Doctests support exception-tail ellipses and `:inspect_opts`.

### Reach for current Mix and IEx commands

```console
mix source Enum.map/2
mix format --no-compile
mix test --dry-run
mix test --name-pattern PATTERN
mix xref graph --format json
```

Use `MIX_OS_DEPS_COMPILE_PARTITION_COUNT` to compile dependencies across OS
processes, balancing speed against memory. Use
`ERL_COMPILER_OPTIONS=deterministic` only when stripped source and compile
metadata are acceptable.

### Compose Ecto queries and schemas

- Use subqueries in by-expressions, literal maps in `dynamic/2`, dynamic values in selected map updates, and any `Enumerable` on the right of query `in`.
- Let root `order_by` macros expand to the full expression and preload subquery
  sources.
- Use arity-two custom preload functions to receive parent IDs and association
  metadata.
- Supply source-only or update-syntax queries to `Repo.insert_all/3`; use the
  broader `select_merge` support for distinct fields.
- Mark read-only fields with `writable: :never`, default `embeds_one` values
  with `defaults_to_struct: true`, and store durations with `:duration`.

### Build LiveView interfaces

- Define colocated hooks with `Phoenix.LiveView.ColocatedHook` and arbitrary colocated JavaScript with `Phoenix.LiveView.ColocatedJS`; merge generated hooks into the `LiveSocket` configuration.
- Add `:key` to comprehensions when identity must survive insertion or
  reordering; prefer streams for very large collections.
- Render elsewhere in the DOM with `Phoenix.Component.portal/1` while retaining LiveView event ownership.
- Preserve browser-controlled attributes with `JS.ignore_attributes/1`.
- Use `stream_insert(..., update_only: true)` to update without inserting.
- Enable `debug_heex_annotations` and `debug_attributes` for definition,
  caller, slot, line, and LiveView PID annotations.

### Follow Phoenix-generated boundaries

- Expect magic-link authentication by default and use generated
  `require_sudo_mode` for recently authenticated operations.
- Pass the generated application-owned scope through contexts, queries, foreign
  keys, PubSub topics, and authenticated LiveView sessions.
- Call app layout function components explicitly so each layout can accept its
  own assigns and slots.
- Treat Tailwind v4, daisyUI, themes, and the layout theme toggle as generator
  defaults, not requirements of `phx.gen.*` output.

## Erlang/OTP quick reference

- Send priority messages only through a priority alias and the `priority` send option; prioritize exit, link, and monitor signals through their APIs.
- Use strict comprehension generators (`<:-`, `<:=`) when non-matches must
  fail, and zip generators with `&&` for parallel iteration.
- Treat native records and comprehension assignment as experimental features.
- Prefer immutable `graph` when persistent graph versions are useful.
- Cap tar extraction with `{max_size, Size}`.
- Explicitly enable required SSH shell, exec, and SFTP services. SSL and SSH
  prefer hybrid ML-KEM-768/X25519 and fall back for older peers.
- Use `proc_lib` labels, independent `trace` sessions, unified `tprof`, and
  native coverage to diagnose runtime behavior.

## Interoperability selection

- Use Popcorn for an AtomVM WebAssembly subset in the browser or Hologram for
  Phoenix-based isomorphic components transpiled to JavaScript.
- Use Fine for signature-driven C++ NIFs or Zigler for inline Zig compiled at
  build time.
- Use Pythonx for in-process Python with `uv`-managed dependencies; account for
  GIL serialization unless native packages release it.
- Use the Swift Erlang Actor System when a Swift program must participate as a
  distributed node.
