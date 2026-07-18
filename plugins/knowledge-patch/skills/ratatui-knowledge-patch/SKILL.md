---
name: ratatui-knowledge-patch
description: Ratatui
license: MIT
version: 0.31.0
metadata:
  author: Nevaberry
---

# Ratatui knowledge patch

Baseline: Ratatui through 0.28.x. Covered range: Ratatui 0.29.0 through 0.31.0.

## Reference index

| Reference | Topics |
|---|---|
| [migration-and-configuration.md](references/migration-and-configuration.md) | MSRV, crate split, Cargo features, `no_std`, breaking migrations, Serde, prelude |
| [layout-text-and-style.md](references/layout-text-and-style.md) | typed layout, flex, overlap, rectangles, text, styles, colors, borders |
| [widgets-and-selection.md](references/widgets-and-selection.md) | tables, lists, tabs, scrollbars, sparklines, titles, calendars, reference widgets |
| [charts-canvas-and-symbols.md](references/charts-canvas-and-symbols.md) | grouped bars, line gauges, canvas markers, clipping, layering, runtime symbols |
| [terminal-backends-and-events.md](references/terminal-backends-and-events.md) | lifecycle, viewports, drawing, cursors, backend traits, event scheduling |
| [architecture-state-and-testing.md](references/architecture-state-and-testing.md) | components, TEA, stateful rendering, templates, snapshots, safe buffers |

## Breaking changes and deprecations

### Toolchain and crates

- Ratatui 0.30.0 requires Rust 1.86.0 and Rust 2024. The current 0.31.0
  workspace requires Rust 1.88.0.
- Applications may keep using `ratatui`. Libraries can use `ratatui-core`,
  `ratatui-widgets`, and backend-specific crates for narrower dependencies.
- A `no_std` build disables defaults. Add `layout-cache` when a `std` build
  disables defaults but still needs cached layout, and add `portable-atomic`
  only on targets without native atomics.
- `palette` and `serde` require `std`.

### Imports and renamed APIs

```rust
// 0.30.0+
use ratatui::layout::HorizontalAlignment;
use ratatui::widgets::{BlockExt, TitlePosition};
```

- Layout `Alignment` is now `HorizontalAlignment`.
- `widgets::block` and `widgets::block::Title` were removed. Pass content
  convertible to `Line` into `Block::title`; use `title_top`/`title_bottom`.
- The prelude includes `Position` and `Size`, but not `Styled`, `Marker`,
  `CompletedFrame`, `TerminalOptions`, or `Viewport`.

### Style migration

```rust
const PANEL: Style = Style::new().blue().on_black();
let reset = Style::reset();
```

- Stylize methods are inherent on `Style`; `Style` itself no longer
  implements `Styled`.
- Replace `style.reset()` with the associated function `Style::reset()`.
- Styling an owned `String` consumes it and produces `Span<'static>`; clone it
  first if it is still needed.

### Backends

Custom backends must define `Backend::Error` and implement `clear_region`.
Generic terminal helpers should return `Result<T, B::Error>` rather than
assuming `std::io::Error`; `TestBackend` uses `Infallible`.

Generic backend conversions were replaced by explicit traits:

```rust
let color = Color::from_crossterm(value);
let backend_color = color.into_crossterm();
```

Equivalent `FromTermion`/`IntoTermion` and `FromTermwiz`/`IntoTermwiz` traits
are available. Prefer `ratatui::crossterm` imports so the version matches the
enabled backend feature.

### Widget and buffer APIs

- Implement `Widget for &Foo` instead of relying on a direct
  `WidgetRef for Foo` implementation to gain `Widget`.
- `StatefulWidget::State` and `StatefulWidgetRef::State` may be unsized.
- `Cell::symbol` is `Option<CompactString>`; direct access must handle `None`.
- `symbols::Marker` is non-exhaustive. Add a wildcard match arm.
- `Marker::Block` is now a full block; use `Marker::Bar` for the former
  upper-half-block canvas appearance.
- `Rect::area()` returns `u32`, and its `Positions` fields are private.
- `LineGauge::line_set` is deprecated; set `filled_symbol` and
  `unfilled_symbol` separately.

### Inference traps

Avoid unnecessary `.into()` when an API itself accepts `Into`:

```rust
let bar = Bar::default().label("name").text_value("42");
let tabs = Tabs::new(["A", "B"]).select(None);
```

Explicit conversions may be needed around `Line: From<Cow<str>>`, while
`Tabs::select(selected.into())` may need an explicitly typed option or
`selected as usize`.

