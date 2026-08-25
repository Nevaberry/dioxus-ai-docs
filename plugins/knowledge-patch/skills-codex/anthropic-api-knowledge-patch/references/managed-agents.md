# Managed Agents and Administration

This reference consolidates Managed Agents guidance from `release-lifecycle`
and `2026-08-01-2026-08-19`.

## Core beta contract

Claude Managed Agents provides API-managed agents, containers, built-in tools,
and server-sent event streaming. Use the following beta header on the core
surface; memory-list endpoints use a different header described below.

```text
Anthropic-Beta: managed-agents-2026-04-01
```

## Start sessions and override one run

`POST /v1/sessions` accepts up to 50 `initial_events`. They may be
`user.message` or `user.define_outcome` events. A non-empty list begins the
agent loop in the session-creation call.

An agent with `type: "agent_with_overrides"` may replace model, system prompt,
tools, MCP servers, or skills for that session without modifying the stored
agent.

## Model settings and concurrent updates

Put `effort` inside the agent's `model` object, not at the agent root. Put
`inference_geo` there as well when creating an agent, or override the inference
location for one session.

When updating an agent, include `version` to request optimistic concurrency. A
version mismatch returns 409. Omit it only when an unconditional update is
intentional.

## Session and thread event streams

`GET /v1/sessions/{session_id}/events/stream` accepts `event_deltas[]` to emit
`event_start` and `event_delta` previews before the complete `agent.message`.
The thread-level `/threads/{thread_id}/stream` accepts the same parameter but
previews only that thread.

Session listings return `prev_page` and `next_page`; pass either cursor back
through `page`.

## Memory-list header cutover

For `GET /v1/memory_stores/{memory_store_id}/memories`, replace the core header
with:

```text
Anthropic-Beta: agent-memory-2026-07-22
```

The endpoint now:

- Uses stable server ordering and ignores `order_by` and `order`.
- Accepts `depth` values of 0, 1, or omitted.
- Requires `path_prefix` to end in `/` and match complete path segments.

Sending both the memory and core beta headers returns 400. Old cursors cannot
be reused. SDK code that passes explicit beta lists must replace the old value,
not append the new one. The old header adopted the same list semantics on July
22, but it is no longer the header for memory endpoints.

## Memory, dreams, and execution

Memory and multiagent orchestration are public beta under the standard Managed
Agents header. Dreams uses `dreaming-2026-04-21` to reorganize a memory store
based on earlier sessions.

Agents may execute in self-hosted sandboxes and change MCP-server or tool
configuration during an active session. A tool output longer than 100,000
characters spills to a sandbox file; the model receives a truncated preview
and the file path. Preserve the path for later tool or agent access.

## Vaults and secret injection

Vaults support environment-variable secrets and background refresh for
`mcp_oauth`. `injection_location` controls egress substitution into request
headers, request bodies, or both. Keep raw credentials out of prompts and tool
results; use vault injection at the external boundary.

## Schedules and webhooks

Sessions may run on cron schedules. Webhooks cover session, thread, vault,
agent, deployment, deployment-run, environment, and memory-store lifecycles.
Events named `session.thread_*` identify their thread with
`session_thread_id`.

## Hard spend budgets

A session can have a hard spend cap calculated at public list rates. When it is
reached, the session pauses with `stop_reason: "budget_reached"`. Changing or
removing the budget resumes the session.

A deployment-level budget applies independently to every session the
deployment starts; it is not one shared allowance across all deployment
sessions.

## Advisor roster entries

The primary session thread can consult an advisor model in the middle of a
turn. Add `{"type": "advisor"}` plus the advisor model to the agent's
multiagent roster. The advisor must be at least as capable as the agent's own
model.

This roster facility is distinct from the request-level beta advisor tool in
[Tools and streaming](tools-and-streaming.md).

## Repository-mounted skills

When a session mounts a GitHub repository, it discovers skills beneath the
repository root's `.claude/skills` directory at session startup. Those skills
remain available for that session. Ensure required skill files are present
before session creation; later repository changes are not a substitute for the
startup discovery step.

## Operational checklist

- Keep core and memory beta headers mutually exclusive on memory routes.
- Supply update versions when overwrites must be prevented.
- Treat delta previews as provisional until the complete event arrives.
- Persist spill-file paths from oversized tool results.
- Monitor session and deployment budgets independently.
- Validate advisor capability ordering when building the roster.
- Confirm repository skill discovery in a fresh mounted session.
