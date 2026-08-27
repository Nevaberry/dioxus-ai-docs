# Serialization, Runtime, and Arrow

Use this reference for persisted frames and plans, Python compatibility, NumPy
conversion, Arrow import/export, and protocol boundaries.

## Frame, lazy-plan, and expression serialization

### Distinguish serialization from JSON I/O

Since `1.0-upgrade`, `LazyFrame`, `DataFrame`, and `Expr` serialization defaults
to binary bytes. Use `BytesIO` for the default format or pass `format="json"`.

```python
from io import BytesIO

buf = BytesIO()
df.serialize(buf)
buf.seek(0)
restored = pl.DataFrame.deserialize(buf)
```

Serialized frames must be read with `DataFrame.deserialize`, not `pl.read_json`.

### Treat row JSON as a separate format

Since `1.0-upgrade`, `DataFrame.write_json` writes only row-oriented JSON. The
`row_oriented` and `pretty` arguments were removed. Use serialization APIs when
the output is a Polars persistence artifact rather than a row-data interchange
file.

### Reject incompatible DSL representations

Since `1.30.0`, deserialization rejects a DSL representation incompatible with
the reader. Persisted expressions and lazy plans are compatibility-sensitive;
do not assume a representation can be loaded by an arbitrary reader.

### Serialize byte-backed lazy frames

In `py-1.43.2-rs-0.55.1-0.55.2`, lazy frames backed by in-memory bytes became
serializable instead of failing because of their source representation.

### Reattach credential providers

Since `1.20.0`, credential-provider objects are excluded from serialization.
Serialized objects and plans do not carry provider state; supply it again in the
loading environment.

## Python runtime compatibility

### Respect the supported Python floor

Polars `1.10.0` supports Python 3.9 and newer. Python 3.13 is officially
supported as of `1.20.0`.

### Detect incompatible serialized UDFs

Since `1.10.0`, UDF deserialization checks the Python version. A UDF produced by
an incompatible Python runtime is rejected rather than silently accepted.

### Load pickle payloads across Python versions

Since `1.20.0`, Polars pickle payloads can be loaded across Python versions.
This is distinct from serialized UDF compatibility, which still validates the
runtime version.

### Preserve Python exception identity

Since `1.30.0`, Python exceptions that cross Polars execution retain their
original type and traceback. Catch specific application exceptions and use the
preserved traceback for diagnosis.

## NumPy interoperability

### Use standard `__array__` signatures

Since `1.41.0`, `DataFrame.__array__` and `Series.__array__` match NumPy's
signature, so NumPy callers can pass the standard conversion arguments.

### Expect fixed-size arrays from two-dimensional NumPy input

Since `1.0-upgrade`, constructing a `Series` from a two-dimensional NumPy array
creates fixed-size Polars `Array` values rather than `List` values.

## Arrow imports

### Preserve decimal dtype

Since `1.0-upgrade`, `pl.from_arrow` imports Arrow decimal arrays as Polars
`Decimal` rather than `Float64`. Decimal support is always available, and
`Config.activate_decimals` was removed.

### Consume all chunks of Arrow structs

Since `1.10.0`, constructing a `Series` from a chunked Arrow struct consumes
every chunk instead of omitting chunks after the first.

### Reject duplicate table columns

Since `1.20.0`, constructing from a PyArrow table with duplicate column names
raises `DuplicateError`.

### Preserve Arrow map nulls

In `py-1.43.2-rs-0.55.1-0.55.2`, importing Arrow map arrays preserves their
null values instead of losing them during conversion.

### Account for Arrow stream conversion changes

In `py-1.43.2-rs-0.55.1-0.55.2`, `from_arrow` emits `FutureWarning` when its
input implements `ArrowStreamExportable`. Treat that path as pending change and
surface or test the warning where the conversion boundary matters.

## Arrow exports

### Export Enum values as ordered dictionaries

Since `1.41.0`, exporting Enum data to Arrow produces an ordered dictionary,
preserving the Enum ordering marker for Arrow consumers.

## Dataframe interchange protocol

Since `1.40.0`, Polars dataframe interchange protocol integration is
deprecated. Treat integrations that currently depend on it as transitional.

## Boundary checklist

- Match `serialize` with `deserialize`; do not substitute a row JSON reader.
- Treat DSL plans and UDFs as compatibility-sensitive even when ordinary pickle
  payloads cross Python versions.
- Recreate credentials and other runtime-only provider state after loading.
- Reject duplicate Arrow names before relying on positional identity.
- Check decimal, Enum ordering, fixed-size array, and map-null semantics at Arrow
  boundaries.
- Do not build new long-lived integrations around the deprecated dataframe
  interchange protocol.
