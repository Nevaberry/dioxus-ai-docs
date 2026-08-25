# Deployment

## Server-owned graph loading and state

When a compiled graph is exported, Agent Server loads it once at container
startup and reuses it. A graph factory runs for every execution and should be
reserved for per-run customization. In both cases, the server injects the
deployment checkpointer and memory Store; graph code must not configure either.

## Agents from other frameworks

Agent Server graphs need not be implemented directly with LangGraph. Adapt
agents from other frameworks for deployment through the LangGraph Functional
API or the `deployments-wrap-sdk` package.

## PostgreSQL and Redis roles

Assistants, threads, runs, and cron jobs always persist in PostgreSQL.
Checkpoints default to PostgreSQL but may use MongoDB or a custom backend. The
long-term Store defaults to PostgreSQL but is replaceable. Redis carries only
ephemeral signaling, cancellation, and streaming pub/sub; it does not persist
user or run data.

## Runtime layouts

Self-hosting supports three layouts:

- Single-host mode is the default; the API server manages the task queue
  without separate workers.
- Split mode independently scales API and worker pools. Enable it with
  `queue.enabled: true`.
- Distributed runtime separates graph orchestration from execution.

```yaml
queue:
  enabled: true
```

## Queue execution and concurrency

A worker leases a queued run from the durable database. At most one run per
thread executes at a time. Each worker runs up to `N_JOBS_PER_WORKER` jobs
concurrently; its default is `10`. This does not limit API request concurrency.
A split deployment must keep at least one queue worker listening.

## Threadless remote streaming

Pass `None` as the thread identifier to stream a threadless run. The following
argument is the deployed graph name from `langgraph.json`.

```python
from langgraph_sdk import get_sync_client

client = get_sync_client(url=deployment_url, api_key=langsmith_api_key)
for chunk in client.runs.stream(
    None,
    "agent",
    input={"messages": [{"role": "human", "content": "Hello"}]},
    stream_mode="updates",
):
    print(chunk.event, chunk.data)
```

## JavaScript deployment beyond LangSmith

JavaScript LangGraph agents can implement the same Agent Streaming Protocol on
Next.js, SvelteKit, Nuxt, Cloudflare Workers, or Deno Deploy.
