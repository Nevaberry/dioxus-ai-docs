# Routing and resilience

## Complexity auto-router classifiers

Since 1.93.0, the complexity router supports keyword-based tier overrides,
semantic keyword matching, custom technical keywords, and an optional LLM
classifier. It can emit a routing log for every decision.

In 1.97.0, complexity-router session affinity defaults off and is configurable
in the UI. Operators can rename all four tiers, configure the reminder marker
pair, replace the classifier system prompt, and test routing from the
auto-router creation form.

## Strict deployment limits

Deployment `rpm` and `tpm` guide selection unless `enforce_model_rate_limits`
is enabled as a pre-call check. The check rejects an over-limit request before
the provider with HTTP 429 and `retry-after: 60`.

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

RPM is exact; TPM is best-effort because usage is recorded after the response.
Multiple Proxy instances require shared Redis state.

## Hidden model-group aliases

Use the object alias form with `hidden: true` to accept another request name
without listing it in `/v1/models`, `/v1/model/info`, or
`/v1/model_group/info`.

```yaml
router_settings:
  model_group_alias:
    legacy-chat:
      model: chat
      hidden: true
```

## Per-model routing groups

`routing_groups` applies different strategies and arguments to different sets
of `model_name` values within one Router. A model can belong to only one group,
`default` is reserved, and ungrouped models use the top-level strategy.
`Router.update_settings(routing_groups=[...])` and `/config/update` rebuild
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

## Silent request mirroring

The Router can mirror production requests to a secondary model for evaluation.
It collects the secondary response in the background without changing the
primary response or its latency.

## Ordered deployment tiers

Set `order` in `litellm_params`; lower values are attempted first. The routing
strategy balances deployments tied within a tier. Each tier receives its
retries before the next tier, and model-level `fallbacks` run only after every
order tier has been exhausted.

```yaml
model_list:
  - model_name: chat
    litellm_params: {model: provider/chat-primary, order: 1}
  - model_name: chat
    litellm_params: {model: provider/chat-secondary, order: 2}
```

## Async weighted failover

With `simple-shuffle`, `enable_weighted_failover` makes an async call exclude a
failed deployment and reselect another same-group peer using current weights
and rate limits before moving to `fallbacks`. It is limited by `max_fallbacks`,
whose default is 5. It does not apply to synchronous calls; context-window and
content-policy errors keep their dedicated routes.

```yaml
router_settings:
  routing_strategy: simple-shuffle
  enable_weighted_failover: true
```

## Team-scoped stale-alias migration

Request team deployments through `model_info.team_public_model_name` so sibling
deployments all take part in ordering and failover. A legacy team
`model_aliases` entry may rewrite the public name to one internal deployment.
Remove the obsolete database alias, or temporarily set
`LITELLM_ENABLE_TEAM_STALE_ALIAS_BYPASS=true` while upgrading.

## Encrypted-content affinity

Encrypted Responses items such as `rs_...` can only continue on the deployment
key that created them. Give each deployment a distinct `model_info.id` and
enable the affinity check. Ordinary calls remain load-balanced.

```yaml
router_settings:
  optional_pre_call_checks:
    - encrypted_content_affinity
```

## Retry, cooldown, and fallback order

The Router has distinct ordered routes for context-window errors,
content-policy violations, and all remaining errors. It exhausts `num_retries`
before moving to another group. `request_timeout` bounds each attempt;
`allowed_fails` and `cooldown_time` decide when and for how long a failed
deployment is removed. A model-specific mapping takes precedence over
`default_fallbacks`.

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

## Request-scoped fallback inputs

SDK and Proxy requests can pass their own `fallbacks`. The object form can
replace model, messages, temperature, and other values for that attempt. It
also applies to operations such as embeddings and image generation.

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

## Pre-call context-window enforcement

Set `router_settings.enable_pre_call_checks: true` to remove undersized
same-group deployments or reject oversized input before provider submission.
`model_info.max_input_tokens` overrides a known limit. When a deployment name
hides its provider model, also set `model_info.base_model`. If no deployment
fits, `ContextWindowExceededError` allows `context_window_fallbacks` to select a
larger group.

```yaml
router_settings:
  enable_pre_call_checks: true
model_list:
  - model_name: chat
    litellm_params: {model: provider/chat}
    model_info:
      max_input_tokens: 8000
```

## Region-aware pre-call filtering

Pre-call checks can filter by region. Set `litellm_params.region_name` when the
provider integration cannot infer it; integrations with location-bearing
parameters may infer the region automatically.

```yaml
router_settings:
  enable_pre_call_checks: true
model_list:
  - model_name: chat
    litellm_params:
      model: provider/chat
      region_name: eu
```

## Exact-deployment fallback targets

A fallback may target `model_info.id` instead of a model group. This selects
only that deployment and intentionally skips its cooldown check. The response
header `x-litellm-model-id` identifies the serving deployment.

```yaml
model_list:
  - model_name: chat
    litellm_params: {model: provider/emergency-chat}
    model_info: {id: emergency-deployment}
litellm_settings:
  fallbacks: [{"chat": ["emergency-deployment"]}]
```

## Wildcard model fallbacks

A wildcard deployment such as `provider/*` makes concrete prefixed names valid
fallback targets without enumerating them.

```yaml
model_list:
  - model_name: "provider/*"
    litellm_params: {model: "provider/*"}
litellm_settings:
  fallbacks: [{"chat": ["provider/backup-chat"]}]
```

## Fallback opt-out

Put `disable_fallbacks: true` in one Proxy request to suppress failover for that
call. Store the same flag in virtual-key `metadata` to suppress failover for
every call made with that key.

```json
{"model":"chat","messages":[],"disable_fallbacks":true}
```

## Proxy fallback testing

Since Proxy v1.85.0, incoming `mock_testing_fallbacks`,
`mock_testing_context_fallbacks`, and
`mock_testing_content_policy_fallbacks` are stripped. They remain available for
direct `Router` calls. Proxy tests must cause a real provider error in a
non-production environment.

## Shared health routing

`enable_health_check_routing` removes unhealthy deployments.
`health_check_staleness_threshold` expires old observations, and
`health_check_ignore_transient_errors` keeps 408 and 429 probes from affecting
routing or cooldown. `use_shared_health_check` stores health in Redis for
multiple Proxy instances.

## Provider-stall timeouts

`ttft_timeout` catches a provider that never emits its first token and
internally streams a nominally non-streaming call. `stream_idle_timeout` catches
long gaps between tokens. `LITELLM_MAX_STREAMING_DURATION_SECONDS` caps total
stream duration, while `LITELLM_STREAM_INACTIVITY_TIMEOUT_SECONDS` catches
async keepalives with no content chunks.

## Deployment and session affinity

`deployment_affinity` and `session_affinity` are pre-call checks independent of
encrypted-response affinity. `deployment_affinity_ttl_seconds` defaults to
3600. `model_group_affinity_config` can choose checks for specific groups;
unlisted groups inherit global checks.

```yaml
router_settings:
  optional_pre_call_checks: [deployment_affinity]
  deployment_affinity_ttl_seconds: 3600
  model_group_affinity_config:
    batch: [session_affinity]
```

## Auto-router savings reporting

Cost optimization reports net savings, derives its default baseline from the
hardest complexity tier, and aggregates benchmarks per session.
