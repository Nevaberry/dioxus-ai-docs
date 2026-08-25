# Charts, canvas, and symbols

Use this reference when building bar charts, line gauges, canvas graphics, or
custom symbol sets.

## Bar charts

`Bar`, `BarGroup`, and `BarChart` provide constructors, and
`BarChart::grouped` builds a chart from several labeled groups (since 0.30.0).
`Bar` implements `Styled`, so `Stylize` methods can be applied directly:

```rust
let bar = Bar::default().label("Errors").text_value("12").red();
```

`Bar::label` and `Bar::text_value` accept `Into` values. Do not write
`"Errors".into()` at those call sites; explicit conversion of a string literal
can leave the target type ambiguous.

## Line gauges

Set filled and unfilled glyphs independently (since 0.30.0):

```rust
let gauge = LineGauge::default()
    .filled_symbol("█")
    .unfilled_symbol("░")
    .ratio(0.8);
```

`LineGauge::line_set` is deprecated. The default percentage label is padded to
three terminal cells, so changing from one to two or three digits does not
shift the layout. An explicit `.label(...)` retains the caller's unpadded
presentation.

## Canvas resolution

Canvas supports these high-resolution marker grids (since 0.30.0):

| Marker | Pseudo-pixels per cell |
|---|---:|
| `Marker::Quadrant` | 2×2 |
| `Marker::Sextant` | 2×3 |
| `Marker::Octant` | 2×4 |

`Marker` is non-exhaustive, so external `match` expressions need a wildcard
arm. `Marker::Block` renders a full block (`█`); use `Marker::Bar` for the
upper-half-block (`▀`) appearance used by older block-marker rendering.

Canvas grids may have width-times-height greater than `u16::MAX`; do not cap a
valid grid at 65,535 pseudo-pixels.

## Coordinates, clipping, and layering

Canvas coordinates are rounded to the nearest grid cell rather than toward
zero (since 0.30.0). This can move edge pixels and change snapshots.

Lines whose starting point is outside the canvas are clipped and their visible
portion is rendered. `Painter::bounds()` returns the active canvas bounds for
custom painting logic.

Charts and canvases preserve existing Braille or block marks when overlapping
charts or text are drawn. Layers can therefore compose without a later layer
simply erasing an underlying block symbol.

## Runtime symbols and buffer cleanup

Symbol-set types have lifetimes, allowing custom sets to borrow strings built
at runtime instead of requiring `'static` symbols.

Buffer diffs clear the full displayed width of VS16 emoji such as `⌨️`. Later
narrow content no longer leaves a stale trailing cell from the wide emoji.
