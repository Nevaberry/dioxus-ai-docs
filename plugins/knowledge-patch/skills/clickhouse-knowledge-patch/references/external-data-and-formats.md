# External data and formats

Use this reference for object storage, lakehouse catalogs, remote database sources, URL routing, Arrow Flight, and row-to-document or row-to-image formats.

## Object-storage paths and archives

### Recursive globs

The `**/` glob matches zero or more directory levels. Therefore:

```text
data/**/file.txt
```

matches both `data/file.txt` and files under nested directories. If the same-directory match is unwanted, constrain the path pattern rather than assuming `**/` requires at least one child directory.

### Object-storage backups

`BACKUP` and `RESTORE` reject `zip` and `zipx` archives when the destination is direct S3 or Azure storage or an object-storage-backed disk. Use a tar-based archive, such as `tar.gz`.

This restriction concerns direct object-storage destinations; do not infer support merely because a format works on a different backup destination.

## S3 writes and access control

### Hive-style partition paths

Combine `partition_strategy = 'hive'` with `PARTITION BY` on an `S3` engine:

```sql
CREATE TABLE exported
(
    region String,
    day Date,
    value Float64
)
ENGINE = S3(
    's3://bucket/root',
    format = 'Parquet',
    partition_strategy = 'hive'
)
PARTITION BY (region, day);
```

Partition values become Hive-style directory components beneath the root.

### Role assumption and URL-scoped grants

The `s3` table function accepts a custom IAM role:

```sql
SELECT *
FROM s3(
    's3://bucket/path/*.parquet',
    extra_credentials(role_arn = 'arn:aws:iam::123456789012:role/reader')
);
```

Access control can target a URL pattern rather than every S3 resource:

```sql
GRANT READ ON S3('s3://foo/.*') TO analyst;
```

This grant controls ClickHouse access authorization. It does not replace the underlying object-store credential policy.

## Scheme-aware URL dispatch

After applying `url_base`, the `URL` engine and `url` function route schemes as follows:

| Scheme | Implementation |
|---|---|
| `file://` | `File` |
| Standard S3-family schemes | `S3` |
| Azure schemes | `AzureBlobStorage` |
| `hdfs://` | `HDFS` |
| `http://`, `https://` | `URL` |

Non-default S3-compatible vendor schemes such as `cos` and `obs` still require the `s3` engine or function. Do not rely on the URL dispatcher to reinterpret them.

## Persistent remote tables and pass-through queries

### `Remote` and `RemoteSecure`

The table engines are persistent counterparts to the `remote` and `remoteSecure` table functions:

```sql
CREATE TABLE remote_events AS events
ENGINE = Remote('addresses', analytics, events);
```

Use `RemoteSecure` when the native connection must be secured. Engine arguments can include the same routing and authentication inputs needed by the corresponding remote access pattern.

### External database queries

The `mysql`, `postgresql`, and `sqlite` table functions and engines can accept a remote query in place of a table name. Express it either directly or through `query(...)`:

```sql
SELECT *
FROM postgresql(
    'db.example:5432',
    'warehouse',
    query('SELECT id, total FROM orders WHERE status = ''open'''),
    'reader',
    'secret'
);
```

ClickHouse infers the result structure. The resulting source is read-only, even when an engine spelling is used; do not generate `INSERT` against a pass-through-query table.

## Distributed external reads

When parallel replicas are enabled, remote data-access functions invoked on a cluster automatically distribute file processing. Their `...Cluster` variants are no longer required merely to divide the external files.

Opt out when this implicit distribution is undesirable:

```sql
SET parallel_replicas_for_cluster_engines = 0;
```

Account for remote-service concurrency, credentials on each participant, and deterministic file selection when enabling this path.

## Lakehouse catalogs

### Glue and Unity databases

`DataLakeCatalog` exposes catalog tables as ordinary ClickHouse database tables. Glue supplies Iceberg tables; Unity supplies Iceberg or Delta Lake tables.

```sql
CREATE DATABASE glue_catalog
ENGINE = DataLakeCatalog
SETTINGS
    catalog_type = 'glue',
    region = 'us-west-2';

CREATE DATABASE unity_catalog
ENGINE = DataLakeCatalog('https://host/api/2.1/unity-catalog')
SETTINGS
    catalog_type = 'unity',
    warehouse = 'workspace',
    catalog_credential = '...';
```

### Delta Lake writes and catalog maturity

Delta Lake tables support writes and time travel. Unity, REST, Glue, and Hive Metastore catalog integrations moved from experimental to beta. Beta status still calls for compatibility and operational testing before a critical deployment.

## Arrow Flight

Configure `arrowflight_port` and the `arrowflight` server section to expose ClickHouse over Arrow Flight. Query another Flight endpoint through the `arrowFlight` table function or `ArrowFlight` engine:

```sql
SELECT * FROM arrowflight('localhost:6379', 'dataset');
```

Treat the server listener and outbound client as separate configuration surfaces, including transport security and access policy.

## GeoJSON

`FORMAT GeoJSON` emits one `FeatureCollection` feature for each result row:

- The single geometry column becomes `geometry`.
- A column named `id` becomes the feature ID.
- Remaining columns become properties.
- If the only property-bearing column is an object named `properties`, that object is emitted directly.

Invalid shapes are rejected by default under `format_geojson_validate_geometry`. GeoJSON input infers `id` as `Nullable(String)`, preserving the distinction between a missing or null ID and an empty string.

## PNG query output

`FORMAT PNG` maps one query-result row to one pixel. Provide either RGB columns `r`, `g`, and `b`, or a grayscale column `v`. Rows can rely on implicit pixel order or include explicit `x` and `y` coordinates.

Validate dimensions and coordinate uniqueness before emitting a large image; a SQL row-shape error becomes a malformed or unintended raster rather than an ordinary tabular mismatch.
