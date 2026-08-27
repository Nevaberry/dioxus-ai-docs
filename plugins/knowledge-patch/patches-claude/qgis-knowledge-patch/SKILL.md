---
name: qgis-knowledge-patch
description: QGIS
version: "4.2"
license: MIT
metadata:
  author: Nevaberry
---


# QGIS Knowledge Patch

Use this skill when implementing, reviewing, migrating, or troubleshooting QGIS
desktop, Server, Processing, provider, or PyQGIS work where recent behavior can
change the answer.

## How to use this patch

1. Identify the QGIS version and, for provider-backed features, the packaged
   GDAL, PDAL, wrench, GEOS, or SFCGAL versions.
2. Read only the topic references needed for the task.
3. Apply guidance introduced no later than the project's QGIS version.
4. Prefer the installed build's capabilities, project files, and runtime
   behavior when they differ from this guidance.
5. Treat UI defaults separately from API availability and provider-library
   prerequisites.

## Reference index

| Reference | Use for |
| --- | --- |
| [3D, mesh, and point clouds](references/3d-mesh-and-point-clouds.md) | 3D scenes, mesh editing, VPC/COPC, point-cloud rendering, editing, and analysis |
| [Data sources and databases](references/data-sources-and-databases.md) | STAC, PostgreSQL, SQL Server, imports, Browser administration, OAPIF clients, and SensorThings |
| [Expressions and APIs](references/expressions-and-apis.md) | Expressions, PyQGIS geometry, GPS, SFCGAL, GeoPandas, and 3D extension APIs |
| [Layouts, editing, and profiles](references/layouts-editing-and-profiles.md) | Layouts, legends, charts, digitizing, forms, attributes, and elevation profiles |
| [Plugins, projects, and migration](references/plugins-projects-and-migration.md) | QGIS 4 plugin metadata, Qt 6 migration, themes, project trust, profiles, and custom UI |
| [Processing and analysis](references/processing-and-analysis.md) | Native, raster, vector, terrain, network, geometry, and metadata algorithms |
| [Rendering and labeling](references/rendering-and-labeling.md) | Labels, symbols, masks, temporal rasters, annotations, and style transfer |
| [Server and web services](references/server-and-web-services.md) | QGIS Server, WMS/WFS/OAPIF, OAuth2, caching, GetFeatureInfo, and remote raster behavior |

## Breaking changes and migration

### Advertise QGIS 4 compatibility with version bounds

For plugin repositories, use `qgisMinimumVersion` and optional
`qgisMaximumVersion`. With no maximum, compatibility is assumed only through
the end of the minimum version's major line. A plugin retaining QGIS 3.22
support while advertising QGIS 4 support can use:

```ini
[general]
qgisMinimumVersion=3.22
qgisMaximumVersion=4.99
```

The QGIS 4 Ready list accepts a plugin when either bound is at least 4.0.
Remove `supportsQt6=True`; it is no longer recognized. Before widening the
range, replace Qt 5-only APIs and direct `PyQt5` imports, preferably using
`qgis.PyQt`, test on QGIS 4, and use the repository's `pyqgis4-checker` report.
See [Plugins, projects, and migration](references/plugins-projects-and-migration.md).

### Redirect settings and deployment automation

QGIS 4.2 uses settings separate from QGIS 3. Its first startup makes a
one-time, lossless copy of the loaded QGIS 3 profile, but later edits do not
synchronize. Installation, profile, backup, and enterprise deployment scripts
must target the QGIS 4 location.

### Update the QGIS Server OAPIF route

Since 4.0, the default OAPIF root is `/ogcapi`, replacing `/wfs3`. Set
`QGIS_SERVER_API_WFS3_ROOT_PATH` when a deployment needs another path, and
update reverse-proxy routes, clients, and tests together.

### Replace deprecated hub-distance algorithms

Since 4.0, the C++ Hub Distance algorithm replaces Distance to Nearest Hub
(Points) and Distance to Nearest Hub (Line to Hub). It provides both optional
outputs; migrate models and automation away from the two deprecated IDs.

### Account for changed legend defaults

Since 4.0, layout legends use All Project Layers, Visible Layers, or Manual
Layer Selection instead of the former Auto update checkbox. New legends
default to Visible Layers. This follows layer-tree visibility and changes but
does not filter by map extent; a global layout option restores the old default.

## Capability gates

Check runtime library versions before exposing these operations:

- COG export controls and GDAL Data Identification require GDAL 3.13 or later
  (4.0).
- GeoPackage field-domain updates and deletion require GDAL 3.12 or later
  (4.0).
- M3C2 point-cloud comparison requires a build with PDAL later than 2.10
  (4.0).
- Export to Raster (TIN) maximum-edge filtering requires PDAL 2.6+ and wrench
  1.2.2+ (4.0).
