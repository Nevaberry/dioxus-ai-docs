# Elixir Language and Core APIs

## Choose compatible runtimes

- Elixir `1.17.0` added Erlang/OTP 27 support, dropped OTP 24, and requires OTP
  25 or newer; OTP 26 or newer was recommended.
- Elixir `1.18.0` is the final Elixir release supporting OTP 25. Experimental
  PowerShell launchers exist for `elixir`, `elixirc`, and `mix`; WERL is no
  longer supported, so Windows users should use OTP 26 or newer.
- Elixir `1.19.0` supports Erlang/OTP 28.1 or newer in the OTP 28 line.
- Elixir `1.20.0` requires Erlang/OTP 27 or newer and is compatible with OTP
  29.

## Update source constructs

### Remove recursive variable cycles

Recursive pattern-variable definitions fail compilation in `1.18.0`, even
when a root-variable cycle could theoretically be satisfied. Remove the cycle
or express equality with guards:

```elixir
# rejected
def same(x = y, y = z, z = x), do: x

# accepted
def same(x, y, z) when x == y and y == z, do: x
```

### Separate scripts in identifiers

Identifier parsing follows newer UTS #55 guidance in `1.18.0`. Scripts may be
combined across underscores, as in `http_сервер`, but direct mixing such as
`Tシャツ` is rejected. The compiler also warns about bidirectionally
confusable identifiers.

### Make descending ranges explicit

Implicit negative-step inference in `Range.new/2` is deprecated in `1.18.0`.
Pass a negative step:

```elixir
Range.new(5, 1, -1)
```

### Match before struct updates

From `1.19.0`, struct update syntax requires an explicit match proving the
updated value has that struct type. Map update syntax retains its typing after
the match:

```elixir
def set_path(%URI{} = uri), do: %{uri | path: "/foo/bar"}
```

Defining a struct or exception inside `defprotocol` is rejected.

### Separate `require` from macro calls

In `1.20.0`, `require SomeModule` still returns the module at runtime, but
`require/1` no longer expands to module AST. Split previously chained code:

```elixir
require SomeModule
SomeModule.some_macro()
```

### Pin bound bitstring sizes

An already-bound bitstring size must be pinned in a pattern (`1.20.0`):

```elixir
size = 8
<<value::size(^size)>> = <<42>>
```

## Handle stricter source parsing

Elixir `1.19.0` rejects U+2028 and U+2029 in comments and strings. Other
disallowed line-break characters warn in strings and raise in comments; the
string warning becomes an error in Elixir 1.20.

Elixir `1.20.0` rejects raw carriage-return line endings in strings, comments,
and after `?`.

The `on_undefined_variable: :warn` option is hard-deprecated in `1.19.0`.
Undefined identifiers must not rely on fallback conversion into function calls.

## Encode and decode JSON

Elixir's `JSON` module in `1.18.0` encodes values, decodes binaries, and
produces encoded iodata without an external library. Object keys decode as
binaries by default. Derive `JSON.Encoder` for selected struct fields; Calendar
types already implement the protocol.

```elixir
defmodule User do
  @derive {JSON.Encoder, only: [:id, :name]}
  defstruct [:id, :name, :email]
end

json = JSON.encode!(%User{id: 1, name: "Ada"})
%{"id" => 1, "name" => "Ada"} = JSON.decode!(json)
```

## Normalize durations

`Kernel.to_timeout/1` converts integers and calendar-style durations for APIs
that accept timeouts (`1.17.0`):

```elixir
Process.send_after(pid, :wake_up, to_timeout(hour: 1))
```

## Read and copy files

`File.read/2` accepts `[:raw]` in `1.20.0`:

```elixir
File.read("data.bin", [:raw])
```

`File.cp_r/3` now skips devices, named pipes, and other special files instead
of returning `:eio`. It preserves directory permissions and avoids loops from
symlink cycles or a destination nested inside the source.

Callbacks passed positionally as the third argument of `File.cp/3` or
`File.cp_r/3` move to `on_conflict: callback` in `1.19.0`.

Call `File.stream!` in the `1.20.0` argument order:

```elixir
File.stream!(path, lines_or_bytes, modes)
```

## Use regular expressions portably

Elixir `1.19.0` on OTP 28 must not put compiled regexes in struct defaults.
Construct them at runtime instead:

```elixir
defstruct [:regex]
def new, do: %__MODULE__{regex: ~r/foo/}
```

OTP's compiled representation is runtime-specific, so recompile expressions
for each node and OTP version. A struct may implement `__escape__/1` to control
how its runtime values are handled by `Macro.escape/1`.

`OptionParser` accepts `:regex` as an option type, and `Regex.to_embed/2`
returns a representation suitable for embedding in another expression
(`1.19.0`):

```elixir
OptionParser.parse(args, strict: [pattern: :regex])
```

Use `Regex.import/1` to load a regex created with uppercase `/E` in `1.20.0`:

```elixir
regex = Regex.import(~r/foo/E)
Regex.match?(regex, "foo")
```

## Use guard-safe minimum and maximum

`min/2` and `max/2` are guard-safe in `1.19.0`:

```elixir
def lower(a, b) when min(a, b) == a, do: a
```

## Name partition supervisors through registries

`PartitionSupervisor.count_children/1` and `PartitionSupervisor.stop/3`
accept standard `{:via, module, term}` references in `1.20.0`:

```elixir
name = {:via, Registry, {MyRegistry, :partitions}}
PartitionSupervisor.count_children(name)
PartitionSupervisor.stop(name, :normal, :infinity)
```

## Customize evaluation and inspection

`Code` evaluation functions accept `:dbg_callback` in `1.20.0`, allowing an
embedded evaluator to customize `dbg`. Pipeline debugging also prints the
intermediate result of every stage.

Pretty printing in `1.19.0` consumes `:limit` across an entire nested structure
rather than resetting at each depth, so nested values can truncate sooner. The
default limit increased from 50 to 100.

`Inspect` derivation accepts `optional: :all`. Custom `Inspect.Algebra`
builders should replace soft-deprecated `next_break_fits` with optimistic or
pessimistic groups:

```elixir
@derive {Inspect, optional: :all}
```

## Migrate process and node APIs

Replace the `1.20.0` hard-deprecated Logger switches:

- `Logger.enable/1` becomes `Logger.put_process_level/2`.
- `Logger.disable/1` becomes `Logger.delete_process_level/1`.

The positional `Node.start/2-3` forms are soft-deprecated in `1.19.0`; call
`Node.start/2` with a keyword list.
