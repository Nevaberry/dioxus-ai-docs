# Cloud and Secrets

## Cloud command structure

### Use explicit subcommands

The v2 CLI removes top-level `k6 login`, positional `k6 cloud script.js`, and
`--upload-only` (since 2.0.0). Use:

```sh
k6 cloud login
k6 cloud run script.js
k6 cloud upload script.js
```

InfluxDB credentials must be provided with `K6_INFLUXDB_*` variables rather
than `k6 login influxdb`.

### Configure scripts under `options.cloud`

`options.ext.loadimpact` is rejected in v2. Move those fields to
`options.cloud` (since 2.0.0):

```javascript
export const options = {
  cloud: { projectID: 12345, name: 'My Test' },
};
```

## Stacks, projects, tests, and load zones

### Set a default stack

Cloud login can save a default stack by slug, and Cloud commands can use its
slug or ID to resolve the default project (since 1.6.0). Override per run with
`K6_CLOUD_STACK_ID` or `options.cloud.stackID`. Stack information was planned
to become mandatory in v2:

```sh
k6 cloud login --token "$MY_TOKEN" --stack my-stack-slug
K6_CLOUD_STACK_ID=12345 k6 cloud run script.js
```

### List projects

The v2 Cloud CLI lists Grafana Cloud k6 projects as a table or JSON (since
2.0.0):

```sh
k6 cloud project list
k6 cloud project list --format=json
```

### List tests

`k6 cloud test list` lists load tests in a project (since 2.1.0). Project
resolution checks `--project-id`, then `K6_CLOUD_PROJECT_ID` or script cloud
`projectID`, then the configured stack's default project. Output is a table
unless `--json` is supplied:

```sh
k6 cloud test list --project-id 12345
k6 cloud test list --json
```

### List load zones

`k6 cloud load-zone list` lists public and private load zones available to the
configured stack (since 2.2.0). It prints a table by default or a JSON array
with `--json`.

## Secret sources

### Configure a source through the environment

`K6_SECRET_SOURCE` accepts the same source syntax as `--secret-source` (since
1.7.0):

```sh
K6_SECRET_SOURCE='mock=cool="not cool secret"' k6 run script.js
```

### Fetch from an HTTP endpoint

URL-based secret management can ask an HTTP service for secrets (since 1.5.0),
but that release provides only a mock implementation and no production-ready
external secret-manager integration.

### Account for local-execution differences

In v2, `k6 cloud run --local-execution` enables the built-in Cloud secret
source automatically, allowing `k6/secrets` to retrieve Grafana Cloud secrets
without `--secret-source=cloud`; use `--no-cloud-secrets` to opt out (since
2.0.0).

The maintained v1 line later changed in the opposite operational direction:
`k6 cloud run --local-execution` no longer enables the Cloud source by default
(since 1.8.1). This avoids an implicit source breaking scripts that configure
their own source. Check the actual major line rather than assuming the same
default across v1 and v2.

## Local Cloud execution

### Reuse an existing Cloud run

`k6 cloud run --local-execution` honors `K6_CLOUD_PUSH_REF_ID` (since 1.8.0).
Set it to an existing run ID to reuse that Cloud test run rather than creating
a new one:

```sh
K6_CLOUD_PUSH_REF_ID="$RUN_ID" k6 cloud run --local-execution script.js
```

### Control Cloud log streaming

Locally executed Cloud tests stream logs to the associated Grafana Cloud run
(since 2.2.0). Pass `--no-cloud-logs` when logs must remain local. Otherwise,
use Grafana secrets management and redaction for sensitive values that might
reach logs:

```sh
k6 cloud run --local-execution --no-cloud-logs script.js
```

### Supply scoped push credentials

An orchestrator that already provisioned a run can pass its scoped destination
and token through `K6_CLOUD_METRICS_PUSH_URL` and
`K6_CLOUD_TEST_RUN_TOKEN` (since 2.2.0).

## Cloud process and output behavior

### Treat aborted runs as failures

In v2, Cloud runs aborted by the system, a limit, a script error, the user, or
a timeout exit with status `97` instead of `0` (since 2.0.0). Successful runs
remain `0`; threshold aborts remain `99`.

### Filter browser failures

Browser API failures in Grafana Cloud Logs have `module=browser`, so they can
be filtered independently from other log sources (since 2.1.0).
