# Keys, Budgets, and Governance

## Spend enforcement

### Spend-limit enforcement now throttles keys

Since 1.93.0, a key that exceeds its budget is rate-limited rather than
revoked. This breaks workflows that treated the spend limit as an immediate
hard block or revocation event. Explicitly revoke or rotate a key when policy
requires invalidating its credential.

### Tag-scoped budgets

Tag budgets require PostgreSQL and are created separately with `/tag/new`.
Attach tags to a virtual key through top-level `tags` or `metadata.tags`, or
send `metadata.tags` or `x-litellm-tags` on a request. A multi-tag request is
charged to every tag and is rejected if any attached tag is over budget.

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

### Team defaults and wall-clock budget resets

`default_team_params` fills only values omitted from `/team/new`, including
teams created through SSO. Its `models` field applies only to SSO-created
teams. In releases after v1.94.0rc1, a quoted `budget_reset_time` selects the
reset wall-clock time in the configured timezone. A malformed value stops
startup, and a budget shorter than one day ignores this setting.

```yaml
litellm_settings:
  default_team_params:
    max_budget: 100
    budget_duration: 30d
    models: [chat]
  budget_reset_time: "09:00"
```

### Temporary key-budget increases

`/key/update` can raise a budget temporarily without modifying the permanent
base budget. Supply both `temp_budget_increase` and `temp_budget_expiry`.

```json
{
  "key": "sk-existing",
  "temp_budget_increase": 100,
  "temp_budget_expiry": "10d"
}
```

## Key identity and access

### Per-key model aliases

A virtual key can expose a client-facing model name while allowing only a
configured model group. Include both `models` and the key-specific `aliases`
map when generating it.

```json
{
  "models": ["free-tier"],
  "aliases": {"legacy-chat": "free-tier"},
  "duration": "30min"
}
```

### Alternate virtual-key header

`general_settings.litellm_key_header_name` moves virtual-key authentication
out of `Authorization`, leaving that header available for an upstream gateway.
The custom header value still has the form `Bearer <key>`.

```yaml
general_settings:
  master_key: sk-admin
  litellm_key_header_name: X-Litellm-Key
```

### Key-derived upstream user identity

From v1.95.0-rc.1, `overwrite_user_with_key_hash: true` replaces an outgoing
chat-completions `user` with the virtual key's SHA-256 hash, or a fixed alias
for the master key, even if the caller supplied a value. It does not change
custom-auth or JWT requests.

### JWT team-membership fallback

Since 1.93.0, if a JWT has no team claims, proxy authentication falls back to
the user's database-backed team memberships.

### Tenant-isolation defaults

Responses IDs are tied to user information by default;
`disable_responses_id_security` removes this cross-user protection. Non-admin
`/spend/keys` and `/spend/users` results are caller-scoped by default;
`legacy_unscoped_spend_list_endpoints` restores the old global view.
`reject_clientside_metadata_tags` prevents callers from changing budget
attribution through request-supplied tags.

## Key generation and rotation

### Custom key-generation veto

`general_settings.custom_key_generate` loads an async callback before
`/key/generate`. It receives a `GenerateKeyRequest`. Return
`{"decision": true}` to allow creation, or
`{"decision": false, "message": "..."}` to deny it.

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

### Key-generation defaults and upper bounds

`default_key_generate_params` fills omitted `/key/generate` values.
`upperbound_key_generate_params` clamps requested values to administrative
ceilings rather than rejecting the request.

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

### Role and parameter restrictions for key generation

`key_generation_settings` separately governs team and personal key creation.
Each scope can allow roles and require fields such as `tags`, enforcing cost
attribution on user-created keys.

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

### Manual key regeneration with cutover

The enterprise `POST /key/{key}/regenerate` endpoint rotates a key and can
change its parameters. `grace_period` keeps the old and new strings valid
during cutover. Omitting it or sending an empty value immediately revokes the
old string.

```http
POST /key/sk-old/regenerate
Authorization: Bearer <master-key>
Content-Type: application/json

{"models":["standard-chat"],"max_budget":100,"grace_period":"48h"}
```

### Automatic virtual-key rotation

`LITELLM_KEY_ROTATION_ENABLED` is off by default. When enabled, the job checks
every 86,400 seconds and uses a 600-second distributed lock by default.
`LITELLM_KEY_ROTATION_GRACE_PERIOD` accepts a duration such as `24h`; an empty
value revokes the old key immediately.

## Authentication and policy checks

### Shared virtual-key auth cache

`litellm_settings.enable_redis_auth_cache` shares virtual-key authentication
payloads between workers through the response-cache Redis client. It requires
`cache: true` and `cache_params.type: redis`.
`general_settings.user_api_key_cache_ttl` can align memory and Redis TTLs.

### Fail-closed authentication and budget checks

`custom_auth_run_common_checks` defaults to `false`. Enable it to apply model
allowlists, budgets, and rate limits after custom authentication.
`fail_closed_budget_enforcement` also defaults off; when enabled, each
budgeted request is checked against the database and returns 503 when neither
Redis nor the database can establish spend. `allow_requests_on_db_unavailable`
deliberately permits a request whose virtual key cannot be checked and is
intended only for private-network deployments.

## Teams and administration

### Team, key, and CLI management additions

Since 1.93.0, organization administrators can update a team with
`PATCH /team/{team_id}` using JSON merge-patch semantics, and `GET /key/list`
accepts an `expires` filter. `lite auth print-token` produces a token suitable
for Claude Code's `apiKeyHelper`. The Microsoft Graph endpoint can be changed
for GCC High deployments.

### Team lifecycle hooks

Since 1.97.0, a custom metadata-validation hook can run during team creation
and update. Calling `disable_logging` from a team callback now stops logging as
requested.

### Spend reports

Since 1.97.0, caller-scoped spend-report endpoints cover keys, users, teams,
and organizations.
