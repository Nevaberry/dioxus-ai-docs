# FTS5, Sessions, and Extensions

## Locale-aware tokenizers (since 3.47.0)

The `fts5_tokenizer_v2` API and `locale=1` option support custom locale-aware
tokenizers.

## Contentless FTS5 tables (since 3.47.0)

For a contentless table, `contentless_unindexed=1` persistently stores
`UNINDEXED` column values. A table may also be dropped when its custom
tokenizer is not registered.

```sql
CREATE VIRTUAL TABLE docs USING fts5(
  body, source UNINDEXED, content='', contentless_unindexed=1
);
```

## Prefix-query tokens for auxiliary functions (since 3.48.0)

The FTS5 `xInstToken()` auxiliary API works with prefix queries when token
collection is enabled through the `insttoken` configuration option or the
`fts5_insttoken()` SQL function.

## Session extension and generated columns (since 3.49.0)

The session extension works with databases whose tables use generated
columns, so those schemas no longer prevent session-based change tracking.

## FTS5 correctness fixes

- Version 3.50.2 fixes updates of FTS5 tables containing BLOBs.
- Version 3.51.1 fixes an `fts5vocab` bug exposed by 3.51.0 optimizations.

## Incremental session changegroups (since 3.53.0)

Applications can add changes to a `sqlite3_changegroup` one at a time using
`sqlite3changegroup_change_begin()`, the typed
blob/double/int64/null/text setters, and
`sqlite3changegroup_change_finish()`. `sqlite3changegroup_config()` configures
the changegroup.
