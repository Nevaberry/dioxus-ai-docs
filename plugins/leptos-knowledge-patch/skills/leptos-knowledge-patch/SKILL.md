---
name: leptos-knowledge-patch
description: "Leptos changes since training cutoff (latest: 0.8.17) — ShowLet component, Show signal support, Bitcode server function encoding. Load before working with Leptos."
version: "0.8.17"
license: MIT
metadata:
  author: Nevaberry
---

# Leptos Knowledge Patch

Covers Leptos 0.8.8–0.8.17 (2024-08-26 through 2025-03-01). Claude Opus 4.6 knows Leptos through 0.6.x. It is **unaware** of the features below.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Components & views | [references/components-and-views.md](references/components-and-views.md) | `<ShowLet>`, `<Show>` signal support |
| Server functions | [references/server-functions.md](references/server-functions.md) | `Bitcode` encoding option |

---

## `<ShowLet>` Component (0.8.8)

New component for unwrapping `Option` values — similar to `<Show>` but provides the inner value to children:

```rust
<ShowLet
    when=move || some_option.get()
    fallback=|| view! { <p>"Nothing here"</p> }
    let:value
>
    <p>"Got: " {value}</p>
</ShowLet>
```

## `<Show>` Accepts Signals Directly (0.8.8)

`<Show when=...>` now accepts signals in addition to closures:

```rust
let visible = RwSignal::new(true);
// Before: <Show when=move || visible.get()>
// Now also: <Show when=visible>
```

## `Bitcode` Encoding for Server Functions (0.8.11)

New `Bitcode` encoding option for server function IO, alongside existing `Json`, `Cbor`, etc. Requires the `bitcode` feature on `server_fn`.

```rust
#[server(endpoint = "my_fn", encoding = "Bitcode")]
pub async fn my_server_fn(data: MyData) -> Result<MyResponse, ServerFnError> {
    // ...
}
```

## Reference Files

| File | Contents |
|---|---|
| [components-and-views.md](references/components-and-views.md) | `<ShowLet>` component, `<Show>` signal support |
| [server-functions.md](references/server-functions.md) | `Bitcode` encoding for server functions |
