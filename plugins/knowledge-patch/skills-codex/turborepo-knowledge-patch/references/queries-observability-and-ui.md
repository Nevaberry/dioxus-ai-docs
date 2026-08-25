# Queries, Observability, and Terminal UI

## Query Repository State

`turbo query` is stable (since 2.9.0). With no query it opens GraphiQL. Supply
GraphQL inline or with `--file`, and use `--schema` to print the schema:

```bash
turbo query
turbo query --schema
turbo query '{ packages { items { name } } }'
turbo query --file=query.gql
```

The `affected` shorthand emits structured JSON for changed tasks or packages:

```bash
turbo query affected --tasks build
turbo query affected --packages
```

`ls` pretty-prints package details by default and supports JSON output,
affected-only results, and selectors:

```bash
turbo query ls web --output=json
turbo query ls --affected --filter='./apps/*'
```

`turbo-ignore` is deprecated in favor of `turbo query affected`.

## Inspect Graphs and Relationships

`turbo devtools` presents live Package Graph and Task Graph views that
hot-reload with repository changes (since 2.7.0):

```bash
turbo devtools
```

The views expose direct and transitive relationships useful for explaining
cache misses. JSON output from `turbo ls` includes package dependents, and
dry-run and summary output includes `with` sidecar relationships (since 2.6.0).

## Export Experimental OpenTelemetry Metrics

Enable the `experimentalObservability` Future Flag and configure an OTLP
endpoint to export metrics (since 2.9.0):

```json
{
  "futureFlags": { "experimentalObservability": true },
  "experimentalObservability": {
    "otel": {
      "enabled": true,
      "endpoint": "http://otel-collector.example.com:4317",
      "protocol": "grpc"
    }
  }
}
```

Exported metrics include `turbo.run.duration_ms`,
`turbo.run.tasks.cached`, and `turbo.run.tasks.failed`.

## Stream and Save Structured Logs

`--json` streams NDJSON objects with `timestamp`, `source`, `level`, and
`text` fields (since 2.9.0):

```bash
turbo run build --json
```

`--log-file` preserves ordinary terminal output while writing structured logs
to `.turbo/logs/<epoch-millis>.json` by default. It accepts a custom path and
can be combined with `--json`:

```bash
turbo run build --log-file
turbo run lint --json --log-file=logs.json
```

## Capture Profiles Without Naming Files

`--profile` and `--anon-profile` no longer require a filename, and profile
output includes a Markdown companion beside the trace (since 2.9.0):

```bash
turbo run build --profile
turbo run build --anon-profile
```

## Use Persistent Terminal UI Controls

The terminal UI remembers the selected task, task-list visibility, and task
pinning between invocations (since 2.4.0).

| Key | Action |
| --- | --- |
| `h` | Toggle the task list |
| `c` | Copy highlighted logs |
| `j` / `k` | Select tasks |
| `p` | Pin or unpin a task |
| `u` / `d` | Scroll logs |
| `m` | List all keybindings |

Press `/` to enter a task search query; the task list filters so only matching
tasks are selected (since 2.6.0). The task list also supports mouse-wheel
scrolling (since 2.10.8).
