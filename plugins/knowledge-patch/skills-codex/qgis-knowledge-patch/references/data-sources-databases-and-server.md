# Data Sources, Databases, and QGIS Server

## Catalogs, geocoding, and cloud assets

### STAC search and footprints

Since 3.42, the Data Source Manager STAC client searches catalogs, applies
advanced result filters, shows or hides result footprints, and highlights the
selected item's footprint.

Since 4.2, STAC can open cloud-optimized assets from Azure and Google storage
and formats beyond GeoTIFF, including JPEG 2000, TileDB, and point clouds. The
asset must carry a `cloud-optimized` MIME label or a supported asset-type
declaration.

### Nominatim country filters

Since 3.44, the Nominatim Geocoder Locator can restrict results to a
comma-separated set of two-letter country codes.

### Planetary Computer authentication

Since 4.0, the authentication manager supports SAS signing for the open
Microsoft Planetary Computer and SAS plus OAuth2 for Pro GeoCatalogs. The auth
configuration works with STAC, GDAL, and point-cloud layers and is preserved in
their data-source URIs.

## WMS and temporal sources

### WMS-T group and raster ranges

Since 3.44, a WMS-T layer-tree group can recursively derive a time dimension
from its children. Disabling the dimension on a group stops its children's
dimensions propagating upward. Group dimensions can include OGC WMS/ISO 8601
date ranges; a raster can use one fixed date/time for both ends of its range.

### Persistent image formats

Since 4.0, WMS connections detect server-advertised image formats and persist
the preferred/default choice in settings.

### Highlight-label frames

Since 4.2, QGIS Server WMS requests can style highlight-label frames with
`HIGHLIGHT_LABELFRAMEBACKGROUNDCOLOR`,
`HIGHLIGHT_LABELFRAMEOUTLINECOLOR`,
`HIGHLIGHT_LABELFRAMEOUTLINEWIDTH`, and `HIGHLIGHT_LABELFRAMESIZE`. Scope a
parameter to a map when needed, for example
`MAP0:HIGHLIGHT_LABELFRAMESIZE=5`.

## WFS, OAPIF, and SensorThings

### WFS feature and request modes

Since 3.44, WFS connection URIs and the UI accept `featureMode`. `default`
keeps server behavior, `SimpleFeatures` simplifies results, and
`ComplexFeatures` disables simplification. Each connection can use POST instead
of the default GET.

### Selectable OAPIF feature formats

Since 4.0, OGC API Features connections can select advertised formats instead
of always choosing GeoJSON. Choices include GML with or without a described
schema or bulk-download link. Depending on feature mode, GML schema handling
uses the simple parser or GDAL GMLAS; `lastFeatureFormatEncoding` supplies the
default for new connections.

The default QGIS Server OAPIF root changed in 4.0 from `/wfs3` to `/ogcapi`.
Use `QGIS_SERVER_API_WFS3_ROOT_PATH` to configure another path. Since 4.2, the
service can export FlatGeobuf.

### SensorThings service detection

Since 4.2, SensorThings layers support version 2.0 and the Sensing, Sampling,
and Relations extensions. The Browser and Data Source Manager dynamically
detect the service version and available extensions.

## Database import and SQL

### Database import mapping and filtering

Since 3.44, imports can rename or exclude fields, set exact destination types,
change source expressions, create fields, filter by extent/expression/current
selection, and normalize field names to upper- or lowercase.

Dragging one layer to a Browser data source opens controls for destination
name, replacement, primary key, geometry column, CRS, and table comment.
Multi-layer drops still import immediately. This dialog does not support
Oracle.

### SQL execution and persistence

Since 3.42, supported layers can execute SQL from their project-layer context
menu. Since 3.44, the Browser Execute SQL dialog can insert, save, and remove
stored queries in the project or user profile, and exposes query history in the
Browser workflow. Execute SQL and Update SQL dialogs can save and load `.sql`
files.

### SQL Server query layers

Since 3.44, SQL Server queries can be loaded as map layers from the Browser,
and the SQL of an existing query layer can be updated.

## PostgreSQL and PostGIS

### Raster styles and overview visibility

Since 3.42, the PostgreSQL raster provider can save raster styles in PostGIS. A
connection can hide raster overview tables listed by the PostGIS
`raster_overviews` view from the Browser.

### Single-schema connections

Since 3.44, a PostgreSQL connection can be restricted to one schema, limiting
both the Browser and data-source selector to matching tables.

### Browser management

Since 3.44, the Browser can rename, delete, duplicate, or move PostGIS-stored
QGIS projects to another schema. It can also move PostgreSQL tables across
schemas and rename their fields.

Since 4.0, supporting providers let the Browser edit table comments and create
or delete spatial indexes. PostgreSQL layer properties report the current
user's table privileges, estimated row count, and spatial-index information.

### Project import, comments, and history

Since 4.0, the Browser can save the open project to a PostgreSQL schema or
batch-import projects from a folder. Name collisions receive suffixes such as
`_1`; stored-project comments appear in Browser tooltips. PostgreSQL projects
can enable automatic history and use dialogs to save, load, edit, and restore
earlier versions.

### GeoPackage field domains

Since 4.0, GeoPackage field domains can be updated or deleted when QGIS uses
GDAL 3.12 or later.

## Authentication and project safety

### Extra OAuth2 tokens as headers

Since 3.44, advanced OAuth2 configuration can attach additional values returned
by the token endpoint as HTTP(S) request headers for any OAuth2 service.

### Automatic token refresh

Since 4.0, OAuth2 connections refresh tokens automatically while in use.
Periodic cleanup and layer removal stop refresh for unused connections.

### Localized metadata

Since 4.0, key project and layer metadata participates in project translation,
so translated values can feed layouts, map decorations, and other consumers.

## Browser presentation

### ESRI REST consolidation

Since 4.2, the Browser collapses duplicate FeatureServer-vector and
MapServer-raster entries into the FeatureServer item. Raster loading moves to
its context menu. The MapServer `All layers` pseudo-layer is likewise replaced
by a context-menu action on the map service.

## QGIS Server operation and metadata

### Project cache sizing

Since 3.44, `QGIS_SERVER_PROJECT_CACHE_SIZE` configures the QCache cost used by
the server project cache instead of a hardcoded value.

### Layer-tree group metadata

Since 3.44, groups can publish keywords, data URL and format, attribution title
and URL, metadata URLs, and legend URL and format in GetCapabilities, in
addition to short name, title, and abstract. When no legend URL is set, QGIS
generates a legend by default.

### Maptip-only HTML GetFeatureInfo

Since 4.0, a project-level server setting can make HTML GetFeatureInfo use only
the layer maptip. The corresponding WMS vendor parameter is
`WITH_MAPTIP=HTML_FI_ONLY_MAPTIP`.

### Retrying bad layers

Since 4.0, `QGIS_SERVER_RETRY_BAD_LAYERS=true` makes every request retest layers
previously accepted as bad and return them to service when dependencies
recover.

### Mesh GetFeatureInfo

Since 4.0, QGIS Server can answer GetFeatureInfo requests for mesh layers.
