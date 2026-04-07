# Components & Views

## `<ShowLet>` Component (0.8.8)

New component similar to `<Show>` but designed for `Option` values. It unwraps the `Option` and provides the inner value to children via `let:value`.

```rust
<ShowLet
    when=move || some_option.get()
    fallback=|| view! { <p>"Nothing here"</p> }
    let:value
>
    <p>"Got: " {value}</p>
</ShowLet>
```

**Props:**
- `when` — closure or signal returning `Option<T>`
- `fallback` — view to render when `None`
- `let:value` — binds the unwrapped `T` for use in children

## `<Show>` Accepts Signals Directly (0.8.8)

`<Show when=...>` now accepts signals in addition to closures, removing the need to wrap a signal in a closure:

```rust
let visible = RwSignal::new(true);

// Before (still works):
<Show when=move || visible.get()>
    <p>"Visible"</p>
</Show>

// Now also valid:
<Show when=visible>
    <p>"Visible"</p>
</Show>
```
