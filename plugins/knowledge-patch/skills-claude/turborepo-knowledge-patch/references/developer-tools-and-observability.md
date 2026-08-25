# Developer tools and observability

## Use persistent terminal UI controls (since 2.4.0)

The terminal UI remembers the selected task, task-list visibility, and task
pinning between invocations.

- Press `h` to toggle the task list.
- Press `c` to copy highlighted logs.
- Press `j` or `k` to select tasks.
- Press `p` to pin or unpin a task.
- Press `u` or `d` to scroll logs.
- Press `m` to list all keybinds.

Press `/` to enter a search query; the task list is filtered so only matching
tasks are selected (since 2.6.0).

The task list can be scrolled with the mouse wheel (since 2.10.8).

## Serve local microfrontends through one proxy (since 2.6.0)

Turborepo can serve several applications through one local proxy at
`localhost:3024`. Put `microfrontends.json` in the parent application, map each
application to its development port and route prefixes, and run `turbo dev`.
The unrouted application handles all remaining paths.

```json
{
  "$schema": "https://turborepo.dev/microfrontends/schema.json",
  "applications": {
    "web": {
      "development": {
        "local": 3000
      }
    },
    "docs": {
      "development": {
        "local": 3001
      },
      "routing": [
        {
          "paths": ["/docs", "/docs/:path*"]
        }
      ]
    }
  }
}
```

```bash
turbo dev
```

## Inspect graph and dry-run output (since 2.6.0)

The JSON output from `turbo ls` includes dependents. Dry-run and summary output
include `with` sidecar relationships.

## Open live package and task graphs (since 2.7.0)

`turbo devtools` provides visual Package Graph and Task Graph views that
hot-reload as the repository changes. The direct and transitive relationships
can explain cache misses.

```bash
turbo devtools
```

## Install the Turborepo Agent Skill (since 2.8.0)

The Turborepo Agent Skill gives compatible coding agents Turborepo and monorepo
guidance, including recommended patterns and anti-patterns.

```bash
npx skills add vercel/turborepo
```

## Request machine-readable documentation (since 2.8.0)

Documentation routes return Markdown when requested with
`Accept: text/markdown`. Markdown is also available by appending `.md` to a
route. The machine-readable index is `/sitemap.md`, and version-pinned
documentation is available from version subdomains such as
`v2-7-6.turborepo.dev`.

```bash
curl -sL -H "Accept: text/markdown" https://turborepo.dev/repo/docs
curl -sL https://turborepo.dev/sitemap.md
```

## Search documentation from the CLI (since 2.8.0)

`turbo docs` searches Turborepo documentation and prints matching pages in the
terminal.

```bash
turbo docs "package configurations"
```

## Export experimental OpenTelemetry metrics (since 2.9.0)

Enable the `experimentalObservability` Future Flag and configure an OTLP
endpoint to export metrics such as `turbo.run.duration_ms`,
`turbo.run.tasks.cached`, and `turbo.run.tasks.failed`.

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

## Write experimental structured logs (since 2.9.0)

`--json` streams NDJSON objects containing `timestamp`, `source`, `level`, and
`text`. `--log-file` keeps normal terminal output while writing structured logs
to `.turbo/logs/<epoch-millis>.json`; it accepts a custom path and can be
combined with `--json`.

```bash
turbo run build --json
turbo run build --log-file
turbo run lint --json --log-file=logs.json
```

## Name profiles optionally (since 2.9.0)

`--profile` and `--anon-profile` do not require a filename. Profile output also
includes a Markdown companion beside the trace.

```bash
turbo run build --profile
turbo run build --anon-profile
```
