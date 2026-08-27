---
name: qgis-knowledge-patch
description: QGIS
version: "4.2"
license: MIT
metadata:
  author: Nevaberry
---


# QGIS Knowledge Patch

Use this skill when changing QGIS projects, plugins, Processing workflows,
providers, QGIS Server deployments, cartography, layouts, elevation profiles,
or 3D and point-cloud workflows. Inspect the project's QGIS, Qt, GDAL, GEOS,
PDAL, SFCGAL, and provider versions before applying version-dependent advice.

## How to use this skill

1. Identify whether the task concerns desktop behavior, server behavior,
   Processing, Python/C++ APIs, plugin metadata, or provider capabilities.
2. Read the matching topic reference below. Consult more than one when a
   workflow crosses boundaries, such as a plugin invoking Processing or a
   server project backed by PostgreSQL.
3. Check dependency gates explicitly. Several features require particular
   GDAL, PDAL, wrench, SFCGAL, or GeoPandas versions.
4. Preserve changed defaults deliberately when upgrading existing projects.
5. Test provider- and rendering-dependent work against the actual data source,
   because advertised service capabilities and build options affect behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [Cartography, labeling, layouts, and profiles](references/cartography-labeling-layouts-and-profiles.md) | Symbols, labels, temporal display, print layouts, charts, forms, and elevation profiles |
| [Data sources, databases, and server](references/data-sources-databases-and-server.md) | STAC, WMS/WFS/OAPIF, authentication, PostgreSQL, GeoPackage, SQL Server, and QGIS Server |
| [Plugins, APIs, and user interface](references/plugins-api-and-user-interface.md) | Plugin migration, PyQGIS/C++ APIs, expressions, themes, GPS, trust, menus, and settings |
| [Processing, geometry, and raster](references/processing-geometry-and-raster.md) | Algorithms, digitizing, geometry engines, raster export, reprojection, and packaging |
| [3D, mesh, and point cloud](references/three-d-mesh-and-point-cloud.md) | 3D scenes, materials, mesh, COPC/VPC, point-cloud editing, and profiles |

## Breaking changes and migration traps

### Declare QGIS 4 plugin compatibility with version bounds

Plugin compatibility is determined by `qgisMinimumVersion` and the optional
`qgisMaximumVersion`. If the maximum is absent, compatibility extends only to
the end of the minimum version's major line. A plugin retaining QGIS 3.22
support while declaring QGIS 4 compatibility can use:

```ini
[general]
qgisMinimumVersion=3.22
qgisMaximumVersion=4.99
```

The QGIS 4 Ready list accepts a plugin when either bound is at least 4.0.
Remove `supportsQt6=True`: QGIS no longer recognizes it. Before widening the
range, replace Qt 5-only APIs and direct `PyQt5` imports with Qt 6 equivalents,
prefer `qgis.PyQt`, test under QGIS 4, and run `pyqgis4-checker`. Its Qt6 Check
findings identify files and lines but do not block upload or approval.

### Target the separate QGIS 4 settings location

QGIS 4 settings are isolated from QGIS 3. First startup performs a one-time,
lossless copy of the loaded QGIS 3 profile, but later changes do not
synchronize. Update installation, profile-management, and enterprise scripts
to target the QGIS 4 location.

### Account for changed server and layout defaults

- The QGIS Server OAPIF root is `/ogcapi`, not `/wfs3`. Override it with
  `QGIS_SERVER_API_WFS3_ROOT_PATH` when a deployment needs another path.
- New layout legends default to Visible Layers. Choose All Project Layers or
  Manual Layer Selection when that is the intended contract; a global layout
  setting can restore the earlier default.
- WMS service resolution for scale-aware raster extraction defaults to 96 DPI.
- Merge Vector Layers still enables source `layer` and `path` fields by
  default for backward compatibility.

### Replace deprecated hub-distance algorithms

Use the C++ Hub Distance algorithm. It replaces Distance to Nearest Hub
(Points) and Distance to Nearest Hub (Line to Hub), exposes both optional
outputs, and leaves the older pair deprecated.

## High-value workflow guidance

### Make Cloud Optimized GeoTIFF intent explicit

When GDAL 3.13 or later is present, raster Save and Export dialogs can request
COG optimization and pyramids, and Processing can bulk-convert a directory.
For Processing outputs pass `-of COG`; the `.tif` or `.tiff` extension cannot
distinguish the COG and GTiff drivers.

### Handle temporal raster and WMS behavior deliberately

Raster layers representing temporal values can accumulate pixels across time.
WMS-T groups can derive a recursive time dimension from children, and a fixed
raster date/time can define both temporal endpoints. Disabling time propagation
on a group prevents child dimensions from reaching its parent.

### Use the expanded geometry APIs and engines