- Approximate Medial Axis `extendToEdges` requires SFCGAL 2.3 (4.2).
- Some raster, point-cloud, 3D Tiles, I3S, and provider features remain
  conditional on the providers compiled into the installed QGIS build.

## High-value desktop behavior

### Choose the right layout-legend mode

- All Project Layers tracks the whole project.
- Visible Layers tracks visibility, order, and layer-tree changes.
- Manual Layer Selection keeps an explicit list.
- Per-layer automatic legend inclusion is enabled by default for vector,
  raster, mesh, and point-cloud layers (4.0).

### Keep temporary outputs named

Processing outputs can remain temporary while using a user-selected layer
name (4.0). The memory-chip icon still identifies them as temporary; naming a
result does not persist it.

### Preserve raw provider values when copying

Attribute tables and Identify Results can copy literal provider values rather
than represented values affected by locale formatting, expressions, or display
relations (4.0). Choose the raw action for round-tripping or exact comparisons.

### Use cumulative temporal raster rendering

Raster layers in represent-temporal-values mode can accumulate pixels over
time (4.0), matching cumulative vector animation behavior. Enable it when
raster and vector frames must remain temporally aligned.

### Use isolated label-collision controls

- Cross-layer margins reserve space around a label (3.44).
- Duplicate prevention suppresses case-sensitive matching text within a
  minimum distance across all layers (3.44).
- Curved labels can ignore spaces and tabs during collision tests; this is off
  by default and applies only to curved placement (4.0).

## High-value Processing behavior

### Distinguish COG from ordinary GeoTIFF

When creating Cloud Optimized GeoTIFF output, pass `-of COG` explicitly (4.0).
The `.tif` or `.tiff` extension cannot distinguish the COG and GTiff drivers.
With GDAL 3.13+, export dialogs can also request optimization and pyramids.

### Preserve provenance when merging vectors

Merge Vector Layers can add source `layer` and `path` attributes (3.42). The
option is enabled by default for backward compatibility; disable it only when
the output schema must exclude provenance.

### Understand raster-rank NoData behavior

Raster rank uses positive ranks from the low end and negative ranks from the
high end: for `[10, 20, 30, 40]`, `2` gives `20` and `-2` gives `30` (3.44).
The default ignores NoData unless the requested rank is unavailable; the
alternate mode propagates NoData when any input cell is NoData.

### Keep WMS extraction scale-aware

Clip Raster by Extent and Clip Raster by Mask Layer can request WMS input at a
reference scale and service resolution (4.0). The default service resolution
is 96 DPI. Use this when scale-dependent remote rendering must survive a clip.

## High-value APIs

### Geometry and dataframe conversion

- `QgsGeometry.as_numpy()` preserves Z and M dimensionality as XYZ, XYM, or
  XYZM arrays (3.42).
- `QgsGeos` is directly available to PyQGIS for GEOS-specific operations not
  exposed by `QgsGeometryEngine` (3.42).
- `QgsGeometry.area3D()` computes polygonal surface area and returns zero for
  points and lines (4.0).
- `QgsVectorLayer.as_geopandas()` creates a GeoPandas dataframe when GeoPandas
  is installed (4.0).

### Time-zone semantics

`convert_timezone` preserves the instant and changes its local representation;
`set_timezone` replaces the zone without changing the date or time components
(4.0). Use `timezone_from_id`, `timezone_id`, and `get_timezone` for IANA-zone
creation and inspection.

### Point-cloud color expressions

Point-cloud renderers can modify `@point_color` with point attributes (4.2).
Arithmetic is channel-by-channel RGBA. Multiplication permits the color on
either side, while other operators require it on the left, for example:

```qgis
@point_color * (@intensity / 65535)
```

## Server operational checks

- `QGIS_SERVER_PROJECT_CACHE_SIZE` controls server project-cache QCache cost
  (3.44).
- `QGIS_SERVER_RETRY_BAD_LAYERS=true` retests previously bad layers on every
  request and restores them after dependencies recover (4.0).
- HTML GetFeatureInfo can use only the layer maptip via the project setting
  corresponding to `WITH_MAPTIP=HTML_FI_ONLY_MAPTIP` (4.0).
- WMS highlight-label frames accept background, outline color, outline width,
  and size vendor parameters, optionally scoped per map (4.2).
- QGIS Server can answer mesh GetFeatureInfo (4.0) and export FlatGeobuf from
  OGC API Features (4.2).

## Verification checklist

- Confirm the installed QGIS and provider-library versions.
- Check defaults separately for newly created and existing projects.
- For plugin migration, test imports, metadata bounds, UI behavior, and package
  validation on QGIS 4.
- For Server changes, test direct requests and proxy-routed public URLs.
- For Processing, inspect output schema, NoData handling, CRS, temporary versus
  persisted status, and conditional outputs.
- For 3D or point clouds, verify both renderer support and data locality before
  enabling editing.
