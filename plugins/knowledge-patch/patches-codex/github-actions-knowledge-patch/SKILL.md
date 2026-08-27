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
workflows and self-hosted runner fleets. Start with the execution event, ref,
permissions, code provenance, environment protections, and runner version;
several safeguards depend on those boundaries rather than on YAML alone.

## Reference index

| Reference | Topics |
| --- | --- |
| [security-trust-and-policy.md](references/security-trust-and-policy.md) | Approval holds, privileged pull-request refs, environment rules, cache trust, fork checkout protection, execution policy, action allowlists, and OIDC identity |
| [self-hosted-runners.md](references/self-hosted-runners.md) | Registration and release-age gates, enforcement and brownouts, fleet discovery, autoscaling, and runner interfaces |
| [workflow-semantics-and-limits.md](references/workflow-semantics-and-limits.md) | Same-repository references, concurrent steps, cancellation, reusable-workflow limits, and manual inputs |
| [hosted-runner-images.md](references/hosted-runner-images.md) | Windows Server 2025 with Visual Studio 2026, macOS 26 Intel, and M2 labels |

## Review the trust boundary first

Before changing a workflow, identify:

- the triggering event and who can trigger it;
- the execution ref and SHA;
- whether any checked-out or fetched code is pull-request-controlled;
- the effective `GITHUB_TOKEN`, OIDC, secret, and environment permissions;
- the cache scope and whether the run may save to it; and
- the runner ownership, isolation, and installed version.

Treat `pull_request_target` and pull-request-derived `workflow_run` jobs as
privileged. Never execute fork-controlled code there without an explicit,
reviewed trust design.

## Account for automatic malicious-workflow holds

On github.com, some runs in public repositories that are identified as
potentially malicious are held automatically. No repository configuration is
needed. The run begins only after a repository collaborator with write access
approves it in an authenticated web session, then proceeds normally.

Do not build automation that assumes every accepted event starts immediately.
This hold does not apply to GitHub Enterprise Server. See
[security-trust-and-policy.md](references/security-trust-and-policy.md) for
the exact scope.

## Re-evaluate `pull_request_target` refs

`pull_request_target` always loads the workflow and commit from the default
branch, including when the pull request targets another base branch:

- `GITHUB_REF` is the default branch.
- `GITHUB_SHA` is the latest commit on that branch.

Environment branch protections evaluate the execution ref, not `HEAD_REF`.
For `pull_request`, `pull_request_review`, and
`pull_request_review_comment`, that ref is `refs/pull/number/merge`; for
`pull_request_target`, it is the default branch. Adjust environment branch
patterns that assumed the older ref selection.

## Expect read-only caches in untrusted shared scopes

The cache token becomes read-only when an untrusted actor can trigger the
event and both execution and cache scope use the shared default-branch SHA.
Restores still work. A blocked save warns but does not fail the job.

Populate required caches from a trusted workflow such as `push`; do not treat
the warning as proof that the cache was updated. The detailed reference lists
the events that retain read-write access.

## Keep fork checkout protection enabled

`actions/checkout` v7 rejects fork pull-request head or merge checkouts in:

- `pull_request_target`; and
- `workflow_run` when the originating event is a `pull_request*` event.

The check covers a fork repository, pull-request head or merge refs, and their
corresponding SHAs when supplied with `repository` or `ref`. Same-repository
pull requests and ordinary `pull_request` runs are unaffected.

Use `allow-unsafe-pr-checkout` only after security review. It does not protect
shell-based fetches or checkouts of unrelated repositories. Floating major
tags and immutable pins have different upgrade behavior; consult the detailed
reference before relying on a supported pre-v7 major.

## Apply policy before execution

Public-preview workflow execution protections use rulesets at enterprise,
organization, and repository scope. Actor rules can allowlist users,
repository roles, GitHub Apps, Copilot, or Dependabot. Event rules can
allowlist triggers such as `push`, `pull_request`, `pull_request_target`, and
`workflow_dispatch`.

Rules are evaluated before a run starts and are configured separately from
general Actions settings under **Actions > Policies**. Use evaluate mode to
preview enforcement, and custom properties to target repositories from an
organization-wide ruleset.

Action and reusable-workflow allowlisting is available on Free, Team, and
Enterprise plans. Repository policy can restrict execution to an explicitly
selected set of actions and reusable workflows.

## Bind OIDC decisions to a job

OIDC tokens include `check_run_id` alongside claims such as `run_id` and
`run_attempt`. Use `check_run_id` when an external authorization or audit
system must identify the exact job and compute that requested a token.

## Enforce both self-hosted runner version gates

Runner `2.329.0` is the minimum for configuring or re-registering a
self-hosted runner on the new platform. It is not a permanent execution floor.
Every runner release, including patch releases, must be installed within 30
days of publication or the service stops queuing jobs to that runner.

Auto-update satisfies the rolling requirement when its update service is
reachable. Fleets with auto-update disabled need a regular manual upgrade
process. A critical security release pauses queuing until installed and has no
normal grace period.

Full enforcement begins July 31, 2026 for Enterprise Cloud with Data
Residency and September 25, 2026 for Enterprise Cloud. Enterprise Server is
not affected. Registration-only and registration-and-runtime brownouts occur
before the standard cloud date; use
[self-hosted-runners.md](references/self-hosted-runners.md) for every window.

Inventory runner versions through the self-hosted-runners REST API using API
version `2026-03-10`. Registration audit events include a version but are not
a complete inventory. Runtime annotations identify outdated runners before
enforcement.

## Gate features on runner interfaces

Runner `2.336.0` supports `$GITHUB_ARTIFACTS` environment files and exposes the
effective cache mode through `ACTIONS_CACHE_MODE`. Workflows or actions using
either interface require that runner version or later.

The same runner floor applies to self-repository `$/` references. A `uses:`
value beginning with `$/` resolves an action or reusable workflow in the same
repository at the exact commit being run, without a checkout:

```yaml
steps:
  - uses: $/.github/actions/setup
```

Use this syntax anywhere a `./` reference is accepted on github.com.

## Coordinate concurrent steps explicitly

Steps can run asynchronously with `background: true` while retaining separate
logs. Use `wait` for a named earlier background step, `wait-all` for all
earlier background steps, and `cancel` for graceful termination. `parallel`
starts a group as background steps and then waits.

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
result, and cancellation waits for the worker to finish. Gate runner versions
when correctness depends on these semantics.

## Use the expanded workflow limits

- A run can nest up to 10 reusable workflows.
- A run can call up to 50 reusable workflows in total.
- `workflow_dispatch` accepts up to 25 top-level inputs, including API starts.

These replace the earlier limits of four nested reusable workflows, 20 total
reusable workflows, and 10 manual-dispatch inputs.

## Choose runner capacity deliberately

The public-preview `actions/scaleset` Go client orchestrates runner scale-set
APIs for custom autoscaling outside Kubernetes and supports multiple labels
per scale set. The integrator still owns infrastructure provisioning, scaling,
and destruction. Actions Runner Controller remains the recommended Kubernetes
implementation.

Hosted choices include the public-preview `windows-2025-vs2026` and
`macos-26-large` labels plus generally available M2 xlarge macOS labels. Read
[hosted-runner-images.md](references/hosted-runner-images.md) before selecting
one; preview status, architecture, and image migration affect reproducibility.
