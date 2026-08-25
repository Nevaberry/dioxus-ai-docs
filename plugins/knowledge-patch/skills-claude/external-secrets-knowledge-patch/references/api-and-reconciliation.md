# API Resources and Reconciliation

Use this reference for resource semantics, status, validation, refresh behavior,
selectors, and controller reconciliation. Provider-specific authentication and
capabilities are covered in the provider references.

## ExternalSecret refresh semantics

### Refresh policies (`api-v1`)

`Periodic` is the default policy. With `refreshInterval: 0`, the controller fetches
and creates once but does not update later. `OnChange` ignores the interval and
refreshes only after `ExternalSecret` metadata or spec changes.

`CreatedOnce` stores its progress in status. It repairs a target Secret that is
changed or deleted while the same `ExternalSecret` object survives, but deleting
and recreating the `ExternalSecret` resets that status and can overwrite an
existing target. Creation policies do not prevent this recreation-time rewrite.
For a generated credential that must survive deletion and reject replacement, use
an orphaned, immutable target:

```yaml
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: bootstrap-credential
spec:
  refreshPolicy: CreatedOnce
  secretStoreRef:
    name: app-store
    kind: SecretStore
  target:
    name: bootstrap-credential
    creationPolicy: Orphan
    immutable: true
  data:
    - secretKey: password
      remoteRef:
        key: app/password
```

### Manual refresh annotations (`api-v1`)

An `ExternalSecret` uses the unqualified `force-sync` annotation when its refresh
policy permits manual refresh. A `ClusterExternalSecret` uses
`external-secrets.io/force-sync`; setting, changing, or deleting it propagates to
each owned `ExternalSecret`.

```sh
kubectl annotate es my-es force-sync=$(date +%s) --overwrite
kubectl annotate ces my-ces external-secrets.io/force-sync=$(date +%s) --overwrite
```

### Sync windows (since 2.7.0)

`ExternalSecret` supports sync windows that gate periodic refreshes. Account for
the window when diagnosing a healthy object whose periodic update has not run.

### Optional strategy fields (since 2.9.0)

The API no longer materializes defaults for optional `ExternalSecret` strategy
fields. Clients, diffs, and manifest pipelines must tolerate omitted fields not
being written back.

## Target construction and metadata

### Template metadata replaces implicit copying (`api-v1`)

Labels and annotations on an `ExternalSecret` normally copy to the target Secret.
Once `target.template.metadata` is configured, its maps replace implicit copying;
empty maps explicitly suppress copying.

```yaml
spec:
  target:
    template:
      metadata:
        labels: {}
        annotations: {}
```

### Dynamic targets (since 1.0.0)

ExternalSecret sources can choose a target dynamically instead of fixing it in
advance. Validate the selected target and its ownership semantics just as for a
static target.

### Ownership propagation (since 2.3.0)

`objectMeta` and `ownerReferences` propagate to target resources. This matters for
garbage collection and for generic targets whose lifecycle follows another
resource.

### Creation policies (since 2.8.0)

`ExternalSecret.spec.target.creationPolicy` accepts `CreateOrMerge` in addition to
the earlier policies. Use it when the target may need to be created and then
merged rather than wholly replaced.

### Finalizers (since 0.20.0)

Secret templates can add finalizers to generated Secrets. Separately, a
`SecretStore` referenced by a `PushSecret` with `deletionPolicy: Delete` receives a
finalizer so remote deletion can finish before store removal.

## ClusterExternalSecret fan-out

### Plural selectors (`api-v1`)

`ClusterExternalSecret.spec.namespaceSelectors` is a list, and its selectors are
ORed. The singular `namespaceSelector` and explicit `namespaces` fields are
deprecated in favor of this list. If a selected namespace already contains a
colliding `ExternalSecret`, the controller records a failed namespace instead of
taking over the object.

```yaml
spec:
  namespaceSelectors:
    - matchLabels:
        team: payments
    - matchLabels:
        shared-credentials: "true"
```

### Reduce upstream provider calls (`api-v1`)

Every generated `ExternalSecret` polls the upstream provider independently, so
calls grow linearly with selected namespaces. At large scale, fetch once into a
dedicated namespace, expose that Secret through a Kubernetes-provider
`ClusterSecretStore`, and fan out from that store. Only the source object then
calls the upstream provider.

## Stores and access control

### ClusterSecretStore namespace conditions (`api-v1`)

`ClusterSecretStore.spec.conditions` can restrict referencing namespaces.
Label-selector, explicit-name, and regular-expression conditions are ORed; any
matching condition grants access.

```yaml
spec:
  conditions:
    - namespaceSelector:
        matchLabels:
          secrets-access: "true"
    - namespaces:
        - platform-system
    - namespaceRegexes:
        - "tenant-.*"
```

### SecretStore retries (`api-v1`)

A namespaced `SecretStore` can define `retrySettings.maxRetries` and
`retrySettings.retryInterval`. The v1 API documentation lists this support only
for AWS, HashiCorp Vault, IBM, and Doppler.

```yaml
spec:
  retrySettings:
    maxRetries: 5
    retryInterval: 10s
```

### Status, deprecation, and refresh

- Since 0.20.0, a `SecretStore` can report unknown status rather than inventing a
  known state when its condition cannot be determined.
- Since 1.2.0, stores can be designated deprecated so consumers can identify and
  migrate away from them.
- Since 2.8.0, `SecretStore.refreshInterval` accepts duration strings.
- Since 1.2.0, a controller flag can enable or disable SecretStore reconciliation.
- Failed reconciliations retry much less aggressively from 0.14.0; do not rely on
  the older rapid retry cadence.

### Unmaintained-provider warnings (`api-v1`)

Stores backed by a provider without an explicit maintainer emit controller and
admission-webhook warning events. This annotation suppresses only the controller
warning; the admission warning cannot be disabled:

```yaml
metadata:
  annotations:
    external-secrets.io/ignore-maintenance-checks: "true"
```

## Validation and API visibility

- `ExternalSecretRewrite` validation rejects invalid rewrite configurations from
  0.19.0.
- `generatorRef` validates `externalsecret_type` from 1.0.0.
- Namespaces in `secretRef` are validated from 0.20.0 rather than accepted for a
  later runtime failure.
- CRDs declare supported fields selectable from 0.20.0, enabling Kubernetes field
  selectors.
- Tabular output includes `storeType` from 0.14.0.
- `ExternalSecret` and `PushSecret` printers include Last Sync from 2.2.0.
- Provider examples use stable `apiVersion: external-secrets.io/v1` from 0.17.0.
- Serving the legacy beta API became configurable in 1.3.0 for migration periods.

## Admission and webhook context

- `ValidatingWebhookConfiguration` accepts annotations from 0.16.0.
- Webhook provider calls include the `ExternalSecret` namespace from 0.20.0,
  enabling namespace-aware webhook logic.
- The SecretStore validating-webhook `failurePolicy` became dynamic in 2.0.0.
- The chart applies `failurePolicy` to the `ClusterSecretStore` webhook from
  2.4.0.

## Source processing details

- Secret metadata can request decoded-value representation from 0.15.0.
- Source null-byte policy is configurable from 2.3.0.
- Group-variable selection became environment-aware in 0.18.0.
- ConfigMap access through `CAProvider` works correctly from 2.4.0.
