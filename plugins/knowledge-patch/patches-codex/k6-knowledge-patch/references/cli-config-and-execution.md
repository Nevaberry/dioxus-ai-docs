# CLI, Configuration, and Execution

## Script execution

### Run TypeScript directly

k6 runs `.ts` files without a separate transpilation step (since 1.0.0):

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

### Detect unsupported HTTP method arguments

`http.get()` and `http.head()` warn about extra positional arguments (since
1.8.0). The arguments remain ignored, but the warning identifies calls whose
signatures should be corrected.

### Understand `--vus` with scenarios

When a script defines scenarios, `k6 run script.js --vus N` warns and replaces
them with one `shared-iterations` scenario containing `N` VUs and `N`
iterations (since 2.1.0). It is no longer silently ignored.

## End-of-test summaries

### Disable summaries with a mode

`--no-summary` and `K6_NO_SUMMARY` are deprecated. Use
`--summary-mode=disabled` or `K6_SUMMARY_MODE=disabled` (since 1.3.0):

```sh
k6 run --summary-mode=disabled script.js
```

The `legacy` summary mode is also deprecated and planned for removal in v2;
migrate to `compact` or `full` (since 1.3.0).

### Opt in to structured machine output

Use `--new-machine-readable-summary` or
`K6_NEW_MACHINE_READABLE_SUMMARY` to select the structured shape shared by
`--summary-export` and `handleSummary()` (since 1.5.0). That shape was planned
to become the v2 default:

```sh
k6 run script.js --new-machine-readable-summary --summary-export=summary.json
```

### Extend the summary callback timeout

Configure the former fixed 120-second `handleSummary()` budget with
`handleSummaryTimeout` or `K6_HANDLE_SUMMARY_TIMEOUT` (since 2.2.0):

```javascript
export const options = { handleSummaryTimeout: '5m' };
```

## Feature flags and configuration behavior

### Discover and enable features

Enable experimental behavior with repeated or comma-separated `--features`,
`K6_FEATURES`, or `features` in `config.json` (since 2.1.0). `k6 features` and
`k6 features --json` show available flags and lifecycle state. Enabled flags
become metric tags and survive archives and Cloud-worker execution.

The first flag, `native-histograms`, stores trend metrics in experimental
native histograms:

```sh
K6_FEATURES=native-histograms k6 run script.js
```

### Merge tags or freeze the environment

The experimental `merge-run-tags` flag merges tags per key across
configuration layers, with higher-priority layers winning conflicts (since
2.2.0). Without it, a higher layer replaces the whole tag map. The
experimental `freeze-env` flag freezes `__ENV`; mutation raises `TypeError` in
strict mode instead of leaking across iterations and scenarios:

```sh
k6 run --features merge-run-tags,freeze-env script.js
```

## Failure and process status

### Identify an explicitly failed test

Status consumers can distinguish a test marked by `execution.test.fail()`
through `ExecutionStatusMarkedAsFailed` (since 1.6.0).

### Interpret Cloud aborts

On v2, a Cloud run aborted by the system, a limit, a script error, the user, or
a timeout exits `97`; successful runs remain `0` and threshold aborts remain
`99` (since 2.0.0). CI must treat `97` as failure.

## Local APIs and dashboards

### Enable the HTTP API explicitly

The HTTP API does not listen on `localhost:6565` by default in v2. Enable it
with `--address` or `K6_ADDRESS` (since 2.0.0):

```sh
k6 run --address=localhost:6565 script.js
```

### Use the built-in web dashboard

The web dashboard is built into the v2 binary; a separate xk6-dashboard
extension is unnecessary (since 2.0.0):

```sh
k6 run --out=web-dashboard script.js
```

## Logging and diagnostics

### Inspect complex values

`console.log()` traverses nested arrays and objects, renders functions and
classes as `"[object Function]"`, and marks cycles as `"[Circular]"` instead of
collapsing the value (since 1.5.0). It also renders `ArrayBuffer` bytes and
typed-array names, lengths, and values, including nested values (since 1.6.0).

### Diagnose automatic provisioning

Automatic extension provisioning emits normal k6 log entries for artifact
resolution, cache hits, downloads, retries, and cache pruning at their
corresponding levels (since 1.8.0).

## Containers and release tags

### Run as the numeric image user

The container image selects numeric UID `12345` rather than the named `k6`
user (since 1.1.0), avoiding a required `runAsUser` override in Kubernetes pod
manifests.

### Pin the intended release line

In v2 release tooling, prereleases and maintenance releases from older majors
do not update Docker `:latest` or GitHub's latest-release marker. Floating
`:vN` tags such as `grafana/k6:v1` track a selected major line (since 2.0.0).
