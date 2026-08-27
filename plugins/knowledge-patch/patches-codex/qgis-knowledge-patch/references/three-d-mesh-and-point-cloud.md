# 3D, Mesh, and Point-Cloud Workflows

## 3D scene navigation and clipping

### Cross sections

Since 3.44, the cross-section tool captures start, end, and thickness points on
the 2D canvas, filters the 3D view to the possibly rotated region, and moves the
camera to a side view. Toggling the section does not reload the entire scene.

Since 4.0, sections can use a fixed editable width and be nudged left or right.
Plugins can derive tools from `Qgs3DMapTool`, apply the section's four clipping
planes, and call `Qgs3DMapCanvas.castRay()` to manage hits through `QgsRay3D`.

### Coordinate camera controls

Since 4.2, the camera dialog sets target XYZ in map-CRS coordinates with pitch,
heading, and distance. Optional live update pushes edits to the view; displayed
values always follow camera movement. Configure vertical-axis inversion
separately for walk dragging, captured-mouse walk mode, and terrain mode.

### Expanded scene aids and export

Since 4.0, scene export can omit terrain, extruded polygons can include floors,
and a 3D view can show a camera-centered 2D overlay with an optional frustum.
Since 4.2, scenes can export STL as well as OBJ; STL is simpler and does not
preserve textures.

## Globe and tiled-scene data

### Globe scenes

Since 3.44, globe mode follows the project ellipsoid. Any map layer can provide
the 2D texture, while tiled-scene and point-cloud 3D renderers are supported. A
suitable CRS and ellipsoid can represent another celestial body.

### Esri I3S

Since 4.0, the tiled-scene provider opens I3S 1.7+ `3DObject` and
`IntegratedMesh` data from ArcGIS REST or local SLPK files in 2D and 3D. It
supports global EPSG:4326 and local projected-CRS datasets.

### Expanded 3D Tiles

Since 4.2, QGIS renders 3D Tiles 1.0 `i3dm` and 1.1 glTF GPU instancing in 2D
and 3D, including projected-CRS rotation correction. Quantized positions,
oct-encoded rotations, and feature IDs are unsupported. It also reads 1.1
implicit quadtree tiling and 1.0 composite `cmpt` tiles.

## Vector 3D rendering and materials

### Categorized and rule-based renderers

Since 4.2, vector 3D symbology can use categorized and rule-based renderers with
controls patterned after their 2D counterparts.

### Physically based materials

Since 4.2, physically based materials accept base-color, metalness, roughness,
and ambient-occlusion maps. Metal-rough materials also support opacity, solid
emission color and strength, and data-defined base/emission colors. Metal-rough
and Phong textures expose data-defined scale, rotation, and offset. Save 3D
materials as tagged or favorited style-database presets.

### Model axes

Since 4.2, 3D point-model symbols can choose explicit up and forward axes
instead of assuming Z-up/Y-forward. This avoids corrective rotations that
interfere with reusable rotation, scale, and data-defined settings.

### Environmental lighting and effects

Since 4.2, a cube-map skybox can generate environmental lighting dynamically
for physically based materials. This is optional and does not apply to
fixed-gradient backgrounds. 3D Effects also include tone mapping, exposure,
gamma, light bloom, global MSAA, and configurable gradient backgrounds.

### Annotation billboards

Since 4.0, annotation layers can render marker and text billboards. Markers
support terrain clamping, offsets, and callout lines; text uses a separate 3D
text format.

## Mesh

### View-dependent color ranges

Since 3.42, mesh color-ramp minimum and maximum can be calculated from the
current canvas extent, either locked to one canvas or following the active
canvas like raster rendering.

### Editing and elevation

Since 3.42, adding a vertex can Delaunay-refine adjacent triangles by flipping
nonconforming edges. Actions select all vertices or only isolated vertices.
For a new vertex, choose whether Z prefers the mesh and then a Z widget or
terrain, or always uses project terrain or the widget. Selected vertices can
infer Z from project terrain.

### Dataset groups

Since 3.42, externally added groups may share names and receive automatic
numbers for disambiguation. Those added groups can be removed; groups belonging
to the original mesh source cannot.

### Surface and server use

Since 3.42, Mesh: Surface to Polygon exports a surface as a MultiPolygon.
Since 4.0, QGIS Server can return mesh-layer GetFeatureInfo responses.

## Virtual point clouds and COPC

### Overview display

Since 3.42, VPC layers render an overview when present and otherwise show
extents when zoomed out. Styling can force extents only, overview only, or both.

### COPC generation and 3D editing

Since 3.44, PDAL Processing can write COPC directly. Point-cloud attributes can
be edited in 3D by choosing an attribute and target value and selecting points
with polygon, paintbrush, or above/below-line tools. An expression can restrict
which selected points change.

### Conversion, remote access, and edit locality

Since 4.0, Build VPC can convert LAS/LAZ inputs to COPC so all data is
renderable, and styling controls how early points replace extents or overviews.
Remote VPCs can be opened directly, but editing requires both the VPC and every
linked COPC file to be local.

### Multiple overviews and zipped VPC

Since 4.2, Build VPC accepts `--overview-length`. Readers recognize every asset
with the `overview` role regardless of ID and render multiple overviews when
zoomed out. `QgsPointCloudLayer.overviews()` and
`QgsVirtualPointCloudProvider.overviews()` return lists, and `.vpz` files can
contain zipped VPC datasets.

## Point-cloud analysis and styling

### M3C2 comparison

Since 4.0, Compare Point Clouds computes signed multiscale distances along
locally estimated surface normals using PDAL `filters.m3c2`. It requires a QGIS
build shipping PDAL later than 2.10.

### Normalization and cleanup

Since 4.0, Height Above Ground either adds `HeightAboveGround` or replaces Z,
using nearby or triangulated ground points classified as class 2. Processing
also includes SMRF ground classification, statistical and radius noise filters,
and point-cloud translation, rotation, and scaling.

### TIN edge limits

Since 4.0, PDAL Export to Raster (TIN) can omit triangles with edges beyond a
maximum length. This requires PDAL 2.6+ and wrench 1.2.2+.

### Per-layer elevation shading

Since 4.2, point-cloud 2D symbology can apply elevation shading per layer rather
than using the map-wide effect, avoiding blending unrelated map content into
the shading.

### Point-color expressions

Since 4.2, renderers can alter base color with an expression using any point
attribute and `@point_color`. Arithmetic is channel-by-channel RGBA.
Multiplication accepts the color on either side; other operators require it on
the left. Example:

```text
@point_color * (@intensity / 65535)
```

## Profiles in 3D

Since 4.0, point clouds can render as continuous profile lines, with tolerance
controlling sparse results and a lockable distance:elevation scale ratio.
Since 4.2, Show Profile in 3D Views draws the elevation curve, derives Z limits
from data within the curve, and links the cursor through line or polygon rubber
bands.
