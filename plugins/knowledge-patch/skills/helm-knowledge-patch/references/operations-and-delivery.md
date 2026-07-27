# Operations and Chart Delivery

The apply, wait, install, dry-run, caching, and packaging behavior here is
attributed to the included `4.2.3` batch.

## Server-side apply

Helm 4 supports server-side apply.

In Helm 4.2, SDK server-side-apply defaults are kept consistent with the CLI
defaults. This matters when the same operation is exposed through both a CLI
workflow and an embedded Helm workflow:

- Do not assume the SDK silently chooses a different default.
- Preserve an explicit SDK option when a deliberate override is required.
- Remove compatibility workarounds whose only purpose was to reconcile
  differing defaults, after verifying the application does not need them for
  another reason.

## kstatus-based resource waiting

Helm 4 bases improved resource watching and waiting on kstatus.

Helm 4.2 adds fine-grained context options for waiting. Use those context
controls when a caller needs to cancel or bound the wait.

Helm 4.2 also avoids waiting forever after a resource has failed. Code around
Helm should preserve the failure and return path instead of replacing it with
another unbounded wait.

Exercise at least these paths when changing wait integration:

- A resource becomes ready.
- A resource reports failure.
- The wait context is canceled.
- A bounded wait reaches its context limit.

## Atomic installation

Helm 4.2 restores `--atomic` on `helm install`. The flag allows a failed
installation to be rolled back automatically again.

```sh
helm install my-release ./chart --atomic
```

Use the flag when automatic rollback is part of the intended install
semantics. Retest failure handling in wrappers that previously removed or
rejected the install flag.

## Server dry-run and generated names

`--dry-run=server` accepts rendered resources that use
`metadata.generateName` rather than `metadata.name`.

This matches server-side name generation behavior. A test or validator for
server dry-runs should therefore accept a resource shaped like:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  generateName: demo-
```

Do not require a rendered `metadata.name` when `metadata.generateName` is the
intentional server-side naming mechanism.

## Content-based caching

Helm 4 adds local content-based caching, including caching for charts.
Identical content can share cached data regardless of its source location.

Consequences for cache reasoning:

- A changed location does not necessarily imply changed cached content.
- Identical chart content from different locations can reuse cached data.
- Cache identity should be understood in terms of content, not only path or
  origin.

When investigating reuse or invalidation, compare the actual content before
attributing behavior to the source location.

## Reproducible chart archives

Helm 4 chart archive builds are reproducible and idempotent. Repeating the
same packaging operation is suitable for deterministic build and
verification workflows.

A verification workflow can:

1. Hold chart inputs constant.
2. Build the archive more than once.
3. Compare the outputs as deterministic artifacts.

If repeated archives differ, inspect the inputs and surrounding build steps;
archive nondeterminism is not the expected Helm 4 behavior.
