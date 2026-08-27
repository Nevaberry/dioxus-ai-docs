# Processing, Geometry, and Raster Workflows

## Metadata, merging, and plotting

### Layer-metadata algorithms

Since 3.42, the native toolbox can copy metadata between layers, apply metadata
from QMD, export metadata to QMD, append history, update only non-empty fields,
and set basic fields including identifier, title, language, CRS, abstract, and
fees.

### Merge provenance and policies

Since 3.42, Merge Vector Layers can add source `layer` and `path` attributes to
the output. The option is enabled by default for backward compatibility.

Since 3.44, per-field configuration can select the initial Merge Features
value. Policies include numeric Sum, Minimum, Maximum, and Geometry Weighted;
Default Value; Unset Field, which falls back to the provider default or first
feature; Largest Geometry, based on length, area, or part count; and Set to
Null.

### Plot labeling and hover text

Since 3.42, Vector Layer Scatterplot can derive optional hover text from an
expression. Scatterplot, Barplot, and Boxplot accept plot and axis titles. An
empty axis title falls back to the field name; a single space suppresses it.
Scatterplots also support logarithmic scaling on either axis.

## Geometry checking and repair

### Check and fix geometry

Since 3.42, Geometry Checker operations are available under Check Geometry and
Fix Geometry in the Processing Toolbox. Checks return an error-only layer plus
point locations and identifiers. Fixes return corrected features plus point
locations and a per-feature report.

Since 4.2, Check Holes has an area threshold that excludes holes larger than
the threshold from errors. With SFCGAL 2.3, Approximate Medial Axis accepts
`extendToEdges` to extend skeleton endpoints to the input boundary.

### Polygon orientation

Since 4.0, `native:forcecw` creates clockwise exterior and counter-clockwise
interior rings; `native:forceccw` creates the inverse. `native:forcecw`
replicates the existing right-hand-rule operation.

### Concave hulls and polygon gaps

Since 4.2, Concave Hull by Feature accepts polygon and line inputs directly, so
polygon interiors participate without prior vertex extraction. Fill Gaps
Between Polygons creates an outer, potentially non-convex hull without
intersecting polygon interiors. GEOS concave-hull-of-polygons functionality is
also exposed to PyQGIS.

### Native SFCGAL integration

Since 4.0, use SFCGAL through `QgsSfcgalEngine` and the conversion-reducing
`QgsSfcgalGeometry` wrapper. Approximate Medial Axis produces a simplified line
skeleton from a shape's 2D projection and ignores Z.

## Digitizing and feature creation

### Georeferencer snapping

Since 3.42, the Georeferencer includes snapping options and the Advanced
Digitizing panel, allowing reference points to be placed against existing
geometry.

### Arrays along a line

Since 4.0, a map tool can copy point, line, or polygon features into an array
distributed along a line.

### Bézier, chamfer, and fillet tools

Since 4.0, the poly-Bézier/freeform map tool creates NURBS curves by dragging
anchors and handles; `Alt`+click resets a point's handles. Polygon digitizing
has chamfer and fillet tools. CAD floaters can show Cartesian or ellipsoidal
area and total length/perimeter, but digitizing remains Cartesian, so an
ellipsoidal display can differ from the stored construction.

## Raster analysis and output

### Extrema extraction

Since 3.42, Raster Zonal Min/Max outputs minimum and maximum pixel-center points
for every polygon zone. Extract Min/Max Pixel handles a chosen raster band and
returns only one point when multiple pixels tie for an extreme.

### Raster rank

Since 3.44, Raster rank selects a requested rank from input values at each cell.
For `[10, 20, 30, 40]`, ranks `2` and `-2` return `20` and `30`. By default it
excludes NoData and emits NoData only when the rank is unavailable; alternate
mode propagates NoData when any input is NoData.

### Terrain-raster tools

Since 4.0, Processing includes feature-preserving DEM smoothing, native
Gaussian blur, and total-curvature algorithms. Slope, aspect, hillshade, and
ruggedness expose output NoData and raster-creation options.

### Cloud Optimized GeoTIFF

Since 4.0, Raster Export and Save can request COG optimization and pyramids when
GDAL 3.13 or later is available, and a Processing algorithm can bulk-convert a
directory. Pass `-of COG` for Processing output because `.tif` and `.tiff` do
not distinguish the COG and GTiff drivers.

### GDAL data identification

Since 4.0, GDAL Data Identification exposes automated dataset metadata
extraction and requires GDAL 3.13 or later.

### WMS-aware extraction

Since 4.0, Clip Raster by Extent and Clip Raster by Mask Layer can request WMS
input at a reference scale and service resolution, preserving scale-dependent
rendering. Resolution defaults to 96 DPI. Supporting APIs are
`QgsProcessingRasterLayerDefinition` and `QgsWmsUtils`.

## General Processing workflow

### Added raster and batch controls

Since 3.44, QGIS includes a native clone of SAGA Fill Sinks (Wang & Liu),
including the source implementation's existing behavior and bugs. Both Raster
Calculator interfaces expose raster creation options, and Batch Processing
accepts temporary output layers.

### Named temporary outputs

Since 4.0, a result can stay temporary while carrying a user-selected layer
name. The memory-chip icon continues to mark it as temporary.

### Reproject Z values

Since 4.0, Reproject Layer has an optional boolean parameter to transform Z
coordinates together with horizontal coordinates.

### Vector audit, filtering, and packaging

Since 4.0, Delete Duplicate Geometries can output the removed duplicates.
Remove Parts by Length/Area drops undersized parts or entire single-part
features. Package Layers can transform to a destination CRS and filter all
inputs by extent; it still creates an empty packaged layer when no features
intersect.

### Network validation

Since 4.0, Validate Network reports invalid direction values,
near-but-unconnected nodes, and nodes too close to segments. It returns bad
source features and lines describing topology errors. Extract Network Endpoints
finds sources/sinks by edge direction or degree-one dead ends regardless of
direction.

### Hub distance replacement

Since 4.0, the C++ Hub Distance algorithm replaces Distance to Nearest Hub
(Points) and Distance to Nearest Hub (Line to Hub) and offers both optional
outputs. The older algorithms are deprecated.

### Elevation-profile images

Since 3.42, a Processing algorithm renders elevation-profile images and can
generate profiles for multiple curves from a workflow.

### Mesh surface export

Since 3.42, Mesh: Surface to Polygon exports a mesh surface as a MultiPolygon
layer.
