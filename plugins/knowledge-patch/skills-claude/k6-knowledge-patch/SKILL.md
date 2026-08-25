---
name: k6-knowledge-patch
description: Grafana k6
version: 2.1.0
license: MIT
metadata:
  author: Nevaberry
---


# Grafana k6 Knowledge Patch

Load this skill when writing, reviewing, upgrading, or troubleshooting Grafana
k6 tests, extensions, browser automation, Cloud workflows, or output pipelines.
Use the quick references for common migration decisions, then open the relevant
topic file for complete behavior and examples.

## Reference index

| Reference | Topics |
| --- | --- |
| [Browser testing](references/browser-testing.md) | Locators, frames, routing, request lifecycle, proxies, CDP, and headers |
| [CLI, Cloud, and configuration](references/cli-cloud-and-configuration.md) | Cloud commands, summaries, feature flags, secrets, API server, tags, and Docker tags |
| [Extensions and dependencies](references/extensions-and-dependencies.md) | Automatic resolution, dependency manifests, `k6 x`, Go modules, DNS, and usage reporting |
| [Migrations and compatibility](references/migrations-and-compatibility.md) | Breaking changes, removals, runtime requirements, containers, HTTP, and stable APIs |
| [Outputs and observability](references/outputs-and-observability.md) | OpenTelemetry, Prometheus, Rate and Gauge shapes, logs, dashboards, and metrics |
| [Scripting, security, and protocols](references/scripting-security-and-protocols.md) | TypeScript, assertions, crypto, TOTP, WebSockets, gRPC, encoding, streams, and secrets |

## Upgrade to k6 v2

Treat a major upgrade as a code and operations migration:

1. Replace Go imports such as `go.k6.io/k6/js/modules` with
   `go.k6.io/k6/v2/js/modules`.
2. Replace `options.ext.loadimpact` with `options.cloud`.
3. Replace removed Cloud syntax with `k6 cloud login`, `k6 cloud run`, or
   `k6 cloud upload`.
4. Remove the `externally-controlled` executor and the `pause`, `resume`,
   `scale`, and `status` commands; choose a supported executor.
5. Move legacy configuration to `{USER_CONFIG_DIR}/k6/config.json`.
6. Remove `K6_BINARY_PROVISIONING`, `K6_ENABLE_COMMUNITY_EXTENSIONS`, and
   `K6_OTEL_SINGLE_COUNTER_FOR_RATE`.
7. Enable the local HTTP API explicitly with `--address` or `K6_ADDRESS`.
8. Update CI to treat Cloud exit status `97` as failure.

See [Migrations and compatibility](references/migrations-and-compatibility.md),
[CLI, Cloud, and configuration](references/cli-cloud-and-configuration.md), and
[Extensions and dependencies](references/extensions-and-dependencies.md) for
the complete migration surface.

## Deprecation checklist

- Use `--summary-mode=disabled` instead of `--no-summary` or
  `K6_NO_SUMMARY`.
- Use `compact` or `full` summaries instead of the deprecated `legacy` mode.
- Use `--out opentelemetry` and `K6_OTEL_EXPORTER_PROTOCOL`; the
  `experimental-opentelemetry` name and `K6_OTEL_EXPORTER_TYPE` are deprecated.
- Replace `k6/experimental/redis` with the official Redis extension.
- Import WebSockets from `k6/websockets`, not
  `k6/experimental/websockets`.
- Replace First Input Delay thresholds with Interaction to Next Paint, such
  as `browser_web_vital_inp: ['p(95)<200']`.

## Browser synchronization

Arm a network wait before triggering the action, so fast requests cannot be
missed:

```javascript
const [response] = await Promise.all([
  page.waitForResponse(/\/api\/.*\.json$/),
  page.click('button[data-testid="load-data"]'),
]);
```

The same pattern applies to `page.waitForRequest()`. For general page events,
create the `page.waitForEvent()` promise before the action. Use
`page.route()` to intercept traffic, `page.unroute()` with the identical
matcher to remove one route, or `page.unrouteAll()` to clear all routes.

For nested frames, prefer chainable frame locators:

