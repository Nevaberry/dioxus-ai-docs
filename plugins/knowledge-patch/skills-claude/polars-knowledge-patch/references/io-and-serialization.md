# I/O and serialization

Use this reference for file formats, Arrow interchange, databases, cloud
storage, spreadsheet engines, and persisted Polars objects.

## Parquet reading and scanning

### Directories and Hive partitioning (1.0-upgrade)

`read_parquet` and `scan_parquet` accept directories and enable Hive
partitioning by default for a directory. Hive partitioning is disabled by
default for a file, glob, or list of files; pass `hive_partitioning=True` when
those paths should recover partition columns.

### `Float16` decoding (1.10.0)

Parquet readers decode `Float16`, including its column statistics.

### Projection-aware validation (1.10.0)

Parquet reads do not validate dtypes for columns outside the projection. An
unused column with a problematic dtype therefore does not block a projected
read.

### Explicit schema preservation in plans (1.10.0)

The Parquet `schema` argument is carried into the intermediate representation
rather than being dropped during planning.

### Scan cast controls (1.30.0)

`scan_parquet` accepts `cast_options` to control casting while scanning.

### Metadata (1.30.0)

Parquet writers can attach field metadata, and Parquet I/O reads and writes
custom file-level metadata.

### Field IDs from sinks (1.40.0)

`sink_parquet` writes Parquet field IDs so the output retains that schema
information.

### PyArrow-backed column indexing (1.41.0)

`read_parquet` supports index-based column selection when the PyArrow reader is
selected. The same behavior applies to PyArrow-backed `read_csv`.

### Unannotated MAP columns (1.41.0)

The Parquet reader accepts MAP columns without a `LogicalType` annotation.

### Duplicate column names (1.41.0)

Reading a Parquet file with duplicate column names raises `DuplicateError`, so
handle that invalid schema separately from other read failures.

### IEEE 754 ordering metadata (py-1.43.2-rs-0.55.1-0.55.2)

The reader understands column-order metadata requesting IEEE 754 total
ordering.

## CSV, JSON, and line-oriented input

### Row JSON versus serialized frames (1.0-upgrade)

`DataFrame.write_json` emits row-oriented JSON only; `row_oriented` and `pretty`
were removed. This JSON API is distinct from object serialization. A serialized
frame must be read with `DataFrame.deserialize`, not `pl.read_json`.

### CSV schema-override validation (1.20.0)

`read_csv` validates the length of `schema_overrides`; an invalid-length
override sequence raises instead of proceeding.

### Empty JSON schema (1.30.0)

Constructing a frame from empty JSON preserves its schema instead of dropping
schema information.

### Singular line-reader column (1.40.0)

`scan_lines` and `read_lines` name their default column `line`, not `lines`.
Update selectors that depended on the old implicit name or rename explicitly.

### Missing CSV columns (1.40.0)

`scan_csv(missing_columns="insert")` safely inserts absent columns and preserves
data in columns that already exist instead of overwriting it with nulls.

### Multi-file CSV schema controls (py-1.43.2-rs-0.55.1-0.55.2)

`scan_csv` provides `infer_schema_files` to control multi-file schema inference,
and `schema_overrides` accepts a dtype list.

## Arrow interchange

### Decimal preservation (1.0-upgrade)

`pl.from_arrow` converts Arrow decimal arrays to Polars `Decimal`, not
`Float64`. Decimal support no longer requires activation, and
`Config.activate_decimals` was removed.

### Complete chunked struct conversion (1.10.0)

Constructing a `Series` from a chunked Arrow struct consumes every chunk rather
than omitting chunks after the first.

### Duplicate table column names (1.20.0)

Constructing from a PyArrow table with duplicate column names raises
`DuplicateError`, distinguishing this invalid schema from other conversion
failures.

### Ordered dictionaries for Enum (1.41.0)

Exporting Enum data to Arrow produces an ordered dictionary and preserves the
Enum ordering marker for Arrow consumers.

