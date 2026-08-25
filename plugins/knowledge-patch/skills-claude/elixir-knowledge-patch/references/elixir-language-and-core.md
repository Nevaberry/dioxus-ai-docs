# Elixir Language and Core APIs

## Runtime compatibility

- Elixir 1.17 (`1.17.0`) supports Erlang/OTP 27, drops OTP 24, and requires OTP
  25 or newer; OTP 26 or newer was recommended.
- Elixir 1.18 (`1.18.0`) is the final Elixir release supporting OTP 25. Windows
  users should use OTP 26 or newer. Experimental PowerShell launchers exist for
  `elixir`, `elixirc`, and `mix`; WERL is unsupported.
- Elixir 1.19 (`1.19.0`) supports Erlang/OTP 28.1 or newer within the OTP 28
  line.
- Elixir 1.20 (`1.20.0`) requires Erlang/OTP 27 or newer and is compatible with
  OTP 29.

## Syntax and source migrations

### Recursive pattern variables (`1.18.0`)

Recursive variable definitions fail compilation, including satisfiable cycles
formed only from root variables. Remove the cycle or express equality in guards:

```elixir
# rejected
def same(x = y, y = z, z = x), do: x

# accepted
def same(x, y, z) when x == y and y == z, do: x
```

### Mixed-script identifiers (`1.18.0`)

Identifiers follow newer UTS #55 guidance. Different scripts may be combined
when separated by underscores, as in `http_сервер`; direct mixing such as
`Tシャツ` is rejected. The compiler warns about bidirectionally confusable
identifiers.

### Explicit descending ranges (`1.18.0`)

Implicitly choosing a negative step in `Range.new/2` is deprecated. Supply it:

```elixir
Range.new(5, 1, -1)
```

### Line-break validation (`1.19.0`, `1.20.0`)

U+2028 and U+2029 raise in comments and strings. Other disallowed line-break
characters warn in strings and raise in comments; the string warning was
scheduled to become an error in Elixir 1.20. Raw carriage-return line endings are
rejected in strings, comments, and after `?`.

### Struct updates require an established type (`1.19.0`)

Explicitly match the value as the struct before using update syntax. Ordinary map
update syntax retains the same typing guarantees after the match:

```elixir
def set_path(%URI{} = uri), do: %{uri | path: "/foo/bar"}
```

### Pinned bitstring sizes (`1.20.0`)

Pin an already-bound size inside a bitstring pattern:

```elixir
size = 8
<<value::size(^size)>> = <<42>>
```

### Separate `require` from macro calls (`1.20.0`)

`require SomeModule` still returns the module at runtime, but its macro expansion
no longer produces module AST. Split chained calls:

```elixir
require SomeModule
SomeModule.some_macro()
```

Do not write `require(SomeModule).some_macro()`.

## JSON (`1.18.0`)

The built-in `JSON` module encodes, decodes, and produces encoded iodata without
an external library. Object keys decode as binaries. Custom structs implement
`JSON.Encoder`, which can be derived for selected fields; Calendar types already
implement it.

```elixir
defmodule User do
  @derive {JSON.Encoder, only: [:id, :name]}
  defstruct [:id, :name, :email]
end

json = JSON.encode!(%User{id: 1, name: "Ada"})
%{"id" => 1, "name" => "Ada"} = JSON.decode!(json)
```

## Timeouts, processes, and debugging

### Duration-based timeouts (`1.17.0`)

`Kernel.to_timeout/1` normalizes integers and calendar-style durations for APIs
that expect a timeout:

```elixir
Process.send_after(pid, :wake_up, to_timeout(hour: 1))
```

### Via names for partition supervisors (`1.20.0`)

`PartitionSupervisor.count_children/1` and `PartitionSupervisor.stop/3` accept
standard `{:via, module, term}` references:

```elixir
name = {:via, Registry, {MyRegistry, :partitions}}
PartitionSupervisor.count_children(name)
PartitionSupervisor.stop(name, :normal, :infinity)
```

### Custom `dbg` evaluation (`1.20.0`)

The `Code` evaluation functions accept `:dbg_callback`, allowing embedded
evaluators to customize `dbg`. Pipeline debugging now prints every intermediate
stage.

## Files, regexes, and inspection

### Raw reads and recursive copies (`1.20.0`)

`File.read/2` accepts `[:raw]`:

```elixir
File.read("data.bin", [:raw])
```

`File.cp_r/3` skips devices, named pipes, and other special files instead of
failing with `:eio`. It preserves directory permissions and avoids loops caused
by symlink cycles or a destination nested inside the source.

### File callback and stream migrations (`1.19.0`, `1.20.0`)

Pass a copy conflict callback as `on_conflict: callback` rather than the third
positional argument to `File.cp/3` or `File.cp_r/3`. Call
`File.stream!(path, lines_or_bytes, modes)` in that argument order.

### OTP 28 regex construction (`1.19.0`)

Regexes cannot be struct field defaults on OTP 28. Initialize them while
constructing the struct. A struct may implement `__escape__/1` to control how
runtime values are escaped by `Macro.escape/1`.

```elixir
defstruct [:regex]
def new, do: %__MODULE__{regex: ~r/foo/}
```

### Regex option APIs (`1.19.0`, `1.20.0`)

`OptionParser` accepts `:regex` as an option type. `Regex.to_embed/2` produces a
representation for embedding one regular expression in another. Import a regex
created with uppercase `/E` by calling `Regex.import/1`:

```elixir
OptionParser.parse(args, strict: [pattern: :regex])
regex = Regex.import(~r/foo/E)
Regex.match?(regex, "foo")
```

### Whole-structure inspect limits (`1.19.0`)

Pretty printing consumes `:limit` across a whole nested structure rather than
separately at each depth, so deep values may truncate sooner. The default limit
increased from 50 to 100.

`Inspect` derivation accepts `optional: :all`. Replace the soft-deprecated
`Inspect.Algebra.next_break_fits` in custom documents with optimistic or
pessimistic groups.

```elixir
@derive {Inspect, optional: :all}
```

## Core and protocol migrations

### Guard-safe minimum and maximum (`1.19.0`)

`min/2` and `max/2` are guard-safe:

```elixir
def lower(a, b) when min(a, b) == a, do: a
```

### Protocol-owned deriving (`1.18.0`)

A protocol may define its own optional `__deriving__/1` macro callback without
requiring an empty implementation. The older `__deriving__/3` callback in the
protocol's `Any` implementation is deprecated.

Defining a struct or exception inside `defprotocol` is rejected (`1.19.0`).

### Undefined-variable fallback (`1.19.0`)

`on_undefined_variable: :warn` is hard-deprecated. Do not rely on an undefined
identifier being converted into a function call.

### Core API replacements (`1.18.0`)

- Replace `List.zip/1` with `Enum.zip/1`.
- Replace `Module.eval_quoted/3` with `Code.eval_quoted/3`.
- Replace `Tuple.append/2` with `Tuple.insert_at/3`.
- Write EEx comments as `<%!-- ... --%>` or `<% # ... %>`, not `<%#`.
- Implement `EEx.handle_text/3`, not arity two.

### Node and Logger configuration (`1.19.0`, `1.20.0`)

Use `Node.start/2` with a keyword list instead of the soft-deprecated positional
`Node.start/2-3` forms. Replace Logger's deprecated `:backends` setting by
disabling `:default_handler` or starting custom backends from the application
start callback. Replace `Logger.enable/1` and `Logger.disable/1` with
`Logger.put_process_level/2` and `Logger.delete_process_level/1`.
