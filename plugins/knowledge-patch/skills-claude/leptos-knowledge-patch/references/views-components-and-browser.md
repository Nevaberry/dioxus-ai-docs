# Views, Components, and Browser APIs

## Return statically typed views

The general `View` enum was replaced by statically typed views in 0.7.0. When
branches produce different concrete view types, use an `Either` enum for a
small number of branches or call `.into_any()` on every branch to produce
`AnyView`.

```rust
if ready {
    Either::Left(view! { <p>"Ready"</p> })
} else {
    Either::Right("Waiting")
}
```

## Erase recursive component output

A recursive component must box or erase its return value so the compiler can
calculate the size of its view tree (since 0.7.0). Ending the recursively used
component with `.into_any()` is sufficient.

## Do not rely on cloneable views

Statically typed views and `AnyView` are not necessarily `Clone` (since
0.7.0). Storing a view in a signal and reading it repeatedly is therefore not
reliable. If that pattern is required, send each view once through a channel
and pair the receiver with an `ArcTrigger` that invalidates the rendering
closure.

## Implement current rendering conversions

For a custom type that previously implemented `IntoView`, implement
`IntoRender` instead (since 0.7.0). For a custom attribute value that used
`IntoAttribute`, implement `IntoAttributeValue`. `IntoRender` is also the
extension point for rendering otherwise arbitrary data types.

## Spread attributes through components

DOM attributes and `class:`, `style:`, `prop:`, and `on:` directives can pass
through a component and apply to every element in its returned view (since
0.7.0). Prefix one explicit plain attribute with `attr:`, or place `{..}`
between component props and the later attributes.

```rust
view! {
    <Card some_prop=13 attr:id="card" {..} title="Details" class:active=true/>
}
```

Old dedicated pass-through props, such as an anchor component's `class` prop,
were removed in favor of this general mechanism.

## Bind form controls in both directions

The `bind:` directive connects a form control to an `RwSignal` or split
`(read, write)` pair (since 0.7.0):

- Use `bind:checked` for a boolean checkbox.
- Use `bind:group` for a string-valued radio group.
- Use `bind:value` for a text input or textarea.

```rust
view! {
    <input type="checkbox" bind:checked=is_checked/>
    <input type="radio" value="one" bind:group=choice/>
    <input type="text" bind:value=(text, set_text)/>
}
```

## Await futures and render optional values

The `Await` component's `future` prop takes a `Future` directly rather than a
`Fn() -> Future` (since 0.7.0).

`<ShowLet>` renders an `Option` and accepts reactive or static `Option` values
(since 0.8.0). `<Show>` accepts a signal directly as well as a closure.

## Use added platform attributes and events

The view macro accepts `Option<_>` in `style:` directives (since 0.8.0):

```rust
view! { <div style:display=move || visible.get().then_some("block")/> }
```

It also recognizes the `scrollend` event, button `command` and `commandfor`,
`<details name>`, anchor `referrerpolicy`, and dialog `closedby`.
