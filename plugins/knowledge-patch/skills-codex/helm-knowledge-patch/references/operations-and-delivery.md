# Operations and Chart Delivery

## Server-side apply

### Keep CLI and SDK defaults aligned

Helm 4 supports server-side apply. In Helm 4.2, the SDK defaults for
server-side apply are kept consistent with the CLI defaults (since 4.2.3).

When CLI and embedded behavior are compared, do not add a compensating SDK
setting for a default mismatch that no longer exists. Retain explicit values
only when the application intentionally overrides the common default.

### Retry Kubernetes conflicts

Server-side apply retries Kubernetes conflicts as of 4.2.4 instead of failing
on the first conflict. This reduces avoidable operation failures when another
actor updates a resource concurrently.

Use a client with this behavior where transient conflicts occur, while still
surfacing a final conflict if retries cannot complete the operation.

## Waiting and failure handling

### Use kstatus-based waiting

Helm 4 bases improved resource watching and waiting on kstatus (since 4.2.3).
Helm 4.2 adds fine-grained context options for waiting and stops waiting
forever after a resource has failed.

Use the available context controls to bound or cancel operations. Preserve
the failed-resource result for diagnosis, and do not wrap the Helm call in an
unbounded wait to compensate for earlier behavior.

Test successful, failed, timed-out, and canceled paths in SDK integrations and
deployment automation.

## Install and dry-run behavior

### Roll back failed installs atomically

Helm 4.2 restores `--atomic` on `helm install` (since 4.2.3). When an
unsuccessful installation must roll back automatically, run:

```sh
helm install my-release ./chart --atomic
```

Include a failed-install case in automation tests so the rollback contract is
verified rather than inferred from the flag being accepted.

### Permit server-generated names

`--dry-run=server` accepts rendered resources with `metadata.generateName`
instead of `metadata.name` (since 4.2.3). The API server will generate the
final name, so validators and server dry-run fixtures must allow this resource
shape.

## Test diagnostics

### Read logs from every test container

`helm test` fetches logs from every container in every test pod as of 4.2.4.
Diagnostics therefore include sidecars and other secondary containers, not
only one primary container.

When a test fails, inspect the complete per-container output. Wrappers that
parse test output should tolerate and retain logs from multiple containers.

## Registry authentication and dependencies

### Request complete push scopes

For token-authenticated registry pushes, `helm push` requests both `pull` and
`push` scopes as of 4.2.4. Upgrade when pushes fail because a registry expects
the full scope set during token exchange.

Do not work around the failure by weakening registry authorization. Confirm
that the upgraded client requests both required scopes.

### Pass registry configuration to dependency downloads

During `helm upgrade`, Helm passes its registry client to
`downloader.Manager` as of 4.2.4. Registry credentials and other client
configuration are therefore available while chart dependencies are
downloaded.

Exercise an upgrade whose dependency comes from an authenticated registry.
The download should use the same registry client configuration available to
the upgrade operation.

## Caching and packaging

### Reason about cache identity by content

Helm 4 adds local content-based caching, including for charts (since 4.2.3).
Identical content can share cached data even when it originates from different
locations.

When investigating cache hits or reuse, compare content rather than treating
the source path as the cache identity. Conversely, a familiar location does
not make changed content identical.

### Build reproducible chart archives

Chart archive builds are reproducible and idempotent in Helm 4 (since 4.2.3).
Repeated packaging can be used for deterministic build and verification
workflows.

If two builds differ, inspect their chart inputs and surrounding workflow.
Archive nondeterminism is not expected behavior to accept without diagnosis.

## Operations verification

Before completing an operational change:

1. Compare explicit SDK server-side apply settings with the CLI defaults.
2. Exercise conflict retries under a concurrent resource update.
3. Test successful, failed, canceled, and bounded wait paths.
4. Verify rollback after a failed `helm install --atomic`.
5. Include a server dry-run resource that uses `metadata.generateName`.
6. Confirm `helm test` captures logs from every container.
7. Test a token-authenticated push with both registry scopes.
8. Test an upgrade that downloads an authenticated registry dependency.
9. Compare repeated packages when deterministic artifacts matter.
10. Evaluate cache reuse using content rather than source location.
