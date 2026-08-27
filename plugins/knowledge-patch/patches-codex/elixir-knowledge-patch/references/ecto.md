# Ecto Queries, Schemas, and Repositories

## Build queries

The following query capabilities are available in `ecto-3.12`.

- `Ecto.Query.is_named_binding` is a guard for recognizing named bindings.
- `distinct`, `group_by`, `order_by`, and `window` accept subqueries.
- `select_merge` works in more `insert_all` and subquery operations when the
  merge fields are distinct.
- `dynamic/2` accepts literal maps:

  ```elixir
  dynamic([post], %{id: post.id, title: post.title})
  ```

- A macro at the root of `order_by` may expand to the whole ordering
  expression.
- A query may preload a subquery used as a `from` or `join` source.
- Map-update expressions inside `select` accept dynamic values.
- The right side of query `in` accepts any `Enumerable`, including a
  `MapSet`:

  ```elixir
  from post in Post, where: post.id in ^MapSet.new(ids)
  ```

## Preload associations

Custom preload functions may have arity two. They receive both the parent IDs
and association metadata, allowing one callback to adapt its fetch to the
association being loaded (`ecto-3.12`).

## Insert and update through repositories

For `Repo.insert_all/3` in `ecto-3.12`, the supplied query may contain only a
source, without an explicit `select`, and it may use Ecto update syntax.

Repository operations on a stale struct or changeset accept
`allow_stale: true` when the write is intentionally allowed to proceed instead
of raising a stale-entry error:

```elixir
Repo.update(changeset, allow_stale: true)
```

Do not make this a blanket default; it suppresses an important concurrency
check.

## Define schemas and embeds

- Mark generated or otherwise read-only fields with `writable: :never`:

  ```elixir
  field :generated_value, :string, writable: :never
  ```

- Give `embeds_one` an embedded-struct default rather than `nil` with
  `defaults_to_struct: true`:

  ```elixir
  embeds_one :profile, Profile, defaults_to_struct: true
  ```

- Store Elixir duration values with the Ecto `:duration` type:

  ```elixir
  field :elapsed, :duration
  ```

These schema options were added in `ecto-3.12`.

## Validate and cast changes

Several `Ecto.Changeset` validators accept `{message, opts}` as the custom
message, preserving the options associated with that validation message
(`ecto-3.12`).

When a custom inner type in `{:map, type}` or `{:array, type}` returns a cast
error, Ecto now propagates that nested error instead of replacing it with a
generic container error.

## Maintain adapters and custom types

Adapter integrations upgrading to `ecto-3.12` must represent `distinct`,
`group_by`, `order_by`, and `window` as `Ecto.Query.ByExpr` structs rather than
`Ecto.Query.QueryExpr` structs.

The private parameterized-type representation is now
`{:parameterized, {module, state}}`. Never construct or inspect that tuple;
instantiate the type through `Ecto.ParameterizedType.init/2`.

The `:array_join` join type that existed for ClickHouse support has been
removed. Remove callers and adapter clauses that still emit it.
