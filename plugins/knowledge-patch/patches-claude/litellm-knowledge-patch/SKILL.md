---
name: litellm-knowledge-patch
description: LiteLLM
version: "1.93.0"
license: MIT
metadata:
  author: Nevaberry
---


# LiteLLM Knowledge Patch

Use this skill when configuring, upgrading, or operating LiteLLM SDK, Router,
or Proxy deployments. Start with the breaking-behavior checklist, then load the
topic reference that matches the task. Prefer the application's pinned version,
configuration, and observed behavior when they differ from this guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [deployment-configuration.md](references/deployment-configuration.md) | Config discovery, credentials, database pools and replicas, runtime support, image verification, environment exposure, prompt framing, and tokenizers |
| [identity-budgets-and-keys.md](references/identity-budgets-and-keys.md) | Authentication, teams, virtual keys, aliases, budgets, rotation, spend reports, and key-generation policy |
| [operations-and-observability.md](references/operations-and-observability.md) | Telemetry, health state, Redis coordination, draining, timeouts, rate limiting, reporting, and Admin UI operations |
| [providers-protocols-and-mcp.md](references/providers-protocols-and-mcp.md) | Provider/model support, protocol bridges, A2A, MCP authentication and filtering, guardrails, and response normalization |
| [proxy-security-and-networking.md](references/proxy-security-and-networking.md) | SSRF defenses, request validation, tenant isolation, explicit grants, network controls, hardening, and signed images |
| [routing-and-resilience.md](references/routing-and-resilience.md) | Routing groups, tiering, failover, fallbacks, pre-call checks, affinity, auto-routing, mirroring, and health filtering |

## Breaking-behavior checklist

### Spend limits throttle instead of revoking

A virtual key that exceeds its budget is rate-limited; it is no longer revoked.
Do not use key-revocation state as the signal that a spend limit was reached.
Update automation to recognize the rate-limit response and preserve the key for
the next reset period.

### Request-parameter checks cover every input location

Parameter policy now checks body, path, and form values consistently. A request
that previously bypassed a restriction by moving a value out of the JSON body
may now be rejected. Exercise all endpoint encodings during an upgrade.

### Provider `finish_reason=error` becomes `stop`

The generic provider adapter normalizes an `error` finish reason to `stop`.
Clients that need error detection must use the request status, exception, or
other error metadata rather than the original finish-reason string.

### Telemetry attribute names changed

Move queries for LiteLLM-specific errors to the `litellm.*` namespace.
Streaming spans use `gen_ai.response.time_to_first_chunk`, failed calls emit
`gen_ai.client.operation.exception`, and v2 error spans expose `error.*` again.

### Custom authentication does not imply common checks

`custom_auth_run_common_checks` defaults to `false`. Enable it when custom-auth
requests must still pass model allowlists, budgets, and rate limits.

```yaml
general_settings:
  custom_auth_run_common_checks: true
```

### Proxy mock fallback flags do nothing

The Proxy strips `mock_testing_fallbacks`,
`mock_testing_context_fallbacks`, and
`mock_testing_content_policy_fallbacks`. Direct `Router` calls may still use
them. Test Proxy fallback behavior by causing a real provider failure in an
isolated environment.

## Routing quick reference

### Enforce deployment rate limits

Deployment `rpm` and `tpm` normally influence selection rather than blocking
traffic. Add the pre-call check to reject excess traffic with HTTP 429 and
`retry-after: 60`.

```yaml
model_list:
  - model_name: chat
    litellm_params:
      model: provider/chat
      rpm: 60
      tpm: 90000
router_settings:
  optional_pre_call_checks: [enforce_model_rate_limits]
```

RPM enforcement is exact. TPM is best-effort because actual usage is recorded
after the response. Share Redis state across Proxy instances.

### Understand retry and fallback order

The Router exhausts `num_retries` before moving to another model group. It has
separate ordered routes for context-window, content-policy, and other errors.
A model-specific fallback mapping wins over `default_fallbacks`.

```yaml
litellm_settings:
  num_retries: 3
  request_timeout: 10
  allowed_fails: 3
  cooldown_time: 30
  default_fallbacks: [emergency]
```

`request_timeout` bounds one attempt. `allowed_fails` and `cooldown_time`
control when a deployment leaves selection and for how long.

### Use ordered deployment tiers

Set `order` in `litellm_params`; lower numbers run first. The configured
strategy balances deployments tied within a tier. Each tier receives its
retries before promotion, and model-level fallbacks run only after every tier.

