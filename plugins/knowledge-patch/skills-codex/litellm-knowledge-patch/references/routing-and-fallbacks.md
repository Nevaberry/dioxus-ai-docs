# Routing, Rate Limits, and Fallbacks

## Rate-limit enforcement and accounting

### Per-tag and token-direction rate limits

Since 1.93.0, one key can enforce RPM limits per tag, and Router deployments
can constrain input TPM and output TPM separately. A local rate-limit error
can enter gateway fallback handling.

### Strict deployment rate-limit enforcement

Deployment `rpm` and `tpm` values normally guide routing; they do not hard
block traffic. Add `enforce_model_rate_limits` to pre-call checks to reject an
over-limit request before provider dispatch with 429 and `retry-after: 60`.
RPM is exact. TPM is best-effort because actual usage is recorded after the
response. Multiple proxy instances require shared Redis state.

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

### TPM reservation mode

The v3 rate limiter reserves TPM before a call by default. Set
`LITELLM_TPM_TOKEN_RESERVATION_ENABLED=false` to skip the reservation and
enforce TPM after the call from actual usage only.

## Model-group selection

### Hidden model-group aliases

Use an object alias with `hidden: true` to accept a request name without
advertising it through `/v1/models`, `/v1/model/info`, or
`/v1/model_group/info`.

```yaml
router_settings:
  model_group_alias:
    legacy-chat:
      model: chat
      hidden: true
```

### Per-model routing groups

`routing_groups` gives model-name sets separate strategies and arguments in a
single Router. A model can occur in only one group, `default` is reserved, and
ungrouped models use the top-level strategy. Updating
`Router.update_settings(routing_groups=[...])` or `/config/update` rebuilds
group state at runtime.

```yaml
router_settings:
  routing_strategy: simple-shuffle
  routing_groups:
    - group_name: latency-sensitive
      models: [premium-chat]
      routing_strategy: latency-based-routing
      routing_strategy_args: {ttl: 60}
```

### Silent traffic mirroring

The Router can mirror production requests to a secondary model for evaluation.
It collects the secondary response in the background without changing the
primary response or adding secondary latency to it.

### Ordered deployment tiers

Set `order` under `litellm_params`; lower values run first. The selected
strategy balances deployments tied within a tier. A tier receives its retries
before the next tier is promoted, and model-level `fallbacks` begin only after
every order tier is exhausted.

```yaml
model_list:
  - model_name: chat
    litellm_params: {model: provider/chat-primary, order: 1}
  - model_name: chat
    litellm_params: {model: provider/chat-secondary, order: 2}
```

### Async weighted failover within a model group

With `simple-shuffle`, `enable_weighted_failover` lets an async call exclude a
failed deployment and choose another same-group peer using current weights and
rate limits before crossing to `fallbacks`. `max_fallbacks` caps attempts and
defaults to 5. This does not apply to synchronous calls. Context-window and
content-policy failures stay on their dedicated fallback paths.

```yaml
router_settings:
  routing_strategy: simple-shuffle
  enable_weighted_failover: true
```

### Team-scoped stale-alias migration

Request team deployments through `model_info.team_public_model_name` so every
sibling deployment participates in ordering and failover. A legacy team
`model_aliases` row can rewrite that public name to one internal deployment.
Remove the obsolete database alias, or temporarily set
`LITELLM_ENABLE_TEAM_STALE_ALIAS_BYPASS=true` during an upgrade.

## Affinity and health

### Encrypted-content affinity for Responses

Encrypted Responses items such as `rs_...` can continue only through the
deployment key that created them. Assign distinct `model_info.id` values and
enable the affinity check; ordinary requests remain load-balanced.

```yaml
router_settings:
  optional_pre_call_checks:
    - encrypted_content_affinity
```

### Deployment and session affinity

`deployment_affinity` and `session_affinity` provide sticky routing separately
from encrypted-response affinity. `deployment_affinity_ttl_seconds` defaults
to 3600. `model_group_affinity_config` can choose checks for individual model
groups; groups absent from it inherit the global checks.

```yaml
router_settings:
  optional_pre_call_checks: [deployment_affinity]
  deployment_affinity_ttl_seconds: 3600
  model_group_affinity_config:
    batch: [session_affinity]
```

### Shared health-aware routing

`enable_health_check_routing` removes unhealthy deployments from selection.
`health_check_staleness_threshold` expires old results, and
`health_check_ignore_transient_errors` prevents 408 and 429 probes from
affecting routing or cooldown. `use_shared_health_check` stores health state in
Redis for a multi-instance proxy.

## Retries, cooldowns, and fallback routes

### Retry sequencing, cooldowns, and fallback routes

