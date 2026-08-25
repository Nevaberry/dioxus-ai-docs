# Types and Static Analysis

## Checker scope and evolution

### Initial same-function inference (`1.17.0`)

The set-theoretic checker initially inferred types from patterns within the same
function. It could diagnose impossible map or struct fields, calls through
non-functions or non-modules, comparisons between structs or non-overlapping
types, invalid binary segments, and invalid rescue targets or fields. At this
stage it did not infer from guards or across function boundaries, and tuple,
list, and function types were not modeled in fine detail.

### Calls and returns (`1.18.0`)

Inference expanded to function inputs and returns and began checking local and
remote calls. It can warn about invalid arguments, impossible matches on results,
and private clauses that no caller can reach. At this stage `for`, `with`,
closures, and guard inference were not yet checked.

### Protocols and anonymous functions (`1.19.0`)

Protocol dispatch and implementations are checked. A warning is produced when an
inferred type cannot implement the protocol, such as interpolating a range via
`String.Chars` or using a `Date` as an `Enumerable` generator.

Anonymous functions and captures propagate their types into callers:

```elixir
fun = fn %{} -> :map end
fun.("hello") # type warning

Enum.map(values, &String.to_integer/1)
```

### All language constructs (`1.20-type-system-guide`)

Inference is now best-effort across every language construct, including guards
and constraints that flow backward from calls. It may miss incompatibilities,
but warns when every possible type combination would fail:

```elixir
def add_rem(a, b), do: rem(a + b, 8)
# rem/2 constrains a and b to integers
```

## Structural types

### Empty and non-empty lists (`1.18-type-system-guide`)

List types distinguish empty and non-empty lists. This represents guarantees such
as `String.split/2` returning a non-empty list. Guard-safe `hd/1` and `tl/1`
require a list proven non-empty; a pattern match can establish that proof.

### Improper-list tails (`1.20-type-system-guide`)

`non_empty_list(element_type, tail_type)` represents proper and improper tails.
When the tail is itself a list type, it is normalized into the element union:

```elixir
non_empty_list(integer(), list(binary()))
# equals non_empty_list(integer() or binary(), empty_list())
```

### Open tuples and indexing (`1.18-type-system-guide`)

A tuple ending in `...` has a minimum size rather than an exact size:

```elixir
{atom(), integer(), ...}
```

A literal `elem/2` index performs exact static access: the tuple must be proven
large enough, and negative or out-of-bounds indexes are rejected. A non-literal
index uses a dynamic signature, preserving possible runtime errors while exposing
the operation as dynamic to otherwise static code:

```elixir
dynamic({...a}), integer() -> dynamic(a)
```

### Guards refine structures (`1.20-type-system-guide`)

Guards infer nested structure as well as broad types. `is_map_key(x, :foo)`
establishes `%{..., foo: dynamic()}`; its negation establishes
`%{..., foo: not_set()}`. Tuple-size comparisons constrain which indexes exist.

## Set-theoretic notation (`1.20-type-system-guide`)

### Unions, intersections, and negation

Diagnostics compose types with `or`, `and`, and `not`. `none()` is the empty set
and `term()` contains every type. Every atom except `nil`, for example, is
`atom() and not nil`.

### Constrained dynamism

`dynamic(t)` means `dynamic() and t`. An operation needs to accept some member of
that range, but warns if it accepts none. Dynamism always occurs at the root, so
`{:ok, dynamic()}` normalizes to `dynamic({:ok, term()})`; it does not make only
one tuple element gradual.

### Function intersections

Arrow types use `(arguments -> result)`. A multi-clause function supporting
distinct input/output pairs belongs to every corresponding function set, so its
type joins arrows with `and`, not `or`:

```elixir
(integer() -> integer()) and (boolean() -> boolean())
```

## Map types and operations

### Open, optional, forbidden, and domain keys (`1.20-type-system-guide`)

A map type without `...` is closed to its listed keys; leading `...` makes it
open. `if_set(type)` marks a key optional, and `not_set()` forbids it:

```elixir
%{name: binary(), age: if_set(integer())}
%{..., age: not_set()}
```

Non-literal key domains use `=>` and are inherently optional. The checker tracks
only the broad top-level domain, so distinct `list(...)` key domains merge under
`list()`. Domain and literal keys may be mixed from broader to more specific;
the later literal overrides its domain:

```elixir
%{..., atom() => binary(), root: integer()}
```

### Inferred `Map` operations (`1.20.0`)

The checker models most `Map` operations:

```elixir
Map.put(map, :key, 123)     # %{..., key: integer()}
Map.delete(map, :key)       # %{..., key: not_set()}
Map.replace(map, :key, 123) # %{..., key: if_set(integer())}
```

`Map.fetch!/2`, `Map.pop!/2`, `Map.replace!/3`, and `Map.update!/3` propagate
required keys and expose calls statically known to fail.

## Control flow and module boundaries (`1.20-type-system-guide`)

### Clause-order subtraction

A later clause excludes types definitely accepted by earlier clauses, improving
its inferred input and exposing redundant clauses. A guarded earlier clause
subtracts only values that its guard certainly accepts:

```elixir
def kind(x) when is_binary(x), do: :binary
def kind(x) when is_integer(x), do: :integer
def kind(x), do: :other
```

The final `x` is neither `binary()` nor `integer()`.

### Cross-module boundaries

Inference sees the current module, standard library, and dependencies. Calls to
another module in the same project are treated as `dynamic()` during local
inference; whole-project checking still compares the inferred module types later.

### Comprehensions assume one iteration

Inference intentionally analyzes a `for` body as running at least once. This can
produce a false positive when the input may be empty. Add an explicit non-empty
guard when that distinction affects correctness.

## Dialyzer nominal types (`otp-28`)

`-nominal` declares structurally identical Erlang types that Dialyzer treats as
incompatible by name when checking inputs, outputs, and specs. A nominal type is
still compatible with a non-nominal, non-opaque type of the same structure.

```erlang
-nominal meter() :: integer().
-nominal foot() :: integer().

-spec as_meter(integer()) -> meter().
as_meter(X) -> X.
```
