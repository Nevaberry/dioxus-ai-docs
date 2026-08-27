# MCP and AI Integrations

All surfaces in this reference are experimental unless a deployment's own
compatibility policy explicitly promotes them.

## MCP server evolution

- In **2.15.0**, the experimental `jaegermcp` extension provided a Streamable
  HTTP MCP server with storage integration and configurable CORS. Its tools
  were `search_traces`, `get_span_details`, `get_trace_errors`,
  `get_trace_topology`, `get_services`, `get_critical_path`, and
  `get_span_names`; tool schemas use OpenTelemetry `span_name` terminology.
- In **2.17.0**, the server enforced tenancy plus configuration-driven handler
  and response limits. It also returned system-prompt instructions to MCP
  clients. Integrations must expect tenant and size boundaries to affect
  requests and results.
- In **2.18.0**, the frontend gained an AI-facing MCP endpoint for dynamic
  contextual tools. `jaegermcp` added `get_service_dependencies`, while its
  non-standard health tool was removed. Do not use MCP tool discovery as a
  health-check contract.
- Since **2.20.0**, the standalone `jaegermcp` extension is merged into
  `jaegerquery`. Migrate configurations that instantiate it separately.

## Session-scoped tools

Since **2.20.0**, the AI gateway's MCP endpoint and stream registry are
session-scoped and can expose per-session UI tools. The tool set includes
`read_skill`. Responses from `get_services` and `get_span_names` include
`total_count` and a `truncated` indicator, so clients should not assume the
returned list is complete.

Apply authentication, authorization, tenancy, CORS, handler limits, response
limits, and session cleanup to both the HTTP endpoint and its backing storage
access.

## AG-UI and feature gating

- Since **2.19.0**, Jaeger has an experimental AG-UI endpoint for AI-assisted
  integrations.
- Since **2.19.0**, AI-assisted UI behavior is gated by `ai.enabled`, which
  defaults to `false`. Enable it explicitly and independently of core trace
  collection and query readiness.

## Trace the AI path

Since **2.20.0**, the UI can emit its own OTLP traces. The Jaeger AI gateway and
sidecar propagate trace context and add GenAI span attributes. Use this
instrumentation to connect a browser action to gateway, tool, storage, and
sidecar work.

Also since **2.20.0**, experimental GenAI trace presentation includes an
auto-activating timeline, a span-detail tab, plain-text/Markdown/JSON message
rendering, and a resizable Markdown-capable assistant panel.

## Deployment checklist

1. Enable `ai.enabled` only in environments intended to expose AI features.
2. Configure MCP under `jaegerquery`, not as a standalone extension.
3. Enforce tenant identity before storage-backed tool execution.
4. Bound handlers and responses and surface truncation to callers.
5. Restrict CORS to intended frontend origins.
6. Treat session-scoped tools and streams as session-owned resources.
7. Instrument UI, gateway, sidecar, and tool work with propagated context.
8. Keep experimental endpoint availability out of core Jaeger health criteria.
