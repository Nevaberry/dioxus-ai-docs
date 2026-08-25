---
name: k6-knowledge-patch
description: Grafana k6
version: 2.1.0
license: MIT
metadata:
  author: Nevaberry
---


# Grafana k6 Knowledge Patch

Use this skill when writing, reviewing, upgrading, or operating Grafana k6
tests. Inspect the project's pinned k6 version before applying version-specific
advice. Prefer the project's manifests, scripts, configuration, and observed
behavior when they disagree with generic guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Browser Testing](references/browser-testing.md) | Locators, frames, network waits, routing, events, proxies, CDP, and browser metrics |
| [CLI, Configuration, and Execution](references/cli-config-and-execution.md) | TypeScript, summaries, scenarios, feature flags, logging, containers, and runtime controls |
| [Cloud and Secrets](references/cloud-and-secrets.md) | Cloud commands, stacks and projects, local execution, secret sources, logs, and orchestrator credentials |
| [Extensions and Dependencies](references/extensions-and-dependencies.md) | Automatic resolution, dependency manifests, `k6 x`, Go extensions, DNS, Redis, and WebSockets |
| [Metrics, Outputs, and Runtime](references/metrics-outputs-and-runtime.md) | OpenTelemetry, Prometheus, Cloud output, gRPC, crypto, HTTP/2, and JavaScript runtime APIs |
| [Migration and Compatibility](references/migration-and-compatibility.md) | Semantic-versioning policy, build toolchains, removals, deprecations, and major-version migration |

## Breaking changes and migration traps

### Treat a v2 upgrade as an explicit migration

Before moving to k6 v2, search code and automation for all of the following:

- Go imports beginning with `go.k6.io/k6/`; change them to
  `go.k6.io/k6/v2/`.
- The `externally-controlled` executor and the `pause`, `resume`, `scale`, or
  `status` CLI commands; replace the executor rather than looking for renamed
  commands.
- Positional `k6 cloud script.js`, top-level `k6 login`, `--upload-only`, and
  `options.ext.loadimpact`; use explicit Cloud subcommands and `options.cloud`.
- `K6_BINARY_PROVISIONING`, `K6_ENABLE_COMMUNITY_EXTENSIONS`, and
  `K6_OTEL_SINGLE_COUNTER_FOR_RATE`; remove them.
- The legacy `loadimpact/config.json` path; move or regenerate the file under
  the `k6` configuration directory.
- Automation that assumes the HTTP API listens by default or that an aborted
  Cloud run exits successfully. Enable the API with `--address`; treat exit
  status `97` as failure.

See [Migration and Compatibility](references/migration-and-compatibility.md)
for extension JSON changes, archive metadata, Docker tags, and the complete
migration checklist.

### Migrate deprecated summary settings

Use `--summary-mode=disabled` or `K6_SUMMARY_MODE=disabled` instead of
`--no-summary` or `K6_NO_SUMMARY`. Do not build new tooling around the legacy
summary mode; choose `compact` or `full`. If `handleSummary()` legitimately
needs longer than its default budget, set `handleSummaryTimeout` or
`K6_HANDLE_SUMMARY_TIMEOUT`.

### Use stable module paths

- Use `k6/websockets`, not `k6/experimental/websockets`.
- Use the official Redis extension instead of `k6/experimental/redis`.
- Use `--out opentelemetry`; the `experimental-opentelemetry` alias and
  `K6_OTEL_EXPORTER_TYPE` are deprecated.
- Replace browser FID thresholds and integrations with INP.

## High-value workflows

### Run JavaScript or TypeScript directly

k6 executes `.ts` files directly, so a separate transpilation stage is not
required for supported TypeScript syntax:

```typescript
import http from 'k6/http';

interface Target { url: string }
const target: Target = { url: 'https://quickpizza.grafana.com/' };

export default function () {
  http.get(target.url);
}
```

```sh
k6 run script.ts
```

### Coordinate browser waits with their trigger

