# Styling & Borders (0.30)

## Border Merging

Overlapping borders automatically merge into clean intersections via `MergeStrategy`. When two bordered widgets share an edge, the intersection characters are resolved automatically instead of overwriting each other.

## Dashed Border Types

Six new dashed border variants:

| BorderType | Description |
|------------|-------------|
| `LightDoubleDashed` | Light double-dashed lines |
| `HeavyDoubleDashed` | Heavy double-dashed lines |
| `LightTripleDashed` | Light triple-dashed lines |
| `HeavyTripleDashed` | Heavy triple-dashed lines |
| `LightQuadrupleDashed` | Light quadruple-dashed lines |
| `HeavyQuadrupleDashed` | Heavy quadruple-dashed lines |

## Color RGB Conversions

`Color` supports construction from arrays and tuples:

```rust
let c = Color::from([255, 0, 0]); // from [u8; 3]
let c = Color::from((255, 0, 0)); // from (u8, u8, u8)
```

## Style::has_modifier

Check whether a `Style` has a specific modifier set:

```rust
let style = Style::new().bold().italic();
assert!(style.has_modifier(Modifier::BOLD));
assert!(!style.has_modifier(Modifier::UNDERLINED));
```
