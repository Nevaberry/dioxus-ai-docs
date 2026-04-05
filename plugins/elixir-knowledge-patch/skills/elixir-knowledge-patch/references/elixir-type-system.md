# Type System & Inference

## Struct Update Syntax (1.19 — Hard Deprecation)

`%URI{uri | path: "/foo"}` now requires `uri` to have been pattern-matched on the struct first. This ensures the type system can verify the struct type.

```elixir
# Before (now deprecated):
def update(uri), do: %URI{uri | path: "/foo"}

# After:
def update(%URI{} = uri), do: %{uri | path: "/foo"}
```

## Regex Can't Be Struct Field Defaults (OTP 28)

```elixir
# This no longer works on OTP 28+:
defstruct regex: ~r/foo/

# Instead, set in constructor:
defstruct [:regex]
def new, do: %__MODULE__{regex: ~r/foo/}
```

## Full Expression Inference (1.20)

The compiler now infers types from all expressions (not just patterns). Backward inference narrows argument types from how they're used:

```elixir
def sum_to_string(a, b), do: Integer.to_string(a + b)
# Infers a, b must be integer() (not float) because Integer.to_string requires integer
```

Guard inference works too:

```elixir
def example(x) when is_map_key(x, :foo)
# Infers x is %{..., foo: dynamic()}
```

Cross-clause inference: later clauses know what previous clauses already matched:

```elixir
case System.get_env("VAR") do
  nil -> :not_found
  value -> String.upcase(value)  # value is binary(), not nil
end
```

## Map Key Typing (1.20)

Non-atom map keys are now fully tracked. The type system also tracks key presence through `Map` operations:

```elixir
Map.put(map, :key, 123)      #=> %{..., key: integer()}
Map.delete(map, :key)         #=> %{..., key: not_set()}
Map.replace(map, :key, 123)   #=> %{..., key: if_set(integer())}
```

`Map.fetch!/2`, `Map.replace!/3` etc. propagate key requirements across modules.
