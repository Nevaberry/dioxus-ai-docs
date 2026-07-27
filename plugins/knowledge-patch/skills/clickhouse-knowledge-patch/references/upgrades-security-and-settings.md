# Upgrades, security, and settings

Use this reference for upgrade preparation, credential boundaries, changed defaults, and settings mutations that can otherwise create startup failures or unintended access.

## Object-storage credential inheritance

### User SQL credential boundary (`26.7`)

S3 access initiated by user SQL no longer inherits the server process's cloud credentials. Supply credentials explicitly or use `NOSIGN` for public or intentionally unsigned access.

Named collections default `use_environment_credentials` to `0`. Environment lookup is restored only when both of these are enabled:

```text
use_environment_credentials = 1
s3_allow_server_credentials_in_user_queries = 1
```

`s3_allow_server_credentials_in_user_queries` is off by default. Enabling it expands the authority available to user-submitted SQL, so pair it with appropriate user and URL-scoped access controls.

Persistent S3-backed objects whose server credentials are restricted load anonymously at startup or during `RESTORE` while the default-on `s3_load_table_anonymously_if_credentials_restricted` remains enabled. Disable that behavior when anonymous fallback would hide a credential-policy error.

## Insert behavior and upgrade sequencing

### Unified deduplication hash (`26.7`)

Synchronous and asynchronous inserts always use the unified deduplication hash. Startup fails when `insert_deduplication_version` is either `old_separate_hashes` or `compatible_double_hashes`.

To migrate from either legacy mode:

1. Run an intermediate release with `insert_deduplication_version = compatible_double_hashes`.
2. For replicated tables, leave it in place for at least `replicated_deduplication_window_seconds`.
3. For non-replicated tables, leave it in place for at least `non_replicated_deduplication_window` inserts.
4. Remove the setting or switch it to `new_unified_hash` before the final upgrade.

This transition allows old and unified hashes to coexist long enough for the active deduplication window to age out. Do not jump directly from an old-only hash configuration to a server that rejects it.

### Asynchronous inserts by default (`26.3-26.6`)

Asynchronous inserts are enabled by default as of the 26.3 LTS line. ClickHouse buffers and batches small inserts before writing them to storage. Review client expectations around acknowledgment, visibility latency, buffer failures, backpressure, and deduplication rather than assuming every insert creates an immediate part.

## Scheduling configuration

### Removed server-config sections (`26.7`)

The `resources` and `workload_classifiers` server-configuration sections are ignored and produce a warning. Define scheduling in SQL instead:

```sql
CREATE RESOURCE memory (MEMORY RESERVATION);
CREATE WORKLOAD interactive;
```

Workload hierarchies can then apply memory limits and weights, and a query selects its workload with `SETTINGS workload = 'name'`. See [operations, integrations, and tooling](operations-integrations-and-tooling.md#workload-scheduling) for the runtime controls.

## Access-setting mutations

### Preserve settings not named by the change (`26.7`)

`ALTER USER`, `ALTER ROLE`, and `ALTER SETTINGS PROFILE` accept the following targeted spelling:

```sql
ALTER USER analyst SET max_threads = 4;
ALTER ROLE readonly SET max_execution_time = 60;
ALTER SETTINGS PROFILE web SET max_memory_usage = 1000000000;
```

Here `SET name = value` is an alias for `MODIFY SETTING name = value`. It preserves all other settings. A bare `SETTINGS` clause has replacement-style behavior and can discard settings that are not restated, so do not substitute it in generated access-management SQL.

## Client output safety

### Binary output to a terminal (`25.1-25.12`)

When a query would write a binary format directly to an interactive terminal, the client asks for confirmation. Answering no reruns the query without emitting its output. Use `INTO OUTFILE` or shell redirection for intentional binary output so automation is non-interactive and the terminal is not corrupted.

## Related upgrade checks

- Direct S3 or Azure backup destinations and object-storage-backed disks reject `zip` and `zipx`; use a tar-based format. See [external data and formats](external-data-and-formats.md#object-storage-backups).
- `AggregatingMergeTree` validates dimension columns at table creation. See [tables, indexes, and views](tables-indexes-and-views.md#aggregatingmergetree-dimensions).
- SQL function removals and return-type changes are collected in [query language and functions](query-language-and-functions.md#compatibility-sensitive-functions).
