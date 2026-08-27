---
name: gitlab-ci-knowledge-patch
description: GitLab CI/CD
version: "19.2"
license: MIT
metadata:
  author: Nevaberry
---


# GitLab CI/CD Knowledge Patch

Use this skill when writing or reviewing pipeline configuration, operating runners,
adopting GitLab automation features, or preparing a GitLab platform upgrade. Begin
with the breaking-change checks below, then open the reference file for the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [Pipeline Configuration and Credentials](references/pipeline-configuration.md) | Security-template pipeline selection, typed inputs, job-token pushes, merge trains, and runner timeouts |
| [Operations, Observability, and Automation](references/operations-and-automation.md) | CI/CD analytics, component usage, OTLP telemetry, Duo CLI, custom and foundational flows, and pipeline assistance |
| [GitLab Platform Upgrade Guidance](references/platform-upgrades.md) | Required upgrade stops, PostgreSQL and Redis, registry migrations and repairs, removed packages and services, Helm changes, and RPM cleanup |
| [Security, Secrets, and Governance](references/security-and-governance.md) | Fine-grained job-token permissions, Secrets Manager, scheduled policies, dependency remediation, and security fixes |

## Working method

1. Identify whether the task concerns pipeline YAML, runner configuration, GitLab
   administration, or an upgrade.
2. Confirm the deployment type and tier before recommending a feature; several
   capabilities differ across GitLab.com, Self-Managed, and Dedicated.
3. For upgrades, identify the current version, target version, installation method,
   database, registry backend, operating system, and bundled services.
4. Preserve explicit feature flags and opt-ins. Do not present beta or limited-
   availability behavior as a universal default.
5. Validate configuration in a non-production project or maintenance window, then
   record rollback or recovery steps before applying the change broadly.

## Upgrade and breaking-change triage

### Follow every required upgrade stop

GitLab 19 upgrades must stop at `19.2`, `19.5`, `19.8`, and `19.11` when those
versions fall between the installed and target releases. Read every intervening
release note and the notes for the actual installation method. Do not jump directly
to the target merely because the package manager permits it.

### Prepare the database and external services first

Before installing GitLab 19:

- Upgrade packaged PostgreSQL 16 or an external PostgreSQL deployment to
  PostgreSQL 17.
- Replace external Redis 6 with Redis 7.0 or later, or Valkey 7.2 or later. The
  Redis bundled with the Linux package is already version 7.
- For Helm or Operator installations, externalize PostgreSQL, Redis, and object
  storage if they use the removed bundled Bitnami PostgreSQL, Bitnami Redis, or
  MinIO charts.
- Externalize Spamcheck. Its bundled Linux-package and Helm-chart forms are gone;
  no Spamcheck data migration is required.

### Remove or migrate discontinued package integrations

- Migrate bundled Mattermost users to a standalone deployment and remove or
  comment every `mattermost[...]` key in `/etc/gitlab/gitlab.rb` before upgrading.
  Otherwise `gitlab-ctl reconfigure` aborts. The versioned `check-config` command
  does not detect this condition.
- Move Ubuntu 20.04 Linux-package hosts to Ubuntu 22.04 or another supported OS;
  GitLab 18.11 is the final package release for Ubuntu 20.04.
- Move openSUSE Leap 15.6, SLES 12.5, and SLES 15.6 package installations that
  must stay on SUSE to Docker; their final GitLab package release is 18.11.

### Migrate registry storage deliberately

The legacy `s3` registry driver is removed in GitLab 19 and aliases to `s3_v2`.
Configure `s3_v2` directly. For a non-AWS S3-compatible backend, use a complete URI
for `regionendpoint`; set `checksum_disabled` if enhanced upload checksums are
rejected. Deletion still sends CRC32, so the backend itself must support it.

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

### Account for the Helm ingress default

The GitLab 19 Helm chart defaults to Gateway API with Envoy Gateway. The bundled
NGINX Ingress can be explicitly restored until its proposed removal in GitLab 20.
Externally managed Ingress or Gateway API controllers and Linux-package NGINX are
not affected by this chart default.

### Avoid known point-release failures

