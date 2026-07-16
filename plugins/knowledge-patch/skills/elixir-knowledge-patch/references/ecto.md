# Ecto Queries, Schemas, and Repositories

Batch attribution: `ecto-3.12`.

## Contents

- [Query composition](#query-composition)
- [Preloading](#preloading)
- [Bulk inserts and repository writes](#bulk-inserts-and-repository-writes)
- [Schemas, embeds, and changesets](#schemas-embeds-and-changesets)
- [Adapter and extension migrations](#adapter-and-extension-migrations)

## Query composition

### Recognize named bindings in guards

Use `Ecto.Query.is_named_binding` when guard code must determine whether a query binding is named.

### Use subqueries in by-expressions

Place subqueries in `distinct`, `group_by`, `order_by`, and `window` expressions. Ecto also expands macros at the root of `order_by`, allowing a macro to return the complete ordering expression rather than only a nested fragment.

### Merge and update selected maps

Use `select_merge` in the expanded set of `insert_all` and subquery operations when merging distinct fields. Map-update expressions inside `select` accept dynamic values.

Use literal maps directly in `dynamic/2`:

```elixir
dynamic([post], %{id: post.id, title: post.title})
```

### Accept any enumerable in `in`

The right side of query `in` can be any value implementing `Enumerable`, not only the previously recognized concrete collections:

```elixir
from post in Post, where: post.id in ^MapSet.new(ids)
```

## Preloading

### Preload subquery sources

Preload a subquery used as the source of a `from` or `join` expression.

### Receive association metadata in custom preloaders

Define a custom preload function with arity two to receive both the parent IDs and the association metadata. Keep using arity one when only the IDs are needed.

## Bulk inserts and repository writes

### Supply source-only and update queries to `insert_all`

The query passed to `Repo.insert_all/3` may consist only of its source, without an explicit `select`. It may also use Ecto update syntax.

### Intentionally allow stale operations

Pass `allow_stale: true` to a repository operation on a struct or changeset only when a stale write should be accepted rather than rejected:

```elixir
Repo.update(changeset, allow_stale: true)
```

## Schemas, embeds, and changesets

### Attach options to validation messages

Several `Ecto.Changeset` validators accept `{message, opts}` as their message value, allowing a custom message to retain the options associated with it.

### Mark fields read-only

Use the `:writable` field option to prevent repository writes:

```elixir
field :generated_value, :string, writable: :never
```

### Default a one-to-one embed to its struct

Set `defaults_to_struct: true` when an `embeds_one` field should default to the embedded struct instead of `nil`:

```elixir
embeds_one :profile, Profile, defaults_to_struct: true
```

### Store durations

Use the Ecto `:duration` type for Elixir duration values:

```elixir
field :elapsed, :duration
```

### Preserve nested custom cast errors

For `{:map, type}` and `{:array, type}`, Ecto propagates cast errors returned by the inner custom type instead of replacing them with a generic container error. Preserve and surface that more specific error information in changeset handling.

## Adapter and extension migrations

### Handle `ByExpr`

Represent `distinct`, `group_by`, `order_by`, and `window` expressions as `Ecto.Query.ByExpr` structs in adapters. Code expecting `Ecto.Query.QueryExpr` for these expressions must be updated.

### Initialize parameterized types through the public API

The private form is `{:parameterized, {module, state}}`. Do not construct or match that representation; instantiate parameterized types with `Ecto.ParameterizedType.init/2`.

### Remove `:array_join`

The `:array_join` query join type that had been added for ClickHouse support is removed. Replace extension code that emitted or matched it with adapter-specific supported syntax.