The Router has distinct ordered routes for context-window errors,
content-policy violations, and all other errors. It consumes `num_retries`
before crossing to another model group. `request_timeout` bounds an attempt;
`allowed_fails` and `cooldown_time` control deployment removal. A specific
model fallback mapping overrides `default_fallbacks`.

```python
router = Router(
    model_list=model_list,
    fallbacks=[{"chat": ["backup"]}],
    context_window_fallbacks=[{"chat": ["long-context"]}],
    content_policy_fallbacks=[{"chat": ["policy-backup"]}],
)
```

```yaml
litellm_settings:
  num_retries: 3
  request_timeout: 10
  allowed_fails: 3
  cooldown_time: 30
  default_fallbacks: [emergency]
```

### Request-scoped fallback inputs

SDK and proxy requests can provide `fallbacks`. An object fallback can replace
the model, messages, temperature, and other parameters for its attempt. The
same form works for operations such as embeddings and image generation.

```python
response = client.chat.completions.create(
    model="chat",
    messages=[{"role": "user", "content": "Summarize this."}],
    extra_body={"fallbacks": [{
        "model": "backup",
        "messages": [{"role": "user", "content": "Give a short summary."}],
        "temperature": 0,
    }]},
)
```

### Pre-call context-window enforcement

Set `router_settings.enable_pre_call_checks: true` to filter undersized peers
or reject oversized input before provider dispatch. A deployment-level
`model_info.max_input_tokens` overrides the known limit. If the deployment
name hides its provider model, also set `model_info.base_model`. If nothing
fits, `ContextWindowExceededError` can select `context_window_fallbacks`.

```yaml
router_settings:
  enable_pre_call_checks: true
model_list:
  - model_name: chat
    litellm_params:
      model: provider/chat
    model_info:
      max_input_tokens: 8000
```

### Region-aware pre-call filtering

Pre-call checks can filter by region. Set `litellm_params.region_name` when an
integration cannot infer it; location-bearing provider parameters may supply
it automatically.

```yaml
router_settings:
  enable_pre_call_checks: true
model_list:
  - model_name: chat
    litellm_params:
      model: provider/chat
      region_name: eu
```

### Exact-deployment fallback targets

A fallback target can name `model_info.id` instead of a model group. This
selects only that deployment and deliberately bypasses its cooldown check.
The response header `x-litellm-model-id` identifies the serving deployment.

```yaml
model_list:
  - model_name: chat
    litellm_params:
      model: provider/emergency-chat
    model_info:
      id: emergency-deployment
litellm_settings:
  fallbacks: [{"chat": ["emergency-deployment"]}]
```

### Wildcard model fallback targets

A wildcard deployment such as `provider/*` makes concrete provider-prefixed
names valid fallback targets without listing each deployment.

```yaml
model_list:
  - model_name: "provider/*"
    litellm_params:
      model: "provider/*"
litellm_settings:
  fallbacks: [{"chat": ["provider/backup-chat"]}]
```

### Per-request and per-key opt-out

Set `disable_fallbacks: true` in a proxy request to suppress failover for that
call. Store the same flag in virtual-key metadata to suppress it for every
request made with that key.

```json
{"model": "chat", "messages": [], "disable_fallbacks": true}
```

```json
{"metadata": {"disable_fallbacks": true}}
```

### Proxy fallback-test flags are ignored

Since Proxy v1.85.0, incoming `mock_testing_fallbacks`,
`mock_testing_context_fallbacks`, and
`mock_testing_content_policy_fallbacks` are stripped. They remain available
only for direct `Router` calls. Test proxy fallbacks by producing a real
provider error outside production.

## Stall detection

### Stall-specific timeout controls

Router `ttft_timeout` detects a provider that never emits its first token and
internally streams even a non-streaming call. `stream_idle_timeout` detects
long gaps between tokens. `LITELLM_MAX_STREAMING_DURATION_SECONDS` caps total
stream life; `LITELLM_STREAM_INACTIVITY_TIMEOUT_SECONDS` catches an async
provider that sends keepalives without content chunks.

## Auto-routing

### Complexity auto-router classifiers

Since 1.93.0, the complexity router supports keyword tier overrides, semantic
keyword matching, custom technical keywords, and an optional LLM classifier.
It can emit a log for each routing decision.

### Complexity and auto-router controls

Since 1.97.0, complexity-router session affinity defaults to off and is
visible in the UI. Operators can rename all four tiers, configure the reminder
marker pair, replace the LLM-classifier system prompt, and test routing from
the auto-router creation form.

### Auto-router savings reports

Since 1.97.0, cost optimization reports net savings, use the hardest tier as
the default baseline, and aggregate benchmarks per session.