### Arrow stream conversion warning (py-1.43.2-rs-0.55.1-0.55.2)

`from_arrow` emits `FutureWarning` when the input implements
`ArrowStreamExportable`. Account for the pending change when relying on that
conversion path.

### Map null preservation (py-1.43.2-rs-0.55.1-0.55.2)

Importing Arrow map arrays preserves null values instead of losing them during
conversion.

## Excel and ODS

### Calamine default engine (1.0-upgrade)

`read_excel` defaults to `calamine` for every Excel format. Calamine does not
accept `engine_options`; request `engine="xlsx2csv"` for options such as
`skip_empty_lines`.

### Empty-row handling (1.10.0)

`read_ods` and `read_excel` accept `drop_empty_rows`. For example,
`pl.read_excel(path, drop_empty_rows=True)` omits empty rows.

### Tables, bytes, and file-like output (1.20.0)

`read_excel` can load a named Excel Table with `table_name`, such as
`pl.read_excel(source, table_name="Sales")`. Every `read_excel` and `read_ods`
engine accepts raw bytes, and `write_excel` accepts file-like output objects.

## Database and Delta I/O

### Existing Delta table objects (1.10.0)

`scan_delta` and `read_delta` accept a `DeltaTable` object directly.

### DuckDB Arrow through SQLAlchemy (1.10.0)

`read_database` consumes DuckDB Arrow output when the query is a SQLAlchemy
`Selectable`.

### Database `Int128` inference (1.30.0)

Database reads infer Polars `Int128` from databases that expose that integer
type.

### Unordered Delta sinks (1.40.0)

`sink_delta` no longer requires `maintain_order=True`; Delta writes can use the
default ordering behavior.

### ADBC append creates tables (1.41.0)

An ADBC write in append mode creates the destination table when it does not
exist.

## Cloud and remote storage

### Credential providers (1.10.0)

AWS and GCP credential-provider utility classes are available.
`scan_parquet` has an experimental `credential_provider` argument for supplying
one.

### Credential state and Azure keys (1.20.0)

Automatic use of an Azure storage-account key is opt-in. Credential-provider
objects are excluded from serialization, so a serialized plan or object does
not carry provider state.

### Invalid-certificate option (1.20.0)

Cloud I/O honors `allow_invalid_certificates` instead of ignoring it.

### Partitioned Parquet cloud writes (1.20.0)

Partitioned Parquet datasets can be written directly to cloud storage.

### Boto3 endpoint discovery (1.30.0)

When AWS configuration comes from boto3, Polars also loads `endpoint_url`, so
boto3-configured S3-compatible endpoints are honored.

### Extensible remote I/O (py-1.43.2-rs-0.55.1-0.55.2)

Callback sinks can target cloud storage. External `object_store`
implementations can handle schemes outside Polars' native set.

## Serialization and persisted plans

### Binary serialization default (1.0-upgrade)

`LazyFrame`, `DataFrame`, and `Expr` serialization defaults to binary bytes.
Use `BytesIO` with default `serialize`/`deserialize`, or pass `format="json"`
for JSON.

### Version-aware UDF deserialization (1.10.0)

UDF deserialization checks the Python version and detects cross-version
incompatibility rather than silently accepting it.

### Cross-version pickle payloads (1.20.0)

Polars pickle payloads can be loaded across Python versions rather than being
restricted to the Python version that created them.

### Credential providers are not serialized (1.20.0)

Recreate credential-provider state after deserializing a plan or object; the
provider itself is deliberately excluded from serialization.

### Incompatible DSL representations (1.30.0)

Deserialization rejects a DSL representation incompatible with the reader.
Persisted expressions and lazy plans must use a compatible representation.

### Byte-backed lazy frames (py-1.43.2-rs-0.55.1-0.55.2)

Lazy frames backed by in-memory bytes can be serialized instead of failing due
to their source representation.
