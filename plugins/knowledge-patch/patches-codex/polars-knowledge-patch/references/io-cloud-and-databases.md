# I/O, Cloud Storage, and Databases

Use this reference for file readers and sinks, spreadsheet engines, cloud
credentials, remote object stores, Delta and Iceberg, and database boundaries.

## Parquet reads and scans

### Choose Hive partition discovery explicitly

Since `1.0-upgrade`, `read_parquet` and `scan_parquet` accept directories. Hive
partitioning is enabled by default for a directory and disabled by default for a
single file, glob, or list of files. Pass `hive_partitioning=True` when partition
columns must be recovered from non-directory inputs.

### Decode `Float16`

Since `1.10.0`, Parquet readers decode `Float16` data and load its column
statistics correctly.

### Validate only projected columns

Since `1.10.0`, Parquet reads do not validate dtypes for columns outside the
projection. An unusable dtype in an unselected column no longer blocks a
projected read.

### Preserve explicit schemas through planning

Since `1.10.0`, the Parquet `schema` argument is carried into the intermediate
representation rather than being dropped during planning.

### Control scan casts

Since `1.30.0`, `scan_parquet` accepts `cast_options` for explicit casting
behavior during a scan.

### Select columns by index with PyArrow readers

Since `1.41.0`, `read_parquet` and `read_csv` support index-based column
selection when the PyArrow reader backend is selected.

### Read unannotated MAP columns

Since `1.41.0`, the Parquet reader accepts MAP columns that lack a `LogicalType`
annotation.

### Reject duplicate Parquet columns precisely

Since `1.41.0`, reading a Parquet file with duplicate column names raises
`DuplicateError`, allowing invalid schemas to be handled separately from other
read failures.

### Respect IEEE 754 ordering metadata

In `py-1.43.2-rs-0.55.1-0.55.2`, the Parquet reader gained support for
column-order metadata that requests IEEE 754 total ordering.

## Parquet writes and metadata

### Write partitioned datasets to cloud storage

Since `1.20.0`, partitioned Parquet datasets can be written directly to cloud
storage.

### Attach field and file metadata

Since `1.30.0`, Parquet writers can attach field metadata, and Parquet I/O can
read and write custom file-level metadata.

### Preserve field IDs in sinks

Since `1.40.0`, `sink_parquet` writes Parquet field IDs so that schema metadata
survives the sink path.

## CSV, line, and JSON input

### Validate CSV schema override lengths

Since `1.20.0`, `read_csv` validates the length of `schema_overrides`. An
override sequence with the wrong length raises instead of proceeding.

### Insert missing CSV columns safely

Since `1.40.0`, `scan_csv(missing_columns="insert")` preserves data in columns
that exist instead of overwriting those values with nulls.

### Control multi-file CSV inference

In `py-1.43.2-rs-0.55.1-0.55.2`, `scan_csv` adds `infer_schema_files` for
multi-file schema inference, and `schema_overrides` accepts a dtype list.

### Use the singular line-reader column

Since `1.40.0`, `scan_lines` and `read_lines` call their implicit output column
`line`, not `lines`.

### Preserve schemas for empty JSON

Since `1.30.0`, constructing a frame from empty JSON preserves its schema.

For the distinction between row-oriented JSON I/O and serialized frame JSON,
see [Serialization, Runtime, and Arrow](serialization-runtime-and-arrow.md).

## Spreadsheet I/O

### Select the Excel engine deliberately

Since `1.0-upgrade`, `read_excel` defaults to Calamine for every Excel format.
Calamine does not accept `engine_options`; request `engine="xlsx2csv"` when
options such as `skip_empty_lines` are required.

### Drop empty spreadsheet rows

Since `1.10.0`, `read_ods` and `read_excel` accept `drop_empty_rows`:

```python
df = pl.read_excel(path, drop_empty_rows=True)
```

### Read named tables and in-memory sources

Since `1.20.0`, `read_excel` can load a named Excel Table with `table_name`, and
every engine used by `read_excel` and `read_ods` accepts raw bytes. `write_excel`
accepts a file-like output object.

## Cloud credentials and remote storage

### Supply provider objects to scans

Since `1.10.0`, AWS and GCP credential-provider utility classes are available,
and `scan_parquet` has an experimental `credential_provider` argument.

Credential-provider objects are excluded from serialization as of `1.20.0`.
Reattach provider state after loading a serialized plan or object.

### Opt in to Azure account keys

Since `1.20.0`, automatic use of an Azure storage-account key is opt-in rather
than implicit.

### Honor configured AWS endpoints

Since `1.30.0`, when Polars obtains AWS configuration through boto3 it also
loads `endpoint_url`, so boto3-configured S3-compatible endpoints are honored.

### Apply invalid-certificate settings

Since `1.20.0`, cloud I/O honors the `allow_invalid_certificates` storage option
instead of ignoring it.

### Extend remote I/O

In `py-1.43.2-rs-0.55.1-0.55.2`, callback sinks can target cloud storage, and
external `object_store` implementations can handle schemes outside the native
set.

## Delta and Iceberg

### Pass existing Delta tables directly

Since `1.10.0`, `scan_delta` and `read_delta` accept a `DeltaTable` object as
their input.

### Allow unordered Delta sinks

Since `1.40.0`, `sink_delta` no longer requires `maintain_order=True`; Delta
writes can use default ordering behavior.

### Write through the Iceberg sink integration

Since `1.40.0`, Polars provides an Iceberg sink DSL and callback for writing
through the sink interface.

## Stable and out-of-core sinks

### Treat sink APIs as stable

Since `1.30.0`, the `sink_*` APIs are stable rather than experimental.

### Budget out-of-core spilling

In `py-1.43.2-rs-0.55.1-0.55.2`, Polars can spill out-of-core work to disk.
Set `POLARS_OOC_DISK_BUDGET_MB` to the disk budget in megabytes.

## Database I/O

### Consume DuckDB Arrow output through SQLAlchemy

Since `1.10.0`, `read_database` can consume DuckDB Arrow output when the query
is supplied as a SQLAlchemy `Selectable`.

### Infer `Int128`

Since `1.30.0`, database reads infer Polars `Int128` when the database exposes
that integer type.

### Create missing ADBC tables on append

Since `1.41.0`, an ADBC write in append mode creates the destination table when
it does not already exist.

## IPC migration

Since `1.40.0`, the cache-related arguments to `scan_ipc` are deprecated. Stop
depending on those caching controls.
