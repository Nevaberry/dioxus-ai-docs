# SQL/JSON and JSON Processing

Batch attribution: `17-json-guide`, `17.0`, `18.0`.

## Query JSON with SQL-standard functions

`JSON_EXISTS`, `JSON_QUERY`, and `JSON_VALUE` accept a SQL/JSON path and named
variables supplied by `PASSING`.

`JSON_EXISTS` tests whether the path produces an item. Its default on error is
`FALSE`.

`JSON_VALUE` extracts exactly one scalar. It returns `text` unless `RETURNING`
requests another SQL type. JSON null becomes SQL `NULL`.

`JSON_QUERY` returns JSON, or the type selected by `RETURNING`. It can apply a
conditional or unconditional array wrapper and can keep or omit the quotes
around scalar strings. Unlike `JSON_VALUE`, it preserves JSON null.

`JSON_QUERY` and `JSON_VALUE` support `ON EMPTY` and `ON ERROR` fallbacks; both
default to SQL `NULL`. Conversion of the context expression to `jsonb` occurs
outside `ON ERROR`, so malformed context input still raises an error.

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

## Project JSON into rows with `JSON_TABLE`

`JSON_TABLE` turns every match of its row path into a row whose shape is
declared by `COLUMNS`. In `FROM` it is implicitly lateral to earlier source
rows.

Columns can:

- extract and coerce a value, with `PATH` optional when `$.column_name` is
  correct;
- test a path with `EXISTS`;
- number matches with `FOR ORDINALITY`; or
- recursively expand arrays with `NESTED PATH`.

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

A nested path's rows join to its parent row. Sibling `NESTED PATH` clauses are
combined as a union, not a cross product. Value extraction defaults to `NULL`
on empty or error, and `EXISTS` defaults to `FALSE`; each column can override
those actions. Top-level `EMPTY ON ERROR` instead produces no rows.

## Construct, serialize, and convert JSON

The SQL-standard constructors and serializer are available:

```sql
SELECT JSON('{"n":1}'),
       JSON_SCALAR(42),
       JSON_SERIALIZE(JSON('{"n":1}') RETURNING text);
```

SQL/JSON paths can convert values with `.bigint()`, `.boolean()`, `.date()`,
`.decimal()`, `.integer()`, `.number()`, `.string()`, `.time()`,
`.time_tz()`, `.timestamp()`, and `.timestamp_tz()`.

## Handle JSON nulls in scalar and array conversions

Casting a `jsonb` null to a scalar produces SQL `NULL`. The optional second
Boolean argument to `jsonb_strip_nulls` also removes null array elements;
without it, the function removes null-valued object fields only.

```sql
SELECT ('null'::jsonb)::integer,
       jsonb_strip_nulls('[1,null,{"x":null}]'::jsonb, true);
```
