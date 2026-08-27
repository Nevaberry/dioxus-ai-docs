# Workflow Semantics and Limits

## Self-repository `$/` references (2026-07-30)

A `uses:` value beginning with `$/` resolves an action or reusable workflow in
the same repository at the exact commit being run. It does not require a
checkout and is accepted anywhere a `./` reference is accepted.

The syntax is available on github.com and requires runner `2.336.0` or later.
Gate self-hosted runner versions before adopting it.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: $/.github/actions/setup
      - run: ./test
```

Because resolution follows the exact commit for the run, the reference avoids
hard-coding a branch or tag for same-repository dependencies.

## Concurrent steps within a job

Set `background: true` on a step to start it asynchronously while retaining a
separate log. Coordinate lifecycle explicitly:

- `wait` joins a named earlier background step.
- `wait-all` joins all earlier background steps.
- `cancel` gracefully terminates a background step.
- `parallel` starts a group as background steps and then waits for the group.

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

Do not assume a background service is ready merely because its step has
started. Add an application-level readiness check before dependent work.

## Canceled background-step results

With runner `2.336.0`, canceled background steps no longer affect the job
result. Cancellation waits for the worker to finish. Pin or gate the runner
version when the final result or cleanup order depends on these semantics.

## Reusable-workflow limits

A workflow run can:

- nest up to 10 reusable workflows; and
- call up to 50 reusable workflows in total.

These are separate limits. The earlier ceilings were four nested reusable
workflows and 20 total reusable-workflow calls.

## Manual-dispatch inputs

`workflow_dispatch` accepts up to 25 top-level inputs, including when the
workflow is started through the API. The earlier ceiling was 10. Keep input
validation in the workflow or called tooling; a larger schema does not make
user-supplied values trusted.
