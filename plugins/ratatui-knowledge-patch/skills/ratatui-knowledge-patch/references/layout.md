# Layout (0.30)

## Rect Arithmetic

`Rect` supports offset-based movement and expansion helpers.

```rust
use ratatui::layout::Offset;

let moved_right = rect + Offset { x: 5, y: 0 };
let moved_left = rect - Offset { x: 5, y: 0 };

let expanded = rect.outer(Margin {
    horizontal: 2,
    vertical: 1,
}); // inverse of inner()
let resized = rect.resize(new_width, new_height); // resize from top-left corner
```

`Size::area()` returns the total area as `u32`.

```rust
let total_cells = size.area(); // -> u32
```

## Flex::SpaceEvenly and SpaceAround

Old `Flex::SpaceAround` behavior (equal spacing everywhere) is now `Flex::SpaceEvenly`.

New `Flex::SpaceAround` matches CSS flexbox: the space between adjacent items is twice the space at the edges.

```rust
// Equal spacing everywhere (old SpaceAround behavior):
Layout::horizontal([Constraint::Length(10); 3]).flex(Flex::SpaceEvenly)

// CSS-style space-around (2x inter-item vs edge spacing):
Layout::horizontal([Constraint::Length(10); 3]).flex(Flex::SpaceAround)
```

## Direction Helper

`Direction::perpendicular()` returns the perpendicular direction:

```rust
let perp = Direction::Horizontal.perpendicular(); // -> Direction::Vertical
```
