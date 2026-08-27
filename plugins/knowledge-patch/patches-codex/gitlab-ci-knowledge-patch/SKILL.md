---
name: gitlab-ci-knowledge-patch
description: GitLab CI/CD
version: "19.2"
license: MIT
metadata:
  author: Nevaberry
---


# GitLab CI/CD Knowledge Patch

Use this skill when configuring GitLab pipelines, runners, security features,
CI/CD inputs, Catalog components, or GitLab upgrades. Start with the quick
reference for high-impact compatibility decisions, then open the topic file
that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [Duo agents and flows](references/duo-agents-and-flows.md) | Duo CLI, custom and foundational flows, dependency remediation, CI Expert Agent, failure fixing |
| [Pipeline configuration](references/pipeline-configuration.md) | AST pipeline selection, array inputs, merge trains, scheduled pipeline policies |
| [Runner, Catalog, and analytics](references/runner-catalog-and-analytics.md) | Runner telemetry and timeouts, Catalog usage, project analytics |
| [Security, secrets, and job tokens](references/security-secrets-and-job-tokens.md) | Job-token permissions and pushes, Secrets Manager, security fixes |
| [Upgrade planning](references/upgrade-planning.md) | Required stops, databases, registry, operating systems, bundled services, Helm, Geo, package cleanup |

## Quick reference: upgrade blockers and removals

### Plan every required upgrade stop

For a GitLab 19 upgrade, include the required stops at `19.2`, `19.5`,
`19.8`, and `19.11`. Read all intervening release notes, including notes for
the installation method in use.

### Upgrade PostgreSQL before GitLab 19

GitLab 19.0 requires PostgreSQL 17 for every installation method. Upgrade a
packaged PostgreSQL 16 server or an external PostgreSQL deployment before
installing GitLab 19.

### Replace unsupported platforms and data services

- Replace external Redis 6 with Redis 7.0 or later or Valkey 7.2 before the
  upgrade. The Redis bundled with the Linux package is already version 7.
- Move off Ubuntu 20.04 packages; GitLab 18.11 is their final release.
- Linux package installations on openSUSE Leap 15.6, SLES 12.5, or SLES 15.6
  must move to Docker for GitLab 19.
- The Helm chart and Operator no longer bundle Bitnami PostgreSQL, Bitnami
  Redis, or MinIO. Configure external services before upgrading.

### Remove or externalize bundled services

- Move bundled Mattermost users to standalone Mattermost and remove or
  comment every `mattermost[...]` key in `/etc/gitlab/gitlab.rb` before
  reconfiguration.
- Deploy Spamcheck separately; GitLab 19.0 removes it from both the Linux
  package and Helm chart, with no data migration required.
- Prepare Helm installations for Gateway API with Envoy Gateway, the new
  default. Bundled NGINX Ingress can still be explicitly enabled for now.

### Migrate registry storage configuration

The legacy `s3` storage driver is removed and aliased to `s3_v2`. For
non-AWS S3-compatible storage, make `regionendpoint` a complete URI. Set
`checksum_disabled` when the backend rejects enhanced upload checksums, but
confirm deletion compatibility because deletion still sends CRC32.

```ruby
registry['storage'] = {
  's3_v2' => {
    'accesskey' => '<your-access-key>',
    'secretkey' => '<your-secret-key>',
    'bucket' => '<your-bucket>',
    'region' => '<your-region>',
    'regionendpoint' => 'https://storage.example.com',
    'pathstyle' => true,
    'checksum_disabled' => true
  }
}
```

### Avoid the affected patch releases

- Upgrade self-hosted Duo directly to 19.2.1 or later. A direct Linux package
  upgrade to 19.2.0 can clear local service endpoints and related settings.
- Upgrade Geo primary and secondary sites to 19.0.2 or later to avoid silently
  omitting OCI image-index tags on secondaries.
- On affected 19.2 self-managed systems, install 19.2.1 immediately. Equivalent
  fixed releases are 19.1.3 and 19.0.5.

