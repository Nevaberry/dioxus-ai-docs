# FTS5, Sessions, and Extensions

## Locale-aware tokenization

The `fts5_tokenizer_v2` API and `locale=1` table option support locale-aware custom tokenizers (since 3.47.0). Tokenizers can receive locale information attached to FTS5 text and apply language-sensitive rules.

## Contentless tables

For a contentless FTS5 table, `contentless_unindexed=1` persistently stores values from `UNINDEXED` columns (since 3.47.0):

```sql
CREATE VIRTUAL TABLE docs USING fts5(
  body,
  source UNINDEXED,
  content='',
  contentless_unindexed=1
);
```

An FTS5 virtual table may also be dropped when its custom tokenizer is not registered.

## Prefix-query tokens in auxiliary functions

The auxiliary-function `xInstToken()` API can return tokens for prefix-query matches (since 3.48.0). Enable collection through the `insttoken` configuration option or the `fts5_insttoken()` SQL function.

## Integrity and correctness fixes

- FTS5 integrity checks no longer report false corruption in secure-delete mode (fixed in the 3.46.0 line).
- Version 3.50.2 fixes FTS5 updates containing BLOB values.
- Version 3.51.1 fixes an `fts5vocab` fault exposed by the `EXISTS`-to-join optimizer.

## Session extension

The session extension works with tables containing generated columns as of 3.49.0, enabling changesets on those schemas.

SQLite 3.53.0 also supports incremental `sqlite3_changegroup` construction. Start with `sqlite3changegroup_change_begin()`, add typed values using the `change_blob`, `change_double`, `change_int64`, `change_null`, or `change_text` interfaces, and call `sqlite3changegroup_change_finish()`. Configure the object with `sqlite3changegroup_config()`.

## Bundled optional extensions

The `carray` and percentile extensions ship in the amalgamation as of 3.51.0 but remain disabled by default. Compile with `SQLITE_ENABLE_CARRAY` or `SQLITE_ENABLE_PERCENTILE` respectively.

The CLI has exposed `median()`, `percentile()`, `percentile_cont()`, and `percentile_disc()` as extension functions since 3.47.0. Do not assume those functions exist in an arbitrary embedded library unless the percentile extension is enabled or loaded.

## Extension loading boundary

SQL `load_extension()` is disabled until explicitly enabled on a connection. It can add functions and collations but cannot modify or remove an existing function/collation while the loading statement runs. Use the C `sqlite3_load_extension()` API when an extension must perform those changes.
