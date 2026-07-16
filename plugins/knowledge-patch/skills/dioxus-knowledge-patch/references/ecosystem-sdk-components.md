# Ecosystem SDK and Styled Components

## Component registry and source ownership

Dioxus Primitives provides unstyled, accessible foundational components; the styled registry layers shadcn-style source on top. `dx components add <name>` copies the chosen component into the application's local `components` directory, so it becomes application-owned code. On the first addition, DX prompts for a root-level link to `/assets/dx-components.css`, which supplies the default theme.

```sh
dx components add button
```

## Composite primitive ordering

Many ordered or roving-focus composites require explicit zero-based `index` props rather than inferring order from RSX position. This includes accordion items, menu/navigation entries, radio/select options, tab triggers and panels, toggle items, and toolbar buttons. Matching tab triggers and panels also share a `value`.

```rust
Tabs {
    TabList {
        TabTrigger { index: 0, value: "account", "Account" }
    }
    TabContent { index: 0, value: "account", "Settings" }
}
```

Recompute indices after filtering, sorting, or conditionally rendering entries.

## Combobox control and filtering

`Combobox<T>` can be controlled with `value` and `query`. Its built-in filter preserves the rendered `ComboboxOption` order; query-dependent ranking must sort data before rendering and then assign indices in that sorted order.

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

## Calendar and date-picker compositions

`Calendar` and `RangeCalendar` render full month views. `DatePicker` and `DateRangePicker` precompose an editable input, trigger, popover, and calendar. `month_count` displays adjacent months; date pickers accept day/month/year placeholder formatter callbacks.

```rust
let mut selected_date = use_signal(|| None::<Date>);

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

`SheetClose` and several sidebar controls accept an `as` closure similar to an `asChild` API. Spread the received attributes onto the replacement element or the wrapper will lose merged classes, state data, ARIA values, and event handlers.

```rust
SheetClose {
    as: |attributes| rsx! {
        a { href: "#", ..attributes, "Go back" }
    }
}
```

## Sidebar state and interaction

`SidebarProvider` owns open, side, and collapse state and installs Cmd/Ctrl+B as its toggle shortcut. `SidebarCollapsible` supports `Offcanvas`, `Icon`, and `None`; `SidebarRail` is an optional resize handle. `SidebarMenuButton` wraps itself in a tooltip only when `tooltip: Option<Element>` is `Some`.

```rust
SidebarProvider {
    Sidebar {
        side: SidebarSide::Left,
        variant: SidebarVariant::Inset,
        collapsible: SidebarCollapsible::Icon,
        SidebarContent { /* groups and menus */ }
    }
    SidebarRail {}
    SidebarInset { /* main content */ }
}
```

## Context-driven toasts

Place `ToastProvider` above consumers, call `consume_toast()` in a descendant, and invoke severity methods with `ToastOptions`. Users can move keyboard focus to rendered toasts with F6.

```rust
button {
    onclick: |_| {
        consume_toast().error(
            "Critical error".to_string(),
            ToastOptions::new()
                .description("More information")
                .duration(Duration::from_secs(10))
                .permanent(false),
        );
    },
    "Show toast"
}
```

## Dynamic-height virtual lists

`VirtualList` renders visible rows plus a configurable approximate-row buffer and supports rows with dynamic heights. The render closure receives the absolute item index; give each row a stable key derived from the item when possible.

```rust
VirtualList {
    count: rows.len(),
    buffer: 8,
    render_item: move |idx| rsx! {
        article { key: "{rows[idx].id}", "{rows[idx].title}" }
    },
}
```

## Dynamic attribute lists

The separate `dioxus-attributes` crate supplies `attributes!`, which uses element-like syntax to produce a `Vec<Attribute>` for `..` spreads. It supports listeners and quoted custom data attributes.

```rust
let attrs = attributes!(div {
    class: "card",
    "data-state": "open",
    onclick: |_| println!("clicked"),
});

rsx! { div { ..attrs } }
```

## SDK feature aggregation

`dioxus-sdk` re-exports separate geolocation, storage, time, window, notification, sync, and utility crates behind same-named features; `notification` is singular. SDK minor versions track Dioxus minor versions. Most APIs return `Err(Unsupported)` at runtime on targets the selected package does not support, so a successful build does not prove runtime support.

```toml
[dependencies]
dioxus-sdk = { version = "0.7", features = ["geolocation", "storage", "time"] }
```

## Geolocation and notifications

Geolocation currently supports Web and Windows. Initialize it with a `PowerMode`, then read `use_geolocation()` as a result that may initially be `Error::NotInitialized`.

```rust
let _geolocator = init_geolocator(PowerMode::High).unwrap();
match use_geolocation() {
    Ok(coords) => rsx! { "{coords.latitude}, {coords.longitude}" },
    Err(Error::NotInitialized) => rsx! { "Initializing..." },
    Err(error) => rsx! { "{error}" },
}
```

Desktop notifications support Windows, macOS, and Linux. Configure application name, summary, and body through the builder before calling `show()`.

```rust
Notification::new()
    .app_name("Example".to_string())
    .summary("Finished".to_string())
    .body("The operation completed".to_string())
    .show()
    .unwrap();
```

## Persistent signals and time handles

`dioxus-sdk-storage::use_persistent(key, init)` exposes local persistent state through the usual readable/writable signal interface.

The time package provides `use_interval`, `use_timeout`, and `sleep`. `use_debounce` returns a handle whose `.action(value)` restarts the delay and eventually passes the newest value to its callback.

```rust
let mut count = use_persistent("count", || 0);
*count.write() += 1;

let mut save = use_debounce(
    Duration::from_millis(500),
    |text| println!("{text}"),
);
save.action("draft");
```
