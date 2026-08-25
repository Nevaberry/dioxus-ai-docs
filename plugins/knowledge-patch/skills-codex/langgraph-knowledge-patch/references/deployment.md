# Deployment

Relevant source topic: `platform-and-deployment`.

## Server-owned graph loading and persistence

When a compiled graph is exported, Agent Server loads it once at container
startup and reuses it. A graph factory runs for every invocation and is
appropriate only when each run needs customization. In either case, the server
injects the deployment's checkpointer and memory Store; graph code must not
configure its own.

## Adapting agents from other frameworks

An Agent Server graph does not need to be implemented directly in LangGraph.
Adapt an agent from another framework for deployment with the LangGraph
Functional API or the `deployments-wrap-sdk` package.

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
- Split mode creates independently scaled API and worker pools. Enable it with
  `queue.enabled: true`.
- Distributed runtime separates graph orchestration from execution.

```yaml
queue:
  enabled: true
```

## Queue and concurrency boundaries

A worker leases a queued run from the durable database. The queue permits at
most one executing run per thread. Each worker runs at most
`N_JOBS_PER_WORKER` jobs concurrently; the default is `10`. This setting does
not limit API request concurrency. Split deployments must keep at least one
queue worker listening.

## Threadless deployment streaming

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

## JavaScript deployment outside LangSmith

JavaScript LangGraph agents can use the same Agent Streaming Protocol when
deployed on Next.js, SvelteKit, Nuxt, Cloudflare Workers, or Deno Deploy.
