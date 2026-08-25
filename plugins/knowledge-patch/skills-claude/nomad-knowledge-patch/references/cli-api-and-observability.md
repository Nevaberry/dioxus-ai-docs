# CLI, API, and Observability

## API response changes

### ACL self-token status codes

In the `1.10-upgrade` guidance for Nomad 1.10.1,
`/v1/acl/token/self` returns `200` with a body indicating ACLs are disabled when
ACLs are off. It returns `403` when ACLs are on but no valid token is present.
Both cases previously returned `404`.

### Node resource fields

In the `1.11-upgrade` guidance, the Go API fields `Node.Resources` and
`Node.Reserved`, and their Read Node API equivalents, are deprecated and never
populated. Use `Node.NodeResources` and `Node.ReservedResources`.

### Missing allocation nodes

Since 2.0.5, client allocation endpoints return `404` rather than `500` when an
allocation's node cannot be found. API consumers can handle this as not found.

## CLI behavior and flags

### Web UI links

Since 1.10.0, common CLI commands show web UI URL hints by default and accept
`-ui` to open the generated link. Disable hints server-side or for one CLI
environment:

```hcl
ui {
  show_cli_hints = false
}
```

```shell
NOMAD_CLI_SHOW_HINTS=0 nomad job status
```

The environment variable also accepts `false`.

### Allocation group selection

Since 1.10.0, `nomad alloc exec`, `nomad alloc logs`, and `nomad alloc fs`
accept `-group`.

### Structured job-plan output

Since 2.0.5, `nomad job plan` accepts `-json-output` and `-t` for structured
plan output.

```shell
nomad job plan -json-output ./job.nomad
```

### Abbreviated root key IDs

Since 2.0.5, `nomad operator root keyring remove` accepts an abbreviated key ID.

## Event streams

### CSI and plugin events

Since 1.10.0, the event stream includes CSI volume and plugin events.

### Variable events

Since 2.0.0, Nomad variables emit events, so consumers can observe variable
activity without polling.

## Metrics and generated identifiers

### Allocation metrics opt-in

Starting in Nomad 1.10.2, clients no longer collect or publish allocation
metrics when `telemetry.publish_allocation_metrics` is unset or false. Set it
explicitly on clients that must continue exporting those metrics.

```hcl
telemetry {
  publish_allocation_metrics = true
}
```

### Eval broker labels

For dispatch and periodic jobs, the `job` label on these metrics now contains
the parent job ID:

- `nomad.nomad.broker.wait_time`
- `nomad.nomad.broker.process_time`
- `nomad.nomad.broker.response_time`
- `nomad.nomad.broker.eval_waiting`

The `nomad.nomad.broker.eval_waiting` metric also no longer has an `eval_id`
label. Update queries and alerts that rely on the old labels.

### Check IDs and rendezvous hashes

Since 2.0.5, Nomad-native service check IDs use SHA-256, Consul check IDs have
moved from SHA-1 to SHA-256, and service rendezvous hashes use SHA-256.
Generated identifiers and rendezvous hashes can differ after an upgrade.

## Evaluation and placement diagnostics

Since 1.11.0, `nomad eval status` shows related evaluations, placed allocations,
plan annotations, failed placements, and preemptions, with more fields shown
without `-verbose`. Reconciler annotations describe the intended plan before
node-feasibility checks.

`nomad alloc status -verbose` adds evaluated and rejected node counts and node
scores. The Go API's `Evaluations.Info` populates `RelatedEvals`.
