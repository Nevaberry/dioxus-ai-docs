# Push workflows

Read this reference before creating or changing `PushSecret`,
`ClusterPushSecret`, provider write mappings, update policy, deletion policy, or
bulk key expansion.

## Namespaced PushSecret

### Source, template, and mapping

A namespaced `PushSecret` accepts exactly one `selector` source: a Kubernetes
Secret or a `generatorRef`. `template` and `templateFrom` can construct outgoing
properties before `data[].match` maps a source or templated `secretKey` to a
provider `remoteKey` and optional `property`.

```yaml
apiVersion: external-secrets.io/v1alpha1
kind: PushSecret
metadata:
  name: app-credentials
spec:
  updatePolicy: Replace
  deletionPolicy: Delete
  refreshInterval: 1h
  secretStoreRefs:
    - name: destination
      kind: SecretStore
  selector:
    secret:
      name: source-credentials
  template:
    data:
      normalized: '{{ index . "raw-key" | toString | upper }}'
    templateFrom:
      - configMap:
          name: push-fragment
          items:
            - key: config.yml
  data:
    - match:
        secretKey: normalized
        remoteRef:
          remoteKey: app-credentials
          property: normalized
    - match:
        secretKey: config.yml
        remoteRef:
          remoteKey: app-config
          property: config.yml
```

### Update and deletion policies

`updatePolicy: Replace` permits overwriting a remote target. `deletionPolicy`
defaults to `None`; set it to `Delete` when deleting the `PushSecret` or source
must clean up the provider-side secret.

A `SecretStore` referenced by a `PushSecret` with `deletionPolicy: Delete`
receives a finalizer so remote cleanup can finish safely (since 0.20.0).
`PushSecret` key deletion removes the intended remote key rather than a
different key (fixed in 1.3.0).

## Bulk expansion with dataTo

### Selecting and mapping keys

`PushSecret.spec.dataTo` (2.3-datato) selects all keys or a regexp-filtered
subset from the Kubernetes Secret named by `spec.selector`. Every entry needs a
`storeRef` by name or label selector, and that store must also appear in
`secretStoreRefs`.

```yaml
spec:
  secretStoreRefs:
    - name: target-store
  dataTo:
    - storeRef:
        name: target-store
      match:
        regexp: '^APP_'
      rewrite:
        - regexp:
            source: '^APP_(.*)$'
            target: '$1'
```

An absent or empty match selects all keys. Without `remoteKey`, each selected
key becomes a separate provider secret or variable. With `remoteKey`, all
matches are bundled into one JSON object at that remote key.

Per-key mode supports regexp and template rewrites but not merge. Bundle mode
does not apply rewrites. Set provider-specific `metadata` and
`conversionStrategy` on each entry.

### Expansion order and precedence

Expansion follows this order:

1. Apply `spec.template`.
2. Expand `dataTo`.
3. Convert each key.
4. Match and rewrite the converted key.

An explicit `spec.data` entry wins when it addresses the same original,
unconverted Kubernetes key.

### Errors and lifecycle

An invalid match regexp puts the `PushSecret` into an error state. No matches is
a successful no-op. Duplicate remote keys within or across entries fail
reconciliation and identify the conflicting sources.

`UpdatePolicy=IfNotExists` applies to every expanded target.
`DeletionPolicy=Delete` records all expanded targets in
`status.syncedPushSecrets` so they can be removed when the source Secret is
deleted.

## ClusterPushSecret

### Namespace-wide selection

Since 0.15.0, `ClusterPushSecret` can push all Secrets from a namespace rather
than requiring every Secret to be selected individually.

### Fan-out and child status

A `ClusterPushSecret` creates its embedded `pushSecretSpec` in every namespace
matching any entry of the ORed `namespaceSelectors` list. `pushSecretName`
defaults to the parent name, `pushSecretMetadata` is copied to children, and
`refreshTime` controls fan-out checks.

Name collisions populate `failedNamespaces`. Parent `Ready` means child
provisioning succeeded; it does not mean each child synchronized with its
provider. Inspect the generated `PushSecret` status for provider errors.

```yaml
apiVersion: external-secrets.io/v1alpha1
kind: ClusterPushSecret
metadata:
  name: app-credentials
spec:
  pushSecretName: app-credentials-push
  pushSecretMetadata:
    labels:
      managed-by: cluster-push
  namespaceSelectors:
    - matchLabels:
        team: payments
    - matchLabels:
        shared-secrets: "true"
  refreshTime: 1m
  pushSecretSpec:
    updatePolicy: Replace
    deletionPolicy: Delete
    refreshInterval: 1h
    secretStoreRefs:
      - name: destination
        kind: SecretStore
    selector:
      secret:
        name: source-credentials
    data:
      - match:
          secretKey: password
          remoteRef:
            remoteKey: app-credentials
            property: password
```

### Cross-namespace stores

Cross-namespace pushes through `ClusterSecretStore` work (since 2.1.0).
Authorize namespace access through store conditions and ensure provider
credential references remain valid in the cluster-scoped context.

## Provider write semantics

### AWS Secrets Manager

AWS tag update, patch, and delete are supported since 0.19.0. Empty resource
policies are handled during pushes (since 2.3.0). Metadata-only tag and resource
policy changes synchronize even when the value is unchanged (since 2.2.0).

Replication locations are configurable since 2.7.0. Empty replica regions are
omitted, and deletion detaches replicated regions first (both since 2.9.0).

### GCP Secret Manager

Location and replication settings are applied correctly (since 0.17.0).
Regional pushes omit replication settings (since 0.18.0), while multiple
replication locations are supported since 2.4.0. The provider checks that a
secret version exists before treating the target as usable (since 1.1.0).

### Kubernetes

The provider supports `SecretExists` (since 2.1.0) and whole-Secret deletion
(since 1.1.0). Since 2.7.0, a push replaces the entire destination Secret rather
than merging, so remote keys missing from the source are removed.

### Vault and OpenBao

Vault has the existence-check and set operations required for push since
0.20.0. Confirm dedicated OpenBao-provider write support separately instead of
assuming every Vault-compatible operation is identical.

### 1Password

1Password Connect is treated as read-write (since 0.18.0). The SDK provider
supports multi-field push (since 2.3.0) and honors `IfNotExists` (since 2.8.0).

### Delinea, Infisical, and Akeyless

- Delinea Secret Server supports push since 2.3.0.
- Infisical supports push since 2.7.0 and maps a missing remote secret to
  `NoSecretErr`.
- Akeyless is classified read-write so push requests route to it (since 2.7.0).

### Azure and GitHub

Azure push supports `contentType` (since 2.4.0). Updating a GitHub organization
secret preserves selected repositories (since 2.7.0); configure organization
visibility explicitly when needed.

### Conjur

Conjur does not implement push or delete and returns explicit errors for both
operations (since 2.4.0). Do not infer write support from successful store
authentication or reads.

## Preflight checklist

- Confirm the provider implements existence, write, overwrite, and delete for
  the exact target form being used.
- Verify update and deletion defaults; provider cleanup is not automatic under
  `deletionPolicy: None`.
- Check whole-secret replacement versus property-level merge behavior.
- Test collisions, empty selection, invalid regexps, and remote-key rewrites.
- Inspect finalizers and `status.syncedPushSecrets` before deleting a store,
  source Secret, or push resource.
- For cluster fan-out, check every generated child rather than relying only on
  parent readiness.
