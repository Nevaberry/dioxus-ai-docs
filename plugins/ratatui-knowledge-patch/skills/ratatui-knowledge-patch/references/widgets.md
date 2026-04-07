# Widgets (0.30-0.31)

## BarChart Constructors

Convenience constructors for common BarChart configurations:

```rust
// Grouped bar chart (default, vertical bars in groups)
let chart = BarChart::grouped(groups);

// Explicit orientation
let chart = BarChart::vertical(groups);
let chart = BarChart::horizontal(groups);

// Bar and BarGroup constructors
let bar = Bar::new(42);
let bar = Bar::with_label("Sales", 42);
let group = BarGroup::new(bars);
let group = BarGroup::with_label("Q1", bars);
```

## List Highlight Symbol Styling

`List::highlight_symbol` accepts `Into<Line>`, enabling styled highlight symbols. This change means the method is no longer const-compatible.

```rust
List::new(items).highlight_symbol(Line::from(">>").red().bold())
```

## Canvas Markers

Three new marker types for canvas rendering:

| Marker | Resolution | Description |
|--------|-----------|-------------|
| `Marker::Quadrant` | 2x2 | Quarter-block characters |
| `Marker::Sextant` | 2x3 | Sextant block characters |
| `Marker::Octant` | 2x4 | Like Braille but with filled blocks |

`Marker` is now `#[non_exhaustive]` -- match statements need a wildcard arm.

## ScrollbarState

`ScrollbarState::get_position()` retrieves the current scroll position.

```rust
let pos = scrollbar_state.get_position();
```

## Tabs

`Tabs::width()` calculates the total rendered width including dividers.

```rust
let w = tabs.width();
```

## Text

`Text` supports `AddAssign` for concatenation:

```rust
let mut text = Text::from("Hello ");
text += Text::from("World");
```

## LineGauge Symbols

`LineGauge::filled_symbol` and `LineGauge::unfilled_symbol` replace the deprecated `line_set` method.

```rust
LineGauge::default().filled_symbol("█").unfilled_symbol("░")
```

## AsRef Impls (0.30.1)

`AsRef<Self>` impls added for all built-in widgets. This may cause type inference ambiguity in rare cases where the compiler cannot determine the target type. Fix by adding explicit type annotations.
