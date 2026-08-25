# Vector Formats and Databases

## Driver inventory and migration

- **New read-only data sources (3.11.0).** OGR ADBC reads DuckDB or Parquet
  when libduckdb is installed. LIBERTIFF is a native thread-safe read-only
  GeoTIFF reader. RCM and AIVector are also new read-only drivers.

- **Removed drivers and writers (3.11.0).** Removed raster drivers are BLX,
  BT, CTable2, ELAS, FIT, GSAG, GSBG, JP2Lura, OZI OZF2/OZFX3, Rasterlite v1,
  R object `.rda`, RDB, SDTS, SGI, XPM, and DIPex. Removed vector drivers are
  Geoconcept Export, OGDI, SDTS, SVG, Tiger, and UK .NTF. Write support was
  removed from Interlis 1/2, ADRG, PAux, MFF, MFF2/HKV, LAN, NTv2, BYN,
  USGSDEM, and ISIS2.

- **Other compatibility changes (3.11.0).** OGR `Memory` is deprecated and
  aliases unified `MEM`. FileGDB create/update routes through OpenFileGDB. PDF
  creation no longer accepts `GEO_ENCODING=OGC_BP`. The OpenCL warper and the
  unofficial `gdalwarpsimple` and `ogrdissolve` were removed, and the shared
  library major changed.

- **Restored legacy drivers (3.13.0).** OGR Tiger and UK .NTF returned after
  their 3.11 removal but remain candidates for future removal. Another shared
  library major bump requires binary dependents to rebuild or link matching
  libraries.

## Generic OGR, schema, and Arrow behavior

- **Warped-layer Arrow reprojection (3.10.1).** `OGRWarpedLayer` does not take
  its Arrow stream directly from the source, because that bypassed
  reprojection. Arrow-stream reads retain the warped layer's transformation.

- **General OGR VRT source regions (3.10.1).** `SrcRegion` and
  `SetSpatialFilter()` accept any geometry type, and `SrcRegion.clip` is
  applied at `OGRVRTLayer` level.

- **Generated fields and Arrow time values (3.11.0).**
  `OGRFieldDefn::SetGenerated()`/`IsGenerated()` marks generated fields.
  `OSRGetAuthorityListFromDatabase()` enumerates CRS authorities, and
  `OGR_GT_GetSingle()` is exposed through SWIG. `OGRLayer::GetArrowStream()`
  accepts `DATETIME_AS_STRING=YES/NO`; `ogr2ogr` uses it to preserve time
  zones and can transfer dataset relationships when supported.

- **Arrow field selection (3.12.1).** `ogr2ogr` and `VectorTranslate` apply
  `selectFields` correctly through the Arrow path.

- **GeoJSON export options (3.12.1).** `OGR_G_ExportToJson()` accepts
  `ALLOW_MEASURE`, `ALLOW_CURVE`, and `COORDINATE_ORDER`.

- **Arrow validity buffers (3.12.4).** `CompactValidityBuffer()` produces a
  compliant `ArrowArray` when `null_count == 0`.

- **String views and directory capabilities (3.13.0).** Arrow field creation
  and batch writing support string-view values. C adds
  `OGR_L_GetAttributeFilter()`. A driver capability identifies directories
  that may hold multiple vector layers; Shapefile, MapInfo, CSV, FlatGeobuf,
  and MiraMonVector advertise it.

- **Workflow preservation (3.13.0).** Unified vector algorithms propagate
  field domains, relationships, and metadata. Conversion warns if the target
  cannot preserve curve, Z, or M geometry.

## GeoPackage, SQLite, and FlatGeobuf

- **FlatGeobuf without an index (3.10.1).** With `SPATIAL_INDEX=NO`, the writer
  accepts a dataset with no features and treats empty geometries as null.

- **GeoPackage vector copy (3.10.1).** GPKG `CreateCopy()` supports vector
  datasets.

