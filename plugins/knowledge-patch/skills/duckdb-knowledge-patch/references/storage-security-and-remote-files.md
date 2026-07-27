# Storage, security, and remote files

Use this reference when creating database files, retaining compatibility with
older readers, encrypting storage, scanning remote data, or parsing CSV. Source
coverage comes from batches `1.2-1.4` and `1.5.0`.

## Explicit storage versions

New storage features remain disabled by default so files created by 1.2 remain
readable by older releases. Opt into a storage format when attaching:

```sql
ATTACH 'modern.db' (STORAGE_VERSION 'v1.2.0');
```

The named storage version becomes the oldest release that can open the file.
Inspect each attached database's selection through the `tags` column:

```sql
SELECT database_name, tags
FROM duckdb_databases();
```

To create an older-compatible copy, attach a destination with the required
older storage version and copy from the source into it:

```sql
ATTACH 'source.db' AS source;
ATTACH 'compatible.db' AS destination (STORAGE_VERSION 'v1.2.0');
COPY FROM DATABASE source TO destination;
```

Do not infer file readability only from the DuckDB engine used to create it;
the explicit storage version controls the compatibility floor.

## Encrypted database files

Pass `ENCRYPTION_KEY` while attaching a database:

```sql
LOAD httpfs;
ATTACH 'encrypted.db' AS enc_db (ENCRYPTION_KEY 'quack_quack');
```

Encryption covers the database, write-ahead log, and temporary files.
AES-256-GCM is the default. Loading `httpfs` chooses its hardware-accelerated
OpenSSL implementation instead of the built-in encryption implementation.

Keep the key out of committed SQL and logs. The expression-capable
`CREATE SECRET` syntax described in [SQL and types](sql-and-types.md) is useful
when a credential can be supplied indirectly.

## Compressed in-memory databases

Checkpointing allows in-memory databases to use compression and reclaim space
left by deletes or truncation. Compression is opt-in on the attachment:

```sql
ATTACH ':memory:' AS memory_compressed (COMPRESS);
USE memory_compressed;
```

Use this form when memory recovery matters; a normal in-memory attachment does
not silently acquire the option.

## External file cache

Remote file data is cached automatically within the global memory limit, so
repeated scans can avoid a second download. Inspect cached entries with:

```sql
FROM duckdb_external_file_cache();
```

Disable the cache for the current connection when freshness, memory policy, or
testing requires it:

```sql
SET enable_external_file_cache = false;
```

Account for cache memory when sizing a process; automatic caching participates
in the global limit rather than being an unbounded side cache.

## CSV compatibility controls

`read_csv` accepts Latin-1 and UTF-16 input, and delimiters may be up to four
bytes long:

```sql
FROM read_csv('legacy.csv', encoding = 'latin-1');
FROM read_csv('utf16.csv', encoding = 'utf-16');
FROM read_csv('data.dsv', sep = '🦆');
```

RFC 4180-style strict parsing is enabled by default. Disable it only for a known
irregular file, such as one with mixed newline styles:

```sql
FROM read_csv('legacy.csv', encoding = 'latin-1', strict_mode = false);
```

## Azure writes

`COPY` writes to Azure Blob Storage with `az://` and to ADLSv2 with
`abfss://`:

```sql
COPY my_table TO 'az://my_container/path/output.parquet';
COPY my_table TO 'abfss://my_container/path/output.parquet';
```

Configure the relevant Azure credentials through DuckDB's secret or environment
mechanisms rather than embedding them in a destination URI.

## Curl-backed `httpfs`

In 1.5.0, the default `httpfs` backend changes from `httplib` to curl. OpenSSL
and settings such as `http_timeout` and `http_retries` remain unchanged.

After curl-backed `httpfs` is loaded, subsequent extension installations use
HTTPS through it. Downloading `httpfs` itself still uses `httplib`, because the
new backend cannot be active before that extension has been obtained.

When diagnosing transport behavior, distinguish these phases rather than
assuming every download used the same HTTP implementation.
