# Vector and database workflows

## Arrow, Parquet, and columnar data

### Arrow stream correctness

`OGRWarpedLayer` obtains Arrow data through the warped layer rather than
directly from its source, preserving reprojection (`3.10.1`). Arrow streams
accept `DATETIME_AS_STRING=YES|NO`; vector translation uses it to preserve time
zones and can carry dataset relationships (`3.11.0`).

Arrow-backed `selectFields` works in `ogr2ogr` and `VectorTranslate`
(`3.12.1`). `CompactValidityBuffer()` produces compliant `ArrowArray` output
when `null_count == 0` (`3.12.4`).

Arrow field creation and batch output support string-view values, and the C API
adds `OGR_L_GetAttributeFilter()` (`3.13.0`).

### Parquet editing, types, and filters

Parquet supports editable layers, `GEOMETRY` with libarrow 21+, and a
`COMPRESSION_LEVEL` layer creation option (`3.12.0`). It adds
`LISTS_AS_STRING_JSON=YES|NO`; ignored fields work for lists of structures
(`3.12.1`).

Hive-partition filters work, and a GeoArrow file lacking GeoParquet metadata
opens without colliding with the `geoarrow.pyarrow` module (`3.12.2`).
`LargeList` is supported (`3.12.4`). Ignored fields work when a top-level and
nested column share a name (`3.13.1`).

Arrow and Parquet support Timestamp With Offset and the
`TIMESTAMP_WITH_OFFSET` layer option. GeoParquet adds `COVERING_BBOX_NAME`
(`3.13.0`).

### Closing and partition metadata

Arrow/Parquet datasets expose `Close()` and flush through it or their
destructors (`3.11.4`). Vector partition can group by geometry type, does not
require `--field`, and builds Parquet `_metadata`; the same index can be made by
`gdal driver parquet create-metadata-file` (`3.13.0`).

Dataset creation warns when an unknown dataset option matches a layer option,
and layer creation gives the converse diagnostic (`3.13.1`).

## GeoPackage and SQLite

### Creation, schema, and capabilities

GeoPackage supports vector `CreateCopy()` (`3.10.1`) and newly created files
default to version 1.4 (`3.11.0`). It supports field-domain update/deletion
(`3.12.0`). GeoPackage and SQLite dialects later add `ST_Hilbert()`
(`3.13.0`).

SQLite accepts `SAVEPOINT` and runs `PRELUDE_STATEMENTS` after initialization
and SpatiaLite loading (`3.11.0`). `ogr_inflate` and `ogr_deflate` use the
64-bit blob-result API to avoid large-result truncation (`3.13.2`).

### Correctness fixes

- SQLite SQL and GeoPackage operate with SQLite 3.49.1 and `SQLITE_DQS=0`
  (`3.10.3`).
- GeoPackage indexed iteration works after `SetNextByIndex()` without forcing
  `GetLayerDefn()` (`3.10.3`).
- SQLite `REGEXP` null behavior matches the official extension (`3.11.4`).
- OGRSQL honors an `ExecuteSQL()` spatial filter for aggregate results; a
  GeoPackage count reflects an in-transaction insertion and active filter
  (`3.12.3`).

## Database drivers

### ADBC, DuckDB, and BigQuery

The read-only ADBC driver accesses DuckDB or Parquet when libduckdb is present
(`3.11.0`). It reports a missing DuckDB database rather than pretending to
open it (`3.11.5`). An installed ADBC BigQuery driver is supported, and layers
are loaded lazily when no SQL open option is used (`3.12.0`). DuckDB 1.5 is
supported (`3.12.3`).

### PostgreSQL, PostGIS, MySQL, MSSQL, and OCI

- OCI offers `TIMESTAMP_WITH_TIME_ZONE` during layer creation, with matching
  `ogr2ogr` behavior (`3.10.1`).
- MSSQLSpatial creates `dbo` metadata tables correctly (`3.10.3`).
- PostgreSQL table names containing `(` are escaped in `TABLES`, and MySQL
  removes its obsolete reconnect option for MySQL 8.0.34+ (`3.11.0`).
- PostgreSQL string truncation is restored (`3.11.3`).
- PostGIS uses full-geometry intersection and offers
  `SPATIAL_FILTER_INTERSECTION=LOCAL|SERVER` (`3.13.0`).

### GeoRaster and MongoDB

