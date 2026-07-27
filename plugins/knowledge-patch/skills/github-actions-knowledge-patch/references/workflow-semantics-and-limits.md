# Workflow semantics and limits

Use this reference when composing concurrent steps, reusable workflows, or
manual inputs.

## Concurrent steps within a job

A step can run asynchronously with `background: true` and retains its own
logs.

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

Use the coordination controls deliberately:

| Control | Behavior |
| --- | --- |
| `wait` | Join a named earlier background step |
| `wait-all` | Join all earlier background steps |
| `cancel` | Gracefully terminate a background step |
| `parallel` | Run a group as background steps, then wait for the group |

Do not assume that reaching the next foreground step implicitly joins all
background work. Place a join before consuming its output or before the job
can safely finish.

Runner `2.336.0` makes canceled background steps neutral to the job result
and waits for the worker to finish during cancellation. A self-hosted fleet
must meet that version floor when those result and cleanup semantics matter.

## Reusable-workflow call limits

One workflow run can:

- nest as many as 10 reusable workflows; and
- call as many as 50 reusable workflows in total.

The previous limits were four levels of nesting and 20 total calls. Count the
whole call graph, not only the reusable workflows named directly by the
entry workflow.

## Manual-dispatch inputs

`workflow_dispatch` accepts as many as 25 top-level inputs. The same maximum
applies when the workflow is started through the API.

The previous maximum was 10. Keep the top-level count at or below 25 even if
some inputs are optional or used only by API callers.
