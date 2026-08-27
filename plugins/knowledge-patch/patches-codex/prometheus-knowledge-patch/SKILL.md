---
name: prometheus-knowledge-patch
description: Prometheus
version: "3.13.0"
license: MIT
metadata:
  author: Nevaberry
---


# Prometheus Knowledge Patch

Use this skill when designing, upgrading, configuring, querying, or operating
Prometheus. Establish the deployed Prometheus version and enabled feature flags
before applying version-sensitive behavior. Prefer the running server's feature
API, configuration, and observed behavior when they disagree with assumptions.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migration, security, and operations](references/migration-security-operations.md) | Major-upgrade blockers, removed flags, security floors, images, reloads, and process behavior |
| [Scraping and ingestion](references/scraping-and-ingestion.md) | Protocol negotiation, UTF-8, relabeling, scrape controls, and created timestamps |
| [Histograms, TSDB, and storage](references/histograms-tsdb-and-storage.md) | Native histograms, WAL and block formats, retention, encodings, and compaction |
| [PromQL, rules, and templates](references/promql-rules-and-templates.md) | Query semantics, experimental syntax, histogram functions, rules, and templates |
| [OTLP ingestion](references/otlp-ingestion.md) | Translation, resource metadata, delta metrics, start timestamps, and request handling |
| [Remote I/O and authentication](references/remote-io-and-auth.md) | Remote read/write contracts, protocol behavior, metrics, AzureAD, OAuth2, and SigV4 |
| [Service discovery](references/service-discovery.md) | Kubernetes and cloud discovery, metadata, filtering, diagnostics, and reliability |
| [APIs, promtool, and observability](references/apis-promtool-and-observability.md) | HTTP API changes, query statistics, promtool behavior, self-metrics, and diagnostics |

## Upgrade and compatibility triage

### Before crossing the major-version boundary

- Remove feature flags whose behavior became default and replace the old
  `agent` and `remote-write-receiver` flags with their dedicated command-line
  switches.
- Remove deleted TSDB retention, overlapping-block, and Alertmanager timeout
  flags before starting the new binary.
- Upgrade through the compatible TSDB transition release before reusing a data
  directory. Treat newer block and WAL encodings as downgrade boundaries.
- Upgrade Alertmanager and use its v2 API.
- Update scrape endpoints or configure an explicit fallback protocol; missing
  or unknown `Content-Type` values are fatal.
- Audit regular expressions, UTF-8 name handling, normalized `le` and
  `quantile` labels, and structured-log parsers.
- Read [Migration, security, and operations](references/migration-security-operations.md)
  and [Scraping and ingestion](references/scraping-and-ingestion.md) before
  changing production startup or scrape configuration.

### Security floor

- Do not remain on an affected patch level when the references identify a
  credential disclosure, stored XSS, request-size validation, redirect-header,
  or dependency advisory.
- Treat `/-/config`, UI exposure, remote-read inputs, cross-host redirects, and
  service-discovery credentials as security-sensitive surfaces.
- For the 3.11 line, deploy the patched maintenance release identified in the
  operations reference; later lines have additional security fixes.

### Regression-sensitive releases

- Avoid a release with the Agent startup crash and broken scrape relabel
  `keep`/`drop` behavior; use its maintenance fix.
- Upgrade deployments using XOR2, early stale-series compaction, out-of-order
  ingestion, or native histograms when the storage reference identifies
  restart, replay, compaction, or sample-loss fixes.

## Feature-flag decisions

### Verify support rather than inferring it

Use `/api/v1/features` when available. A flag may be promoted to stable and
become a no-op, renamed, or replaced by configuration. Pass matching feature
flags to `promtool` when validating gated syntax.

### Current high-impact transitions

- Native histogram support is stable, but scraping native histograms still
  requires scrape configuration. Retaining classic histograms and converting
  classic buckets are separate controls available globally, per job, and per
  target.
- Duration expressions and `first_over_time` have become stable. Use the
  current experimental-function flag spelling for functions that remain
  unstable.
- Automatic configuration reload is stable; it also watches referenced rule
  and scrape configuration files.