## High-value layout APIs

### Typed areas

```rust
let layout = Layout::vertical([Constraint::Length(3), Constraint::Min(0)]);
let [header, body] = area.layout(&layout);
```

Use `Rect::try_layout` or `Layout::try_areas` for fallible arrays, and
`Rect::layout_vec` for a vector. Center areas with `Rect::centered`,
`centered_vertically`, or `centered_horizontally`; expand with `Rect::outer`.

### Fill, flex, and overlap

- `Constraint::Fill(weight)` proportionally divides excess space.
- Conflict priority is `Min > Max > Length > Percentage > Ratio > Fill`.
- `Flex::SpaceAround` now has CSS semantics; `Flex::SpaceEvenly` preserves the
  earlier equal-edge-gap behavior.
- `Layout::split_with_spacers` exposes generated spacer rectangles.
- Negative spacing creates overlaps. Later rendering wins shared cells:

```rust
let panes = Layout::horizontal(constraints).spacing(-1).split(area);
```

## High-value terminal APIs

### Lifecycle

For the default Crossterm terminal, prefer managed execution:

```rust
ratatui::run(|terminal| {
    terminal.draw(|frame| frame.render_widget("Hello", frame.area()))?;
    Ok(())
})
```

For manual control, call `init`, preserve the application result, call
`restore`, and then return the result. Use `try_init`,
`try_init_with_options`, and `try_restore` to propagate lifecycle errors.

### Viewports and fallible drawing

- `draw` tracks backend resizing for fullscreen and inline viewports, but a
  fixed viewport stays at its configured `Rect`.
- Explicit `Terminal::resize` changes fixed viewports.
- `Terminal::clear` uses the latest resized area.
- `Terminal::try_draw` accepts a fallible callback; errors prevent the update.
- `get_cursor_position`/`set_cursor_position` replace untyped cursor methods.
- `Terminal::size()` returns the real backend `Size`, not a viewport `Rect`.

## High-value widget APIs

### Tables

```rust
state.select_column(Some(column));
state.select_cell(Some((row, column)));
```

Use `column_highlight_style` and `cell_highlight_style`. Overlapping selection
styles apply as row, then column, then cell. `Table` can be collected from
rows, and `Table::flex` controls unused column width.

### Scrollbars, lists, and tabs

- Initialize a scrollbar with `ScrollbarState::new(total)` or it renders
  blank; then set `position` and optionally `viewport_content_length`.
- Set scrollbar orientation before custom symbols, because `orientation`
  resets the symbol set.
- List selection beyond the item count clamps to the last item.
- `Tabs::select(None)` renders no selected tab. The default selected style is
  reversed.

### Optional and stateful rendering

`Option<W>: Widget`, so `None` draws nothing:

```rust
frame.render_widget(show.then(|| Paragraph::new("Details")), area);
```

Stateful widgets mutate separate persistent state during full-frame redraws.
Keep child widget state inside the parent state and pass mutable model access
when rendering can adjust offsets. For lightweight in-place mutation,
implement `Widget` for `&mut MyWidget`.

## Charts and canvas

- `BarChart::grouped` builds multiple labeled bar groups, and `Bar` implements
  `Styled`.
- Canvas adds `Quadrant` (2×2), `Sextant` (2×3), and `Octant` (2×4) markers.
- Canvas coordinates round to the nearest grid cell; out-of-bounds line starts
  are clipped, and `Painter::bounds()` exposes the current bounds.
- Overlaid charts and text preserve Braille and block marks for composition.
- Canvas grids may exceed 65,535 pseudo-pixels.

## Text and color reminders

- `Text += other` appends lines but ignores the appended text's top-level
  style and alignment; line/span attributes remain.
- `Text`, `Line`, and `Span` implement `UnicodeWidthStr` with `width` and
  `width_cjk`; `Span` suppresses Unicode control characters.
- Styles patch in widget → text → line → span order.
- `Color::from_hsl` takes one `palette::Hsl` with saturation/lightness in
  `0.0..=1.0`; `Color::from_hsluv` is also available with `palette`.
- `ratatui::style::palette::tailwind` supplies compile-time color families.

## Testing reminders

- Snapshot a fixed-size `TestBackend` with `insta` and review changes with
  `cargo insta review`.
- Clip a custom widget's area with `area.intersection(buf.area)` before direct
  buffer writes.
- Expect snapshot changes from concise text/style `Debug`, nearest-cell canvas
  rounding, padded line-gauge labels, and inherited-alignment truncation.
