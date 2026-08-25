# Widgets and selection

Use this reference for selection state, table and scrollbar behavior, block
titles, calendars, and generic or optional widget rendering.

## Tables

### Construction and width distribution

`Table` implements `FromIterator` for values convertible to `Row`. Collect the
rows and then set widths; bare `u16` widths convert to `Constraint`:

```rust
let table = [Row::new(["A", "B"])]
    .into_iter()
    .collect::<Table>()
    .widths([10, 20]);
```

`Table::flex` controls unused width. The default leaves extra space
undistributed. `Flex::Legacy` assigns it to the last column.

`Table::default()` leaves one cell between columns. Use `.column_spacing(0)`
when zero-gap rendering is required.

### Row, column, and cell selection

`TableState` supports rows, columns, and cells. Alongside row navigation, use
`select_column(Some(column))`, `select_cell(Some((row, column)))`, the
first/next/previous/last-column helpers, and `scroll_left_by` or
`scroll_right_by` (since 0.29.0).

Configure `row_highlight_style`, `column_highlight_style`, and
`cell_highlight_style`. When selections overlap, styles apply in this order:

```text
row -> column -> cell
```

Column attributes override conflicting row attributes, and the cell style has
final precedence.

## Lists

`List::highlight_symbol` accepts `Into<Line>` (since 0.30.0), so the symbol may
be styled:

```rust
let list = List::new(["Item"])
    .highlight_symbol(Line::from(">>").red().bold());
```

`ListState` implements `Copy`. Rendering clamps an out-of-range selected index
to the last item, including selections produced by `select`, `first`, `last`,
`previous`, and `next`; invalid selection no longer stays invisible.

## Tabs

`Tabs::select` accepts `Into<Option<usize>>`, so `select(None)` renders no
selected tab (since 0.29.0):

```rust
let tabs = Tabs::new(["A", "B"]).select(None);
```

The default highlight style is `Style::new().reversed()`, making a selected
tab visible without explicit styling.

## Scrollbars

`Scrollbar` is rendered separately from the content it describes. It is blank
until its `ScrollbarState` has a content length:

```rust
let state = ScrollbarState::new(total)
    .position(current)
    .viewport_content_length(visible);
```

A viewport length of zero uses the track length. Navigate state with `prev`,
`next`, `first`, `last`, or `scroll(ScrollDirection)`.

Calling `Scrollbar::orientation` also resets symbols to `DOUBLE_VERTICAL` or
`DOUBLE_HORIZONTAL`. Apply custom symbols after orientation, or set both with
`orientation_and_symbol(orientation, symbols)`. A later `symbols(set)` keeps
begin, end, or track symbols explicitly disabled with `None` instead of
restoring those entries from the set.

## Sparklines

Sparkline data distinguishes a missing sample from zero. Customize missing
samples with `absent_value_style` and `absent_value_symbol` (since 0.29.0):

```rust
let sparkline = Sparkline::default()
    .absent_value_symbol(symbols::shade::FULL)
    .data([None, Some(0), Some(3)]);
```

Each `SparklineBar` can carry an optional `Style`. Its style is applied in
addition to the enclosing sparkline style, enabling per-sample styling.

## Blocks and titles

`Block::title` accepts values convertible into `Line`; the former
`widgets::block::Title` type and module were removed in 0.30. Use
`title_top`, `title_bottom`, and `TitlePosition` for placement.

Centered titles truncate symmetrically, while left-aligned titles truncate on
the right. Overlap precedence is:

```text
left < center < right
```

A centered title overwrites a left title; a right title overwrites either.

## Calendar

`Monthly::new(display_date, events)` accepts a `DateStyler`.
`CalendarEventStore` stores per-date styles and provides `today`, `add`, and
`get_style`. Styling precedence is:

```text
default_style -> show_surrounding -> event style
```

The event style wins. Configure the surrounding presentation with
`show_weekdays_header`, `show_month_header`, and `block`. Calendar support is
enabled by default in `ratatui-widgets` as of 0.30.0.

## Optional and generic widgets

`Option<W>` implements `Widget` when `W` does; `None` draws nothing:

```rust
frame.render_widget(show.then(|| Paragraph::new("Details")), area);
```

Every built-in widget implements `AsRef<Self>`, allowing generic helpers to
accept owned or borrowed widgets through an `AsRef<WidgetType>` bound.

## Reference rendering

`WidgetRef` and `StatefulWidgetRef` remain experimental and are outside
semantic-versioning guarantees. Avoid exposing them from stability-sensitive
APIs without accepting possible method, signature, and behavior changes.

`WidgetRef` supports trait objects, so heterogeneous, runtime-selected widgets
can be collected and rendered repeatedly:

```rust
let widgets: Vec<Box<dyn WidgetRef>> =
    vec![Box::new(Greeting), Box::new(Farewell)];
for widget in &widgets {
    widget.render_ref(area, buf);
}
```

For 0.30.0+, implement `Widget` for `&Foo` rather than relying on a direct
`WidgetRef for Foo` implementation to gain `Widget`. Frame reference rendering
also needs `unstable-widget-ref` and `widgets::FrameExt`.

## Project art widgets

- `RatatuiLogo::tiny()` renders a 2×15-cell logo; `RatatuiLogo::small()`
  renders a 2×27-cell logo (since 0.29.0).
- `RatatuiMascot::default()` renders the rat mascot (since 0.30.0).