- PyQGIS exposes `QgsGeos` directly.
- `QgsGeometry.as_numpy()` preserves XY, XYZ, XYM, or XYZM dimensionality.
- `QgsGeometry.area3D()` returns surface area for polygonal and surface types,
  and zero for points and lines.
- `QgsVectorLayer.as_geopandas()` creates a GeoPandas dataframe when GeoPandas
  is installed.
- SFCGAL is available through `QgsSfcgalEngine` and `QgsSfcgalGeometry`.

### Choose OAPIF formats and paths intentionally

OGC API Features connections can select advertised formats, including GML and
bulk-download choices, rather than always using GeoJSON. The server exports
FlatGeobuf. Keep client format selection and the `/ogcapi` server root aligned
with deployment routing.

### Use durable OAuth2 and cloud authentication

OAuth2 can attach extra token-endpoint values as HTTP headers and refresh
tokens automatically while connections remain in use. Authentication-manager
SAS signing supports Microsoft Planetary Computer, while Pro GeoCatalogs can
use SAS plus OAuth2; the authentication configuration travels in STAC, GDAL,
and point-cloud data-source URIs.

### Build reusable layouts instead of per-output workarounds

- Layout legends can wrap text in millimeters and synchronize using explicit
  layer-selection modes.
- Atlas polygons can reshape map frames for clipping and masking, and an atlas
  can render only its current coverage feature.
- Charts accept expression-driven series, filtering, ordering, pie plots, and
  renderer-derived categories and colors.
- Geospatial PDF export can preserve the project layer tree when the map has no
  locked layers, but does not support mutually exclusive groups.

### Treat elevation profiles as project resources

Profiles can be saved, reopened, renamed, removed, and optionally synchronized
to the main layer tree. Per-layer custom tolerance overrides the widget-wide
value. Point clouds can render continuous profile lines, and a profile curve
can be displayed in 3D with linked cursor feedback.

### Validate point-cloud dependency gates

- M3C2 comparison requires a build with PDAL later than 2.10.
- PDAL TIN maximum-edge filtering requires PDAL 2.6+ and wrench 1.2.2+.
- VPC editing requires the VPC and every linked COPC file to be local.
- A `.vpz` may contain a zipped VPC, and multiple assets with the `overview`
  role can supply zoomed-out overviews.

### Select Processing outputs precisely

Temporary outputs can retain user-selected layer names. Batch Processing also
accepts temporary outputs. For raster output, set creation options and NoData
values where exposed; for vector packaging, remember that an extent filter
still creates an empty packaged layer when nothing intersects.

### Control QGIS Server recovery and caching

Set `QGIS_SERVER_PROJECT_CACHE_SIZE` to configure the server project cache.
Set `QGIS_SERVER_RETRY_BAD_LAYERS=true` when each request should retest layers
previously accepted as invalid and restore them after dependencies recover.

## Common correctness checks

### Labels and symbols

- Budget symbol extent buffers: larger buffers fix off-canvas generated-symbol
  clipping but increase rendering work.
- HTML label backgrounds do not work on curved text; negative margins are
  limited to the bottom margin.
- Cross-layer duplicate suppression compares text case-sensitively.
- Whitespace-ignoring collisions apply only to curved placement and default
  off.
- Multipart split labeling drops surplus lines when parts are insufficient;
  vertex-based curved placement similarly drops excess characters.

### Rasters and geometry

- Raster rank excludes NoData by default; its alternate mode propagates any
  input NoData.
- Extract Min/Max Pixel returns one point when multiple pixels tie.
- Approximate Medial Axis uses a 2D projection and ignores Z.
- `native:forcecw` and `native:forceccw` use opposite exterior/interior ring
  conventions; select the intended convention explicitly.
- Enabling Z transformation in Reproject Layer changes vertical coordinates as
  well as horizontal ones.

### Layouts and projects

- Project scale method affects displayed/API scale, visibility, Processing,
  layouts, and server renders, but not map-unit symbol sizes.
- Geospatial PDF layer-tree preservation exports visible and invisible project
  layers and enables attributes for either all layers or none.
- Project-embedded Python is governed separately for macros, expressions,
  actions, and form initialization; do not assume a single trust switch.

### 3D and point clouds

- STL export does not preserve textures; use OBJ when textures matter.
- Environmental cube-map lighting applies to physically based materials but
  not fixed-gradient backgrounds.
- Some instanced 3D Tiles encodings are unsupported: quantized positions,
  oct-encoded rotations, and feature IDs.
- Remote VPC display does not imply remote editing support.

## Version and dependency discipline

Treat provider-advertised capabilities and compiled dependency versions as
runtime facts. In particular, check GDAL before COG, GeoPackage-domain, and
dataset-identification work; PDAL and wrench before point-cloud algorithms;
SFCGAL before medial-axis extensions; and GeoPandas before dataframe export.
When preserving an older project's behavior, set formerly implicit options
explicitly and verify results visually as well as through API or algorithm
outputs.
