# Pipeline Configuration

## Select AST merge-request or branch pipelines

Since 18.0, set `AST_ENABLE_MR_PIPELINES` to choose whether application
security testing uses a merge-request pipeline or a branch pipeline when a
merge request is open.

```yaml
variables:
  AST_ENABLE_MR_PIPELINES: "true"
```

Stable security templates continue to default to branch pipelines and Latest
templates default to merge-request pipelines, so set the variable when the
template default is not the desired behavior. The control applies to every
security scanning template except `API-Discovery.gitlab-ci.yml`. API Discovery
itself defaults to branch pipelines starting in 18.0.

## Index an array input element

Since 19.0, CI/CD input interpolation supports the `[]` array index operator.
Consume a single input element without adding a processing step.

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

## Select multiple pipeline input options

Since 19.0, an array input with options accepts multiple selections in the
Run pipeline UI. GitLab combines the selected values into an array such as
`["option1","option2"]`, allowing one run to act on several targets.

## Configure merge-train concurrency

Since 19.0, Premium and Ultimate customers on GitLab Self-Managed and GitLab
Dedicated can replace the former fixed maximum of 20 parallel merge-train
pipelines with a per-project or instance-wide limit. Set the limit to `1` to
process merge requests sequentially against a clean target branch.

## Enforce scheduled pipeline execution policies

Since 19.2, define a pipeline schedule once in a security policy project and
enforce it across every project in scope without editing each project's
`.gitlab-ci.yml`.

Each policy starts a separate pipeline independently of commit activity. The
schedule can be daily, weekly, or monthly and can specify a time zone,
execution-window distribution, and target branch.
