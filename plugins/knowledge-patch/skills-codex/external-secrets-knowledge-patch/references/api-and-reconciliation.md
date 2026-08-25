# API and reconciliation

Read this reference when changing `ExternalSecret`, `SecretStore`,
`ClusterSecretStore`, or `ClusterExternalSecret` behavior, status, validation,
refresh, metadata, and namespace access.

## API versions, fields, and validation

### Stable provider examples and legacy beta serving

Provider examples use `apiVersion: external-secrets.io/v1` (since 0.17.0).
Serving the legacy beta API became configurable in 1.3.0 for migrations. Do not
assume disabling a CRD version also disables its reconciler or conversion; those
are independently controlled deployment concerns.

### Optional strategy fields

Since 2.9.0, the API does not materialize defaults for optional
`ExternalSecret` strategy fields. Clients must apply their own semantic defaults
and must not expect omitted values to appear when the object is read back.

### Validation changes

- `ExternalSecretRewrite` constraints are validated (since 0.19.0).
- `generatorRef` validates `externalsecret_type` (since 1.0.0).
- Namespaces in `secretRef` configurations are validated (since 0.20.0).
- Invalid configurations can therefore fail admission rather than waiting for a
  later reconciliation failure.

### Selectable fields and printer columns

CRDs declare supported selectable fields for Kubernetes field selectors (since
0.20.0). Tabular store output includes `storeType` (since 0.14.0), and
`ExternalSecret` and `PushSecret` printers include Last Sync (since 2.2.0).

## Refresh and reconciliation

### Refresh-policy edge behavior

`Periodic` is the default policy. A zero `refreshInterval` under `Periodic`
fetches and creates once but does not update later. `OnChange` ignores the
interval and reacts only when `ExternalSecret` metadata or spec changes.

`CreatedOnce` stores its decision in `ExternalSecret` status. It repairs a
target Secret that is changed or deleted while that status survives. Recreating
the `ExternalSecret` resets status and may overwrite an existing target;
creation policy alone does not prevent this recreation-time rewrite.

For a generated credential that must survive deletion and never be replaced,
combine an orphaned, immutable target with `CreatedOnce`:

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

### Manual refresh annotations

Change the unqualified `force-sync` annotation to refresh an `ExternalSecret`
when its policy supports refresh. `ClusterExternalSecret` instead uses the
qualified `external-secrets.io/force-sync`; setting, changing, or deleting it
propagates to every owned child.

```sh
kubectl annotate es my-es force-sync=$(date +%s) --overwrite
kubectl annotate ces my-ces external-secrets.io/force-sync=$(date +%s) --overwrite
```

### Retry and requeue behavior

Failed reconciliations have used a much less aggressive retry cadence since
0.14.0. Do not build alerts or runbooks around the older rapid retry behavior.
The chart exposes `storeRequeueInterval` for store requeue cadence (since
2.7.0), while `SecretStore.refreshInterval` accepts duration strings (since
2.8.0).

A namespaced `SecretStore` may set `retrySettings.maxRetries` and
`retrySettings.retryInterval`. API guidance lists retry support only for AWS,
HashiCorp Vault, IBM, and Doppler providers.

```yaml
spec:
  retrySettings:
    maxRetries: 5
    retryInterval: 10s
```

### Store reconciliation and status

SecretStore reconciliation can be enabled or disabled by controller flag (since
1.2.0). Stores may be marked deprecated so operators can steer users away from
them (since 1.2.0). A store whose state cannot be determined reports an unknown
status instead of a misleading known state (since 0.20.0).

### Sync windows

`ExternalSecret` supports sync windows that gate periodic refreshes (since
2.7.0). Evaluate windows together with refresh policy, interval, manual refresh,
and the controller's retry/requeue behavior.

## Targets, values, and metadata

### Dynamic targets and creation policy

Sources can select targets dynamically (since 1.0.0). `CreateOrMerge` is an
accepted target creation policy (since 2.8.0). Verify the resulting target name,
ownership, and collision behavior rather than assuming a statically named
Secret.

### Native and decoded values

Secret metadata can explicitly request decoded values (since 0.15.0).
Value-scoped processing preserves native values instead of coercing them to
strings (since 0.19.0). Preserve type deliberately until Kubernetes Secret
serialization or a template conversion requires bytes or text.

### Metadata copying and target ownership

Labels and annotations on an `ExternalSecret` normally copy to its target.
Defining `target.template.metadata` replaces implicit copying; empty maps
explicitly suppress the corresponding metadata:

```yaml
spec:
  target:
    template:
      metadata:
        labels: {}
        annotations: {}
```

Target resource `objectMeta` and `ownerReferences` propagate correctly (since
2.3.0). Templates can also add finalizers to generated Secrets (since 0.20.0).
Review ownership and finalizers together because both affect deletion.

### Source null bytes

Sources have a configurable null-byte policy (since 2.3.0). Choose it explicitly
when a provider can return binary-like values, and test the eventual Secret or
generic target representation.

### Certificate-only PKCS#12 data

PKCS#12 processing accepts certificate-only bundles without a private key
(since 0.20.0). Consumers must still tolerate the absence of a private-key
field.

## Namespace fan-out and access

### Plural ClusterExternalSecret selectors

`ClusterExternalSecret.spec.namespaceSelectors` is a list; selector entries are
ORed. The singular `namespaceSelector` and explicit `namespaces` fields are
deprecated. A collision with an existing `ExternalSecret` is recorded as a
failed namespace instead of taking the object over.

```yaml
spec:
  namespaceSelectors:
    - matchLabels:
        team: payments
    - matchLabels:
        shared-credentials: "true"
```

### Efficient fan-out

Every child created by a `ClusterExternalSecret` polls the upstream provider
independently, so provider calls grow linearly with matched namespaces. For
large fan-out, fetch once into a dedicated namespace, point a Kubernetes-backed
`ClusterSecretStore` at that source Secret, and replicate through that store.
Only the source object then calls the upstream provider.

### ClusterSecretStore namespace conditions

`ClusterSecretStore.spec.conditions` can allow label-selected namespaces,
explicit names, or regular expressions. The separate condition forms are ORed;
satisfying any one grants access.

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

Namespaced resources cannot cross-reference a namespaced store, Secret, or
other namespaced referent in another namespace. Treat every cluster-scoped
resource as a separate authority boundary.

## Provider maintenance warnings

A store backed by a provider without an explicit maintainer produces controller
and admission-webhook warning events. The following annotation suppresses only
the controller warning; the admission warning cannot be disabled:

```yaml
metadata:
  annotations:
    external-secrets.io/ignore-maintenance-checks: "true"
```
