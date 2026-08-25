# Ecosystem SDK and Styled Components

Use this reference for first-party primitives, copied styled components,
virtual lists, dynamic attribute lists, SDK feature crates, platform support,
persistence, timers, and internationalization.

## Primitives and copied components

Dioxus Primitives introduced 28 unstyled, Radix-style foundations in 0.7.0.
They provide keyboard and ARIA behavior across Web, Desktop, and Mobile and are
intended to be restyled and composed.

The component registry supplies shadcn-style precomposed variants.
`dx components add <name>` copies source into the application's local
`components` directory. On the first addition, the CLI offers to add a
root-level link to `/assets/dx-components.css`, which provides the default
theme.

```sh
dx components add button
```

Because source is copied rather than hidden behind a binary abstraction, edit
it locally as application code and review updates before replacing
customizations.

## Composite indices

Ordered and roving-focus composites commonly require explicit zero-based
`index` props rather than inferring order from RSX. This includes accordion
items, menus, navigation entries, radio/select options, tab triggers and
content, toggles, and toolbar buttons. Matching tab triggers and panels share a
`value`.

```rust
Tabs {
    TabList {
        TabTrigger { index: 0, value: "account", "Account" }
    }
    TabContent { index: 0, value: "account", "Settings" }
}
```

If a list is filtered or sorted, recompute indices in rendered order.

## Combobox filtering

`Combobox<T>` can be controlled with `value` and `query`. Built-in filtering
preserves the rendered `ComboboxOption` order; for query-dependent ranking,
sort the input first and assign fresh indices after sorting.

```rust
let mut value = use_signal(|| None::<String>);
let mut query = use_signal(String::new);

Combobox::<String> {
    value: Some(value.into()),
    on_value_change: move |next| value.set(next),
    query: Some(query()),
    on_query_change: move |next| query.set(next),
    ComboboxOption::<String> {
        index: 0,
        value: "rust".to_string(),
        text_value: "Rust",
        "Rust"
    }
}
```

## Calendar and date pickers

`Calendar` and `RangeCalendar` render full month views. `DatePicker` and
`DateRangePicker` precompose editable input, trigger, popover, and calendar.
`month_count` adds adjacent months. Date pickers can override day, month, and
year placeholder formatters.

```rust
DatePicker {
    selected_date: selected_date(),
    on_value_change: move |date: Option<Date>| selected_date.set(date),
    month_count: 2,
    on_format_day_placeholder: || "D",
    on_format_month_placeholder: || "M",
    on_format_year_placeholder: || "Y",
}
```

## Attribute-preserving custom rendering

`SheetClose` and several sidebar controls accept an `as` closure analogous to
an `asChild` API. Spread the received attributes so merged state data and event
handlers are not lost.

```rust
SheetClose {
    as: |attributes| rsx! {
        a { href: "#", ..attributes, "Go back" }
    }
}
```

The separate `dioxus-attributes` crate provides `attributes!` to create a
`Vec<Attribute>` with element-like syntax, including listeners and custom data
attributes.

```rust
let attrs = attributes!(div {
    class: "card",
    "data-state": "open",
    onclick: |_| println!("clicked"),
});
rsx! { div { ..attrs } }
```

## Sidebar behavior

`SidebarProvider` owns open, side, and collapse state and registers Cmd/Ctrl+B
as its toggle. `SidebarCollapsible` supports `Offcanvas`, `Icon`, and `None`.
`SidebarRail` is an optional resize handle. `SidebarMenuButton` wraps itself in
a tooltip only when its `tooltip: Option<Element>` is `Some`.

## Toasts

Place `ToastProvider` above consumers, retrieve the controller with
`consume_toast()`, and send through severity methods with `ToastOptions`.
Rendered toasts can receive keyboard focus with F6.

```rust
consume_toast().error(
    "Critical error".to_string(),
    ToastOptions::new()
        .description("More information")
        .duration(Duration::from_secs(10))
        .permanent(false),
);
```

## Virtual lists

`VirtualList` renders visible rows plus a configurable approximate-row buffer
and supports dynamic heights. Its renderer receives the absolute item index,
so rows need stable keys.

```rust
VirtualList {
    count: rows.len(),
    buffer: 8,
    render_item: move |idx| rsx! {
        article { key: "{idx}", "{rows[idx].title}" }
    },
}
```

## SDK feature aggregation

`dioxus-sdk` re-exports separate geolocation, storage, time, window,
notification, sync, and utility crates through same-named feature flags;
`notification` is singular. SDK minor versions track Dioxus minor versions.

```toml
[dependencies]
dioxus-sdk = { version = "0.7", features = ["geolocation", "storage", "time"] }
```

Most SDK calls return `Err(Unsupported)` at runtime on an unsupported target.
Do not infer availability merely because a crate compiles.

The documented community helper for localization is `dioxus-i18n`, which
provides Dioxus-oriented translation utilities.

## Geolocation and notifications

Geolocation currently supports Web and Windows. Initialize it with a
`PowerMode`, then handle `use_geolocation()` as a result that can initially be
`Error::NotInitialized`.

```rust
let _geolocator = init_geolocator(PowerMode::High).unwrap();
match use_geolocation() {
    Ok(coords) => rsx! { "{coords.latitude}, {coords.longitude}" },
    Err(Error::NotInitialized) => rsx! { "Initializing..." },
    Err(error) => rsx! { "{error}" },
}
```

Notifications support Windows, macOS, and Linux. Use the builder to set the
application name, summary, and body before `show()`.

```rust
Notification::new()
    .app_name("Example".to_string())
    .summary("Finished".to_string())
    .body("The operation completed".to_string())
    .show()
    .unwrap();
```

## Persistence and timers

`dioxus-sdk-storage::use_persistent(key, init)` exposes local persistent data
through the normal readable/writable signal interface.

The time package supplies `use_interval`, `use_timeout`, and `sleep`.
`use_debounce` returns a handle whose `action(value)` restarts the delay and
passes the final value into the callback.

```rust
let mut count = use_persistent("count", || 0);
*count.write() += 1;

let mut save = use_debounce(
    Duration::from_millis(500),
    |text| println!("{text}"),
);
save.action("draft");
```
