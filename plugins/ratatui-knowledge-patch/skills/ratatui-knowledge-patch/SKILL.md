---
name: ratatui-knowledge-patch
description: "Ratatui changes since training cutoff (latest: 0.31.0) — ratatui::run() entry point, Rect arithmetic, border merging, const Style, no_std support, widget updates. Load before working with Ratatui."
version: "0.31.0"
license: MIT
metadata:
  author: Nevaberry
---

# Ratatui Knowledge Patch

Covers new APIs and breaking changes in Ratatui 0.30-0.31. Assumes familiarity with Ratatui basics through 0.29.x (tui-rs heritage, widget system, immediate-mode rendering).

| Topic | File | Key Content |
|-------|------|-------------|
| Layout | `references/layout.md` | Rect arithmetic, Flex::SpaceEvenly, centered variants |
| Widgets | `references/widgets.md` | BarChart, List, canvas markers, LineGauge, ScrollbarState |
| Styling & Borders | `references/styling-and-borders.md` | Border merging, dashed borders, Color conversions |
| Migration Guide | `references/migration-guide.md` | Alignment rename, WidgetRef reversal, backend Error type, FromCrossterm |
| Backend & Platform | `references/backend-and-platform.md` | Crossterm versions, no_std, ratatui-core modularization |

## Entry Point: `ratatui::run()`

*Added in 0.30.* Handles `init()`/`restore()` automatically. Accepts a closure that receives `&mut DefaultTerminal`.

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    ratatui::run(|terminal| {
        loop {
            terminal.draw(|frame| frame.render_widget("Hello World!", frame.area()))?;
            if crossterm::event::read()?.is_key_press() {
                break Ok(());
            }
        }
    })
}
// Also works with methods: ratatui::run(App::new().run)?;
```

## Rect Layout Methods

*Added in 0.30.* `Rect::layout` splits into a fixed-size array with compile-time size inference. `Rect::centered` centers a sub-rect using constraints.

```rust
let layout = Layout::vertical([Constraint::Fill(1); 2]);
let [top, main] = area.layout(&layout); // array size inferred
// Fallible: area.try_layout(&layout)?, layout.try_areas(area)?
// Vec: area.layout_vec(&layout)

let popup = area.centered(Constraint::Ratio(1, 2), Constraint::Ratio(1, 3));
let strip = area.centered_vertically(Constraint::Length(5));
let col = area.centered_horizontally(Constraint::Length(20));
```

### Rect Arithmetic

```rust
use ratatui::layout::Offset;

let moved = rect + Offset { x: 5, y: 0 }; // move right
let moved = rect - Offset { x: 5, y: 0 }; // move left
let expanded = rect.outer(Margin {
    horizontal: 2,
    vertical: 1,
}); // inverse of inner()
let resized = rect.resize(new_width, new_height);
```

See `references/layout.md` for Flex changes and `Direction::perpendicular()`.

## Style Const Shorthand

*Added in 0.30.* Color methods like `.blue()`, `.on_black()` are now `const` on `Style` directly (no longer require `Styled` trait).

```rust
const MY_STYLE: Style = Style::new().blue().on_black();
```

## `block::Title` Removed

*Breaking in 0.30.* Use `Line` directly for block titles. `block::Position` moved to `widgets::TitlePosition`. `BlockExt` moved to `widgets::BlockExt`.

```rust
// Old: Block::default().title(Title::from("Hi").position(Position::Bottom))
// New:
Block::default().title_bottom(Line::from("Hi").centered());
```

## `Flex::SpaceAround` Semantics Changed

*Breaking in 0.30.* Old `SpaceAround` behavior is now `Flex::SpaceEvenly`. New `SpaceAround` matches CSS flexbox semantics (inter-item spacing is 2x edge spacing).

## Key Widget Changes (0.30)

### BarChart constructors

```rust
let chart = BarChart::grouped(groups); // default vertical grouped
let chart = BarChart::horizontal(groups);
let bar = Bar::with_label("Sales", 42);
let group = BarGroup::with_label("Q1", bars);
```

### List highlight symbol styling

`List::highlight_symbol` now accepts `Into<Line>`, enabling styled highlight symbols (no longer const-compatible):

```rust
List::new(items).highlight_symbol(Line::from(">>").red().bold())
```

### New canvas markers

`Marker::Quadrant` (2x2), `Marker::Sextant` (2x3), `Marker::Octant` (2x4, like Braille but filled). `Marker` is now `#[non_exhaustive]`.

### Other widget additions

- `ScrollbarState::get_position()` retrieves current scroll position
- `Tabs::width()` calculates total width including dividers
- `Text += Text` via `AddAssign`
- `LineGauge::filled_symbol` / `unfilled_symbol` replace deprecated `line_set`

See `references/widgets.md` for full details and code examples.

## Styling & Borders

### Border merging

*Added in 0.30.* Overlapping borders auto-merge into clean intersections via `MergeStrategy`.

### New dashed `BorderType`s

`LightDoubleDashed`, `HeavyDoubleDashed`, `LightTripleDashed`, `HeavyTripleDashed`, `LightQuadrupleDashed`, `HeavyQuadrupleDashed`.

### Color RGB conversions

```rust
let c = Color::from([255, 0, 0]); // from array
let c = Color::from((255, 0, 0)); // from tuple
```

`Style::has_modifier()` checks for a specific modifier.

See `references/styling-and-borders.md` for full details.

## Migration Quick Reference (0.30 Breaking Changes)

| Change | Migration |
|--------|-----------|
| `block::Title` removed | Use `Line` directly; `title_top()` / `title_bottom()` |
| `Alignment` renamed | Now `HorizontalAlignment` (alias exists). `VerticalAlignment` added |
| `Flex::SpaceAround` changed | Old behavior is now `Flex::SpaceEvenly` |
| `From` impls for backend types removed | Use `FromCrossterm`/`IntoCrossterm` (and Termion/Termwiz equivalents) |
| Backend `Error` type required | Custom backends: add `type Error`; implement `clear_region` |
| `WidgetRef` reversed | Implement `Widget for &Foo`; use `FrameExt` for `render_widget_ref()` |

See `references/migration-guide.md` for full migration details with code examples.

## Version Notes

- **0.30.1**: `AsRef<Self>` impls added for built-in widgets. May cause type inference ambiguity in rare cases -- add explicit type annotations if needed.
- **0.31**: MSRV bumped to 1.88.0.

## Reference Files

For detailed coverage of each topic area, consult:

- **`references/layout.md`** -- Rect arithmetic (`+`/`-` Offset, `outer`, `resize`), Flex changes, Size::area()
- **`references/widgets.md`** -- BarChart constructors, List highlight, canvas markers, LineGauge symbols, ScrollbarState, Tabs, Text AddAssign, AsRef impls
- **`references/styling-and-borders.md`** -- Border merging (MergeStrategy), all dashed border types, Color RGB conversions, Style::has_modifier
- **`references/migration-guide.md`** -- Complete migration details for all 0.30 breaking changes with before/after code
- **`references/backend-and-platform.md`** -- Multiple crossterm version support, no_std, ratatui-core for library authors
