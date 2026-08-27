# MCP, Agents, and Guardrails

## Agent gateway

### A2A agent gateway

The gateway can register and invoke A2A agents beside model and MCP routes, so
the deployment does not need a separate agent gateway.

## Client-held MCP authorization

### Client-held MCP credentials

Since 1.93.0, MCP servers support `true_passthrough` and `oauth_delegate` auth
modes, with upstream OAuth discovery bound to the individual server. The
`dcr_bridge` route transports client-held credentials in a sealed envelope and
provides discovery plus registration and token relays. The flow requires PKCE
S256.

### MCP OAuth token exchange

Since 1.93.0, MCP server configuration accepts the `oauth2_token_exchange`
authentication type and the `entra_obo` token-exchange profile through both
the REST API and dashboard. The chosen `oauth2_flow` is persisted explicitly,
and legacy null values are backfilled during startup. Outbound concurrency
limits apply to on-behalf-of MCP tool calls.

### MCP ingress origin and explicit grants

Behind ingress, set `PROXY_BASE_URL` to the exact public origin for MCP OAuth,
without a path or trailing slash. It takes precedence over forwarded headers.
Otherwise, `use_x_forwarded_for` is trusted only when the immediate peer is in
`mcp_trusted_proxy_ranges`.

`require_key_mcp_access_defined` prevents an empty virtual-key grant from
inheriting the team's MCP servers. `require_end_user_mcp_access_defined`
requires an explicit end-user grant as well.

## Tool selection and filtering

### MCP semantic filtering

Since 1.93.0, the semantic filter expands `litellm_proxy` tools before it
filters, reports the number of removed tools, and preserves whole tool names
in its response header. Context-window failures are surfaced and the filter
fails closed.

## Guardrail coverage

### MCP-aware guardrails

Since 1.93.0, Model Armor can inspect MCP tool calls in `pre_mcp_call` and
`during_mcp_call` modes. Content Filter supports `pre_mcp_call`. With
`skip_unscannable_attachments`, Model Armor passes reference-only attachments
through and no longer applies an attachment-count limit.

### Rubrik and Responses guardrail coverage

Since 1.97.0, the Rubrik guardrail supports prompt moderation, response-text
blocking, buffered streaming, and failure logging. A blocked request is
attributed to its caller. Output scanning also covers the
`/openai/v1/responses` alias.

## Agent-client administration

### Claude Code skill updates

Since 1.97.0, Claude Code skill registration is create-only. Use the separate
`PUT` route to update an existing registration.
