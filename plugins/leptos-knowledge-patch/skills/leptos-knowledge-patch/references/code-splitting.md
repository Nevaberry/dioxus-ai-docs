# WASM Code Splitting

Lazy loading and code splitting introduced in 0.7.5 (macros) and fully released in 0.8.5.

## #[lazy] Macro (0.8.5+)

Converts any sync or async function into a lazily-loaded async function, split into its own WASM chunk:

```rust
#[lazy]
fn deserialize_comments(data: &str) -> Vec<Comment> {
    serde_json::from_str(data).unwrap()
}
// Now returns a Future — loaded on demand in a separate WASM chunk
```

### Visibility Modifiers (0.8.9+)

`#[lazy]` correctly propagates visibility modifiers (`pub`, `pub(crate)`, etc.).

## #[lazy_route] and LazyRoute Trait (0.8.5+)

Splits routes into a data half and a view half, loaded **concurrently** by the router. Works with nested routing — the router concurrently loads all data and all lazy views before navigating:

```rust
struct ViewD {
    data: Resource<Result<Vec<i32>, ServerFnError>>,
}

#[lazy_route]
impl LazyRoute for ViewD {
    fn data() -> Self {
        Self {
            data: Resource::new(|| (), |_| d_data()),
        }
    }

    fn view(this: Self) -> AnyView {
        let items = move || {
            Suspend::new(async move {
                this.data
                    .await
                    .unwrap_or_default()
                    .into_iter()
                    .map(|item| view! { <li>{item}</li> })
                    .collect::<Vec<_>>()
            })
        };
        view! {
            <p id="page">"View D"</p>
            <Suspense fallback=|| view! { <p id="loading">"Loading..."</p> }>
                <ul>{items}</ul>
            </Suspense>
            <Outlet/>
        }
        .into_any()
    }
}
```

Integration with `cargo-leptos` is required for actual WASM splitting. See the `lazy_routes` example.

### Navigation Fix (0.8.9)

Fixed double-rebuild and incorrect behavior when navigating multiple times to the same lazy route.

### Preload Fix (0.8.10)

Correctly preloads the `__wasm_split.*.js` file.

## Lazy Server Functions (0.8.6+)

`#[server]` and `#[lazy]` attributes can be combined — the server function's client-side code is lazy-loaded:

```rust
#[server]
#[lazy]
async fn heavy_server_fn() -> Result<String, ServerFnError> {
    Ok("result".into())
}
```

File hashing works correctly with lazy loading as of 0.8.6.

## --cfg=erase_components (0.8.0+)

Compile-time optimization that significantly improves compile times. Now the **default** in latest `cargo-leptos`. Can be set up manually for Trunk.

Works correctly with `AttributeInterceptor` (fixed 0.7.3), `AddAnyAttr` (fixed 0.7.5), and `{..}` spreading.

### Missing Import Fix (0.8.15)

`IntoAnyAttribute` import when using `erase_components` was fixed.

## wasm-split Crate (0.8.12)

The vendored `wasm-split` crate was replaced with the published out-of-repo version. No API changes.
