# Managed Agents

## Core beta contract

Batch `release-lifecycle` describes Claude Managed Agents: API-managed agents,
containers, built-in tools, and server-sent event streaming. Core endpoints use
`managed-agents-2026-04-01`; memory list endpoints have a separate header
cutover below.

## Starting and overriding a session

`POST /v1/sessions` accepts at most 50 `initial_events`, each a `user.message`
or `user.define_outcome`. A non-empty list starts the agent loop during that
same request.

An agent of `type: "agent_with_overrides"` may replace the model, system prompt,
tools, MCP servers, or skills for a single session without modifying the stored
agent.

Place `effort` inside the agent's `model` object. On update, include `version`
for optimistic concurrency; a mismatch returns 409. Omitting `version` applies
the update unconditionally.

## Session and thread streams

`GET /v1/sessions/{session_id}/events/stream` accepts `event_deltas[]` so
`event_start` and `event_delta` previews arrive before the complete
`agent.message`. `/threads/{thread_id}/stream` accepts the same parameter but
previews only that thread.

Session lists expose `prev_page` and `next_page`; pass either cursor back as
`page`.

## Memory-list header cutover

`agent-memory-2026-07-22` replaces `managed-agents-2026-04-01` on memory
endpoints. Sending both returns HTTP 400, old cursors cannot be reused, and
explicit SDK beta lists must replace rather than append the old value.

Under the new header,
`GET /v1/memory_stores/{memory_store_id}/memories` uses stable server ordering,
ignores `order_by` and `order`, permits only `depth` 0, 1, or omitted, and
requires `path_prefix` to end in `/` and match whole segments. The old header
adopted the same list semantics on July 22.

## Memory, execution, and dynamic configuration

Memory and multiagent orchestration are public beta under the standard Managed
Agents header. Dreams uses `dreaming-2026-04-21` to reorganize a memory store
from earlier sessions.

Agents can run in self-hosted sandboxes and alter MCP-server or tool
configuration during an active session. Tool outputs above 100,000 characters
spill into a sandbox file, leaving a truncated preview and its path.

## Vaults, schedules, and webhooks

Vaults support environment-variable secrets and background refresh for
`mcp_oauth`. `injection_location` can substitute credentials at egress into
headers, the body, or both.

Sessions can run on cron schedules. Webhooks cover session, thread, vault,
agent, deployment, deployment-run, environment, and memory-store lifecycles.
Events named `session.thread_*` contain `session_thread_id`.

## Hard session budgets

Batch `2026-08-01-2026-08-19` adds hard per-session spend caps at public list
rates. Reaching a cap pauses the session with `stop_reason: "budget_reached"`.
Changing or removing the cap resumes it. A deployment-level budget applies
independently to every session launched by that deployment.

## Advisors

The primary session thread may consult an advisor during a turn. Put an entry
with `{"type": "advisor"}` and the advisor model in the multiagent roster. The
advisor must be at least as capable as the agent's model.

This roster feature is separate from the direct beta advisor tool used in a
Messages request.

## Inference location

Set `inference_geo` inside the agent's `model` object when creating an agent,
or override it for one session. Apply geography requirements at both stored
configuration and override layers during audits.

## Repository-mounted skills

When a session mounts a GitHub repository, skills under the repository root's
`.claude/skills` directory are discovered automatically at session start and
remain available for that session.
