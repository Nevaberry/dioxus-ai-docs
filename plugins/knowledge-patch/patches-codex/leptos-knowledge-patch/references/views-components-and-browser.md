# Views, Components, and Browser APIs

## Statically typed views

The general `View` enum was replaced by statically typed views in 0.7.0. Keep
one concrete return type, use `Either` for a small set of branch types, or call
`.into_any()` on every branch to erase them consistently.

```rust
if ready {
    Either::Left(view! { <p>"Ready"</p> })
} else {
    Either::Right("Waiting")
}
```

Statically typed views and `AnyView` are not necessarily `Clone`. Do not store
views in signals and assume they can be read repeatedly. If that pattern is
necessary, send each view once through a channel and pair the receiver with an
`ArcTrigger` that invalidates the rendering closure.

Recursive components must box or erase their result so the compiler can
determine the view tree's size. Ending the recursively used component with
`.into_any()` is sufficient.

## Custom rendering conversions

Custom types that implemented `IntoView` should implement `IntoRender` after
the 0.7.0 migration. Types that implemented `IntoAttribute` should implement
`IntoAttributeValue`. `IntoRender` is also the extension point for rendering
otherwise arbitrary data types.

## Component attribute spreading

Spread DOM attributes and `class:`, `style:`, `prop:`, and `on:` directives
through a component to apply them to every element in the returned view (since
0.7.0). Prefix one explicit plain attribute with `attr:`, or put `{..}`
between component props and the later attributes.

```rust
view! {
    <Card some_prop=13 attr:id="card" {..} title="Details" class:active=true/>
}
```

Use spreading instead of old dedicated pass-through props such as an anchor
component's former `class` prop.

## Two-way input binding

The `bind:` directive accepts an `RwSignal` or a split `(read, write)` pair
(since 0.7.0):

- `bind:checked` binds boolean checkboxes.
- `bind:group` binds string-valued radio groups.
- `bind:value` binds text inputs and textareas.

```rust
view! {
    <input type="checkbox" bind:checked=is_checked/>
    <input type="radio" value="one" bind:group=choice/>
    <input type="text" bind:value=(text, set_text)/>
}
```

## Await, Show, and ShowLet

The `Await` component's `future` prop takes a `Future` directly, not a
`Fn() -> Future` (since 0.7.0).

Use `<ShowLet>` to render reactive or static `Option` values (since 0.8.0).
It is the optional-value counterpart to `<Show>`. `<Show>` accepts a signal
directly as well as a closure.

## View-macro platform support

The view macro added these platform capabilities in 0.8.0:

- `Option<_>` values in `style:` directives
- the `scrollend` event
- button `command` and `commandfor`
- `<details name>`
- anchor `referrerpolicy`
- dialog `closedby`

```rust
view! { <div style:display=move || visible.get().then_some("block")/> }
```
