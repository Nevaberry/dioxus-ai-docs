# Workflow Semantics and Limits

Use this reference when introducing asynchronous steps, composing reusable
workflows, defining manual inputs, or referencing code in the current
repository.

## Concurrent steps within a job

Set `background: true` to run a step asynchronously while retaining a separate
log for it. Coordinate background work explicitly:

- `wait` joins a named earlier background step;
- `wait-all` joins all earlier background steps;
- `cancel` gracefully terminates a background step; and
- `parallel` starts a group as background steps and then waits.

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

Make service readiness and termination explicit; starting a process in the
background does not by itself establish that it is ready for dependent steps.

## Canceled background-step results

With runner `2.336.0`, a canceled background step no longer affects the job
result. Cancellation waits for the worker to finish. Pin or gate the runner
version when a job relies on either result propagation or shutdown timing.

## Reusable-workflow limits

A workflow run can:

- nest up to 10 reusable workflows, increased from four; and
- call up to 50 reusable workflows in total, increased from 20.

The nesting limit concerns call depth; the total-call limit concerns all
reusable-workflow calls made by the run.

## Manual-dispatch inputs

`workflow_dispatch` accepts up to 25 top-level inputs, increased from 10. The
same limit applies when the workflow is started through the API.

## Self-repository `$/` references

(Since 2026-07-30.) A `uses:` value beginning with `$/` resolves an action or
reusable workflow in the same repository at the exact commit being run. It
does not require a checkout and works anywhere a `./` reference works.

The syntax is available on github.com and requires runner `2.336.0` or later.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: $/.github/actions/setup
      - run: ./test
```
