# User Interface

## Routing and reverse-proxy paths

- Since **2.16.0**, the UI's API v3 client honors the configured base-path
  prefix instead of sending v3 requests to the site root.
- Since **2.18.0**, the query frontend and UI derive their URL prefix from the
  browser URL at page load. Path-prefixed deployments can use this automatic
  discovery rather than depending only on explicit UI base-path configuration.
- `jaeger_query.base_path` still represents the prefix on requests that reach
  Jaeger. When a proxy strips an external prefix, leave the internal base path
  `/`; otherwise configure the forwarded prefix.

Test the browser URL, static assets, API v3 requests, and copied deep links
through the real proxy chain.

## Search and trace identifiers

- Since **2.4.0**, the UI can display full trace IDs instead of shortened IDs
  when configured.
- Since **2.10.0**, clicking a trace ID copies it.
- Since **2.19.0**, search results come from
  `/api/v3/trace-summaries`. Columns requiring storage-native summary support
  are hidden when the backend lacks that capability.
- Since **2.19.0**, search results have an optional table view; its side panel
  is resizable and collapsible.
- Since **2.19.0**, the default search lookback is configurable, and a lookback
  can be reconstructed from timestamp parameters in the search URL.
- Since **2.20.0**, the table is the default search-results view. It supports
  ascending start-time sorting, improved column sorting, and an
  absolute/relative start-time display toggle.
- Since **2.20.0**, the UI treats trace IDs as opaque strings and can therefore
  display and query base64-encoded identifiers without converting them to hex.

## Trace views

- Since **2.7.0**, displayed logs can be filtered to the selected trace time
  range.
- Since **2.17.0**, an aggregate trace logs view shows events from every span
  without opening spans individually.
- Since **2.18.0**, the trace timeline can prune spans by service.
- In **2.16.0**, the experimental trace experience introduced layout-mode
  state, toggles, and a span-details side panel.
- In **2.17.0**, experimental layout work added tree-only mode, which hides the
  timeline, as well as combined modes, analytics, and later side-panel
  selection and polish.
- Since **2.20.0**, a native flamegraph view provides an adjustable
  table/chart split and scrolling behavior.

## DAG view

- Since **2.5.0**, the DAG view has search, refreshed styling, depth and layout
  controls, and an SFDP layout.
- Since **2.6.0**, DAG nodes expose a context menu for node-specific actions.

## Links, uploads, and selectors

- Since **2.0.0**, trace upload accepts `.jsonl` files containing one OTLP JSON
  object per line.
- Since **2.1.0**, configured UI-link parameters support `add` and `pad_start`,
  and values can be formatted as ISO dates.
- Since **2.13.0**, UI development mode accepts custom UI configuration.
- Since **2.13.0**, the shared searchable selector supports fuzzy matching.
  Deep-dependencies and quality-metrics headers use it.
- Since **2.14.0**, the UI detects incomplete traces and lets users change the
  search time offset used to retrieve them.

## Theme and terminology

- An experimental dark-theme selector appeared in **2.13.0**. Since
  **2.14.0**, dark theme is officially supported and the selector is enabled by
  default. If theme selection is disabled by configuration, light mode is the
  default.
- Since **2.14.0**, an experimental feature flag can switch the UI to
  OpenTelemetry terminology and visually distinguish synthetic OpenTelemetry
  attributes.

## Monitor and SPM

- Since **2.17.0**, storage capabilities are authoritative for SPM availability
  and Monitor-tab visibility.
- Since **2.20.0**, Monitor filters synchronize to the URL, including
  `service`, `spankind`, and `timeframe`, so a filtered view can be restored or
  shared.

## Browser and build compatibility

- Since **2.16.0**, the primary package is
  `@jaegertracing/jaeger-ui`; update workspace references that use the earlier
  package identity.
- Since **2.18.0**, legacy browsers are unsupported. Validate the actual browser
  fleet before upgrading a user-facing deployment.
- Since **2.20.0**, UI and embedded-UI builds use pnpm instead of npm.

## AI-assisted presentation

- Since **2.20.0**, experimental GenAI traces can auto-activate a specialized
  timeline and expose a span-detail tab. Message content can render as plain
  text, Markdown, or JSON, and the assistant panel supports Markdown and
  resizing.
- Since **2.20.0**, the UI can export its own OTLP traces. Related gateway and
  sidecar instrumentation is covered in [mcp-ai.md](mcp-ai.md).