```javascript
const frame = page.frameLocator('#payment-iframe');
await frame.frameLocator('#nested-frame').locator('#submit').click();
```

See [Browser testing](references/browser-testing.md) for locator selection,
visibility retries, request events, redirect semantics, per-context proxies,
and CDP attachment.

## Automatic extension resolution

k6 discovers extensions from static ES module imports and provisions a
matching binary automatically. It does not discover dynamic CommonJS
`require()` calls. For CommonJS, put a directive at the beginning of each
relevant file:

```javascript
"use k6 with k6/x/redis"
const redis = require('k6/x/redis');
```

Use `k6 deps --json script.js` to inspect dependencies and
`K6_DEPENDENCIES_MANIFEST` to constrain dependencies without a version pragma.
Run `k6 x` to discover extension subcommands; missing subcommand extensions can
be provisioned on demand.

## Cloud command patterns

Use explicit Cloud subcommands:

```sh
k6 cloud login --token "$MY_TOKEN" --stack my-stack-slug
k6 cloud run script.js
k6 cloud upload script.js
k6 cloud project list --format=json
k6 cloud test list --json
```

For local execution, `K6_CLOUD_PUSH_REF_ID` reuses an existing run. On the 1.8
maintenance line, Cloud secret sources must be configured explicitly. Cloud
logs are streamed for locally executed Cloud tests unless `--no-cloud-logs` is
passed.

## Summaries and machine-readable output

Select the end-of-test presentation with `--summary-mode=compact`, `full`, or
`disabled`. A structured shape for `--summary-export` and `handleSummary()` is
available with `--new-machine-readable-summary` or
`K6_NEW_MACHINE_READABLE_SUMMARY`. Configure long summary callbacks with
`handleSummaryTimeout` or `K6_HANDLE_SUMMARY_TIMEOUT`.

## Feature flags

Enable experimental behavior with repeated or comma-separated `--features`,
with `K6_FEATURES`, or with `features` in `config.json`. Inspect flags and their
lifecycle with `k6 features --json`.

```sh
k6 run --features native-histograms,merge-run-tags,freeze-env script.js
```

`native-histograms` changes trend storage. `merge-run-tags` merges tags per
key across configuration layers. `freeze-env` makes `__ENV` immutable.
Feature selections are included in metric tags and preserved in archives and
Cloud workers.

## Output migration

Use the stable OpenTelemetry output:

```sh
k6 run --out opentelemetry script.js
```

Exported Rate metrics use one counter labeled with `zero` and `nonzero`.
Consumers must accept this labeled representation. The OpenTelemetry HTTP
exporter supports Basic Auth through `K6_OTEL_HTTP_EXPORTER_USERNAME` and
`K6_OTEL_HTTP_EXPORTER_PASSWORD`. Prometheus remote write defaults to TLS 1.3
and exposes `K6_PROMETHEUS_RW_TLS_MIN_VERSION` for its minimum.

## Script APIs

k6 runs `.ts` files directly. `k6/browser`, `k6/net/grpc`, and `k6/crypto` are
stable modules, and WebSockets are stable at `k6/websockets`. The global
`TextEncoder` and `TextDecoder` work in init and VU contexts. PBKDF2 is
available in the crypto module, and the TOTP jslib package supports RFC 6238
generation and verification.

Use `k6/secrets` for asynchronous secret retrieval and log redaction. Configure
sources explicitly for the execution environment; environment configuration
uses `K6_SECRET_SOURCE` with the same syntax as `--secret-source`.

## Verification habits

- Pin Docker image tags when reproducibility matters; floating `:vN` tags
  follow a major line.
- Run `k6 deps --json` and archive inspection before moving an extension-heavy
  test between hosts.
- Inspect provisioning logs for resolution, cache, download, retry, and pruning
  behavior.
- Check downstream output schemas after Rate, Gauge, redirect, or histogram
  changes.
- Exercise browser redirect chains when relying on events, response headers,
  or sent/received byte metrics.
- Treat warnings about extra `http.get()` or `http.head()` arguments as a call
  signature bug even though the extra values are still ignored.
