# Ecto Queries, Schemas, and Repositories

## Query construction (`ecto-3.12`)

### Named-binding guard

Use `Ecto.Query.is_named_binding/1` in guards that need to recognize named query
bindings.

### Richer by-expressions

Subqueries may appear in `distinct`, `group_by`, `order_by`, and `window`.
Macros at the root of `order_by` now expand to the complete ordering expression,
so a macro may supply the whole value. Adapters must represent all four kinds as
`Ecto.Query.ByExpr`, not `Ecto.Query.QueryExpr`.

### Dynamic expressions

`dynamic/2` accepts literal maps:

```elixir
dynamic([post], %{id: post.id, title: post.title})
```

Map-update expressions inside `select` accept dynamic values. The right side of
query `in` may be any `Enumerable`, rather than only the formerly supported
concrete data structures:

```elixir
from post in Post, where: post.id in ^MapSet.new(ids)
```

### Subqueries, preloads, and merged selections

A query may preload a subquery used as the source of a `from` or `join`.
`select_merge` works in more `insert_all` and subquery operations when the fields
being merged are distinct. Custom preload functions may have arity two, receiving
both parent IDs and association metadata.

## Repository operations (`ecto-3.12`)

### `insert_all` query forms

The query passed to `Repo.insert_all/3` may contain only its source, without an
explicit select, and may use Ecto update syntax.

### Intentional stale writes

Repository operations on structs or changesets accept `allow_stale: true` when a
stale write should be permitted instead of rejected:

```elixir
Repo.update(changeset, allow_stale: true)
```

Use this only when accepting stale state is deliberate.

## Schemas, changesets, and types (`ecto-3.12`)

### Validator messages with options

Several `Ecto.Changeset` validators accept `{message, opts}` as the message, so a
custom message can carry its associated options.

### Field and embed options

Mark a schema field read-only with `writable: :never`:

```elixir
field :generated_value, :string, writable: :never
```

Set `defaults_to_struct: true` on `embeds_one` when its default should be the
embedded struct rather than `nil`:

```elixir
embeds_one :profile, Profile, defaults_to_struct: true
```

Use Ecto's `:duration` type for Elixir duration values:

```elixir
field :elapsed, :duration
```

### Nested custom cast errors

For `{:map, type}` and `{:array, type}`, cast errors from the inner custom type
now propagate instead of being replaced by a generic container error.

### Parameterized types

The private representation changed to `{:parameterized, {module, state}}`.
Never construct or inspect it directly; initialize parameterized types with
`Ecto.ParameterizedType.init/2`.

## Adapter and extension migrations (`ecto-3.12`)

- Handle `distinct`, `group_by`, `order_by`, and `window` as
  `Ecto.Query.ByExpr`.
- Initialize parameterized types through `Ecto.ParameterizedType.init/2`.
- Remove uses of the deleted `:array_join` query join type, which had been added
  for ClickHouse support.