- **SQLite with DQS disabled (3.10.3).** The SQLite dialect and GeoPackage work
  with SQLite 3.49.1 built/configured with `SQLITE_DQS=0`.

- **GeoPackage upsert sources (3.10.3).** `ogr2ogr -upsert` works when its
  source is a GeoPackage.

- **Indexed iteration (3.10.3).** After `SetNextByIndex()`, GeoPackage
  `GetNextFeature()` works without a prior `GetLayerDefn()` call.

- **SQLite initialization and transactions (3.11.0).** SQLite supports
  `SAVEPOINT`; `PRELUDE_STATEMENTS` runs after initialization and SpatiaLite
  loading.

- **SQLite null REGEXP (3.11.4).** `REGEXP` on null matches the official SQLite
  extension behavior.

- **Schema and domain changes (3.12.0).** GeoPackage updates and deletes field
  domains. MEM can create a layer from an `OGRFeatureDefn` and declares
  Boolean, Int16, Float32, JSON, and UUID subtypes. PGDump adds
  `SKIP_CONFLICTS`.

- **Filtered aggregate/count results (3.12.3).** OGRSQL honors a spatial
  filter passed to `ExecuteSQL()` for aggregation records. GeoPackage
  `GetFeatureCount()` returns the filtered count immediately after an insert
  within a transaction.

- **Hilbert SQL (3.13.0).** GeoPackage and SQLite dialects add
  `ST_Hilbert()`.

- **Large SQLite compression blobs (3.13.2).** `ogr_inflate` and `ogr_deflate`
  use the 64-bit blob-result API, avoiding truncation of large results.

## PostgreSQL, MySQL, MSSQL, OCI, and ADBC

- **OCI time-zone timestamps (3.10.1).** OCI exposes a
  `TIMESTAMP_WITH_TIME_ZONE` layer creation option, with matching `ogr2ogr`
  behavior.

- **MSSQL metadata in dbo (3.10.3).** MSSQLSpatial creates metadata tables for
  the `dbo` schema correctly.

- **PostgreSQL and MySQL details (3.11.0).** PostgreSQL correctly escapes table
  names containing `(` in the `TABLES` option. MySQL removes the deprecated
  reconnect option for MySQL 8.0.34 and later.

- **PostgreSQL truncation (3.11.3).** Intended string truncation is restored
  after the 3.11.1 regression.

- **Missing ADBC DuckDB targets (3.11.5).** ADBC returns an error for a
  nonexistent DuckDB database.

- **ADBC BigQuery and lazy loading (3.12.0).** ADBC uses an installed BigQuery
  ADBC driver and defers layer loading when no SQL open option is given.

- **DuckDB 1.5 (3.12.3).** ADBC is compatible with DuckDB 1.5.

- **PostGIS intersection controls (3.13.0).** PostGIS uses full-geometry
  intersection and supports `SPATIAL_FILTER_INTERSECTION=LOCAL|SERVER`.

## Parquet, GeoParquet, and JSON-FG

- **JSON-FG 0.3 and Parquet evolution (3.12.0).** JSON-FG 0.3.0 reads/writes
  curve and measured geometries. Parquet supports editable-layer updates,
  reads/writes the Parquet `GEOMETRY` logical type with libarrow 21 or later,
  and exposes `COMPRESSION_LEVEL` as a layer creation option.

- **Parquet lists (3.12.1).** `LISTS_AS_STRING_JSON=YES/NO` controls list
  representation. `SetIgnoredFields()` works for list-of-structure fields.

- **Hive and GeoArrow interoperability (3.12.2).** Filters work on
  Hive-partitioned Parquet. GeoArrow-encoded files without GeoParquet metadata
  open without conflicting with the `geoarrow.pyarrow` module.

- **LargeList support (3.12.4).** Parquet supports Arrow `LargeList`.

- **Partition metadata (3.13.0).** Vector partitioning creates Parquet
  `_metadata`; `gdal driver parquet create-metadata-file` can create it
  independently.

