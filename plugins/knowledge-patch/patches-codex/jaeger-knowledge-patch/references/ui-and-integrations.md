# UI and Contextual Integrations

## Trace input, navigation, and visualization

- **JSON Lines upload (2.0.0):** The UI accepts `.jsonl` containing
  one OTLP JSON object per line, in addition to earlier formats.
- **Configured links (2.1.0):** Link parameters support `add` and `pad_start`
  formatting functions plus ISO-date formatting.
- **Full IDs (2.4.0):** UI configuration can show full trace IDs instead of
  shortened IDs.
- **DAG tools:** Search, styling, depth/layout controls, and SFDP layout arrived
  in 2.5.0; node context menus arrived in 2.6.0.
- **Log time filtering (2.7.0):** Displayed logs can follow the selected trace
  time range.
- **Copy trace IDs (2.10.0):** Clicking a trace ID copies it.
- **Aggregate logs (2.17.0):** The trace logs view aggregates events from every
  span.
- **Timeline filtering (2.18.0):** Prune displayed timeline spans by service.
- **Flamegraph (2.20.0):** The native flamegraph has an adjustable table/chart
  split and scrolling support.

## Search and Monitor

- **Fuzzy selectors (2.13.0):** Shared searchable selectors use fuzzy matching,
  including deep-dependencies and quality-metrics headers.
- **Incomplete traces (2.14.0):** The UI detects incomplete traces and exposes
  a search-time offset for retrieving them.
- **Summary migration (2.19.0):** Search results come from
  `/api/v3/trace-summaries`. Storage-specific summary columns are hidden if the
  backend lacks them.
- **Search presentation (2.19.0):** Results can use a table instead of a list;
  the side panel is resizable and collapsible. Default lookback is configurable
  and can be reconstructed from URL timestamps.
- **Table defaults (2.20.0):** Table is the default result view. It supports
  ascending start-time sorting, improved column sorting, and an
  absolute/relative start-time toggle.
- **Shareable Monitor filters (2.20.0):** `service`, `spankind`, and `timeframe`
  are synchronized to the URL.

## Themes and trace layout

- **Themes:** The selector was experimental in 2.13.0. Dark theme became
  supported and enabled by default in 2.14.0; disabling theme selection makes
  light mode the default.
- **OpenTelemetry terminology (experimental, 2.14.0):** A feature flag switches
  UI terminology and visually distinguishes synthetic OpenTelemetry
  attributes.
- **Trace layout (experimental):** Version 2.16.0 introduced layout state,
  toggles, and a span side panel. Version 2.17.0 added tree-only and combined
  modes, analytics, and later side-panel selection and polish.
- **Legacy browsers (2.18.0):** The UI no longer supports legacy browsers.
- **Package identity (2.16.0):** The main package is
  `@jaegertracing/jaeger-ui`; update workspace references.
- **Development configuration (2.13.0):** The development server supports
  custom UI configuration.

## MCP and AI-facing integration

- **Initial MCP server (experimental, 2.15.0):** `jaegermcp` provided a
  Streamable HTTP server with storage integration and configurable CORS. Tools
  included `search_traces`, `get_span_details`, `get_trace_errors`,
  `get_trace_topology`, `get_services`, `get_critical_path`, and
  `get_span_names`, using OpenTelemetry `span_name` terminology.
- **Tenancy and bounds (experimental, 2.17.0):** The server enforces tenancy
  plus configuration-driven handler and response limits and supplies
  system-prompt instructions for clients.
- **Frontend endpoint changes (experimental, 2.18.0):** An AI-facing MCP
  endpoint exposes dynamic contextual frontend tools. `get_service_dependencies`
  was added and the non-standard health tool was removed.
- **AG-UI and UI gate (experimental, 2.19.0):** Jaeger implements an AG-UI
  endpoint. AI-assisted UI features require `ai.enabled: true`; the default is
  `false`.
- **Consolidation (2.20.0):** The standalone `jaegermcp` extension merged into
  `jaegerquery`; migrate configurations that instantiate it separately.
  The MCP endpoint and stream registry are session-scoped, can expose
  per-session UI tools, and add `read_skill`. `get_services` and
  `get_span_names` report `total_count` and `truncated`.
- **GenAI views (experimental, 2.20.0):** GenAI traces can auto-activate a
  timeline viewer and use a span-detail tab. Message content supports
  plain-text, Markdown, and JSON views; the assistant panel supports Markdown
  and resizing.