- Upgrade directly to `19.2.1` or later rather than `19.2.0` on Linux-package
  installations that use local AI Gateway or Duo Agent Platform endpoints. If
  `19.2.0` cleared them, restore the URLs under **Admin area** > **GitLab Duo** >
  **Configuration** > **Service endpoints**.
- In `19.0.0` and `19.0.1`, registry metadata database `prefer` mode can make
  `/gitlab/v1/` return HTTP 500. Temporarily disable the metadata database, then
  remove the override after reaching `19.0.2` or later.
- Geo sites on `19.0.0` or `19.0.1` can omit OCI image-index tags. Upgrade both
  sites to `19.0.2` or later and manually resync container repositories when the
  default verification interval is too slow.

See [GitLab Platform Upgrade Guidance](references/platform-upgrades.md) for exact
recovery configuration, affected installation methods, and post-upgrade cleanup.

## Pipeline configuration quick reference

### Select security-scanner pipeline behavior explicitly

Set `AST_ENABLE_MR_PIPELINES` to choose merge-request or branch pipelines when an
MR is open. Stable security templates default to branch pipelines; Latest templates
default to MR pipelines. The setting applies to every security scanning template
except `API-Discovery.gitlab-ci.yml`, whose own default is branch pipelines.

```yaml
variables:
  AST_ENABLE_MR_PIPELINES: "true"
```

### Address individual array inputs

Use the `[]` operator in CI/CD input interpolation when a job needs one array
element. The Run pipeline UI can also collect multiple allowed options into the
array supplied to the pipeline.

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

### Constrain job-token access and pushes

Prefer resource-specific job-token permissions for least privilege. Cross-project
pushes require the target project to opt in and the triggering user to have at
least the Developer role there. In GitLab 19.0, also enable the disabled-by-default
`allow_push_to_allowlisted_projects` feature flag.

### Tune merge trains and runner startup

Premium and Ultimate Self-Managed or Dedicated instances can set merge-train
pipeline concurrency per project or instance instead of using the old fixed limit
of 20. Use `1` to test merge requests sequentially against a clean target branch.
Runner configuration also supports a configurable prepare-stage timeout.

## Operations and automation quick reference

### Export runner job traces

GitLab Runner 19.0 negotiates instrumentation and can export OTLP telemetry. Its
initial trace signal is the `job_execution` span. Confirm collector connectivity
and sampling before relying on traces for incident diagnosis.

### Centralize scheduled pipelines

Scheduled pipeline execution policies define one schedule in a security policy
project and enforce it across projects in scope without editing each
`.gitlab-ci.yml`. Each policy starts its own daily, weekly, or monthly pipeline,
independent of commits, with time-zone, execution-window, and target-branch controls.

### Choose the right automation surface

- Use the Duo CLI interactively through `glab` or as a standalone tool, and use
  headless mode in CI/CD.
- Use YAML custom flows for reusable multi-agent work that needs triggers,
  approvals, feedback, or controlled identities.
- Hand work from Agentic Chat to the Developer, Code Review, or Fix CI/CD Pipeline
  foundational flow after the user approves the handoff.
- Use the CI Expert Agent to create, debug, or optimize pipelines from repository
  context.
- Use the Fix CI/CD Pipeline Flow when failure classification, child-pipeline
  traversal, or merge-request code suggestions are needed.

See [Operations, Observability, and Automation](references/operations-and-automation.md)
for availability and behavior details.

## Security response quick reference

Install `19.2.1` immediately on affected Self-Managed `19.2` systems. Equivalent
fixed releases are `19.1.3` and `19.0.5`; GitLab.com is already patched and
Dedicated customers do not need to act. Review exposure involving Workhorse,
pipeline schedule inputs, merge-request discussions, protected-branch approvals,
pipeline test reports, Duo Code Review, and workflow tool-governance enforcement.

For preventive controls, use explicitly requested Secrets Manager access, narrow
job-token resources, centrally enforced schedules, and dependency scanning
auto-remediation. Open [Security, Secrets, and Governance](references/security-and-governance.md)
before enabling beta functionality or credit-consuming major-version remediation.
