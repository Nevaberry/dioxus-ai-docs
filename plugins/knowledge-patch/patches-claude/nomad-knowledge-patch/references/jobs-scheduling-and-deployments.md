# Jobs, Scheduling, and Deployments

## Submission and validation

### System job reschedule blocks

Starting in the `1.11-upgrade` guidance for Nomad 1.11.0, `system` and
`sysbatch` jobs fail submission when they contain a `reschedule` block. Earlier
versions silently ignored it. Remove these blocks before upgrading.

### Reserved task name

Since 1.11.0, tasks may not be named `alloc`, because the name breaks inter-task
filesystem isolation. Rename such tasks before submission.

### Negative core requests

Since 2.0.5, job validation and registration reject a negative `cores` value in
a task resource block. Job generators must not emit negative core requests.

### Scheduler count limit

Since 1.10.0, `num_schedulers` must be between zero and the machine's available
CPU count.

## Scheduling behavior

### Per-job allocation limit

The `job_max_count` server option defaults to `50000` and limits the sum of a
job's task-group `count` values when the job is submitted or scaled. Changing
the option does not affect existing jobs.

```hcl
server {
  job_max_count = 100000
}
```

### Zero-count task groups

Since 1.11.0, changing a task group in a service or batch job to `count = 0`
behaves like removing the group and stops all its non-terminal allocations.

### Plan-apply pipelining

Since 2.0.5, `plan_apply_pipeline` lets the leader have more outstanding Raft
writes while evaluating plans.

## Updates and deployments

### In-place update behavior

Since 1.10.0, affinity and spread updates are no longer treated as destructive.
During in-place updates, Nomad-native services interpolate correctly.

Task-level services, checks, and identities no longer interpolate jobspec
values from other tasks in the group.

### Preserve resources during CLI updates

Since 1.11.0, the job-update CLI accepts `-preserve-resources` to retain the
existing resource block while updating a job.

### System job deployments

Since 1.11.0, `system` jobs support deployments and controlled rollouts through
the job's `update` configuration, including blue/green and canary strategies.
Deployment status is available in the web UI and through `nomad deployment`
commands.

## Networking and disconnect behavior

### Deprecated disconnect fields

Since 1.10.0, previously deprecated task-group disconnect fields have no
effect. Use the `disconnect` block introduced in Nomad 1.8.

### Consul Connect with CNI

Since 1.11.0, Consul Connect permits `cni/*` network modes. The release marks
this combination as use-at-your-own-risk.

## Jobspec secrets and templates

### Secret blocks

Since 1.11.0, a `secret` block can fetch secrets from Nomad, Vault, or a custom
secret-provider plugin for jobspec interpolation. Reference a fetched value as
`${secret.secret_name.key}`.

### Service field interpolation

Since 2.0.5, task secrets interpolate into service check `Header` and `Args`
fields and service `Tags`.

### Initial render scripts

Since 2.0.5, `change_script` supports `run_on_first_render`. When enabled, the
script executes on the initial template render through the task's Poststart
lifecycle hook.

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

### Validation message language

Since 2.0.5, a variable validation block's `error_message` does not have to be
a full English sentence, so messages in other languages are accepted.
