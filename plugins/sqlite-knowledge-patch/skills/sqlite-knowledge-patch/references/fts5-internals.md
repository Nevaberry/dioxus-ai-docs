# FTS5 & Internals (3.47–3.51)

## FTS5 Locale-Aware Tokenizers (3.47.0)

New `fts5_tokenizer_v2` API enables locale-aware tokenization. Tables opt in with `locale=1`:

```sql
CREATE VIRTUAL TABLE t1 USING fts5 (content, locale = 1);

-- Insert with locale context via fts5_locale() wrapper
INSERT INTO
  t1 (content)
VALUES
  (fts5_locale ('tr_TR', 'Istanbul'));
```

## FTS5 `contentless_unindexed=1` (3.47.0)

Contentless FTS5 tables can now persistently store UNINDEXED column values:

```sql
CREATE VIRTUAL TABLE t1 USING fts5(
  body,
  title UNINDEXED,
  content='',
  contentless_unindexed=1  -- title values are stored, not just indexed
);
```

## STRICT Typing Enforced on Computed Columns (3.51.0)

Generated columns in STRICT tables now have type affinity enforced. Previously, computed columns could return values that didn't match their declared type without error.

## `PRAGMA wal_checkpoint(NOOP)` (3.51.0)

New checkpoint mode that returns checkpoint status without actually checkpointing:

```sql
PRAGMA wal_checkpoint(NOOP);  -- returns (busy, log, checkpointed) without doing work
```