Arm request or response waits at the same time as the action so fast network
events cannot be missed:

```javascript
const [response] = await Promise.all([
  page.waitForResponse(/\/api\/.*\.json$/),
  page.click('button[data-testid="load-data"]'),
]);
```

Use `page.route()` to abort, modify, or fulfill matching requests. Remove a
specific route with the identical matcher passed to `page.unroute()`, or clear
all routes with `page.unrouteAll()`. For nested iframes, chain
`frameLocator()` calls rather than manually switching frame context.

### Resolve extensions automatically

Use static ES module imports so k6 can detect and provision extensions:

```javascript
import dns from 'k6/x/dns';
```

Dynamic CommonJS `require()` is not discovered. If CommonJS is unavoidable,
put a directive at the beginning of each relevant file, after only an optional
shebang, whitespace, or comments:

```javascript
"use k6 with k6/x/redis"
const redis = require('k6/x/redis');
```

Inspect dependencies with `k6 deps --json script.js`. Supply missing
constraints through `K6_DEPENDENCIES_MANIFEST`; use `k6 x` to discover or run
extension subcommands.

### Configure Cloud context explicitly

Prefer explicit Cloud commands:

```sh
k6 cloud login --token "$MY_TOKEN" --stack my-stack-slug
k6 cloud run script.js
k6 cloud upload script.js
k6 cloud project list --format=json
k6 cloud test list --json
```

Cloud project resolution can come from an explicit project ID, environment or
script configuration, or the configured stack's default project. For local
Cloud execution, decide explicitly whether secrets and logs should leave the
machine; behavior differs between maintained major lines and newer commands
provide `--no-cloud-logs`.

### Inspect and enable features

List lifecycle information with `k6 features` or `k6 features --json`. Enable
features with repeated or comma-separated `--features`, `K6_FEATURES`, or the
`features` key in `config.json`:

```sh
k6 run --features native-histograms,merge-run-tags script.js
```

Feature selections are tagged in metrics and preserved in archives and Cloud
workers. `native-histograms` changes trend storage; `merge-run-tags` changes
tag precedence; `freeze-env` makes mutation of `__ENV` fail in strict mode.

## Operational guardrails

### Make scenario overrides visible

Passing `--vus N` now replaces configured scenarios with a
`shared-iterations` scenario containing `N` VUs and `N` iterations, and emits
a warning. Treat the flag as a scenario override, not a harmless default.

### Interpret exits and explicit failures correctly

Status consumers can distinguish a run marked by `execution.test.fail()` with
`ExecutionStatusMarkedAsFailed`. In Cloud automation, preserve the distinct
exit meanings: successful runs use `0`, Cloud aborts use `97`, and threshold
aborts use `99`.

### Keep sensitive output deliberate

Locally executed Cloud tests can stream logs to their Cloud run. Use
`--no-cloud-logs` when logs must remain local, and otherwise rely on Grafana
secrets management and redaction for values that might be logged. Anonymous
extension usage reporting can be disabled with `--no-usage-report`.

### Pin infrastructure assumptions

Container images run as numeric UID `12345`, which is useful in Kubernetes
security contexts. Pin explicit Docker tags when reproducibility matters;
floating `:vN` tags track a major line, while prereleases and maintenance
releases from older majors do not update `:latest`.

### Check output compatibility

- Rate exports use one counter labeled `zero` or `nonzero`; the old
  OpenTelemetry fallback is gone in v2.
- Experimental OpenTelemetry and Prometheus outputs began with a TLS 1.3
  default. Prometheus remote write can set its floor with
  `K6_PROMETHEUS_RW_TLS_MIN_VERSION`.
- Cloud output v2 reports Gauge `min` and `max` in their correct fields.
- OpenTelemetry HTTP Basic Auth uses the dedicated username and password
  environment variables or output-config keys.

Consult the topic references before changing browser synchronization,
extension provisioning, Cloud local execution, or exported metric schemas;
those areas have version-sensitive behavior that is easy to misapply.
