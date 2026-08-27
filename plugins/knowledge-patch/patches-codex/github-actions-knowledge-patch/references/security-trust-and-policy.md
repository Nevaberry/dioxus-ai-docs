# Security, Trust, and Policy

## Automatic approval holds for potentially malicious workflows (2026-07-28)

GitHub Actions automatically holds certain workflow runs it identifies as
potentially malicious in public repositories on github.com. Repository owners
do not need to enable or configure the hold.

A held run starts only after a repository collaborator with write access
approves it through an authenticated web session. After approval, the run
continues normally. Account for this human gate in timeouts, status handling,
and automation that waits for a run to start. GitHub Enterprise Server is not
covered by this behavior.

## Privileged pull-request refs

Since December 8, 2025, `pull_request_target` always sources its workflow and
commit from the default branch. `GITHUB_REF` is the default branch and
`GITHUB_SHA` is its latest commit, even when the pull request targets a
different base branch.

This makes the workflow definition trusted by default, but does not make code
from the pull request safe to execute. Treat any explicit checkout, fetch,
build, or script execution from the pull request as a separate trust decision.

## Environment protection ref matching

Environment branch protections evaluate the execution ref rather than
`HEAD_REF`:

| Event | Ref evaluated by environment protection |
| --- | --- |
| `pull_request` | `refs/pull/number/merge` |
| `pull_request_review` | `refs/pull/number/merge` |
| `pull_request_review_comment` | `refs/pull/number/merge` |
| `pull_request_target` | Default branch |

Update environment branch patterns that expected a pull request's base branch
or `HEAD_REF`. Test the effective execution ref before depending on an
environment to gate secrets or deployments.

## Read-only caches for untrusted default-branch contexts

The cache token is read-only when both of these are true:

1. An untrusted actor can trigger the event.
2. Execution and cache scope use the shared default-branch SHA.

Cache restores continue to work. An attempted save emits a warning and the
job continues, so a successful job does not prove the cache was populated.
Use a trusted workflow, commonly `push`, to create caches required by these
runs.

The usual default-branch triggers retain read-write cache access:

- `push`
- `schedule`
- `workflow_dispatch`
- `repository_dispatch`
- `delete`
- `registry_package`
- `page_build`

Events with non-default-branch scope, including `pull_request` and `release`,
also retain read-write access.

## Fork checkout safeguards

`actions/checkout` v7 rejects a fork pull request's head or merge checkout in
`pull_request_target`. It applies the same protection to `workflow_run` when
the originating event is a `pull_request*` event.

The guard detects:

- a fork repository passed through `repository`;
- a pull-request head or merge ref passed through `ref`; and
- the corresponding head or merge SHA.

Same-repository pull requests and ordinary `pull_request` runs are unaffected.
The safeguard was scheduled for backport to every other supported major on
July 20, 2026, except v1. Floating major tags receive a backport automatically;
SHA, minor, and patch pins must be upgraded explicitly.

`allow-unsafe-pr-checkout` deliberately bypasses the check. Use it only after
a documented review of event permissions, secrets, token permissions, runner
isolation, fetched ref, and commands that execute the fetched content. The
checkout guard does not cover shell-based fetches or checkouts of unrelated
repositories.

## Central workflow execution protections

Public-preview workflow execution protections use rulesets at enterprise,
organization, and repository scope. They are evaluated before a run starts,
so a denied run cannot weaken the policy from its workflow file.

Actor rules can allowlist:

- individual users;
- repository roles;
- GitHub Apps;
- Copilot; and
- Dependabot.

Event rules can allowlist triggers such as `push`, `pull_request`,
`pull_request_target`, and `workflow_dispatch`. Organization-wide rulesets can
select repositories using custom properties. Use evaluate mode to preview
what enforcement would block before enabling it.

Configure these controls separately from general Actions settings under
**Actions > Policies**.

## Allowed actions and reusable workflows

Free, Team, and Enterprise plans can restrict action and reusable-workflow use.
At repository scope, select an explicit allowlist when workflows should not be
able to execute arbitrary marketplace or cross-repository code. Keep reusable
workflow dependencies in the same review and pinning process as actions.

## Job-specific OIDC identity

Actions OIDC tokens include `check_run_id` in addition to claims such as
`run_id` and `run_attempt`. An external authorization or audit system can use
`check_run_id` to bind a token request to the exact job and compute rather
than only to the overall workflow run.