- **Timestamp With Offset and bounding boxes (3.13.0).** Arrow/Parquet support
  the Timestamp With Offset extension and `TIMESTAMP_WITH_OFFSET` creation
  option. GeoParquet adds `COVERING_BBOX_NAME`.

- **Ignored-field collisions (3.13.1).** `SetIgnoredFields()` works when a
  top-level Parquet column and a nested column share a name.

- **Explicit close/flush (3.11.4).** Arrow and Parquet datasets implement
  `Close()` and call it from destructors so pending output is flushed.

## CSV, GeoJSON, ESRIJSON, and text formats

- **Driver HTTP headers (3.10.1).** GeoJSON-like drivers combine
  `GDAL_HTTP_HEADERS` with their generated `Accept` header; custom headers do
  not replace content negotiation.

- **CSV embedded quotes (3.10.2).** A double quote inside a CSV field value is
  parsed correctly.

- **Full Int64 CSV values (3.10.3).** CSV preserves integer interpretation for
  64-bit values above `2^53`.

- **GeoJSON geometry-first detection (3.10.3).** GeoJSON recognizes features
  whose first object member is `geometry`.

- **Schema and foreign-member controls (3.11.0).** CSV, GML, and SQLite accept
  `OGR_SCHEMA`. GeoJSON adds `FOREIGN_MEMBERS=AUTO|ALL|NONE|STAC`. Newly
  created GeoPackages default to 1.4. Shapefile conversion writes DateTime as
  ISO 8601 text, and TopoJSON reads a top-level `crs`.

- **CSV directory sidecars (3.11.4).** CSV opens a directory containing both
  `.csv` and `.prj` files.

- **ESRIJSON types and detection (3.11.5).** ESRIJSON recognizes
  `esriFieldTypeDateOnly`, `esriFieldTypeTimeOnly`,
  `esriFieldTypeBigInteger`, `esriFieldTypeGUID`, and
  `esriFieldTypeGlobalID`, plus additional document variants during identify.

- **CSV and binary DXF controls (3.12.0).** CSV supports pipe separators,
  `HEADER=YES/NO`, and 64-bit feature IDs. DXF reads binary AutoCAD DXF,
  converts it directly to ASCII DXF, and supports true color, transparency,
  and additional HATCH styling.

- **ODS short rows (3.12.2).** ODS retains title-row field names when the first
  data row has fewer columns.

- **ESRIJSON HTTP method (3.13.0).** `HTTP_METHOD=AUTO|GET|POST` selects the
  ESRIJSON request method.

- **Shapefile aliases and MapInfo bounds (3.13.0).** Shapefile reads long field
  names and aliases from `.shp.xml`; MapInfo exposes coordinate-system bounds
  as `BOUNDS` metadata.

- **Creation-option routing (3.13.1).** For CSV output,
  `GEOMETRY=AS_WKT` supplied as a layer creation option is also applied as a
  dataset creation option.

- **GeoJSON media types (3.13.1).** The writer recognizes
  `application/geo+json` and `application/vnd.geo+json`.

## GML, GMLAS, KML, and XML formats

- **AIXM and coordinate swapping (3.10.1).** GML supports AIXM
  `ElevatedCurve` and honors `SWAP_COORDINATES=YES` even when a geometry lacks
  a spatial reference.

- **ISO center-point circles (3.10.2).** `gml:CircleByCenterPoint()` emits a
  five-point `CIRCULARSTRING`, complying with ISO/IEC 13249-3:2011.

- **Repeated GMLAS string lists (3.10.3).** Every repeated element used for a
  `StringList` field is read.

- **CityGML resolution (3.11.0).** GMLAS resolves CityGML 2.0 without
  `schemaLocation`.

- **Empty GML curves (3.11.1).**
  `<gml:Curve><gml:segments/></gml:Curve>` becomes `LINESTRING EMPTY`.

- **LIBKML creation fields (3.11.1).** LIBKML advertises Date, Time, DateTime,
  and Integer64 for creation and maps them to strings; Boolean fields map
  correctly.

