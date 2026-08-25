# 3D, mesh, and point clouds

Use this reference for 3D scene configuration, mesh workflows, virtual point
clouds, point-cloud editing and rendering, and conditional PDAL operations.

## View-dependent mesh color ranges (since 3.42)

Mesh color-ramp minimum and maximum values can be calculated from the current
canvas extent. Lock the range to one canvas or let it follow the active canvas,
matching raster-rendering behavior.

## Mesh editing and elevation controls (since 3.42)

Adding a mesh vertex can Delaunay-refine adjacent triangles by flipping
nonconforming edges. Selection actions cover all vertices or isolated vertices
only. New-vertex Z values can prefer the mesh then a Z widget or terrain,
always use project terrain, or always use the Z widget. Selected vertices can
also infer Z from project terrain.

## Mesh dataset-group management (since 3.42)

Externally added dataset groups may share names and are numbered automatically
to disambiguate them. These groups can be removed; groups belonging to the
original mesh source cannot.

## Virtual point-cloud overview behavior (since 3.42)

VPC layers render an overview when one exists, otherwise extents when zoomed
out. The styling panel can force extents only, overview only, or both.

## 3D cross sections (since 3.44)

The cross-section tool takes start, end, and thickness points from the 2D
canvas, removes everything outside that possibly rotated region from the 3D
view, and moves the camera to a side view. Toggling the section does not reload
the entire scene.

## Globe scenes (since 3.44)

A 3D scene can use globe mode with a mesh following the project ellipsoid. Any
map layer can supply its 2D texture; tiled-scene and point-cloud 3D renderers
are supported. A suitable project CRS and ellipsoid can represent a celestial
body other than Earth.

## COPC Processing output (since 3.44)

PDAL Processing algorithms can write Cloud Optimized Point Cloud outputs
directly.

## Point-cloud editing in 3D (since 3.44)

Choose an attribute and target value, then select points in a 3D view using a
polygon, paintbrush, or above/below-line tool. An expression filter can limit
which selected points are modified.

## Annotation editing and 3D billboards (since 4.0)

The annotation selection tool can multi-select, move, delete, resize, and
rotate items. Annotation layers can render markers and text as 3D billboards.
Marker billboards support terrain clamping, offsets, and callout lines; text
billboards use a separately configurable 3D text format.

## Expanded 3D scene controls (since 4.0)

Cross sections can use a fixed editable width and be nudged left or right.
Scene export can omit terrain, extruded polygons can include floors, and a 3D
view can show a camera-centered 2D map overlay with an optional camera frustum.

## Esri I3S scene layers (since 4.0)

The tiled-scene provider opens I3S 1.7+ `3DObject` and `IntegratedMesh` data
from ArcGIS REST services or local SLPK files in both 2D and 3D. Global
EPSG:4326 and local projected-CRS datasets are supported.

## Virtual point-cloud conversion, access, and editing (since 4.0)

Build VPC can convert LAS/LAZ inputs to COPC so the result is fully renderable.
VPC styling controls how early actual points replace extents or overviews.
Remote VPCs open directly, but editing requires both the VPC and every linked
COPC file to be local.

## M3C2 point-cloud comparison (since 4.0)

Compare Point Clouds computes signed multiscale distances along locally
estimated surface normals through PDAL `filters.m3c2`. It is available only in
QGIS builds shipping PDAL later than 2.10.

## Point-cloud normalization and cleanup (since 4.0)

Height Above Ground adds `HeightAboveGround` or replaces Z using nearby or
triangulated ground points classified as class 2. Processing also provides
SMRF ground classification, statistical and radius noise filters, and point
cloud translation, rotation, and scaling.

## Continuous point-cloud profile lines (since 4.0)

Elevation profiles can draw a point cloud as a continuous elevation line
instead of points; tolerance controls sparse results. A lockable
distance:elevation scale ratio can replace the usual 1:1 navigation ratio.

## Point-cloud TIN edge limits (since 4.0)

PDAL Export to Raster (TIN) can omit triangles whose edges exceed a configured
maximum. This parameter requires PDAL 2.6+ and wrench 1.2.2+.

## Categorized and rule-based 3D rendering (since 4.2)

Vector 3D symbology supports categorized and rule-based renderers with controls
modeled on their 2D counterparts.

## Physically based 3D materials (since 4.2)

The physically based material supports base-color, metalness, roughness, and
ambient-occlusion texture maps. Metal-rough materials also support opacity,
solid emission color and strength, and data-defined base/emission colors.
Metal-rough and Phong textures expose data-defined scale, rotation, and offset.
Save 3D materials as tagged or favorited style-database presets.

## Configurable 3D model axes (since 4.2)

3D point-model symbols can explicitly select up and forward axes instead of
assuming Z-up/Y-forward. This avoids corrective rotations that interfere with
reusable rotation, scale, and data-defined settings.

## 3D environmental lighting and effects (since 4.2)

A cube-map skybox can generate environmental lighting dynamically for
physically based materials. This is optional and does not apply to
fixed-gradient backgrounds. The 3D Effects settings also provide tone mapping,
exposure, gamma, light bloom, global MSAA, and configurable gradient
backgrounds.

## Expanded 3D Tiles support (since 4.2)

QGIS renders instanced meshes from 3D Tiles 1.0 `i3dm` and 1.1 glTF GPU
instancing in 2D and 3D, including projected-CRS rotation correction.
Quantized positions, oct-encoded rotations, and feature IDs are unsupported.
It also reads 1.1 implicit tiling with quadtree subdivision and 1.0 composite
`cmpt` tiles.

## Coordinate-based 3D camera controls (since 4.2)

The camera dialog accepts target XYZ in map-CRS coordinates plus pitch,
heading, and distance. Optional live update pushes edits to the view; displayed
values always follow camera movement. Vertical-axis inversion is configurable
independently for walk dragging, captured-mouse walk mode, and terrain mode.

## STL scene export (since 4.2)

3D scenes export to STL as well as OBJ. STL is simpler and does not preserve
textures.

## Multi-overview and zipped VPC (since 4.2)

Build VPC accepts optional `--overview-length`. Readers recognize every asset
with the `overview` role regardless of ID and render multiple overviews when
zoomed out. `QgsPointCloudLayer.overviews()` and
`QgsVirtualPointCloudProvider.overviews()` return lists. Open zipped VPC data
from `.vpz` files.

## Per-layer point-cloud elevation shading (since 4.2)

Point-cloud 2D symbology can apply elevation shading per layer instead of via
the map-wide effect, preventing unrelated map elements from being blended into
the shading.

## Point-cloud color expressions (since 4.2)

Renderers can modify base color with any point attribute and `@point_color`.
Color arithmetic operates channel by channel on RGBA. Multiplication allows
the color on either side; other operators require it on the left:

```qgis
@point_color * (@intensity / 65535)
```

## Elevation profiles in 3D (since 4.2)

Show Profile in 3D Views displays the profile curve in 3D, derives Z limits
from data within the curve, and links cursor position through line or polygon
rubber bands.
