# Jobs and Scheduling

## Reject invalid job shapes before submission

Starting with the 1.11-upgrade behavior, `system` and `sysbatch` jobs are rejected
when they contain a `reschedule` block. Earlier releases ignored the block. Remove
it before submitting or upgrading these jobs.

Tasks cannot be named `alloc` because that name breaks inter-task filesystem
isolation (since 1.11.0). Job validation and registration also reject negative
task resource `cores` values as of 2.0.5; job generators must never emit them.

## Per-job allocation ceiling

The `job_max_count` server option defaults to `50000` and limits the sum of all
task-group `count` values when a job is submitted or scaled. Changing the option
does not retroactively affect existing jobs.

```hcl
server {
  job_max_count = 100000
}
```

## System deployments and zero-count groups

System jobs support deployments through their `update` configuration (since
1.11.0), including canary and blue/green rollouts. Inspect their deployment state
in the web UI or with `nomad deployment` commands.

For service and batch jobs, setting a task group to `count = 0` now behaves like
removing it and stops all non-terminal allocations in that group.

## Safer updates and interpolation

Affinity and spread changes are no longer destructive (batch 1.10.0). During an
in-place update, Nomad-native services interpolate correctly. Task-level services,
checks, and identities no longer interpolate jobspec values from other tasks in
the group, so keep their dependencies within the owning task's interpolation
scope.

The job-update CLI accepts `-preserve-resources` when an updated job should retain
its existing resource block (since 1.11.0).

## Allocation command targeting

`nomad alloc exec`, `nomad alloc logs`, and `nomad alloc fs` accept `-group`,
allowing commands to select a task group explicitly.

## Evaluation and placement diagnostics

`nomad eval status` shows related evaluations, placed allocations, plan
annotations, failed placements, and preemptions, with more information available
without `-verbose` (since 1.11.0). Reconciler annotations describe the intended
plan before node-feasibility checks.

`nomad alloc status -verbose` adds evaluated and rejected node counts plus node
scores. In the Go API, `Evaluations.Info` now populates `RelatedEvals`.

## Structured plan output

The 2.0.5 CLI accepts `-json-output` and `-t` on `nomad job plan` for structured
plan output.

```shell
nomad job plan -json-output ./job.nomad
```

## Plan-apply throughput

The `plan_apply_pipeline` configuration lets the leader keep more outstanding
Raft writes while evaluating plans (since 2.0.5). Tune it deliberately and watch
evaluation and Raft behavior.

## Template scripts on first render

`change_script` supports `run_on_first_render` (since 2.0.5). When enabled, the
script runs for the initial template render through the task's Poststart lifecycle
hook.

```hcl
template {
  data        = "ready"
  destination = "local/ready"
  change_mode = "script"

  change_script {
    command             = "/bin/true"
    run_on_first_render = true
  }
}
```

## Network mode and validation text

Consul Connect permits `cni/*` network modes as of 1.11.0, but this combination is
explicitly use-at-your-own-risk.

A variable validation block's `error_message` no longer needs to be a complete
English sentence (since 2.0.5), so localized validation messages are accepted.