GeoRaster preserves double quotes inside database connection strings
(`3.12.3`). The MongoDB driver builds with `mongo-cpp-driver` 4+
(`3.11.4`).

## GeoJSON, JSON-FG, ESRIJSON, and TopoJSON

### GeoJSON-family behavior

GeoJSON detection works when a feature object begins with `geometry`
(`3.10.3`). `FOREIGN_MEMBERS=AUTO|ALL|NONE|STAC` controls preserved members
(`3.11.0`). `OGR_G_ExportToJson()` accepts `ALLOW_MEASURE`, `ALLOW_CURVE`, and
`COORDINATE_ORDER` (`3.12.1`). The writer recognizes both
`application/geo+json` and `application/vnd.geo+json` (`3.13.1`).

GeoJSON-like drivers merge caller `GDAL_HTTP_HEADERS` with their generated
`Accept` header (`3.10.1`).

### JSON-FG, ESRIJSON, and TopoJSON

JSON-FG implements specification 0.3.0 and reads/writes curved and measured
geometry (`3.12.0`). ESRIJSON recognizes DateOnly, TimeOnly, BigInteger, GUID,
and GlobalID field kinds and identifies more document variants (`3.11.5`); it
later adds `HTTP_METHOD=AUTO|GET|POST` (`3.13.0`). TopoJSON reads a top-level
`crs` (`3.11.0`).

## GML, GMLAS, and XML-related formats

### Geometry interpretation

GML supports AIXM `ElevatedCurve` and honors `SWAP_COORDINATES=YES` on geometry
without an SRS (`3.10.1`). A center-point circle becomes a five-point
`CIRCULARSTRING` as required by ISO/IEC 13249-3:2011 (`3.10.2`). An empty GML
curve with empty segments becomes `LINESTRING EMPTY` (`3.11.1`).

JGD2024 is recognized (`3.11.4`). GML/GMLAS supports `gml:TimeInstantType`
(`3.11.5`). A 3D `srsName` establishes three-dimensional geometry even without
`srsDimension`; when the last of several geometry elements is consistently
selected, its column is named (`3.12.1`). GML reads CityGML 3 Shell geometry
(`3.12.0`).

### Schema and repeated values

GMLAS reads every repeated element representing a `StringList` (`3.10.3`) and
resolves CityGML 2.0 without `schemaLocation` (`3.11.0`). GML accepts
`SKIP_CORRUPTED_FEATURES` and `SKIP_RESOLVE_ELEMS` (`3.12.0`).

## CSV, tabular, and office formats

### CSV parsing and creation

Embedded double quotes parse correctly (`3.10.2`), and integers above `2^53`
remain 64-bit integers (`3.10.3`). A directory containing `.csv` and `.prj`
files opens as a CSV dataset (`3.11.4`).

CSV creation supports pipe separators and `HEADER=YES|NO`; FIDs are 64-bit
(`3.12.0`). `GEOMETRY=AS_WKT` supplied as a layer option is also routed as a
dataset option (`3.13.1`). CSV, GML, and SQLite accept the `OGR_SCHEMA` open
option (`3.11.0`).

### ODS and Shapefile

ODS preserves title-row field names when the first data row is shorter
(`3.12.2`). Shapefile conversion writes DateTime as ISO 8601 text (`3.11.0`),
and reading `.shp.xml` can supply long names and aliases (`3.13.0`).

## DXF, MapInfo, and CAD

### DXF behavior

An `INSERT` array with zero row/column count is treated as count one
(`3.10.2`). Creation can set `$INSUNITS`/`$MEASUREMENT`, output MultiPoint, and
read WIPEOUT (`3.11.0`). The `ENCODING` open option is honored (`3.11.5`).

AutoCAD Binary DXF can be read and translated directly to ASCII. Reading and
writing support true color, transparency, and more HATCH styles (`3.12.0`).
Edge-built HATCH polygons may be `MULTIPOLYGON`, matching
`OGRBuildPolygonFromEdges()` (`3.11.5`).

### MapInfo and MIF

MapInfo styling distinguishes `px` and `pt` pen widths and permits fractional
points (`3.11.5`). MIF accepts one-point and empty line/multiline geometry
(`3.12.2`). MapInfo exposes coordinate-system bounds as `BOUNDS` metadata
(`3.13.0`).

## KML, MVT, and tile vectors

