# SQL/JSON and JSON Processing

## Query JSON with SQL-standard functions (17-json-guide)

`JSON_EXISTS`, `JSON_QUERY`, and `JSON_VALUE` accept SQL/JSON paths and named
variables supplied by `PASSING`. `JSON_EXISTS` reports whether a path yields an
item, `JSON_QUERY` returns JSON or a declared `RETURNING` type, and
`JSON_VALUE` extracts one scalar as `text` unless another SQL type is requested.

```sql
SELECT JSON_EXISTS(
         jsonb '{"scores":[1,3,5]}',
         'strict $.scores[*] ? (@ > $minimum)' PASSING 3 AS minimum
       ),
       JSON_VALUE(jsonb '{"age":"42"}', '$.age' RETURNING integer),
       JSON_QUERY(
         jsonb '{"scores":[1,3,5]}', '$.scores[*]'
         WITH CONDITIONAL WRAPPER
       );
```

`JSON_QUERY` supports conditional or unconditional array wrappers and can keep
or omit quotes around scalar strings. `JSON_QUERY` and `JSON_VALUE` support
`ON EMPTY` and `ON ERROR`; both default to SQL `NULL`, while `JSON_EXISTS`
defaults to `FALSE`. Conversion of the context value to `jsonb` happens outside
`ON ERROR`, so malformed context input still raises an error. `JSON_VALUE`
maps JSON null to SQL `NULL`; `JSON_QUERY` preserves JSON null.

## Project JSON into rows (17-json-guide)

`JSON_TABLE` produces a row per row-path match using a schema declared in
`COLUMNS`. It is implicitly lateral to its source row. Columns may coerce a
value, test a path with `EXISTS`, count matches with `FOR ORDINALITY`, or
recursively expand arrays with `NESTED PATH`; an omitted column path defaults
to `$.column_name`.

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

A nested path joins its rows to the parent row. Sibling `NESTED PATH` clauses
form a union, not a cross product. Column extraction defaults to `NULL` on
empty or error, except that `EXISTS` defaults to `FALSE`; override behavior per
column. Top-level `EMPTY ON ERROR` instead emits no rows.

## Construct, serialize, and convert JSON (17.0)

Use the SQL-standard `JSON()`, `JSON_SCALAR()`, and `JSON_SERIALIZE()`
constructors. SQL/JSON paths also provide `.bigint()`, `.boolean()`, `.date()`,
`.decimal()`, `.integer()`, `.number()`, `.string()`, `.time()`, `.time_tz()`,
`.timestamp()`, and `.timestamp_tz()` conversions.

```sql
SELECT JSON('{"n":1}'),
       JSON_SCALAR(42),
       JSON_SERIALIZE(JSON('{"n":1}') RETURNING text);
```

## Handle JSON nulls and binary casts (18.0)

Casting a JSONB null to a scalar yields SQL `NULL`. Pass `true` as the second
argument to `jsonb_strip_nulls()` to remove null array elements as well as null
object fields. Integer-to-`bytea` casts use two's-complement representation,
and reverse casts are supported.

```sql
SELECT ('null'::jsonb)::integer,
       jsonb_strip_nulls('[1,null,{"x":null}]'::jsonb, true);
```