See [Upgrade planning](references/upgrade-planning.md) for recovery steps,
registry metadata behavior, exact package cleanup, and installation-specific
details.

## Quick reference: pipeline configuration

### Choose AST merge-request behavior explicitly

Set `AST_ENABLE_MR_PIPELINES` to select merge-request or branch pipelines when
a merge request is open. Stable security templates default to branch
pipelines, while Latest templates default to merge-request pipelines.

```yaml
variables:
  AST_ENABLE_MR_PIPELINES: "true"
```

This applies to all security scanning templates except
`API-Discovery.gitlab-ci.yml`; API Discovery defaults to branch pipelines.

### Address individual array inputs

Use `[]` to interpolate one element of an array input directly.

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

The Run pipeline UI can also collect multiple options for an array input and
combine them into one array for the pipeline run.

### Control merge-train concurrency

Premium and Ultimate self-managed or Dedicated installations can configure a
per-project or instance-wide merge-train limit instead of the former fixed
maximum of 20 pipelines. Use `1` to process merge requests one at a time
against a clean target branch.

### Enforce scheduled pipeline policies centrally

Define daily, weekly, or monthly schedules once in a security policy project.
Each policy launches a separate pipeline across projects in scope without
editing their `.gitlab-ci.yml`, with time-zone, execution-window distribution,
and target-branch controls.

## Quick reference: tokens, secrets, and security

### Prefer least-privilege job tokens

Fine-grained job-token permissions can restrict a CI job token to named project
resources instead of inheriting the triggering user's full permissions. The
beta applies to GitLab.com and self-managed projects in all tiers.

### Gate cross-project job-token pushes

For a `CI_JOB_TOKEN` push to another project, the target must opt in and the
pipeline starter must have at least the Developer role there. The
`allow_push_to_allowlisted_projects` feature flag is also required and is
disabled by default.

### Request Secrets Manager access explicitly

GitLab Secrets Manager is an open beta for Premium and Ultimate customers on
GitLab.com and self-managed installations. Project and group Owners can scope
stored secrets to their project or group; pipeline jobs receive only secrets
they explicitly request. Treat the service as beta and assess production
readiness accordingly.

### Prioritize the security patch

The 19.2.1 release fixes 13 vulnerabilities, including three high-severity
issues affecting Workhorse information access, pipeline schedule input
authorization, and merge-request discussion denial of service. It also fixes
authorization and policy-enforcement paths involving protected branches,
pipeline reports, Duo Code Review, and Duo Workflows.

## Quick reference: runners and visibility

### Export Runner job telemetry

GitLab Runner can negotiate instrumentation, export through an OTLP client,
and emit its initial `job_execution` span. Runner configuration also exposes
the prepare-stage timeout.

### Inspect component consumers

Ultimate customers can view the projects consuming each CI/CD Catalog
component, their chosen versions, and whether those versions are current.
Outdated consumers appear first.

### Use project analytics on Dedicated

The limited-availability project CI/CD analytics view on GitLab Dedicated
shows pipeline performance trends and reliability metrics in the project UI.

## Quick reference: agents and flows

### Use terminal and CI/CD sessions

GitLab Duo CLI is generally available through `glab` or as a standalone tool.
It supports interactive chat and headless CI/CD use with project, pipeline,
and agent context. Administrators on self-managed and Dedicated installations
can disable it.

### Reuse controlled workflows

Custom flows are YAML-defined reusable workflows managed from a project or the
AI Catalog. They can coordinate multiple agents, approval or feedback
checkpoints, visibility, validated configuration, identities, and lifecycle
or pipeline triggers.

### Route failures to focused fixes

The Fix CI/CD Pipeline Flow classifies failures, follows child-pipeline
failures, honors project behavior from `AGENTS.md`, and can return code
suggestions when relevant files are already in a merge request diff.

See [Duo agents and flows](references/duo-agents-and-flows.md) for handoffs,
dependency remediation, the CI Expert Agent, tool controls, and flow execution
details.
