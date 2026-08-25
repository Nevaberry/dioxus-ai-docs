# Platforms, Discovery, and Limits

This reference consolidates platform and administration guidance from
`release-lifecycle`, `rate-limits`, and `2026-08-01-2026-08-19`.

## Identity and inference location

Workload Identity Federation is generally available. Configure OIDC issuers
and federation rules in the Console, then let an SDK exchange and refresh
short-lived credentials instead of distributing static API keys.

For models released after February 1, 2026, `inference_geo` can request US-only
inference at 1.1x pricing. For Managed Agents, place it in the agent's `model`
object or override it for one session.

## Distinguish AWS-hosted surfaces

Claude Platform on AWS uses Anthropic-managed infrastructure with AWS billing
and IAM. It exposes Messages, Files, Message Batches, Managed Agents, Agent
Skills, code execution, and tool use through native AWS endpoints.

Amazon Bedrock's `/anthropic/v1/messages` uses the first-party Messages request
shape on AWS-managed infrastructure. Opus 4.7 and Haiku 4.5 are self-serve
there through global and regional endpoints. Do not transfer assumptions about
model IDs, caching, billing, limits, or available betas between the two
surfaces.

## Discover models and limits

Use `GET /v1/models` or `GET /v1/models/{model_id}` to read
`max_input_tokens`, `max_tokens`, and `capabilities`. Avoid hard-coded limits.
Opus 4.6 and Sonnet 4.6 can request a 300k single-turn output cap with:

```text
Anthropic-Beta: output-300k-2026-03-24
```

Responses include `anthropic-workspace-id`. Its `wrkspc_`-prefixed value
identifies the workspace resolved from the API key or access token, including
the Default Workspace. Record it when diagnosing workspace-scoped behavior.

## MCP tunnel route migration

Tunnel management moved from the Admin API route
`/v1/organizations/tunnels` to `/v1/tunnels` on the Claude API. The new route
requires the `mcp-tunnels-2026-06-22` beta header and the
`workspace:manage_tunnels` Workload Identity Federation scope. The old route is
available only during a migration window.

## Rate-limit mechanics

### Continuous and acceleration throttles

The Messages API independently limits requests per minute, input tokens per
minute, and output tokens per minute with continuously replenished token
buckets. Enforcement can occur over sub-minute windows. A rapid traffic ramp
may produce an acceleration-limit 429 even when a steady-state calculation
looks acceptable. Ramp gradually and obey `retry-after`.

### Monthly spend caps

| Usage tier | Calendar-month API spend cap |
| --- | ---: |
| Start | $500 |
| Build | $1,000 |
| Scale | $200,000 |

Reaching the cap pauses API use until the next month unless it is raised.
Custom-tier organizations have no standard monthly cap. Any organization may
set a lower self-imposed cap.

### AWS-billed tier handling

Claude Platform on AWS organizations begin on Start and do not automatically
advance through usage tiers. Billing uses AWS Marketplace and spend limits are
under Billing rather than Limits. Arrange higher limits through an account
representative or support; the normal increase-request flow is unavailable.

### Cache-aware token accounting

For most models, input TPM usage is
`input_tokens + cache_creation_input_tokens`; cache reads are excluded.
`input_tokens` is only content after the final breakpoint, while total input is
`cache_read_input_tokens + cache_creation_input_tokens + input_tokens`. Haiku
3.5 is the exception that also charges cache reads against input TPM.

Input TPM is estimated at request start and corrected to actual input during
processing. Output TPM is charged in real time for generated tokens; requested
`max_tokens` does not reserve output capacity.

### Shared model-family pools

Most models have independent limits, with these shared or separate pools:

- Opus 4.5 through 4.8 share one Opus 4.x pool.
- Sonnet 4.5 and 4.6 share one Sonnet 4.x pool.
- Opus 5 and Sonnet 5 each have separate pools.
- `inference_geo: "us"` and `"global"` draw from the same capacity.

### Message Batches and Managed Agents

Message Batches have a model-independent pool of 1,000 API requests per minute,
at most 200,000 constituent requests awaiting successful processing, and at
most 100,000 constituent requests in one batch. Each constituent item occupies
queue capacity, not just its enclosing batch.

Managed Agents use a separate organization-level pool: create operations allow
300 requests per minute, while retrieve, list, stream, and other read operations
allow 1,200 requests per minute.

### Dedicated fast-mode pool

Supported `speed: "fast"` requests use a dedicated pool rather than the
standard Opus pool. Throttling returns 429 plus `retry-after`; inspect the
`anthropic-fast-*` response headers for pool state.

### Workspace safeguards

A non-default workspace can set lower RPM, input TPM, output TPM, and spend
ceilings. An unset limiter inherits the organization limit. Unused workspace
capacity remains available elsewhere. The Default Workspace cannot be capped,
and organization limits still apply when configured workspace limits sum above
them.

### Response headers

`retry-after` gives the seconds until a retry can succeed. The response also
contains these families:

```text
anthropic-ratelimit-{requests|tokens|input-tokens|output-tokens}-{limit|remaining|reset}
```

Reset fields are RFC 3339 timestamps for full bucket replenishment. Remaining
token counts are rounded to the nearest thousand.

## Enterprise user administration

Member, invite, group, and custom-role Admin API endpoints are generally
available. Group and custom-role calls no longer require
`ce-user-management-2026-07-13`; sending that beta header remains accepted.
Member and invite calls likewise need no beta header.

An Admin key with `read:org_audit` may call all user-management `GET` routes.
Console-created API and Admin keys can have expiration dates. Existing keys are
unchanged, keys lasting at least seven days trigger a pre-expiration email, and
the Admin API reports the expiration.

## Compliance transcripts

Enterprise organizations can use an existing Compliance Access Key with
`read:compliance_user_data` to list cloud Cowork sessions and retrieve their
transcripts.

```text
GET /v1/compliance/apps/sessions/remote
GET /v1/compliance/apps/sessions/remote/{session_id}/messages
```

Beta routes cover Cowork and Claude Code sessions run on user machines. The
same key and scope can list organization-wide local sessions, retrieve session
metadata, and fetch transcripts.

```text
GET /v1/compliance/apps/sessions/local
GET /v1/compliance/apps/sessions/local/{session_id}
GET /v1/compliance/apps/sessions/local/{session_id}/messages
```
