---
name: github-actions-knowledge-patch
description: GitHub Actions
license: MIT
version: null
metadata:
  author: Nevaberry
---

# GitHub Actions Knowledge Patch

Use this skill when writing, reviewing, securing, or operating GitHub Actions
workflows and runner fleets. Check the security-sensitive behavior first,
especially for privileged pull-request workflows, cache writes, action
allowlists, and self-hosted runner updates.

## Reference index

| Reference | Topics |
| --- | --- |
| [security-trust-and-policy.md](references/security-trust-and-policy.md) | Privileged pull-request refs, environment protections, cache trust, checkout safeguards, allowed actions, execution rulesets, and OIDC identity |
| [self-hosted-runners.md](references/self-hosted-runners.md) | Registration and update gates, enforcement dates and brownouts, fleet discovery, custom autoscaling, and runner interfaces |
| [workflow-semantics-and-limits.md](references/workflow-semantics-and-limits.md) | Concurrent steps, cancellation behavior, reusable-workflow limits, and manual-dispatch inputs |
| [hosted-runner-images.md](references/hosted-runner-images.md) | Windows Server 2025 with Visual Studio 2026, macOS 26 Intel, and M2 macOS labels |

## Apply this patch

1. Identify the event, execution ref, trust boundary, permissions, environment,
   and cache scope before changing a workflow.
2. Treat `pull_request_target` and pull-request-derived `workflow_run` jobs as
   privileged contexts. Do not fetch or execute fork code unless the workflow
   has an explicit, reviewed trust design.
3. For self-hosted runners, check both the registration minimum and the moving
   release-age requirement; they are separate gates.
4. Confirm that preview-only syntax, images, clients, and policy controls are
   available to the repository or enterprise before relying on them.
5. Load the indexed reference for full exceptions, dates, labels, and rollout
   details before implementing a change.

## Security and trust changes

### Re-evaluate `pull_request_target` refs

Since December 8, 2025, `pull_request_target` always loads its workflow and
commit from the default branch:

- `GITHUB_REF` is the default branch.
- `GITHUB_SHA` is the latest commit on that branch.
- This remains true when the pull request targets a different base branch.

Environment branch protections now evaluate the execution ref rather than
`HEAD_REF`. For `pull_request`, `pull_request_review`, and
`pull_request_review_comment`, that ref is `refs/pull/number/merge`; for
`pull_request_target`, it is the default branch. Update environment branch
patterns if they assumed the older ref behavior.

### Expect read-only caches in untrusted default-branch contexts

The cache token is read-only when an untrusted actor can trigger an event and
both the execution and cache scope use the shared default-branch SHA. Restores
continue to work. A blocked save emits a warning and does not fail the job.

Populate any required cache from a trusted workflow such as `push`. Do not
treat the warning as evidence that the cache was updated. The detailed
reference lists the events that retain read-write access.

### Keep fork checkout protection enabled

`actions/checkout` v7 rejects fork pull-request head or merge checkouts in:

- `pull_request_target`; and
- `workflow_run` when the originating event is a `pull_request*` event.

The check covers fork repositories, pull-request head or merge refs, and their
corresponding SHAs when supplied with `repository` or `ref`. Same-repository
pull requests and ordinary `pull_request` runs are unaffected.

Use `allow-unsafe-pr-checkout` only after an explicit security review. It does
not protect shell-based fetches or checkouts of unrelated repositories.

### Apply policy before a run starts

Public-preview workflow execution protections use rulesets at enterprise,
organization, and repository scope. Actor rules can allowlist users,
repository roles, GitHub Apps, Copilot, or Dependabot. Event rules can
allowlist triggers such as `push`, `pull_request`, `pull_request_target`, and
`workflow_dispatch`.

These rules are evaluated before a run starts and are configured separately
from general Actions settings under **Actions > Policies**. Use evaluate mode
to preview enforcement, and use custom properties to target repositories from
organization-wide rulesets.

Action and reusable-workflow allowlisting is also available on Free, Team, and
Enterprise plans. Repository policy can restrict execution to an explicitly
selected set of actions and reusable workflows.

### Bind OIDC decisions to a job

OIDC tokens include `check_run_id` in addition to claims such as `run_id` and
`run_attempt`. Use `check_run_id` when an external authorization or audit
system must identify the exact job and compute that requested a token.

## Self-hosted runner enforcement

### Enforce both version gates

Runner `2.329.0` is the minimum for configuring or re-registering a
self-hosted runner on the new platform. This is not a permanent execution
floor. Every runner release, including patch releases, must be installed
within 30 days of publication or the service stops queuing jobs to that
runner.

Auto-update satisfies the rolling requirement when the update service is
reachable. Fleets with auto-update disabled need a regular manual upgrade
process. A critical security release pauses job queuing until installed and
does not receive the normal grace period.

### Plan for cloud enforcement

Full enforcement begins:

| Deployment | Date |
| --- | --- |
| Enterprise Cloud with Data Residency | July 31, 2026 |
| Enterprise Cloud | September 25, 2026 |
| Enterprise Server | Not affected |

Before the standard Enterprise Cloud date, registration and runtime
brownouts occur on specified August and September dates. Consult
[self-hosted-runners.md](references/self-hosted-runners.md) for every window
before scheduling fleet work.

After enforcement, versions below `2.329.0` cannot register or re-register.
Already registered runners below the moving execution floor stop running
jobs.

### Audit the whole fleet

Use the self-hosted-runners REST API with API version `2026-03-10` to obtain
runner versions. Registration audit-log events also include versions, but
they are not a complete inventory because they exist only when a runner
registers. Runtime annotations identify outdated runners before enforcement.

## Workflow behavior and limits

### Coordinate concurrent steps explicitly

Steps can run asynchronously with `background: true` while keeping separate
logs. Use `wait` for a named earlier background step, `wait-all` for all
earlier background steps, and `cancel` for graceful termination. `parallel`
is shorthand for starting a group as background steps and then waiting.

```yaml
jobs:
  integration:
    runs-on: ubuntu-latest
    steps:
      - name: Start service
        run: ./serve
        background: true
      - name: Exercise service
        run: ./test
```

On runner `2.336.0`, canceled background steps no longer affect the job
result, and cancellation waits for the worker to finish. Pin or gate runner
versions when workflow correctness depends on these semantics.

### Use the expanded workflow limits

- A run can nest up to 10 reusable workflows.
- A run can call up to 50 reusable workflows in total.
- `workflow_dispatch` accepts up to 25 top-level inputs, including API starts.

These replace the earlier limits of four nested reusable workflows, 20 total
reusable workflows, and 10 manual-dispatch inputs.

## Runner interfaces and hosted images

Runner `2.336.0` supports `$GITHUB_ARTIFACTS` environment files and exposes
the effective cache mode through `ACTIONS_CACHE_MODE`. Workflows and actions
that consume either interface require that runner version or later.

For custom autoscaling outside Kubernetes, the public-preview
`actions/scaleset` Go client handles runner scale-set API orchestration.
Infrastructure provisioning, scaling, and destruction remain the
integrator's responsibility. Actions Runner Controller remains the
recommended Kubernetes implementation.

Current hosted-runner choices covered here include:

- public-preview `windows-2025-vs2026` for Windows Server 2025 with Visual
  Studio 2026 validation;
- public-preview `macos-26-large` for macOS 26 on Intel larger runners; and
- generally available M2 xlarge labels from macOS 13 through macOS 15,
  including `macos-latest-xlarge`.

Read [hosted-runner-images.md](references/hosted-runner-images.md) before
selecting a label; preview status, architecture, and image migration affect
reproducibility.
