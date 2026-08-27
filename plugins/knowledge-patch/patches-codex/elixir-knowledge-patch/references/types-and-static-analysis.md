# Types and Static Analysis

## Understand the checker boundary

The initial set-theoretic checker in `1.17.0` inferred from patterns inside one
function. It could warn about impossible map or struct fields, calls through
non-functions or non-modules, comparisons between structs or disjoint types,
invalid binary segments, and invalid rescue targets or fields. It did not yet
infer from guards or across function boundaries, and modeled tuples, lists,
and functions only coarsely.

In `1.18.0`, inference expanded to function inputs and returns plus local and
remote call checking. It can diagnose invalid arguments, impossible matches
on results, and private clauses unreachable by every caller. At that point,
`for`, `with`, closures, and guard inference were still outside the boundary.

By `1.20-type-system-guide`, best-effort inference covers every language
construct, including guards and constraints flowing backward from calls. It
may miss some incompatibilities, but warns when every possible type
combination fails:

```elixir
def add_rem(a, b), do: rem(a + b, 8)
# rem/2 constrains both values to integers
```

## Follow values through calls and protocols

`1.19.0` adds inference for anonymous functions. Captures such as
`&String.to_integer/1` propagate their types into callers:

```elixir
fun = fn %{} -> :map end
fun.("hello") # type warning
```

The checker also verifies protocol dispatch and implementations. It warns when
an inferred input cannot implement the protocol—for example, interpolating a
range through `String.Chars` or using `Date` as an `Enumerable` generator.

## Read guard and clause refinements

Guards refine nested shapes, not only broad types
(`1.20-type-system-guide`). For example:

- `is_map_key(x, :foo)` establishes `%{..., foo: dynamic()}`.
- Its negation establishes `%{..., foo: not_set()}`.
- Tuple-size comparisons constrain the indexes that may exist.

Clause order contributes negative information. A later clause excludes values
definitely accepted by earlier clauses; guarded clauses subtract only inputs
their guard certainly accepts:

```elixir
def kind(x) when is_binary(x), do: :binary
def kind(x) when is_integer(x), do: :integer
def kind(x), do: :other # neither binary() nor integer()
```

This refinement can also reveal redundant clauses.

## Account for cross-module inference

Inference considers the current module, the standard library, and dependencies
(`1.20-type-system-guide`). A call to another module in the same project is
treated as `dynamic()` during local inference. Whole-project checking still
compares the types inferred for all project modules afterward.

## Read set-theoretic notation

Diagnostics compose sets with `or`, `and`, and `not`. `none()` is the empty
set; `term()` is the set of all terms. Every atom except `nil`, for example,
is `atom() and not nil` (`1.20-type-system-guide`).

`dynamic(t)` means `dynamic() and t`. An operation only needs to accept some
member of the range, but it warns when it accepts none. Dynamism is always at
the root: `{:ok, dynamic()}` normalizes to
`dynamic({:ok, term()})`, rather than making only one tuple element gradual.

Function arrows use `(arguments -> result)`. A multi-clause function that
supports distinct input/output pairs belongs to all the corresponding function
sets, so its complete type joins arrows with `and`, not `or`:

```elixir
(integer() -> integer()) and (boolean() -> boolean())
```

## Model lists

`1.18-type-system-guide` distinguishes empty and non-empty lists, allowing a
guarantee such as `String.split/2` returning a non-empty list to be represented.
Guard-safe `hd/1` and `tl/1` require proof that the input is non-empty; a
pattern match can supply it.

In `1.20-type-system-guide`,
`non_empty_list(element_type, tail_type)` describes proper and improper list
tails. If the tail is itself a list, it normalizes into the element union:

```elixir
non_empty_list(integer(), list(binary()))
# equals non_empty_list(integer() or binary(), empty_list())
```

## Model tuples and indexes

An open tuple ends in `...` and specifies only a minimum size
(`1.18-type-system-guide`):

```elixir
{atom(), integer(), ...}
```

For a literal index, `elem/2` performs exact static access: the checker must
prove the tuple is large enough and rejects negative or out-of-range indexes.
A non-literal index uses a dynamic signature, preserving the possible runtime
error while making the dynamic boundary visible:

```elixir
dynamic({...a}), integer() -> dynamic(a)
```

## Model map shapes and operations

In `1.20-type-system-guide`, a map without `...` is closed to its listed keys;
leading `...` makes it open. `if_set(type)` marks an optional key, and
`not_set()` proves a key cannot occur:

```elixir
%{name: binary(), age: if_set(integer())}
%{..., age: not_set()}
```

Non-literal key domains use `=>` and are inherently optional. The checker
tracks only their broad top-level domain, so distinct `list(...)` domains merge
under `list()`. Mix domain and literal keys from broad to specific; a later
literal key overrides its broader domain:

```elixir
%{..., atom() => binary(), root: integer()}
```

The `1.20.0` checker models most `Map` operations:

```elixir
Map.put(map, :key, 123)     # %{..., key: integer()}
Map.delete(map, :key)       # %{..., key: not_set()}
Map.replace(map, :key, 123) # %{..., key: if_set(integer())}
```

Bang operations including `Map.fetch!/2`, `Map.pop!/2`, `Map.replace!/3`, and
`Map.update!/3` propagate required keys and expose calls statically known to
fail.

## Handle comprehension inference

Inference assumes a `for` body runs at least once
(`1.20-type-system-guide`). Constraints learned inside it can therefore cause
a false positive if the input may really be empty. When the distinction
matters, guard the comprehension with an explicit non-empty check.

## Declare nominal Dialyzer types

The `-nominal` attribute in `otp-28` declares structurally identical types
that Dialyzer treats as incompatible by name when checking specs, inputs, and
outputs. A nominal type remains compatible with a non-nominal, non-opaque type
of the same structure.

```erlang
-nominal meter() :: integer().
-nominal foot() :: integer().

-spec as_meter(integer()) -> meter().
as_meter(X) -> X.
```
