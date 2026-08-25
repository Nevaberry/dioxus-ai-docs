# FTS5, Sessions, and Extensions

Use this reference for locale-aware or contentless FTS5 tables, token access,
session tracking, extension availability, and FTS-related fixes.

## Tokenization and contentless tables

### Locale-aware custom tokenizers (3.47.0)

The `fts5_tokenizer_v2` API and `locale=1` option support custom locale-aware
tokenizers.

### Persistent unindexed content (3.47.0)

For a contentless FTS5 table, `contentless_unindexed=1` persistently stores
values from `UNINDEXED` columns:

```sql
CREATE VIRTUAL TABLE docs USING fts5(
  body, source UNINDEXED, content='', contentless_unindexed=1
);
```

A contentless table can also be dropped when its custom tokenizer is not
registered.

### Prefix-query tokens for auxiliary functions (3.48.0)

FTS5 `xInstToken()` works with prefix queries when token collection is enabled
with the `insttoken` configuration option or the `fts5_insttoken()` SQL
function.

## Session tracking

### Generated-column schemas (3.49.0)

The session extension works with tables that contain generated columns; those
schemas no longer prevent session-based change tracking.

## Bundled and loadable extensions

### Amalgamation contents (3.51.0)

The amalgamation contains `carray` and `percentile`, but neither is active
unless the build defines `SQLITE_ENABLE_CARRAY` or
`SQLITE_ENABLE_PERCENTILE`.

## FTS5 correctness

### BLOB updates and vocabulary tables (3.50.0, 3.51.0)

Version 3.50.2 fixes updates of FTS5 tables containing BLOBs. Version 3.51.1
fixes an `fts5vocab` bug exposed by 3.51.0 optimizations.
