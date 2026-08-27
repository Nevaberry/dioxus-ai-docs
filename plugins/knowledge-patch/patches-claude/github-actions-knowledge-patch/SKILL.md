---
name: github-actions-knowledge-patch
description: GitHub Actions
version: null
license: MIT
metadata:
  author: Nevaberry
---


# GitHub Actions Knowledge Patch

Use this skill when writing, reviewing, securing, or operating GitHub Actions
workflows and runner fleets. Check trust boundaries first for workflows that
run with elevated permissions or consume pull-request-controlled input, then
verify runner versions and preview availability before relying on newer
interfaces.

## Reference index

| Reference | Topics |
| --- | --- |
| [security-trust-and-policy.md](references/security-trust-and-policy.md) | Privileged pull-request refs, cache trust, checkout safeguards, approval holds, action allowlists, execution rulesets, and OIDC identity |
| [self-hosted-runners.md](references/self-hosted-runners.md) | Registration and update gates, enforcement dates and brownouts, fleet discovery, custom autoscaling, and runner environment interfaces |
| [workflow-semantics-and-limits.md](references/workflow-semantics-and-limits.md) | Concurrent steps, cancellation behavior, reusable-workflow limits, manual-dispatch inputs, and self-repository references |
| [hosted-runner-images.md](references/hosted-runner-images.md) | Windows Server 2025 with Visual Studio 2026, macOS 26 Intel, and M2 macOS labels |

## Apply this patch

1. Identify the event, execution ref, actor trust, permissions, environment,
   and cache scope before changing a workflow.
2. Treat `pull_request_target` and pull-request-derived `workflow_run` jobs as
   privileged contexts. Do not fetch or execute fork code without an explicit,
   reviewed trust design.
3. Keep the fork protection in `actions/checkout` enabled unless the workflow
   has undergone a security review.
4. For self-hosted runners, check both the registration minimum and the moving
   release-age requirement; they are separate gates.
5. Gate features that require runner `2.336.0`, including concurrent-step
   behavior, new environment interfaces, and `$/` repository references.
6. Confirm that public-preview images, clients, and policy controls are
   available at the required repository or enterprise scope.
7. Open the indexed reference before implementing security policy, scheduling
   fleet work, or choosing a hosted-runner label.

## Security and trust changes

### Re-evaluate `pull_request_target` refs

`pull_request_target` always loads its workflow and commit from the default
branch. `GITHUB_REF` is the default branch and `GITHUB_SHA` is the latest
commit on that branch, including when the pull request targets another base
branch.

Environment branch protections evaluate the execution ref rather than
`HEAD_REF`. For `pull_request`, `pull_request_review`, and
`pull_request_review_comment`, the execution ref is
`refs/pull/number/merge`; for `pull_request_target`, it is the default branch.
Update environment branch patterns that assumed the previous behavior.

### Expect read-only caches in untrusted default-branch contexts

The cache token is read-only when an untrusted actor can trigger an event and
both the execution and cache scope use the shared default-branch SHA. Restores
still work. A blocked save emits a warning without failing the job.

Populate required caches from a trusted workflow such as `push`; do not treat
the warning as proof that a cache was updated. See the security reference for
the events that retain read-write access.

### Keep fork checkout protection enabled

`actions/checkout` v7 rejects fork pull-request head or merge checkouts in
`pull_request_target` and in `workflow_run` when the originating event is a
`pull_request*` event. Same-repository pull requests and ordinary
`pull_request` runs are unaffected.

Use `allow-unsafe-pr-checkout` only after explicit review. The checkout action
cannot protect shell-based fetches or checkouts of unrelated repositories.

### Account for automatic approval holds

On github.com, certain workflow runs identified as potentially malicious are
automatically held in public repositories. A repository collaborator with
write access must approve a held run through an authenticated web session.
No repository configuration is required, and GitHub Enterprise Server is not
covered.

### Apply policy before a run starts

