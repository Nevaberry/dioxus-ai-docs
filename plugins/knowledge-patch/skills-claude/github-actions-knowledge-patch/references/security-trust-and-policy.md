# Security, Trust, and Policy

Use this reference when a workflow crosses a pull-request trust boundary,
writes a cache, checks out contributor code, requests an OIDC token, or is
subject to repository or organization policy.

## Start with the execution identity

Before changing a privileged workflow, establish:

- which event starts the run and who can trigger it;
- which ref and commit supply the workflow;
- which contributor-controlled values reach checkout, shell, actions, or
  reusable workflows;
- the effective token permissions and environment protections; and
- the cache scope and whether the run is allowed to write it.

## `pull_request_target` execution refs

Since December 8, 2025, `pull_request_target` always sources its workflow and
commit from the repository's default branch. `GITHUB_REF` is the default branch
and `GITHUB_SHA` is the latest commit on that branch, even when the pull request
targets another base branch.

This behavior makes the workflow definition trusted, but does not make the
pull request's code or metadata safe to execute. Treat any later checkout,
fetch, interpolation, or action selection derived from the pull request as a
separate trust decision.

Environment branch protections evaluate the execution ref rather than
`HEAD_REF`:

| Event | Ref evaluated by environment branch protection |
| --- | --- |
| `pull_request` | `refs/pull/number/merge` |
| `pull_request_review` | `refs/pull/number/merge` |
| `pull_request_review_comment` | `refs/pull/number/merge` |
| `pull_request_target` | Default branch |

Review environment branch patterns that expected the pull request's head or
base branch.

## Cache writes in untrusted contexts

The cache token becomes read-only when both of these conditions hold:

1. an untrusted actor can trigger the event; and
2. the execution and cache scope use the shared default-branch SHA.

Cache restores continue to work. When a save is blocked, the step emits a
warning and the job continues; the warning is not evidence that a new cache
entry was stored. Populate caches required by untrusted runs from a trusted
workflow such as `push`.

The usual default-branch triggers that retain read-write cache access are:

- `push`
- `schedule`
- `workflow_dispatch`
- `repository_dispatch`
- `delete`
- `registry_package`
- `page_build`

Events with non-default-branch cache scope, including `pull_request` and
`release`, also retain read-write access.

## Fork checkout protection

`actions/checkout` v7 rejects a fork pull request's head or merge checkout in:

- `pull_request_target`; and
- `workflow_run` when the originating event is a `pull_request*` event.

The protection recognizes a fork repository, a pull-request head or merge ref,
and the corresponding head or merge SHA when supplied through `repository` or
`ref`. Same-repository pull requests and ordinary `pull_request` runs are
unaffected.

The protection was scheduled for backport to every other supported major
version on July 20, 2026, except v1. Floating major tags receive the backport
automatically. SHA, minor, and patch pins must be upgraded explicitly to pick
it up.

`allow-unsafe-pr-checkout` deliberately bypasses the action's protection. Use
it only after reviewing the workflow's permissions, secrets, environment,
cache writes, artifacts, and all code that will execute. The action cannot
protect shell-based fetches or checkouts of unrelated repositories.

## Automatic approval holds

(Since 2026-07-28.) GitHub Actions automatically holds certain workflow runs
that it identifies as potentially malicious in public repositories on
github.com. No repository configuration is needed. GitHub Enterprise Server
is not covered.

A held run starts only after a repository collaborator with write access
approves it through an authenticated web session. After approval, the run
continues normally.

## Action and reusable-workflow allowlisting

Allowlisting is available on Free, Team, and Enterprise plans. A repository
policy can restrict execution to an explicitly selected set of actions and
reusable workflows. Keep the allowed set intentional and update policy before
introducing a new dependency.

## Workflow execution protection rulesets

Public-preview workflow execution protections provide ruleset policy at the
enterprise, organization, and repository scopes. They are evaluated before a
run starts rather than being controlled only by the workflow file.

Actor rules can allowlist:

- individual users;
- repository roles;
- GitHub Apps;
- Copilot; and
- Dependabot.

Event rules can allowlist triggers such as `push`, `pull_request`,
`pull_request_target`, and `workflow_dispatch`.

Organization-wide rulesets can use custom properties to select repositories.
Use evaluate mode to preview which runs enforcement would block. Configure
these rules under **Actions > Policies**; they are separate from the general
Actions settings.

## Job-specific OIDC identity

Actions OIDC tokens include `check_run_id` alongside claims such as `run_id`
and `run_attempt`. An external authorization or audit system can bind its
decision to `check_run_id` when it must identify the exact job and compute
that requested a token, rather than only the overall workflow run.
