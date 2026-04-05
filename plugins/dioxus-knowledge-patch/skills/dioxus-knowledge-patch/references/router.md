# Router

## Route Parameter Syntax

```rust
#[derive(Routable, Clone, PartialEq)]
enum Route {
    #[route("/")]
    Home {},
    #[route("/user/:id")] // Dynamic segment
    User { id: u32 },
    #[route("/files/:..path")] // Catch-all (multiple segments)
    Files { path: Vec<String> },
    #[route("/search?:query")] // Query parameter
    Search { query: String },
    #[route("/docs#:section")] // Hash fragment
    Docs { section: String },
}
```

## Nested Routes with Layouts

```rust
#[derive(Routable, Clone, PartialEq)]
enum Route {
    #[nest("/admin")]
    #[layout(AdminLayout)]
    #[route("/")]
    AdminHome {},
    #[route("/users")]
    AdminUsers {},
    #[end_layout]
    #[end_nest]
    #[route("/")]
    Home {},
}

#[component]
fn AdminLayout() -> Element {
    rsx! {
        nav { "Admin Nav" }
        Outlet::<Route> {}  // Child routes render here
    }
}
```

## Navigation

### Programmatic Navigation

Use `use_navigator`:

```rust
fn LoginButton() -> Element {
    let nav = use_navigator();

    rsx! {
        button {
            onclick: move |_| {
                nav.push(Route::Dashboard {});  // Navigate forward
                // nav.replace(Route::Home {});  // Replace current (no back)
                // nav.go_back();                // Browser back
                // nav.go_forward();             // Browser forward
            },
            "Login"
        }
    }
}
```

### Link Component

Declarative navigation with active state:

```rust
rsx! {
    Link {
        to: Route::Home {},
        active_class: "nav-active",  // Applied when route matches
        class: "nav-link",
        "Home"
    }
    Link {
        to: "https://example.com",  // External URL
        new_tab: true,              // Opens in new tab
        "External"
    }
}
```

### Get Current Route

```rust
fn Breadcrumb() -> Element {
    let route: Route = use_route(); // Current matched route
    rsx! { "Current: {route:?}" }
}
```
