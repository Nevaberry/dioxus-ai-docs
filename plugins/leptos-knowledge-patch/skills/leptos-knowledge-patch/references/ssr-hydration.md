# SSR & Hydration

Custom HTML shell, hydration changes, compile-time optimizations, and streaming fixes.

## Custom HTML Shell (0.7+)

The HTML shell is no longer hardcoded. Write it yourself as a Leptos component:

```rust
pub fn shell(options: LeptosOptions) -> impl IntoView {
    view! {
        <!DOCTYPE html>
        <html lang="en">
            <head>
                <meta charset="utf-8"/>
                <meta name="viewport" content="width=device-width, initial-scale=1"/>
                <AutoReload options=options.clone() />
                <HydrationScripts options/>
                <MetaTags/>
            </head>
            <body>
                <App/>
            </body>
        </html>
    }
}
```

You can now set `<title>` directly without `leptos_meta`.

## Hydration Changes (0.7+)

- `leptos::mount::hydrate_body` for SSR hydration; `mount_to_body` is CSR-only
- `leptos::mount::mount_to_body` for CSR entry point
- `get_configuration` is now **sync** (remove `.await`)
- `.leptos_routes()` no longer takes `LeptosOptions` as argument

## --cfg=erase_components (0.8.0+)

Compile-time optimization for significant compile time improvements. Now the **default** in latest `cargo-leptos`.

Manual setup for Trunk: add `--cfg=erase_components` to rustflags.

## subsecond Hot Patching (0.8.10+)

Minimal support for the `subsecond` crate, enabling hot-reloading of Rust logic without full recompiles. An example is provided.

## Hot Reload Improvements (0.8.4+)

- Myers diffing algorithm for hot-reload diffs (0.8.4) — more correct when view count changes
- Fixed longstanding issue where hot-reload stops working when number of views changes
- Multiple hot-reload bugs fixed

## Live Reload

| Version | Change |
|---|---|
| 0.8.8 | Default "auto" protocol option (auto-detects ws vs wss) |
| 0.8.9 | Correctly uses `wss://` when page is on HTTPS |
| 0.8.16 | Auto-reconnects on close |

## --cfg locations (0.7.1+)

Opt-in diagnostic location tracking in release builds:

```
RUSTFLAGS="--cfg locations" cargo build --release
```

Previously locations were only available in debug mode.

## Streaming SSR Fixes

| Version | Fix |
|---|---|
| 0.7.1 | Blocking resources no longer cause out-of-order streaming chunks |
| 0.7.4 | CSP nonces applied to streaming script tags and `leptos_meta` components |
| 0.8.10 | Out-of-order streaming: all chunks correctly polled |
| 0.8.11 | `Suspend` `dry_resolve()` call fixed (caused SSR issues) |

## Suspense and Error Boundary Fixes

| Version | Fix |
|---|---|
| 0.7.4 | Adjacent `<Transition>` components no longer overwrite `SuspenseContext` |
| 0.7.5 | `ErrorBoundary` correctly catches errors through reactive view updates |
| 0.8.1 | Nested `Suspense > ErrorBoundary > Suspense` works |
| 0.8.3 | Meta tags render correctly inside synchronously-available `Suspend` |
| 0.8.13 | Conditionally-read resources correctly tracked in `Suspense` |
| 0.8.16 | `Transition` fallback not incorrectly shown on 2nd change |

## Islands Mode

- `experimental-islands` renamed to `islands` (0.7+)
- `islands-router` feature for client-side routing with islands (0.8.0+)
- Islands no longer require unnecessary `Either` wrapper (0.8.1)
- Context correctly provided through islands to children (0.8.1)
- Islands routing works in 404 routes (0.8.8)

## Axum Integration

| Version | Change |
|---|---|
| 0.8.0 | Upgraded to Axum 0.8 (forced migration from 0.7) |
| 0.7.3 | Custom state in `file_and_error_handler` |
| 0.8.3 | `handle_response_inner` made public |
| 0.8.4 | Actix default features disabled for cleaner deps |
| 0.8.13 | Static file response headers correctly set in `leptos_axum` |
| 0.8.16 | `file_and_error_handler_with_context` broken into composable tower services |

## DOM and Hydration Fixes

| Version | Fix |
|---|---|
| 0.7.1 | `Vec<_>` DOM swapping fixed |
| 0.7.1 | Hydration inside `<noscript>` no longer attempted |
| 0.7.1 | Duplicate `Location` headers on redirect fixed |
| 0.7.2 | Static text node hydration in nightly fixed |
| 0.8.3 | `<select>` value: children mounted before attributes set |
| 0.8.3 | `Vec<_>` can be rebuilt before mount (no panic) |
| 0.8.8 | `task::spawn` maintains reactive ownership |
| 0.8.9 | `Vec<AnyAttribute>` replacement clears old attributes first |
| 0.8.10 | Event listeners correctly removed on drop |
| 0.8.13 | `class` attribute consistent between SSR and CSR |
| 0.8.17 | SSR panic messages replaced with actionable diagnostics |

## Dependency Reductions (0.8.16)

`parking_lot`, `dashmap`, and `linear-map` all removed from dependency tree, reducing compile times and binary size.

## Params Derive Without Nightly (0.8.16+)

`Params` derive macro no longer requires the nightly compiler.

## console Feature (0.7.3+)

`reactive_graph` enables the `console` feature of `web-sys` when targeting WASM, allowing reactive graph internals to log to browser console.

## codee / rkyv (0.7.5+)

`codee` bumped to support `rkyv` version 8. Feature propagation fixed in 0.7.4.
