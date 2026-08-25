# Architecture, state, and testing

Use this reference when structuring an application, managing render-time
state, starting from a template, or testing custom widgets.

## Component architecture

Ratatui's documented component contract is an application template pattern,
not a trait provided by the library. A component owns local state and defines
initialization, event-to-action mapping, action updates, and rendering. The
template maps quit, tick, and resize directly and delegates keyboard and mouse
events:

```rust
trait Component {
    fn init(&mut self) -> Result<()> { Ok(()) }
    fn handle_events(&mut self, event: Option<Event>) -> Action { /* map or delegate */ }
    fn handle_key_events(&mut self, key: KeyEvent) -> Action { Action::Noop }
    fn handle_mouse_events(&mut self, mouse: MouseEvent) -> Action { Action::Noop }
    fn update(&mut self, action: Action) -> Action { Action::Noop }
    fn render(&mut self, frame: &mut Frame, area: Rect);
}
```

The event task independently schedules ticks and renders and passes terminal
events through a channel. Coordinate its startup, cancellation, suspend, and
resume behavior with terminal entry and restoration; see
`terminal-backends-and-events.md`.

## Cascading update loops

The TEA guide permits a pragmatic Rust variant in which `update` mutates the
model and returns an optional follow-up message. Drain generated messages
before reading another external event. This makes transitions such as an
out-of-range counter producing a `Reset` explicit:

```rust
let mut next = handle_event(&model)?;
while let Some(message) = next {
    next = update(&mut model, message);
}
```

## Persistent render state

The whole UI is redrawn every frame, but a `StatefulWidget` borrows a separate
state object that persists across frames. `Frame::render_stateful_widget`
therefore takes mutable state. Widgets such as `List` can update the stored
`ListState` offset while rendering so the selection stays in view; the view
may consequently need `&mut Model`.

Keep the state of nested stateful widgets inside their parent's state:

```rust
fn view(model: &mut Model, frame: &mut Frame) {
    let items = model.items.iter().map(ListItem::new);
    frame.render_stateful_widget(
        List::new(items),
        frame.area(),
        &mut model.list_state,
    );
}
```

State associated types on `StatefulWidget` and `StatefulWidgetRef` may be
unsized (`?Sized`), enabling slices, `dyn Any`, and other dynamically sized
state values.

## In-place widget mutation

When a separate state type would be excessive, implement `Widget` for
`&mut MyWidget` and render a mutable reference. The widget can then mutate
itself during rendering. `RefCell` is another option when an immutable
reference constraint prevents passing `&mut`.

## Construction helpers and templates

The default `macros` feature supplies `span!`, `line!`, and `text!` through
`ratatui-macros`.

The official `cargo-generate` templates include a Hello World application
with initialization, draw/event loop, and restoration wiring:

```shell
cargo install --locked cargo-generate
cargo generate ratatui/templates
```

## Snapshot testing

Render a frame into a fixed-size `TestBackend` and snapshot the backend with
`insta`. Add `insta` as a development dependency, and inspect intentional
changes with `cargo insta review`.

```rust
use insta::assert_snapshot;
use ratatui::{backend::TestBackend, Terminal};

#[test]
fn render_snapshot() {
    let mut terminal = Terminal::new(TestBackend::new(20, 3)).unwrap();
    terminal
        .draw(|frame| frame.render_widget("Hello", frame.area()))
        .unwrap();
    assert_snapshot!(terminal.backend());
}
```

Remember that concise `Debug` output for text/style types, nearest-cell canvas
rounding, padded default line-gauge labels, and alignment-aware truncation can
change snapshots even when application logic is unchanged.

## Safe custom-widget drawing

Direct buffer writes can panic for coordinates outside the buffer. Intersect
the widget's supplied area with `buf.area` before drawing. Prefer
`area.rows()` or `area.columns()` over manual coordinate increments:

```rust
use ratatui::{buffer::Buffer, layout::Rect, style::Style, widgets::Widget};

struct MyWidget;

impl Widget for MyWidget {
    fn render(self, area: Rect, buf: &mut Buffer) {
        let area = area.intersection(buf.area);
        buf.set_style(area, Style::default());
    }
}
```
