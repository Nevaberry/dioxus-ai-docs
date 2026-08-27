# CLI, Cloud, and Configuration

## End-of-test summaries

### Disable the summary explicitly (since 1.3.0)

`--no-summary` and `K6_NO_SUMMARY` are deprecated. Select the `disabled`
summary mode instead.

```sh
k6 run --summary-mode=disabled script.js
K6_SUMMARY_MODE=disabled k6 run script.js
```

The `legacy` mode is also deprecated and was planned for removal in v2. Use
`compact` or `full` for human-readable summaries.

### Structured summary data (since 1.5.0)

An opt-in machine-readable shape is shared by `--summary-export` and
`handleSummary()`. Enable it with `--new-machine-readable-summary` or
`K6_NEW_MACHINE_READABLE_SUMMARY`. The shape was planned to become the v2
default, so consumers should validate the schema they receive.

```sh
k6 run script.js --new-machine-readable-summary --summary-export=summary.json
```

### Summary callback timeout (since 2.2.0)

The former fixed 120-second `handleSummary()` budget is configurable through
the `handleSummaryTimeout` option or `K6_HANDLE_SUMMARY_TIMEOUT`.

```javascript
export const options = { handleSummaryTimeout: '5m' };
```

## Cloud account and project selection

### Default stack (since 1.6.0)

Cloud login can save a default Grafana Cloud stack. Commands use its slug or ID
to resolve the default project. Override it with `K6_CLOUD_STACK_ID` or
`options.cloud.stackID`. Stack information was announced as mandatory for v2.

```sh
k6 cloud login --token "$MY_TOKEN" --stack my-stack-slug
K6_CLOUD_STACK_ID=12345 k6 cloud run script.js
```

### Explicit Cloud commands (since 2.0.0)

The top-level `k6 login`, positional `k6 cloud script.js`, and `--upload-only`
were removed. Use explicit commands.

```sh
k6 cloud login
k6 cloud run script.js
k6 cloud upload script.js
```

Supply InfluxDB credentials through `K6_INFLUXDB_*` variables rather than
`k6 login influxdb`.

### Cloud option namespace (since 2.0.0)

`options.ext.loadimpact` is no longer accepted. Move its fields into
`options.cloud`.

```javascript
export const options = {
  cloud: { projectID: 12345, name: 'My Test' },
};
```

### List projects (since 2.0.0)

List Grafana Cloud k6 projects as a table or JSON.

```sh
k6 cloud project list
k6 cloud project list --format=json
```

### List tests (since 2.1.0)

`k6 cloud test list` resolves its project in this order: `--project-id`,
`K6_CLOUD_PROJECT_ID` or cloud `projectID`, then the configured stack's default
project. Output is a table unless `--json` is supplied.

```sh
k6 cloud test list --project-id 12345
k6 cloud test list --json
```

### List load zones (since 2.2.0)

`k6 cloud load-zone list` reports the public and private load zones available
to the configured stack. It produces a table by default or a JSON array with
`--json`.

```sh
k6 cloud load-zone list
k6 cloud load-zone list --json
```

## Local Cloud execution

### Cloud secret source behavior (since 2.0.0)

On the 2.0 line, `k6 cloud run --local-execution` automatically enabled the
built-in Cloud secret source, letting `k6/secrets` retrieve Grafana Cloud
secrets without `--secret-source=cloud`. `--no-cloud-secrets` opted out.

### Maintenance-line secret correction (since 1.8.1)

On the 1.8 maintenance line, local Cloud execution no longer enables the
Grafana Cloud secret source by default. This avoids an implicit default source
breaking scripts that configure their own source; configure the desired source
explicitly.

### Reuse an existing run (since 1.8.0)

Local execution honors `K6_CLOUD_PUSH_REF_ID`. Provide an existing run ID to
reuse the Cloud test run instead of creating another one.

```sh
K6_CLOUD_PUSH_REF_ID="$RUN_ID" k6 cloud run --local-execution script.js
```

### Stream or suppress Cloud logs (since 2.2.0)

Locally executed Cloud tests stream logs into the Grafana Cloud test run. Pass
`--no-cloud-logs` to keep logs local. Otherwise, use Grafana secrets management
and redaction for sensitive values that might reach the stream.

```sh
k6 cloud run --local-execution script.js
k6 cloud run --local-execution --no-cloud-logs script.js
```

### Scoped orchestrator credentials (since 2.2.0)

An orchestrator that already provisioned a test run can pass a scoped metrics
destination and token to local execution through
`K6_CLOUD_METRICS_PUSH_URL` and `K6_CLOUD_TEST_RUN_TOKEN`.

## Exit status and local control

### Cloud abort status (since 2.0.0)

A Cloud run aborted by the system, a limit, a script error, the user, or a
timeout exits with status `97`, not `0`. Successful runs remain `0`, and
threshold aborts remain `99`. Update CI to treat `97` as failure.

### Opt-in HTTP API (since 2.0.0)

The k6 HTTP API no longer listens on `localhost:6565` by default. Enable it
with `--address` or `K6_ADDRESS`.

```sh
k6 run --address=localhost:6565 script.js
```

## Configuration files and precedence

### Legacy path removal (since 2.0.0)

k6 no longer reads, migrates, or falls back to
`{USER_CONFIG_DIR}/loadimpact/config.json`. Move the file to
`{USER_CONFIG_DIR}/k6/config.json`, or regenerate it with `k6 cloud login`.

### `--vus` replaces configured scenarios (since 2.1.0)

`k6 run script.js --vus N` warns and replaces script-defined scenarios with a
`shared-iterations` scenario containing `N` VUs and `N` iterations. It is no
longer silently ignored when scenarios exist.

## Feature flags

### Enable and inspect flags (since 2.1.0)

Pass repeated or comma-separated `--features`, set `K6_FEATURES`, or use the
`features` key in `config.json`. Enabled features are added to metric tags and
preserved in archives and Cloud workers. Use `k6 features` or
`k6 features --json` to inspect flags and lifecycle status.

The first flag, `native-histograms`, makes trend metrics use experimental
native histograms.

```sh
k6 run --features native-histograms script.js
K6_FEATURES=native-histograms k6 run script.js
```

### Merge tags and freeze the environment (since 2.2.0)

The experimental `merge-run-tags` flag merges tags per key across
configuration layers, with the higher-priority layer winning individual
conflicts instead of replacing the entire tag map. The experimental
`freeze-env` flag freezes `__ENV`; mutation throws `TypeError` in strict mode
instead of persisting across iterations and scenarios.

```sh
k6 run --features merge-run-tags,freeze-env script.js
```

## Bundled dashboard and image tags

### Built-in web dashboard (since 2.0.0)

The web dashboard is included in the k6 binary and no longer needs the
separate xk6-dashboard extension.

```sh
k6 run --out=web-dashboard script.js
```

### Major-line Docker tags (since 2.0.0)

Prereleases and maintenance releases from older major lines no longer update
Docker `:latest` or the GitHub latest-release marker. Floating tags such as
`grafana/k6:v1` follow a selected major line; pin a full tag for reproducible
execution.
