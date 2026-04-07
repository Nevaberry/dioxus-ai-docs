# Migration Guide (0.29 to 0.30)

## `Alignment` Renamed to `HorizontalAlignment`

`Alignment` is renamed to `HorizontalAlignment`. A type alias `Alignment` still exists for backwards compatibility. `VerticalAlignment` is also added as a new type.

## `FromCrossterm` / `IntoCrossterm` Replace `From` Impls

Direct `From` trait conversions between ratatui types and backend types are removed. Use the explicit conversion traits instead.

```rust
use ratatui::backend::crossterm::{FromCrossterm, IntoCrossterm};

let color = Color::from_crossterm(crossterm::style::Color::Black);
let ct: crossterm::style::Color = color.into_crossterm();
```

Equivalent traits exist for other backends:
- Termion: `FromTermion` / `IntoTermion`
- Termwiz: `FromTermwiz` / `IntoTermwiz`

## Backend Associated `Error` Type

Custom backends must now define an associated `type Error` and implement the `clear_region` method. Generic code should use `B::Error`:

```rust
fn run<B: Backend>(terminal: Terminal<B>) -> Result<(), B::Error> {
    // ...
}

// Or use the concrete DefaultTerminal to avoid generics:
fn run(terminal: DefaultTerminal) -> io::Result<()> {
    // ...
}
```

## `WidgetRef` Trait Reversed

Instead of implementing `WidgetRef for Foo`, implement `Widget for &Foo`:

```rust
// Old:
// impl WidgetRef for MyWidget { fn render_ref(&self, area: Rect, buf: &mut Buffer) { ... } }

// New:
impl Widget for &MyWidget {
    fn render(self, area: Rect, buf: &mut Buffer) {
        // ...
    }
}
```

To use `render_widget_ref()` on `Frame`, import the `FrameExt` trait from `ratatui::widgets` and enable the `unstable-widget-ref` feature flag.
