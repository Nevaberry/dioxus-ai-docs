# Operations and Chart Delivery

Use this reference for install, upgrade, server-side apply, waiting, tests,
server dry-runs, registry operations, caching, and deterministic packaging.

## Install and server-side apply

### Atomic installation *(since 4.2.3)*

Helm 4.2 restores `--atomic` on `helm install`. Use it when failed
installation work must be rolled back automatically:

```sh
helm install my-release ./chart --atomic
```

Exercise the failure path as well as the successful install. The flag expresses
the rollback requirement; verification should confirm that the surrounding
release workflow handles the resulting failure and rollback as intended.

### CLI and SDK defaults *(since 4.2.3)*

Helm 4 supports server-side apply. In Helm 4.2, the SDK's server-side-apply
defaults are kept consistent with the CLI defaults. When comparing CLI and
embedded behavior, do not add configuration solely to compensate for a
default difference that no longer exists.

Keep explicit settings when the caller intentionally overrides the shared
default. Test both configuration wiring and the resulting Kubernetes behavior.

### Conflict retries *(since 4.2.4)*

Server-side apply retries Kubernetes conflicts instead of failing on the first
conflict. This makes concurrent resource updates less likely to abort a Helm
operation immediately.

Do not treat retries as a substitute for time bounds or final error handling.
Test a conflicting update and ensure the calling workflow handles both eventual
success and exhausted failure.

## Waiting and diagnostics

### Kstatus-based waiting *(since 4.2.3)*

Helm 4 bases improved resource watching and waiting on kstatus. Helm 4.2 adds
fine-grained context options for waiting and avoids waiting forever after a
resource has failed.

Pass an appropriate context for the operation, cover cancellation and timeout
paths, and retain failed-resource information for diagnosis. Do not wrap the
operation in an unbounded wait to imitate older behavior.

### Multi-container test logs *(since 4.2.4)*

`helm test` fetches logs from every container in each test pod. Failures from
sidecars and other secondary containers are therefore part of the diagnostic
output.

Log processors and test harnesses should accept multiple container streams.
When diagnosing a failed test, inspect every container rather than assuming
the primary container contains the relevant failure.

### Generated names in server dry-runs *(since 4.2.3)*

`--dry-run=server` accepts rendered resources that set
`metadata.generateName` instead of `metadata.name`. This matches the API
server's ability to generate the final resource name.

Allow this shape in validators and server dry-run fixtures. Do not reject a
resource solely because `metadata.name` is absent when `metadata.generateName`
is present and server-side name generation is intended.

## Registry operations

### Token-authenticated pushes *(since 4.2.4)*

`helm push` requests both `pull` and `push` scopes when authenticating to a
registry with tokens. Upgrade when pushes fail because the registry requires
the complete scope set during token exchange.

When debugging authentication, inspect the granted scopes as well as stored
credentials. A valid token with an incomplete requested scope can still make a
push fail.

### Dependency downloads during upgrade *(since 4.2.4)*

During `helm upgrade`, Helm passes its registry client to
`downloader.Manager`. Registry credentials and client configuration are then
available while chart dependencies are downloaded.

Test an upgrade whose dependencies require registry authentication. Use the
same registry client configuration expected by the upgrade instead of creating
an unrelated unauthenticated dependency-download path.

## Caching and archives

### Content-based caching *(since 4.2.3)*

Helm 4 provides local content-based caching, including for charts. Identical
content can share cached data independently of the source location.

Reason about cache identity from content. Moving or obtaining identical chart
content from a different location does not necessarily require a distinct
cached copy, while changed content should not be treated as the same object
merely because its path is unchanged.

### Reproducible chart archives *(since 4.2.3)*

Chart archive builds are reproducible and idempotent in Helm 4. Repeated
packaging is suitable for deterministic build and verification workflows.

When repeated archives differ, investigate chart inputs and the surrounding
workflow. Archive nondeterminism is not expected behavior to accept by default.

## Operations checklist

- Test failed installation rollback with `--atomic` where required.
- Compare explicit apply configuration with aligned CLI and SDK defaults.
- Exercise conflict retry success and terminal failure.
- Bound waits with context and preserve failed-resource diagnostics.
- Capture logs from every container in each test pod.
- Include `metadata.generateName` in a server dry-run fixture.
- Verify token exchange requests both registry scopes for pushes.
- Test authenticated registry dependencies during `helm upgrade`.
- Compare cached objects by content, not only by path.
- Package identical chart inputs repeatedly and compare the archives.
