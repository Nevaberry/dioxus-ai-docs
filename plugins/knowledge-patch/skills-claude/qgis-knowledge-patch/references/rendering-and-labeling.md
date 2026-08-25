# Rendering and labeling

Use this reference for symbol extents, label formatting and placement, masks,
temporal raster display, and reusable layer styles.

## Symbol rendering extent buffers (since 3.42)

Symbols can request a configurable buffer around the canvas extent. Features
outside the visible extent are then considered when generated symbols extend
into view, fixing geometry-generator cases such as
`buffer(@geometry, 7)`. Larger buffers improve correctness at a rendering-cost
tradeoff.

## Raster pixel labeling (since 3.42)

Raster layers can label pixels from a selected band through the standard
labeling engine. This includes conflict handling, numeric formatting, text
effects, priority, scale and pixel-size visibility, z-index, and optional
values resampled over neighboring pixels.

## Custom label tab stops (since 3.42)

Label formatting can use a list of custom tab-stop distances instead of one
distance for every tab.

## Expanded CSS for HTML labels (since 3.42)

The text renderer supports `background-color` and `background-image` on block
or inline HTML, point-unit margins on blocks, and `line-height` in points or
percent:

```html
<div style="margin: 5pt 0pt 10pt 0pt; background-color: #fff; line-height: 120%">Text</div>
```

Backgrounds do not work on curved text. Negative margins are limited to the
bottom margin.

## Cross-layer label separation (since 3.44)

Vector labels can reserve a margin that prevents any other labels from being
placed nearby. A separate duplicate-prevention option suppresses matching text
within a minimum distance across all layers; its comparison is case-sensitive.

## Accumulating temporal raster pixels (since 4.0)

Raster layers in represent-temporal-values mode can accumulate pixels over
time. This matches the existing cumulative single-date/time behavior for
vector features, allowing raster and vector animation frames to accumulate
together.

## Editable blank segments in line symbology (since 4.0)

The blank-segment map tool creates, selects, deletes, and resizes per-feature
gaps where a templated line omits hashes or markers. Segments are stored in a
data-defined field or auxiliary-storage property, backed by templated-line
symbol-layer support.

## Bulk layer-style transfer (since 4.0)

The layer-tree menu can copy and paste all named styles between layers in one
operation. Grouped style-category shortcuts transfer related sets of style
properties.

## Whitespace-aware curved-label collisions (since 4.0)

Curved placement has a data-definable option to ignore spaces and tabs during
label/obstacle collision tests. It is off by default and is unavailable to
non-curved placement modes.

## Multipart label distribution (since 4.0)

Multipart labeling can use the largest part only, repeat the same text on every
part, or split newline-delimited label lines across parts. Splitting happens
after the existing wrap-character setting. Surplus lines are not rendered when
the geometry has too few parts.

## Curved-label placement modes (since 4.0)

Curved labels can place successive characters at line vertices, stretch
character spacing to the line length, or stretch word spacing to the line
length. The mode can be data-defined per feature. Vertex placement drops
excess characters when the line has too few vertices.

## Shared selective-masking presets (since 4.0)

Store mask sources in named presets to reuse them across layers. Editing a
preset's source selection immediately updates every linked layer. Select
`custom` to retain independent per-layer configuration.

## Editable templated-line items (since 4.2)

Hash and marker line symbol layers have start/end trim distances. Templated-line
tools can create, move, rotate, and delete extra hashes or markers that share
the original item's style and state.