```yaml
model_list:
  - model_name: chat
    litellm_params: {model: provider/primary, order: 1}
  - model_name: chat
    litellm_params: {model: provider/secondary, order: 2}
```

### Enable context-window checks explicitly

Set `router_settings.enable_pre_call_checks: true` to filter undersized
same-group deployments and raise `ContextWindowExceededError` before sending a
request. Set `model_info.max_input_tokens` when discovery is insufficient and
`model_info.base_model` when the deployment name hides the underlying model.

```yaml
router_settings:
  enable_pre_call_checks: true
model_list:
  - model_name: chat
    litellm_params: {model: provider/chat}
    model_info:
      max_input_tokens: 8000
```

### Preserve encrypted-response affinity

Encrypted Responses items can only continue on the deployment key that created
them. Give deployments unique `model_info.id` values and enable:

```yaml
router_settings:
  optional_pre_call_checks: [encrypted_content_affinity]
```

Ordinary requests remain load-balanced.

## Security quick reference

### Keep URL validation enabled

`litellm_settings.user_url_validation` defaults to `true` and blocks fetches
whose DNS result is private, loopback, link-local, or otherwise non-global.
Allowlisted hosts must exactly match the URL hostname, including its port. For
split-horizon DNS, allowlist the public hostname, not its private address.

### Choose fail-open or fail-closed budgets deliberately

`fail_closed_budget_enforcement` defaults off. When enabled, every budgeted
request is verified against the database and returns 503 if neither Redis nor
the database can establish spend. `allow_requests_on_db_unavailable` permits an
unchecked key and is suitable only for private-network deployments.

### Preserve tenant isolation defaults

Responses IDs are user-bound by default. Do not set
`disable_responses_id_security` unless cross-user access is intentional.
Non-admin spend-list endpoints are caller-scoped; use
`legacy_unscoped_spend_list_endpoints` only for a controlled migration. Enable
`reject_clientside_metadata_tags` to prevent callers from changing budget tags.

### Harden the deployment surface

HSTS is opt-in with `LITELLM_ENABLE_HSTS` and applies only over HTTPS.
`DISABLE_ADMIN_UI`, `NO_DOCS`, `NO_OPENAPI`, and `NO_REDOC` independently
remove interfaces. Secret redaction defaults on; do not set
`LITELLM_DISABLE_REDACT_SECRETS=true` unless logs are otherwise protected.

## Identity and budget quick reference

### Configure tag budgets as independent objects

Tag budgets require PostgreSQL and are created with `/tag/new`. Attach tags to
a key or request. A multi-tag request is charged to every tag and is rejected
when any one tag is over budget.

```json
{"name":"engineering","max_budget":500,"soft_budget":400,"budget_duration":"30d"}
```

### Apply key-generation defaults and ceilings

`default_key_generate_params` fills omitted fields.
`upperbound_key_generate_params` clamps requested values to administrative
ceilings rather than rejecting the request. Use `key_generation_settings` to
restrict team and personal key creation by role and require attribution fields.

### Rotate with an explicit cutover

`/key/{key}/regenerate` can update key parameters while rotating. Set
`grace_period` to keep old and new strings valid together; omit it or pass an
empty value to revoke the old string immediately.

## Operational quick reference

### Separate coordination Redis from response caching

Coordination Redis may be configured independently of the response cache. The
usage cache can be built from `REDIS_*` variables, and the request allowlist in
`general_settings` is applied to LiteLLM globals.

### Drain safely

`enable_drain_endpoint` exposes `GET /health/drain` for pre-stop hooks and is
off by default. Without `drain_endpoint_token` it is unauthenticated; with a
token, callers must send the matching `X-Drain-Token`. `cancel_on_disconnect`
cancels abandoned non-streaming upstream work and records status 499.

### Distinguish stall timeouts

`ttft_timeout` detects no first token and internally streams even a nominally
non-streaming call. `stream_idle_timeout` detects excessive inter-token gaps.
Use `LITELLM_MAX_STREAMING_DURATION_SECONDS` for total lifetime and
`LITELLM_STREAM_INACTIVITY_TIMEOUT_SECONDS` when keepalives arrive without
content chunks.

## Working method

1. Identify whether the task concerns SDK calls, direct `Router`, or Proxy.
2. Read the matching topic reference before changing configuration.
3. Check defaults and scope: global, model group, deployment, team, key, or
   request.
4. For multi-instance deployments, identify which state must be in Redis.
5. Test error paths, tenant boundaries, cooldowns, and upgrade-sensitive input
   locations in a non-production environment.
