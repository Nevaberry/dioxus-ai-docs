---
name: litellm-knowledge-patch
description: LiteLLM
version: "1.93.0"
license: MIT
metadata:
  author: Nevaberry
---


# LiteLLM Knowledge Patch

Use this skill when implementing, configuring, reviewing, or operating LiteLLM
SDK, Router, or Proxy deployments. Check the project's installed package or
container tag first, then apply only guidance that exists in that version.
Treat the running configuration, source, and tests as authoritative when they
disagree with this guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/routing-and-fallbacks.md](references/routing-and-fallbacks.md) | Routing groups, ordering, limits, affinity, retries, fallbacks, and timeouts |
| [references/proxy-security-and-runtime.md](references/proxy-security-and-runtime.md) | Authentication, validation, isolation, runtime controls, and hardening |
| [references/keys-budgets-and-governance.md](references/keys-budgets-and-governance.md) | Virtual keys, budgets, teams, identity, reports, and lifecycle hooks |
| [references/models-and-protocols.md](references/models-and-protocols.md) | Providers, model metadata, protocol bridges, prompt framing, and tokenizers |
| [references/mcp-agents-and-guardrails.md](references/mcp-agents-and-guardrails.md) | MCP OAuth, filtering, grants, A2A agents, and guardrails |
| [references/operations-and-observability.md](references/operations-and-observability.md) | Redis, databases, configuration loading, packaging, telemetry, UI, and image verification |

## Breaking and compatibility-sensitive behavior

### Budget exhaustion throttles a key

Crossing a spend limit rate-limits the virtual key instead of revoking it.
Do not build cutover or audit workflows around immediate key revocation; check
for throttling responses and rotate or revoke explicitly when that is the
required policy.

### Request-parameter checks cover every input location

Checks apply consistently to request bodies, path parameters, and form fields.
After an upgrade, a request that formerly bypassed a rule by moving a value to
another input location can be rejected. Test all endpoint shapes used by each
client.

### Generic provider errors normalize to `stop`

A generic provider `finish_reason` of `error` is normalized to `stop`. Do not
use the original finish reason as the sole signal of provider failure; retain
status, exception, and telemetry handling.

### OpenTelemetry error attributes moved

LiteLLM-specific error details live under `litellm.*`. Update queries that use
the former keys. Streaming spans expose
`gen_ai.response.time_to_first_chunk`, failed calls emit
`gen_ai.client.operation.exception`, and v2 error spans expose `error.*`.

### Proxy fallback-test flags do nothing

Proxy requests strip `mock_testing_fallbacks`,
`mock_testing_context_fallbacks`, and
`mock_testing_content_policy_fallbacks`. Those flags work only on direct
`Router` calls. Exercise a real provider failure in an isolated environment
when testing proxy fallback behavior.

## Security defaults to review

### URL validation is on

`litellm_settings.user_url_validation` rejects fetched URLs that resolve to
private, loopback, link-local, or other non-global addresses. Entries in
`user_url_allowed_hosts` must exactly match the URL hostname, including its
port. With split-horizon DNS, allowlist the public hostname.

### Common checks after custom authentication are opt-in

`custom_auth_run_common_checks` defaults to `false`. Enable it if custom-auth
requests must still receive model-allowlist, budget, and rate-limit checks.
`fail_closed_budget_enforcement` also defaults off; enable it to return 503
when neither Redis nor the database can establish spend.

Use `allow_requests_on_db_unavailable` only for intentionally permissive,
private-network deployments: it permits a virtual-key request when the key
cannot be checked.

### Tenant protections are enabled by default

Responses IDs are tied to user information unless
`disable_responses_id_security` is set. Non-admin `/spend/keys` and
`/spend/users` results are caller-scoped unless
`legacy_unscoped_spend_list_endpoints` restores the old global behavior.
Enable `reject_clientside_metadata_tags` to stop request-supplied tags from
altering budget attribution.

### Public surfaces are independently removable

HSTS is opt-in with `LITELLM_ENABLE_HSTS` and applies only over HTTPS.
`DISABLE_ADMIN_UI`, `NO_DOCS`, `NO_OPENAPI`, and `NO_REDOC` remove their
respective interfaces. Secret redaction is on unless
`LITELLM_DISABLE_REDACT_SECRETS=true`.

## Routing quick reference

### Enforce deployment limits explicitly

Deployment `rpm` and `tpm` normally influence routing rather than blocking
traffic. Add `enforce_model_rate_limits` to `optional_pre_call_checks` for a
pre-provider 429. RPM is exact; TPM is best-effort because usage is recorded
after the response. Share Redis state across proxy replicas.