- **JGD2024 (3.11.4).** GML recognizes the JGD2024 CRS used by current Japanese
  Fundamental Geospatial Data.

- **Time instants (3.11.5).** GML and GMLAS support `gml:TimeInstantType`.

- **GML controls and CityGML 3 (3.12.0).** GML adds
  `SKIP_CORRUPTED_FEATURES` and `SKIP_RESOLVE_ELEMS` and reads CityGML 3 Shell
  geometry.

- **GML 3D discovery (3.12.1).** GML accepts 3D geometries when `srsName` is
  three-dimensional without requiring `srsDimension='3'`. If several geometry
  elements exist and the last is consistently selected, that geometry column
  receives a name.

- **LIBKML name collisions (3.12.2).** A simple field that collides with a
  core attribute receives a `2` suffix.

## DXF, MapInfo, MVT, and geometry edge cases

- **Zero-sized DXF insert arrays (3.10.2).** A DXF `INSERT` with zero rows or
  columns is interpreted as a count of one.

- **DXF creation and input (3.11.0).** Creation can set `$INSUNITS` and
  `$MEASUREMENT`; output supports MultiPoint and input supports WIPEOUT.

- **DXF encoding (3.11.5).** The reader honors the `ENCODING` open option.

- **MapInfo pen widths (3.11.5).** `.tab` styling distinguishes pixel (`px`)
  and point (`pt`) widths and accepts fractional point widths.

- **Degenerate MIF lines (3.12.2).** MITAB `.mif` accepts line and multiline
  geometries containing one point or no points.

- **MVT tile fields (3.13.0).** MVT reads expose tile-coordinate fields.

- **Single-part linear references (3.13.2).** `ogrlineref` accepts a
  single-part `MULTILINESTRING` and safely handles non-line input.

## Web services and remote vector sources

- **WFS filtered counts (3.10.3).** `GetFeatureCount()` no longer crashes when
  a WFS layer uses a client-side filter.

- **OAPIF item counts (3.11.1).** OAPIF recognizes `itemCount` in Collection
  descriptions.

- **NGW controls (3.11.0).** NGW supports HTTP timeouts/retries, filtered
  deletes, coded domains, COG and TMS web-map sources, and field alteration.

- **WFS spatial-filter forwarding (3.11.5).** WFS forwards a spatial filter to
  the server even if it cannot interpret the XSD schema.

- **Synthetic GeoServer CRS (3.12.2).** WFS ignores the fake identifier
  `EPSG:404000`.

- **WFS-T typed values (3.12.4).** WFS-T correctly formats `xs:dateTime`,
  `xs:date`, and `xs:boolean`.

## Specialized vector formats

- **Exact nonrectangular clipping (3.10.2).** `ogr2ogr -clipsrc` and
  `-clipdst` reject a geometry that falls inside a nonrectangular clip's
  envelope but does not intersect the clip itself.

- **OpenFileGDB multipatch and ZIP (3.11.0).** OpenFileGDB supports
  `CREATE_MULTIPATCH=YES` and ZIP archives whose contents are directly at the
  archive root.

- **MiraMon and ADBC sources (3.12.0).** MiraMonRaster is read-only; ADBC can
  use an installed BigQuery driver and delays layer loading without an SQL open
  option.

- **NAS property updates (3.12.2).** NAS updates unqualified properties as
  well as qualified equivalents.

- **Complex OSM multipolygons (3.12.2).** OSM again reads complex
  multipolygons after the 3.11.5 regression.

- **MiraMon layer filenames (3.12.4).** MiraMonVector launders `CreateLayer()`
  names for filename safety.

- **ILI2 and MEM relationships (3.13.0).** ILI2 supports INTERLIS 2.4. MEM can
  create, update, and delete dataset relationships.

## Option diagnostics

- **Dataset/layer option mix-ups (3.13.1).** Dataset creation warns when an
  unknown dataset option matches a layer creation option, and layer creation
  emits the converse warning.