LIBKML advertises Date, Time, DateTime, and Integer64 for creation, maps them to
strings, and maps Boolean fields correctly (`3.11.1`). A simple field colliding
with a core attribute is renamed with a `2` suffix (`3.12.2`).

MVT supports multiple zoom-zero tiles (`3.10.2`), reads trailing zero padding
(`3.11.5`), and exposes tile-coordinate fields (`3.13.0`).

## FlatGeobuf, OpenFileGDB, and memory datasets

FlatGeobuf accepts an empty dataset with `SPATIAL_INDEX=NO` and writes empty
geometry as null (`3.10.1`).

OpenFileGDB accepts `CREATE_MULTIPATCH=YES` and ZIP files whose contents are at
archive root (`3.11.0`). Its writer rejects range domains missing a bound, while
Python range-domain creation accepts `None`; binding failure is surfaced
(`3.11.1`).

MEM creates layers from `OGRFeatureDefn` and advertises Boolean, Int16,
Float32, JSON, and UUID subtypes (`3.12.0`). It later creates, updates, and
deletes relationships (`3.13.0`).

## Web feature and service drivers

### WFS and WFS-T

WFS feature counts do not crash under a client-side filter (`3.10.3`). A
spatial filter is forwarded even if the XSD is not understood (`3.11.5`). The
synthetic GeoServer CRS `EPSG:404000` is ignored (`3.12.2`). WFS-T formats
`xs:dateTime`, `xs:date`, and `xs:boolean` values correctly (`3.12.4`).

### STACIT, OAPIF, WMS, and NGW

STACIT supports STAC 1.1 and identifies an item if at least two of
`proj:transform`, `proj:bbox`, and `proj:shape` exist (`3.10.2`). It avoids an
initial empty JSON pagination body (`3.12.1`).

OAPIF reads Collection `itemCount` (`3.11.1`). WMS adds an IIIF Image API 3.0
mini-driver (`3.11.1`). NGW adds timeout/retry, filtered delete, coded domains,
COG and TMS web maps, and field alteration (`3.11.0`).

## OGR VRT, filters, and schema

An OGR VRT `SrcRegion` accepts any geometry type, `SetSpatialFilter()` accepts
the same, and clipping applies at the OGRVRTLayer level (`3.10.1`).

Schema overrides can match all layers with `*` and select by
`srcType`/`srcSubType` (`3.12.0`). Unified vector filters can update extents,
and algorithms preserve domains, relationships, and metadata (`3.13.0`).

## Geometry and feature APIs

### Domains, generated fields, and geometry APIs

Generated fields use `SetGenerated()`/`IsGenerated()` (`3.11.0`). Envelope
conversion and constrained Delaunay triangulation are public, and vector
datasets expose `GetSpatialRef()` (`3.12.0`).

Concave hull from polygons and invalidity-reason retrieval are available in C,
C++, and SWIG. `ExportToKML()` fails on invalid latitude instead of emitting
bad coordinates (`3.13.0`).

`OGR_G_SetPoint()` can grow geometry again for an out-of-range insertion index
(`3.13.2`). C point mutation functions return `OGRErr` as described in the API
migration reference.

### Geometry filtering and validation

`gdal vector make-valid` processes 3D geometry (`3.12.1`). Polar reprojection
closes output polygons (`3.12.4`). Curve layers work in unified clip
(`3.13.2`).

## Additional format and service details

- NAS updates qualified and unqualified properties (`3.12.2`).
- OSM complex multipolygons recover from an earlier regression (`3.12.2`),
  and OSM/PBF operation/filter pipelines work (`3.13.2`).
- MiraMonVector launders layer names to safe filenames (`3.12.4`).
- ILI2 supports INTERLIS 2.4 (`3.13.0`).
- PGDump adds `SKIP_CONFLICTS` (`3.12.0`).
- AIVector is a new read-only driver (`3.11.0`).
- A directory-oriented vector capability is advertised by Shapefile, MapInfo,
  CSV, FlatGeobuf, and MiraMonVector (`3.13.0`).

## Conversion safety checklist

1. Explicitly select output drivers and creation/open options.
2. Close Arrow/Parquet outputs and check flush results.
3. Validate whether geometry curves, Z, M, domains, and relationships survive.
4. Test spatial filters in service, SQL, Arrow, and transaction paths.
5. Expect conversion failure on destination field-creation errors unless the
   explicit skip policy is chosen.