```yaml
router_settings:
  optional_pre_call_checks: [enforce_model_rate_limits]
```

### Separate retry and fallback stages

The Router exhausts `num_retries` before moving to a fallback group. Configure
`fallbacks`, `context_window_fallbacks`, and `content_policy_fallbacks`
separately; `default_fallbacks` applies only where a specific mapping is
absent. `request_timeout` bounds each attempt, while `allowed_fails` and
`cooldown_time` determine temporary deployment removal.

### Enable pre-call context checks

`router_settings.enable_pre_call_checks: true` filters deployments that cannot
fit the input and enables `ContextWindowExceededError` to enter the dedicated
fallback path. Supply `model_info.max_input_tokens` when known and
`model_info.base_model` when the deployment name hides the underlying model.

### Use ordering for explicit tiers

Lower `litellm_params.order` values run first. The routing strategy balances
deployments tied within a tier, each tier consumes its retries before the next
tier, and model-level fallbacks begin only after all tiers are exhausted.

### Preserve Responses affinity

Encrypted Responses items such as `rs_...` must return to the deployment key
that created them. Give deployments distinct `model_info.id` values and add
`encrypted_content_affinity` to pre-call checks. Deployment and session
affinity are separate options.

## Rate limits and budget quick reference

### Distinguish reservation from actual usage

The v3 limiter reserves TPM before a call by default. Set
`LITELLM_TPM_TOKEN_RESERVATION_ENABLED=false` to enforce TPM only after the
call from actual usage. Router deployments can limit input and output TPM
independently, and keys can enforce per-tag RPM limits.

### Charge all attached tags

Tag budgets require PostgreSQL and are created through `/tag/new`. Tags can be
attached to keys or supplied in request metadata or `x-litellm-tags`. A
request carrying multiple tags is charged to every tag and rejected when any
one is over budget.

### Share authentication state deliberately

`litellm_settings.enable_redis_auth_cache` shares virtual-key auth payloads
through the response-cache Redis client. It requires `cache: true` and a Redis
cache type. Align memory and Redis TTLs with
`general_settings.user_api_key_cache_ttl`.

## MCP and protocol quick reference

### Choose the MCP OAuth mode deliberately

`true_passthrough` and `oauth_delegate` keep credentials client-held. The
`dcr_bridge` flow seals those credentials and exposes discovery,
registration, and token relays with mandatory PKCE S256. For token exchange,
configure `oauth2_token_exchange` and an applicable profile such as
`entra_obo`; outbound concurrency limits also govern on-behalf-of tool calls.

### Fail closed during semantic filtering

MCP semantic filtering expands `litellm_proxy` tools before filtering,
reports the removal count, and preserves whole tool names in its response
header. Context-window failures surface and fail closed.

### Select bridge direction explicitly

`use_chat_completions_url_for_anthropic_messages` routes compatible
`/v1/messages` calls through Chat Completions instead of Responses.
`route_all_chat_openai_to_responses` moves Chat Completions through the
Responses bridge. Both have corresponding `LITELLM_*` environment variables.

## Operations quick reference

### Separate coordination from response caching

Coordination Redis can be configured independently of response caching, and
the usage cache can be built from `REDIS_*` variables. The Redis circuit
breaker is enabled by default, opens after five consecutive failures, and
tries recovery after 60 seconds; environment variables override these values.

### Size database pools per worker

`database_connection_pool_limit` applies to each worker. Total potential
connections equal instances multiplied by workers multiplied by this limit.
Connection-call, connection-open, and idle socket timeouts are distinct.

### Bound stalled and abandoned calls

Use `ttft_timeout` for a provider that never emits its first token and
`stream_idle_timeout` for long inter-token gaps.
`LITELLM_MAX_STREAMING_DURATION_SECONDS` caps total duration, while
`LITELLM_STREAM_INACTIVITY_TIMEOUT_SECONDS` catches keepalives without content.
`cancel_on_disconnect: true` cancels abandoned non-streaming upstream calls
and records them as 499.

## Working method

1. Determine whether the code uses the SDK, `Router`, Proxy, or a combination.
2. Read the relevant topic reference before changing configuration names or
   relying on defaults.
3. Verify provider-specific behavior against the project's pinned LiteLLM
   version and its tests.
4. Test failure paths: budget exhaustion, rate limits, timeouts, cooldowns,
   fallback category, Redis/database loss, and client disconnects.
5. In multi-instance deployments, confirm which state is shared through Redis
   and which remains process-local.
