# Cartography, Labeling, Layouts, and Profiles

## Symbols and styles

### Rendering extent buffers

Since 3.42, symbols can request a configurable buffer around the canvas extent
so features outside the visible area remain candidates when generated symbols
extend into view, such as `buffer(@geometry, 7)` geometry generators. Balance
correct edge rendering against the extra work caused by a larger buffer.

### Bulk style transfer

Since 4.0, the layer-tree menu can copy and paste every named style between
layers in one operation. Grouped category shortcuts transfer related groups of
style properties.

### Editable templated-line content

Since 4.0, the blank-segment map tool creates, selects, deletes, and resizes
per-feature gaps in a templated line. Store the gaps in a data-defined field or
auxiliary-storage property. Since 4.2, hash and marker line layers also have
start/end trim distances, and templated-line tools can create, move, rotate,
and delete extra hashes or markers that share the source item's style and
state.

## Labeling

### Raster pixel labels

Since 3.42, a raster can label pixels from a selected band through the regular
labeling engine. Configure conflicts, numeric formatting, text effects,
priority, scale and pixel-size visibility, z-index, and optional values
resampled across neighboring pixels just as deliberately as for vector labels.

### Tabs and HTML text

Since 3.42, label formatting accepts a list of custom tab-stop distances rather
than one distance for every tab. HTML text supports `background-color` and
`background-image` on blocks or inline content, point-unit block margins, and
`line-height` in points or percent:

```html
<div style="margin: 5pt 0pt 10pt 0pt; background-color: #fff; line-height: 120%">Text</div>
```

Backgrounds do not work on curved text, and negative margins are limited to
the bottom margin.

### Cross-layer separation and duplicates

Since 3.44, vector labels can reserve a margin against labels from every layer.
A separate cross-layer duplicate-prevention distance suppresses matching text
using case-sensitive comparison.

### Curved and multipart placement

Since 4.0, curved labels can ignore spaces and tabs during label/obstacle
collision tests through a data-definable, default-off setting unavailable to
other placement modes. Curved text can also place characters at vertices,
stretch character spacing to the line length, or stretch word spacing; the
mode can be data-defined per feature, and vertex mode drops characters when
the line has too few vertices.

Multipart labeling can show text only on the largest part, repeat it on every
part, or distribute newline-delimited lines across parts. Distribution follows
the existing wrap-character processing, and surplus lines are not rendered.

### Shared masking presets

Since 4.0, named selective-masking presets let multiple layers share mask
sources. Editing a preset updates all linked layers immediately; choose
`custom` to retain per-layer configuration.

## Temporal display and scale

### Accumulating raster pixels

Since 4.0, raster layers in represent-temporal-values mode can accumulate
pixels over time, matching cumulative vector behavior so mixed animation
frames stay aligned.

### Project scale method

Since 3.44, projects can calculate scale at the map top, bottom, middle,
horizontal average, or equator. The setting affects new layout scale bars,
displayed and API values such as `@map_scale`, scale visibility, Processing map
renders, and server renders. It does not affect symbol sizes in map units.
Equator mode removes latitude dependence only for degree-based CRSs.

## Layout legends and grids

### Wrapping and synchronization

Since 3.44, legend text can wrap automatically after a length measured in
millimeters. In 4.0, the former Auto update behavior became three modes: All
Project Layers, Visible Layers, and Manual Layer Selection, with Reset replacing
Update All. New legends default to Visible Layers, which follows visibility and
tree changes but does not filter by map extent; a global layout option restores
the previous default.

Since 4.0, vector, raster, mesh, and point-cloud layer properties also have an
enabled-by-default flag controlling automatic inclusion in print legends.

### Data-defined grid annotations

Since 4.0, each layout-grid annotation can be shown or hidden by expression.
Use `@grid_axis`, `@grid_number`, `@grid_count`, and the one-based per-axis
`@grid_index` variables.

### Layer-tree-aware Geospatial PDF

Since 4.2, Geospatial PDF export can preserve project groups, nesting, order,
names, visibility, and group layers when the map item has no locked layers.
Visible and invisible project layers are both exported. Attributes are enabled
for all layers or none, and mutually exclusive groups are unsupported.

## Atlas, pictures, and charts

### Atlas frame and coverage control

Since 4.0, an atlas polygon can reshape a map item's frame for clipping and
masking. A separate option renders only the current coverage feature, avoiding
expressions that hide the other coverage features.

### Shape-clipped pictures

Since 4.2, a layout picture can be clipped by a shape item. Both pictures and
shapes can be driven dynamically by atlas attributes.

### Data-driven charts

Since 4.0, print and atlas layouts can contain chart items whose X and Y series
come from source-layer expressions. Bar and line charts support filtering and
ordered iteration, and pie charts are available.

Since 4.2, a chart can derive X-axis categories and symbol colors from a source
vector renderer. A blank series counts matching features; a Y expression can
instead sum a field or calculated value.

## Annotations and forms

### Annotation editing and billboards

Since 4.0, the annotation selection tool can multi-select, move, delete,
resize, and rotate items. Annotation layers can draw markers and text as 3D
billboards. Marker billboards support terrain clamping, offsets, and callout
lines; text billboards use a separately configurable 3D text format.

### Raw values and remembered values

Since 4.0, attribute tables and Identify Results can copy the literal provider
value rather than the represented value produced by locale formatting,
expressions, or display relations.

Attribute forms expose a pin controlling reuse of the last captured value.
Layer form configuration sets per-field session reuse policy and default, or
disables reuse for every field.

## Elevation profiles

### Layer tolerance and subsection indicators

Since 3.42, a vector layer's elevation properties can set `custom tolerance`,
overriding the profile widget's global tolerance for that layer. Since 3.44,
profiles and Print Layout profile elements can show subsection indicators as
vertical lines with custom symbology.

### Persistent and synchronized profiles

Since 4.0, profiles can be stored in a project and reopened, renamed, or removed
through the project profile manager. The opt-in Synchronize Layers to Project
mode mirrors main-tree groups and order. APIs can use `QgsLayerTreeCustomNode`
to represent non-layer application objects in a layer tree.

### Continuous point-cloud lines and 3D display

Since 4.0, a profile can render point-cloud data as a continuous elevation line;
tolerance controls sparse results. A lockable distance:elevation scale ratio can
replace normal 1:1 navigation.

Since 4.2, Show Profile in 3D Views draws the profile curve in 3D, derives Z
limits from data within the curve, and links cursor position through line or
polygon rubber bands.
