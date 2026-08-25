# Data sources and databases

Use this reference for catalog discovery, database import and administration,
stored projects, query layers, feature-service clients, and authentication
attached to data-source URIs.

## STAC catalog search and footprints (since 3.42)

The Data Source Manager STAC client searches catalogs, applies advanced result
filters, shows or hides result footprints on the map, and highlights the
selected item's footprint.

## SQL from the layer context menu (since 3.42)

Supported layers can execute SQL directly from their context menu in the
project table of contents.

## PostGIS raster storage controls (since 3.42)

The PostgreSQL raster provider can save raster styles in PostGIS. A connection
option hides raster overview tables listed by the PostGIS `raster_overviews`
view from the Browser.

## Database import mapping and filtering (since 3.44)

Database imports can rename fields, select exact destination types, replace
source expressions, exclude fields, or create new fields. Filter by extent,
expression, or current selection, and transform names to upper- or lowercase.

Dragging one layer onto a Browser data source opens controls for destination
name, replacement, primary key, geometry column, CRS, and table comment.
Dragging multiple layers still imports immediately. The single-layer dialog
does not support Oracle.

## SQL query persistence (since 3.44)

The Browser Execute SQL dialog inserts, saves, and removes stored queries held
in either the project or user profile. Its query-history panel is directly
available in the Browser workflow. Execute SQL and Update SQL dialogs can also
save and load `.sql` files.

## Nominatim country filtering (since 3.44)

The Nominatim Geocoder Locator restricts results to one or more countries using
a comma-separated list of two-letter country codes.

## PostgreSQL Browser management (since 3.44)

The Browser renames, deletes, duplicates, or moves PostGIS-stored QGIS projects
to another schema. It can also move PostgreSQL tables between schemas and
rename their fields.

## WFS feature and request modes (since 3.44)

WFS connection URIs and the UI accept `featureMode`:

- `default` retains server behavior.
- `SimpleFeatures` simplifies returned features.
- `ComplexFeatures` disables simplification.

Each WFS connection can use POST instead of the default GET requests.

## Single-schema PostgreSQL connections (since 3.44)

A PostgreSQL connection can be restricted to one schema, limiting both the
Browser and data-source selector to matching tables.

## SQL Server query layers (since 3.44)

Load SQL Server queries as map layers from the Browser. The SQL of an existing
query layer can be updated.

## Browser database administration (since 4.0)

For supporting providers, the Browser edits table comments and creates or
deletes spatial indexes. PostgreSQL layer properties report the current user's
table privileges, estimated row count, and spatial-index information.

## Selectable OAPIF feature formats (since 4.0)

OGC API Features connections can select server-advertised formats instead of
always using GeoJSON. Choices include GML with or without a described schema or
bulk-download link. According to feature mode, GML schema handling uses the
simple parser or GDAL GMLAS. `lastFeatureFormatEncoding` provides the default
for new connections.

## GeoPackage field-domain maintenance (since 4.0)

GeoPackage field domains can be updated or deleted when QGIS uses GDAL 3.12 or
later.

## PostgreSQL project import and versioning (since 4.0)

The Browser can save the open project to a PostgreSQL schema or batch-import
projects from a folder, suffixing colliding names such as `_1`. Stored projects
can have comments shown in Browser tooltips. They can also enable automatic
history and use QGIS dialogs to save, load, edit, and restore older versions.

## Planetary Computer authentication (since 4.0)

The authentication manager supports SAS signing for the open Microsoft
Planetary Computer and SAS plus OAuth2 for Pro GeoCatalogs. The configuration
works with STAC, GDAL, and point-cloud layers and is carried in their data-source
URIs.

## Persistent WMS image-format selection (since 4.0)

WMS connections detect server-advertised image formats and persist the
preferred/default format in settings for later use.

## SensorThings 2.0 (since 4.2)

SensorThings layers support version 2.0 plus the Sensing, Sampling, and
Relations extensions. The Browser and Data Source Manager dynamically detect a
service's version and extensions.

## Changed ESRI REST Browser layout (since 4.2)

The Browser collapses duplicate FeatureServer-vector and MapServer-raster
entries into the FeatureServer item. Raster loading moves to its context menu.
The MapServer `All layers` pseudo-layer is similarly replaced by a context-menu
action on the map service.

## Broader cloud STAC assets (since 4.2)

STAC opens cloud-optimized assets from Azure and Google storage and formats
beyond GeoTIFF, including JPEG 2000, TileDB, and point clouds, when the asset
has a `cloud-optimized` MIME label or a supported asset-type declaration.
