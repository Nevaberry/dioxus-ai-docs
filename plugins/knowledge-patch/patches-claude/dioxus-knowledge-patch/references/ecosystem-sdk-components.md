# Ecosystem SDK and Styled Components

## SDK crate layout

`dioxus-sdk` is a facade over capability crates, not a module namespace. The
individual packages are `dioxus-sdk-storage`, `dioxus-sdk-geolocation`,
`dioxus-sdk-time`, `dioxus-sdk-window`, `dioxus-sdk-notification`,
`dioxus-sdk-sync`, and `dioxus-sdk-util`. Depend on one directly or enable its
suffix as a facade feature:

```toml
dioxus-sdk = { version = "0.7", features = ["storage", "time"] }
```

Imports still use the capability crate, such as
`dioxus_sdk_time::use_interval`, never `dioxus_sdk::time::...`. SDK minor
versions track Dioxus minor versions.

Platform gaps generally appear as runtime `Err(Unsupported)` rather than compile
errors. Geolocation supports web and Windows; notifications are desktop-only.
Test the target behavior rather than treating a successful build as proof of
support.

## Persistence, time, and device services

`use_persistent(key, || default)` returns a signal backed by browser local
storage or the platform data directory. Read and write it like any other signal.

Timing services include `use_interval`, `use_timeout`, `sleep`, and
`use_debounce`. Debounce returns a handle; fire it with `.action(arg)` instead of
wrapping an existing callback:

```rust
let mut debounce = use_debounce(Duration::from_millis(2000), move |text| {
    tracing::info!(%text, "settled");
});

button { onclick: move |_| debounce.action("clicked"), "Run" }
```

Geolocation has two phases: call `init_geolocator(PowerMode)` in an ancestor,
then `use_geolocation()` below it. The hook yields
`Err(Error::NotInitialized)` until the first fix.

Desktop notifications use a builder rather than a hook:

```rust
Notification::new()
    .app_name("Example")
    .summary("Complete")
    .body("The task finished")
    .show();
```

Other facilities include window theme/size, sync channels, and
`dioxus-sdk-util::use_root_scroll`.

Internationalization is not maintained in-tree; use the community
`dioxus-i18n` crate from the `dioxus-community` organization.

## Primitive and styled-component distribution

The first-party `dioxus-primitives` crate supplies an unstyled accessible layer
with 28 Radix-like components and keyboard/ARIA behavior across web, desktop,
and mobile. The
styled shadcn-like layer is not a dependency crate. Instead:

```sh
dx components add <name>
```

copies Rust and CSS source into the project's `components/` directory. The
first add prompts for `/assets/dx-components.css`, which carries the theme. You
own the copied source; upgrades are explicit re-adds rather than Cargo version
bumps.

Styled plain controls are HTML elements, not capitalized components—there is no
`Button` primitive. Apply `dx-*` classes and use `data-*` attributes for variants:

```rust
button {
    class: "dx-button",
    "data-style": "outline",
    "data-size": "default",
    "Save"
}
```

## Ordered children and generic props

Components with roving focus do not infer order from the DOM. Pass a unique,
zero-based `index` to each ordered child; it controls display and keyboard focus
order. This applies to:

- `AccordionItem`;
- `TabTrigger` and `TabContent`;
- `RadioItem`, `ToggleItem`, and `ToolbarButton`;
- `SelectOption` and `ComboboxOption`;
- `Tag`, `MenubarMenu`, and dropdown/context-menu item families.

Duplicate or stale indexes misorder the list rather than failing to compile.
Combobox filtering preserves index order; for relevance ranking, sort the data
and reassign indexes before rendering.

Orientation uses `horizontal: bool` on `Separator`, `ToggleGroup`, and
`ToolbarSeparator`, not an orientation enum. Generic components require a
turbofish in RSX, for example `Select::<String> {}` and
`ComboboxOption::<String> {}`.

## Rendering a primitive as another element

The `as` prop is the `asChild` equivalent. It is a closure that receives merged
attributes, including built-in handlers, and returns the node that should carry
them:

```rust
SheetClose {
    as: |attributes| rsx! {
        a { href: "#", ..attributes, "Go back" }
    }
}
```

Spread every received attribute or close/toggle/focus behavior silently
disappears. This convention appears on `SheetClose` and the `Sidebar*` family,
including trigger, menu button/action, group label/action, and submenu button.

## Dynamic attribute vectors

`dioxus-attributes::attributes!` builds the `Vec<Attribute>` consumed by RSX
spread syntax:

```rust
let attrs = attributes!(div {
    class: "card",
    "data-state": "open",
    onclick: |_| tracing::info!("clicked"),
});

rsx! { div { ..attrs } }
```

This complements forwarding attributes received through props by allowing a
component to construct them dynamically.

## Toasts and extended widgets

Toasts are consumed from a `ToastProvider` inside a handler, not obtained from a
hook. `consume_toast()` returns the API; methods such as `.error(title,
ToastOptions::new().description(...).duration(...).permanent(...))` enqueue a
toast. The `F6` key moves focus to the toast region.

Beyond the Radix-like set, the component library includes:

- `VirtualList` with `count`, `buffer`, and `render_item: |index|`;
- `DragAndDropList`;
- `ColorPicker`;
- `DatePicker`, `DateRangePicker`, `Calendar`, and `RangeCalendar`;
- `TagGroup`, `Sidebar`, `Navbar`, `Pagination`, and `Skeleton`;
- `Item` and `ItemGroup` families.

`ColorPicker::on_color_change` returns the `palette` crate's
`Hsv<encoding::Srgb, f64>` directly. `SidebarProvider` installs Cmd/Ctrl+B as a
toggle shortcut.

## Accessibility checks

- Keep each ordered child's `index` synchronized with visual order.
- Preserve merged attributes in every `as` closure.
- Test keyboard navigation after filtering or reordering.
- Treat runtime `Unsupported` from SDK services as a normal platform branch.
- Verify copied styled-component source and theme CSS are upgraded together.
