# Layout, text, and style

Use this reference when splitting terminal areas, positioning rectangles,
composing text, or building themes.

## Layout constraints and spacing

### Typed splitting

`Rect::layout(&layout)` returns a fixed-size array whose length is inferred
from the constraints, making destructuring compile-time checked (since 0.30.0):

```rust
let layout = Layout::vertical([Constraint::Length(3), Constraint::Min(0)]);
let [header, main] = area.layout(&layout);
```

Use `Rect::try_layout` or `Layout::try_areas` for fallible fixed-array
splitting. Use `Rect::layout_vec` when the result should remain a `Vec<Rect>`.

### Fill and conflict behavior

`Constraint::Fill(weight)` receives excess space and shares it
proportionally with other fill constraints. For example, three `Fill`
constraints weighted 1, 2, and 3 divide available space in a 1:2:3 ratio after
higher-priority constraints have been satisfied.

When constraints conflict, solver priority is:

```text
Min > Max > Length > Percentage > Ratio > Fill
```

An impossible set can still resolve nondeterministically. Do not depend on a
particular rectangle winning a conflict.

### Flex defaults and corrected spacing

- `Layout` defaults to `Flex::Start`, and `Min` constraints grow to consume
  excess space. To reproduce the pre-0.26 stretching behavior, explicitly use
  `Flex::Legacy`.
- `Flex::SpaceAround` follows CSS spacing in 0.30.0: gaps between items are
  twice the edge gaps. `Flex::SpaceEvenly` preserves the former behavior of
  equal gaps at edges and between items.
- `Layout::split_with_spacers` returns both constrained areas and the spacer
  rectangles created by flex and spacing:

```rust
let (panes, spacers) = Layout::horizontal([Length(20), Length(20)])
    .flex(Flex::SpaceBetween)
    .spacing(1)
    .split_with_spacers(area);
```

### Gaps and overlaps

`Layout::spacing` accepts ordinary nonnegative gaps, negative overlap, and
`Spacing::{Space, Overlap}` (since 0.29.0). A negative value shares boundary
cells between segments; a later widget rendered into the overlap overwrites
the earlier cell.

```rust
let columns = Layout::horizontal(constraints).spacing(-1).split(area);
```

## Rectangle geometry

- `Rect::centered`, `centered_vertically`, and `centered_horizontally` derive
  centered areas from constraints. `Rect::outer` expands a rectangle by a
  margin (since 0.30.0).
- `Position::offset`, addition, and subtraction work with `Offset`. `Rect`
  supports `Add`, `Sub`, `AddAssign`, and `SubAssign` with offsets; these move
  the rectangle without changing its size.
- `Rows` and `Columns` implement `DoubleEndedIterator`, so coordinate strips
  can use `next_back()` or `.rev()` (since 0.29.0).
- Canvas grids and ordinary rectangle areas can exceed `u16::MAX`; do not
  impose a 65,535-cell limit. `Rect::area()` is `u32`.

```rust
let moved = Rect::new(1, 2, 3, 4) + Offset(1, 2);
```

## Text composition and measurement

### Concatenation

`Text` implements `AddAssign` (since 0.30.0):

```rust
text += other_text;
```

The appended value's top-level style and alignment are ignored. Styles and
alignments attached to its lines and spans are preserved.

### Width and control characters

`Text`, `Line`, and `Span` implement `UnicodeWidthStr`, exposing `width` and
`width_cjk`. `Span` no longer renders Unicode control characters.

An overlong `Line` honors alignment inherited from its parent `Text`, not only
alignment set directly on the line. Parent-level centered or right-aligned
text therefore keeps the corresponding portion when truncated (since 0.29.0).

## Hierarchical styling

Styles patch rather than replace one another in this order:

```text
Widget -> Text -> Line -> Span
```

At each level, specified colors replace inherited colors, added modifiers
accumulate, and `sub_modifier` removes inherited modifiers. Thus an outer
yellow color and an inner bold modifier combine:

```rust
let text = Text::from(Line::from("warning".bold())).yellow();
```

Stylize methods are inherent on `Style`, enabling compile-time constants:

```rust
const PANEL: Style = Style::new().blue().on_black();
```

Applying a `Stylize` shorthand to an owned `String` consumes the string and
returns `Span<'static>`. Clone before styling if the original is still needed:

```rust
let red = value.clone().red();
let blue = value.blue();
```

## Color construction and interoperability

With `palette`, `Color::from_hsl` accepts one `palette::Hsl`, not three `f64`
components. Saturation and lightness use `0.0..=1.0`, and values are clamped
before conversion (since 0.29.0):

```rust
let green = Color::from_hsl(ratatui::palette::Hsl::new(120.0, 1.0, 0.5));
```

The same feature supports HSLuv:

```rust
let color = Color::from_hsluv(ratatui::palette::Hsluv::new(0.0, 100.0, 0.0));
```

With `anstyle`, Ratatui colors can be created from `anstyle` colors. `Color`
also accepts RGB/RGBA arrays and tuples. Primitive values including numbers
and `Cow<str>` implement `Styled`, so they can use helpers such as `.red()`.

Built-in Tailwind families are available under
`ratatui::style::palette::tailwind`; shade fields work in constants:

```rust
use ratatui::style::{palette::tailwind, Color};
const ACCENT: Color = tailwind::BLUE.c900;
```

## Borders and cell symbols

Overlapping borders merge automatically (since 0.30.0). Directly merge cell
symbols with a chosen strategy:

```rust
Cell::new("┘").merge_symbol("┏", MergeStrategy::Exact);
```

`BorderType` includes light and heavy forms of double-, triple-, and
quadruple-dashed borders.

The public `Cell::symbol` is optional. A `None` cell compares and hashes like
an empty symbol, while merging into it installs the incoming symbol directly.
