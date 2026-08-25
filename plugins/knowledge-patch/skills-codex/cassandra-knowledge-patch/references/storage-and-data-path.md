# Storage and Data Path

Use this reference for SSTable lifecycle, compaction, commitlog recovery,
snapshots, caches, deletion reconciliation, and disk-space decisions.

## SSTable lifecycle and caches

### Preserve the key cache optionally (since 5.0.3)

SSTable deletion has a flag that skips key-cache invalidation. Use it only when
the caller can guarantee that preserving the affected entries is safe; the
default invalidation behavior remains the conservative choice.

### Read large memory-mapped trie indexes (since 5.0.5)

Memory-mapped trie indexes larger than 2 GiB can be read correctly. Storage
planning need not cap these indexes below that boundary as a workaround.

### Query early-open BTI ranges (since 5.0.6)

Range queries against early-open BTI SSTables return correct results before the
files are fully opened. Keep this state in tests that exercise incremental
SSTable availability.

### Preserve TOC exception classification (since 5.0.6)

A runtime exception from `FileUtils.write` while writing a `TOCComponent`
remains a runtime exception instead of being reclassified as `FSError`.
Callers should handle it according to its original class.

### Include boundary SSTables in leveled scans (since 5.0.9)

`LeveledScanner` considers an SSTable's first token when calculating
intersections. Boundary SSTables are not omitted from the scan.

### Avoid corruption during schema disagreement (since 5.0.9)

Resetting `BTree.FastBuilder` clears saved buffer and next-key state. This
prevents the `ClassCastException` and SSTable-header corruption path that could
occur while schemas disagree.

## Deletions and reconciliation

### Preserve complex collection deletions (since 5.0.4)

Mutation serialization keeps complex deletions when one row contains multiple
collections. Replication and replay no longer lose those deletion markers.

### Retain deletions required for reconciliation (since 5.0.5)

`RowFilter` does not purge deletions when reconciliation is required. Do not
strip those deletions in adjacent filtering code before replicas reconcile.

### Make equal-expiration TTL updates deterministic (since 5.0.5)

Updating a column with a new TTL but the same expiration time is deterministic.
Replicas avoid repair mismatches caused solely by choosing different equivalent
TTL updates.

## Commitlog durability and recovery

### Flush Direct I/O commitlogs safely (since 5.0.5)

Commitlog data is flushed safely when Direct I/O mode is enabled. Durability
tests should cover the Direct I/O path rather than forcing buffered I/O.

### Skip damaged sync blocks correctly (since 5.0.5)

`CommitLogSegmentReader` advances correctly past sync blocks when it encounters
CRC errors. Recovery can continue after the damaged block without rereading the
wrong boundary.

## Compaction and disk sizing

### Validate Unified Compaction sizes (since 5.0.5)

Unified Compaction validates its minimum and target size settings and rejects
invalid combinations. Validate configuration before rollout and handle startup
or schema validation errors explicitly.

### Quarantine corrupt SSTables during compaction (since 5.0.5)

A corrupt SSTable read during compaction is marked suspected, and its associated
buffer-pool resources are released. Operational response should investigate or
replace the suspected file rather than repeatedly retrying it.

### Use compressed estimates for free-space checks (since 5.0.9)

Compaction free-space checks use each table's estimated compressed size.
Admission decisions therefore reflect expected compressed output rather than an
uncompressed-size assumption.

## Snapshots and restore

### Accept valid snapshot directory names (since 5.0.5)

SSTable path validation accepts snapshot names that were unnecessarily rejected
before. Do not preserve stricter client validation for names Cassandra accepts.

### Load pre-table-ID snapshot schemas (since 5.0.8)

`SnapshotLoader` loads schemas created before Cassandra 2.1 when their directory
names do not contain a table ID. Restore tooling should allow this legacy layout
to reach the loader.

### Validate snapshot operation names (since 5.0.9)

Snapshot operations validate snapshot names. Automation that supplies an
invalid name should expect immediate rejection, even though valid legacy or
previously over-restricted directory names are supported.
