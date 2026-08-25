# Identity, budgets, and virtual keys

## Spend-limit behavior

Since 1.93.0, a key over its budget is rate-limited rather than revoked. Treat
this as a throttling state and do not wait for key revocation as proof that the
spend limit was enforced.

## Rate limits by tag and token direction

A single key can enforce RPM limits per tag. Router deployments can limit input
TPM and output TPM separately. Local rate-limit failures may participate in
gateway fallbacks.

The v3 limiter reserves TPM before a call by default. Set
`LITELLM_TPM_TOKEN_RESERVATION_ENABLED=false` to skip reservation and enforce
TPM after the call using actual usage.

## Tag-scoped budgets

Tag budgets require PostgreSQL and are independent objects created with
`/tag/new`. Attach them to a key with top-level `tags` or `metadata.tags`, or to
a request through `metadata.tags` or `x-litellm-tags`. A request with several
tags is charged to all of them and rejected if any one is over budget.

```http
POST /tag/new
Authorization: Bearer <master-key>
Content-Type: application/json

{"name":"engineering","max_budget":500,"soft_budget":400,"budget_duration":"30d"}

POST /key/generate
Authorization: Bearer <master-key>
Content-Type: application/json

{"tags":["engineering","project-alpha"]}
```

## Team defaults and budget reset time

`default_team_params` fills only fields omitted from `/team/new`, including
SSO-created teams. Its `models` field applies only to SSO-created teams.

```yaml
litellm_settings:
  default_team_params:
    max_budget: 100
    budget_duration: 30d
    models: [chat]
  budget_reset_time: "09:00"
```

In releases after v1.94.0rc1, quoted `budget_reset_time` values choose the
wall-clock reset time in the configured timezone. Malformed values fail
startup, and sub-day budgets ignore the setting.

## Per-key model aliases

A key can expose a client-facing model name while restricting use to an allowed
model group. Supply both `models` and the key-specific `aliases` map.

```json
{
  "models": ["free-tier"],
  "aliases": {"legacy-chat": "free-tier"},
  "duration": "30min"
}
```

## Alternate authentication header

`general_settings.litellm_key_header_name` moves virtual-key authentication out
of `Authorization`, leaving that header for an upstream gateway. The custom
header value still has the `Bearer <key>` form.

```yaml
general_settings:
  master_key: sk-admin
  litellm_key_header_name: X-Litellm-Key
```

## Key-derived upstream user identity

From v1.95.0-rc.1, `overwrite_user_with_key_hash: true` replaces the outgoing
chat-completions `user` with the virtual key's SHA-256 hash, or with a fixed
master-key alias. It overrides a client-supplied value. Custom-auth and JWT
requests are unchanged.

## JWT team-membership fallback

When a JWT has no team claims, authentication falls back to the user's
database-backed team memberships.

## Fail-closed authentication and budget checks

`custom_auth_run_common_checks` defaults to `false`. Enable it to run model
allowlists, budgets, and rate limits after custom authentication.

`fail_closed_budget_enforcement` also defaults off. When enabled, every
budgeted request is checked against the database and returns 503 if neither
Redis nor the database can establish spend. `allow_requests_on_db_unavailable`
instead permits an unchecked virtual key and should be limited to private
networks.

## Tenant isolation and caller scoping

Responses IDs are user-bound by default; `disable_responses_id_security`
removes that protection. Non-admin `/spend/keys` and `/spend/users` output is
caller-scoped by default. `legacy_unscoped_spend_list_endpoints` restores the
old global view, and `reject_clientside_metadata_tags` prevents request tags
from changing budget attribution.

## Shared virtual-key auth cache

`litellm_settings.enable_redis_auth_cache` shares auth payloads across workers
using the response-cache Redis client. It requires `cache: true` and
`cache_params.type: redis`. Set `general_settings.user_api_key_cache_ttl` when
the memory and Redis caches should use the same TTL.

## Custom key-generation veto

`general_settings.custom_key_generate` loads an async callback before
`/key/generate`. It receives `GenerateKeyRequest`; return `decision: true` to
allow the request or `decision: false` with a message to deny it.

```python
async def custom_generate_key_fn(data: GenerateKeyRequest) -> dict:
    if data.team_id is None:
        return {"decision": False, "message": "team_id is required"}
    return {"decision": True}
```

```yaml
general_settings:
  custom_key_generate: custom_auth.custom_generate_key_fn
```

## Key-generation defaults and ceilings

`default_key_generate_params` fills omitted `/key/generate` fields, while
`upperbound_key_generate_params` clamps requests to administrative ceilings
instead of rejecting them.

```yaml
litellm_settings:
  default_key_generate_params:
    max_budget: 1.5
    models: [standard-chat]
    team_id: core-infra
  upperbound_key_generate_params:
    max_budget: 100
    budget_duration: 10d
    duration: 30d
    max_parallel_requests: 1000
    tpm_limit: 1000
    rpm_limit: 1000
```

## Key-generation role and parameter policy

`key_generation_settings` controls team and personal creation separately. Each
scope can allow roles and require fields such as `tags`.

```yaml
litellm_settings:
  key_generation_settings:
    team_key_generation:
      allowed_team_member_roles: [admin]
      required_params: [tags]
    personal_key_generation:
      allowed_user_roles: [proxy_admin]
      required_params: [tags]
```

## Manual regeneration and automatic rotation

The enterprise `/key/{key}/regenerate` endpoint rotates a key and may update
its parameters in the same call. `grace_period` keeps both strings valid during
cutover; omit it or pass an empty value to revoke the old string immediately.

```json
{"models":["standard-chat"],"max_budget":100,"grace_period":"48h"}
```

Automatic rotation is off by default. Enable it with
`LITELLM_KEY_ROTATION_ENABLED`; the job checks every 86,400 seconds and uses a
600-second distributed lock by default. `LITELLM_KEY_ROTATION_GRACE_PERIOD`
keeps the old key for a duration such as `24h`; an empty value revokes it.

## Temporary key-budget increases

`/key/update` can add a temporary amount without changing the base budget. Set
both `temp_budget_increase` and `temp_budget_expiry`.

```json
{
  "key": "sk-existing",
  "temp_budget_increase": 100,
  "temp_budget_expiry": "10d"
}
```

## Team and key administration

Organization admins can update a team with `PATCH /team/{team_id}` using JSON
merge-patch semantics. `GET /key/list` accepts an `expires` filter. `lite auth
print-token` can provide a token to an API-key helper, and the Microsoft Graph
endpoint can be configured for GCC High.

## Team lifecycle hooks

As of 1.97.0, a custom metadata-validation hook can run when a team is created
or updated. Calling `disable_logging` from a team callback now suppresses
logging as intended.

## Spend reports

Caller-scoped spend-report endpoints cover keys, users, teams, and
organizations. Auto-router cost reporting calculates net savings, chooses its
default baseline from the hardest tier, and aggregates benchmarks per session.