Action and reusable-workflow allowlisting is available on Free, Team, and
Enterprise plans. Repository policy can restrict execution to an explicitly
selected set of actions and reusable workflows.

Public-preview workflow execution protections add rulesets at enterprise,
organization, and repository scope. Actor and event rules are evaluated before
a run starts. These protections are configured separately from general Actions
settings under **Actions > Policies**.

Use evaluate mode to preview enforcement, and use custom properties to target
repositories from organization-wide rulesets.

### Bind OIDC decisions to a job

OIDC tokens include `check_run_id` alongside claims such as `run_id` and
`run_attempt`. Use `check_run_id` when an external authorization or audit
system must identify the exact job and compute that requested a token.

## Self-hosted runner enforcement

### Enforce both version gates

Runner `2.329.0` is the minimum for configuring or re-registering a
self-hosted runner on the new platform. It is not a permanent execution floor.
Every runner release, including patch releases, must be installed within 30
days of publication or the service stops queuing jobs to that runner.

Auto-update satisfies the moving requirement when its update service is
reachable. Fleets with auto-update disabled need a regular manual upgrade
process. A critical security release pauses job queuing until installed and
does not receive the normal grace period.

### Plan for cloud enforcement

| Deployment | Full enforcement |
| --- | --- |
| Enterprise Cloud with Data Residency | July 31, 2026 |
| Enterprise Cloud | September 25, 2026 |
| Enterprise Server | Not affected |

Registration-only and registration-and-runtime brownouts precede standard
Enterprise Cloud enforcement. Consult
[self-hosted-runners.md](references/self-hosted-runners.md) for every date and
window before scheduling fleet work.

### Audit the whole fleet

Use the self-hosted-runners REST API with API version `2026-03-10` to obtain
runner versions. Registration audit-log events include versions but are not a
complete inventory because they exist only when a runner registers. Runtime
annotations identify outdated runners before enforcement.

### Separate autoscaling orchestration from infrastructure

The public-preview `actions/scaleset` Go client handles runner scale-set API
orchestration for custom autoscalers outside Kubernetes. Infrastructure setup,
provisioning, scaling, and runner destruction remain the integrator's
responsibility. Actions Runner Controller remains the recommended Kubernetes
implementation.

## Workflow behavior and limits

### Coordinate concurrent steps explicitly

Steps can run asynchronously with `background: true` while retaining separate
logs. Use `wait` for a named earlier step, `wait-all` for all earlier
background steps, and `cancel` for graceful termination. `parallel` starts a
group as background steps and then waits for them.

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

On runner `2.336.0`, canceled background steps no longer affect the job result,
and cancellation waits for the worker to finish. Gate runner versions when
workflow correctness depends on these semantics.

### Use the expanded workflow limits

- A run can nest up to 10 reusable workflows.
- A run can call up to 50 reusable workflows in total.
- `workflow_dispatch` accepts up to 25 top-level inputs, including API starts.

### Reference the current repository without checkout

A `uses:` value beginning with `$/` resolves an action or reusable workflow in
the same repository at the exact commit being run. It works anywhere `./`
references work, does not require checkout, is available on github.com, and
requires runner `2.336.0` or later.

## Runner interfaces and hosted images

Runner `2.336.0` supports `$GITHUB_ARTIFACTS` environment files and exposes the
effective cache mode through `ACTIONS_CACHE_MODE`. Workflows and actions that
consume either interface require that runner version or later.

Current hosted-runner choices in this patch include:

- public-preview `windows-2025-vs2026` for Windows Server 2025 with Visual
  Studio 2026 validation;
- public-preview `macos-26-large` for macOS 26 on Intel larger runners; and
- generally available M2 xlarge labels from macOS 13 through macOS 15,
  including `macos-latest-xlarge`.

Read [hosted-runner-images.md](references/hosted-runner-images.md) before
selecting a label; preview status, architecture, and image migration affect
reproducibility.
