# Types and Static Analysis

Batch attribution: `1.17.0`, `1.18-type-system-guide`, `1.18.0`, `1.19.0`, `1.20-type-system-guide`, `1.20.0`, and `otp-28`.

## Contents

- [Understand checker scope](#understand-checker-scope)
- [Read set-theoretic notation](#read-set-theoretic-notation)
- [Refine maps with guards and operations](#refine-maps-with-guards-and-operations)
- [Describe lists and tuples](#describe-lists-and-tuples)
- [Read function and protocol types](#read-function-and-protocol-types)
- [Avoid inference traps](#avoid-inference-traps)
- [Use nominal Dialyzer types in Erlang](#use-nominal-dialyzer-types-in-erlang)

## Understand checker scope

### Treat warnings as best-effort proofs

The set-theoretic checker warns when every possible type combination would fail. It may miss an incompatibility when gradual or uninferred values leave at least one successful possibility.

Its inference scope expanded across releases:

- In Elixir 1.17, inference comes from patterns within the same function. It can identify impossible map or struct fields, calls through non-functions or non-modules, comparisons between structs or disjoint types, invalid binary segments, and invalid rescue targets or fields. It does not infer from guards or across function boundaries, and tuple, list, and function types remain coarse.
- In Elixir 1.18, it infers function inputs and returns, checks local and remote calls, warns on impossible matches against call results, and identifies private clauses no caller can reach. `for`, `with`, closures, and guard inference remain outside that release's checker.
- In Elixir 1.19, it infers anonymous functions and captures and checks protocol dispatch and implementations.
- In Elixir 1.20, best-effort inference spans every language construct, including guards and constraints that flow backward from calls.

```elixir
def add_rem(a, b), do: rem(a + b, 8)
# rem/2 constrains both a and b to integers through the addition
```

### Respect module boundaries

Function inference considers the current module, the standard library, and dependencies. During local inference, a call to another module in the same project is treated as `dynamic()`. Whole-project checking still compares the types inferred for all project modules afterward.

### Let earlier clauses subtract types

A later clause excludes inputs definitely accepted by earlier clauses, improving its inferred input and exposing redundant clauses. A guarded clause subtracts only the values its guard is certain to accept:

```elixir
def kind(x) when is_binary(x), do: :binary
def kind(x) when is_integer(x), do: :integer
def kind(x), do: :other # neither binary() nor integer()
```

## Read set-theoretic notation

### Compose sets explicitly

Diagnostics combine types with `or`, `and`, and `not`. `none()` is the empty set; `term()` contains every type. For example, `atom() and not nil` means every atom except `nil`.

### Interpret `dynamic()` as a constrained range

`dynamic(t)` is `dynamic() and t`. An operation on that value must accept at least one member of the range and warns when it accepts none. Dynamism always sits at the root: `{:ok, dynamic()}` normalizes to `dynamic({:ok, term()})`, not to a fully static tuple with only a dynamic element.

## Refine maps with guards and operations

### Infer presence and absence from guards

Guards refine nested structures, not only broad types. `is_map_key(x, :foo)` establishes `%{..., foo: dynamic()}`; its negation establishes `%{..., foo: not_set()}`. Tuple-size comparisons similarly constrain which tuple indexes may exist.

### Distinguish closed, open, optional, and forbidden maps

A map type without `...` is closed to the listed keys. Put `...` first to make it open. Use `if_set(type)` for an optional key and `not_set()` for a key that must be absent:

```elixir
%{name: binary(), age: if_set(integer())}
%{..., age: not_set()}
```

### Order domain and literal keys by specificity

Write non-literal key domains with `=>`; they are inherently optional. The checker records only their broad top-level domain, so distinct `list(...)` domains merge under `list()`. Mix domain and literal entries in increasing specificity so a later literal key overrides its broader domain:

```elixir
%{..., atom() => binary(), root: integer()}
```

### Track key information through `Map`

Most `Map` operations preserve inferred shape information:

```elixir
Map.put(map, :key, 123)     # %{..., key: integer()}
Map.delete(map, :key)       # %{..., key: not_set()}
Map.replace(map, :key, 123) # %{..., key: if_set(integer())}
```

Bang operations including `Map.fetch!/2`, `Map.pop!/2`, `Map.replace!/3`, and `Map.update!/3` propagate required keys and reveal statically certain failures.

## Describe lists and tuples

### Prove a list is non-empty

List types distinguish empty and non-empty lists, allowing guarantees such as `String.split/2` returning a non-empty list. Guard-safe `hd/1` and `tl/1` require proof of a non-empty input; establish it with pattern matching or a suitable guard.

### Represent improper-list tails

`non_empty_list(element_type, tail_type)` represents both proper and improper tails. When the tail is another list type, normalize its elements into the outer element union:

```elixir
non_empty_list(integer(), list(binary()))
# equals non_empty_list(integer() or binary(), empty_list())
```

### Write open tuples

End a tuple type with `...` to express a minimum size while constraining only known positions:

```elixir
{atom(), integer(), ...}
```

### Distinguish literal and dynamic tuple indexing

With a literal index, `elem/2` is exact static access: the checker must prove the tuple is large enough and rejects negative or out-of-bounds indexes. A non-literal index uses a dynamic signature, retaining the possible runtime error while marking the operation dynamic to fully static code:

```elixir
dynamic({...a}), integer() -> dynamic(a)
```

## Read function and protocol types

### Join clauses as intersections

Arrow types use `(arguments -> result)`. A function supporting distinct input/output pairs belongs to every corresponding function set, so join its arrows with `and`, not `or`:

```elixir
(integer() -> integer()) and (boolean() -> boolean())
```

### Propagate anonymous-function and capture types

Anonymous functions are inferred and checked. Captures such as `&String.to_integer/1` carry their types into callers:

```elixir
fun = fn %{} -> :map end
fun.("hello") # type warning
```

### Check protocol dispatch

The checker verifies both dispatch and implementations. It warns when an inferred type cannot implement the required protocol, such as interpolating a range through `String.Chars` or using a `Date` as an `Enumerable` generator.

## Avoid inference traps

### Guard possibly empty comprehensions

Inference intentionally treats a `for` body as executing at least once. Constraints learned inside the body can therefore cause a false positive when the input may actually be empty. When that distinction matters, branch on an explicit non-empty check before the comprehension.

### Do not create recursive variable cycles

Recursive pattern-variable definitions are compile errors, including satisfiable cycles made only from root variables. Express equality with guards:

```elixir
def same(x, y, z) when x == y and y == z, do: x
```

### Match a struct before its update

The checker requires the value in struct-update syntax to have been explicitly matched as that struct:

```elixir
def set_path(%URI{} = uri), do: %{uri | path: "/foo/bar"}
```

## Use nominal Dialyzer types in Erlang

Declare `-nominal` types when structural equality must not make two named concepts interchangeable in specs, inputs, and outputs:

```erlang
-nominal meter() :: integer().
-nominal foot() :: integer().
```

A nominal type remains compatible with a non-nominal, non-opaque type that has the same structure.
