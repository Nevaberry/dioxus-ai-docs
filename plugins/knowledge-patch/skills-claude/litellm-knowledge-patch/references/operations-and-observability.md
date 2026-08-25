# Operations and observability

## Telemetry attribute migration

Since 1.93.0, LiteLLM-specific error details use the `litellm.*` namespace, so
update queries that use the old keys. Streaming spans add
`gen_ai.response.time_to_first_chunk`, failed calls emit
`gen_ai.client.operation.exception`, and v2 error spans expose `error.*`
attributes again.

Inference spans in 1.97.0 include service-tier attributes, allowing traces to
distinguish the tier used by a request.

## Independent coordination Redis

Coordination Redis can be separate from the response cache. The usage cache can
be constructed from `REDIS_*` environment variables. The request allowlist
under `general_settings` is also applied to LiteLLM globals.

## Redis circuit breaker

The Redis circuit breaker defaults on. It opens after five consecutive
failures and tries recovery after 60 seconds. Override the behavior with:

- `REDIS_CIRCUIT_BREAKER_ENABLED`
- `REDIS_CIRCUIT_BREAKER_FAILURE_THRESHOLD`
- `REDIS_CIRCUIT_BREAKER_RECOVERY_TIMEOUT`

## Shared health-aware routing

`enable_health_check_routing` filters unhealthy deployments.
`health_check_staleness_threshold` expires old results, while
`health_check_ignore_transient_errors` prevents HTTP 408 and 429 probe results
from changing routing or cooldown. `use_shared_health_check` keeps the health
state in Redis for multi-instance Proxy deployments.

## Graceful drain and disconnect cancellation

`enable_drain_endpoint` exposes `GET /health/drain` for pre-stop hooks and is
off by default. Without `drain_endpoint_token`, the endpoint is unauthenticated;
when a token is set, require the matching `X-Drain-Token`.

`cancel_on_disconnect: true` cancels a non-streaming provider request after the
client disconnects and records the cancellation as status 499.

## Request, response, and pass-through bounds

`max_request_size_mb` rejects oversized requests.
`max_response_size_mb` prevents oversized model responses from being sent.
`pass_through_request_timeout` separately limits custom and native-provider
pass-through calls and defaults to 600 seconds; an endpoint-specific timeout
wins.

## Stall-specific timeout controls

Router `ttft_timeout` detects a provider that never emits its first token and
internally streams even a non-streaming call. `stream_idle_timeout` detects
excessive gaps between tokens.

`LITELLM_MAX_STREAMING_DURATION_SECONDS` caps total stream lifetime.
`LITELLM_STREAM_INACTIVITY_TIMEOUT_SECONDS` catches an async provider that
sends keepalives without content chunks.

## Outbound HTTP transport controls

The aiohttp transport ignores `HTTP_PROXY` and `HTTPS_PROXY` by default. Set
`AIOHTTP_TRUST_ENV=true` to use them. Connector limits default to unlimited
(`0`). Socket keepalive defaults off; when enabled with
`AIOHTTP_SO_KEEPALIVE`, idle, interval, and probe-count settings default to 60
seconds, 30 seconds, and 5 probes respectively.

## Deployment rate-limit enforcement

Deployment `rpm` and `tpm` guide routing unless
`enforce_model_rate_limits` is in `optional_pre_call_checks`. With the check,
over-limit calls fail before the provider with HTTP 429 and `retry-after: 60`.
RPM is exact; TPM is best-effort because actual usage is recorded after the
response. Use shared Redis state across Proxy instances.

## Admin UI operations

In 1.97.0, the Playground can send non-streaming requests. Administrators can
configure a user-facing banner. The auto-router creation form includes a
routing test action and exposes its expanded complexity controls.

The Admin UI build toolchain targets Node.js 24, with bootstrap selecting that
dashboard version floor through nvm or fnm.

## Cost and routing reports

Caller-scoped spend-report endpoints are available for keys, users, teams, and
organizations. Auto-router cost optimization reports net savings, uses the
hardest tier as its default baseline, and rolls benchmarks up by session.
