# Layouts, editing, and profiles

Use this reference for digitizing, form behavior, merge policies, layout
legends and charts, atlas framing, Geospatial PDF export, and elevation-profile
persistence and presentation.

## Snapping in the Georeferencer (since 3.42)

The Georeferencer includes snapping options and the Advanced Digitizing panel
for placing reference points against existing geometry.

## Value-relation sorting (since 3.42)

Value Relation widgets can reverse their order or sort choices by a specified
field.

## Per-layer elevation-profile tolerance (since 3.42)

A vector layer's elevation properties can set `custom tolerance`, overriding
the elevation-profile widget's global tolerance for that layer.

## Auto-wrapped layout legends (since 3.44)

Layout legend text can wrap automatically after a configured line length
measured in millimeters.

## Per-field merge policies (since 3.44)

Field configuration controls the initial value used by Merge Features.
Policies include:

- Numeric Sum, Minimum, Maximum, and Geometry Weighted values.
- Default Value.
- Unset Field, falling back to the provider default or first feature.
- Largest Geometry, based on length, area, or part count.
- Set to Null.

## Project-wide scale calculation methods (since 3.44)

Projects calculate scale at the map top, bottom, middle, horizontal average,
or equator. The choice affects new layout scale bars, displayed and API values
such as `@map_scale`, scale-based visibility, Processing map renders, and
server renders. It does not affect symbol sizes in map units. Equator mode is
latitude-independent only for degree-based CRSs.

## Profile subsection indicators (since 3.44)

Elevation profiles and Print Layout profile elements can show subsection
indicators as vertical lines with custom symbology.

## Feature arrays along a line (since 4.0)

A map tool can copy point, line, or polygon features into an array distributed
along a line.

## Layout-legend synchronization modes (since 4.0)

The former Auto update checkbox is replaced by All Project Layers, Visible
Layers, and Manual Layer Selection. Reset replaces Update All. New legends
default to Visible Layers, which follows visibility and layer-tree changes but
does not filter by map extent. A global layout option can restore the previous
default.

## Data-defined layout-grid annotations (since 4.0)

Each grid annotation can be shown or hidden by expression using `@grid_axis`,
`@grid_number`, `@grid_count`, and one-based per-axis `@grid_index` variables.

## Atlas frame and coverage controls (since 4.0)

An atlas polygon can reshape a layout map item's frame for clipping and
masking. A separate atlas option renders only the current coverage feature,
avoiding expressions that suppress the other coverage features.

## Data-driven layout charts (since 4.0)

Print and atlas layouts can contain chart items whose X and Y series come from
source-layer expressions. Bar and line charts support filtering and ordered
iteration; pie charts are also available.

## Bézier, chamfer, and fillet digitizing (since 4.0)

The poly-Bézier/freeform map tool creates NURBS curves by dragging anchors and
handles; `Alt`+click resets a point's handles. Polygon digitizing includes
chamfer and fillet tools. CAD floaters can display Cartesian or ellipsoidal
area and total length/perimeter. Digitizing stays Cartesian, so its ellipsoidal
display can differ.

## Raw attribute copying (since 4.0)

Attribute tables and Identify Results can copy the literal provider value
instead of the represented value produced by locale formatting, expressions,
or display relations.

## Per-field remembered form values (since 4.0)

Attribute forms show a pin indicating whether the last captured value will be
reused and let the user toggle it. Layer form configuration sets session reuse
policies and their defaults or disables reuse for every field.

## Automatic layout-legend inclusion (since 4.0)

Vector, raster, mesh, and point-cloud layer properties have an enabled-by-default
setting that controls whether the layer is added automatically to print-layout
legends.

## Persistent and synchronized elevation profiles (since 4.0)

Save elevation profiles in the project and reopen, rename, or remove them via
the project-level profile manager. Opt-in Synchronize Layers to Project mode
mirrors groups, layer order, and the main layer tree into a profile.
`QgsLayerTreeCustomNode` lets APIs represent non-layer application objects in
layer trees.

## Renderer-derived layout charts (since 4.2)

Layout charts can derive X-axis categories from a source vector layer's
renderer and reuse its symbol colors. A blank series counts matching features;
a Y expression can instead sum a field or calculated value.

## Shape-clipped layout pictures (since 4.2)

A layout picture can be clipped by a shape item. Both pictures and shapes may
be driven dynamically by atlas attributes.

## Layer-tree-aware Geospatial PDFs (since 4.2)

Print-layout Geospatial PDF export can preserve project groups, nesting, order,
names, visibility, and group layers when the map item has no locked layers.
Visible and invisible project layers are exported. Attributes are enabled for
all layers or none, and mutually exclusive groups are unsupported.

## Processing actions in custom UI (since 4.2)

Assign a Processing algorithm to a user-defined menu or toolbar. Triggering
the action opens the algorithm's parameter and execution dialog.
