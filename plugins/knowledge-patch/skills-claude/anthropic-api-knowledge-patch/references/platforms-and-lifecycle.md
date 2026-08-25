# Platforms and Release Lifecycle

## Lifecycle operations

Legacy targets receive no updates but lack a retirement date. Deprecated
targets continue working until their scheduled retirement, while retired IDs
reject requests. Publicly released targets receive at least 60 days' retirement
notice. Use the Console usage-export CSV, grouped by API key and model, to find
remaining callers.

The current schedule in batch `release-lifecycle` requires moving
`claude-opus-4-1-20250805` to `claude-opus-4-8` before August 5, 2026.
`claude-mythos-preview` is deprecated in favor of `claude-mythos-5`; listed
Claude 4.0, 3.x, 2.x, 1.x, and Instant IDs are already retired.

Earliest tentative retirement dates are:

- Opus 4.5: November 24, 2026; Sonnet 4.5: September 29, 2026; Haiku 4.5:
  October 15, 2026.
- Opus 4.6, 4.7, 4.8, and 5: February 5, April 16, May 28, and July 24, 2027.
- Sonnet 4.6 and 5: February 17 and June 30, 2027.
- Fable 5: June 9, 2027.

## Workbench and prompt-tool shutdown

Legacy Workbench access ends August 17, 2026. Its prompts, variables, and evals
do not transfer to the updated experience, so export them first. The endpoints
`/v1/experimental/generate_prompt`, `/v1/experimental/improve_prompt`, and
`/v1/experimental/templatize_prompt` retire the same day and then error.

## Fast-mode retirement behavior

`speed: "fast"` on Opus 4.7 now errors. On Opus 4.6 it silently uses standard
speed and standard pricing. Inspect `usage.speed` rather than trusting the
requested mode, and move fast workloads to a supported newer target.

## Discovering capabilities

`GET /v1/models` and `GET /v1/models/{model_id}` expose
`max_input_tokens`, `max_tokens`, and `capabilities`. Discover these values
instead of hard-coding family assumptions.

## Workload identity and inference geography

Workload Identity Federation is GA. Configure OIDC issuers and federation
rules in Console, then use an SDK to exchange and refresh short-lived
credentials instead of distributing static API keys.

For targets released after February 1, 2026, `inference_geo` can request
US-only inference at 1.1x pricing. Managed Agents place this field inside the
agent model object and can override it per session.

## AWS-hosted surfaces

Claude Platform on AWS is Anthropic-managed infrastructure with AWS billing and
IAM. Native AWS endpoints expose Messages, Files, Message Batches, Managed
Agents, Agent Skills, code execution, and tool use.

Amazon Bedrock is separate AWS-managed infrastructure. Its
`/anthropic/v1/messages` route accepts the first-party Messages shape. Opus 4.7
and Haiku 4.5 are self-serve there through global and regional endpoints.
Feature availability, ID syntax, caching isolation, and billing behavior must
be checked per surface.

## Automatic prompt caching and diagnosis

A request-level `cache_control` automatically caches the last eligible block
and advances with the conversation; it can coexist with block-level controls.
For a miss, enable `cache-diagnosis-2026-04-07`, send
`diagnostics.previous_message_id`, and inspect `cache_miss_reason` for the
diverging prefix.

## Hosted tools and instruction updates

`web_search_20260318` and `web_fetch_20260318` support `response_inclusion` to
omit already consumed result blocks from loop responses.

Fable 5, Mythos 5, and Opus 4.8 accept `role: "system"` messages immediately
after a user turn without a beta header, allowing instruction changes while
preserving earlier cache prefixes.

## Enterprise users and key lifetime

Batch `2026-08-01-2026-08-19` supersedes the earlier beta requirement:
member, invite, group, and custom-role Admin API endpoints are GA. Group and
custom-role requests no longer require `ce-user-management-2026-07-13`, though
requests that still include it continue to work. Member and invite calls never
needed that header. An Admin key with `read:org_audit` may call all
user-management `GET` routes.

Console-created API and Admin API keys may have expiration dates. Existing keys
are unchanged; keys lasting at least seven days trigger pre-expiration email,
and the Admin API reports expiration.

## Compliance session transcripts

Enterprise organizations can use an existing Compliance Access Key with
`read:compliance_user_data` to list cloud Cowork sessions and retrieve their
transcripts:

```text
GET /v1/compliance/apps/sessions/remote
GET /v1/compliance/apps/sessions/remote/{session_id}/messages
```

Beta routes cover local Cowork and Claude Code sessions across the organization,
including list, metadata, and transcript retrieval:

```text
GET /v1/compliance/apps/sessions/local
GET /v1/compliance/apps/sessions/local/{session_id}
GET /v1/compliance/apps/sessions/local/{session_id}/messages
```

## Resolved workspace identity

API responses include `anthropic-workspace-id`. Its `wrkspc_`-prefixed value
identifies the workspace selected from the request credential, including the
Default Workspace. Record it when diagnosing limits, spend, caching, or access.
