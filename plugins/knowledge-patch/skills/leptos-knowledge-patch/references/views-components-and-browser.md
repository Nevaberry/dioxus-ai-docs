# Views, Components, and Browser APIs

## Statically typed views

The general `View` enum is replaced by statically typed views (since 0.7.0).
When control-flow branches produce different view types, prefer an `Either`
variant for explicit alternatives:

```rust
if ready {
    Either::Left(view! { <p>"Ready"</p> })
} else {
    Either::Right("Waiting")
}
```

For broader type erasure, call `.into_any()` on every branch to return
`AnyView`. Recursive components must box or erase their result so the compiler
can calculate the view tree's size; ending the recursively used component in
`.into_any()` is sufficient.

Typed views and `AnyView` are not necessarily `Clone`. Do not store views in
signals and repeatedly read them. If a design must deliver dynamically built
views, send each view once through a channel and pair the receiver with an
`ArcTrigger` that invalidates the rendering closure.

## Custom rendering conversions

For custom data types, replace former `IntoView` implementations with
`IntoRender` and former `IntoAttribute` implementations with
`IntoAttributeValue` (since 0.7.0). `IntoRender` is also the extension point
for making otherwise arbitrary data renderable.

## Component attribute spreading

DOM attributes and `class:`, `style:`, `prop:`, and `on:` directives can pass
through a component and apply to every element in its returned view. Prefix a
single plain attribute with `attr:`, or put `{..}` between the component's
props and the attributes that follow:

```rust
view! {
    <Card some_prop=13 attr:id="card" {..} title="Details" class:active=true/>
}
```

Use this mechanism instead of dedicated pass-through props such as an anchor
component's former `class` prop.

## Two-way input binding

The `bind:` directive connects form controls to an `RwSignal` or to a split
`(read, write)` signal pair (since 0.7.0):

```rust
view! {
    <input type="checkbox" bind:checked=is_checked/>
    <input type="radio" value="one" bind:group=choice/>
    <input type="text" bind:value=(text, set_text)/>
}
```

Use `bind:checked` for boolean checkboxes, `bind:group` for string-valued radio
groups, and `bind:value` for text inputs and textareas.

## Await, Show, and optional values

The `Await` component's `future` prop receives a `Future` directly rather than
a `Fn() -> Future` (since 0.7.0).

`<ShowLet>` is the `Option` counterpart to `<Show>` (since 0.8.0) and accepts
both reactive and static `Option` values. `<Show>` accepts a signal directly
as well as a closure.

## View macro platform support

The view macro accepts `Option<_>` values in `style:` directives:

```rust
view! {
    <div style:display=move || visible.get().then_some("block")/>
}
```

It also recognizes the `scrollend` event, button `command` and `commandfor`,
`name` on `details`, `referrerpolicy` on anchors, and `closedby` on dialogs
(since 0.8.0).