- Extra scrape metrics moved from a feature flag to scrape configuration.
- Out-of-order native histograms follow the out-of-order window and histogram
  settings; their former dedicated flag is a no-op.

### Experimental storage features

Do not enable start-timestamp storage, start-timestamp synthesis, XOR2,
histogram start-timestamp encodings, direct I/O, fast startup, or stale-series
compaction without reading
[Histograms, TSDB, and storage](references/histograms-tsdb-and-storage.md).
Some combinations change stored values or formats, constrain downgrade paths,
or require paired encodings.

### Experimental query features

Before using extended range selectors, query-boundary functions, fill
modifiers, metadata labels, or concurrent rule evaluation, read
[PromQL, rules, and templates](references/promql-rules-and-templates.md).
Function allowlists, subquery restrictions, rule offsets, reserved labels, and
concurrency limits materially affect correctness.

## Scraping and histogram quick reference

### Native and classic histogram controls

```yaml
global:
  scrape_native_histograms: true
  always_scrape_classic_histograms: true
  convert_classic_histograms_to_nhcb: true
```

Use only the controls required by the deployment. Per-target relabel labels can
override all three behaviors. Mixed classic and native samples at one timestamp
can make some histogram functions return no value.

### Protocol and naming compatibility

- Fix exporters to return an accepted protobuf, Prometheus text, or OpenMetrics
  content type; use `fallback_scrape_protocol` only deliberately.
- Set `metric_name_validation_scheme: legacy` globally or per job when an
  upgrade must preserve legacy name rejection.
- Configure `scrape_protocols` explicitly when created-timestamp zero injection
  must not change the default protocol preference.
- Use the requested escaping scheme and per-target controls when different
  exporters need different behavior.

## PromQL and rules quick reference

- A regex dot matches newlines; audit broad matchers after upgrading.
- Duration literals work as scalars, duration expressions support arithmetic,
  and the newest experimental helpers are named `min_of()` and `max_of()`.
- Histogram-aware functions have function-specific output typing and omission
  rules. Do not assume float behavior for mixed vectors.
- `anchored` and `smoothed` selectors accept only specific rate/reset
  functions, reject subqueries, and require rule offsets for reliable smoothed
  evaluation.
- Raw OTLP deltas are not counters. Query them with aligned
  `sum_over_time(...)` windows rather than `rate()` or `increase()`.
- Range-query sorting functions have no effect and now warn.
- Concurrent rule evaluation adds query load independently of the ordinary
  query concurrency settings.

## Remote I/O quick reference

- Remote-write HTTP/2 is opt-in. Enable it explicitly only when retaining that
  transport behavior is desired.
- Remote-read implementations must enforce requested selectors and return only
  matching results.
- Remote Write 1.0 cannot transport custom-bucket native histograms; use a
  compatible protocol or expect them to be rejected with a warning.
- Remote Write 2 uses start-timestamp terminology and has specific rejection
  semantics for too-old histogram samples.
- Validate queue configuration during configuration loading and migrate from
  deprecated remote-write self-metrics.
- Cross-host redirects strip credentials and configured authorization headers.

## OTLP choice points

Choose one delta strategy:

- `otlp-deltatocumulative` maintains in-memory cumulative state and resets it
  across restarts.
- Native delta ingestion stores raw deltas, is mutually exclusive with
  conversion, and requires delta-aware queries and explicit stream labeling.

Then decide translation strategy, resource and scope metadata promotion,
reserved type/unit labels, start-timestamp handling, and explicit-histogram
conversion. Read [OTLP ingestion](references/otlp-ingestion.md) before combining
these switches.

## Validation workflow

1. Determine the binary version, image variant, feature flags, and runtime
   configuration.
2. Read only the references relevant to the planned change.
3. Run `promtool check config` and `promtool check rules`, passing required
   syntax flags. Account for stdout/stderr behavior in pipelines.
4. Inspect `/api/v1/features`, status APIs, target relabel traces, query
   warnings, and the relevant self-metrics.
5. For storage changes, test restart, replay, compaction, and downgrade or
   downstream-reader compatibility on a copy of the data.
6. For query changes, compare annotations, histogram typing, sample limits, and
   read statistics against representative production expressions.
