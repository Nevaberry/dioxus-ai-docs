# Processing and analysis

Use this reference for Processing algorithms, their output contracts, NoData
behavior, conditional library requirements, and replacements for deprecated
algorithm families.

## Layer-metadata Processing algorithms (since 3.42)

The native toolbox can copy metadata between layers, apply metadata from QMD,
export metadata to QMD, append history, update only non-empty fields, and set
basic fields such as identifiers, title, language, CRS, abstract, and fees.

## Expression-driven scatterplot hover text (since 3.42)

Vector Layer Scatterplot can derive optional hover text from a QGIS expression.

## Merge Vector Layers provenance fields (since 3.42)

Merge Vector Layers can add source `layer` and `path` attributes. This option
is enabled by default for backward compatibility.

## Geometry checks and fixes in Processing (since 3.42)

Geometry Checker operations appear under Check Geometry and Fix Geometry.
Checks return an error-only layer plus point error locations and identifiers.
Fixes return a corrected layer, point locations, and a per-feature fix report.

## Plot titles and logarithmic axes (since 3.42)

Scatterplot, Barplot, and Boxplot accept plot and axis titles. An empty axis
title falls back to the field name; a single space suppresses it. Scatterplots
also support logarithmic scaling on either axis.

## Raster-extrema extraction (since 3.42)

Raster Zonal Min/Max emits minimum and maximum pixel-center points for every
polygon zone. Extract Min/Max Pixel emits extrema for a selected raster band
and returns one point only when multiple pixels tie for an extreme.

## Elevation-profile image generation (since 3.42)

A Processing algorithm renders elevation-profile images, allowing models to
generate profiles for multiple curves.

## Mesh surface export (since 3.42)

Mesh: Surface to Polygon exports a mesh surface as a MultiPolygon layer.

## Processing workflow additions (since 3.44)

The native toolbox includes a clone of SAGA Fill Sinks (Wang & Liu), including
the source implementation's existing behavior and bugs. Raster-creation
options are exposed in both Raster Calculator interfaces. Batch Processing
accepts temporary output layers.

## Raster rank (since 3.44)

Raster rank selects the requested rank from input raster values at each cell.
For `[10, 20, 30, 40]`, ranks `2` and `-2` produce `20` and `30`. By default,
NoData values are excluded and only an unavailable rank produces NoData. An
alternate mode propagates NoData when any input cell is NoData.

## Explicit Cloud Optimized GeoTIFF output (since 4.0)

With GDAL 3.13+, raster export and Save dialogs can request COG optimization
and pyramids, and a Processing algorithm can bulk-convert a raster directory.
Processing outputs must pass `-of COG` explicitly because the COG and GTiff
drivers both use `.tif` or `.tiff`.

## Named temporary Processing outputs (since 4.0)

Processing results can remain temporary while carrying a user-selected layer
name. The memory-chip icon continues to identify them as temporary.

## Polygon orientation algorithms (since 4.0)

`native:forcecw` makes exterior rings clockwise and interior rings
counter-clockwise. `native:forceccw` applies the inverse. `native:forcecw`
replicates the existing right-hand-rule operation.

## Network validation algorithms (since 4.0)

Validate Network reports invalid direction values, near-but-unconnected nodes,
and nodes too close to segments. Outputs include bad source features plus line
features describing topology errors. Extract Network Endpoints identifies
sources and sinks by edge direction or degree-one dead ends regardless of
direction.

## Terrain-raster processing controls (since 4.0)

Processing includes feature-preserving DEM smoothing, native Gaussian blur,
and total-curvature algorithms. Slope, aspect, hillshade, and ruggedness expose
output NoData and raster-creation options.

## GDAL dataset identification (since 4.0)

GDAL Data Identification exposes automated dataset metadata extraction and
requires GDAL 3.13 or later.

## Z-aware reprojection (since 4.0)

Reproject Layer has an optional Boolean parameter to transform Z coordinates
along with horizontal coordinates.

## WMS-aware raster extraction (since 4.0)

Clip Raster by Extent and Clip Raster by Mask Layer can request WMS input at a
reference scale and service resolution, preserving scale-dependent rendering.
Service resolution defaults to 96 DPI. Supporting APIs are
`QgsProcessingRasterLayerDefinition` and `QgsWmsUtils`.

## Vector audit, filtering, and packaging outputs (since 4.0)

Delete Duplicate Geometries can emit removed duplicates. Remove Parts by
Length/Area drops undersized parts or entire single-part features. Package
Layers can transform to a destination CRS and filter every input by an extent;
it still creates an empty packaged layer when no features intersect.

## Hub-distance algorithm replacement (since 4.0)

The C++ Hub Distance algorithm replaces Distance to Nearest Hub (Points) and
Distance to Nearest Hub (Line to Hub), and provides both optional outputs. The
two older algorithms are deprecated.

## Geometry-check and medial-axis controls (since 4.2)

Check Holes has an area threshold that excludes holes larger than the threshold
from error results. With SFCGAL 2.3, Approximate Medial Axis accepts
`extendToEdges` to extend skeleton endpoints to the input polygon boundary.

## Concave hulls of polygons (since 4.2)

Concave Hull by Feature accepts polygon and line inputs directly, so polygon
interiors participate without prior vertex extraction. Fill Gaps Between
Polygons creates an outer, possibly non-convex hull without intersecting
polygon interiors. The underlying GEOS concave-hull-of-polygons functionality
is also exposed to PyQGIS.
