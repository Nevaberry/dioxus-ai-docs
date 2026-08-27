# Data and protocol-aware filters

Use this reference for MCP, gRPC/JSON, metadata extraction, GeoIP, content inspection, and other protocol-aware filters.

## MCP

### MCP bridges, aggregation, and A2A (since 1.38.0)

The work-in-progress `mcp_json_rest_bridge` transcodes MCP JSON-RPC to JSON REST, including session negotiation and `tools/call` requests and responses, but is not recommended for production. A multi-cluster extension aggregates MCP services, and Envoy can parse Agent2Agent JSON-RPC messages.

### MCP filter and router protocol coverage (since 1.38.0)

The MCP router adds resource list/read/subscribe/unsubscribe, resource-template listing, prompt list/get, completion, logging-level, cancellation, and roots-changed methods. The MCP filter accepts `application/json` parameters, recognizes session-ending HTTP `DELETE` in `REJECT_NO_MCP` mode, moves its default metadata namespace to `envoy.filters.http.mcp` unless `envoy.reloadable_features.mcp_filter_use_new_metadata_namespace=false`, and can propagate trace context and baggage from MCP parameters.

### MCP inspection and routing (since 1.37.0)

The new MCP HTTP filter parses Model Context Protocol JSON-RPC, stores request method and ID in dynamic metadata, and can classify methods into built-in or custom groups. The `mcp_router` filter adds multi-backend initialization and tool-list fanout, tool-prefix routing, composite session IDs, and response aggregation.

### MCP routing and bridge controls (since 1.39.0)

The MCP router now handles server-to-client elicitation, sampling, and roots requests by rewriting JSON-RPC IDs for multiplexed routing; `lazy_initialization` returns the initial response immediately and initializes each backend on first use. The JSON REST bridge accepts per-route tool configuration and can serve `tools/list` locally through `tools_list_local`.

### MCP sessions, SSE, and observability (since 1.38.0)

The router accepts session-less backends and streams SSE for `tools/call`, while incrementally aggregating SSE fanout for tools, initialization, resources, and prompts. It also adds routing, fanout, and error statistics.

### MCP validation and body-limit behavior (since 1.39.0)

The MCP filter adds `reject_duplicate_keys` to reject duplicate JSON keys at any depth and exposes processing status through dynamic metadata and filter state. When a body exceeds its limit, `PASS_THROUGH` forwards it with `is_exceeding_limit`, whereas `REJECT_NO_MCP` returns `400` if required MCP fields were not found within the inspected prefix.

## gRPC, protobuf, and Thrift

### gRPC-JSON output controls (since 1.35.0)

The gRPC JSON transcoder's JSON print options are now configurable, and streamed responses can use SSE-style message framing.

### gRPC-to-JSON transcoding (since 1.33.0)

A new HTTP filter transcodes gRPC requests to JSON.

### Proto API Scrubber (since 1.37.0)

The Proto API Scrubber HTTP filter can restrict and scrub gRPC request and response messages, including message- and enum-level restrictions. Blocked methods now return `404 Not Found` or gRPC `NOT_FOUND` rather than revealing their existence with `403` or `PERMISSION_DENIED`.

### Proto API Scrubber unknown fields (since 1.38.0)

`ProtoApiScrubberConfig.scrub_unknown_fields=true` removes unknown protobuf fields while scrubbing; it is disabled by default.

### Thrift field selection (since 1.36.0)

The Thrift-to-metadata HTTP filter can use `field_selector` to extract selected body fields; if both `field_selector` and the older `field` are set, `field_selector` wins.

## Metadata, GeoIP, and IP tagging

### File-backed IP tags (since 1.39.0)

The HTTP IP-tagging filter can load tag definitions from a YAML or JSON file-backed `DataSource`. Supplying `watched_directory` dynamically reloads file changes.

### GeoIP and tracing additions (since 1.38.0)

GeoIP `geo_field_keys.asn_org` exposes the autonomous-system organization name from a MaxMind ASN database. OpenTelemetry tracer spans can now carry log events.

### GeoIP ASN database selection (since 1.35.0)

ASN lookup uses `asn_db` when `asn_db_path` is configured and otherwise falls back to `isp_db`.

### GeoIP database configuration and outputs (since 1.34.0)

GeoIP configuration renames the existing `isp_db_path` to `asn_db_path`, while `MaxMindConfig` gains a distinct `isp_db_path` for an ISP database. `CommonGeoipProviderConfig` can emit `isp` and `apple_private_relay`, with the latter true when the ISP is `iCloud Private Relay`.

### GeoIP network filtering and inputs (since 1.37.0)

A network GeoIP filter performs lookups without HTTP and stores results in filter state. GeoIP also adds `country_db_path` for MaxMind Country databases, `custom_header_config` for header-derived addresses, and a format-specifier-based `client_ip` for the network filter.

### SSE parsing and metadata extraction (since 1.38.0)

The SSE parser now understands `id`, `event`, and digits-only `retry` fields in addition to `data`. `envoy.filters.http.sse_to_metadata` extracts values from SSE streams into dynamic metadata, using pluggable parsers such as `envoy.content_parsers.json` with JSON-path selectors.

## Content, JSON, SSE, and file serving

### Direct-response and JSON metadata overrides (since 1.37.0)

`DirectResponseAction.body_format` applies substitution formatting to direct-response bodies. The JSON-to-Metadata HTTP filter now accepts per-route configuration so routes can use different request- or response-body extraction rules.

### XFCC JSON and static file serving (since 1.38.0)

The XFCC header supports an optional JSON representation selected by its `format` setting. The new `file_server` HTTP filter serves file contents from the local filesystem.

