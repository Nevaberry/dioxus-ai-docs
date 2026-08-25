# Compatibility and migrations

Use this reference when upgrading DuckDB, validating generated SQL against a
new engine, or deciding whether an existing deployment remains supported.
Relevant extraction batches: `1.2-1.4` and `1.5.0`.

## Release-line support

DuckDB 1.5 is the current non-LTS line in the source material and is scheduled
to reach end of life on 2026-09-01. The 1.4 LTS line remains supported through
September 2026. Beginning with 1.4, every other release line is designated LTS
and receives one year of community support.

Treat engine support, extension availability, and storage-file compatibility
as separate questions. An engine may still run on a platform while official
extensions or a particular database storage version do not.

## Expression and return-type changes

### `date_trunc` on `DATE`

In 1.5.0, applying `date_trunc` to a `DATE` returns `TIMESTAMP`, not `DATE`:

```sql
SELECT typeof(date_trunc('month', DATE '2026-03-27')); -- TIMESTAMP
```

Add an explicit cast if a view, client decoder, schema comparison, or downstream
expression requires a `DATE` result.

### Map lookup

Within the 1.2-1.4 batch, bracket lookup changed to return the value itself.
`map_extract_value` is the named equivalent. `map_extract` retains the
single-element-list result:

```sql
SELECT map(['k'], ['v'])['k'];               -- 'v'
SELECT map_extract_value(map(['k'], ['v']), 'k'); -- 'v'
SELECT map_extract(map(['k'], ['v']), 'k'); -- ['v']
```

Audit callers that index into the result or expect a list-typed column.

### Timezone and pseudo-random behavior

`current_time` and `current_date` use the local timezone and require ICU. A
deployment that omits ICU cannot assume those expressions behave as before.

The random-number generator state changed, so a fixed seed produces a different
sequence from earlier engines. Treat seeded outputs as reproducible only within
a compatible DuckDB implementation, not as permanent fixture data across an
upgrade.

### Nested-value serialization

String values inside serialized nested structures escape quotes so the text can
round-trip. Code that parsed or compared the old unquoted display must adapt.
Use `array_to_string` when the intended output really is the old unquoted
presentation rather than a round-trippable serialization.

## Parser and identifier changes

`AT` and `LAMBDA` are reserved identifiers and require quoting when used as
object or column names. `GRANT` is no longer reserved. Inspect generated SQL,
migration files, and ORM mappings for all three cases.

## Lambda syntax migration

Both lambda forms parse in 1.5.0, but the single-arrow form warns:

```sql
-- Preferred
SELECT list_transform([1, 2, 3], lambda x: x + 1);

-- Compatibility controls
SET lambda_syntax = 'ENABLE_SINGLE_ARROW';
SET lambda_syntax = 'DISABLE_SINGLE_ARROW';
```

`ENABLE_SINGLE_ARROW` retains `x -> x + 1` without a warning.
`DISABLE_SINGLE_ARROW` turns the warning into an error so a codebase can find
remaining uses before migration. The arrow form is scheduled for default
disablement in 2.0.

## Spatial axis-order migration

Spherical and spheroidal distance, perimeter, area, and within functions, plus
`ST_Transform`, are moving from legacy `(x = latitude, y = longitude)` handling
to conventional `(x = longitude, y = latitude)` handling. An unset
`geometry_always_xy` warns in 1.5.0:

```sql
SET geometry_always_xy = true;  -- new behavior
SET geometry_always_xy = false; -- pin legacy behavior temporarily
```

The unset state is scheduled to become an error in 2.0; `true` is scheduled to
become the default in 2.1. See [Spatial and geometry](spatial-and-geometry.md)
before changing geospatial production queries.

## CSV strictness

RFC 4180-style strict parsing is enabled by default. For a known irregular file,
such as one containing mixed newline styles, opt out on that read:

```sql
FROM read_csv('legacy.csv', strict_mode = false);
```

Do not assume a permissively parsed fixture proves that production input will
load under the default.

## Linux compatibility floor

Official Linux binaries starting with 1.3 require glibc 2.28 or later.
Extensions are no longer published for `linux_amd64_gcc4`. Older systems must
build DuckDB from source rather than expecting the old extension target.

For musl systems such as Alpine, use the musl build and install `libstdc++`.
This is distinct from the glibc requirement for the regular official build.

## Upgrade checklist

1. Record the engine, CLI, and loaded extension versions.
2. Locate `date_trunc` calls whose declared or decoded type matters.
3. Locate bracket map lookups and distinguish scalar from list expectations.
4. Quote identifiers named `AT` or `LAMBDA`; reconsider unnecessary quoting of
   `GRANT` only when doing so is useful.
5. Replace arrow lambdas or use `DISABLE_SINGLE_ARROW` to expose remaining uses.
6. Set `geometry_always_xy` explicitly and verify known coordinate pairs.
7. Re-test timezone-sensitive and fixed-seed behavior.
8. Re-test comparisons or parsers that consume nested-value text.
9. Check glibc or musl requirements and extension distribution targets.
10. Verify that every database file uses a storage version accepted by all
    readers; engine upgrades alone do not decide that compatibility.
