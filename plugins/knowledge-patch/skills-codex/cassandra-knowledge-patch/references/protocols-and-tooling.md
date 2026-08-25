# Protocols and Tooling

Use this reference for native-protocol boundaries, serialization, command-line
tools, runtime support, build workflows, and `CQLSSTableWriter`.

## Native protocol and serialization

### Enforce multiframe CQL limits (since 5.0.3)

The CQL message-size limit applies to multiframe messages as well as
single-frame messages. Splitting an oversized message across frames does not
bypass the configured limit.

### Serialize the full UTF-8 range (since 5.0.3)

`CBUtil` correctly serializes the full UTF-8 range. Applications do not need to
exclude otherwise valid UTF-8 values to avoid the former serialization error.

### Preserve null tombstones in FQL batches (since 5.0.4)

Full Query Logging batch statements support null column-value tombstones.
Replay or analysis tools must preserve those nulls as deletion semantics rather
than treating them as missing log data.

### Bound native value lengths (since 5.0.9)

`CBUtil` checks a declared value length against the bytes still readable.
Malformed or truncated values cannot direct a read beyond the available
payload; custom protocol tooling should enforce the same invariant.

### Correlate overloaded requests (since 5.0.9)

Load-shedding `OverloadedException` responses carry the originating request
stream ID. Multiplexed clients should route the error to that request rather
than whichever request happens to be pending.

## `CQLSSTableWriter`

### Observe produced SSTables (since 5.0.3)

`CQLSSTableWriter` can notify a client when it produces an SSTable. Register the
notification before writing when downstream ingestion or bookkeeping must react
as each file is emitted.

### Select the output format (since 5.0.5)

`CQLSSTableWriter` can write BTI or Big-format SSTables. Choose the format for
the target cluster explicitly instead of assuming a single hard-coded output.

### Serialize date and time vectors (since 5.0.7)

Vectors whose elements are CQL `date` or `time` values serialize correctly in
`CQLSSTableWriter`. Bulk-generation code can use those vector element types
without custom byte conversion.

## Command-line behavior

### Initialize tools without DirectIO checks (since 5.0.4)

Cassandra tools skip the DirectIO check during initialization. Tool startup no
longer depends on whether the server's Direct I/O environment can be validated.

### Avoid incidental environment loading (since 5.0.5)

`nodetool` and other tools do not source `cassandra-env.sh` when it is
unnecessary. Scripts must supply their own required environment rather than
depending on unrelated side effects from that file.

### Disable `cqlsh` history when needed (since 5.0.7)

`cqlsh` offers an option to disable command history. Use it for sessions where
entered statements must not persist locally.

### Use the new import short option (since 5.0.9)

The short form of `nodetool import --copy-data` is `-cd`, replacing the
conflicting `-p`. Update automation that uses the short form.

```shell
nodetool import -cd keyspace_name table_name /path/to/sstables
```

## Runtimes, stress testing, and builds

### Run the server on Java 17 (since 5.0.5)

The server has full Java 17 support. Runtime selection, images, and CI matrices
can treat Java 17 as supported rather than experimental or partial.

### Build source distributions (since 5.0.5)

The Ant `artifacts` target builds source distributions, and the native-protocol
processing script it invokes is executable.

```shell
ant artifacts
```

### Negotiate TLS in `cassandra-stress` (since 5.0.8)

`cassandra-stress` supports TLS 1.3 by automatically negotiating the TLS
version. Do not pin an older protocol merely to compensate for the previous
client behavior.

### Run `cqlsh` on current Python (since 5.0.9)

`cqlsh` supports Python 3.12 and 3.13. Tool images can adopt those runtimes
without retaining an older Python solely for `cqlsh`.

### Generate documentation without Go (since 5.0.9)

The `gen-doc` tooling uses Python rather than Go. Documentation build
environments no longer need a Go installation for this workflow.
