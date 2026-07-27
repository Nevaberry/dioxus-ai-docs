# Security, trust, and policy

Use this reference when a workflow handles fork content, environments,
caches, OIDC credentials, or centrally managed execution policy.

## Privileged pull-request execution refs

Since December 8, 2025, `pull_request_target` always sources both its workflow
and commit from the repository's default branch. `GITHUB_REF` is the default
branch and `GITHUB_SHA` is the latest commit on that branch, even when the
pull request targets some other base branch.

Do not use either value as the pull request's proposed revision. If a
privileged workflow needs information about the pull request, obtain it from
the event payload and keep all untrusted content separate from executable
code.

Environment branch protections now evaluate the execution ref instead of
`HEAD_REF`:

| Event | Ref evaluated by environment protection |
| --- | --- |
| `pull_request` | `refs/pull/number/merge` |
| `pull_request_review` | `refs/pull/number/merge` |
| `pull_request_review_comment` | `refs/pull/number/merge` |
| `pull_request_target` | Default branch |

Review existing environment branch filters and add the corresponding patterns
where access was previously based on the pull request's head or base branch.

## Cache tokens in untrusted contexts

The cache token becomes read-only when both of these conditions hold:

1. An untrusted actor can trigger the event.
2. The execution scope and cache scope both use the shared default-branch SHA.

Cache restoration still succeeds. A save attempt is blocked with a warning,
but the step and job continue. Do not mistake a successful job for a
successful cache update. Populate caches needed by such runs from a trusted
workflow, commonly `push`.

The usual default-branch triggers retain read-write cache access:

- `push`
- `schedule`
- `workflow_dispatch`
- `repository_dispatch`
- `delete`
- `registry_package`
- `page_build`

Events with non-default-branch cache scope, including `pull_request` and
`release`, also retain read-write access.

## Safer checkout defaults for fork content

`actions/checkout` v7 rejects a fork pull request's head or merge checkout in
`pull_request_target`. It applies the same protection to `workflow_run` when
the originating event is any `pull_request*` event.

The action detects:

- a fork repository;
- a pull-request head or merge ref; and
- the corresponding head or merge SHA passed through `repository` or `ref`.

Same-repository pull requests are unaffected. Ordinary `pull_request` runs are
also unaffected because they do not have the privileged trust boundary these
checks address.

The safeguard was scheduled for backport to every other supported major
version on July 20, 2026, except v1. Floating major tags receive the backport
automatically. SHA pins and minor or patch pins must be upgraded explicitly.

A reviewed workflow can deliberately bypass the check with the
`allow-unsafe-pr-checkout` input. This opt-out does not cover untrusted code
fetched with shell commands, and it does not cover unrelated repositories.
Review those paths separately.

## Allowed actions and reusable workflows

Action and reusable-workflow allowlisting is available on Free, Team, and
Enterprise plans. A repository policy can restrict execution to an explicitly
selected set of actions and reusable workflows.

Treat the allowlist as a dependency policy: account for every reusable
workflow in the call graph as well as direct `uses:` entries.

## Workflow execution protections

Public-preview workflow execution protections provide ruleset-based policy at
enterprise, organization, and repository scope. The policies are evaluated
before a run begins rather than relying solely on conditions inside the
workflow file.

Actor rules can allowlist:

- users;
- repository roles;
- GitHub Apps;
- Copilot; and
- Dependabot.

Event rules can allowlist triggers such as:

- `push`;
- `pull_request`;
- `pull_request_target`; and
- `workflow_dispatch`.

Organization-wide rulesets can select repositories with custom properties.
Use evaluate mode to preview which runs enforcement would block before
turning it on. Configure these controls separately from general Actions
settings under **Actions > Policies**.

## Job-specific OIDC identity

Actions OIDC tokens include `check_run_id` alongside `run_id` and
`run_attempt`. `run_id` and `run_attempt` identify the workflow run and its
attempt; `check_run_id` identifies the exact job and compute that requested
the token.

External authorization and audit systems can use this claim to bind an
identity decision to one job rather than granting based only on the overall
run.
