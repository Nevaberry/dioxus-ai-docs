# Migration and configuration

Use this reference when upgrading dependencies, selecting crate features, or
repairing compilation and persisted-data issues.

Versioned coverage in this file includes batches `0.29.0`, `0.29-guide`,
`0.30.0`, and `0.30-guide`.

## Rust and dependency requirements

- Ratatui 0.30.0 was released with Rust 1.86.0 and the Rust 2024 edition. The
  current 0.31.0 workspace requires Rust 1.88.0.
- Applications can continue to use the `ratatui` facade. Reusable widget
  libraries can depend on the more stable `ratatui-core`; specialized crates
  include `ratatui-widgets`, `ratatui-crossterm`, `ratatui-termion`, and
  `ratatui-termwiz` (since 0.30.0).
- Choose a compatible Crossterm release with a feature such as
  `crossterm_0_28` or `crossterm_0_29`. The newest supported release is the
  default, and when multiple version features are enabled Ratatui selects the
  newest.
- Import the matched Crossterm through `ratatui::crossterm`, for example
  `use ratatui::crossterm::event;`, to avoid adding a second,
  semver-incompatible backend dependency.

## Feature selection

### `no_std` and the layout cache

Disable defaults for a `no_std` build:

```toml
ratatui = { version = "0.30.0", default-features = false }
```

Disabling defaults also disables the layout cache. A `std` application that
turns defaults off should add `features = ["layout-cache"]`.
`Layout::init_cache` and `Layout::DEFAULT_CACHE_SIZE` exist only with that
feature.

For a target without native atomics, enable `portable-atomic`:

```toml
ratatui = { version = "0.30.0", default-features = false, features = ["portable-atomic"] }
```

Leave it disabled on targets with native atomics. The `palette` and `serde`
features require `std` and cannot be used in a true `no_std` build.

### Other feature behavior

- `scrolling-regions` makes `Terminal::insert_before` use terminal scrolling
  regions, avoiding flicker when inserting before an inline viewport (since
  0.29.0).
- The previously unusable `unstable-backend-writer` feature is declared and
  can be enabled normally (since 0.29.0).
- The default `macros` feature exposes `span!`, `line!`, and `text!` from the
  separate `ratatui-macros` crate.
- The calendar widget is a default feature of `ratatui-widgets` (since 0.30.0).
  Disable defaults and select individual features when minimizing dependencies.
- `unstable-rendered-line-info` enables experimental
  `Paragraph::line_count` and `Paragraph::line_width`. The umbrella `unstable`
  feature enables these and every other unstable API.
- Reference rendering on `Frame` requires `unstable-widget-ref` and an import
  of `widgets::FrameExt`.
- `try_init`, `try_init_with_options`, `try_restore`, `run`, and
  `DefaultTerminal` require the `crossterm` feature.
- The default `underline-color` feature affects Crossterm and Termwiz only. It
  is unsupported on Windows 7, and Termion cannot emit underline colors.

## Breaking API migrations

### Block titles

In 0.29.0, `ratatui::widgets::block::Title` was deprecated in favor of `Line` or
directly convertible title content:

```rust
Block::new().title("top").title_bottom("bottom")
```

In 0.30.0, `widgets::block` and `widgets::block::Title` were removed and
`Block::title` accepts `Into<Line>`. Import the former public types as
`widgets::TitlePosition` and `widgets::BlockExt`.

### Alignment, styling, and symbols

- Rename `ratatui::layout::Alignment` to `HorizontalAlignment` (since 0.30.0).
  `VerticalAlignment` is a separate type.
- Stylize methods are inherent on `Style`, so style constants can call them.
  As a breaking trait change, `Style` no longer implements `Styled`.
- Reset is the exception to the inherent shorthand migration: replace
  `style.reset()` with `Style::reset()`.
- `symbols::Marker` is `#[non_exhaustive]`; external matches need a wildcard
  arm (since 0.30.0).
- `Marker::Block` now means a full block (`█`). Select `Marker::Bar` for the
  former upper-half-block (`▀`) canvas rendering.
- Symbol-set types carry lifetimes, so custom sets may borrow strings created
  at runtime rather than requiring all symbols to be `'static`.

### Backend integrations

- Generic conversions to and from backend types were replaced by explicit
  `FromCrossterm`/`IntoCrossterm`, `FromTermion`/`IntoTermion`, and
  `FromTermwiz`/`IntoTermwiz` traits. Use, for example,
  `Color::from_crossterm(value)` or `color.into_crossterm()`.
- A custom `Backend` must define an associated `Error` and implement
  `clear_region`. Generic functions should return `Result<_, B::Error>`, not
  assume `std::io::Error`. `TestBackend::Error` is
  `core::convert::Infallible`.

### Reference widgets

`WidgetRef` no longer supplies implementors with a blanket `Widget`
implementation. Ratatui instead implements `WidgetRef` for `&W` when
`W: Widget`. Migrate:

```rust
// old: impl WidgetRef for Foo { ... }
impl Widget for &Foo {
    fn render(self, area: Rect, buf: &mut Buffer) { /* ... */ }
}
```

The `State` associated types of `StatefulWidget` and `StatefulWidgetRef` are
now `?Sized`, allowing slice, `dyn Any`, and other dynamically sized state.

### Inference and public-field changes

- `Tabs::select` accepts `Into<Option<usize>>`, including `None`. If
  `select(selected.into())` becomes ambiguous, pass `selected as usize` or an
  explicitly typed `Option<usize>`.
- `Line: From<Cow<str>>` preserves borrowed-or-owned string input, but the new
  conversion can make inference ambiguous. Use an explicit target such as
  `Line::from(String::from(value))`.
- `Bar::label` and `Bar::text_value` accept `Into`; remove `.into()` from
  string literals when inference is ambiguous.
- `List::highlight_symbol` accepts `Into<Line>`. Explicit-conversion call
  sites may need adjustment, and the method is no longer callable in a const
  context.
- `Cell::symbol` is `Option<CompactString>` and defaults to `None`. Direct
  field access must handle the option. Equality and hashing treat `None` like
  an empty string; merging into an empty cell installs the incoming symbol.
- `Rect::area()` returns `u32`, not `u16`. `Rect::new` clamps width and height
  independently instead of clamping total area to `u16::MAX` while preserving
  aspect ratio.
- `Rect`'s `Positions` iterator no longer exposes `rect` or
  `current_position`; use the iterator interface.

### Snapshot-sensitive behavior

- `Span`, `Line`, `Text`, and `Style` now have concise, builder-like `Debug`
  output that omits default fields. Update snapshots of their debug strings
  (since 0.29.0).
- Canvas coordinate mapping rounds to the nearest grid cell instead of toward
  zero, and default `LineGauge` percentage labels are padded to three cells.
  Both can change rendering snapshots (since 0.30.0).

## Serialization

Many layout, style, and widget configuration types derive `Serialize` and
`Deserialize`, including `Constraint`, `Layout`, `Spacing`, `Padding`,
`Borders`, `BorderType`, palette types, alignments, and list/scrollbar
direction types.

When deserializing `Style`, `add_modifier` and `sub_modifier` may be absent or
`null`; either case means no modifiers. Themes need not include placeholder
modifier fields.

The bitflags 2.3 migration changed the serialized representation of `Borders`
and `Modifier`. Persisted values written before Ratatui 0.22 must be
re-serialized before current code reads them.

## Prelude boundaries

The prelude includes `Position` and `Size`. It does not include `Styled`,
`Marker`, `CompletedFrame`, `TerminalOptions`, or `Viewport`. Import the
terminal types from the crate root and `Styled` or `Marker` from their defining
modules.
