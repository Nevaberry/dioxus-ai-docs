# SQL/JSON and JSON Processing

Use this reference for SQL-standard JSON queries, relational projection,
constructors, path conversion, and JSON null behavior. The query-function and
table material is attributed to `17-json-guide`; the scalar changes are from
`18.0`.

## Query JSON with SQL-standard functions

PostgreSQL 17 supports `JSON_EXISTS`, `JSON_QUERY`, and `JSON_VALUE`. Each
accepts an SQL/JSON path and named variables supplied by `PASSING`:

```sql
SELECT JSON_EXISTS(
         jsonb '{"scores":[1,3,5]}',
         'strict $.scores[*] ? (@ > $minimum)' PASSING 3 AS minimum
       ),
       JSON_VALUE(
         jsonb '{"age":"42"}', '$.age' RETURNING integer
       ),
       JSON_QUERY(
         jsonb '{"scores":[1,3,5]}', '$.scores[*]'
         WITH CONDITIONAL WRAPPER
       );
```

- `JSON_EXISTS` tests whether the path yields an item.
- `JSON_VALUE` extracts one scalar as `text` by default or as the requested SQL
  type.
- `JSON_QUERY` returns JSON or another `RETURNING` type. It supports
  conditional and unconditional array wrappers and controls for retaining or
  omitting scalar-string quotes.

`JSON_QUERY` and `JSON_VALUE` accept `ON EMPTY` and `ON ERROR` fallbacks and
default to SQL `NULL`; `JSON_EXISTS` defaults to `FALSE`. Context conversion to
`jsonb` occurs outside `ON ERROR`, so malformed input still raises an error.
`JSON_VALUE` maps JSON null to SQL `NULL`, while `JSON_QUERY` preserves JSON
null.

## Project JSON as rows with JSON_TABLE

`JSON_TABLE` turns every row-path match into a row whose schema is declared by
`COLUMNS`. It is implicitly lateral to its source row in `FROM`:

```sql
SELECT o.id, item.*
FROM orders AS o,
     JSON_TABLE(
       o.payload, '$.items[*]'
       COLUMNS (
         item_no FOR ORDINALITY,
         sku text,
         quantity integer PATH '$.qty' DEFAULT 0 ON EMPTY,
         discounted boolean EXISTS PATH '$.discount',
         NESTED PATH '$.tags[*]' COLUMNS (tag text PATH '$')
       )
     ) AS item;
```

Columns can extract and coerce values, test a path with `EXISTS`, number rows
with `FOR ORDINALITY`, or recursively expand arrays with `NESTED PATH`.
Omitting a column path uses `$.column_name`.

A nested path's rows join to its parent. Sibling `NESTED PATH` clauses form a
union rather than a cross product. Column extraction defaults to `NULL` on
empty or error, while `EXISTS` defaults to `FALSE`; per-column clauses can
override those defaults. Top-level `EMPTY ON ERROR` produces no rows.

## Construct and convert JSON

PostgreSQL 17 adds standard `JSON()`, `JSON_SCALAR()`, and `JSON_SERIALIZE()`:

```sql
SELECT JSON('{"n":1}'),
       JSON_SCALAR(42),
       JSON_SERIALIZE(JSON('{"n":1}') RETURNING text);
```

SQL/JSON paths add `.bigint()`, `.boolean()`, `.date()`, `.decimal()`,
`.integer()`, `.number()`, `.string()`, `.time()`, `.time_tz()`,
`.timestamp()`, and `.timestamp_tz()` conversion methods.

## Handle JSONB nulls explicitly

In PostgreSQL 18, casting a JSONB null to a scalar produces SQL `NULL`.
`jsonb_strip_nulls()` accepts a second Boolean argument that also removes null
array elements:

```sql
SELECT ('null'::jsonb)::integer,
       jsonb_strip_nulls('[1,null,{"x":null}]'::jsonb, true);
```

This behavior is distinct from SQL/JSON `JSON_QUERY`, which deliberately
preserves a JSON null result.
