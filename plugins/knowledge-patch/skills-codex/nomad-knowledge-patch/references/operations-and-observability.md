# Operations and Observability

## Bound server startup work

Nomad 1.10.1 adds `server.start_timeout`, which defaults to `30s`. Setup and
startup work such as keyring decryption must complete within the interval; on
timeout, the server logs the errors and exits (batch 1.10-upgrade).

```hcl
server {
  start_timeout = "1m"
}
```

## Allocation metrics require opt-in

Starting in 1.10.2, clients neither collect nor publish allocation metrics when
`telemetry.publish_allocation_metrics` is unset or `false`. Enable it explicitly
on clients that must export those metrics.

```hcl
telemetry {
  publish_allocation_metrics = true
}
```

## Evaluation metric label changes

For dispatch and periodic jobs, the `job` label on these metrics now contains the
parent job ID (batch 1.11-upgrade):

- `nomad.nomad.broker.wait_time`
- `nomad.nomad.broker.process_time`
- `nomad.nomad.broker.response_time`
- `nomad.nomad.broker.eval_waiting`

The `nomad.nomad.broker.eval_waiting` metric no longer has an `eval_id` label.
Update dashboards, recording rules, and alerts that depend on the former labels.

## CLI links and UI hints

Common CLI commands show web UI URL hints and accept `-ui` to open the generated
link (batch 1.10.0). Disable hints globally in server configuration or for one CLI
environment:

```hcl
ui {
  show_cli_hints = false
}
```

```shell
export NOMAD_CLI_SHOW_HINTS=0
```

The environment value may be `0` or `false`.

## Scheduler and node resource APIs

`num_schedulers` must be between zero and the machine's available CPU count.

The Go API `Node.Resources` and `Node.Reserved` fields, and the corresponding Read
Node API fields, are deprecated and never populated. Use `Node.NodeResources` and
`Node.ReservedResources` (since 1.11.0).

## Event stream additions

CSI volume and plugin events are included in the event stream (since 1.10.0).
Nomad variables also emit events (since 2.0.0), allowing consumers to observe
variable activity without polling.

## Identifier and rendezvous hash changes

In 2.0.5, Nomad-native service check IDs use SHA-256, Consul check IDs move from
SHA-1 to SHA-256, and service rendezvous hashes also use SHA-256. Generated IDs
and rendezvous hashes can therefore differ after an upgrade.

## API and operator response changes

Client allocation endpoints return `404`, rather than `500`, when an allocation's
node cannot be found (since 2.0.5). Treat it as a not-found condition.

`nomad operator root keyring remove` accepts an abbreviated root key ID as of
2.0.5.

## Executor failure status

Executor failures in the `exec`, `raw_exec`, `java`, and `qemu` task drivers
report exit code `-1` (batch 1.10.0). Monitoring and automation should distinguish
this from a normal process exit.
