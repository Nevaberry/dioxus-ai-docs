# Pipeline Configuration and Credentials

## Choose AST scanner pipeline types

Since 18.0, `AST_ENABLE_MR_PIPELINES` controls whether security scanners create
merge-request or branch pipelines when a merge request is open.

```yaml
variables:
  AST_ENABLE_MR_PIPELINES: "true"
```

Stable security templates continue to default to branch pipelines, while Latest
templates default to merge-request pipelines. Override the default explicitly when
a project requires the other behavior. The variable applies to all security
scanning templates except `API-Discovery.gitlab-ci.yml`; API Discovery itself
defaults to branch pipelines in 18.0.

## Index array input elements

Since 19.0, CI/CD input interpolation accepts the `[]` array index operator. Use it
when a job needs one element and should not add a separate array-processing step.

```yaml
spec:
  inputs:
    targets:
      type: array
      default: [staging, production]
---
show-first-target:
  script:
    - echo "$[[ inputs.targets[0] ]]"
```

## Collect multiple pipeline input options

Since 19.0, an array input with declared options can be presented as a multi-select
control in the **Run pipeline** UI. GitLab combines the selected values into an
array such as `["option1","option2"]`, allowing one run to target several selected
environments or tasks.

## Push across projects with a job token

Since 19.0, `CI_JOB_TOKEN` can push to a different project only when all of these
conditions hold:

- The target project opts in to job-token pushes from the source.
- The user who started the pipeline has at least the Developer role in the target.
- The `allow_push_to_allowlisted_projects` feature flag is enabled.

That feature flag is disabled by default in GitLab 19.0. Treat target-project
allowlisting and the triggering user's authorization as separate requirements.

## Configure merge-train concurrency

Since 19.0, Premium and Ultimate customers on GitLab Self-Managed and GitLab
Dedicated can replace the old fixed maximum of 20 parallel merge-train pipelines
with either a per-project or instance-wide limit. A limit of `1` processes merge
requests one at a time, testing each against a clean target branch.

## Configure the runner prepare-stage timeout

GitLab Runner 19.0 makes the prepare-stage timeout configurable in runner
configuration. Set it deliberately for environments where provisioning, executor
startup, or dependency preparation legitimately takes longer; avoid masking a
stalled preparation phase with an unnecessarily broad timeout.
