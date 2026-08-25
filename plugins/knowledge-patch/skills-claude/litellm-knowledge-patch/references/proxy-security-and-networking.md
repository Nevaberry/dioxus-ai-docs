# Proxy security and networking

## SSRF validation for fetched URLs

`litellm_settings.user_url_validation` defaults to `true`. It blocks URLs whose
DNS result is private, loopback, link-local, or otherwise non-global.
`user_url_allowed_hosts` entries must exactly match the URL hostname, including
a port when present. With split-horizon DNS, allowlist the public hostname, not
the private address to which it resolves.

## Request, key-alias, and upload validation

`enable_json_schema_validation` opts all requests into schema validation.
`enable_key_alias_format_validation` requires aliases to be 2–255 characters,
start and end with an alphanumeric character, and use only
`a-zA-Z0-9_-/.@` internally.

`require_managed_files: true` makes `POST /v1/files` require
`target_model_names` and rejects classic provider uploads with HTTP 400.

## Checks across input locations

In 1.97.0, request-parameter checks cover body, path, and form inputs
consistently. This is breaking for calls that previously bypassed a check by
placing a value in a different input location.

## Common checks after custom authentication

`custom_auth_run_common_checks` defaults to `false`. Enable it when custom-auth
requests must also pass model allowlists, budget checks, and rate limits.

## Fail-closed budget enforcement

`fail_closed_budget_enforcement` defaults off. When enabled, every budgeted
request is checked against the database and returns 503 when neither Redis nor
the database can establish spend.

`allow_requests_on_db_unavailable` instead allows requests whose virtual key
cannot be checked. Reserve that setting for private-network deployments.

## Tenant isolation

Responses IDs are tied to user information by default.
`disable_responses_id_security` removes the cross-user protection. Non-admin
`/spend/keys` and `/spend/users` results are caller-scoped;
`legacy_unscoped_spend_list_endpoints` restores the global view.
`reject_clientside_metadata_tags` prevents callers from supplying tags that
manipulate budget attribution.

## Drain endpoint protection and disconnects

`enable_drain_endpoint` exposes `GET /health/drain` and defaults off. Without
`drain_endpoint_token`, the route is unauthenticated. When configured, the
caller must send the matching `X-Drain-Token`.

`cancel_on_disconnect: true` cancels an abandoned non-streaming upstream call
and records status 499.

## Request and pass-through bounds

`max_request_size_mb` rejects oversized requests. `max_response_size_mb`
prevents oversized model output from being returned. The custom/native-provider
`pass_through_request_timeout` defaults to 600 seconds; a timeout defined for a
specific endpoint takes precedence.

## MCP public origin and trusted proxies

For MCP OAuth behind ingress, set `PROXY_BASE_URL` to the exact public origin
with no path or trailing slash. It takes precedence over forwarded headers.
Without it, `use_x_forwarded_for` is honored only when the direct peer is in
`mcp_trusted_proxy_ranges`.

## Explicit MCP grants

`require_key_mcp_access_defined` prevents an empty key grant from inheriting
the team's MCP servers. `require_end_user_mcp_access_defined` requires an
explicit end-user grant.

## Outbound proxy and socket behavior

aiohttp ignores `HTTP_PROXY` and `HTTPS_PROXY` by default. Enable environment
proxy discovery with `AIOHTTP_TRUST_ENV=true`. Connector limits default to
unlimited (`0`). Socket keepalive is disabled unless
`AIOHTTP_SO_KEEPALIVE` is enabled; idle, interval, and probe-count values then
default to 60 seconds, 30 seconds, and 5 probes.

## Deployment hardening switches

`LITELLM_ENABLE_HSTS` opts into HSTS and only takes effect over HTTPS.
`DISABLE_ADMIN_UI`, `NO_DOCS`, `NO_OPENAPI`, and `NO_REDOC` independently
remove public interfaces.

Log secret redaction is enabled by default unless
`LITELLM_DISABLE_REDACT_SECRETS=true`. `LITELLM_OIDC_ALLOWED_CREDENTIAL_DIRS`
restricts file-backed OIDC tokens; its default is
`/var/run/secrets,/run/secrets`.

## Docker image signature verification

All LiteLLM Docker images in 1.97.0 are signed with the Cosign key introduced at
commit `0112e53`. Pin the immutable commit when verifying an image:

```shell
cosign verify \
  --key https://raw.githubusercontent.com/BerriAI/litellm/0112e53046018d726492c814b3644b7d376029d0/cosign.pub \
  ghcr.io/berriai/litellm:v1.97.0
```

The more readable tag-relative `v1.97.0/cosign.pub` URL depends on repository
tag protection.
