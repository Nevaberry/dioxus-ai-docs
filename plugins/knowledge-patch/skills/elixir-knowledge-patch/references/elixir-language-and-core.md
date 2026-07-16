# Elixir Language and Core APIs

Batch attribution: `1.17.0`, `1.18.0`, `1.19.0`, and `1.20.0`.

## Contents

- [Runtime compatibility](#runtime-compatibility)
- [Syntax and parsing migrations](#syntax-and-parsing-migrations)
- [JSON and data representation](#json-and-data-representation)
- [Time, guards, and collections](#time-guards-and-collections)
- [Files, regexes, and processes](#files-regexes-and-processes)
- [Protocols and derivation](#protocols-and-derivation)
- [Debug evaluation](#debug-evaluation)

## Runtime compatibility

- Elixir 1.17 supports Erlang/OTP 27, drops OTP 24, requires OTP 25 or newer, and recommends OTP 26 or newer.
- Elixir 1.18 is the final release supporting OTP 25. Use OTP 26 or newer on Windows; WERL is no longer supported. Experimental PowerShell entry scripts are available for `elixir`, `elixirc`, and `mix`.
- Elixir 1.19 requires Erlang/OTP 28.1 or newer when running on OTP 28.
- Elixir 1.20 requires Erlang/OTP 27 or newer and is compatible with OTP 29.

## Syntax and parsing migrations

### Remove recursive pattern-variable cycles

Recursive variable definitions fail compilation, even when a cycle consists only of root variables and could be satisfied. Remove the cycle or state equality in guards:

```elixir
# rejected
def same(x = y, y = z, z = x), do: x

# accepted
def same(x, y, z) when x == y and y == z, do: x
```

### Follow mixed-script identifier rules

Identifier parsing follows the newer UTS #55 guidance. Combine different scripts only across underscore-delimited segments, such as `http_сервер`; direct mixing such as `Tシャツ` is rejected. The compiler warns about bidirectionally confusable identifiers.

### Make descending ranges explicit

Inferring a negative step in `Range.new/2` is deprecated. Supply it explicitly:

```elixir
Range.new(5, 1, -1)
```

### Match structs before updating them

The updated expression in struct-update syntax must have been explicitly matched as that struct. After the match, map-update syntax keeps the same typing guarantees:

```elixir
def set_path(%URI{} = uri), do: %{uri | path: "/foo/bar"}
```

### Pin bound bitstring sizes

Pin an already-bound size used in a bitstring pattern:

```elixir
size = 8
<<value::size(^size)>> = <<42>>
```

### Account for stricter line parsing

- Raw carriage-return line endings are rejected in strings, comments, and after `?`.
- U+2028 and U+2029 raise in comments and strings.
- Other disallowed line-break characters raise in comments and warn in strings; that string warning becomes an error in Elixir 1.20.
- `Code.string_to_quoted/2` returns an error for invalid Unicode instead of raising and accepts an `:indentation` option for embedded source.

### Separate `require` from macro calls

`require SomeModule` still evaluates to the module at runtime, but its macro expansion no longer produces module AST. Do not chain a macro call from `require(SomeModule)`:

```elixir
require SomeModule
SomeModule.some_macro()
```

### Stop relying on undefined-variable fallback

The `on_undefined_variable: :warn` option is hard-deprecated. Undefined identifiers must not be treated as implicit function calls.

## JSON and data representation

### Use the built-in `JSON` module

Encode, decode, or produce encoded iodata without an external JSON library. Decoded object keys are binaries by default. Derive `JSON.Encoder` for selected struct fields; Calendar types have built-in implementations:

```elixir
defmodule User do
  @derive {JSON.Encoder, only: [:id, :name]}
  defstruct [:id, :name, :email]
end

json = JSON.encode!(%User{id: 1, name: "Ada"})
%{"id" => 1, "name" => "Ada"} = JSON.decode!(json)
```

### Expect whole-structure inspect limits

Pretty printing spends `:limit` across an entire nested structure instead of restarting the allowance at every depth, so deeply nested values may truncate earlier. The default limit is 100 rather than 50.

Derive `Inspect` with `optional: :all` when every field may be omitted. In custom `Inspect.Algebra` document builders, replace the soft-deprecated `next_break_fits` with optimistic or pessimistic groups.

### Customize runtime escaping

Structs may define `__escape__/1` to control how runtime values are escaped by `Macro.escape/1`.

## Time, guards, and collections

### Normalize durations as timeouts

Use `Kernel.to_timeout/1` to normalize integer or calendar-style durations for timeout-taking APIs:

```elixir
Process.send_after(pid, :wake_up, to_timeout(hour: 1))
```

### Use minimum and maximum in guards

`min/2` and `max/2` are guard-safe:

```elixir
def lower(a, b) when min(a, b) == a, do: a
```

### Let map operations refine types

The checker tracks most `Map` operations. `put` makes a key present, `delete` makes it absent, and `replace` leaves it optional:

```elixir
Map.put(map, :key, 123)     # %{..., key: integer()}
Map.delete(map, :key)       # %{..., key: not_set()}
Map.replace(map, :key, 123) # %{..., key: if_set(integer())}
```

`Map.fetch!/2`, `Map.pop!/2`, `Map.replace!/3`, and `Map.update!/3` propagate required-key information and expose calls known statically to fail.

## Files, regexes, and processes

### Read and copy files safely

`File.read/2` accepts `[:raw]`:

```elixir
File.read("data.bin", [:raw])
```

`File.cp_r/3` skips devices, named pipes, and other special files rather than failing with `:eio`. Recursive copies preserve directory permissions and avoid loops from symlink cycles or a destination inside the source.

Callbacks formerly passed as the third positional argument to `File.cp/3` or `File.cp_r/3` move to `on_conflict: callback`.

Use `File.stream!(path, lines_or_bytes, modes)` instead of the hard-deprecated old argument order.

### Construct and import regexes

- `OptionParser` can parse `:regex` option values.
- `Regex.to_embed/2` returns a representation suitable for embedding in another regex.
- Define a regular expression with uppercase `/E`, then load it with `Regex.import/1`:

```elixir
regex = Regex.import(~r/foo/E)
Regex.match?(regex, "foo")
```

On Erlang/OTP 28, do not use a compiled regex as a struct field default. Initialize it while constructing the struct:

```elixir
defstruct [:regex]
def new, do: %__MODULE__{regex: ~r/foo/}
```

### Name partition supervisors through registries

`PartitionSupervisor.count_children/1` and `PartitionSupervisor.stop/3` accept standard `{:via, module, term}` references:

```elixir
name = {:via, Registry, {MyRegistry, :partitions}}
PartitionSupervisor.count_children(name)
PartitionSupervisor.stop(name, :normal, :infinity)
```

### Use current node and logger APIs

- Replace positional `Node.start/2-3` calls with `Node.start/2` and a keyword list.
- Replace `Logger.enable/1` and `Logger.disable/1` with `Logger.put_process_level/2` and `Logger.delete_process_level/1`.
- Replace Logger's deprecated `:backends` setting by disabling `:default_handler` or starting custom backends from the application start callback.

## Protocols and derivation

### Let protocols own deriving

A protocol can define an optional `__deriving__/1` macro callback without requiring an empty implementation. Defining the older `__deriving__/3` callback in the protocol's `Any` implementation is deprecated.

Do not define a struct or exception inside `defprotocol`; the compiler rejects it.

## Debug evaluation

Pass `:dbg_callback` to `Code` evaluation functions when an embedded evaluator must customize `dbg` handling. A pipeline passed to `dbg` prints every intermediate stage, not only the final result.
