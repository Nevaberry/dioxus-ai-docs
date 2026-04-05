# htmx 2.0 Changes (2024-06-17)

Mostly cleanup release. Key behavioral changes from 1.9.x:

## Breaking Changes

- **DELETE requests** use query params instead of form-encoded body
  - Revert: `htmx.methodsThatUseUrlParams = ['get']`
- **`htmx.config.selfRequestsOnly`** defaults `true` — htmx will only make requests to the same domain by default
- **`htmx.config.scrollBehavior`** defaults `'instant'` (was `'smooth'`)
- **Extensions** moved to separate repo at `extensions.htmx.org`
  - `hx-sse` and `hx-ws` attributes removed — use the SSE and WebSocket extensions instead
- **`hx-on` special syntax removed** — use `hx-on:` prefix syntax (e.g., `hx-on:click="..."`)
- **`htmx.swap()`** — new public API replacing internal `selectAndSwap()`
