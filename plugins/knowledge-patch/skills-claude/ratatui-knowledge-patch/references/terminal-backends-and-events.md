# Terminal, backends, and events

Use this reference for terminal lifecycle, viewport behavior, fallible drawing,
custom backends, and asynchronous input scheduling.

## Managed lifecycle

`ratatui::run` initializes a default terminal, passes it to a closure, restores
the terminal afterward, and returns the closure's result (since 0.30.0):

```rust
fn main() -> Result<(), Box<dyn std::error::Error>> {
    ratatui::run(|terminal| {
        terminal.draw(|frame| frame.render_widget("Hello", frame.area()))?;
        Ok(())
    })
}
```

For explicit control, `ratatui::init()` enters raw mode and the alternate
screen, installs a restoring panic hook, and returns `DefaultTerminal`, an
alias for `Terminal<CrosstermBackend<Stdout>>`. Preserve the application
result, restore, and then return the result:

```rust
fn main() -> color_eyre::Result<()> {
    color_eyre::install()?;
    let terminal = ratatui::init();
    let result = run(terminal);
    ratatui::restore();
    result
}
```

`restore()` returns `()` and reports restoration errors to stderr. Use
`try_init`, `try_init_with_options`, and `try_restore` to propagate lifecycle
errors. These helpers, `run`, and `DefaultTerminal` require `crossterm`.

## Viewports and resizing

`Terminal::new` creates a fullscreen viewport. `Terminal::with_options` can
create a fixed viewport:

```rust
let viewport = Viewport::Fixed(Rect::new(0, 0, 80, 24));
let mut terminal = Terminal::with_options(backend, TerminalOptions { viewport })?;
```

`draw` automatically tracks backend size changes for fullscreen and inline
viewports. It leaves a fixed viewport at its configured `Rect`. An explicit
`Terminal::resize` does resize a fixed viewport; the former no-op behavior was
fixed in 0.29.0, so remove workarounds based on it doing nothing.

`Terminal::clear` uses the latest post-resize area, rather than a cached stale
area, and clears the whole resized region (since 0.29.0).

For inline insertion, enabling `scrolling-regions` lets
`Terminal::insert_before` use terminal scrolling regions and avoid viewport
flicker.

## Drawing and manual presentation

### Fallible callbacks

Use `Terminal::try_draw` when rendering itself can fail. Its callback returns
`Result<(), E>` where `E: Into<B::Error>`. An error prevents the terminal
update; success follows the normal draw lifecycle and returns `CompletedFrame`:

```rust
terminal.try_draw(|frame| {
    let value: u8 = "42".parse().map_err(std::io::Error::other)?;
    frame.render_widget(Paragraph::new(value.to_string()), frame.area());
    std::io::Result::Ok(())
})?;
```

### Frames outside `draw`

`Terminal::get_frame` exposes a frame for tests, buffer inspection, and custom
multi-pass rendering. It bypasses `draw`, so present the frame manually in
this order: flush the buffer diff, swap buffers, then flush the backend.
`current_buffer_mut` permits direct buffer mutation.

```rust
{
    let mut frame = terminal.get_frame();
    frame.render_widget(Paragraph::new("Hello"), frame.area());
}
terminal.flush()?;
terminal.swap_buffers();
terminal.backend_mut().flush()?;
```

## Cursor and backend size

`Terminal::get_cursor` and `set_cursor(x, y)` are deprecated. Use typed
positions:

```rust
let position = terminal.get_cursor_position()?;
terminal.set_cursor_position((position.x, position.y))?;
let backend_size: Size = terminal.size()?;
```

`Terminal::size()` queries the real backend and returns `Size`; it is distinct
from the viewport's `Rect`.

## Backend API and conversions

A custom `Backend` must provide an associated `Error` and implement
`clear_region`. Write generic results as `Result<T, B::Error>` instead of
hard-coding `std::io::Error`. `TestBackend` uses `Infallible`.

Backend conversions use explicit traits:

- `FromCrossterm` and `IntoCrossterm`
- `FromTermion` and `IntoTermion`
- `FromTermwiz` and `IntoTermwiz`

For example, call `Color::from_crossterm(value)` or
`color.into_crossterm()`. Ratatui re-exports the selected compatible version
as `ratatui::crossterm`.

With Crossterm, removing `DIM` preserves `BOLD`: the backend resets terminal
intensity and reapplies the modifier that should remain. Underline color works
with Crossterm and Termwiz, not Termion, and is unavailable on Windows 7.

## Asynchronous event scheduling

The component template runs `crossterm::EventStream` in a Tokio task and uses
`tokio::select!` to multiplex cancellation, application ticks, render
deadlines, and terminal input. Tick and render rates are independent (the
template defaults to 4 and 60 per second), and an `Init` event is emitted at
startup.

Only `KeyEventKind::Press` is converted into a key event. Focus, paste, mouse,
and resize events go through the same unbounded MPSC channel consumed by
`next_event().await`:

```rust
let event = tokio::select! {
    _ = cancellation_token.cancelled() => break,
    _ = tick_interval.tick() => Event::Tick,
    _ = render_interval.tick() => Event::Render,
    event = event_stream.next().fuse() => match event {
        Some(Ok(CrosstermEvent::Key(key))) if key.kind == KeyEventKind::Press => Event::Key(key),
        Some(Ok(_)) => continue,
        Some(Err(_)) => Event::Error,
        None => break,
    },
};
if event_tx.send(event).is_err() { break; }
```

In that template, `Tui::enter` configures the terminal and then starts the
event task. `Tui::exit` cancels and stops it before symmetrically disabling
optional bracketed-paste and mouse capture and restoring the terminal. `Drop`
calls `exit`. On non-Windows systems, `suspend` exits before raising
`SIGTSTP`, and `resume` enters again.
