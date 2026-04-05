# Components & Views

Static typed views, new components, attribute spreading, and two-way binding.

## Static Typed Views (0.7+)

The `View` enum is gone. Views are now statically typed. This is the source of WASM binary size savings.

### Either for Branching

```rust
if condition {
    Either::Left(view! { <p>"A"</p> })
} else {
    Either::Right(view! { <span>"B"</span> })
}
```

The `either!` macro supports many branch arms (limit increased in 0.7.1). `either_or` / `either_of` combinators added in 0.7.5.

### .into_any() for Type Erasure

```rust
view! { <p>"Hello"</p> }.into_any()  // returns AnyView
```

**Required** for recursive components. `IntoFragment` implemented for `AnyView` (0.8.3).

## Two-Way Binding: bind: Syntax (0.7+)

Replaces manual `prop:value` + `on:input` pairs:

```rust
let checked = RwSignal::new(true);
let group = RwSignal::new("one".to_string());
let (text, set_text) = signal("Hello".to_string());

view! {
    <input type="checkbox" bind:checked=checked />
    <input type="radio" value="one" bind:group=group />
    <input type="radio" value="two" bind:group=group />
    <input type="text" bind:value=(text, set_text) />
    <textarea bind:value=(text, set_text) />
}
```

## Attribute Spreading (0.7+)

Any valid attribute can be spread onto any component using `{..}` separator:

```rust
<MyComponent
    some_prop=13           // component prop (before {..})
    {..}                   // separator: everything after is HTML attribute
    class:foo=true
    style:font-weight="bold"
    on:click=move |_| {}
    title="a title"
    attr:id="foo"          // explicit HTML attribute prefix
    {..spread_attrs}       // spread a variable
/>
```

### Option<_> in style: (0.8.0+)

```rust
<div style:color=move || if active() { Some("red") } else { None } />
// None removes the style, Some sets it
```

### AttributeInterceptor (0.7.1+)

New component for passing arbitrary HTML attributes through to child elements:

```rust
<AttributeInterceptor /* attributes forwarded to inner element */>
    <div>/* content */</div>
</AttributeInterceptor>
```

Works with `erase_components` as of 0.7.3.

## ShowLet Component (0.8.8+)

Like `<Show>` but for `Option<T>` values, binding the inner value:

```rust
<ShowLet when=move || optional_value() let:value>
    <p>{value}</p>
</ShowLet>
```

Accepts static `Option` values (not just signals/closures) as of 0.8.15.

### Show Accepts Signals (0.8.8+)

`<Show>` now accepts signals directly:

```rust
let visible = RwSignal::new(true);
// Previously: when=move || visible.get()
// Now:
<Show when=visible>
    <p>"Visible"</p>
</Show>
```

### transparent Attribute (0.8.16+)

`Show` and `ShowLet` have a `transparent` attribute to work around scoping issues.

## #[component] Macro Improvements

### Destructured Props with #[prop(name)] (0.7.3+)

```rust
#[component]
fn MyComponent(#[prop(name = "data")] UserInfo { email, user_id }: UserInfo) -> impl IntoView {
    // Caller passes data=some_user_info
    // Function body uses email, user_id directly
    view! { <p>{email}</p> }
}
```

### TypedChildrenFn Clone (0.7.1+)

`TypedChildrenFn` derives `Clone`.

### Lint Attributes (0.8.3+)

Lint attributes passed to `#[component]` are forwarded correctly.

## HTML Attribute Additions

| Version | Attributes |
|---|---|
| 0.7.2 | `popovertarget`, `popovertargetaction` on `<button>` |
| 0.8.8 | `command`, `commandfor` on `<button>`; `name` on `<details>` |
| 0.8.16 | `closedby` on `<dialog>` |
| 0.8.9 | `referrerpolicy` on `<a>` |

## IntoSplitSignal (0.8.0+)

`(Signal<T>, SignalSetter<T>)` implements `IntoSplitSignal`.

## SignalSetter and TextProp in Prelude (0.8.0+)

No longer need explicit imports.

### TextProp Improvements

- Supports conversion from signals (0.8.4+)
- Implements `IntoAttributeValue` (0.7.5+)

## Oco Type (0.8.8+)

`Oco` implements `IntoProperty`. `InnerHtmlValue` implemented for `Oco<'static, str>` (0.8.16).

## AttributeValue for Cow and MaybeProp

- `Cow<'_, str>` implements `IntoClass` (0.7.3+) and `AttributeValue` (0.8.3+)
- `MaybeProp` implements `AttributeValue` (0.8.16+)

## Debug Logging Macros (0.8.4+)

Conditional debug-only logging:

```rust
debug_log!("only in debug builds: {}", value);
debug_error!("debug-only error: {}", err);
```

Also available as `console_debug_log` and `console_debug_error`. Re-exported in `logging` module (0.8.11+).

## is_server() and is_browser() (0.8.8+)

Runtime check helpers made public API.

## SVG Support

Inert SVG elements (`svg::InertElement`) added in 0.8.3. SVG `use_` element trailing underscore stripped correctly in 0.8.16.
