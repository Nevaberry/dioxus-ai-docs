# CQL, Schema, Clients, and Tools

## Native protocol and serialization

### CQL multiframe message limits

The CQL message-size limit applies to multiframe as well as single-frame
messages (since 5.0.3). Splitting a message across frames does not bypass the
configured limit.

### Complete UTF-8 serialization

`CBUtil` serializes the full UTF-8 range correctly (since 5.0.3), including
valid data that older maintenance releases mishandled.

### Correctly correlated overload responses

Coordinator load shedding attaches the request stream ID to
`OverloadedException` responses (since 5.0.9), preventing an overloaded
response from being delivered to the wrong in-flight request.

### Native value-length bounds

`CBUtil` bounds a declared value length against the remaining readable bytes
(since 5.0.9). Malformed or truncated values cannot cause a read beyond the
available payload.

## CQL types and schema

### Descending UDT and vector clustering keys

UDTs and vectors can be descending clustering keys (since 5.0.3):

```cql
CREATE TYPE coordinates (x int, y int);
CREATE TABLE samples (
    sensor_id uuid,
    position frozen<coordinates>,
    embedding vector<float, 3>,
    PRIMARY KEY (sensor_id, position, embedding)
) WITH CLUSTERING ORDER BY (position DESC, embedding DESC);
```

### Materialized views in `DESCRIBE TABLE`

`DESCRIBE TABLE` includes the table's materialized views (since 5.0.4).
Schema export and inspection tooling should account for the additional DDL.

### `min` and `max` over descending clustering columns

The built-in `min` and `max` functions return correct results for descending
clustering columns (since 5.0.4).

### Table-name length validation

Cassandra rejects table names that would create filenames that are too long
(since 5.0.6). DDL generators should handle validation failure instead of
expecting a later filesystem-path error.

### Scalar-only `BytesType` compatibility

`BytesType` compatibility is restricted to scalar types (since 5.0.7).
Schema evolution or tooling that treats it as compatible with non-scalar types
may now be rejected.

## `CQLSSTableWriter`

### `CQLSSTableWriter` production notifications

`CQLSSTableWriter` can notify clients whenever it produces an SSTable (since
5.0.3), allowing callers to react as files are emitted.

### Configurable `CQLSSTableWriter` format

`CQLSSTableWriter` can choose BTI or Big-format SSTables (since 5.0.5). Select
the format deliberately for the destination cluster and workflow.

### Date and time vectors in `CQLSSTableWriter`

`CQLSSTableWriter` correctly serializes vectors whose elements are `date` or
`time` values (since 5.0.7).

## Command-line tools and builds

### Tool initialization without DirectIO

Cassandra tools skip the DirectIO check during initialization (since 5.0.4),
so management tools can initialize independently of that storage capability.

### Selective tool environment loading

`nodetool` and other tools avoid sourcing `cassandra-env.sh` when unnecessary
(since 5.0.5). Wrappers must not depend on unrelated side effects from that
file.

### Buildable source distributions

Source distributions can be built with the Ant `artifacts` target, and the
native-protocol processing script used by the build is executable (since
5.0.5):

```shell
ant artifacts
```

### Optional `cqlsh` history

`cqlsh` can disable command history (since 5.0.7), allowing sensitive or
ephemeral sessions to avoid persisting entered statements.

### TLS 1.3 negotiation in `cassandra-stress`

`cassandra-stress` supports TLS 1.3 by default through automatic TLS-version
negotiation (since 5.0.8).

### Python 3.12 and 3.13 for `cqlsh`

`cqlsh` supports running with Python 3.12 and 3.13 (since 5.0.9).

### Documentation generation without Go

The `gen-doc` tooling uses Python rather than Go (since 5.0.9), so Go is no
longer a dependency for generating Cassandra documentation.

### `nodetool import --copy-data` short option

The short form of `nodetool import --copy-data` is `-cd`, not the conflicting
`-p` (since 5.0.9). Update command automation accordingly:

```shell
nodetool import -cd keyspace_name table_name /path/to/sstables
```
