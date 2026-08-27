# Storage, SSTables, and Recovery

## Cache and schema snapshots

### Optional key-cache preservation

A deletion flag allows SSTables to be removed without invalidating the key
cache (since 5.0.3). Use the opt-out deliberately when the caller needs to
preserve cached keys across deletion.

### Snapshot schemas for descending UDT keys

Snapshot-generated schema CQL includes definitions for UDTs used as reverse
clustering columns (since 5.0.3), so restoring schemas with descending UDT keys
retains their type definitions.

### Relaxed snapshot-name validation

SSTable path validation accepts snapshot names that were unnecessarily
rejected before (since 5.0.5).

### Pre-2.1 snapshot schema loading

`SnapshotLoader` can load pre-2.1 schemas whose directory names do not contain
a table ID (since 5.0.8).

### Snapshot-name validation

Snapshot operations validate snapshot names (since 5.0.9). Automation should
expect invalid names to be rejected.

## Commitlog and recovery

### Safe Direct I/O commitlog flushes

Commitlog data is flushed safely with Direct I/O enabled (since 5.0.5).

### Commitlog recovery after CRC errors

`CommitLogSegmentReader` skips sync blocks correctly after CRC errors (since
5.0.5), allowing recovery to continue at the appropriate boundary.

## Compaction and disk accounting

### Unified Compaction size validation

Unified Compaction validates minimum and target size settings (since 5.0.5),
rejecting invalid size combinations.

### Corrupt SSTables during compaction

A corrupted SSTable encountered during compaction is marked suspected, and
associated buffer-pool resources are released (since 5.0.5).

### Compressed-size compaction checks

Compaction free-space checks use each table's estimated compressed size (since
5.0.9). Admission decisions therefore reflect estimated compressed output
rather than an incompatible size basis.

### Leveled-scanner boundary intersections

`LeveledScanner` includes an SSTable's first token when calculating
intersections (since 5.0.9), preventing boundary SSTables from being omitted.

## SSTable formats and components

### Large memory-mapped trie indexes

Memory-mapped trie indexes larger than 2 GiB can be read correctly (since
5.0.5).

### TOC write exception classification

A runtime exception from `FileUtils.write` while writing a `TOCComponent`
remains a runtime exception instead of being reclassified as an `FSError`
(since 5.0.6).

### Legacy-SSTable zero-copy streaming fallback

Zero-copy streaming is automatically disabled for legacy SSTables using the
old Bloom-filter format (since 5.0.7), allowing a compatible streaming fallback.

### Schema-disagreement SSTable corruption

Resetting `BTree.FastBuilder` clears its saved buffer and next-key state (since
5.0.9), preventing the `ClassCastException` and SSTable-header corruption path
that could occur during schema disagreement.
